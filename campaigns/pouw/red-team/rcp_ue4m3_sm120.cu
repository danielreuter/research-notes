// `tt-out/fp4-sm120`'s chain-only price flag: GPU 4's block-scale price uses rcp.approx, while the spec's reciprocal is
// correctly rounded (div.rn). Is rcp.approx.f32 (and .ftz) exact on every valid UE4M3 scale byte, 0x01–0x7E (126 values)?
// Each value's reciprocal is compared with div.rn.f32(1, s) bit for bit; the same for the FP32 values 6·s and s/6 that the
// block rule touches is reported too, for context.
//   nvcc -O3 -std=c++17 -gencode arch=compute_120a,code=sm_120a rcp_ue4m3_sm120.cu -o rcp_ue4m3 && ./rcp_ue4m3
#include <cuda_runtime.h>
#include <cstdint>
#include <cstdio>
#include <cmath>

__global__ void run(uint32_t* out) {
  const int b = threadIdx.x + 1;                         // bytes 1..126
  if (b > 126) return;
  const int e = (b >> 3) & 15, m = b & 7;
  const float s = e ? ldexpf(1.0f + m / 8.0f, e - 7) : ldexpf((float)m, -9);
  float approx, approx_ftz, rn;
  asm("rcp.approx.f32 %0, %1;" : "=f"(approx) : "f"(s));
  asm("rcp.approx.ftz.f32 %0, %1;" : "=f"(approx_ftz) : "f"(s));
  asm("div.rn.f32 %0, %1, %2;" : "=f"(rn) : "f"(1.0f), "f"(s));
  out[4 * b] = __float_as_uint(s);
  out[4 * b + 1] = __float_as_uint(approx);
  out[4 * b + 2] = __float_as_uint(approx_ftz);
  out[4 * b + 3] = __float_as_uint(rn);
}

int main() {
  uint32_t* out;
  cudaMallocManaged(&out, 4 * 128 * 4);
  run<<<1, 128>>>(out);
  cudaDeviceSynchronize();
  int bad = 0, bad_ftz = 0, sub = 0;
  printf("[");
  for (int b = 1; b <= 126; ++b) {
    uint32_t s = out[4 * b], a = out[4 * b + 1], af = out[4 * b + 2], r = out[4 * b + 3];
    if (a != r) bad++;
    if (af != r) bad_ftz++;
    if (((b >> 3) & 15) == 0) sub++;
    if (a != r || af != r) printf("{\"byte\": %d, \"s\": \"%08x\", \"approx\": \"%08x\", \"approx_ftz\": \"%08x\", \"rn\": \"%08x\"},", b, s, a, af, r);
  }
  printf("{}]\n{\"check\": \"rcp.approx vs div.rn on UE4M3 bytes 0x01-0x7E\", \"bytes\": 126, \"subnormal_bytes\": %d, "
         "\"approx_mismatches\": %d, \"approx_ftz_mismatches\": %d}\n", sub, bad, bad_ftz);
  return 0;
}
