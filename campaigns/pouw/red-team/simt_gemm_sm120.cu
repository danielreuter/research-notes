// Writer: bc-cb8013f7 (by its own report), an agent the sm_120 PoUW coordinator (bc-2aa33ad8) started by mistake, not the assessor. The assessor (bc-d7d4b0d1) reviewed and adopted it (run r20260930-085618-5cfa), 30 Sep 2026.
// Red-team fill job (bc-d7d4b0d1): the fastest non-tensor-core GEMM on one RTX PRO 6000 (sm_120a), for the MVP cost
// model's generic-core rate and `no-exact-rewrite/*`'s CUDA-core routes, measured as whole GEMMs rather than peaks.
//
//   C[m x n] = A[m x k] . B[n x k]^T   (TN, both K-major, as the harness times its baselines)
//
// Kinds (the global format -> what the mainloop multiplies):
//   f32_ffma     f32            -> FFMA, f32 accumulate
//   bf16_ffma    bf16           -> f32 on staging, FFMA
//   e4m3_ffma    E4M3           -> f32 on staging (products exact), FFMA
//   nvfp4_ffma   E2M1 + UE4M3/16 -> value * scale in f32 on staging (products exact), FFMA
//   e4m3_hfma2   E4M3           -> f16x2 on staging, HFMA2 with f16 accumulate, promoted to f32 every PROM k (0: never)
//   bf16_hfma2   bf16           -> bf16x2, HFMA2.BF16 with bf16 accumulate, promoted to f32 every PROM k
//   i8_dp4a      int8           -> IDP4A, int32 accumulate (exact)
//   nvfp4_dp4a   E2M1 + UE4M3/16 -> 2*E2M1 as int8 on staging, IDP4A per 16-block onto a biased int (exact block sums), then
//                                  two FFMAs per (word, block) apply the scales
// Controls: cuBLAS SGEMM with CUBLAS_PEDANTIC_MATH (FFMA, no TF32), cuBLASLt BF16, FP8 E4M3 and NVFP4 (tensor cores).
//
// Usage: simt_gemm_sm120 <task> <m> <n> <k> <target_ms> <seed>   ->  one JSON line on stdout.
// Every task gates its output first: 512 sampled words against a float64 (int64 for i8) host reference.
#include <cuda_runtime.h>
#include <cuda_fp16.h>
#include <cuda_bf16.h>
#include <cuda_fp8.h>
#include <cublas_v2.h>
#include <cublasLt.h>

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

#define CK(x) do { cudaError_t e_ = (x); if (e_ != cudaSuccess) { \
  fprintf(stderr, "CUDA %s at %s:%d\n", cudaGetErrorString(e_), __FILE__, __LINE__); exit(2); } } while (0)
#define CB(x) do { int s_ = (int)(x); if (s_ != 0) { fprintf(stderr, "cuBLAS status %d at %s:%d\n", s_, __FILE__, __LINE__); exit(2); } } while (0)

enum Kind { F32_FFMA, BF16_FFMA, E4M3_FFMA, NVFP4_FFMA, E4M3_HFMA2, BF16_HFMA2, I8_DP4A, NVFP4_DP4A };

// Elements per raw 32-bit global word, and compute words per raw word.
__host__ __device__ constexpr int epr(int K) {
  return K == F32_FFMA ? 1 : (K == BF16_FFMA || K == BF16_HFMA2) ? 2 : (K == NVFP4_FFMA || K == NVFP4_DP4A) ? 8 : 4;
}
__host__ __device__ constexpr int cpr(int K) {
  return K == F32_FFMA ? 1 : K == BF16_FFMA ? 2 : K == E4M3_FFMA ? 4 : K == NVFP4_FFMA ? 8
       : K == E4M3_HFMA2 ? 2 : K == BF16_HFMA2 ? 1 : K == I8_DP4A ? 1 : 2;
}
__host__ __device__ constexpr bool scaled(int K) { return K == NVFP4_FFMA || K == NVFP4_DP4A; }

__device__ __forceinline__ float ue4m3_f(uint32_t b) {
  uint32_t e = (b >> 3) & 15, m = b & 7;
  return e ? ldexpf(1.0f + m * 0.125f, (int)e - 7) : ldexpf(m * 0.125f, -6);
}
__device__ __forceinline__ float e2m1_f(uint32_t c) {  // E2M1: 0 .5 1 1.5 2 3 4 6
  const float t[8] = {0.f, .5f, 1.f, 1.5f, 2.f, 3.f, 4.f, 6.f};
  float v = t[c & 7];
  return (c & 8) ? -v : v;
}
// 2*E2M1 as a signed byte, 8 codes at a time, via two byte permutes on a 16-entry table.
__device__ __forceinline__ void e2m1x8_to_i8x8(uint32_t w, uint32_t& lo, uint32_t& hi) {
  // table bytes for codes 0..15: 0 1 2 3 4 6 8 12, then negatives
  const uint32_t t0 = 0x03020100u, t1 = 0x0C080604u, t2 = 0xFDFEFF00u, t3 = 0xF4F8FAFCu;
  uint32_t r[8];
#pragma unroll
  for (int i = 0; i < 8; ++i) {
    uint32_t c = (w >> (4 * i)) & 15;
    uint32_t pos = __byte_perm(t0, t1, c & 7);  // selects byte (c&7) of {t1:t0}
    uint32_t neg = __byte_perm(t2, t3, c & 7);
    r[i] = ((c & 8) ? neg : pos) & 0xFF;
  }
  lo = r[0] | (r[1] << 8) | (r[2] << 16) | (r[3] << 24);
  hi = r[4] | (r[5] << 8) | (r[6] << 16) | (r[7] << 24);
}

// Convert one raw word (row r, element offset k0) into cpr(K) compute words.
template <int K>
__device__ __forceinline__ void convert(uint32_t w, float scale, uint32_t* out) {
  if constexpr (K == F32_FFMA || K == BF16_HFMA2 || K == I8_DP4A) {
    out[0] = w;
  } else if constexpr (K == BF16_FFMA) {
    out[0] = w << 16; out[1] = w & 0xFFFF0000u;
  } else if constexpr (K == E4M3_FFMA) {
#pragma unroll
    for (int i = 0; i < 2; ++i) {
      __half2_raw h = __nv_cvt_fp8x2_to_halfraw2((__nv_fp8x2_storage_t)(w >> (16 * i)), __NV_E4M3);
      float2 f = __half22float2(*reinterpret_cast<__half2*>(&h));
      out[2 * i] = __float_as_uint(f.x); out[2 * i + 1] = __float_as_uint(f.y);
    }
  } else if constexpr (K == E4M3_HFMA2) {
#pragma unroll
    for (int i = 0; i < 2; ++i) {
      __half2_raw h = __nv_cvt_fp8x2_to_halfraw2((__nv_fp8x2_storage_t)(w >> (16 * i)), __NV_E4M3);
      out[i] = (uint32_t)h.x | ((uint32_t)h.y << 16);
    }
  } else if constexpr (K == NVFP4_FFMA) {
#pragma unroll
    for (int i = 0; i < 8; ++i) out[i] = __float_as_uint(e2m1_f(w >> (4 * i)) * scale);
  } else if constexpr (K == NVFP4_DP4A) {
    e2m1x8_to_i8x8(w, out[0], out[1]);
  }
}

