// Red-team probe for the MVP cost model's generic-core rate (internal/pouw/neekon-mvp-cost-model.md, measurement 1): the peak
// rate, on one RTX PRO 6000 (sm_120a), of every non-tensor-core primitive a matmul or lookup-table matmul could be built from.
// A real kernel is bounded by these peaks. Same harness as tc_rates_sm120.cu: CH independent chains per thread, 16 warps/SM
// on every SM, best of 5; the FP8 mma.sync (FP32 accumulate) runs first as the unit. MACs per instruction: HFMA2 and BF16x2 2,
// DP4A 4 (int8), DP2A 2, IMAD 1; lookups (PRMT byte select, LDS from a shared table with a data-dependent index) count 1.
//
//   nvcc -O3 -std=c++17 -gencode arch=compute_120a,code=sm_120a generic_rates_sm120.cu -o generic_rates && ./generic_rates 2100
#include <cstdio>
#include <cstdint>
#include <cstdlib>
#include <cuda_runtime.h>

#define CK(x) do { cudaError_t e_ = (x); if (e_ != cudaSuccess) { fprintf(stderr, "%s: %s\n", #x, cudaGetErrorString(e_)); exit(1); } } while (0)

constexpr int CH = 8, THREADS = 128, BLOCKS_PER_SM = 4;
enum Op { FP8_MMA, HFMA2, BF16X2_FMA, DP4A, DP2A, IMAD, FFMA, PRMT, LDS, NOPS };
static const char* NAMES[NOPS] = {"fp8_e4m3_f32acc_mma", "hfma2_f16x2", "fma_bf16x2", "dp4a_s8", "dp2a_s16s8", "imad_s32",
                                  "ffma_f32", "prmt_byte_lookup", "lds_table_lookup"};
static const double WORK[NOPS] = {4096, 2, 2, 4, 2, 1, 1, 1, 1};

template <int OP>
__global__ void __launch_bounds__(THREADS) probe(const uint32_t* __restrict__ in, uint32_t* __restrict__ out, int iters, int flag) {
  __shared__ uint32_t table[1024];
  const int t = blockIdx.x * blockDim.x + threadIdx.x;
  for (int i = threadIdx.x; i < 1024; i += blockDim.x) table[i] = in[i] & 1023u;
  __syncthreads();
  uint32_t a0 = in[(t * 8) & 1023], a1 = in[(t * 8 + 1) & 1023], a2 = in[(t * 8 + 2) & 1023], a3 = in[(t * 8 + 3) & 1023];
  uint32_t b0 = in[(t * 8 + 4) & 1023], b1 = in[(t * 8 + 5) & 1023];
  float d[CH][4];
  uint32_t x[CH];
  float f[CH];
#pragma unroll
  for (int c = 0; c < CH; ++c) {
    x[c] = in[(t + 5 * c) & 1023] & 0x3BFF3BFFu;  // small finite halves / bf16s, and table indices below 1024
    f[c] = __uint_as_float(0x3F800000u | (in[(t + c) & 1023] & 0xFFFFu));
#pragma unroll
    for (int j = 0; j < 4; ++j) d[c][j] = 0.f;
  }
  const uint32_t h1 = 0x3C003C00u ^ (in[9] & 0x00010001u);   // about (1.0, 1.0) in f16x2, known only at run time
  const uint32_t hb = 0x3F803F80u ^ (in[11] & 0x00010001u);  // about (1.0, 1.0) in bf16x2
  const uint32_t eps = a1 & 0x00FF00FFu;
  for (int it = 0; it < iters; ++it) {
#pragma unroll
    for (int c = 0; c < CH; ++c) {
      if constexpr (OP == FP8_MMA)
        asm volatile("mma.sync.aligned.m16n8k32.row.col.kind::f8f6f4.f32.e4m3.e4m3.f32 {%0,%1,%2,%3},{%4,%5,%6,%7},{%8,%9},{%0,%1,%2,%3};"
                     : "+f"(d[c][0]), "+f"(d[c][1]), "+f"(d[c][2]), "+f"(d[c][3])
                     : "r"(a0), "r"(a1), "r"(a2), "r"(a3), "r"(b0), "r"(b1));
      if constexpr (OP == HFMA2) asm volatile("fma.rn.f16x2 %0, %0, %1, %2;" : "+r"(x[c]) : "r"(h1), "r"(eps));
      if constexpr (OP == BF16X2_FMA) asm volatile("fma.rn.bf16x2 %0, %0, %1, %2;" : "+r"(x[c]) : "r"(hb), "r"(eps));
      if constexpr (OP == DP4A) asm volatile("dp4a.s32.s32 %0, %1, %2, %0;" : "+r"(x[c]) : "r"(a2), "r"(a3));
      if constexpr (OP == DP2A) asm volatile("dp2a.lo.s32.s32 %0, %1, %2, %0;" : "+r"(x[c]) : "r"(a2), "r"(a3));
      if constexpr (OP == IMAD) asm volatile("mad.lo.s32 %0, %0, %1, %2;" : "+r"(x[c]) : "r"(a2 | 1u), "r"(a3));
      if constexpr (OP == FFMA) asm volatile("fma.rn.f32 %0, %0, %1, %2;" : "+f"(f[c]) : "f"(1.0f), "f"(1e-30f));
      if constexpr (OP == PRMT) asm volatile("prmt.b32 %0, %1, %2, %0;" : "+r"(x[c]) : "r"(a2), "r"(a3));
      if constexpr (OP == LDS) x[c] = table[(x[c] ^ c) & 1023u];
    }
  }
  uint32_t acc = 0;
#pragma unroll
  for (int c = 0; c < CH; ++c) {
    acc ^= x[c] ^ __float_as_uint(f[c]);
#pragma unroll
    for (int j = 0; j < 4; ++j) acc ^= __float_as_uint(d[c][j]);
  }
  if (flag || acc == 0x12345678u) out[t] = acc;
}

