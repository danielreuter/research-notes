// `concurrent-budgets/sm120` and `declared-hw/sm120`: which pipes co-issue on one RTX PRO 6000 (sm_120a). Each kernel runs a
// fixed mix per loop iteration (per thread: nF FFMA, nI IADD3/LOP3-class adds, nD dp4a, nH HFMA2, and per warp nM FP8
// mma.sync), CH independent chains per op so latency hides, 16 warps per SM on every SM, best of REPS. Printed per mix:
// each op's rate per SM per clock and the sum of (rate / its solo peak): 1.0 means the ops share one pipe's time, 2.0 means
// two pipes run fully concurrently.
//   nvcc -O3 -std=c++17 -gencode arch=compute_120a,code=sm_120a coissue_sm120.cu -o coissue && ./coissue 2100 [iters]
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cuda_fp16.h>
#include <cuda_runtime.h>

#define CK(x) do { cudaError_t e_ = (x); if (e_ != cudaSuccess) { fprintf(stderr, "%s: %s\n", #x, cudaGetErrorString(e_)); exit(1); } } while (0)

constexpr int CH = 4, THREADS = 128, BLOCKS_PER_SM = 4;

template <int NF, int NI, int ND, int NH, int NM>
__global__ void __launch_bounds__(THREADS) mix(const uint32_t* __restrict__ in, uint32_t* __restrict__ out, int iters) {
  const int t = blockIdx.x * blockDim.x + threadIdx.x;
  uint32_t a0 = in[(t * 8) & 1023] & 0x37373737u, a1 = in[(t * 8 + 1) & 1023] & 0x37373737u, a2 = in[(t * 8 + 2) & 1023] & 0x37373737u,
           a3 = in[(t * 8 + 3) & 1023] & 0x37373737u, b0 = in[(t * 8 + 4) & 1023] & 0x37373737u, b1 = in[(t * 8 + 5) & 1023] & 0x37373737u;
  float f[CH], d[CH][4];
  uint32_t ia[CH], id[CH], h[CH];
  const float fy = __uint_as_float(0x33800000u | (a0 & 0xFFFF));
  const uint32_t hy = 0x00010001u;
#pragma unroll
  for (int c = 0; c < CH; ++c) {
    f[c] = __uint_as_float(0x3F800000u | (in[(t + c) & 1023] & 0xFFFF)); ia[c] = in[(t + 2 * c) & 1023]; id[c] = in[(t + 3 * c) & 1023];
    h[c] = 0x3C003C00u; d[c][0] = d[c][1] = d[c][2] = d[c][3] = 0.f;
  }
  for (int it = 0; it < iters; ++it) {
#pragma unroll
    for (int c = 0; c < CH; ++c) {
#pragma unroll
      for (int j = 0; j < NF; ++j) asm volatile("fma.rn.f32 %0, %0, %1, %2;" : "+f"(f[c]) : "f"(1.0f), "f"(fy));
#pragma unroll
      for (int j = 0; j < NI; ++j) asm volatile("add.s32 %0, %0, %1;" : "+r"(ia[c]) : "r"(a1));
#pragma unroll
      for (int j = 0; j < ND; ++j) asm volatile("dp4a.s32.s32 %0, %1, %2, %0;" : "+r"(id[c]) : "r"(a2), "r"(a3));
#pragma unroll
      for (int j = 0; j < NH; ++j) asm volatile("fma.rn.f16x2 %0, %0, %1, %2;" : "+r"(h[c]) : "r"(0x3C003C00u), "r"(hy));
#pragma unroll
      for (int j = 0; j < NM; ++j)
        asm volatile("mma.sync.aligned.m16n8k32.row.col.kind::f8f6f4.f32.e4m3.e4m3.f32 {%0,%1,%2,%3},{%4,%5,%6,%7},{%8,%9},{%0,%1,%2,%3};"
                     : "+f"(d[c][0]), "+f"(d[c][1]), "+f"(d[c][2]), "+f"(d[c][3])
                     : "r"(a0), "r"(a1), "r"(a2), "r"(a3), "r"(b0), "r"(b1));
    }
  }
  uint32_t acc = 0;
#pragma unroll
  for (int c = 0; c < CH; ++c)
    acc ^= __float_as_uint(f[c]) ^ ia[c] ^ id[c] ^ h[c] ^ __float_as_uint(d[c][0]) ^ __float_as_uint(d[c][1]) ^
           __float_as_uint(d[c][2]) ^ __float_as_uint(d[c][3]);
  if (acc == 0x12345678u) out[t] = acc;
}