// One CTA of 256 threads computes BM x BN; BK compute words per k-tile; each thread TM x TN words.
template <int K, int BM, int BN, int BK, int TM, int TN, int PROM>
__global__ void __launch_bounds__(256) simt_gemm(const uint32_t* __restrict__ A, const uint32_t* __restrict__ B,
                                                  const uint8_t* __restrict__ SA, const uint8_t* __restrict__ SB,
                                                  void* __restrict__ C, int M, int N, int Kel) {
  constexpr int CPR = cpr(K), EPR = epr(K), RWT = BK / CPR;  // raw words per row per k-tile
  static_assert(BK % CPR == 0 && RWT % 4 == 0, "k-tile must be a whole number of 16-byte loads per row");
  constexpr int TX = BN / TN, TY = BM / TM;
  static_assert(TX * TY == 256, "256 threads");
  constexpr int LA = (BM * RWT / 4 + 255) / 256, LB = (BN * RWT / 4 + 255) / 256;
  constexpr int NBLK = scaled(K) ? (BK * (EPR / CPR)) / 16 : 1;  // 16-element scale blocks per k-tile
  static_assert(!scaled(K) || (BK * (EPR / CPR)) % 16 == 0, "whole scale blocks per k-tile");
  extern __shared__ __align__(16) uint32_t smem[];
  uint32_t* As = smem;                        // [2][BK][BM]
  uint32_t* Bs = As + 2 * BK * BM;            // [2][BK][BN]
  float* SAs = reinterpret_cast<float*>(Bs + 2 * BK * BN);  // [2][NBLK][BM]   (nvfp4_dp4a only)
  float* SBs = SAs + 2 * NBLK * BM;                          // [2][NBLK][BN]

  const int tid = threadIdx.x, tx = tid % TX, ty = tid / TX;
  const int m0 = blockIdx.y * BM, n0 = blockIdx.x * BN;
  const int Kraw = Kel / EPR, ntiles = Kraw / RWT;
  const int Kblk = Kel / 16;

  uint4 ra[LA], rb[LB];
  auto gload = [&](int t) {
#pragma unroll
    for (int l = 0; l < LA; ++l) {
      int idx = tid + 256 * l;
      if (idx < BM * RWT / 4) {
        int r = idx / (RWT / 4), c = idx % (RWT / 4);
        ra[l] = *reinterpret_cast<const uint4*>(A + (size_t)(m0 + r) * Kraw + (size_t)t * RWT + 4 * c);
      }
    }
#pragma unroll
    for (int l = 0; l < LB; ++l) {
      int idx = tid + 256 * l;
      if (idx < BN * RWT / 4) {
        int r = idx / (RWT / 4), c = idx % (RWT / 4);
        rb[l] = *reinterpret_cast<const uint4*>(B + (size_t)(n0 + r) * Kraw + (size_t)t * RWT + 4 * c);
      }
    }
  };
  auto sstore = [&](int t, int buf) {
    uint32_t* as = As + buf * BK * BM;
    uint32_t* bs = Bs + buf * BK * BN;
#pragma unroll
    for (int l = 0; l < LA; ++l) {
      int idx = tid + 256 * l;
      if (idx < BM * RWT / 4) {
        int r = idx / (RWT / 4), c = idx % (RWT / 4);
        uint32_t w4[4] = {ra[l].x, ra[l].y, ra[l].z, ra[l].w};
#pragma unroll
        for (int q = 0; q < 4; ++q) {
          int rw = 4 * c + q;                                   // raw word within the row's k-tile
          float s = 1.f;
          if constexpr (K == NVFP4_FFMA) s = ue4m3_f(SA[(size_t)(m0 + r) * Kblk + ((t * RWT + rw) * EPR) / 16]);
          uint32_t o[CPR];
          convert<K>(w4[q], s, o);
#pragma unroll
          for (int u = 0; u < CPR; ++u) as[(rw * CPR + u) * BM + r] = o[u];
        }
      }
    }
#pragma unroll
    for (int l = 0; l < LB; ++l) {
      int idx = tid + 256 * l;
      if (idx < BN * RWT / 4) {
        int r = idx / (RWT / 4), c = idx % (RWT / 4);
        uint32_t w4[4] = {rb[l].x, rb[l].y, rb[l].z, rb[l].w};
#pragma unroll
        for (int q = 0; q < 4; ++q) {
          int rw = 4 * c + q;
          float s = 1.f;
          if constexpr (K == NVFP4_FFMA) s = ue4m3_f(SB[(size_t)(n0 + r) * Kblk + ((t * RWT + rw) * EPR) / 16]);
          uint32_t o[CPR];
          convert<K>(w4[q], s, o);
#pragma unroll
          for (int u = 0; u < CPR; ++u) bs[(rw * CPR + u) * BN + r] = o[u];
        }
      }
    }
    if constexpr (K == NVFP4_DP4A) {
      float* sas = SAs + buf * NBLK * BM;
      float* sbs = SBs + buf * NBLK * BN;
      for (int idx = tid; idx < NBLK * BM; idx += 256) {
        int b = idx / BM, r = idx % BM;
        sas[b * BM + r] = ue4m3_f(SA[(size_t)(m0 + r) * Kblk + t * NBLK + b]);
      }
      for (int idx = tid; idx < NBLK * BN; idx += 256) {
        int b = idx / BN, r = idx % BN;
        sbs[b * BN + r] = 0.25f * ue4m3_f(SB[(size_t)(n0 + r) * Kblk + t * NBLK + b]);  // (2a)(2b) = 4ab
      }
    }
  };

  float facc[TM][TN];
  int iacc[TM][TN];
  uint32_t hacc[TM][TN];
#pragma unroll
  for (int i = 0; i < TM; ++i)
#pragma unroll
    for (int j = 0; j < TN; ++j) { facc[i][j] = 0.f; iacc[i][j] = 0; hacc[i][j] = 0; }

  constexpr int KEL_PER_TILE = BK * (EPR / CPR);
  constexpr int PROM_TILES = PROM > 0 ? (PROM / KEL_PER_TILE > 0 ? PROM / KEL_PER_TILE : 1) : 0;

  gload(0);
  sstore(0, 0);
  __syncthreads();
  for (int t = 0; t < ntiles; ++t) {
    const int buf = t & 1;
    if (t + 1 < ntiles) gload(t + 1);
    const uint32_t* as = As + buf * BK * BM + ty * TM;
    const uint32_t* bs = Bs + buf * BK * BN + tx * TN;
    if constexpr (K == NVFP4_DP4A) {
      const float* sas = SAs + buf * NBLK * BM + ty * TM;
      const float* sbs = SBs + buf * NBLK * BN + tx * TN;
#pragma unroll
      for (int b = 0; b < NBLK; ++b) {
        int is[TM][TN];
#pragma unroll
        for (int i = 0; i < TM; ++i)
#pragma unroll
          for (int j = 0; j < TN; ++j) is[i][j] = 0x4B400000;  // 1.5 * 2^23: an exact block sum rides in the mantissa
#pragma unroll
        for (int w = 0; w < 4; ++w) {
          uint32_t a[TM], bb[TN];
#pragma unroll
          for (int i = 0; i < TM; i += 4) *reinterpret_cast<uint4*>(&a[i]) = *reinterpret_cast<const uint4*>(as + (b * 4 + w) * BM + i);
#pragma unroll
          for (int j = 0; j < TN; j += 2) *reinterpret_cast<uint2*>(&bb[j]) = *reinterpret_cast<const uint2*>(bs + (b * 4 + w) * BN + j);
#pragma unroll
          for (int i = 0; i < TM; ++i)
#pragma unroll
            for (int j = 0; j < TN; ++j) is[i][j] = __dp4a((int)a[i], (int)bb[j], is[i][j]);
        }
        float sa[TM], sb[TN], nb[TN];
#pragma unroll
        for (int i = 0; i < TM; ++i) sa[i] = sas[b * BM + i];
#pragma unroll
        for (int j = 0; j < TN; ++j) { sb[j] = sbs[b * BN + j]; nb[j] = -12582912.0f * sb[j]; }
#pragma unroll
        for (int i = 0; i < TM; ++i)
#pragma unroll
          for (int j = 0; j < TN; ++j) {
            float x = fmaf(__int_as_float(is[i][j]), sb[j], nb[j]);  // exact: (block sum) * sb
            facc[i][j] = fmaf(x, sa[i], facc[i][j]);
          }
      }
    } else {
#pragma unroll
      for (int kk = 0; kk < BK; ++kk) {
        uint32_t a[TM], bb[TN];
#pragma unroll
        for (int i = 0; i < TM; i += 4) *reinterpret_cast<uint4*>(&a[i]) = *reinterpret_cast<const uint4*>(as + kk * BM + i);
#pragma unroll
        for (int j = 0; j < TN; j += 2) *reinterpret_cast<uint2*>(&bb[j]) = *reinterpret_cast<const uint2*>(bs + kk * BN + j);
#pragma unroll
        for (int i = 0; i < TM; ++i)
#pragma unroll
          for (int j = 0; j < TN; ++j) {
            if constexpr (K == I8_DP4A) {
              iacc[i][j] = __dp4a((int)a[i], (int)bb[j], iacc[i][j]);
            } else if constexpr (K == E4M3_HFMA2) {
              __half2 r = __hfma2(*reinterpret_cast<__half2*>(&a[i]), *reinterpret_cast<__half2*>(&bb[j]),
                                  *reinterpret_cast<__half2*>(&hacc[i][j]));
              hacc[i][j] = *reinterpret_cast<uint32_t*>(&r);
            } else if constexpr (K == BF16_HFMA2) {
              __nv_bfloat162 r = __hfma2(*reinterpret_cast<__nv_bfloat162*>(&a[i]), *reinterpret_cast<__nv_bfloat162*>(&bb[j]),
                                         *reinterpret_cast<__nv_bfloat162*>(&hacc[i][j]));
              hacc[i][j] = *reinterpret_cast<uint32_t*>(&r);
            } else {
              facc[i][j] = fmaf(__uint_as_float(a[i]), __uint_as_float(bb[j]), facc[i][j]);
            }
          }
      }
      if constexpr ((K == E4M3_HFMA2 || K == BF16_HFMA2) && PROM_TILES > 0) {
        if ((t + 1) % PROM_TILES == 0) {
#pragma unroll
          for (int i = 0; i < TM; ++i)
#pragma unroll
            for (int j = 0; j < TN; ++j) {
              float2 f;
              if constexpr (K == E4M3_HFMA2) f = __half22float2(*reinterpret_cast<__half2*>(&hacc[i][j]));
              else f = __bfloat1622float2(*reinterpret_cast<__nv_bfloat162*>(&hacc[i][j]));
              facc[i][j] += f.x + f.y;
              hacc[i][j] = 0;
            }
        }
      }
    }
    if (t + 1 < ntiles) sstore(t + 1, buf ^ 1);
    __syncthreads();
  }
  if constexpr (K == E4M3_HFMA2 || K == BF16_HFMA2) {
#pragma unroll
    for (int i = 0; i < TM; ++i)
#pragma unroll
      for (int j = 0; j < TN; ++j) {
        float2 f;
        if constexpr (K == E4M3_HFMA2) f = __half22float2(*reinterpret_cast<__half2*>(&hacc[i][j]));
        else f = __bfloat1622float2(*reinterpret_cast<__nv_bfloat162*>(&hacc[i][j]));
        facc[i][j] += f.x + f.y;
      }
  }
#pragma unroll
  for (int i = 0; i < TM; ++i)
#pragma unroll
    for (int j = 0; j < TN; ++j) {
      size_t o = (size_t)(m0 + ty * TM + i) * N + n0 + tx * TN + j;
      if constexpr (K == I8_DP4A) reinterpret_cast<int*>(C)[o] = iacc[i][j];
      else reinterpret_cast<float*>(C)[o] = facc[i][j];
    }
}

