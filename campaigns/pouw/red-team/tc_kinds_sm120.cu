// `fp8-tile-only/sm120`'s completeness: the tensor-core kinds `tc_rates_sm120.cu` didn't time, against its E4M3 reference.
// Same method (register-only, CH independent accumulator chains per warp, 16 warps per SM on every SM, best of REPS).
//   e4m3, e5m2, e3m2, e2m3    kind::f8f6f4 m16n8k32, FP32 accumulate
//   mxf8f6f4_e4m3             kind::mxf8f6f4 block_scale (UE8M0) m16n8k32
//   mxf4_e2m1                 kind::mxf4 block_scale (UE8M0) m16n8k64
//   b1_and_popc               m16n8k256 .and.popc, s32 accumulate (1-bit MACs)
//   nvcc -O3 -std=c++17 -gencode arch=compute_120a,code=sm_120a tc_kinds_sm120.cu -o tc_kinds && ./tc_kinds 2100 [iters]
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cuda_runtime.h>

#define CK(x) do { cudaError_t e_ = (x); if (e_ != cudaSuccess) { fprintf(stderr, "%s: %s\n", #x, cudaGetErrorString(e_)); exit(1); } } while (0)

constexpr int CH = 8, THREADS = 128, BLOCKS_PER_SM = 4;

#define F32_4(OPSTR) asm volatile(OPSTR " {%0,%1,%2,%3},{%4,%5,%6,%7},{%8,%9},{%0,%1,%2,%3};" \
  : "+f"(d[c][0]), "+f"(d[c][1]), "+f"(d[c][2]), "+f"(d[c][3]) : "r"(a0), "r"(a1), "r"(a2), "r"(a3), "r"(b0), "r"(b1))
#define S32_4(OPSTR) asm volatile(OPSTR " {%0,%1,%2,%3},{%4,%5,%6,%7},{%8,%9},{%0,%1,%2,%3};" \
  : "+r"(di[c][0]), "+r"(di[c][1]), "+r"(di[c][2]), "+r"(di[c][3]) : "r"(a0), "r"(a1), "r"(a2), "r"(a3), "r"(b0), "r"(b1))
#define SCALED(OPSTR) asm volatile(OPSTR " {%0,%1,%2,%3}, {%4,%5,%6,%7}, {%8,%9}, {%0,%1,%2,%3}, {%10}, {0, 0}, {%11}, {0, 0};" \
  : "+f"(d[c][0]), "+f"(d[c][1]), "+f"(d[c][2]), "+f"(d[c][3]) \
  : "r"(a0), "r"(a1), "r"(a2), "r"(a3), "r"(b0), "r"(b1), "r"(0x7F7F7F7Fu), "r"(0x7F7F7F7Fu))

enum Op { E4M3, E5M2, E3M2, E2M3, MXF8, MXF4, B1, NOPS };
static const char* NAMES[NOPS] = {"f8f6f4_e4m3", "f8f6f4_e5m2", "f8f6f4_e3m2", "f8f6f4_e2m3", "mxf8f6f4_e4m3_ue8m0",
                                  "mxf4_e2m1_ue8m0", "b1_and_popc"};
static const long long WORK[NOPS] = {16 * 8 * 32, 16 * 8 * 32, 16 * 8 * 32, 16 * 8 * 32, 16 * 8 * 32, 16 * 8 * 64, 16 * 8 * 256};

