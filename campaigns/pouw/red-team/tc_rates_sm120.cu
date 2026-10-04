// Red-team rate probe for `no-exact-rewrite/sm120-e4m3`: the relative throughput, on one RTX PRO 6000 (sm_120a), of every
// exact route a rewrite of Pearl-C's FP8 chain could use. Register-only: each warp issues CH independent accumulator chains
// of one instruction in a loop, operands held in registers (loaded once from memory so nothing folds), 16 warps per SM on
// every SM. Prints one JSON line per op: instructions issued, MACs (or scalar ops), seconds (best of REPS), ops per SM per
// clock at the clock the caller passes. The rewrite's W1 price of a route is rate(fp8_f32acc) / rate(route).
//
//   nvcc -O3 -std=c++17 -gencode arch=compute_120a,code=sm_120a tc_rates_sm120.cu -o tc_rates
//   ./tc_rates <sm_clock_mhz> [iters]
#include <cstdio>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <cuda_runtime.h>

#define CK(x) do { cudaError_t e_ = (x); if (e_ != cudaSuccess) { fprintf(stderr, "%s: %s\n", #x, cudaGetErrorString(e_)); exit(1); } } while (0)

constexpr int CH = 8;          // independent chains per thread
constexpr int THREADS = 128;   // 4 warps per block
constexpr int BLOCKS_PER_SM = 4;

#define MMA_F32_4(OPSTR)                                                                                             \
  asm volatile(OPSTR " {%0,%1,%2,%3},{%4,%5,%6,%7},{%8,%9},{%0,%1,%2,%3};"                                            \
               : "+f"(d[c][0]), "+f"(d[c][1]), "+f"(d[c][2]), "+f"(d[c][3])                                          \
               : "r"(a0), "r"(a1), "r"(a2), "r"(a3), "r"(b0), "r"(b1))
#define MMA_S32_4(OPSTR)                                                                                             \
  asm volatile(OPSTR " {%0,%1,%2,%3},{%4,%5,%6,%7},{%8,%9},{%0,%1,%2,%3};"                                            \
               : "+r"(di[c][0]), "+r"(di[c][1]), "+r"(di[c][2]), "+r"(di[c][3])                                      \
               : "r"(a0), "r"(a1), "r"(a2), "r"(a3), "r"(b0), "r"(b1))
#define MMA_H_2(OPSTR)                                                                                               \
  asm volatile(OPSTR " {%0,%1},{%2,%3,%4,%5},{%6,%7},{%0,%1};"                                                        \
               : "+r"(di[c][0]), "+r"(di[c][1])                                                                      \
               : "r"(a0), "r"(a1), "r"(a2), "r"(a3), "r"(b0), "r"(b1))

enum Op {
  FP8_F32ACC, FP8_F32ACC_LEGACY, FP8_F16ACC, E2M1_F8F6F4, INT8_S32, INT4_S32, FP16_F32ACC, BF16_F32ACC, FP16_F16ACC, TF32_F32ACC,
  NVFP4_BLOCK, FADD, FFMA, IADD, LOP3, I2F, NOPS
};
static const char* NAMES[NOPS] = {"fp8_e4m3_f32acc", "fp8_e4m3_f32acc_legacy", "fp8_e4m3_f16acc", "e2m1_f8f6f4_f32acc",
                                  "int8_s32", "int4_s32", "fp16_f32acc", "bf16_f32acc", "fp16_f16acc", "tf32_f32acc",
                                  "nvfp4_block_scaled_f32acc", "fadd_f32", "ffma_f32", "iadd_s32", "lop3_b32", "i2f_s32_f32"};
// MACs per warp-level instruction (tensor ops) or ops per thread-level instruction (scalar ops)
static const long long WORK[NOPS] = {16 * 8 * 32, 16 * 8 * 32, 16 * 8 * 32, 16 * 8 * 32, 16 * 8 * 32, 16 * 8 * 64,
                                     16 * 8 * 16, 16 * 8 * 16, 16 * 8 * 16, 16 * 8 * 8, 16 * 8 * 64, 1, 1, 1, 1, 1};
