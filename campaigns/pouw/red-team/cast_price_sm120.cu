// `admits-ref/pearl-c-sm120-*` and `w1-complete/sm120` on one RTX PRO 6000 (sm_120a):
//   cast   the honest E4M3 cast's price per code in W1 units (FP8 E4M3 m16n8k32 MACs), measured as a ratio against the FP8
//          mma.sync loop on the same die in the same process: F2FP alone (e4m3x2 on two live floats), and packed codes
//          stored to a shared-memory tile with 32-, 64- or 128-bit stores at a 144- or 160-byte row stride (thread t writes
//          row t of a 32-row tile), as GPU 0's store-bound loops do. Inputs are loop-invariant registers; the cast is volatile
//          asm, so it is re-issued every iteration and nothing else runs per code. Stores are volatile, so ptxas can't
//          merge narrow stores into STS.128.
//   mma    mma.sync E4M3 m16n8k32 throughput on random, all-zero and 7/8-zero operands: the full-fragment rule prices every
//          issued instruction alike, which holds only if the tensor pipe doesn't run faster on zeros.
//   nvcc -O3 -std=c++17 -gencode arch=compute_120a,code=sm_120a cast_price_sm120.cu -o cast_price && ./cast_price [iters]
#include <cuda_runtime.h>
#include <cstdint>
#include <cstdio>
#include <cstdlib>

#define CK(x) do { cudaError_t e_ = (x); if (e_ != cudaSuccess) { fprintf(stderr, "%s: %s\n", #x, cudaGetErrorString(e_)); exit(1); } } while (0)

constexpr int THREADS = 128, BLOCKS_PER_SM = 4, CH = 8;

__device__ __forceinline__ uint32_t cvt2(float hi, float lo) {
  uint16_t d;
  asm volatile("cvt.rn.satfinite.e4m3x2.f32 %0, %1, %2;" : "=h"(d) : "f"(hi), "f"(lo));
  return d;
}

// STORE: 0 none, 32, 64, 128 bits per thread per store; STRIDE: row stride in bytes
template <int STORE, int STRIDE>
__global__ void __launch_bounds__(THREADS) cast_loop(const float* __restrict__ in, uint32_t* __restrict__ out, int iters) {
  __shared__ __align__(16) uint8_t tile[4][32 * 176];
  const int t = threadIdx.x, lane = t & 31, w = t >> 5;
  float f[16];
#pragma unroll
  for (int i = 0; i < 16; ++i) f[i] = in[(blockIdx.x * THREADS + t + 97 * i) & 4095];
  uint32_t acc = 0;
  uint8_t* row = &tile[w][lane * STRIDE];
  for (int it = 0; it < iters; ++it) {
    // 16 codes per iteration: 8 F2FP.e4m3x2
    uint32_t c[8];
#pragma unroll
    for (int i = 0; i < 8; ++i) c[i] = cvt2(f[2 * i], f[2 * i + 1]);
    uint32_t p0 = c[0] | (c[1] << 16), p1 = c[2] | (c[3] << 16), p2 = c[4] | (c[5] << 16), p3 = c[6] | (c[7] << 16);
    const int off = (it & 3) * 16;
    if constexpr (STORE == 0) acc ^= p0 ^ p1 ^ p2 ^ p3;
    if constexpr (STORE == 32) {
      asm volatile("st.volatile.shared.b32 [%0], %1;" :: "r"((uint32_t)__cvta_generic_to_shared(row + off)), "r"(p0));
      asm volatile("st.volatile.shared.b32 [%0], %1;" :: "r"((uint32_t)__cvta_generic_to_shared(row + off + 4)), "r"(p1));
      asm volatile("st.volatile.shared.b32 [%0], %1;" :: "r"((uint32_t)__cvta_generic_to_shared(row + off + 8)), "r"(p2));
      asm volatile("st.volatile.shared.b32 [%0], %1;" :: "r"((uint32_t)__cvta_generic_to_shared(row + off + 12)), "r"(p3));
    }
    if constexpr (STORE == 64) {
      asm volatile("st.volatile.shared.v2.b32 [%0], {%1, %2};" :: "r"((uint32_t)__cvta_generic_to_shared(row + off)), "r"(p0), "r"(p1));
      asm volatile("st.volatile.shared.v2.b32 [%0], {%1, %2};" :: "r"((uint32_t)__cvta_generic_to_shared(row + off + 8)), "r"(p2), "r"(p3));
    }
    if constexpr (STORE == 128)
      asm volatile("st.volatile.shared.v4.b32 [%0], {%1, %2, %3, %4};" :: "r"((uint32_t)__cvta_generic_to_shared(row + off)),
                   "r"(p0), "r"(p1), "r"(p2), "r"(p3));
  }
  __syncwarp();
  if (acc == 0x12345678u || tile[w][lane] == 0x5A) out[blockIdx.x * THREADS + t] = acc;
}

