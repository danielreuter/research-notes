// `fp-model/sm120-scalar` on one RTX PRO 6000 (sm_120a): the three scalar facts Pearl-C's noisy cast and noise-loss proof
// read, checked on the device.
//   cast   cvt.rn.satfinite.e4m3x2.f32 on all 2^32 FP32 bit patterns in both lanes, against an integer reference
//          (nearest-even at E4M3's quantum, saturating to +-448, NaN -> 0x7F|sign); `castdump` writes the device's codes
//          for a host sample so the host can compare them with `pearl_kw.f32_to_fp8` directly.
//   fadd   add.rn.f32 against the double sum rounded once to FP32 (innocuous double rounding: 53 >= 2*24 + 2), on 2^32
//          counter-hashed pairs weighted to subnormals, ties and cancellation; `fadddump` writes sums for a host sample.
//   mma    mma.sync m16n8k32 E4M3 x E4M3 -> FP32 with A and B broadcast (every element code c, every element code d), so
//          D = 32 * c * d exactly, for all 254 x 254 finite code pairs, subnormals included.
// Built once as is and once with -DPOSITIVE_CONTROL (add.rn.ftz.f32: the fadd check must then fail on subnormals).
//   nvcc -O3 -std=c++17 -gencode arch=compute_120a,code=sm_120a scalar_model_sm120.cu -o scalar_model
//   ./scalar_model cast | fadd | mma | castdump IN OUT | fadddump IN OUT       (JSON on stdout)
#include <cuda_runtime.h>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>

#ifdef POSITIVE_CONTROL
#define ADD_PTX "add.rn.ftz.f32 %0, %1, %2;"
#else
#define ADD_PTX "add.rn.f32 %0, %1, %2;"
#endif
#define CK(x) do { cudaError_t e_ = (x); if (e_ != cudaSuccess) { \
  fprintf(stderr, "CUDA %s at %s:%d\n", cudaGetErrorString(e_), __FILE__, __LINE__); exit(2); } } while (0)

__device__ __forceinline__ uint32_t cvt_pair(float hi, float lo) {
  uint16_t d;
  asm("cvt.rn.satfinite.e4m3x2.f32 %0, %1, %2;" : "=h"(d) : "f"(hi), "f"(lo));
  return d;
}

__host__ __device__ inline uint32_t ref_e4m3(uint32_t u) {
  uint32_t s = (u >> 31) << 7, e = (u >> 23) & 0xFF, m = u & 0x7FFFFF;
  if (e == 0xFF) return m ? (0x7F | s) : (0x7E | s);
  if (e == 0 && m == 0) return s;
  uint32_t M = e ? (m | 0x800000) : m;
  int E2 = e ? (int)e - 150 : -149;                     // |x| = M * 2^E2
  int E = e ? (int)e - 127 : -127;                      // floor(log2|x|) for normals; subnormals sit below -6 anyway
  int qe = (E > -6 ? E : -6) - 3;                       // E4M3's quantum at |x|
  int sh = qe - E2;                                     // > 0 on every FP32 input
  uint32_t q;
  if (sh >= 32) q = 0;
  else {
    uint32_t rem = M & ((1u << sh) - 1), half = 1u << (sh - 1);
    q = M >> sh;
    if (rem > half || (rem == half && (q & 1))) q++;
  }
  if (q >= 16) { q >>= 1; qe++; }
  uint32_t code;
  if (q == 0) code = 0;
  else if (q >= 8) {
    int ef = qe + 10;
    code = (ef > 15 || (ef == 15 && q - 8 == 7)) ? 0x7E : (uint32_t)((ef << 3) | (q - 8));
  } else code = q;                                      // qe == -9: subnormal
  return code | s;
}

__global__ void cast_all(unsigned long long* bad, uint32_t* first) {
  uint64_t stride = (uint64_t)gridDim.x * blockDim.x;
  unsigned long long nb = 0;
  for (uint64_t i = (uint64_t)blockIdx.x * blockDim.x + threadIdx.x; i < (1ull << 32); i += stride) {
    uint32_t u = (uint32_t)i, v = u ^ 0x9E3779B9u;
    uint32_t d = cvt_pair(__uint_as_float(u), __uint_as_float(v));
    bool ok = (d >> 8) == ref_e4m3(u) && (d & 0xFF) == ref_e4m3(v);
    if (!ok) { nb++; if (atomicCAS(first, 0u, 1u) == 0u) { first[1] = u; first[2] = v; first[3] = d; } }
  }
  if (nb) atomicAdd(bad, nb);
}

__device__ __forceinline__ uint32_t mix(uint64_t x) {
  x ^= x >> 33; x *= 0xff51afd7ed558ccdull; x ^= x >> 33; x *= 0xc4ceb9fe1a85ec53ull; x ^= x >> 33;
  return (uint32_t)x;
}

