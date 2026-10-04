// The masked int8-Strassen route, run end to end (the assessor, bc-d7d4b0d1): F2's route on a flat NVFP4 tile.
// A (m x k) and B (n x k) hold E2M1 codes as int8 half-units (2·value, in [-12, 12]); on a flat tile (one scale byte on
// each side) the NVFP4 product is their integer product times one scale, so an exact route computes C = A·Bᵀ in s32.
// The route is breadth-first Strassen (7 products, 18 adds per level) to depth L:
//   pre-add  one fused kernel per level and side: reads the 4 quadrants once, writes the 7 children, saturating to int8
//            and counting elements outside [-128, 127] (such a leaf needs wider arithmetic, so the int8 route is not
//            exact there; the count is reported, and the check below catches it);
//   leaves   7^L batched int8 IMMA GEMMs (cuBLASLt, s8 x s8 -> s32), in calls of at most 7^5;
//   merge    one fused s32 kernel per level: 7 children in, 4 quadrants out.
// Every timed row is checked word for word against the direct int8 GEMM (cuBLASLt), with a poisoned word (one output
// changed by 1 must be caught) and, in the self-test, a negative control (a depth whose leaves overflow must mismatch).
//
// usage: int8_route_replay selftest
//        int8_route_replay N FAMILY L0 L1        (FAMILY: uniform | tiedmax | gauss; prints one JSON line per depth)
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <cstring>
#include <vector>
#include <string>
#include <cuda_runtime.h>
#include <cublasLt.h>

#define CK(x) do { cudaError_t ck_=(x); if(ck_!=cudaSuccess){fprintf(stderr,"cuda %s:%d %s\n",__FILE__,__LINE__,cudaGetErrorString(ck_));exit(2);} } while(0)
#define LK(x) do { cublasStatus_t lk_=(x); if(lk_!=CUBLAS_STATUS_SUCCESS){fprintf(stderr,"cublasLt %s:%d %d\n",__FILE__,__LINE__,(int)lk_);exit(2);} } while(0)

struct TabS { signed char c[7][4]; };   // per product, the coefficients of the stored quadrants (00, 01, 10, 11)
struct TabC { signed char c[4][7]; };   // per C quadrant (00, 01, 10, 11), the coefficients of M1..M7
// A is m x k row-major, so its stored quadrants are A11, A12, A21, A22. B is n x k row-major, so Bᵀ's quadrant ij is B's
// stored (j, i): stored (00, 01, 10, 11) = (Bᵀ11, Bᵀ21, Bᵀ12, Bᵀ22). Checked against A @ B.T by strassen_tables_check.py.
static const TabS TA = {{{1,0,0,1},{0,0,1,1},{1,0,0,0},{0,0,0,1},{1,1,0,0},{-1,0,1,0},{0,1,0,-1}}};
static const TabS TB = {{{1,0,0,1},{1,0,0,0},{0,0,1,-1},{-1,1,0,0},{0,0,0,1},{1,0,1,0},{0,1,0,1}}};
static const TabC TC = {{{1,0,0,1,-1,0,1},{0,0,1,0,1,0,0},{0,1,0,1,0,0,0},{1,-1,1,0,0,1,0}}};

__host__ __device__ inline uint64_t mix64(uint64_t x){
  x += 0x9E3779B97F4A7C15ULL; x = (x ^ (x >> 30)) * 0xBF58476D1CE4E5B9ULL; x = (x ^ (x >> 27)) * 0x94D049BB133111EBULL;
  return x ^ (x >> 31);
}
__constant__ signed char E2M1H[16] = {0,1,2,3,4,6,8,12,0,-1,-2,-3,-4,-6,-8,-12};

