// The 2:4-sparse block-scaled NVFP4 MMA (OMMA.SF.SP, m16n8k128) against the dense one (m16n8k64) on sm_120a: useful
// products per SM per clock. A sparse k128 instruction on a 2:4 operand does 16 x 8 x 64 useful products (half its
// logical 16 x 8 x 128), so equal useful rates mean half the price per logical MAC for a 2:4 operand.
// Same harness as tc_rates_sm120.cu.
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cuda_runtime.h>

#define CK(x) do { cudaError_t e_ = (x); if (e_ != cudaSuccess) { fprintf(stderr, "%s: %s\n", #x, cudaGetErrorString(e_)); exit(1); } } while (0)

constexpr int CH = 8, THREADS = 128, BLOCKS_PER_SM = 4;
static const char* NAMES[2] = {"nvfp4_dense_k64", "nvfp4_sparse24_k128"};
static const double USEFUL[2] = {16 * 8 * 64, 16 * 8 * 64};

template <int OP>
__global__ void __launch_bounds__(THREADS) probe(const uint32_t* __restrict__ in, uint32_t* __restrict__ out, int iters, int flag) {
  const int t = blockIdx.x * blockDim.x + threadIdx.x;
  uint32_t a0 = in[(t * 8) & 1023], a1 = in[(t * 8 + 1) & 1023], a2 = in[(t * 8 + 2) & 1023], a3 = in[(t * 8 + 3) & 1023];
  uint32_t b0 = in[(t * 8 + 4) & 1023], b1 = in[(t * 8 + 5) & 1023], b2 = in[(t * 8 + 6) & 1023], b3 = in[(t * 8 + 7) & 1023];
  const uint32_t meta = 0x44444444u, sa = 0x38383838u, sb = 0x38383838u;
  float d[CH][4];
#pragma unroll
  for (int c = 0; c < CH; ++c)
#pragma unroll
    for (int j = 0; j < 4; ++j) d[c][j] = 0.f;
  for (int it = 0; it < iters; ++it) {
#pragma unroll
    for (int c = 0; c < CH; ++c) {
      if constexpr (OP == 0)
        asm volatile("mma.sync.aligned.kind::mxf4nvf4.block_scale.scale_vec::4X.m16n8k64.row.col.f32.e2m1.e2m1.f32.ue4m3 "
                     "{%0,%1,%2,%3}, {%4,%5,%6,%7}, {%8,%9}, {%0,%1,%2,%3}, {%10}, {0, 0}, {%11}, {0, 0};"
                     : "+f"(d[c][0]), "+f"(d[c][1]), "+f"(d[c][2]), "+f"(d[c][3])
                     : "r"(a0), "r"(a1), "r"(a2), "r"(a3), "r"(b0), "r"(b1), "r"(sa), "r"(sb));
      if constexpr (OP == 1)
        asm volatile("mma.sp::ordered_metadata.sync.aligned.m16n8k128.row.col.kind::mxf4nvf4.block_scale.scale_vec::4X.f32.e2m1.e2m1.f32.ue4m3 "
                     "{%0,%1,%2,%3}, {%4,%5,%6,%7}, {%8,%9,%10,%11}, {%0,%1,%2,%3}, %12, 0x0, {%13}, {0, 0}, {%14}, {0, 0};"
                     : "+f"(d[c][0]), "+f"(d[c][1]), "+f"(d[c][2]), "+f"(d[c][3])
                     : "r"(a0), "r"(a1), "r"(a2), "r"(a3), "r"(b0), "r"(b1), "r"(b2), "r"(b3), "r"(meta), "r"(sa), "r"(sb));
    }
  }
  uint32_t acc = 0;
#pragma unroll
  for (int c = 0; c < CH; ++c)
#pragma unroll
    for (int j = 0; j < 4; ++j) acc ^= __float_as_uint(d[c][j]);
  if (flag || acc == 0x12345678u) out[t] = acc;
}

typedef void (*Kern)(const uint32_t*, uint32_t*, int, int);
static Kern KERNS[2] = {probe<0>, probe<1>};

int main(int argc, char** argv) {
  const double mhz = argc > 1 ? atof(argv[1]) : 2100.0;
  const int iters = argc > 2 ? atoi(argv[2]) : 4096;
  cudaDeviceProp p; CK(cudaGetDeviceProperties(&p, 0));
  uint32_t host[1024], s = 0x9E3779B9u;
  for (int i = 0; i < 1024; ++i) { s = s * 1664525u + 1013904223u; host[i] = s & 0x33333333u; }
  uint32_t *din, *dout;
  CK(cudaMalloc(&din, sizeof host)); CK(cudaMemcpy(din, host, sizeof host, cudaMemcpyHostToDevice));
  const int blocks = p.multiProcessorCount * BLOCKS_PER_SM;
  CK(cudaMalloc(&dout, sizeof(uint32_t) * blocks * THREADS));
  cudaEvent_t e0, e1; CK(cudaEventCreate(&e0)); CK(cudaEventCreate(&e1));
  printf("{\"device\": \"%s\", \"sms\": %d, \"clock_mhz_assumed\": %.1f, \"iters\": %d}\n", p.name, p.multiProcessorCount, mhz, iters);
  for (int op = 0; op < 2; ++op) {
    KERNS[op]<<<blocks, THREADS>>>(din, dout, iters / 8, 0); CK(cudaGetLastError()); CK(cudaDeviceSynchronize());
    float best = 1e30f;
    for (int r = 0; r < 5; ++r) {
      CK(cudaEventRecord(e0)); KERNS[op]<<<blocks, THREADS>>>(din, dout, iters, 0); CK(cudaEventRecord(e1));
      CK(cudaEventSynchronize(e1)); float ms; CK(cudaEventElapsedTime(&ms, e0, e1)); if (ms < best) best = ms;
    }
    const double inst = (double)blocks * (THREADS / 32) * iters * CH, useful = inst * USEFUL[op];
    printf("{\"op\": \"%s\", \"instructions\": %.0f, \"useful_products\": %.0f, \"seconds\": %.6f, \"useful_per_sm_per_clk\": %.2f}\n",
           NAMES[op], inst, useful, best * 1e-3, useful / (best * 1e-3) / (p.multiProcessorCount * mhz * 1e6));
    fflush(stdout);
  }
  return 0;
}