__device__ __forceinline__ uint32_t pick(uint64_t i, uint32_t salt) {
  uint32_t r = mix(i * 2 + salt), cls = r & 7, sign = r & 0x80000000u, man = mix(i * 7 + salt + 99) & 0x7FFFFF;
  uint32_t e;
  if (cls == 0) e = 0;                                  // subnormal
  else if (cls == 1) e = 1 + (r >> 8) % 4;              // just above the subnormal range
  else if (cls == 2) e = 120 + (r >> 8) % 16;           // around 1 (the accumulators' range)
  else e = 1 + (r >> 8) % 254;                          // anywhere finite
  if (((r >> 16) & 15) == 0) man &= 0x7FFF00;           // short mantissas: more ties
  return sign | (e << 23) | man;
}

__global__ void fadd_all(unsigned long long* bad, unsigned long long* sub_cases, uint32_t* first, uint64_t n) {
  uint64_t stride = (uint64_t)gridDim.x * blockDim.x;
  unsigned long long nb = 0, ns = 0;
  for (uint64_t i = (uint64_t)blockIdx.x * blockDim.x + threadIdx.x; i < n; i += stride) {
    uint32_t ua = pick(i, 1), ub = pick(i, 2);
    if ((i & 3) == 0) ub = (ua ^ 0x80000000u) + (mix(i + 5) & 7) - 3;   // near-cancellation
    float a = __uint_as_float(ua), b = __uint_as_float(ub), hw;
    asm(ADD_PTX : "=f"(hw) : "f"(a), "f"(b));
    float ref = __double2float_rn((double)a + (double)b);
    uint32_t h = __float_as_uint(hw), r = __float_as_uint(ref);
    bool sub = ((h & 0x7F800000u) == 0 && (h & 0x7FFFFFu)) || ((r & 0x7F800000u) == 0 && (r & 0x7FFFFFu)) ||
               ((ua & 0x7F800000u) == 0 && (ua & 0x7FFFFFu)) || ((ub & 0x7F800000u) == 0 && (ub & 0x7FFFFFu));
    ns += sub;
    if (h != r) { nb++; if (atomicCAS(first, 0u, 1u) == 0u) { first[1] = ua; first[2] = ub; first[3] = h; first[4] = r; } }
  }
  atomicAdd(bad, nb); atomicAdd(sub_cases, ns);
}

__global__ void cast_dump(const uint32_t* in, uint8_t* out, size_t n) {
  size_t i = (size_t)blockIdx.x * blockDim.x + threadIdx.x;
  if (i < n) out[i] = (uint8_t)(cvt_pair(__uint_as_float(in[i]), 0.f) >> 8);
}

__global__ void fadd_dump(const uint32_t* in, uint32_t* out, size_t n) {
  size_t i = (size_t)blockIdx.x * blockDim.x + threadIdx.x;
  if (i < n) {
    float s;
    asm(ADD_PTX : "=f"(s) : "f"(__uint_as_float(in[2 * i])), "f"(__uint_as_float(in[2 * i + 1])));
    out[i] = __float_as_uint(s);
  }
}

__global__ void mma_pairs(float* out) {                // block (c, d): one warp, A = c everywhere, B = d everywhere
  uint32_t c = blockIdx.x, d = blockIdx.y;
  uint32_t a = c * 0x01010101u, b = d * 0x01010101u;
  float d0 = 0, d1 = 0, d2 = 0, d3 = 0;
  asm volatile("mma.sync.aligned.m16n8k32.row.col.f32.e4m3.e4m3.f32 {%0,%1,%2,%3}, {%4,%5,%6,%7}, {%8,%9}, {%0,%1,%2,%3};"
               : "+f"(d0), "+f"(d1), "+f"(d2), "+f"(d3) : "r"(a), "r"(a), "r"(a), "r"(a), "r"(b), "r"(b));
  float lo = fminf(fminf(d0, d1), fminf(d2, d3)), hi = fmaxf(fmaxf(d0, d1), fmaxf(d2, d3));
  for (int o = 16; o; o >>= 1) { lo = fminf(lo, __shfl_xor_sync(~0u, lo, o)); hi = fmaxf(hi, __shfl_xor_sync(~0u, hi, o)); }
  if (threadIdx.x == 0) { out[2 * (c * 256 + d)] = lo; out[2 * (c * 256 + d) + 1] = hi; }
}

static float e4m3_val(uint32_t c) {
  uint32_t s = c >> 7, e = (c >> 3) & 15, m = c & 7;
  float v = e ? ldexpf(1.f + m / 8.f, (int)e - 7) : ldexpf((float)m, -9);
  return s ? -v : v;
}

