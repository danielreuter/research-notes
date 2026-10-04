// Writer: bc-c7421547 (by its own report), an agent the sm_120 PoUW coordinator (bc-2aa33ad8) started by mistake, not the assessor. The assessor (bc-d7d4b0d1) reviewed and adopted its GEMM jobs (run r20260930-085618-5cfa), 30 Sep 2026.
// Assessment of `generic-core-rate/sm120` (the MVP cost model's r_g): the fastest non-tensor-core GEMM we can build on one
// RTX PRO 6000 (sm_120a), as a whole kernel rather than an instruction peak, against cuBLAS in the same process.
//
// Variants (every one a register-tiled SIMT GEMM, 8x8 outputs per thread, double-buffered shared memory, no tensor-core op):
//   ffma_f32     FP32 x FP32, FFMA into FP32
//   ffma_bf16    BF16 x BF16 converted on the shared-memory store, FFMA into FP32 (a BF16 GEMM on the CUDA cores)
//   hfma2_f16    FP16x2 packed FMA into FP16x2 (an upper bound: FP16 accumulation)
//   hfma2_bf16   BF16x2 packed FMA into BF16x2 (an upper bound: BF16 accumulation)
//   dp4a_s8      int8 x int8, dp4a into int32 (the FP8 / int8 route)
//   dp4a_nvfp4   NVFP4: E2M1 codes x2 as int8 (a PRMT table on the shared-memory store), dp4a over each 16-block, then the
//                block's int32 turned into FP32 (the 2^23 + 2^22 bias trick: one FADD) and FFMA'd with the two UE4M3 scales
// References: cuBLAS SGEMM in pedantic math (NVIDIA's SIMT kernel) and cuBLAS BF16 GemmEx (tensor cores), same operands.
//
// Gates, per (variant, config, shape) before timing:
//   - bit-exact on 256 sampled words against a device emulation of the same arithmetic in the same order (split-K 1);
//     with split-K > 1 (atomics, order not fixed) a tolerance against FP64 instead;
//   - the SASS gate (no HMMA/IMMA/QMMA/OMMA/HGMMA/UTC* in any gemm_kernel) is the fill script's, from cuobjdump.
// Timing: back-to-back launches for a fixed GPU time per config, in batches of >= 2 ms each timed by one event pair,
// operands rotated over enough sets that they exceed 2x L2 at small shapes. Screening numbers, not a panel row.
//
//   nvcc -O3 -std=c++17 -gencode arch=compute_120a,code=sm_120a -Xptxas -v generic_gemm_sm120.cu -lcublas -o generic_gemm
//   ./generic_gemm M N K SECONDS [variant,...]      (JSON lines on stdout; GPU_LEASE_UUID, if set, must be the device's)
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

#include <cublas_v2.h>
#include <cuda_bf16.h>
#include <cuda_fp16.h>
#include <cuda_runtime.h>

