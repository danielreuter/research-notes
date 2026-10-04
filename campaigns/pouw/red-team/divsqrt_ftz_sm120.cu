// `fp-model/sm120-scalar`'s allowlist: nvcc's correctly rounded div.rn.f32, rcp.rn.f32 and sqrt.rn.f32 lower to sequences
// that contain .FTZ ops even in a build without an FTZ flag. The harness's SASS gate allows exactly those sequences, on the
// condition that they are bit-exact against a correctly rounded reference, subnormals included. This checks that on the card:
//   sqrt   sqrt.rn.f32 on all 2^32 inputs, against sqrt in double rounded once (innocuous double rounding: 53 >= 2*24 + 2)
//   rcp    rcp.rn.f32 on all 2^32 inputs, against 1/x in double rounded once
//   div    div.rn.f32 on 2^32 counter-hashed pairs weighted to subnormal operands and results, ties and the overflow edge,
//          against a/b in double rounded once
//   dump   the device's div and sqrt on a host sample, for `verity.ml.tc.fp32.div` / `fp32.sqrt`
// NaN results compare as equal whatever their payload (outside the domain); everything else must match bit for bit.
//   nvcc -O3 -std=c++17 -gencode arch=compute_120a,code=sm_120a divsqrt_ftz_sm120.cu -o divsqrt
#include <cuda_runtime.h>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>

#define CK(x) do { cudaError_t e_ = (x); if (e_ != cudaSuccess) { \
  fprintf(stderr, "CUDA %s at %s:%d\n", cudaGetErrorString(e_), __FILE__, __LINE__); exit(2); } } while (0)

__device__ __forceinline__ bool same(float h, float r) {
  uint32_t a = __float_as_uint(h), b = __float_as_uint(r);
  return a == b || (h != h && r != r);
}
__device__ __forceinline__ bool subn(float x) {
  uint32_t u = __float_as_uint(x);
  return (u & 0x7F800000u) == 0 && (u & 0x7FFFFFu);
}

__global__ void sqrt_all(unsigned long long* bad, unsigned long long* sub, uint32_t* first) {
  unsigned long long nb = 0, ns = 0;
  for (uint64_t i = (uint64_t)blockIdx.x * blockDim.x + threadIdx.x; i < (1ull << 32); i += (uint64_t)gridDim.x * blockDim.x) {
    float x = __uint_as_float((uint32_t)i), h;
    asm("sqrt.rn.f32 %0, %1;" : "=f"(h) : "f"(x));
    float r = __double2float_rn(sqrt((double)x));
    ns += subn(x);
    if (!same(h, r)) { nb++; if (atomicCAS(first, 0u, 1u) == 0u) { first[1] = (uint32_t)i; first[2] = __float_as_uint(h); first[3] = __float_as_uint(r); } }
  }
  atomicAdd(bad, nb); atomicAdd(sub, ns);
}

__global__ void rcp_all(unsigned long long* bad, unsigned long long* sub, uint32_t* first) {
  unsigned long long nb = 0, ns = 0;
  for (uint64_t i = (uint64_t)blockIdx.x * blockDim.x + threadIdx.x; i < (1ull << 32); i += (uint64_t)gridDim.x * blockDim.x) {
    float x = __uint_as_float((uint32_t)i), h;
    asm("rcp.rn.f32 %0, %1;" : "=f"(h) : "f"(x));
    float r = __double2float_rn(1.0 / (double)x);
    ns += subn(x) || subn(r);
    if (!same(h, r)) { nb++; if (atomicCAS(first, 0u, 1u) == 0u) { first[1] = (uint32_t)i; first[2] = __float_as_uint(h); first[3] = __float_as_uint(r); } }
  }
  atomicAdd(bad, nb); atomicAdd(sub, ns);
}

__device__ __forceinline__ uint32_t mix(uint64_t x) {
  x ^= x >> 33; x *= 0xff51afd7ed558ccdull; x ^= x >> 33; x *= 0xc4ceb9fe1a85ec53ull; x ^= x >> 33;
  return (uint32_t)x;
}