// families: 0 uniform over the 16 codes; 1 tiedmax (uniform, one +-12 per 16-block: the flat single-class rows);
// 2 gauss (N(0,1) per 16-block cast to E2M1 at amax/6, the smallest codes a real block has); 3 small (|v| <= 3, self-test)
__global__ void gen(signed char* x, size_t n, uint64_t seed, int fam){
  size_t nb = n / 16;
  for(size_t b = blockIdx.x*(size_t)blockDim.x + threadIdx.x; b < nb; b += (size_t)gridDim.x*blockDim.x){
    signed char* o = x + b*16; uint64_t h = mix64(seed ^ (b * 0x100000001B3ULL));
    if(fam == 2){
      float g[16], amax = 0.f;
      for(int t = 0; t < 16; t++){
        uint64_t r = mix64(h + 1000 + t);
        float u1 = ((float)(r >> 40) + 1.f) / 16777217.f, u2 = (float)((r >> 8) & 0xFFFFFF) / 16777216.f;
        g[t] = sqrtf(-2.f * logf(u1)) * cospif(2.f * u2); amax = fmaxf(amax, fabsf(g[t]));
      }
      const float mid[7] = {0.25f,0.75f,1.25f,1.75f,2.5f,3.5f,5.f}; const signed char hv[8] = {0,1,2,3,4,6,8,12};
      for(int t = 0; t < 16; t++){
        float q = fabsf(g[t]) * 6.f / amax; int c = 0; while(c < 7 && q >= mid[c]) c++;
        o[t] = g[t] < 0 ? -hv[c] : hv[c];
      }
    } else {
      for(int t = 0; t < 16; t++){
        uint64_t r = mix64(h + t);
        o[t] = fam == 3 ? (signed char)((int)((r >> 8) % 7) - 3) : E2M1H[r & 15];
      }
      if(fam == 1) o[(h >> 40) & 15] = ((h >> 50) & 1) ? 12 : -12;
    }
  }
}

__global__ void preadd(const signed char* __restrict__ par, signed char* __restrict__ ch, size_t P, int R, int C, TabS tab,
                       unsigned long long* ovf){
  int hr = R / 2, hc = C / 2, hc4 = hc / 4; size_t per = (size_t)hr * hc4, total = P * per; unsigned cnt = 0;
  for(size_t idx = blockIdx.x*(size_t)blockDim.x + threadIdx.x; idx < total; idx += (size_t)gridDim.x*blockDim.x){
    size_t p = idx / per, rem = idx % per; int i = (int)(rem / hc4), j4 = (int)(rem % hc4);
    const signed char* base = par + p * (size_t)R * C;
    char4 q[4];
    q[0] = *(const char4*)(base + (size_t)i*C + 4*j4);
    q[1] = *(const char4*)(base + (size_t)i*C + hc + 4*j4);
    q[2] = *(const char4*)(base + (size_t)(i + hr)*C + 4*j4);
    q[3] = *(const char4*)(base + (size_t)(i + hr)*C + hc + 4*j4);
#pragma unroll
    for(int t = 0; t < 7; t++){
      int v0 = 0, v1 = 0, v2 = 0, v3 = 0;
#pragma unroll
      for(int s = 0; s < 4; s++){ int w = tab.c[t][s]; v0 += w*q[s].x; v1 += w*q[s].y; v2 += w*q[s].z; v3 += w*q[s].w; }
      cnt += (v0 > 127 || v0 < -128) + (v1 > 127 || v1 < -128) + (v2 > 127 || v2 < -128) + (v3 > 127 || v3 < -128);
      char4 o; o.x = (signed char)max(-128, min(127, v0)); o.y = (signed char)max(-128, min(127, v1));
      o.z = (signed char)max(-128, min(127, v2)); o.w = (signed char)max(-128, min(127, v3));
      *(char4*)(ch + (p*7 + t) * (size_t)hr * hc + (size_t)i*hc + 4*j4) = o;
    }
  }
  cnt = __reduce_add_sync(0xffffffffu, cnt);
  if((threadIdx.x & 31) == 0 && cnt) atomicAdd(ovf, (unsigned long long)cnt);
}

