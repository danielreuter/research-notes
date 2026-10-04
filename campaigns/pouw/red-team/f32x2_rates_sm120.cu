// Red-team rate probe for `price-floor/sm120` clause (b) and the promotion's credited price: does sm_120a run packed FP32
// arithmetic (`add.rn.f32x2`, `fma.rn.f32x2`, two FP32 results per instruction in a 64-bit register pair) at the scalar
// rate? If so an FP32 add costs half of FADD's 8.46 units, and a promotion credited at the scalar price is over-credited.
// Same harness as tc_rates_sm120.cu; work counts FP32 results (2 per packed instruction).
#include <cstdio>
#include <cstdint>
#include <cstdlib>
#include <cuda_runtime.h>

#define CK(x) do { cudaError_t e_ = (x); if (e_ != cudaSuccess) { fprintf(stderr, "%s: %s\n", #x, cudaGetErrorString(e_)); exit(1); } } while (0)

constexpr int CH = 8, THREADS = 128, BLOCKS_PER_SM = 4;
enum Op { FP8_MMA, FADD, ADD_F32X2, FFMA, FMA_F32X2, NOPS };
static const char* NAMES[NOPS] = {"fp8_e4m3_f32acc_mma", "fadd_f32", "add_f32x2", "ffma_f32", "fma_f32x2"};
static const double WORK[NOPS] = {4096, 1, 2, 1, 2};

template <int OP>
__global__ void __launch_bounds__(THREADS) probe(const uint32_t* __restrict__ in, uint32_t* __restrict__ out, int iters, int flag) {
  const int t = blockIdx.x * blockDim.x + threadIdx.x;
  uint32_t a0 = in[(t * 8) & 1023], a1 = in[(t * 8 + 1) & 1023], a2 = in[(t * 8 + 2) & 1023], a3 = in[(t * 8 + 3) & 1023];
  uint32_t b0 = in[(t * 8 + 4) & 1023], b1 = in[(t * 8 + 5) & 1023];
  float d[CH][4];
  float f[CH];
  unsigned long long p[CH];
  const float fy = __uint_as_float(0x33800000u | (a0 & 0xFFFFu));
  const unsigned long long py = ((unsigned long long)__float_as_uint(fy) << 32) | __float_as_uint(fy);
  const unsigned long long p1 = ((unsigned long long)0x3F800000u << 32) | 0x3F800000u;
#pragma unroll
  for (int c = 0; c < CH; ++c) {
    f[c] = __uint_as_float(0x3F800000u | (in[(t + c) & 1023] & 0xFFFFu));
    p[c] = ((unsigned long long)__float_as_uint(f[c]) << 32) | __float_as_uint(f[c] + 1.0f);
#pragma unroll
    for (int j = 0; j < 4; ++j) d[c][j] = 0.f;
  }
  for (int it = 0; it < iters; ++it) {
#pragma unroll
    for (int c = 0; c < CH; ++c) {
      if constexpr (OP == FP8_MMA)
        asm volatile("mma.sync.aligned.m16n8k32.row.col.kind::f8f6f4.f32.e4m3.e4m3.f32 {%0,%1,%2,%3},{%4,%5,%6,%7},{%8,%9},{%0,%1,%2,%3};"
                     : "+f"(d[c][0]), "+f"(d[c][1]), "+f"(d[c][2]), "+f"(d[c][3])
                     : "r"(a0), "r"(a1), "r"(a2), "r"(a3), "r"(b0), "r"(b1));
      if constexpr (OP == FADD) asm volatile("add.rn.f32 %0, %0, %1;" : "+f"(f[c]) : "f"(fy));
      if constexpr (OP == ADD_F32X2) asm volatile("add.rn.f32x2 %0, %0, %1;" : "+l"(p[c]) : "l"(py));
      if constexpr (OP == FFMA) asm volatile("fma.rn.f32 %0, %0, %1, %2;" : "+f"(f[c]) : "f"(1.0f), "f"(fy));
      if constexpr (OP == FMA_F32X2) asm volatile("fma.rn.f32x2 %0, %0, %1, %2;" : "+l"(p[c]) : "l"(p1), "l"(py));
    }
  }
  uint32_t acc = 0;
#pragma unroll
  for (int c = 0; c < CH; ++c) {
    acc ^= __float_as_uint(f[c]) ^ (uint32_t)p[c] ^ (uint32_t)(p[c] >> 32);
#pragma unroll
    for (int j = 0; j < 4; ++j) acc ^= __float_as_uint(d[c][j]);
  }
  if (flag || acc == 0x12345678u) out[t] = acc;
}

typedef void (*Kern)(const uint32_t*, uint32_t*, int, int);
static Kern KERNS[NOPS] = {probe<0>, probe<1>, probe<2>, probe<3>, probe<4>};

int main(int argc, char** argv) {
  const double mhz = argc > 1 ? atof(argv[1]) : 2100.0;
  const int iters = argc > 2 ? atoi(argv[2]) : 4096;
  cudaDeviceProp prop;
  CK(cudaGetDeviceProperties(&prop, 0));
  uint32_t host[1024], s = 0x9E3779B9u;
  for (int i = 0; i < 1024; ++i) { s = s * 1664525u + 1013904223u; host[i] = s & 0x37373737u; }
  uint32_t *din, *dout;
  CK(cudaMalloc(&din, sizeof host));
  CK(cudaMemcpy(din, host, sizeof host, cudaMemcpyHostToDevice));
  const int blocks = prop.multiProcessorCount * BLOCKS_PER_SM;
  CK(cudaMalloc(&dout, sizeof(uint32_t) * blocks * THREADS));
  cudaEvent_t e0, e1;
  CK(cudaEventCreate(&e0));
  CK(cudaEventCreate(&e1));
  printf("{\"device\": \"%s\", \"sms\": %d, \"cc\": \"%d.%d\", \"clock_mhz_assumed\": %.1f, \"iters\": %d, \"chains\": %d, "
         "\"warps_per_sm\": %d}\n", prop.name, prop.multiProcessorCount, prop.major, prop.minor, mhz, iters, CH,
         BLOCKS_PER_SM * THREADS / 32);
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
           work / (best * 1e-3) / (prop.multiProcessorCount * mhz * 1e6));
    fflush(stdout);
  }
  return 0;
}