typedef void (*Kern)(const uint32_t*, uint32_t*, int, int);
static Kern KERNS[NOPS] = {probe<0>, probe<1>, probe<2>, probe<3>, probe<4>, probe<5>, probe<6>, probe<7>, probe<8>};

int main(int argc, char** argv) {
  const double mhz = argc > 1 ? atof(argv[1]) : 2100.0;
  const int iters = argc > 2 ? atoi(argv[2]) : 4096;
  cudaDeviceProp p;
  CK(cudaGetDeviceProperties(&p, 0));
  uint32_t host[1024], s = 0x9E3779B9u;
  for (int i = 0; i < 1024; ++i) { s = s * 1664525u + 1013904223u; host[i] = s & 0x37373737u; }
  uint32_t *din, *dout;
  CK(cudaMalloc(&din, sizeof host));
  CK(cudaMemcpy(din, host, sizeof host, cudaMemcpyHostToDevice));
  const int blocks = p.multiProcessorCount * BLOCKS_PER_SM;
  CK(cudaMalloc(&dout, sizeof(uint32_t) * blocks * THREADS));
  cudaEvent_t e0, e1;
  CK(cudaEventCreate(&e0));
  CK(cudaEventCreate(&e1));
  printf("{\"device\": \"%s\", \"sms\": %d, \"cc\": \"%d.%d\", \"clock_mhz_assumed\": %.1f, \"iters\": %d, \"chains\": %d, "
         "\"warps_per_sm\": %d}\n", p.name, p.multiProcessorCount, p.major, p.minor, mhz, iters, CH, BLOCKS_PER_SM * THREADS / 32);
  for (int op = 0; op < NOPS; ++op) {
    const int it = op == FP8_MMA ? iters : iters * 4;
    KERNS[op]<<<blocks, THREADS>>>(din, dout, it / 8, 0);
    CK(cudaGetLastError());
    CK(cudaDeviceSynchronize());
    float best = 1e30f;
    for (int r = 0; r < 5; ++r) {
      CK(cudaEventRecord(e0));
      KERNS[op]<<<blocks, THREADS>>>(din, dout, it, 0);
      CK(cudaEventRecord(e1));
      CK(cudaEventSynchronize(e1));
      float ms;
      CK(cudaEventElapsedTime(&ms, e0, e1));
      if (ms < best) best = ms;
    }
    const double inst = op == FP8_MMA ? (double)blocks * (THREADS / 32) * it * CH : (double)blocks * THREADS * it * CH;
    const double work = inst * WORK[op];
    printf("{\"op\": \"%s\", \"tensor\": %s, \"instructions\": %.0f, \"work\": %.0f, \"seconds\": %.6f, \"per_sm_per_clk\": %.2f}\n",
           NAMES[op], op == FP8_MMA ? "true" : "false", inst, work, best * 1e-3,
           work / (best * 1e-3) / (p.multiProcessorCount * mhz * 1e6));
    fflush(stdout);
  }
  return 0;
}