__global__ void postadd(const int* __restrict__ ch, int* __restrict__ par, size_t P, int Rm, int Rn, TabC tab){
  int rm4 = Rm / 4; size_t per = (size_t)rm4 * Rn, total = P * per;
  for(size_t idx = blockIdx.x*(size_t)blockDim.x + threadIdx.x; idx < total; idx += (size_t)gridDim.x*blockDim.x){
    size_t p = idx / per, rem = idx % per; int j = (int)(rem / rm4), i4 = (int)(rem % rm4);
    int4 m[7];
#pragma unroll
    for(int t = 0; t < 7; t++) m[t] = *(const int4*)(ch + (p*7 + t) * (size_t)Rm * Rn + (size_t)j*Rm + 4*i4);
#pragma unroll
    for(int qd = 0; qd < 4; qd++){
      int qi = qd >> 1, qj = qd & 1; int4 s = make_int4(0, 0, 0, 0);
#pragma unroll
      for(int t = 0; t < 7; t++){ int w = tab.c[qd][t]; s.x += w*m[t].x; s.y += w*m[t].y; s.z += w*m[t].z; s.w += w*m[t].w; }
      *(int4*)(par + p * (size_t)4 * Rm * Rn + (size_t)(j + qj*Rn) * (2*Rm) + qi*Rm + 4*i4) = s;
    }
  }
}

__global__ void diff_count(const int* a, const int* b, size_t n, unsigned long long* out){
  unsigned cnt = 0;
  for(size_t i = blockIdx.x*(size_t)blockDim.x + threadIdx.x; i < n; i += (size_t)gridDim.x*blockDim.x) cnt += a[i] != b[i];
  cnt = __reduce_add_sync(0xffffffffu, cnt);
  if((threadIdx.x & 31) == 0 && cnt) atomicAdd(out, (unsigned long long)cnt);
}

// One batched int8 GEMM shape: C_b (m x n col-major) = A_b (m x k row-major) · B_bᵀ (B_b n x k row-major), b < batch.
struct Gemm {
  cublasLtHandle_t lt; cublasLtMatmulDesc_t op; cublasLtMatrixLayout_t la, lb, lc; cublasLtMatmulAlgo_t algo;
  bool ok = false; void* ws; size_t wsz; int m, n, k, batch;
};
static void gemm_init(Gemm& g, cublasLtHandle_t lt, int m, int n, int k, int batch, void* ws, size_t wsz){
  g.lt = lt; g.m = m; g.n = n; g.k = k; g.batch = batch; g.ws = ws; g.wsz = wsz;
  LK(cublasLtMatmulDescCreate(&g.op, CUBLAS_COMPUTE_32I, CUDA_R_32I));
  cublasOperation_t tn = CUBLAS_OP_T, nn = CUBLAS_OP_N;
  LK(cublasLtMatmulDescSetAttribute(g.op, CUBLASLT_MATMUL_DESC_TRANSA, &tn, sizeof(tn)));
  LK(cublasLtMatmulDescSetAttribute(g.op, CUBLASLT_MATMUL_DESC_TRANSB, &nn, sizeof(nn)));
  LK(cublasLtMatrixLayoutCreate(&g.la, CUDA_R_8I, k, m, k));
  LK(cublasLtMatrixLayoutCreate(&g.lb, CUDA_R_8I, k, n, k));
  LK(cublasLtMatrixLayoutCreate(&g.lc, CUDA_R_32I, m, n, m));
  if(batch > 1){
    int64_t oa = (int64_t)m*k, ob = (int64_t)n*k, oc = (int64_t)m*n;
    cublasLtMatrixLayout_t ls[3] = {g.la, g.lb, g.lc}; int64_t os[3] = {oa, ob, oc};
    for(int i = 0; i < 3; i++){
      LK(cublasLtMatrixLayoutSetAttribute(ls[i], CUBLASLT_MATRIX_LAYOUT_BATCH_COUNT, &batch, sizeof(batch)));
      LK(cublasLtMatrixLayoutSetAttribute(ls[i], CUBLASLT_MATRIX_LAYOUT_STRIDED_BATCH_OFFSET, &os[i], sizeof(os[i])));
    }
  }
  cublasLtMatmulPreference_t pref; LK(cublasLtMatmulPreferenceCreate(&pref));
  LK(cublasLtMatmulPreferenceSetAttribute(pref, CUBLASLT_MATMUL_PREF_MAX_WORKSPACE_BYTES, &wsz, sizeof(wsz)));
  cublasLtMatmulHeuristicResult_t h[1]; int got = 0;
  cublasStatus_t st = cublasLtMatmulAlgoGetHeuristic(lt, g.op, g.la, g.lb, g.lc, g.lc, pref, 1, h, &got);
  if(st == CUBLAS_STATUS_SUCCESS && got > 0){ g.algo = h[0].algo; g.ok = true; }
  cublasLtMatmulPreferenceDestroy(pref);
}
static void gemm_run(Gemm& g, const void* A, const void* B, void* C, cudaStream_t s){
  int32_t alpha = 1, beta = 0;
  LK(cublasLtMatmul(g.lt, g.op, &alpha, A, g.la, B, g.lb, &beta, C, g.lc, C, g.lc, &g.algo, g.ws, g.wsz, s));
}