static const bool TENSOR[NOPS] = {1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0};

template <int OP>
__global__ void __launch_bounds__(THREADS) probe(const uint32_t* __restrict__ in, uint32_t* __restrict__ out, int iters, int flag) {
  const int t = blockIdx.x * blockDim.x + threadIdx.x;
  uint32_t a0 = in[(t * 8 + 0) & 1023], a1 = in[(t * 8 + 1) & 1023], a2 = in[(t * 8 + 2) & 1023], a3 = in[(t * 8 + 3) & 1023];
  uint32_t b0 = in[(t * 8 + 4) & 1023], b1 = in[(t * 8 + 5) & 1023];
  float d[CH][4];
  uint32_t di[CH][4];
#pragma unroll
  for (int c = 0; c < CH; ++c)
#pragma unroll
    for (int j = 0; j < 4; ++j) { d[c][j] = 0.f; di[c][j] = in[(t + c * 4 + j) & 1023] & 0x3F003F00u; }
  float fx[CH];
  uint32_t ix[CH];
#pragma unroll
  for (int c = 0; c < CH; ++c) { fx[c] = __uint_as_float(0x3F800000u | (in[(t + c) & 1023] & 0xFFFFu)); ix[c] = in[(t + 3 * c) & 1023]; }
  const float fy = __uint_as_float(0x33800000u | (a0 & 0xFFFFu));  // tiny, so accumulations stay finite
  for (int it = 0; it < iters; ++it) {
#pragma unroll
    for (int c = 0; c < CH; ++c) {
      if constexpr (OP == FP8_F32ACC) MMA_F32_4("mma.sync.aligned.m16n8k32.row.col.kind::f8f6f4.f32.e4m3.e4m3.f32");
      if constexpr (OP == FP8_F32ACC_LEGACY) MMA_F32_4("mma.sync.aligned.m16n8k32.row.col.f32.e4m3.e4m3.f32");
      if constexpr (OP == FP8_F16ACC) MMA_H_2("mma.sync.aligned.m16n8k32.row.col.f16.e4m3.e4m3.f16");
      if constexpr (OP == E2M1_F8F6F4) MMA_F32_4("mma.sync.aligned.m16n8k32.row.col.kind::f8f6f4.f32.e2m1.e2m1.f32");
      if constexpr (OP == INT8_S32) MMA_S32_4("mma.sync.aligned.m16n8k32.row.col.s32.s8.s8.s32");
#ifndef NO_INT4
      if constexpr (OP == INT4_S32) MMA_S32_4("mma.sync.aligned.m16n8k64.row.col.s32.s4.s4.s32");
#endif
      if constexpr (OP == FP16_F32ACC) MMA_F32_4("mma.sync.aligned.m16n8k16.row.col.f32.f16.f16.f32");
      if constexpr (OP == BF16_F32ACC) MMA_F32_4("mma.sync.aligned.m16n8k16.row.col.f32.bf16.bf16.f32");
      if constexpr (OP == FP16_F16ACC) MMA_H_2("mma.sync.aligned.m16n8k16.row.col.f16.f16.f16.f16");
      if constexpr (OP == TF32_F32ACC) MMA_F32_4("mma.sync.aligned.m16n8k8.row.col.f32.tf32.tf32.f32");
      if constexpr (OP == NVFP4_BLOCK)
        asm volatile(
            "mma.sync.aligned.kind::mxf4nvf4.block_scale.scale_vec::4X.m16n8k64.row.col.f32.e2m1.e2m1.f32.ue4m3 "
            "{%0,%1,%2,%3}, {%4,%5,%6,%7}, {%8,%9}, {%0,%1,%2,%3}, {%10}, {0, 0}, {%11}, {0, 0};"
            : "+f"(d[c][0]), "+f"(d[c][1]), "+f"(d[c][2]), "+f"(d[c][3])
            : "r"(a0), "r"(a1), "r"(a2), "r"(a3), "r"(b0), "r"(b1), "r"(0x38383838u), "r"(0x38383838u));
      if constexpr (OP == FADD) asm volatile("add.rn.f32 %0, %0, %1;" : "+f"(fx[c]) : "f"(fy));
      if constexpr (OP == FFMA) asm volatile("fma.rn.f32 %0, %0, %1, %2;" : "+f"(fx[c]) : "f"(1.0f), "f"(fy));
      if constexpr (OP == IADD) asm volatile("add.s32 %0, %0, %1;" : "+r"(ix[c]) : "r"(a1));
      if constexpr (OP == LOP3) asm volatile("lop3.b32 %0, %0, %1, %2, 0x96;" : "+r"(ix[c]) : "r"(a1), "r"(a2));
      if constexpr (OP == I2F) {
        float f;
        asm volatile("cvt.rn.f32.s32 %0, %1;" : "=f"(f) : "r"(ix[c]));
        ix[c] = __float_as_uint(f) ^ a3;
      }
    }
  }
  uint32_t acc = 0;
#pragma unroll
  for (int c = 0; c < CH; ++c) {
    acc ^= __float_as_uint(fx[c]) ^ ix[c];
#pragma unroll
    for (int j = 0; j < 4; ++j) acc ^= __float_as_uint(d[c][j]) ^ di[c][j];
  }
  if (flag || acc == 0x12345678u) out[t] = acc;
}