static std::vector<uint8_t> slurp(const char* p) {
  FILE* f = fopen(p, "rb"); if (!f) { perror(p); exit(2); }
  std::vector<uint8_t> v; uint8_t buf[1 << 16]; size_t r;
  while ((r = fread(buf, 1, sizeof buf, f)) > 0) v.insert(v.end(), buf, buf + r);
  fclose(f); return v;
}

int main(int argc, char** argv) {
  if (argc < 2) { fprintf(stderr, "usage: %s cast|fadd|mma|castdump IN OUT|fadddump IN OUT\n", argv[0]); return 1; }
  const char* mode = argv[1];
#ifdef POSITIVE_CONTROL
  const int ftz_build = 1;
#else
  const int ftz_build = 0;
#endif
  cudaDeviceProp p; CK(cudaGetDeviceProperties(&p, 0));
  if (!strcmp(mode, "cast")) {
    unsigned long long* bad; uint32_t* first;
    CK(cudaMallocManaged(&bad, 8)); CK(cudaMallocManaged(&first, 16)); *bad = 0; memset(first, 0, 16);
    cast_all<<<p.multiProcessorCount * 8, 256>>>(bad, first); CK(cudaDeviceSynchronize());
    printf("{\"check\":\"cast\",\"inputs\":%llu,\"lanes\":2,\"bad\":%llu,\"first\":[%u,%u,%u]}\n", 1ull << 32, *bad,
           first[1], first[2], first[3]);
  } else if (!strcmp(mode, "fadd")) {
    unsigned long long *bad, *sub; uint32_t* first; uint64_t n = 1ull << 32;
    CK(cudaMallocManaged(&bad, 8)); CK(cudaMallocManaged(&sub, 8)); CK(cudaMallocManaged(&first, 20));
    *bad = 0; *sub = 0; memset(first, 0, 20);
    fadd_all<<<p.multiProcessorCount * 8, 256>>>(bad, sub, first, n); CK(cudaDeviceSynchronize());
    printf("{\"check\":\"fadd\",\"pairs\":%llu,\"subnormal_cases\":%llu,\"bad\":%llu,\"first\":[%u,%u,%u,%u]}\n",
           (unsigned long long)n, *sub, *bad, first[1], first[2], first[3], first[4]);
  } else if (!strcmp(mode, "mma")) {
    float* out; CK(cudaMallocManaged(&out, 256 * 256 * 2 * 4));
    mma_pairs<<<dim3(256, 256), 32>>>(out); CK(cudaDeviceSynchronize());
    unsigned long long pairs = 0, bad = 0, sub_pairs = 0; int fc = -1, fd = -1;
    for (uint32_t c = 0; c < 256; ++c) for (uint32_t d = 0; d < 256; ++d) {
      if ((c & 0x7F) == 0x7F || (d & 0x7F) == 0x7F) continue;          // NaN codes
      float want = 32.f * e4m3_val(c) * e4m3_val(d);
      float lo = out[2 * (c * 256 + d)], hi = out[2 * (c * 256 + d) + 1];
      pairs++; sub_pairs += ((c & 0x78) == 0 && (c & 7)) || ((d & 0x78) == 0 && (d & 7));
      if (!(lo == want && hi == want)) { bad++; if (fc < 0) { fc = c; fd = d; } }
    }
    printf("{\"check\":\"mma\",\"pairs\":%llu,\"subnormal_pairs\":%llu,\"bad\":%llu,\"first\":[%d,%d]}\n", pairs, sub_pairs, bad,
           fc, fd);
  } else if ((!strcmp(mode, "castdump") || !strcmp(mode, "fadddump")) && argc == 4) {
    std::vector<uint8_t> raw = slurp(argv[2]);
    bool is_cast = !strcmp(mode, "castdump");
    size_t n = raw.size() / (is_cast ? 4 : 8), ob = n * (is_cast ? 1 : 4);
    uint32_t* din; void* dout; CK(cudaMalloc(&din, raw.size())); CK(cudaMalloc(&dout, ob));
    CK(cudaMemcpy(din, raw.data(), raw.size(), cudaMemcpyHostToDevice));
    if (is_cast) cast_dump<<<(n + 255) / 256, 256>>>(din, (uint8_t*)dout, n);
    else fadd_dump<<<(n + 255) / 256, 256>>>(din, (uint32_t*)dout, n);
    CK(cudaDeviceSynchronize());
    std::vector<uint8_t> o(ob); CK(cudaMemcpy(o.data(), dout, ob, cudaMemcpyDeviceToHost));
    FILE* f = fopen(argv[3], "wb"); fwrite(o.data(), 1, ob, f); fclose(f);
    printf("{\"check\":\"%s\",\"n\":%zu}\n", mode, n);
  } else { fprintf(stderr, "bad mode\n"); return 1; }
  fprintf(stderr, "device=%s ftz_build=%d\n", p.name, ftz_build);
  return 0;
}