// ZEROS: 0 random operands, 1 all zero, 2 seven of eight bytes zero
template <int ZEROS>
__global__ void __launch_bounds__(THREADS) mma_loop(const uint32_t* __restrict__ in, uint32_t* __restrict__ out, int iters) {
  const int t = blockIdx.x * THREADS + threadIdx.x;
  uint32_t m = ZEROS == 0 ? 0x37373737u : ZEROS == 1 ? 0u : 0x00000037u;
  uint32_t a0 = in[(t * 8) & 1023] & m, a1 = in[(t * 8 + 1) & 1023] & m, a2 = in[(t * 8 + 2) & 1023] & m,
           a3 = in[(t * 8 + 3) & 1023] & m, b0 = in[(t * 8 + 4) & 1023] & m, b1 = in[(t * 8 + 5) & 1023] & m;
  float d[CH][4];
#pragma unroll
  for (int c = 0; c < CH; ++c) d[c][0] = d[c][1] = d[c][2] = d[c][3] = 0.f;
  for (int it = 0; it < iters; ++it) {
#pragma unroll
    for (int c = 0; c < CH; ++c)
      asm volatile("mma.sync.aligned.m16n8k32.row.col.kind::f8f6f4.f32.e4m3.e4m3.f32 {%0,%1,%2,%3},{%4,%5,%6,%7},{%8,%9},{%0,%1,%2,%3};"
                   : "+f"(d[c][0]), "+f"(d[c][1]), "+f"(d[c][2]), "+f"(d[c][3]) : "r"(a0), "r"(a1), "r"(a2), "r"(a3), "r"(b0), "r"(b1));
  }
  uint32_t acc = 0;
#pragma unroll
  for (int c = 0; c < CH; ++c) acc ^= __float_as_uint(d[c][0]) ^ __float_as_uint(d[c][3]);
  if (acc == 0x12345678u) out[t] = acc;
}

int main(int argc, char** argv) {
  const int iters = argc > 1 ? atoi(argv[1]) : 4096, reps = 7;
  cudaDeviceProp p; CK(cudaGetDeviceProperties(&p, 0));
  const int blocks = p.multiProcessorCount * BLOCKS_PER_SM;
  float* fin; uint32_t *uin, *out;
  CK(cudaMalloc(&fin, 4096 * 4)); CK(cudaMalloc(&uin, 1024 * 4)); CK(cudaMalloc(&out, 4 * blocks * THREADS));
  float hf[4096]; uint32_t hu[1024]; uint32_t s = 0x9E3779B9u;
  for (int i = 0; i < 4096; ++i) { s = s * 1664525u + 1013904223u; hf[i] = (float)((s >> 8) % 1000) / 7.0f - 60.0f; }
  for (int i = 0; i < 1024; ++i) { s = s * 1664525u + 1013904223u; hu[i] = s; }
  CK(cudaMemcpy(fin, hf, sizeof hf, cudaMemcpyHostToDevice)); CK(cudaMemcpy(uin, hu, sizeof hu, cudaMemcpyHostToDevice));
  cudaEvent_t e0, e1; CK(cudaEventCreate(&e0)); CK(cudaEventCreate(&e1));
  auto timeit = [&](auto launch) {
    launch(iters / 8); CK(cudaGetLastError()); CK(cudaDeviceSynchronize());
    float best = 1e30f;
    for (int r = 0; r < reps; ++r) {
      CK(cudaEventRecord(e0)); launch(iters); CK(cudaEventRecord(e1)); CK(cudaEventSynchronize(e1));
      float ms; CK(cudaEventElapsedTime(&ms, e0, e1)); if (ms < best) best = ms;
    }
    return (double)best;
  };
  // the unit: one FP8 E4M3 m16n8k32 MAC, from the random-operand mma loop
  const double macs = (double)blocks * (THREADS / 32) * iters * CH * 4096;
  const double t_mma = timeit([&](int n) { mma_loop<0><<<blocks, THREADS>>>(uin, out, n); });
  const double t_mma0 = timeit([&](int n) { mma_loop<1><<<blocks, THREADS>>>(uin, out, n); });
  const double t_mma7 = timeit([&](int n) { mma_loop<2><<<blocks, THREADS>>>(uin, out, n); });
  const double unit = t_mma / macs;                    // ms per FP8 MAC on this die
  printf("{\"device\": \"%s\", \"sms\": %d, \"iters\": %d, \"mma_ms_random\": %.4f, \"mma_ms_zero\": %.4f, \"mma_ms_7of8_zero\": %.4f, "
         "\"zero_over_random\": %.4f, \"sparse_over_random\": %.4f}\n", p.name, p.multiProcessorCount, iters, t_mma, t_mma0, t_mma7,
         t_mma0 / t_mma, t_mma7 / t_mma);
  const double codes = (double)blocks * THREADS * iters * 16;
  struct V { const char* name; double ms; };
  V v[] = {
      {"f2fp_only", timeit([&](int n) { cast_loop<0, 144><<<blocks, THREADS>>>(fin, out, n); })},
      {"packed_st32_stride144", timeit([&](int n) { cast_loop<32, 144><<<blocks, THREADS>>>(fin, out, n); })},
      {"packed_st32_stride160", timeit([&](int n) { cast_loop<32, 160><<<blocks, THREADS>>>(fin, out, n); })},
      {"packed_st64_stride144", timeit([&](int n) { cast_loop<64, 144><<<blocks, THREADS>>>(fin, out, n); })},
      {"packed_st64_stride160", timeit([&](int n) { cast_loop<64, 160><<<blocks, THREADS>>>(fin, out, n); })},
      {"packed_st128_stride144", timeit([&](int n) { cast_loop<128, 144><<<blocks, THREADS>>>(fin, out, n); })},
      {"packed_st128_stride160", timeit([&](int n) { cast_loop<128, 160><<<blocks, THREADS>>>(fin, out, n); })},
  };
  for (auto& x : v)
    printf("{\"loop\": \"%s\", \"ms\": %.4f, \"w1_units_per_code\": %.3f}\n", x.name, x.ms, x.ms / codes / unit);
  return 0;
}