// ---------------------------------------------------------------------------------------------------------------------
// Host side.

static uint64_t splitmix(uint64_t& s) {
  uint64_t z = (s += 0x9E3779B97F4A7C15ull);
  z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ull;
  z = (z ^ (z >> 27)) * 0x94D049BB133111EBull;
  return z ^ (z >> 31);
}
static double h_e4m3(uint32_t b) {
  uint32_t e = (b >> 3) & 15, m = b & 7;
  double v = e ? std::ldexp(1.0 + m / 8.0, (int)e - 7) : std::ldexp(m / 8.0, -6);
  return (b & 0x80) ? -v : v;
}
static double h_e2m1(uint32_t c) {
  const double t[8] = {0, .5, 1, 1.5, 2, 3, 4, 6};
  return (c & 8) ? -t[c & 7] : t[c & 7];
}
static double h_ue4m3(uint32_t b) {
  uint32_t e = (b >> 3) & 15, m = b & 7;
  return e ? std::ldexp(1.0 + m / 8.0, (int)e - 7) : std::ldexp(m / 8.0, -6);
}
static double h_bf16(uint16_t h) { uint32_t u = (uint32_t)h << 16; float f; memcpy(&f, &u, 4); return f; }
static uint16_t f2bf16(float f) { uint32_t u; memcpy(&u, &f, 4); u += 0x7FFF + ((u >> 16) & 1); return (uint16_t)(u >> 16); }