__device__ __forceinline__ uint32_t pick(uint64_t i, uint32_t salt) {
  uint32_t r = mix(i * 2 + salt), cls = r & 7, man = mix(i * 7 + salt + 99) & 0x7FFFFF, e;
  if (cls == 0) e = 0;                                  // subnormal
  else if (cls == 1) e = 1 + (r >> 8) % 8;              // just above
  else if (cls == 2) e = 247 + (r >> 8) % 8;            // near overflow
  else if (cls == 3) e = 120 + (r >> 8) % 16;           // around 1
  else e = 1 + (r >> 8) % 254;
  if (((r >> 16) & 7) == 0) man &= 0x7F0000;            // short mantissas: exact quotients and ties
  return (r & 0x80000000u) | (e << 23) | man;
}

__global__ void div_all(unsigned long long* bad, unsigned long long* sub, uint32_t* first, uint64_t n) {
  unsigned long long nb = 0, ns = 0;
  for (uint64_t i = (uint64_t)blockIdx.x * blockDim.x + threadIdx.x; i < n; i += (uint64_t)gridDim.x * blockDim.x) {
    float a = __uint_as_float(pick(i, 1)), b = __uint_as_float(pick(i, 2)), h;
    asm("div.rn.f32 %0, %1, %2;" : "=f"(h) : "f"(a), "f"(b));
    float r = __double2float_rn((double)a / (double)b);
    ns += subn(a) || subn(b) || subn(r);
    if (!same(h, r)) { nb++; if (atomicCAS(first, 0u, 1u) == 0u) { first[1] = __float_as_uint(a); first[2] = __float_as_uint(b); first[3] = __float_as_uint(h); first[4] = __float_as_uint(r); } }
  }
  atomicAdd(bad, nb); atomicAdd(sub, ns);
}

__global__ void dump(const uint32_t* in, uint32_t* out, size_t n) {   // in: (a, b) pairs; out: (div, sqrt(a))
  size_t i = (size_t)blockIdx.x * blockDim.x + threadIdx.x;
  if (i < n) {
    float a = __uint_as_float(in[2 * i]), b = __uint_as_float(in[2 * i + 1]), q, s;
    asm("div.rn.f32 %0, %1, %2;" : "=f"(q) : "f"(a), "f"(b));
    asm("sqrt.rn.f32 %0, %1;" : "=f"(s) : "f"(a));
    out[2 * i] = __float_as_uint(q); out[2 * i + 1] = __float_as_uint(s);
  }
}

int main(int argc, char** argv) {
  if (argc < 2) return 1;
  cudaDeviceProp p; CK(cudaGetDeviceProperties(&p, 0));
  const char* m = argv[1];
  if (!strcmp(m, "dump") && argc == 4) {
    FILE* f = fopen(argv[2], "rb"); std::vector<uint32_t> in; uint32_t w;
    while (fread(&w, 4, 1, f) == 1) in.push_back(w);
    fclose(f);
    size_t n = in.size() / 2;
    uint32_t *din, *dout; CK(cudaMalloc(&din, in.size() * 4)); CK(cudaMalloc(&dout, in.size() * 4));
    CK(cudaMemcpy(din, in.data(), in.size() * 4, cudaMemcpyHostToDevice));
    dump<<<(n + 255) / 256, 256>>>(din, dout, n); CK(cudaDeviceSynchronize());
    std::vector<uint32_t> out(in.size()); CK(cudaMemcpy(out.data(), dout, out.size() * 4, cudaMemcpyDeviceToHost));
    f = fopen(argv[3], "wb"); fwrite(out.data(), 4, out.size(), f); fclose(f);
    printf("{\"check\":\"dump\",\"n\":%zu}\n", n);
    return 0;
  }
  unsigned long long *bad, *sub; uint32_t* first;
  CK(cudaMallocManaged(&bad, 8)); CK(cudaMallocManaged(&sub, 8)); CK(cudaMallocManaged(&first, 20));
  *bad = 0; *sub = 0; memset(first, 0, 20);
  const int grid = p.multiProcessorCount * 8;
  unsigned long long n = 1ull << 32;
  if (!strcmp(m, "sqrt")) sqrt_all<<<grid, 256>>>(bad, sub, first);
  else if (!strcmp(m, "rcp")) rcp_all<<<grid, 256>>>(bad, sub, first);
  else if (!strcmp(m, "div")) div_all<<<grid, 256>>>(bad, sub, first, n);
  else return 1;
  CK(cudaDeviceSynchronize());
  printf("{\"check\":\"%s\",\"cases\":%llu,\"subnormal_cases\":%llu,\"bad\":%llu,\"first\":[%u,%u,%u,%u]}\n", m, n, *sub, *bad,
         first[1], first[2], first[3], first[4]);
  return 0;
}