typedef void (*Kern)(const uint32_t*, uint32_t*, int, int);
static Kern KERNS[NOPS] = {probe<0>, probe<1>, probe<2>, probe<3>, probe<4>, probe<5>, probe<6>, probe<7>,
                           probe<8>, probe<9>, probe<10>, probe<11>, probe<12>, probe<13>, probe<14>, probe<15>};

int main(int argc, char** argv) {
  const double mhz = argc > 1 ? atof(argv[1]) : 2100.0;
  const int iters = argc > 2 ? atoi(argv[2]) : 4096;
  const int reps = 5;
  cudaDeviceProp p;
  CK(cudaGetDeviceProperties(&p, 0));
  uint32_t host[1024];
  uint32_t s = 0x9E3779B9u;
  for (int i = 0; i < 1024; ++i) { s = s * 1664525u + 1013904223u; host[i] = (s & 0x37373737u); }  // finite, small codes
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
#ifdef NO_INT4
    if (op == INT4_S32) continue;
#endif
    const int it = TENSOR[op] ? iters : iters * 4;
    KERNS[op]<<<blocks, THREADS>>>(din, dout, it / 8, 0);
    CK(cudaGetLastError());
    CK(cudaDeviceSynchronize());
    float best = 1e30f;
    for (int r = 0; r < reps; ++r) {
      CK(cudaEventRecord(e0));
      KERNS[op]<<<blocks, THREADS>>>(din, dout, it, 0);
      CK(cudaEventRecord(e1));
      CK(cudaEventSynchronize(e1));
      float ms;
      CK(cudaEventElapsedTime(&ms, e0, e1));
      if (ms < best) best = ms;
    }
    const long long inst = TENSOR[op] ? (long long)blocks * (THREADS / 32) * it * CH : (long long)blocks * THREADS * it * CH;
    const double work = (double)inst * WORK[op];
    const double per_sm_clk = work / (best * 1e-3) / (p.multiProcessorCount * mhz * 1e6);
    printf("{\"op\": \"%s\", \"tensor\": %s, \"instructions\": %lld, \"work\": %.0f, \"seconds\": %.6f, \"per_sm_per_clk\": %.2f}\n",
           NAMES[op], TENSOR[op] ? "true" : "false", inst, work, best * 1e-3, per_sm_clk);
    fflush(stdout);
  }
  return 0;
}