// Operands in the global format, K-major rows. Values are kept small enough that f16/bf16 accumulation doesn't overflow.
struct Operand {
  std::vector<uint32_t> raw;   // rows x (k / epr) words
  std::vector<uint8_t> scale;  // rows x (k / 16), UE4M3 (scaled kinds)
  int rows = 0, k = 0, fmt = 0;  // fmt: 0 f32, 1 bf16, 2 e4m3, 3 int8, 4 e2m1, 5 f16
  double at(int r, int kk) const {
    const int e = fmt == 0 ? 1 : (fmt == 1 || fmt == 5) ? 2 : fmt == 4 ? 8 : 4;
    uint32_t w = raw[(size_t)r * (k / e) + kk / e];
    int s = kk % e;
    switch (fmt) {
      case 0: { float f; memcpy(&f, &w, 4); return f; }
      case 1: return h_bf16((uint16_t)(w >> (16 * s)));
      case 5: { __half_raw h; h.x = (uint16_t)(w >> (16 * s)); return (double)__half2float(__half(h)); }
      case 2: return h_e4m3((w >> (8 * s)) & 0xFF);
      case 3: return (double)(int8_t)((w >> (8 * s)) & 0xFF);
      default: return h_e2m1((w >> (4 * s)) & 15) * h_ue4m3(scale[(size_t)r * (k / 16) + kk / 16]);
    }
  }
};
static Operand make_operand(int fmt, int rows, int k, uint64_t seed) {
  Operand o; o.fmt = fmt; o.rows = rows; o.k = k;
  const int e = fmt == 0 ? 1 : (fmt == 1 || fmt == 5) ? 2 : fmt == 4 ? 8 : 4;
  o.raw.resize((size_t)rows * (k / e));
  uint64_t s = seed;
  for (auto& w : o.raw) {
    uint64_t z = splitmix(s);
    switch (fmt) {
      case 0: { float f = (float)((int64_t)(z >> 40) - (1 << 23)) / (1 << 23); memcpy(&w, &f, 4); break; }
      case 5: { float f0 = (float)((int64_t)(z >> 40) - (1 << 23)) / (1 << 23);
                float f1 = (float)((int64_t)((z >> 8) & 0xFFFFFF) - (1 << 23)) / (1 << 23);
                __half_raw h0 = __half_raw(__float2half(f0)), h1 = __half_raw(__float2half(f1));
                w = (uint32_t)h0.x | ((uint32_t)h1.x << 16); break; }
      case 1: { float f0 = (float)((int64_t)(z >> 40) - (1 << 23)) / (1 << 23);
                float f1 = (float)((int64_t)((z >> 8) & 0xFFFFFF) - (1 << 23)) / (1 << 23);
                w = f2bf16(f0) | ((uint32_t)f2bf16(f1) << 16); break; }
      case 2: { w = 0;  // sign, exponent 4..8 (|v| in [1/8, 3.75]), any mantissa
                for (int i = 0; i < 4; ++i) { uint32_t r = (uint32_t)(z >> (16 * i));
                  uint32_t b = ((r & 1) << 7) | ((4 + (r >> 1) % 5) << 3) | ((r >> 4) & 7); w |= b << (8 * i); }
                break; }
      case 3: w = (uint32_t)z; break;
      default: w = (uint32_t)z; break;
    }
  }
  if (fmt == 4) {
    o.scale.resize((size_t)rows * (k / 16));
    for (auto& b : o.scale) { uint64_t z = splitmix(s); b = (uint8_t)(((5 + z % 5) << 3) | ((z >> 8) & 7)); }  // 2^-2 .. 2^2
  }
  return o;
}

struct Result { double ms_med, ms_min, ms_p10, ms_p90; int reps; };

template <class F>
static Result time_it(F&& launch, double target_ms) {
  cudaEvent_t a, b;
  CK(cudaEventCreate(&a)); CK(cudaEventCreate(&b));
  launch(); CK(cudaDeviceSynchronize());  // warm
  CK(cudaEventRecord(a)); launch(); CK(cudaEventRecord(b)); CK(cudaEventSynchronize(b));
  float one; CK(cudaEventElapsedTime(&one, a, b));
  int reps = std::max(10, std::min(2000, (int)(target_ms / std::max(one, 1e-3f))));
  std::vector<cudaEvent_t> ev(reps + 1);
  for (auto& e : ev) CK(cudaEventCreate(&e));
  CK(cudaEventRecord(ev[0]));
  for (int r = 0; r < reps; ++r) { launch(); CK(cudaEventRecord(ev[r + 1])); }
  CK(cudaEventSynchronize(ev[reps]));
  std::vector<double> t(reps);
  for (int r = 0; r < reps; ++r) { float x; CK(cudaEventElapsedTime(&x, ev[r], ev[r + 1])); t[r] = x; }
  for (auto& e : ev) CK(cudaEventDestroy(e));
  CK(cudaEventDestroy(a)); CK(cudaEventDestroy(b));
  std::sort(t.begin(), t.end());
  return {t[reps / 2], t[0], t[reps / 10], t[(reps * 9) / 10], reps};
}

struct Gate { int samples = 0, bad = 0; double worst = 0; };  // worst = max |err| / (tolerance)

static Gate gate_words(const Operand& A, const Operand& B, const void* hC, bool is_int, double rel_tol, int M, int N, int Kel,
                       uint64_t seed) {
  Gate g; uint64_t s = seed ^ 0xA5A5A5A5ull;
  for (int q = 0; q < 512; ++q) {
    int i = (int)(splitmix(s) % M), j = (int)(splitmix(s) % N);
    double ref = 0, mag = 0; int64_t iref = 0;
    for (int kk = 0; kk < Kel; ++kk) {
      double x = A.at(i, kk), y = B.at(j, kk);
      ref += x * y; mag += std::fabs(x * y);
      if (is_int) iref += (int64_t)x * (int64_t)y;
    }
    ++g.samples;
    if (is_int) {
      int got = reinterpret_cast<const int*>(hC)[(size_t)i * N + j];
      if ((int64_t)got != (int64_t)(int32_t)iref) { ++g.bad; g.worst = std::max(g.worst, 1e9); }
    } else {
      double got = reinterpret_cast<const float*>(hC)[(size_t)i * N + j];
      double tol = rel_tol * std::max(mag, 1e-30), err = std::fabs(got - ref) / tol;
      if (!(err <= 1.0)) ++g.bad;
      g.worst = std::max(g.worst, std::isfinite(err) ? err : 1e30);
    }
  }
  return g;
}

