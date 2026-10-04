// `__frsqrt_rn` on sm_120a (GPU 1's forming uses it; its nvcc sequence emits .FTZ ops): exact on all 2^32 inputs?
// The reference is exact, not a double rounded once (rsqrt is not an operation for which one double rounding is innocuous):
// for positive finite x, y is the correctly rounded 1/sqrt(x) iff the midpoints m- and m+ around y satisfy
// m-^2 x < 1 < m+^2 x (ties, m^2 x = 1, go to the even neighbour). m^2 is exact in double (m has 25 significant bits) and
// m^2 x - 1 is formed exactly as (p - 1) + fma(m^2, x, -p) with p = m^2 x (Sterbenz: p is near 1), so its sign is exact.
// Specials: +0 -> +inf, -0 -> -inf, +inf -> +0, negative or NaN -> NaN (any payload).
//   nvcc -O3 -std=c++17 -gencode arch=compute_120a,code=sm_120a frsqrt_sm120.cu -o frsqrt && ./frsqrt
#include <cuda_runtime.h>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>

#define CK(x) do { cudaError_t e_ = (x); if (e_ != cudaSuccess) { \
  fprintf(stderr, "CUDA %s at %s:%d\n", cudaGetErrorString(e_), __FILE__, __LINE__); exit(2); } } while (0)

__device__ int side(double m, double x) {              // sign of m^2 x - 1, exactly
  double m2 = m * m, p = m2 * x, e = fma(m2, x, -p), s = (p - 1.0) + e;
  return (s > 0) - (s < 0);
}

__device__ bool correct(float y, float x) {
  uint32_t u = __float_as_uint(y);
  double yd = y, up = __uint_as_float(u + 1), dn = __uint_as_float(u - 1), X = x;
  int lo = side((yd + dn) / 2, X), hi = side((yd + up) / 2, X);
  bool even = (u & 1) == 0;
  return (lo < 0 || (lo == 0 && even)) && (hi > 0 || (hi == 0 && even));
}

__device__ float ref(float x) {
  uint32_t u = __float_as_uint(x);
  if (x != x || ((u >> 31) && (u & 0x7FFFFFFFu))) return __uint_as_float(0x7FC00000u);
  if ((u & 0x7FFFFFFFu) == 0) return (u >> 31) ? -__int_as_float(0x7F800000) : __int_as_float(0x7F800000);
  if (u == 0x7F800000u) return 0.0f;
  float y = __double2float_rn(1.0 / sqrt((double)x));
  for (int d = 0; d < 3 && !correct(y, x); ++d) {       // the once-rounded guess is off by at most an ulp; try its neighbours
    float a = __uint_as_float(__float_as_uint(y) + 1), b = __uint_as_float(__float_as_uint(y) - 1);
    y = correct(a, x) ? a : b;
  }
  return y;
}

__global__ void run(unsigned long long* bad, unsigned long long* fixed, unsigned long long* sub, uint32_t* first) {
  unsigned long long nb = 0, nf = 0, ns = 0;
  for (uint64_t i = (uint64_t)blockIdx.x * blockDim.x + threadIdx.x; i < (1ull << 32); i += (uint64_t)gridDim.x * blockDim.x) {
    float x = __uint_as_float((uint32_t)i), h = __frsqrt_rn(x), r = ref(x);
    uint32_t xu = (uint32_t)i;
    ns += (xu & 0x7F800000u) == 0 && (xu & 0x7FFFFFu) && !(xu >> 31);
    if (x > 0 && x < __int_as_float(0x7F800000) && __double2float_rn(1.0 / sqrt((double)x)) != r) nf++;
    bool ok = __float_as_uint(h) == __float_as_uint(r) || (h != h && r != r);
    if (!ok) { nb++; if (atomicCAS(first, 0u, 1u) == 0u) { first[1] = xu; first[2] = __float_as_uint(h); first[3] = __float_as_uint(r); } }
  }
  atomicAdd(bad, nb); atomicAdd(fixed, nf); atomicAdd(sub, ns);
}

int main() {
  cudaDeviceProp p; CK(cudaGetDeviceProperties(&p, 0));
  unsigned long long *bad, *fixed, *sub; uint32_t* first;
  CK(cudaMallocManaged(&bad, 8)); CK(cudaMallocManaged(&fixed, 8)); CK(cudaMallocManaged(&sub, 8)); CK(cudaMallocManaged(&first, 16));
  *bad = *fixed = *sub = 0; memset(first, 0, 16);
  run<<<p.multiProcessorCount * 8, 256>>>(bad, fixed, sub, first); CK(cudaDeviceSynchronize());
  printf("{\"check\":\"frsqrt_rn\",\"inputs\":%llu,\"subnormal_inputs\":%llu,\"bad\":%llu,"
         "\"double_guess_corrected\":%llu,\"first\":[%u,%u,%u]}\n", 1ull << 32, *sub, *bad, *fixed, first[1], first[2], first[3]);
  return 0;
}