#define CK(x)                                                                                    \
  do {                                                                                           \
    cudaError_t e_ = (x);                                                                        \
    if (e_ != cudaSuccess) {                                                                     \
      fprintf(stderr, "%s:%d %s: %s\n", __FILE__, __LINE__, #x, cudaGetErrorString(e_));         \
      exit(1);                                                                                   \
    }                                                                                            \
  } while (0)
#define CB(x)                                                                                    \
  do {                                                                                           \
    cublasStatus_t s_ = (x);                                                                     \
    if (s_ != CUBLAS_STATUS_SUCCESS) {                                                           \
      fprintf(stderr, "%s:%d %s: cublas status %d\n", __FILE__, __LINE__, #x, (int)s_);          \
      exit(1);                                                                                   \
    }                                                                                            \
  } while (0)

enum Var { FFMA_F32, FFMA_BF16, HFMA2_F16, HFMA2_BF16, DP4A_S8, DP4A_NVFP4, NVAR };
static const char* VNAME[NVAR] = {"ffma_f32", "ffma_bf16", "hfma2_f16", "hfma2_bf16", "dp4a_s8", "dp4a_nvfp4"};

// k elements per global word of A, and per shared-memory row
__host__ __device__ constexpr int kpw_a(int v) { return v == FFMA_F32 ? 1 : v == DP4A_S8 ? 4 : v == DP4A_NVFP4 ? 8 : 2; }
__host__ __device__ constexpr int kps(int v) { return (v == DP4A_S8 || v == DP4A_NVFP4) ? 4 : 1; }
// shared-memory rows per global word of A (along k)
__host__ __device__ constexpr int xa(int v) { return (v == FFMA_F32 || v == DP4A_S8) ? 1 : 2; }
__host__ __device__ constexpr bool packed_out(int v) { return v == HFMA2_F16 || v == HFMA2_BF16; }
// global rows of B per tile, and global words of B per tile row
__host__ __device__ constexpr int gb_rows(int v, int bks) { return v == DP4A_NVFP4 ? bks / 2 : bks; }
__host__ __device__ constexpr int gb_words(int v, int bnw) { return v == FFMA_BF16 ? bnw / 2 : bnw; }
// words per row of B in global memory, for N output columns
__host__ __device__ inline int64_t b_row_words(int v, int64_t N) { return (v == FFMA_BF16 || packed_out(v)) ? N / 2 : N; }

__device__ __forceinline__ float bf16lo(uint32_t x) { return __uint_as_float(x << 16); }
__device__ __forceinline__ float bf16hi(uint32_t x) { return __uint_as_float(x & 0xFFFF0000u); }

// four E2M1 codes (the low 16 bits, first code lowest) -> four int8 (2 x value, in [-12, 12])
__device__ __forceinline__ uint32_t e2m1x4_to_s8x4(uint32_t x) {
  const uint32_t sel = x & 0x7777u;
  const uint32_t pos = __byte_perm(0x03020100u, 0x0C080604u, sel);
  const uint32_t neg = __byte_perm(0xFDFEFF00u, 0xF4F8FAFCu, sel);  // 0,-1,-2,-3 | -4,-6,-8,-12
  const uint32_t spread = (x & 0xFu) | ((x & 0xF0u) << 4) | ((x & 0xF00u) << 8) | ((x & 0xF000u) << 12);
  const uint32_t mask = ((spread >> 3) & 0x01010101u) * 0xFFu;
  return pos ^ ((pos ^ neg) & mask);
}
// UE4M3 scale byte -> 0.5 * value (normal codes only; the generator never draws exponent 0)
__device__ __forceinline__ float ue4m3_half(uint32_t b) {
  const uint32_t e = (b >> 3) & 0xFu, m = b & 7u;
  return __uint_as_float(((e + 119u) << 23) | (m << 20));
}

template <int V, int BM, int BNW, int BKS>
__global__ void __launch_bounds__((BM / 8) * (BNW / 8))
    gemm_kernel(int M, int N, int K, int splits, const uint32_t* __restrict__ A, const uint32_t* __restrict__ B,
                const uint8_t* __restrict__ SA, const uint8_t* __restrict__ SB, uint32_t* __restrict__ C) {
  constexpr int TM = 8, TN = 8, NT = (BM / TM) * (BNW / TN);
  constexpr int GA = BKS / xa(V), LA = BM * GA / NT;
  constexpr int GBR = gb_rows(V, BKS), GBW = gb_words(V, BNW), LB = GBR * GBW / NT;
  constexpr int KPT = BKS * kps(V);  // k per tile
  constexpr bool NV = V == DP4A_NVFP4;
  constexpr int BPT = NV ? BKS / 4 : 1;  // NVFP4 16-blocks per tile
  static_assert(LA >= 1 && LA * NT == BM * GA, "A tile split");
  static_assert(LB >= 1 && LB * NT == GBR * GBW, "B tile split");
  static_assert(!NV || BKS % 4 == 0, "NVFP4 tile holds whole blocks");

  __shared__ __align__(16) uint32_t As[2][BKS][BM + 4];
  __shared__ __align__(16) uint32_t Bs[2][BKS][BNW];
  __shared__ __align__(16) float SAs[2][BPT][BM];
  __shared__ __align__(16) float SBs[2][BPT][BNW];

  const int tid = threadIdx.x, tx = tid % (BNW / TN), ty = tid / (BNW / TN);
  const int m0 = blockIdx.y * BM;
  const int NW = packed_out(V) ? N / 2 : N;  // words per row of C
  const int n0 = blockIdx.x * BNW;           // first word column of C
  const int64_t KAW = K / kpw_a(V);
  const int64_t BW = b_row_words(V, N);
  const int64_t nb0 = (int64_t)blockIdx.x * GBW;
  const int tiles = K / KPT / splits, t0 = blockIdx.z * tiles;
  const int KB = K / 16;

  uint32_t ra[LA], rb[LB];
  uint8_t rsa[NV ? (BM * BPT + NT - 1) / NT : 1], rsb[NV ? (BPT * BNW + NT - 1) / NT : 1];

  auto load = [&](int t) {
#pragma unroll
    for (int l = 0; l < LA; ++l) {
      const int idx = tid + l * NT, r = idx / GA, c = idx % GA;
      ra[l] = A[(int64_t)(m0 + r) * KAW + (int64_t)t * GA + c];
    }
#pragma unroll
    for (int l = 0; l < LB; ++l) {
      const int idx = tid + l * NT, r = idx / GBW, c = idx % GBW;
      rb[l] = B[((int64_t)t * GBR + r) * BW + nb0 + c];
    }
    if constexpr (NV) {
#pragma unroll
      for (int l = 0; l < (int)sizeof(rsa); ++l) {
        const int idx = tid + l * NT;
        if (idx < BM * BPT) rsa[l] = SA[(int64_t)(m0 + idx / BPT) * KB + t * BPT + idx % BPT];
      }
#pragma unroll
      for (int l = 0; l < (int)sizeof(rsb); ++l) {
        const int idx = tid + l * NT;
        if (idx < BPT * BNW) rsb[l] = SB[(int64_t)(t * BPT + idx / BNW) * N + n0 + idx % BNW];
      }
    }
  };
  auto store = [&](int buf) {
#pragma unroll
    for (int l = 0; l < LA; ++l) {
      const int idx = tid + l * NT, r = idx / GA, c = idx % GA;
      const uint32_t x = ra[l];
      if constexpr (V == FFMA_F32 || V == DP4A_S8) {
        As[buf][c][r] = x;
      } else if constexpr (V == FFMA_BF16) {
        As[buf][2 * c][r] = __float_as_uint(bf16lo(x));
        As[buf][2 * c + 1][r] = __float_as_uint(bf16hi(x));
      } else if constexpr (packed_out(V)) {
        As[buf][2 * c][r] = (x & 0xFFFFu) * 0x10001u;
        As[buf][2 * c + 1][r] = (x >> 16) * 0x10001u;
      } else {
        As[buf][2 * c][r] = e2m1x4_to_s8x4(x & 0xFFFFu);
        As[buf][2 * c + 1][r] = e2m1x4_to_s8x4(x >> 16);
      }
    }
#pragma unroll
    for (int l = 0; l < LB; ++l) {
      const int idx = tid + l * NT, r = idx / GBW, c = idx % GBW;
      const uint32_t x = rb[l];
      if constexpr (V == FFMA_BF16) {
        Bs[buf][r][2 * c] = __float_as_uint(bf16lo(x));
        Bs[buf][r][2 * c + 1] = __float_as_uint(bf16hi(x));
      } else if constexpr (NV) {
        Bs[buf][2 * r][c] = e2m1x4_to_s8x4(x & 0xFFFFu);
        Bs[buf][2 * r + 1][c] = e2m1x4_to_s8x4(x >> 16);
      } else {
        Bs[buf][r][c] = x;
      }
    }
    if constexpr (NV) {
#pragma unroll
      for (int l = 0; l < (int)sizeof(rsa); ++l) {
        const int idx = tid + l * NT;
        if (idx < BM * BPT) SAs[buf][idx % BPT][idx / BPT] = ue4m3_half(rsa[l]);
      }
#pragma unroll
      for (int l = 0; l < (int)sizeof(rsb); ++l) {
        const int idx = tid + l * NT;
        if (idx < BPT * BNW) SBs[buf][idx / BNW][idx % BNW] = ue4m3_half(rsb[l]);
      }
    }
  };

  uint32_t acc[TM][TN];  // float bits, int32, or a packed pair
  float accf[NV ? TM : 1][NV ? TN : 1];
#pragma unroll
  for (int i = 0; i < TM; ++i)
#pragma unroll
    for (int j = 0; j < TN; ++j) {
      acc[i][j] = 0u;
      if constexpr (NV) accf[i][j] = 0.f;
    }

  load(t0);
  store(0);
  __syncthreads();
  for (int t = 0; t < tiles; ++t) {
    const int buf = t & 1;
    if (t + 1 < tiles) load(t0 + t + 1);
#pragma unroll
    for (int ks = 0; ks < BKS; ++ks) {
      const uint4 qa0 = *(const uint4*)&As[buf][ks][ty * 4], qa1 = *(const uint4*)&As[buf][ks][BM / 2 + ty * 4];
      const uint4 qb0 = *(const uint4*)&Bs[buf][ks][tx * 4], qb1 = *(const uint4*)&Bs[buf][ks][BNW / 2 + tx * 4];
      const uint32_t a[TM] = {qa0.x, qa0.y, qa0.z, qa0.w, qa1.x, qa1.y, qa1.z, qa1.w};
      const uint32_t b[TN] = {qb0.x, qb0.y, qb0.z, qb0.w, qb1.x, qb1.y, qb1.z, qb1.w};
#pragma unroll
      for (int i = 0; i < TM; ++i)
#pragma unroll
        for (int j = 0; j < TN; ++j) {
          if constexpr (V == FFMA_F32 || V == FFMA_BF16) {
            acc[i][j] = __float_as_uint(fmaf(__uint_as_float(a[i]), __uint_as_float(b[j]), __uint_as_float(acc[i][j])));
          } else if constexpr (V == HFMA2_F16) {
            asm("fma.rn.f16x2 %0, %1, %2, %0;" : "+r"(acc[i][j]) : "r"(a[i]), "r"(b[j]));
          } else if constexpr (V == HFMA2_BF16) {
            asm("fma.rn.bf16x2 %0, %1, %2, %0;" : "+r"(acc[i][j]) : "r"(a[i]), "r"(b[j]));
          } else if constexpr (V == DP4A_S8) {
            acc[i][j] = (uint32_t)__dp4a((int)a[i], (int)b[j], (int)acc[i][j]);
          } else {  // NVFP4: a block's first dp4a starts from the bias 0x4B400000 = 1.5 * 2^23
            acc[i][j] = (uint32_t)__dp4a((int)a[i], (int)b[j], (ks % 4 == 0) ? 0x4B400000 : (int)acc[i][j]);
          }
        }
      if constexpr (NV) {
        if (ks % 4 == 3) {
          const float4 s0 = *(const float4*)&SAs[buf][ks / 4][ty * 4], s1 = *(const float4*)&SAs[buf][ks / 4][BM / 2 + ty * 4];
          const float4 u0 = *(const float4*)&SBs[buf][ks / 4][tx * 4], u1 = *(const float4*)&SBs[buf][ks / 4][BNW / 2 + tx * 4];
          const float sa[TM] = {s0.x, s0.y, s0.z, s0.w, s1.x, s1.y, s1.z, s1.w};
          const float sb[TN] = {u0.x, u0.y, u0.z, u0.w, u1.x, u1.y, u1.z, u1.w};
#pragma unroll
          for (int i = 0; i < TM; ++i)
#pragma unroll
            for (int j = 0; j < TN; ++j)
              accf[i][j] = fmaf(__uint_as_float(acc[i][j]) - 12582912.0f, sa[i] * sb[j], accf[i][j]);
        }
      }
    }
    if (t + 1 < tiles) store(buf ^ 1);
    __syncthreads();
  }

#pragma unroll
  for (int i = 0; i < TM; ++i) {
    const int r = m0 + (i < 4 ? ty * 4 + i : BM / 2 + ty * 4 + i - 4);
#pragma unroll
    for (int h = 0; h < 2; ++h) {
      const int c = n0 + (h == 0 ? tx * 4 : BNW / 2 + tx * 4);
      uint32_t w[4];
#pragma unroll
      for (int j = 0; j < 4; ++j) {
        if constexpr (NV) w[j] = __float_as_uint(accf[i][h * 4 + j]);
        else w[j] = acc[i][h * 4 + j];
      }
      uint32_t* dst = C + (int64_t)r * NW + c;
      if (splits == 1) {
        *(uint4*)dst = make_uint4(w[0], w[1], w[2], w[3]);
      } else {
#pragma unroll
        for (int j = 0; j < 4; ++j) {
          if constexpr (V == DP4A_S8) atomicAdd((int*)&dst[j], (int)w[j]);
          else if constexpr (V == HFMA2_F16) atomicAdd((__half2*)&dst[j], *(__half2*)&w[j]);
          else if constexpr (V == HFMA2_BF16) atomicAdd((__nv_bfloat162*)&dst[j], *(__nv_bfloat162*)&w[j]);
          else atomicAdd((float*)&dst[j], __uint_as_float(w[j]));
        }
      }
    }
  }
}

// ---- operands ----------------------------------------------------------------------------------------------------------
__device__ __forceinline__ uint32_t mix(uint64_t x) {
  x ^= x >> 33; x *= 0xff51afd7ed558ccdULL; x ^= x >> 33; x *= 0xc4ceb9fe1a85ec53ULL; x ^= x >> 33;
  return (uint32_t)x;
}
__device__ __forceinline__ float unif(uint32_t h) { return (float)(h >> 8) * (2.0f / 16777216.0f) - 1.0f; }
__device__ __forceinline__ uint32_t to_bf16(float f) { return __bfloat16_as_ushort(__float2bfloat16_rn(f)); }
__device__ __forceinline__ uint32_t to_f16(float f) { return __half_as_ushort(__float2half_rn(f)); }

// kind: 0 float, 1 bf16 pairs, 2 f16 pairs, 3 random bytes / codes, 4 UE4M3 scale bytes (4 per word, exponent 5..9)
__global__ void fill_words(uint32_t* p, int64_t n, uint64_t seed, int kind) {
  for (int64_t i = blockIdx.x * (int64_t)blockDim.x + threadIdx.x; i < n; i += (int64_t)gridDim.x * blockDim.x) {
    const uint32_t h0 = mix(seed * 0x9E3779B97F4A7C15ULL + 2 * i), h1 = mix(seed * 0x9E3779B97F4A7C15ULL + 2 * i + 1);
    uint32_t w;
    if (kind == 0) w = __float_as_uint(unif(h0));
    else if (kind == 1) w = to_bf16(unif(h0)) | (to_bf16(unif(h1)) << 16);
    else if (kind == 2) w = to_f16(unif(h0)) | (to_f16(unif(h1)) << 16);
    else if (kind == 3) w = h0;
    else {
      w = 0;
      for (int b = 0; b < 4; ++b) {
        const uint32_t hb = (h0 >> (8 * b)) & 0xFFu;
        w |= ((((5 + hb % 5) << 3) | ((hb >> 4) & 7u)) & 0xFFu) << (8 * b);
      }
    }
    p[i] = w;
  }
}

// ---- reference: the same arithmetic, in the same order, for sampled words (exact), and an FP64 sum with sum |terms| ------
__device__ float e2m1_val(uint32_t c) {
  const float mag[8] = {0.f, 0.5f, 1.f, 1.5f, 2.f, 3.f, 4.f, 6.f};
  return (c & 8u) ? -mag[c & 7u] : mag[c & 7u];
}
__device__ uint32_t half_of(uint32_t w, int h) { return h ? (w >> 16) : (w & 0xFFFFu); }

template <int V>
__global__ void reference(int M, int N, int K, const uint32_t* A, const uint32_t* B, const uint8_t* SA, const uint8_t* SB,
                          const int* ri, const int* cj, int ns, uint32_t* exact, double* ref, double* absum) {
  const int s = blockIdx.x * blockDim.x + threadIdx.x;
  if (s >= ns) return;
  const int i = ri[s], j = cj[s];  // j is a word column of C
  const int64_t KAW = K / kpw_a(V), BW = b_row_words(V, N);
  double r = 0, a_ = 0;
  if constexpr (V == FFMA_F32 || V == FFMA_BF16) {
    float acc = 0.f;
    for (int k = 0; k < K; ++k) {
      float a, b;
      if constexpr (V == FFMA_F32) {
        a = __uint_as_float(A[(int64_t)i * K + k]);
        b = __uint_as_float(B[(int64_t)k * N + j]);
      } else {
        a = __uint_as_float(half_of(A[(int64_t)i * KAW + k / 2], k & 1) << 16);
        b = __uint_as_float(half_of(B[(int64_t)k * BW + j / 2], j & 1) << 16);
      }
      acc = fmaf(a, b, acc);
      r += (double)a * b;
      a_ += fabs((double)a * b);
    }
    exact[s] = __float_as_uint(acc);
  } else if constexpr (packed_out(V)) {
    uint32_t out = 0;
    for (int h = 0; h < 2; ++h) {
      double acc = 0;
      for (int k = 0; k < K; ++k) {
        const uint32_t ah = half_of(A[(int64_t)i * KAW + k / 2], k & 1), bh = half_of(B[(int64_t)k * BW + j], h);
        double a, b;
        if constexpr (V == HFMA2_F16) {
          a = __half2float(__ushort_as_half((unsigned short)ah));
          b = __half2float(__ushort_as_half((unsigned short)bh));
          acc = __half2float(__double2half(a * b + acc));
        } else {
          a = __bfloat162float(__ushort_as_bfloat16((unsigned short)ah));
          b = __bfloat162float(__ushort_as_bfloat16((unsigned short)bh));
          acc = __bfloat162float(__double2bfloat16(a * b + acc));
        }
        if (h == 0) { r += a * b; a_ += fabs(a * b); }
      }
      const uint32_t bits = V == HFMA2_F16 ? __half_as_ushort(__double2half(acc)) : __bfloat16_as_ushort(__double2bfloat16(acc));
      out |= bits << (16 * h);
    }
    exact[s] = out;
  } else if constexpr (V == DP4A_S8) {
    long long acc = 0;
    for (int k = 0; k < K; ++k) {
      const int a = (int8_t)(A[(int64_t)i * KAW + k / 4] >> (8 * (k % 4)));
      const int b = (int8_t)(B[(int64_t)(k / 4) * N + j] >> (8 * (k % 4)));
      acc += (long long)a * b;
      a_ += fabs((double)a * b);
    }
    r = (double)acc;
    exact[s] = (uint32_t)(int)acc;
  } else {
    float acc = 0.f;
    for (int kb = 0; kb < K / 16; ++kb) {
      const float sa = ue4m3_half(SA[(int64_t)i * (K / 16) + kb]), sb = ue4m3_half(SB[(int64_t)kb * N + j]);
      int p = 0;
      for (int k = kb * 16; k < kb * 16 + 16; ++k) {
        const uint32_t ca = (A[(int64_t)i * KAW + k / 8] >> (4 * (k % 8))) & 0xFu;
        const uint32_t cb = (B[(int64_t)(k / 8) * N + j] >> (4 * (k % 8))) & 0xFu;
        p += (int)(2 * e2m1_val(ca)) * (int)(2 * e2m1_val(cb));
        const double t = (double)e2m1_val(ca) * e2m1_val(cb) * (4.0 * sa * sb);
        r += t;
        a_ += fabs(t);
      }
      acc = fmaf((float)p, sa * sb, acc);
    }
    exact[s] = __float_as_uint(acc);
  }
  ref[s] = r;
  absum[s] = a_;
}

// ---- host ---------------------------------------------------------------------------------------------------------------
struct Cfg { int bm, bnw, bks; };
static const Cfg CFGS[] = {{128, 128, 8}, {128, 128, 16}, {128, 64, 8}, {64, 128, 8},
                           {32, 256, 16},  {64, 256, 8},   {256, 64, 8}, {64, 64, 16}};
constexpr int NCFG = sizeof(CFGS) / sizeof(CFGS[0]);

typedef void (*KernFn)(int, int, int, int, const uint32_t*, const uint32_t*, const uint8_t*, const uint8_t*, uint32_t*);
template <int V> KernFn kern(int c) {
  switch (c) {
    case 0: return gemm_kernel<V, 128, 128, 8>;
    case 1: return gemm_kernel<V, 128, 128, 16>;
    case 2: return gemm_kernel<V, 128, 64, 8>;
    case 3: return gemm_kernel<V, 64, 128, 8>;
    case 4: return gemm_kernel<V, 32, 256, 16>;
    case 5: return gemm_kernel<V, 64, 256, 8>;
    case 6: return gemm_kernel<V, 256, 64, 8>;
    default: return gemm_kernel<V, 64, 64, 16>;
  }
}
static KernFn kern_of(int v, int c) {
  switch (v) {
    case FFMA_F32: return kern<FFMA_F32>(c);
    case FFMA_BF16: return kern<FFMA_BF16>(c);
    case HFMA2_F16: return kern<HFMA2_F16>(c);
    case HFMA2_BF16: return kern<HFMA2_BF16>(c);
    case DP4A_S8: return kern<DP4A_S8>(c);
    default: return kern<DP4A_NVFP4>(c);
  }
}
typedef void (*RefFn)(int, int, int, const uint32_t*, const uint32_t*, const uint8_t*, const uint8_t*, const int*, const int*,
                      int, uint32_t*, double*, double*);
static RefFn ref_of(int v) {
  switch (v) {
    case FFMA_F32: return reference<FFMA_F32>;
    case FFMA_BF16: return reference<FFMA_BF16>;
    case HFMA2_F16: return reference<HFMA2_F16>;
    case HFMA2_BF16: return reference<HFMA2_BF16>;
    case DP4A_S8: return reference<DP4A_S8>;
    default: return reference<DP4A_NVFP4>;
  }
}

struct Set { uint32_t *A, *B; uint8_t *SA, *SB; };

static double pct(std::vector<double> v, double q) {
  std::sort(v.begin(), v.end());
  return v[(size_t)std::min<double>(v.size() - 1, std::floor(q * (v.size() - 1) + 0.5))];
}

// Launch `fn(set)` back to back for `seconds` of GPU time; returns per-call ms samples.
template <typename F> static std::vector<double> timed(F fn, int nsets, double seconds) {
  cudaEvent_t e0, e1;
  CK(cudaEventCreate(&e0)); CK(cudaEventCreate(&e1));
  for (int w = 0; w < 3; ++w) fn(w % nsets);
  CK(cudaDeviceSynchronize());
  CK(cudaEventRecord(e0));
  fn(0);
  CK(cudaEventRecord(e1)); CK(cudaEventSynchronize(e1));
  float one; CK(cudaEventElapsedTime(&one, e0, e1));
  const int batch = std::max(1, (int)std::ceil(2.0 / std::max(one, 1e-4f)));
  std::vector<double> ms;
  double total = 0;
  int it = 0;
  while (total < seconds * 1000.0 || ms.size() < 10) {
    CK(cudaEventRecord(e0));
    for (int b = 0; b < batch; ++b) fn((it++) % nsets);
    CK(cudaEventRecord(e1)); CK(cudaEventSynchronize(e1));
    float t; CK(cudaEventElapsedTime(&t, e0, e1));
    ms.push_back(t / batch);
    total += t;
  }
  CK(cudaGetLastError());
  CK(cudaEventDestroy(e0)); CK(cudaEventDestroy(e1));
  return ms;
}

static std::string uuid_str(const cudaUUID_t& u) {
  const unsigned char* b = (const unsigned char*)u.bytes;
  char s[64];
  snprintf(s, sizeof s, "GPU-%02x%02x%02x%02x-%02x%02x-%02x%02x-%02x%02x-%02x%02x%02x%02x%02x%02x", b[0], b[1], b[2], b[3], b[4],
           b[5], b[6], b[7], b[8], b[9], b[10], b[11], b[12], b[13], b[14], b[15]);
  return s;
}

int main(int argc, char** argv) {
  if (argc < 5) { fprintf(stderr, "usage: %s M N K SECONDS [variant,...]\n", argv[0]); return 2; }
  const int M = atoi(argv[1]), N = atoi(argv[2]), K = atoi(argv[3]);
  const double secs = atof(argv[4]);
  std::string only = argc > 5 ? argv[5] : "";

  cudaDeviceProp prop; CK(cudaGetDeviceProperties(&prop, 0));
  const std::string uuid = uuid_str(prop.uuid);
  const char* want = getenv("GPU_LEASE_UUID");
  if (want && *want && uuid != want) { fprintf(stderr, "device is %s, the lease gave %s\n", uuid.c_str(), want); return 3; }
  const int sms = prop.multiProcessorCount;
  printf("{\"kind\":\"device\",\"name\":\"%s\",\"uuid\":\"%s\",\"sms\":%d,\"cc\":\"%d.%d\",\"l2_bytes\":%d}\n", prop.name,
         uuid.c_str(), sms, prop.major, prop.minor, prop.l2CacheSize);
  fflush(stdout);

  const int64_t words_a = (int64_t)M * K, words_b = (int64_t)K * N, words_c = (int64_t)M * N;  // upper bounds (f32)
  std::vector<Set> sets;
  auto ensure_sets = [&](int n) {
    while ((int)sets.size() < n) {
      Set s;
      CK(cudaMalloc(&s.A, words_a * 4)); CK(cudaMalloc(&s.B, words_b * 4));
      CK(cudaMalloc(&s.SA, (int64_t)M * K / 16 + 16)); CK(cudaMalloc(&s.SB, (int64_t)K / 16 * N + 16));
      sets.push_back(s);
    }
  };
  uint32_t* C; CK(cudaMalloc(&C, words_c * 4));

  const int NS = 256;
  std::vector<int> hri(NS), hcj(NS);
  uint64_t lcg = 0x243F6A8885A308D3ULL ^ ((uint64_t)M << 40) ^ ((uint64_t)N << 20) ^ (uint64_t)K;
  auto nxt = [&]() { lcg = lcg * 6364136223846793005ULL + 1442695040888963407ULL; return (uint32_t)(lcg >> 33); };
  int *dri, *dcj; uint32_t* dex; double *dref, *dabs;
  CK(cudaMalloc(&dri, NS * 4)); CK(cudaMalloc(&dcj, NS * 4)); CK(cudaMalloc(&dex, NS * 4));
  CK(cudaMalloc(&dref, NS * 8)); CK(cudaMalloc(&dabs, NS * 8));

  cublasHandle_t h; CB(cublasCreate(&h));

  for (int v = 0; v < NVAR; ++v) {
    if (!only.empty() && ("," + only + ",").find("," + std::string(VNAME[v]) + ",") == std::string::npos) continue;
    const int kindA = v == FFMA_F32 ? 0 : v == HFMA2_F16 ? 2 : (v == FFMA_BF16 || v == HFMA2_BF16) ? 1 : 3;
    const int64_t wa = (int64_t)M * K / kpw_a(v);
    const int64_t wb = (int64_t)K * N / ((v == FFMA_F32) ? 1 : (v == DP4A_S8) ? 4 : (v == DP4A_NVFP4) ? 8 : 2);
    const int64_t set_bytes = (wa + wb) * 4 + (v == DP4A_NVFP4 ? ((int64_t)M + N) * K / 16 : 0);
    const int nsets = (int)std::max<int64_t>(1, std::min<int64_t>(16, (4LL * prop.l2CacheSize + set_bytes - 1) / set_bytes));
    ensure_sets(nsets);
    for (int si = 0; si < nsets; ++si) {
      fill_words<<<1024, 256>>>(sets[si].A, wa, 1000 * v + 2 * si + 1, kindA);
      fill_words<<<1024, 256>>>(sets[si].B, wb, 1000 * v + 2 * si + 2, kindA);
      if (v == DP4A_NVFP4) {
        fill_words<<<256, 256>>>((uint32_t*)sets[si].SA, (int64_t)M * K / 64, 1000 * v + 2 * si + 101, 4);
        fill_words<<<256, 256>>>((uint32_t*)sets[si].SB, (int64_t)K / 64 * N, 1000 * v + 2 * si + 102, 4);
      }
    }
    CK(cudaDeviceSynchronize());
    const int NW = packed_out(v) ? N / 2 : N;

    for (int c = 0; c < NCFG; ++c) {
      const Cfg cf = CFGS[c];
      const int kpt = cf.bks * kps(v);
      if (M % cf.bm || NW % cf.bnw || K % kpt) continue;
      const int ctas = (M / cf.bm) * (NW / cf.bnw);
      int splits = 1;
      while (ctas * splits < 2 * sms && (K / kpt) % (2 * splits) == 0 && K / kpt / (2 * splits) >= 8) splits *= 2;
      const dim3 grid(NW / cf.bnw, M / cf.bm, splits), block((cf.bm / 8) * (cf.bnw / 8));
      KernFn fn = kern_of(v, c);
      cudaFuncAttributes fa; CK(cudaFuncGetAttributes(&fa, (const void*)fn));
      int occ = 0; CK(cudaOccupancyMaxActiveBlocksPerMultiprocessor(&occ, (const void*)fn, block.x, 0));
      auto launch = [&](int si) {
        if (splits > 1) CK(cudaMemsetAsync(C, 0, (int64_t)M * NW * 4));
        fn<<<grid, block>>>(M, N, K, splits, sets[si].A, sets[si].B, sets[si].SA, sets[si].SB, C);
      };
      // gate
      for (int s = 0; s < NS; ++s) { hri[s] = nxt() % M; hcj[s] = nxt() % NW; }
      CK(cudaMemcpy(dri, hri.data(), NS * 4, cudaMemcpyHostToDevice));
      CK(cudaMemcpy(dcj, hcj.data(), NS * 4, cudaMemcpyHostToDevice));
      launch(0);
      CK(cudaGetLastError());
      CK(cudaDeviceSynchronize());
      std::vector<uint32_t> got(NS), ex(NS);
      std::vector<double> rf(NS), ab(NS);
      for (int s = 0; s < NS; ++s) CK(cudaMemcpy(&got[s], C + (int64_t)hri[s] * NW + hcj[s], 4, cudaMemcpyDeviceToHost));
      ref_of(v)<<<(NS + 127) / 128, 128>>>(M, N, K, sets[0].A, sets[0].B, sets[0].SA, sets[0].SB, dri, dcj, NS, dex, dref, dabs);
      CK(cudaGetLastError());
      CK(cudaMemcpy(ex.data(), dex, NS * 4, cudaMemcpyDeviceToHost));
      CK(cudaMemcpy(rf.data(), dref, NS * 8, cudaMemcpyDeviceToHost));
      CK(cudaMemcpy(ab.data(), dabs, NS * 8, cudaMemcpyDeviceToHost));
      int exact_ok = 0;
      double worst = 0;
      for (int s = 0; s < NS; ++s) {
        exact_ok += got[s] == ex[s];
        double g;
        if (v == DP4A_S8) g = (double)(int)got[s];
        else if (v == HFMA2_F16) g = __half2float(__ushort_as_half((unsigned short)(got[s] & 0xFFFF)));
        else {
          const uint32_t bits = v == HFMA2_BF16 ? (got[s] & 0xFFFFu) << 16 : got[s];
          float f; memcpy(&f, &bits, 4); g = f;
        }
        worst = std::max(worst, std::fabs(g - rf[s]) / std::max(ab[s], 1e-30));
      }
      const double tol = v == HFMA2_BF16 ? 5e-2 : v == HFMA2_F16 ? 1e-2 : v == DP4A_S8 ? 0 : 2e-4;
      const bool pass = splits == 1 ? exact_ok == NS : worst <= tol;
      std::vector<double> ms;
      if (pass) ms = timed(launch, nsets, secs);
      const double macs = (double)M * N * K;
      const double med = ms.empty() ? 0 : pct(ms, 0.5);
      printf("{\"kind\":\"kernel\",\"variant\":\"%s\",\"cfg\":\"bm%d_bnw%d_bks%d\",\"M\":%d,\"N\":%d,\"K\":%d,\"splits\":%d,"
             "\"threads\":%d,\"regs\":%d,\"local_bytes\":%zu,\"ctas_per_sm\":%d,\"gate\":{\"sampled\":%d,\"bit_exact\":%d,"
             "\"worst_rel_to_abs_sum\":%.3e,\"tol\":%.1e,\"pass\":%s},\"reps\":%zu,\"ms_median\":%.5f,\"ms_p10\":%.5f,"
             "\"ms_p90\":%.5f,\"tmacs\":%.3f,\"nsets\":%d}\n",
             VNAME[v], cf.bm, cf.bnw, cf.bks, M, N, K, splits, block.x, fa.numRegs, fa.localSizeBytes, occ, NS, exact_ok,
             worst, tol, pass ? "true" : "false", ms.size(), med, ms.empty() ? 0 : pct(ms, 0.1),
             ms.empty() ? 0 : pct(ms, 0.9), med > 0 ? macs / (med * 1e-3) / 1e12 : 0.0, nsets);
      fflush(stdout);
    }

    // cuBLAS references on the same operands (column-major: C^T = B^T A^T)
    if (v == FFMA_F32 || v == FFMA_BF16) {
      const float one = 1.f, zero = 0.f;
      const bool bf = v == FFMA_BF16;
      CB(cublasSetMathMode(h, bf ? CUBLAS_DEFAULT_MATH : CUBLAS_PEDANTIC_MATH));
      auto launch = [&](int si) {
        if (bf)
          CB(cublasGemmEx(h, CUBLAS_OP_N, CUBLAS_OP_N, N, M, K, &one, sets[si].B, CUDA_R_16BF, N, sets[si].A, CUDA_R_16BF, K,
                          &zero, C, CUDA_R_32F, N, CUBLAS_COMPUTE_32F, CUBLAS_GEMM_DEFAULT));
        else
          CB(cublasSgemm(h, CUBLAS_OP_N, CUBLAS_OP_N, N, M, K, &one, (const float*)sets[si].B, N, (const float*)sets[si].A, K,
                         &zero, (float*)C, N));
      };
      for (int s = 0; s < NS; ++s) { hri[s] = nxt() % M; hcj[s] = nxt() % N; }
      CK(cudaMemcpy(dri, hri.data(), NS * 4, cudaMemcpyHostToDevice));
      CK(cudaMemcpy(dcj, hcj.data(), NS * 4, cudaMemcpyHostToDevice));
      launch(0);
      CK(cudaDeviceSynchronize());
      ref_of(v)<<<(NS + 127) / 128, 128>>>(M, N, K, sets[0].A, sets[0].B, nullptr, nullptr, dri, dcj, NS, dex, dref, dabs);
      std::vector<double> rf(NS), ab(NS);
      CK(cudaMemcpy(rf.data(), dref, NS * 8, cudaMemcpyDeviceToHost));
      CK(cudaMemcpy(ab.data(), dabs, NS * 8, cudaMemcpyDeviceToHost));
      double worst = 0;
      for (int s = 0; s < NS; ++s) {
        float f; CK(cudaMemcpy(&f, (float*)C + (int64_t)hri[s] * N + hcj[s], 4, cudaMemcpyDeviceToHost));
        worst = std::max(worst, std::fabs(f - rf[s]) / std::max(ab[s], 1e-30));
      }
      const bool pass = worst <= 2e-4;
      std::vector<double> ms;
      if (pass) ms = timed(launch, nsets, secs);
      const double med = ms.empty() ? 0 : pct(ms, 0.5);
      printf("{\"kind\":\"reference\",\"variant\":\"%s\",\"M\":%d,\"N\":%d,\"K\":%d,\"gate\":{\"worst_rel_to_abs_sum\":%.3e,"
             "\"pass\":%s},\"reps\":%zu,\"ms_median\":%.5f,\"ms_p10\":%.5f,\"ms_p90\":%.5f,\"tmacs\":%.3f,\"nsets\":%d}\n",
             bf ? "cublas_bf16_tensor" : "cublas_sgemm_pedantic", M, N, K, worst, pass ? "true" : "false", ms.size(), med,
             ms.empty() ? 0 : pct(ms, 0.1), ms.empty() ? 0 : pct(ms, 0.9),
             med > 0 ? (double)M * N * K / (med * 1e-3) / 1e12 : 0.0, nsets);
      fflush(stdout);
    }
  }
  CB(cublasDestroy(h));
  return 0;
}