struct Cfg { int BM, BN, BK, TM, TN, PROM; };

template <int K, int BM, int BN, int BK, int TM, int TN, int PROM>
static void launch_simt(const uint32_t* A, const uint32_t* B, const uint8_t* SA, const uint8_t* SB, void* C, int M, int N,
                        int Kel, cudaStream_t st) {
  constexpr int NBLK = scaled(K) ? (BK * (epr(K) / cpr(K))) / 16 : 1;
  size_t sm = (size_t)(2 * BK * BM + 2 * BK * BN) * 4 + (K == NVFP4_DP4A ? (size_t)(2 * NBLK * (BM + BN)) * 4 : 0);
  static bool once = false;
  if (!once) { CK(cudaFuncSetAttribute(simt_gemm<K, BM, BN, BK, TM, TN, PROM>, cudaFuncAttributeMaxDynamicSharedMemorySize, (int)sm)); once = true; }
  dim3 grid(N / BN, M / BM);
  simt_gemm<K, BM, BN, BK, TM, TN, PROM><<<grid, 256, sm, st>>>(A, B, SA, SB, C, M, N, Kel);
}

using LaunchFn = void (*)(const uint32_t*, const uint32_t*, const uint8_t*, const uint8_t*, void*, int, int, int, cudaStream_t);
struct Entry { const char* name; int kind; Cfg cfg; LaunchFn fn; };

#define E(name, K, BM, BN, BK, TM, TN, P) {name, K, {BM, BN, BK, TM, TN, P}, launch_simt<K, BM, BN, BK, TM, TN, P>}
static const Entry kEntries[] = {
  E("f32_ffma:128x128x8:8x8", F32_FFMA, 128, 128, 8, 8, 8, 0),
  E("f32_ffma:128x128x16:8x8", F32_FFMA, 128, 128, 16, 8, 8, 0),
  E("f32_ffma:256x128x8:16x8", F32_FFMA, 256, 128, 8, 16, 8, 0),
  E("f32_ffma:64x64x16:4x4", F32_FFMA, 64, 64, 16, 4, 4, 0),
  E("f32_ffma:32x128x16:4x4", F32_FFMA, 32, 128, 16, 4, 4, 0),
  E("bf16_ffma:128x128x8:8x8", BF16_FFMA, 128, 128, 8, 8, 8, 0),
  E("bf16_ffma:128x128x16:8x8", BF16_FFMA, 128, 128, 16, 8, 8, 0),
  E("bf16_ffma:256x128x8:16x8", BF16_FFMA, 256, 128, 8, 16, 8, 0),
  E("e4m3_ffma:128x128x16:8x8", E4M3_FFMA, 128, 128, 16, 8, 8, 0),
  E("e4m3_ffma:128x128x32:8x8", E4M3_FFMA, 128, 128, 32, 8, 8, 0),
  E("e4m3_ffma:256x128x16:16x8", E4M3_FFMA, 256, 128, 16, 16, 8, 0),
  E("e4m3_ffma:32x128x16:4x4", E4M3_FFMA, 32, 128, 16, 4, 4, 0),
  E("nvfp4_ffma:128x128x32:8x8", NVFP4_FFMA, 128, 128, 32, 8, 8, 0),
  E("nvfp4_ffma:256x128x32:16x8", NVFP4_FFMA, 256, 128, 32, 16, 8, 0),
  E("e4m3_hfma2:128x128x8:8x8:p64", E4M3_HFMA2, 128, 128, 8, 8, 8, 64),
  E("e4m3_hfma2:128x128x16:8x8:p64", E4M3_HFMA2, 128, 128, 16, 8, 8, 64),
  E("e4m3_hfma2:128x128x8:8x8:p0", E4M3_HFMA2, 128, 128, 8, 8, 8, 0),
  E("bf16_hfma2:128x128x8:8x8:p16", BF16_HFMA2, 128, 128, 8, 8, 8, 16),
  E("bf16_hfma2:128x128x16:8x8:p32", BF16_HFMA2, 128, 128, 16, 8, 8, 32),
  E("bf16_hfma2:128x128x8:8x8:p0", BF16_HFMA2, 128, 128, 8, 8, 8, 0),
  E("i8_dp4a:128x128x8:8x8", I8_DP4A, 128, 128, 8, 8, 8, 0),
  E("i8_dp4a:128x128x16:8x8", I8_DP4A, 128, 128, 16, 8, 8, 0),
  E("i8_dp4a:256x128x8:16x8", I8_DP4A, 256, 128, 8, 16, 8, 0),
  E("i8_dp4a:32x128x16:4x4", I8_DP4A, 32, 128, 16, 4, 4, 0),
  E("nvfp4_dp4a:128x128x8:8x8", NVFP4_DP4A, 128, 128, 8, 8, 8, 0),
  E("nvfp4_dp4a:128x128x16:8x8", NVFP4_DP4A, 128, 128, 16, 8, 8, 0),
  E("nvfp4_dp4a:32x128x16:4x4", NVFP4_DP4A, 32, 128, 16, 4, 4, 0),
};
#undef E

static int fmt_of(int K) {
  switch (K) { case F32_FFMA: return 0; case BF16_FFMA: case BF16_HFMA2: return 1; case E4M3_FFMA: case E4M3_HFMA2: return 2;
               case I8_DP4A: return 3; default: return 4; }
}
static const char* fmt_name(int f) { const char* n[] = {"f32", "bf16", "e4m3", "int8", "e2m1-nv", "f16"}; return n[f]; }

static void upload(const Operand& o, uint32_t** d, uint8_t** ds) {
  CK(cudaMalloc(d, o.raw.size() * 4));
  CK(cudaMemcpy(*d, o.raw.data(), o.raw.size() * 4, cudaMemcpyHostToDevice));
  *ds = nullptr;
  if (!o.scale.empty()) { CK(cudaMalloc(ds, o.scale.size())); CK(cudaMemcpy(*ds, o.scale.data(), o.scale.size(), cudaMemcpyHostToDevice)); }
}