template <int OP>
__global__ void __launch_bounds__(THREADS) probe(const uint32_t* __restrict__ in, uint32_t* __restrict__ out, int iters, int flag) {
  const int t = blockIdx.x * blockDim.x + threadIdx.x;
  uint32_t a0 = in[(t * 8) & 1023], a1 = in[(t * 8 + 1) & 1023], a2 = in[(t * 8 + 2) & 1023], a3 = in[(t * 8 + 3) & 1023];
  uint32_t b0 = in[(t * 8 + 4) & 1023], b1 = in[(t * 8 + 5) & 1023];
  float d[CH][4];
  uint32_t di[CH][4];
#pragma unroll
  for (int c = 0; c < CH; ++c)
#pragma unroll
    for (int j = 0; j < 4; ++j) { d[c][j] = 0.f; di[c][j] = in[(t + c * 4 + j) & 1023] & 0xFFu; }
  for (int it = 0; it < iters; ++it) {
#pragma unroll
    for (int c = 0; c < CH; ++c) {
      if constexpr (OP == E4M3) F32_4("mma.sync.aligned.m16n8k32.row.col.kind::f8f6f4.f32.e4m3.e4m3.f32");
      if constexpr (OP == E5M2) F32_4("mma.sync.aligned.m16n8k32.row.col.kind::f8f6f4.f32.e5m2.e5m2.f32");
      if constexpr (OP == E3M2) F32_4("mma.sync.aligned.m16n8k32.row.col.kind::f8f6f4.f32.e3m2.e3m2.f32");
      if constexpr (OP == E2M3) F32_4("mma.sync.aligned.m16n8k32.row.col.kind::f8f6f4.f32.e2m3.e2m3.f32");
#ifndef SKIP_MX
      if constexpr (OP == MXF8)
        SCALED("mma.sync.aligned.kind::mxf8f6f4.block_scale.scale_vec::1X.m16n8k32.row.col.f32.e4m3.e4m3.f32.ue8m0");
      if constexpr (OP == MXF4)
        SCALED("mma.sync.aligned.kind::mxf4.block_scale.scale_vec::2X.m16n8k64.row.col.f32.e2m1.e2m1.f32.ue8m0");
#endif
#ifndef SKIP_B1
      if constexpr (OP == B1) S32_4("mma.sync.aligned.m16n8k256.row.col.s32.b1.b1.s32.and.popc");
#endif
    }
  }
  uint32_t acc = 0;
#pragma unroll
  for (int c = 0; c < CH; ++c)
#pragma unroll
    for (int j = 0; j < 4; ++j) acc ^= __float_as_uint(d[c][j]) ^ di[c][j];
  if (flag || acc == 0x12345678u) out[t] = acc;
}

typedef void (*Kern)(const uint32_t*, uint32_t*, int, int);
static Kern KERNS[NOPS] = {probe<0>, probe<1>, probe<2>, probe<3>, probe<4>, probe<5>, probe<6>};

int main(int argc, char** argv) {
  const double mhz = argc > 1 ? atof(argv[1]) : 2100.0;
  const int iters = argc > 2 ? atoi(argv[2]) : 4096, reps = 5;
  cudaDeviceProp p; CK(cudaGetDeviceProperties(&p, 0));
  uint32_t host[1024], s = 0x9E3779B9u;
  for (int i = 0; i < 1024; ++i) { s = s * 1664525u + 1013904223u; host[i] = s & 0x37373737u; }
  uint32_t *din, *dout;
  CK(cudaMalloc(&din, sizeof host)); CK(cudaMemcpy(din, host, sizeof host, cudaMemcpyHostToDevice));
  const int blocks = p.multiProcessorCount * BLOCKS_PER_SM;
  CK(cudaMalloc(&dout, sizeof(uint32_t) * blocks * THREADS));
  cudaEvent_t e0, e1; CK(cudaEventCreate(&e0)); CK(cudaEventCreate(&e1));
  printf("{\"device\": \"%s\", \"sms\": %d, \"clock_mhz_assumed\": %.1f, \"iters\": %d}\n", p.name, p.multiProcessorCount, mhz, iters);
  for (int op = 0; op < NOPS; ++op) {
#ifdef SKIP_MX
    if (op == MXF8 || op == MXF4) continue;
#endif
#ifdef SKIP_B1
    if (op == B1) continue;
#endif
    KERNS[op]<<<blocks, THREADS>>>(din, dout, iters / 8, 0); CK(cudaGetLastError()); CK(cudaDeviceSynchronize());
    float best = 1e30f;
    for (int r = 0; r < reps; ++r) {
      CK(cudaEventRecord(e0)); KERNS[op]<<<blocks, THREADS>>>(din, dout, iters, 0); CK(cudaEventRecord(e1));
      CK(cudaEventSynchronize(e1)); float ms; CK(cudaEventElapsedTime(&ms, e0, e1)); if (ms < best) best = ms;
    }
    const long long inst = (long long)blocks * (THREADS / 32) * iters * CH;
    const double work = (double)inst * WORK[op], rate = work / (best * 1e-3) / (p.multiProcessorCount * mhz * 1e6);
    printf("{\"op\": \"%s\", \"instructions\": %lld, \"work\": %.0f, \"seconds\": %.6f, \"per_sm_per_clk\": %.2f}\n", NAMES[op], inst,
           work, best * 1e-3, rate);
    fflush(stdout);
  }
  return 0;
}
