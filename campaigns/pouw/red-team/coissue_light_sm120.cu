// `concurrent-budgets/sm120`, the two unmeasured time terms: light CUDA-core mixes beside each MMA kind (sm_120a).
//   FP8 mma.sync m16n8k32 (E4M3) + dp4a at 0/1/2/4 per thread per MMA: an adversary emulating credited FP8 work on idle
//     issue slots (the table measured 4 and 8 per MMA; lighter mixes were open);
//   NVFP4 mma.sync m16n8k64 block_scale (OMMA.SF) + dp4a at 0/1/2/4/8: Pearl-C4's CUDA-core route beside its own MMA,
//     "not measured" in the table, bounded only at 8.4-10.1% of native;
//   FP16 mma.sync m16n8k16 (a v1 rewrite's leaf) + HFMA2 at 0/1/2/4: the rewrite's pre-adds hiding behind its leaves
//     (v1's exact-region time item; its pre-add mix is about 0.55 HFMA2 per thread per MMA).
// Per mix: MMA MACs per SM per clock and the CUDA-core op's rate; 16 warps per SM on every SM, CH chains, best of REPS.
//   nvcc -O3 -std=c++17 -gencode arch=compute_120a,code=sm_120a coissue_light_sm120.cu -o coissue_light && ./coissue_light 2092
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cuda_runtime.h>
#define CK(x) do { cudaError_t e_ = (x); if (e_ != cudaSuccess) { fprintf(stderr, "%s: %s\n", #x, cudaGetErrorString(e_)); exit(1); } } while (0)
constexpr int CH = 4, THREADS = 128, BLOCKS_PER_SM = 4;

template <int KIND, int ND, int NH>
__global__ void __launch_bounds__(THREADS) mix(const uint32_t* __restrict__ in, uint32_t* __restrict__ out, int iters) {
  const int t = blockIdx.x * blockDim.x + threadIdx.x;
  uint32_t a0 = in[(t * 8) & 1023] & 0x37373737u, a1 = in[(t * 8 + 1) & 1023] & 0x37373737u, a2 = in[(t * 8 + 2) & 1023] & 0x37373737u,
           a3 = in[(t * 8 + 3) & 1023] & 0x37373737u, b0 = in[(t * 8 + 4) & 1023] & 0x37373737u, b1 = in[(t * 8 + 5) & 1023] & 0x37373737u;
  const uint32_t sa = 0x38383838u, sb = 0x38383838u, h16 = 0x3C003C00u;
  float d[CH][4]; uint32_t id[CH], h[CH];
#pragma unroll
  for (int c = 0; c < CH; ++c) { id[c] = in[(t + 3 * c) & 1023]; h[c] = h16; d[c][0] = d[c][1] = d[c][2] = d[c][3] = 0.f; }
  for (int it = 0; it < iters; ++it) {
#pragma unroll
    for (int c = 0; c < CH; ++c) {
#pragma unroll
      for (int j = 0; j < ND; ++j) asm volatile("dp4a.s32.s32 %0, %1, %2, %0;" : "+r"(id[c]) : "r"(a2), "r"(a3));
#pragma unroll
      for (int j = 0; j < NH; ++j) asm volatile("fma.rn.f16x2 %0, %0, %1, %2;" : "+r"(h[c]) : "r"(h16), "r"(0x00010001u));
      if constexpr (KIND == 0)
        asm volatile("mma.sync.aligned.m16n8k32.row.col.kind::f8f6f4.f32.e4m3.e4m3.f32 {%0,%1,%2,%3},{%4,%5,%6,%7},{%8,%9},{%0,%1,%2,%3};"
                     : "+f"(d[c][0]), "+f"(d[c][1]), "+f"(d[c][2]), "+f"(d[c][3]) : "r"(a0), "r"(a1), "r"(a2), "r"(a3), "r"(b0), "r"(b1));
      if constexpr (KIND == 1)
        asm volatile("mma.sync.aligned.kind::mxf4nvf4.block_scale.scale_vec::4X.m16n8k64.row.col.f32.e2m1.e2m1.f32.ue4m3 "
                     "{%0,%1,%2,%3}, {%4,%5,%6,%7}, {%8,%9}, {%0,%1,%2,%3}, {%10}, {0, 0}, {%11}, {0, 0};"
                     : "+f"(d[c][0]), "+f"(d[c][1]), "+f"(d[c][2]), "+f"(d[c][3]) : "r"(a0), "r"(a1), "r"(a2), "r"(a3), "r"(b0), "r"(b1), "r"(sa), "r"(sb));
      if constexpr (KIND == 2)
        asm volatile("mma.sync.aligned.m16n8k16.row.col.f32.f16.f16.f32 {%0,%1,%2,%3},{%4,%5,%6,%7},{%8,%9},{%0,%1,%2,%3};"
                     : "+f"(d[c][0]), "+f"(d[c][1]), "+f"(d[c][2]), "+f"(d[c][3]) : "r"(h16), "r"(h16), "r"(h16), "r"(h16), "r"(h16), "r"(h16));
    }
  }
  uint32_t acc = 0;
#pragma unroll
  for (int c = 0; c < CH; ++c) acc ^= id[c] ^ h[c] ^ __float_as_uint(d[c][0]) ^ __float_as_uint(d[c][1]) ^ __float_as_uint(d[c][2]) ^ __float_as_uint(d[c][3]);
  if (acc == 0x12345678u) out[t] = acc;
}