static void emit(const char* task, const char* engine, const char* fmt, const char* exact, int M, int N, int Kel, const Result& r,
                 const Gate& g, const char* extra) {
  double macs = (double)M * N * Kel;
  printf("{\"task\":\"%s\",\"engine\":\"%s\",\"inputs\":\"%s\",\"exactness\":\"%s\",\"m\":%d,\"n\":%d,\"k\":%d,"
         "\"reps\":%d,\"ms_median\":%.5f,\"ms_min\":%.5f,\"ms_p10\":%.5f,\"ms_p90\":%.5f,\"tmacs\":%.3f,"
         "\"gate\":{\"samples\":%d,\"bad\":%d,\"worst_over_tol\":%.3g,\"pass\":%s}%s}\n",
         task, engine, fmt, exact, M, N, Kel, r.reps, r.ms_med, r.ms_min, r.ms_p10, r.ms_p90, macs / (r.ms_med * 1e-3) / 1e12,
         g.samples, g.bad, g.worst, g.bad == 0 ? "true" : "false", extra);
  fflush(stdout);
}

// cuBLASLt: D (col-major n x m, i.e. row-major C m x n) = A_lt^T B_lt with A_lt = our B (k x n col-major), B_lt = our A.
// The fastest of the first 8 heuristic candidates is kept (screened at up to 300 ms each).
struct LtGemm {
  cublasLtHandle_t lt; cublasLtMatmulDesc_t op; cublasLtMatrixLayout_t la, lb, ld;
  cublasLtMatmulAlgo_t algo; void* wsp = nullptr; size_t ws = 64ull << 20; int bi = -1, nh = 0;
  const void *Bdev, *Adev; void* D;
  LtGemm(cublasLtHandle_t h_, cudaDataType_t in_t, bool nvfp4, cudaDataType_t out_t, const void* Bd, const void* Ad,
         const void* sB, const void* sA, void* Dd, int M, int N, int Kel)
      : lt(h_), Bdev(Bd), Adev(Ad), D(Dd) {
    CB(cublasLtMatmulDescCreate(&op, CUBLAS_COMPUTE_32F, CUDA_R_32F));
    cublasOperation_t T = CUBLAS_OP_T, Nn = CUBLAS_OP_N;
    CB(cublasLtMatmulDescSetAttribute(op, CUBLASLT_MATMUL_DESC_TRANSA, &T, sizeof(T)));
    CB(cublasLtMatmulDescSetAttribute(op, CUBLASLT_MATMUL_DESC_TRANSB, &Nn, sizeof(Nn)));
    if (nvfp4) {
      cublasLtMatmulMatrixScale_t sm = CUBLASLT_MATMUL_MATRIX_SCALE_VEC16_UE4M3;
      CB(cublasLtMatmulDescSetAttribute(op, CUBLASLT_MATMUL_DESC_A_SCALE_MODE, &sm, sizeof(sm)));
      CB(cublasLtMatmulDescSetAttribute(op, CUBLASLT_MATMUL_DESC_B_SCALE_MODE, &sm, sizeof(sm)));
      CB(cublasLtMatmulDescSetAttribute(op, CUBLASLT_MATMUL_DESC_A_SCALE_POINTER, &sB, sizeof(sB)));
      CB(cublasLtMatmulDescSetAttribute(op, CUBLASLT_MATMUL_DESC_B_SCALE_POINTER, &sA, sizeof(sA)));
    }
    CB(cublasLtMatrixLayoutCreate(&la, in_t, Kel, N, Kel));
    CB(cublasLtMatrixLayoutCreate(&lb, in_t, Kel, M, Kel));
    CB(cublasLtMatrixLayoutCreate(&ld, out_t, N, M, N));
    cublasLtMatmulPreference_t pref; CB(cublasLtMatmulPreferenceCreate(&pref));
    CK(cudaMalloc(&wsp, ws));
    CB(cublasLtMatmulPreferenceSetAttribute(pref, CUBLASLT_MATMUL_PREF_MAX_WORKSPACE_BYTES, &ws, sizeof(ws)));
    cublasLtMatmulHeuristicResult_t h[16];
    CB(cublasLtMatmulAlgoGetHeuristic(lt, op, la, lb, ld, ld, pref, 16, h, &nh));
    if (nh == 0) { fprintf(stderr, "no cuBLASLt algorithm\n"); exit(4); }
    double best = 1e30;
    for (int c = 0; c < std::min(nh, 8); ++c) {
      algo = h[c].algo;
      Result r = time_it([&] { run(0); }, 300.0);
      if (r.ms_med < best) { best = r.ms_med; bi = c; }
    }
    algo = h[bi].algo;
  }
  void run(cudaStream_t st) {
    float alpha = 1.f, beta = 0.f;
    CB(cublasLtMatmul(lt, op, &alpha, Bdev, la, Adev, lb, &beta, D, ld, D, ld, &algo, wsp, ws, st));
  }
  std::string note() const { return "heuristic " + std::to_string(bi) + " of " + std::to_string(nh); }
};

static Result lt_matmul(cublasLtHandle_t lt, cudaDataType_t in_t, bool nvfp4, cudaDataType_t out_t, const void* Bdev,
                        const void* Adev, const void* sB, const void* sA, void* D, int M, int N, int Kel, double target_ms,
                        std::string& algo_note) {
  LtGemm g(lt, in_t, nvfp4, out_t, Bdev, Adev, sB, sA, D, M, N, Kel);
  algo_note = g.note();
  return time_it([&] { g.run(0); }, target_ms);
}

// ---------------------------------------------------------------------------------------------------------------------
// One-level Strassen of an E4M3 GEMM with FP16 sub-products (the attacker's route of `no-exact-rewrite/sm120-e4m3`, as a
// timing: pre-adds E4M3 -> FP16, 7 cuBLASLt FP16 GEMMs at half size with FP32 out, then the post-adds). Not bit-exact to
// any Pearl-C word: it bounds the time of a Strassen route from below, since a per-group (128-deep) route runs the same
// sub-products and more post-adds.
struct View { const uint8_t* p; int ld; };
__global__ void preadd_e4m3_f16(View x, View y, int sign, __half* out, int rows, int cols) {
  size_t i = (size_t)blockIdx.x * blockDim.x + threadIdx.x;
  if (i >= (size_t)rows * cols / 2) return;
  size_t r = (2 * i) / cols, c = (2 * i) % cols;
  __half2_raw hx = __nv_cvt_fp8x2_to_halfraw2(*reinterpret_cast<const uint16_t*>(x.p + r * x.ld + c), __NV_E4M3);
  __half2 v = *reinterpret_cast<__half2*>(&hx);
  if (sign) {
    __half2_raw hy = __nv_cvt_fp8x2_to_halfraw2(*reinterpret_cast<const uint16_t*>(y.p + r * y.ld + c), __NV_E4M3);
    __half2 w = *reinterpret_cast<__half2*>(&hy);
    v = sign > 0 ? __hadd2(v, w) : __hsub2(v, w);
  }
  reinterpret_cast<__half2*>(out)[i] = v;
}
__global__ void postadd(const float* const* Mt, float* C, int m, int n) {
  size_t i = (size_t)blockIdx.x * blockDim.x + threadIdx.x;
  if (i >= (size_t)m * n) return;
  size_t r = i / n, c = i % n, N = 2 * (size_t)n;
  float m1 = Mt[0][i], m2 = Mt[1][i], m3 = Mt[2][i], m4 = Mt[3][i], m5 = Mt[4][i], m6 = Mt[5][i], m7 = Mt[6][i];
  C[r * N + c] = m1 + m4 - m5 + m7;
  C[r * N + n + c] = m3 + m5;
  C[(r + m) * N + c] = m2 + m4;
  C[(r + m) * N + n + c] = m1 - m2 + m3 + m6;
}