static size_t pw7(int l){ size_t r = 1; while(l--) r *= 7; return r; }
static int grid_for(size_t n){ size_t b = (n + 255) / 256; return (int)(b < 188 * 64 ? (b ? b : 1) : 188 * 64); }

struct Result { double ms_pre = 0, ms_leaf = 0, ms_post = 0, ms_total = 0; unsigned long long ovf_a = 0, ovf_b = 0, mism = 0;
                long long poison = -1; bool supported = true; int iters = 0; };

// The route at depth L on A0, B0 (N x N each), checked against cref. Buffers ping-pong so that each side holds two levels.
static Result route(int N, int L, const signed char* A0, const signed char* B0, const int* cref, cublasLtHandle_t lt,
                    void* ws, size_t wsz, cudaStream_t s, int iters){
  Result r; r.iters = iters;
  auto lsz = [&](int l){ size_t d = (size_t)N >> l; return pw7(l) * d * d; };
  signed char *AX = nullptr, *AY = nullptr, *BX = nullptr, *BY = nullptr; int *CX = nullptr, *CY = nullptr;
  if(L >= 1){ CK(cudaMalloc(&AX, lsz(L))); CK(cudaMalloc(&BX, lsz(L))); }
  if(L >= 2){ CK(cudaMalloc(&AY, lsz(L - 1))); CK(cudaMalloc(&BY, lsz(L - 1))); }
  CK(cudaMalloc(&CX, lsz(L) * 4)); if(L >= 1) CK(cudaMalloc(&CY, lsz(L - 1) * 4));
  auto abuf = [&](int l, bool a) -> signed char* { if(l == 0) return (signed char*)(a ? A0 : B0);
                                                   return ((L - l) % 2 == 0) ? (a ? AX : BX) : (a ? AY : BY); };
  auto cbuf = [&](int l) -> int* { return ((L - l) % 2 == 0) ? CX : CY; };
  int leaf = N >> L; size_t nleaf = pw7(L); int chunk_l = L < 5 ? L : 5; size_t chunk = pw7(chunk_l), calls = nleaf / chunk;
  Gemm g; gemm_init(g, lt, leaf, leaf, leaf, (int)chunk, ws, wsz);
  if(!g.ok){ r.supported = false; cudaFree(AX); cudaFree(AY); cudaFree(BX); cudaFree(BY); cudaFree(CX); cudaFree(CY); return r; }
  unsigned long long* dcnt; CK(cudaMalloc(&dcnt, 3 * sizeof(unsigned long long)));
  cudaEvent_t e0, e1, e2, e3; cudaEventCreate(&e0); cudaEventCreate(&e1); cudaEventCreate(&e2); cudaEventCreate(&e3);
  auto once = [&](bool timed){
    CK(cudaMemsetAsync(dcnt, 0, 3 * sizeof(unsigned long long), s));
    if(timed) cudaEventRecord(e0, s);
    for(int l = 0; l < L; l++){
      size_t P = pw7(l), d = (size_t)N >> l, per = P * (d / 2) * (d / 8);
      preadd<<<grid_for(per), 256, 0, s>>>(abuf(l, true), abuf(l + 1, true), P, (int)d, (int)d, TA, dcnt);
      preadd<<<grid_for(per), 256, 0, s>>>(abuf(l, false), abuf(l + 1, false), P, (int)d, (int)d, TB, dcnt + 1);
    }
    if(timed) cudaEventRecord(e1, s);
    size_t sa = (size_t)leaf * leaf;
    for(size_t c = 0; c < calls; c++)
      gemm_run(g, abuf(L, true) + c * chunk * sa, abuf(L, false) + c * chunk * sa, cbuf(L) + c * chunk * sa, s);
    if(timed) cudaEventRecord(e2, s);
    for(int l = L - 1; l >= 0; l--){
      size_t P = pw7(l), h = (size_t)N >> (l + 1), per = P * (h / 4) * h;
      postadd<<<grid_for(per), 256, 0, s>>>(cbuf(l + 1), cbuf(l), P, (int)h, (int)h, TC);
    }
    if(timed) cudaEventRecord(e3, s);
  };
  once(false); CK(cudaStreamSynchronize(s)); CK(cudaGetLastError());
  for(int it = 0; it < iters; it++){
    once(true); CK(cudaEventSynchronize(e3));
    float a, b, c; cudaEventElapsedTime(&a, e0, e1); cudaEventElapsedTime(&b, e1, e2); cudaEventElapsedTime(&c, e2, e3);
    r.ms_pre += a / iters; r.ms_leaf += b / iters; r.ms_post += c / iters;
  }
  r.ms_total = r.ms_pre + r.ms_leaf + r.ms_post;
  unsigned long long h[3]; CK(cudaMemcpy(h, dcnt, 2 * sizeof(unsigned long long), cudaMemcpyDeviceToHost));
  r.ovf_a = h[0]; r.ovf_b = h[1];
  int* c0 = cbuf(0); size_t nn = (size_t)N * N;
  CK(cudaMemset(dcnt + 2, 0, sizeof(unsigned long long)));
  diff_count<<<grid_for(nn), 256, 0, s>>>(c0, cref, nn, dcnt + 2); CK(cudaStreamSynchronize(s));
  CK(cudaMemcpy(&r.mism, dcnt + 2, sizeof(unsigned long long), cudaMemcpyDeviceToHost));
  size_t pidx = (nn / 2) + 12345 % (nn / 2); int w; CK(cudaMemcpy(&w, c0 + pidx, 4, cudaMemcpyDeviceToHost));
  int w1 = w + 1; CK(cudaMemcpy(c0 + pidx, &w1, 4, cudaMemcpyHostToDevice));
  CK(cudaMemset(dcnt + 2, 0, sizeof(unsigned long long)));
  diff_count<<<grid_for(nn), 256, 0, s>>>(c0, cref, nn, dcnt + 2); CK(cudaStreamSynchronize(s));
  unsigned long long pm; CK(cudaMemcpy(&pm, dcnt + 2, sizeof(unsigned long long), cudaMemcpyDeviceToHost));
  r.poison = (long long)pm - (long long)r.mism;
  cudaFree(dcnt); cudaFree(AX); cudaFree(AY); cudaFree(BX); cudaFree(BY); cudaFree(CX); cudaFree(CY);
  return r;
}

