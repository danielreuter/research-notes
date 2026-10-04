// How sm_120's NVFP4 block-scaled MMA reads scale bytes outside UE4M3 (bit 7 set, and 0x7F). One warp per (side, byte):
// A and B are E2M1 1.0 everywhere (code 0x2), the other side's scales are 0x38 (1.0), and every scale byte on the probed
// side is s, so D = 64 * decode(s) at every coordinate. Printed per byte: the decode the device implies (D / 64), whether
// all 128 D elements agree, and UE4M3's decode of s where it is defined.
//   nvcc -O3 -std=c++17 -gencode arch=compute_120a,code=sm_120a scale_bytes_sm120.cu -o scale_bytes && ./scale_bytes
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cuda_runtime.h>

#define CK(x) do { cudaError_t e_ = (x); if (e_ != cudaSuccess) { fprintf(stderr, "%s: %s\n", #x, cudaGetErrorString(e_)); exit(1); } } while (0)

__global__ void probe(float* out) {                     // blockIdx.x = byte, blockIdx.y = side (0: A's scale, 1: B's)
  const uint32_t s = blockIdx.x, side = blockIdx.y;
  const uint32_t sa = side == 0 ? s * 0x01010101u : 0x38383838u, sb = side == 1 ? s * 0x01010101u : 0x38383838u;
  const uint32_t a = 0x22222222u, b = 0x22222222u;
  float d0 = 0, d1 = 0, d2 = 0, d3 = 0;
  asm volatile(
      "mma.sync.aligned.kind::mxf4nvf4.block_scale.scale_vec::4X.m16n8k64.row.col.f32.e2m1.e2m1.f32.ue4m3 "
      "{%0,%1,%2,%3}, {%4,%5,%6,%7}, {%8,%9}, {%0,%1,%2,%3}, {%10}, {0, 0}, {%11}, {0, 0};"
      : "+f"(d0), "+f"(d1), "+f"(d2), "+f"(d3) : "r"(a), "r"(a), "r"(a), "r"(a), "r"(b), "r"(b), "r"(sa), "r"(sb));
  float* o = out + (side * 256 + s) * 128 + threadIdx.x * 4;
  o[0] = d0; o[1] = d1; o[2] = d2; o[3] = d3;
}

static double ue4m3(uint32_t s) {                      // UE4M3: E4M3 without the sign; 0x7F is NaN
  if (s == 0x7F) return NAN;
  uint32_t e = (s >> 3) & 15, m = s & 7;
  return e ? std::ldexp(1.0 + m / 8.0, (int)e - 7) : std::ldexp((double)m, -9);
}

int main() {
  float* out; CK(cudaMallocManaged(&out, 2 * 256 * 128 * 4));
  probe<<<dim3(256, 2), 32>>>(out); CK(cudaGetLastError()); CK(cudaDeviceSynchronize());
  cudaDeviceProp p; CK(cudaGetDeviceProperties(&p, 0));
  printf("{\"device\": \"%s\"}\n", p.name);
  for (int side = 0; side < 2; ++side)
    for (uint32_t s = 0; s < 256; ++s) {
      const float* o = out + (side * 256 + s) * 128;
      bool same = true;
      for (int i = 1; i < 128; ++i) same &= (o[i] == o[0]) || (std::isnan(o[i]) && std::isnan(o[0]));
      const double implied = o[0] / 64.0, want = s < 0x80 ? ue4m3(s) : NAN;
      const bool in_range = s < 0x7F;
      const bool match_low7 = implied == ue4m3(s & 0x7F) || (std::isnan(implied) && std::isnan(ue4m3(s & 0x7F)));
      printf("{\"side\": \"%s\", \"byte\": %u, \"d\": %.9g, \"implied_scale\": %.9g, \"uniform\": %s, \"ue4m3\": %.9g, "
             "\"in_ue4m3\": %s, \"equals_ue4m3_of_low7\": %s}\n",
             side ? "B" : "A", s, o[0], implied, same ? "true" : "false", want, in_range ? "true" : "false",
             match_low7 ? "true" : "false");
    }
  return 0;
}