static int strassen1(int M, int N, int Kel, double target, uint64_t seed, const cudaDeviceProp& p) {
  Operand A = make_operand(2, M, Kel, seed), B = make_operand(2, N, Kel, seed + 1);
  uint32_t *dA, *dB; uint8_t *s0, *s1;
  upload(A, &dA, &s0); upload(B, &dB, &s1);
  const int m = M / 2, n = N / 2, k = Kel / 2;
  const uint8_t* a = reinterpret_cast<const uint8_t*>(dA);
  const uint8_t* b = reinterpret_cast<const uint8_t*>(dB);
  auto Ab = [&](int i, int j) { return View{a + (size_t)i * m * Kel + (size_t)j * k, Kel}; };
  auto Bb = [&](int i, int j) { return View{b + (size_t)j * n * Kel + (size_t)i * k, Kel}; };  // B_ij = (Bt block j,i)^T
  struct Pre { View x, y; int s; };
  const Pre pa[7] = {{Ab(0,0), Ab(1,1), 1}, {Ab(1,0), Ab(1,1), 1}, {Ab(0,0), Ab(0,0), 0}, {Ab(1,1), Ab(1,1), 0},
                     {Ab(0,0), Ab(0,1), 1}, {Ab(1,0), Ab(0,0), -1}, {Ab(0,1), Ab(1,1), -1}};
  const Pre pb[7] = {{Bb(0,0), Bb(1,1), 1}, {Bb(0,0), Bb(0,0), 0}, {Bb(0,1), Bb(1,1), -1}, {Bb(1,0), Bb(0,0), -1},
                     {Bb(1,1), Bb(1,1), 0}, {Bb(0,0), Bb(0,1), 1}, {Bb(1,0), Bb(1,1), 1}};
  __half *SA[7], *SB[7]; float* Mt[7]; float** dMt; float* dC;
  for (int i = 0; i < 7; ++i) {
    CK(cudaMalloc(&SA[i], (size_t)m * k * 2)); CK(cudaMalloc(&SB[i], (size_t)n * k * 2)); CK(cudaMalloc(&Mt[i], (size_t)m * n * 4));
  }
  CK(cudaMalloc(&dMt, sizeof Mt)); CK(cudaMemcpy(dMt, Mt, sizeof Mt, cudaMemcpyHostToDevice));
  CK(cudaMalloc(&dC, (size_t)M * N * 4));
  cublasLtHandle_t lt; CB(cublasLtCreate(&lt));
  std::vector<LtGemm*> g;
  for (int i = 0; i < 7; ++i) g.push_back(new LtGemm(lt, CUDA_R_16F, false, CUDA_R_32F, SB[i], SA[i], nullptr, nullptr, Mt[i], m, n, k));
  auto pre = [&] {
    for (int i = 0; i < 7; ++i) {
      preadd_e4m3_f16<<<(unsigned)(((size_t)m * k / 2 + 255) / 256), 256>>>(pa[i].x, pa[i].y, pa[i].s, SA[i], m, k);
      preadd_e4m3_f16<<<(unsigned)(((size_t)n * k / 2 + 255) / 256), 256>>>(pb[i].x, pb[i].y, pb[i].s, SB[i], n, k);
    }
  };
  auto sub = [&] { for (int i = 0; i < 7; ++i) g[i]->run(0); };
  auto post = [&] { postadd<<<(unsigned)(((size_t)m * n + 255) / 256), 256>>>(dMt, dC, m, n); };
  auto all = [&] { pre(); sub(); post(); };
  all(); CK(cudaGetLastError()); CK(cudaDeviceSynchronize());
  std::vector<float> hC((size_t)M * N); CK(cudaMemcpy(hC.data(), dC, hC.size() * 4, cudaMemcpyDeviceToHost));
  Gate gt = gate_words(A, B, hC.data(), false, 1e-3, M, N, Kel, seed);  // FP16 pre-adds may round: a loose gate
  Result r_all = time_it(all, target), r_pre = time_it(pre, target / 4), r_sub = time_it(sub, target / 2),
         r_post = time_it(post, target / 4);
  char extra[512];
  snprintf(extra, sizeof extra,
           ",\"device\":\"%s\",\"components_ms\":{\"preadd\":%.5f,\"subproducts\":%.5f,\"postadd\":%.5f},\"sub_algo\":\"%s\"",
           p.name, r_pre.ms_med, r_sub.ms_med, r_post.ms_med, g[0]->note().c_str());
  emit("strassen1_e4m3_f16", "Strassen one level: E4M3 -> FP16 pre-adds, 7 cuBLASLt FP16 GEMMs (FP32 out), post-adds",
       "e4m3", "not bit-exact (a time bound)", M, N, Kel, r_all, gt, extra);
  return 0;
}

