# Packed PCM test contract, version 1

This is the implementation contract for TEST-008's host tools, not another
requirements document or a physical test result. Version changes require new
vectors. The normative input is a manifest containing channels (1–24), pattern,
seed and first_frame (unsigned 64-bit, including zero), frames (positive
unsigned 64-bit), and
rotation (0–channels-1). No first_frame + frames - 1 overflow is permitted.
The JSON manifest has schema=1, integer channels/rotation/rate_hz, a pattern
string, and decimal strings for seed/first_frame/frames, preserving all 64 bits.
Supported rate_hz values are 48000 and 96000. Rate labels describe playback
and frame-count interpretation; these tools do not pace output in real time.

## Stream layout

Each frame contains channels values in ascending channel order. Each value is
an unsigned 24-bit code serialized least-significant byte first, exactly three
bytes; bit 23 is the sign bit when interpreted as S24_3LE. Codes are compared
without gain, dither, resampling or floating-point conversion. The frame index
is global, starting at first_frame; it is not a byte or per-channel counter.

The finite stream is four START marker frames, exactly frames data frames,
and four END marker frames. The manifest is supplied independently to the
checker; the stream is not self-describing or an authentication protocol.
Use a new seed for each hardware run. Reusing a seed reproduces a fixture.

Define M(x), with every operation modulo 2^64 and logical right shifts:

1. z = x + 0x9e3779b97f4a7c15
2. z = (z XOR (z >> 30)) * 0xbf58476d1ce4e5b9
3. z = (z XOR (z >> 27)) * 0x94d049bb133111eb
4. return z XOR (z >> 31)

For marker frame j=0..3 and channel c, code is the low 24 bits of
M(seed XOR domain XOR (j * channels + c)). START domain is
0x5354415254303031; END domain is 0x454e442d30303031.

## Data patterns

For global frame f and channel c:

- identity: when channels >= 3, role = (c + channels - rotation) modulo
  channels. Roles 0/1/2 carry f bits 0–23, bits 24–47, and
  0xa50000 OR bits 48–63 respectively. Every other role carries the low
  24 bits of M(f XOR (seed + (c+1)*0x9e3779b97f4a7c15)). For one/two channels,
  all values use that mixed-data formula; they are diagnostic configurations,
  not the explicit three-word frame-index proof. Repeat short runs with
  different rotations to exercise every channel as metadata and mixed data.
- edges: index a fixed table by ((f modulo 12)+c) modulo 12. The table is
  000000, ffffff, 000001, fffffe, 7fffff, 800000, 0000ff, 000100,
  00ffff, 010000, 555555, aaaaaa (hexadecimal).
- walking: k=((f modulo 48)+c) modulo 48. For k<24 use 1<<k;
  otherwise use 0xffffff XOR (1<<(k-24)).
- alternating: 0x555555 when ((f modulo 2)+c) is even, otherwise 0xaaaaaa.

Modular indexing above avoids overflowing f+c near the 64-bit boundary.
The short periodic patterns cannot detect replacement by identical periods;
run identity separately. None measures analog quality or USB electrical eyes.
Tones/sweeps/application sanity remain separate TEST-008 work, not an
implemented feature of these four-pattern tools.

## Capture alignment and failure

The offline default requires START at byte zero and EOF immediately after END.
For a later capture, explicitly permit at most two seconds of leading/trailing
complete frames at the declared sample rate. Search only at known PCM frame
boundaries, never arbitrary byte offsets. Report the excluded counts. After
START, compare every value and require END at the declared position; never
search again or hide an interior mismatch by realigning. Partial frames,
missing markers, excess exclusions, short data and extra interior data fail.

A PASS means only that this finite PCM file matches this contract. It does
not prove its origin, real-time delivery, USB speed, clock accuracy, hardware
channel independence or absence of errors outside the compared window.

## Independent validation

The generator and checker have separate C implementations. The tests use a
third Python definition and fixed literal byte vectors, including sign/byte
and 24/32/48/64-bit index boundaries. Neither C program imports the other's
encoder. Deliberately corrupted fixtures must fail; an unchanged file must
pass. This reduces common implementation errors, not formal verification.
