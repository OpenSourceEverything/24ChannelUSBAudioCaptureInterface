/* Packed PCM contract v1: independently implemented comparator. */
#include <errno.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static uint64_t permutation(uint64_t value)
{
    uint64_t a = value + UINT64_C(11400714819323198485);
    uint64_t b = (a ^ (a >> 30)) * UINT64_C(13787848793156543929);
    uint64_t c = (b ^ (b >> 27)) * UINT64_C(10723151780598845931);
    return c ^ (c >> 31);
}

static uint64_t integer(const char *text)
{
    char *tail;
    errno = 0;
    unsigned long long n = strtoull(text, &tail, 0);
    if (*text < '0' || *text > '9' || *tail || errno || n > UINT64_MAX) {
        fprintf(stderr, "Invalid unsigned integer\n"); exit(2);
    }
    return (uint64_t)n;
}

static uint32_t expected(uint64_t index, unsigned channel, unsigned count,
                         unsigned rotate, unsigned kind, uint64_t key)
{
    static const uint32_t table[12] = {0x000000, 0xffffff, 0x000001, 0xfffffe,
        0x7fffff, 0x800000, 0x0000ff, 0x000100, 0x00ffff, 0x010000, 0x555555, 0xaaaaaa};
    switch (kind) {
    case 1: return table[(index % 12 + channel) % 12];
    case 2: {
        unsigned bit = (unsigned)((index % 48 + channel) % 48);
        uint32_t v = UINT32_C(1) << (bit % 24);
        return bit / 24 ? (UINT32_C(0xffffff) - v) : v;
    }
    case 3: return (index % 2 + channel) % 2 ? 11184810 : 5592405;
    default: break;
    }
    unsigned tag = (channel + count - rotate) % count;
    if (count >= 3 && tag < 3) {
        if (tag == 2) return UINT32_C(10813440) + (uint32_t)(index / UINT64_C(281474976710656));
        return (uint32_t)((index / (tag ? UINT64_C(16777216) : 1)) % UINT64_C(16777216));
    }
    uint64_t salt = key + UINT64_C(11400714819323198485) * ((uint64_t)channel + 1);
    return (uint32_t)(permutation(index ^ salt) % UINT64_C(16777216));
}

static uint32_t unpack(const unsigned char *p)
{
    return (uint32_t)p[0] + 256 * (uint32_t)p[1] + 65536 * (uint32_t)p[2];
}

static int fail(const char *reason, uint64_t index, unsigned channel,
                 uint32_t want, uint32_t got)
{
    printf("{\"status\":\"FAIL\",\"reason\":\"%s\",\"frame\":\"%" PRIu64
           "\",\"channel\":%u,\"expected\":%u,\"actual\":%u}\n",
           reason, index, channel, want, got);
    return 1;
}

/* 1 = full frame, 0 = EOF, -1 = partial frame or I/O error. */
static int read_frame(unsigned char *p, size_t size)
{
    size_t n = fread(p, 1, size, stdin);
    return n == size ? 1 : (n || ferror(stdin) ? -1 : 0);
}

static int marker(const unsigned char *p, unsigned n, unsigned j,
                   uint64_t seed, uint64_t domain)
{
    for (unsigned c = 0; c < n; c++) {
        uint32_t value = (uint32_t)(permutation(seed ^ domain ^ ((uint64_t)j * n + c)) & 0xffffff);
        if (unpack(p + c * 3) != value) return 0;
    }
    return 1;
}