static int fam_of(const char* s){
  if(!strcmp(s, "uniform")) return 0; if(!strcmp(s, "tiedmax")) return 1; if(!strcmp(s, "gauss")) return 2;
  if(!strcmp(s, "small")) return 3; fprintf(stderr, "family %s\n", s); exit(2);
}

struct Case { int N; signed char *A, *B; int* cref; double ms_ref; };
static Case make_case(int N, int fam, uint64_t seed, cublasLtHandle_t lt, void* ws, size_t wsz, cudaStream_t s, int iters){
  Case c; c.N = N; size_t nn = (size_t)N * N;
  CK(cudaMalloc(&c.A, nn)); CK(cudaMalloc(&c.B, nn)); CK(cudaMalloc(&c.cref, nn * 4));
  gen<<<grid_for(nn / 16), 256, 0, s>>>(c.A, nn, seed, fam); gen<<<grid_for(nn / 16), 256, 0, s>>>(c.B, nn, seed ^ 0xB0B, fam);
  Gemm g; gemm_init(g, lt, N, N, N, 1, ws, wsz); if(!g.ok){ fprintf(stderr, "no reference GEMM at %d\n", N); exit(2); }
  gemm_run(g, c.A, c.B, c.cref, s); CK(cudaStreamSynchronize(s));
  cudaEvent_t a, b; cudaEventCreate(&a); cudaEventCreate(&b);
  for(int i = 0; i < 3; i++) gemm_run(g, c.A, c.B, c.cref, s);
  cudaEventRecord(a, s); for(int i = 0; i < iters; i++) gemm_run(g, c.A, c.B, c.cref, s); cudaEventRecord(b, s);
  cudaEventSynchronize(b); float ms; cudaEventElapsedTime(&ms, a, b); c.ms_ref = ms / iters;
  return c;
}
static void free_case(Case& c){ cudaFree(c.A); cudaFree(c.B); cudaFree(c.cref); }