int main(int argc, char** argv) {
  if (argc < 7) { fprintf(stderr, "usage: %s <task> <m> <n> <k> <target_ms> <seed> | --list\n", argv[0]); return 1; }
  std::string task = argv[1];
  int M = atoi(argv[2]), N = atoi(argv[3]), Kel = atoi(argv[4]);
  double target = atof(argv[5]);
  uint64_t seed = strtoull(argv[6], nullptr, 10);

  cudaDeviceProp p; CK(cudaGetDeviceProperties(&p, 0));
  char extra[512];

  if (task == "strassen1_e4m3_f16") return strassen1(M, N, Kel, target, seed, p);
  if (task == "cublas_sgemm_pedantic" || task.rfind("lt_", 0) == 0) {
    const bool f32out = task == "lt_f16_f32" || task == "lt_e4m3_f32";
    int fmt = task == "cublas_sgemm_pedantic" ? 0 : task == "lt_bf16" ? 1 : (task == "lt_e4m3" || task == "lt_e4m3_f32") ? 2
            : task == "lt_nvfp4" ? 4 : task == "lt_f16_f32" ? 5 : -1;
    if (fmt < 0) { fprintf(stderr, "unknown task %s\n", task.c_str()); return 1; }
    Operand A = make_operand(fmt, M, Kel, seed), B = make_operand(fmt, N, Kel, seed + 1);
    uint32_t *dA, *dB; uint8_t *sA, *sB;
    upload(A, &dA, &sA); upload(B, &dB, &sB);
    Result r; Gate g; std::string note = "";
    if (task == "cublas_sgemm_pedantic") {
      float* dC; CK(cudaMalloc(&dC, (size_t)M * N * 4));
      cublasHandle_t hb; CB(cublasCreate(&hb)); CB(cublasSetMathMode(hb, CUBLAS_PEDANTIC_MATH));
      float al = 1.f, be = 0.f;
      auto go = [&] { CB(cublasSgemm(hb, CUBLAS_OP_T, CUBLAS_OP_N, N, M, Kel, &al, (const float*)dB, Kel, (const float*)dA, Kel, &be, dC, N)); };
      r = time_it(go, target);
      std::vector<float> hC((size_t)M * N); CK(cudaMemcpy(hC.data(), dC, hC.size() * 4, cudaMemcpyDeviceToHost));
      g = gate_words(A, B, hC.data(), false, 1e-4, M, N, Kel, seed);
      snprintf(extra, sizeof extra, ",\"device\":\"%s\"", p.name);
      emit(task.c_str(), "cuBLAS SGEMM, CUBLAS_PEDANTIC_MATH (FFMA)", "f32", "f32 accumulate", M, N, Kel, r, g, extra);
    } else {
      cublasLtHandle_t lt; CB(cublasLtCreate(&lt));
      cudaDataType_t in_t = fmt == 1 ? CUDA_R_16BF : fmt == 2 ? CUDA_R_8F_E4M3 : fmt == 5 ? CUDA_R_16F : CUDA_R_4F_E2M1;
      void* dD; CK(cudaMalloc(&dD, (size_t)M * N * 4));
      // Timing only for the scales' layout: cuBLASLt wants them swizzled, so the words aren't gated for NVFP4.
      void *lsA = nullptr, *lsB = nullptr;
      if (fmt == 4) {
        auto sz = [](int rows, int k) { return (size_t)((rows + 127) / 128 * 128) * ((k / 16 + 3) / 4 * 4); };
        CK(cudaMalloc(&lsA, sz(M, Kel))); CK(cudaMalloc(&lsB, sz(N, Kel)));
        CK(cudaMemset(lsA, 0x38, sz(M, Kel))); CK(cudaMemset(lsB, 0x38, sz(N, Kel)));
      }
      r = lt_matmul(lt, in_t, fmt == 4, f32out ? CUDA_R_32F : CUDA_R_16BF, dB, dA, lsB, lsA, dD, M, N, Kel, target, note);
      if (fmt != 4) {
        std::vector<float> hC((size_t)M * N);
        if (f32out) CK(cudaMemcpy(hC.data(), dD, hC.size() * 4, cudaMemcpyDeviceToHost));
        else {
          std::vector<uint16_t> h16((size_t)M * N); CK(cudaMemcpy(h16.data(), dD, h16.size() * 2, cudaMemcpyDeviceToHost));
          for (size_t i = 0; i < h16.size(); ++i) hC[i] = (float)h_bf16(h16[i]);
        }
        g = gate_words(A, B, hC.data(), false, f32out ? 1e-4 : 1e-2, M, N, Kel, seed);
      } else { g.samples = 0; }
      snprintf(extra, sizeof extra, ",\"device\":\"%s\",\"algo\":\"%s\"", p.name, note.c_str());
      emit(task.c_str(), "cuBLASLt (tensor cores)", fmt_name(fmt), f32out ? "f32 out" : "bf16 out", M, N, Kel, r, g, extra);
    }
    return 0;
  }

  const Entry* e = nullptr;
  for (auto& x : kEntries) if (task == x.name) e = &x;
  if (!e) { fprintf(stderr, "unknown task %s\n", task.c_str()); return 1; }
  const Cfg& c = e->cfg;
  if (M % c.BM || N % c.BN || Kel % 256) { fprintf(stderr, "shape not a multiple of the tile\n"); return 1; }
  int fmt = fmt_of(e->kind);
  Operand A = make_operand(fmt, M, Kel, seed), B = make_operand(fmt, N, Kel, seed + 1);
  uint32_t *dA, *dB; uint8_t *sA, *sB;
  upload(A, &dA, &sA); upload(B, &dB, &sB);
  void* dC; CK(cudaMalloc(&dC, (size_t)M * N * 4));
  auto go = [&] { e->fn(dA, dB, sA, sB, dC, M, N, Kel, 0); };
  go(); CK(cudaGetLastError()); CK(cudaDeviceSynchronize());
  std::vector<uint32_t> hC((size_t)M * N); CK(cudaMemcpy(hC.data(), dC, hC.size() * 4, cudaMemcpyDeviceToHost));
  bool is_int = e->kind == I8_DP4A;
  double tol = (e->kind == E4M3_HFMA2) ? 2e-2 : (e->kind == BF16_HFMA2) ? 1e-1 : 1e-4;
  Gate g = gate_words(A, B, hC.data(), is_int, tol, M, N, Kel, seed);
  Result r = time_it(go, target);
  const char* engine[] = {"FFMA", "FFMA (bf16 -> f32 on staging)", "FFMA (E4M3 -> f32 on staging)", "FFMA (E2M1*UE4M3 -> f32 on staging)",
                          "HFMA2 (E4M3 -> f16x2 on staging)", "HFMA2.BF16", "IDP4A", "IDP4A per 16-block + 2 FFMA per (word, block)"};
  const char* exact[] = {"f32 accumulate", "products exact, f32 accumulate", "products exact, f32 accumulate",
                         "products exact, f32 accumulate", "f16 accumulate", "bf16 accumulate", "exact (int32)",
                         "block sums exact, f32 across blocks"};
  snprintf(extra, sizeof extra, ",\"device\":\"%s\",\"tile\":{\"bm\":%d,\"bn\":%d,\"bk_words\":%d,\"tm\":%d,\"tn\":%d,\"prom_k\":%d}",
           p.name, c.BM, c.BN, c.BK, c.TM, c.TN, c.PROM);
  emit(task.c_str(), engine[e->kind], fmt_name(fmt), exact[e->kind], M, N, Kel, r, g, extra);
  return 0;
}