struct Mix { const char* name; void (*k)(const uint32_t*, uint32_t*, int); int kind, nd, nh; };
#define M(NAME, K, D, H) {NAME, mix<K, D, H>, K, D, H}
static const Mix MIXES[] = {
    M("dp4a-solo", 3, 4, 0), M("hfma2-solo", 3, 0, 4),
    M("fp8", 0, 0, 0), M("fp8+dp4a1", 0, 1, 0), M("fp8+dp4a2", 0, 2, 0), M("fp8+dp4a4", 0, 4, 0),
    M("nvfp4", 1, 0, 0), M("nvfp4+dp4a1", 1, 1, 0), M("nvfp4+dp4a2", 1, 2, 0), M("nvfp4+dp4a4", 1, 4, 0), M("nvfp4+dp4a8", 1, 8, 0),
    M("fp16", 2, 0, 0), M("fp16+hfma2_1", 2, 0, 1), M("fp16+hfma2_2", 2, 0, 2), M("fp16+hfma2_4", 2, 0, 4),
};
static const int MACS[4] = {4096, 8192, 2048, 0};

int main(int argc, char** argv) {
  const double mhz = argc > 1 ? atof(argv[1]) : 2092.0;
  const int iters = argc > 2 ? atoi(argv[2]) : 2048, reps = 5;
  cudaDeviceProp p; CK(cudaGetDeviceProperties(&p, 0));
  uint32_t host[1024], s = 0x9E3779B9u;
  for (int i = 0; i < 1024; ++i) { s = s * 1664525u + 1013904223u; host[i] = s; }
  uint32_t *din, *dout; CK(cudaMalloc(&din, sizeof host)); CK(cudaMemcpy(din, host, sizeof host, cudaMemcpyHostToDevice));
  const int blocks = p.multiProcessorCount * BLOCKS_PER_SM; CK(cudaMalloc(&dout, 4 * blocks * THREADS));
  cudaEvent_t e0, e1; CK(cudaEventCreate(&e0)); CK(cudaEventCreate(&e1));
  for (const Mix& m : MIXES) {
    m.k<<<blocks, THREADS>>>(din, dout, iters / 8); CK(cudaGetLastError()); CK(cudaDeviceSynchronize());
    float best = 1e30f;
    for (int r = 0; r < reps; ++r) {
      CK(cudaEventRecord(e0)); m.k<<<blocks, THREADS>>>(din, dout, iters); CK(cudaEventRecord(e1)); CK(cudaEventSynchronize(e1));
      float ms; CK(cudaEventElapsedTime(&ms, e0, e1)); if (ms < best) best = ms;
    }
    const double denom = best * 1e-3 * p.multiProcessorCount * mhz * 1e6;
    const double thr = (double)blocks * THREADS * iters * CH, warps = (double)blocks * (THREADS / 32) * iters * CH;
    printf("{\"mix\":\"%s\",\"mma_macs\":%.1f,\"dp4a\":%.1f,\"hfma2\":%.1f}\n", m.name,
           m.kind < 3 ? warps * MACS[m.kind] / denom : 0.0, thr * m.nd / denom, thr * m.nh / denom);
    fflush(stdout);
  }
  return 0;
}