int main(int argc, char **argv)
{
    uint64_t n64 = 24, rotation64 = 0, frames = 0, first = 0, seed = 0;
    uint64_t max_lead = 0, max_tail = 0;
    const char *name = "identity";
    for (int i = 1; i < argc; i += 2) {
        if (i + 1 >= argc) { fprintf(stderr, "Expected option/value pairs\n"); return 2; }
        const char *key = argv[i], *value = argv[i + 1];
        if (!strcmp(key, "--channels")) n64 = integer(value);
        else if (!strcmp(key, "--frames")) frames = integer(value);
        else if (!strcmp(key, "--first-frame")) first = integer(value);
        else if (!strcmp(key, "--seed")) seed = integer(value);
        else if (!strcmp(key, "--rotation")) rotation64 = integer(value);
        else if (!strcmp(key, "--max-leading-frames")) max_lead = integer(value);
        else if (!strcmp(key, "--max-trailing-frames")) max_tail = integer(value);
        else if (!strcmp(key, "--pattern")) name = value;
        else { fprintf(stderr, "Unknown option\n"); return 2; }
    }
    if (!n64 || n64 > 24 || rotation64 >= n64 || !frames ||
        frames - 1 > UINT64_MAX - first || frames > UINT64_MAX / (n64 * 3) - 8 ||
        max_lead > UINT64_MAX - 4) {
        fprintf(stderr, "Invalid range or configuration\n"); return 2;
    }
    const char *names[] = {"identity", "edges", "walking", "alternating"};
    unsigned kind;
    for (kind = 0; kind < 4; kind++) if (!strcmp(name, names[kind])) break;
    if (kind == 4) { fprintf(stderr, "Unknown pattern\n"); return 2; }
    unsigned n = (unsigned)n64, rotation = (unsigned)rotation64;
    size_t bytes = (size_t)n * 3;
    unsigned char window[4][72], current[72];
    uint64_t leading = 0;
    (void)setvbuf(stdin, NULL, _IOFBF, 65536);
    for (unsigned j = 0; j < 4; j++) {
        int r = read_frame(window[j], bytes);
        if (r != 1) return fail(r < 0 ? "partial_frame_or_read_error" : "missing_start", 0, 0, 0, 0);
    }
    for (;;) {
        unsigned j;
        for (j = 0; j < 4; j++) if (!marker(window[j], n, j, seed, UINT64_C(0x5354415254303031))) break;
        if (j == 4) break;
        if (leading == max_lead) return fail("start_outside_allowed_window", leading, 0, 0, 0);
        for (j = 0; j < 3; j++) memcpy(window[j], window[j + 1], bytes);
        if (read_frame(window[3], bytes) != 1) return fail("missing_start", leading, 0, 0, 0);
        leading++;
    }
    for (uint64_t k = 0; k < frames; k++) {
        int r = read_frame(current, bytes);
        if (r != 1) return fail(r < 0 ? "partial_frame_or_read_error" : "short_data", first + k, 0, 0, 0);
        for (unsigned c = 0; c < n; c++) {
            uint32_t got = unpack(current + c * 3);
            uint32_t want = expected(first + k, c, n, rotation, kind, seed);
            if (got != want) return fail("sample_mismatch", first + k, c, want, got);
        }
    }
    for (unsigned j = 0; j < 4; j++) {
        if (read_frame(current, bytes) != 1 ||
            !marker(current, n, j, seed, UINT64_C(0x454e442d30303031)))
            return fail("missing_or_misplaced_end", frames, 0, 0, 0);
    }
    uint64_t trailing = 0;
    for (;;) {
        int r = read_frame(current, bytes);
        if (!r) break;
        if (r < 0) return fail("partial_frame_or_read_error", frames, 0, 0, 0);
        if (trailing == max_tail) return fail("excess_trailing_frames", frames, 0, 0, 0);
        trailing++;
    }
    printf("{\"status\":\"PASS\",\"scope\":\"finite_pcm_comparison\","
           "\"channels\":%u,\"pattern\":\"%s\",\"frames\":\"%" PRIu64
           "\",\"first_frame\":\"%" PRIu64 "\",\"compared_bytes\":\"%" PRIu64
           "\",\"leading_frames_excluded\":\"%" PRIu64
           "\",\"trailing_frames_excluded\":\"%" PRIu64 "\"}\n",
           n, name, frames, first, frames * n * 3, leading, trailing);
    return fflush(stdout) || ferror(stdout) ? 1 : 0;
}