struct Mix { const char* name; void (*k)(const uint32_t*, uint32_t*, int); int nf, ni, nd, nh, nm; };
#define M(NAME, F, I, D, H, MM) {NAME, mix<F, I, D, H, MM>, F, I, D, H, MM}
static const Mix MIXES[] = {
    M("ffma", 4, 0, 0, 0, 0), M("iadd", 0, 4, 0, 0, 0), M("dp4a", 0, 0, 4, 0, 0), M("hfma2", 0, 0, 0, 4, 0), M("mma", 0, 0, 0, 0, 1),
    M("ffma+iadd", 2, 2, 0, 0, 0), M("ffma+dp4a", 2, 0, 2, 0, 0), M("ffma+hfma2", 2, 0, 0, 2, 0), M("dp4a+iadd", 0, 2, 2, 0, 0),
    M("dp4a+hfma2", 0, 0, 2, 2, 0), M("mma+ffma", 4, 0, 0, 0, 1), M("mma+dp4a", 0, 0, 4, 0, 1), M("mma+hfma2", 0, 0, 0, 4, 1),
    M("mma+iadd", 0, 4, 0, 0, 1), M("mma+ffma8", 8, 0, 0, 0, 1), M("mma+dp4a8", 0, 0, 8, 0, 1),
};

int main(int argc, char** argv) {
  const double mhz = argc > 1 ? atof(argv[1]) : 2100.0;
  const int iters = argc > 2 ? atoi(argv[2]) : 2048, reps = 5;
  cudaDeviceProp p; CK(cudaGetDeviceProperties(&p, 0));
  uint32_t host[1024], s = 0x9E3779B9u;
  for (int i = 0; i < 1024; ++i) { s = s * 1664525u + 1013904223u; host[i] = s; }
  uint32_t *din, *dout; CK(cudaMalloc(&din, sizeof host)); CK(cudaMemcpy(din, host, sizeof host, cudaMemcpyHostToDevice));
  const int blocks = p.multiProcessorCount * BLOCKS_PER_SM; CK(cudaMalloc(&dout, 4 * blocks * THREADS));
  cudaEvent_t e0, e1; CK(cudaEventCreate(&e0)); CK(cudaEventCreate(&e1));
  const int n = sizeof MIXES / sizeof MIXES[0];
  double solo[5] = {0, 0, 0, 0, 0};   // ffma, iadd, dp4a, hfma2 (thread ops), mma (MACs), per SM per clock
  printf("{\"device\": \"%s\", \"sms\": %d, \"clock_mhz_assumed\": %.1f, \"iters\": %d}\n", p.name, p.multiProcessorCount, mhz, iters);
  for (int i = 0; i < n; ++i) {
    const Mix& m = MIXES[i];
    m.k<<<blocks, THREADS>>>(din, dout, iters / 8); CK(cudaGetLastError()); CK(cudaDeviceSynchronize());
    float best = 1e30f;
    for (int r = 0; r < reps; ++r) {
      CK(cudaEventRecord(e0)); m.k<<<blocks, THREADS>>>(din, dout, iters); CK(cudaEventRecord(e1)); CK(cudaEventSynchronize(e1));
      float ms; CK(cudaEventElapsedTime(&ms, e0, e1)); if (ms < best) best = ms;
    }
    const double denom = best * 1e-3 * p.multiProcessorCount * mhz * 1e6;
    const double thr = (double)blocks * THREADS * iters * CH, warps = (double)blocks * (THREADS / 32) * iters * CH;
    double r[5] = {thr * m.nf / denom, thr * m.ni / denom, thr * m.nd / denom, thr * m.nh / denom, warps * m.nm * 4096 / denom};
    if (i < 5) solo[i] = r[i];
    double util = 0;
    for (int j = 0; j < 5; ++j) if (solo[j] > 0) util += r[j] / solo[j];
    printf("{\"mix\": \"%s\", \"ffma\": %.1f, \"iadd\": %.1f, \"dp4a\": %.1f, \"hfma2\": %.1f, \"mma_macs\": %.1f, \"sum_of_solo_shares\": %.3f}\n",
           m.name, r[0], r[1], r[2], r[3], r[4], util);
    fflush(stdout);
  }
  return 0;
}
