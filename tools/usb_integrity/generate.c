/* Packed PCM contract v1: producer. No board/device access. */
#include <errno.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static uint64_t mix(uint64_t x)
{
    x += UINT64_C(0x9e3779b97f4a7c15);
    x = (x ^ (x >> 30)) * UINT64_C(0xbf58476d1ce4e5b9);
    x = (x ^ (x >> 27)) * UINT64_C(0x94d049bb133111eb);
    return x ^ (x >> 31);
}

static uint64_t number(const char *s)
{
    char *end;
    if (*s < '0' || *s > '9') goto bad;
    errno = 0;
    unsigned long long n = strtoull(s, &end, 0);
    if (errno || *end || n > UINT64_MAX) goto bad;
    return (uint64_t)n;
bad:
    fprintf(stderr, "Invalid unsigned integer: %s\n", s);
    exit(2);
}

static unsigned pattern_id(const char *s)
{
    const char *names[] = {"identity", "edges", "walking", "alternating"};
    for (unsigned i = 0; i < 4; i++) if (!strcmp(s, names[i])) return i;
    fprintf(stderr, "Unknown pattern: %s\n", s);
    exit(2);
}

static uint32_t sample(uint64_t f, unsigned c, unsigned channels,
                       unsigned rotation, unsigned pattern, uint64_t seed)
{
    static const uint32_t edges[] = {0, 0xffffff, 1, 0xfffffe, 0x7fffff,
        0x800000, 0xff, 0x100, 0xffff, 0x10000, 0x555555, 0xaaaaaa};
    if (pattern == 1) return edges[((unsigned)(f % 12) + c) % 12];
    if (pattern == 2) {
        unsigned k = ((unsigned)(f % 48) + c) % 48;
        return k < 24 ? UINT32_C(1) << k : 0xffffff ^ (UINT32_C(1) << (k - 24));
    }
    if (pattern == 3) return (((unsigned)(f % 2) + c) % 2) ? 0xaaaaaa : 0x555555;
    unsigned role = (c + channels - rotation) % channels;
    if (channels >= 3) {
        if (role == 0) return (uint32_t)(f & 0xffffff);
        if (role == 1) return (uint32_t)((f >> 24) & 0xffffff);
        if (role == 2) return 0xa50000 | (uint32_t)(f >> 48);
    }
    return (uint32_t)(mix(f ^ (seed + ((uint64_t)c + 1) *
                            UINT64_C(0x9e3779b97f4a7c15))) & 0xffffff);
}

static void frame(uint64_t f, unsigned channels, unsigned rotation,
                  unsigned pattern, uint64_t seed, uint64_t domain)
{
    unsigned char bytes[72];
    for (unsigned c = 0; c < channels; c++) {
        uint32_t v = domain ? (uint32_t)(mix(seed ^ domain ^ (f * channels + c)) & 0xffffff)
                            : sample(f, c, channels, rotation, pattern, seed);
        for (unsigned b = 0; b < 3; b++) bytes[c * 3 + b] = (unsigned char)(v >> (b * 8));
    }
    if (fwrite(bytes, 3, channels, stdout) != channels) {
        perror("PCM output");
        exit(1);
    }
}

int main(int argc, char **argv)
{
    uint64_t channels = 24, rotation = 0, seed = 0, first = 0, frames = 0;
    unsigned pattern = 0;
    for (int i = 1; i < argc; i += 2) {
        if (i + 1 >= argc) { fprintf(stderr, "Expected --option value pairs\n"); return 2; }
        if (!strcmp(argv[i], "--channels")) channels = number(argv[i + 1]);
        else if (!strcmp(argv[i], "--frames")) frames = number(argv[i + 1]);
        else if (!strcmp(argv[i], "--first-frame")) first = number(argv[i + 1]);
        else if (!strcmp(argv[i], "--seed")) seed = number(argv[i + 1]);
        else if (!strcmp(argv[i], "--rotation")) rotation = number(argv[i + 1]);
        else if (!strcmp(argv[i], "--pattern")) pattern = pattern_id(argv[i + 1]);
        else { fprintf(stderr, "Unknown option: %s\n", argv[i]); return 2; }
    }
    if (!channels || channels > 24 || rotation >= channels || !frames ||
        frames - 1 > UINT64_MAX - first || frames > UINT64_MAX / (channels * 3) - 8) {
        fprintf(stderr, "Invalid channels, rotation, frame range or byte count\n"); return 2;
    }
    (void)setvbuf(stdout, NULL, _IOFBF, 65536);
    for (unsigned j = 0; j < 4; j++)
        frame(j, (unsigned)channels, (unsigned)rotation, pattern, seed,
              UINT64_C(0x5354415254303031));
    for (uint64_t i = 0; i < frames; i++)
        frame(first + i, (unsigned)channels, (unsigned)rotation, pattern, seed, 0);
    for (unsigned j = 0; j < 4; j++)
        frame(j, (unsigned)channels, (unsigned)rotation, pattern, seed,
              UINT64_C(0x454e442d30303031));
    if (fflush(stdout)) { perror("PCM flush"); return 1; }
    return 0;
}