static void emit(const char* fam, int N, int L, const Case& c, const Result& r){
  printf("{\"op\":\"route\",\"family\":\"%s\",\"N\":%d,\"L\":%d,\"leaf\":%d,\"supported\":%s,\"iters\":%d,"
         "\"ms_preadd\":%.5f,\"ms_leaf\":%.5f,\"ms_merge\":%.5f,\"ms_total\":%.5f,\"ms_int8_gemm\":%.5f,"
         "\"overflow_a\":%llu,\"overflow_b\":%llu,\"mismatch\":%llu,\"poison_caught\":%lld}\n",
         fam, N, L, N >> L, r.supported ? "true" : "false", r.iters, r.ms_pre, r.ms_leaf, r.ms_post, r.ms_total, c.ms_ref,
         r.ovf_a, r.ovf_b, r.mism, r.poison);
  fflush(stdout);
}

int main(int argc, char** argv){
  cudaStream_t s; CK(cudaStreamCreate(&s));
  cublasLtHandle_t lt; LK(cublasLtCreate(&lt));
  size_t wsz = (size_t)256 << 20; void* ws; CK(cudaMalloc(&ws, wsz));
  if(argc >= 2 && !strcmp(argv[1], "selftest")){
    // exact where no leaf overflows (small codes to depth 3, E2M1 codes to depth 3 at |v| <= 96), with a caught poison,
    // and the negative control: E2M1 codes at depth 5 (64-wide leaves) overflow int8 and must mismatch
    struct T { int N, fam, L; bool exact; } ts[] = {{256,3,1,true},{256,3,2,true},{256,3,3,true},{256,0,3,true},
                                                    {512,0,2,true},{2048,0,5,false}};
    int bad = 0;
    for(auto t : ts){
      Case c = make_case(t.N, t.fam, 7, lt, ws, wsz, s, 3);
      Result r = route(t.N, t.L, c.A, c.B, c.cref, lt, ws, wsz, s, 1);
      emit(t.fam == 3 ? "small" : "uniform", t.N, t.L, c, r);
      bool ok = r.supported && (t.exact ? (r.mism == 0 && r.ovf_a + r.ovf_b == 0 && r.poison == 1)
                                        : (r.mism > 0 && r.ovf_a + r.ovf_b > 0));
      if(!ok){ fprintf(stderr, "selftest failed at N=%d fam=%d L=%d\n", t.N, t.fam, t.L); bad = 1; }
      free_case(c);
    }
    printf("{\"op\":\"selftest\",\"pass\":%s}\n", bad ? "false" : "true");
    return bad;
  }
  if(argc < 5){ fprintf(stderr, "usage: %s selftest | N FAMILY L0 L1\n", argv[0]); return 2; }
  int N = atoi(argv[1]), fam = fam_of(argv[2]), L0 = atoi(argv[3]), L1 = atoi(argv[4]);
  Case c = make_case(N, fam, 1, lt, ws, wsz, s, N <= 8192 ? 20 : 8);
  for(int L = L0; L <= L1; L++){
    if((N >> L) < 32) break;
    int iters = L <= 4 ? 10 : 3;
    Result r = route(N, L, c.A, c.B, c.cref, lt, ws, wsz, s, iters);
    emit(argv[2], N, L, c, r);
  }
  free_case(c);
  return 0;
}
