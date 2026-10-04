// The base-split break end to end, part 2 (device): CUTLASS 4.8's sm_120 NVFP4 GEMMs with FP32 words, on the operands
// `basesplit_e2e_rows.py` formed on the exact reference.  One binary per variant:
//   -DVARIANT_DENSE128   honest: dense block-scaled NVFP4 (79a's mainloop, 128x128x128 tile), the A′·B̃ᵀ words
//   -DVARIANT_DENSE256   honest, the 128x128x256 tile (the faster of the two is the divisor)
//   -DVARIANT_SPARSE     the split's residual: 2:4-sparse block-scaled NVFP4 (80b's mainloop) on ΔA with A′'s scales
//   -DOUT_BF16           BF16 words instead of FP32 (timing only), to show the ratio isn't the epilogue's
// Modes:
//   check  OPS OUT            at the operands' own size: every output poisoned (0xA5) first; writes D.f32 (beta = 0),
//                              DC.f32 (sparse, beta = 1 with C = the fast A0 part) and negctl.f32 (poisoned, no launch)
//   time   OPS M N K ITERS    operands tiled to M x N x K; one JSON line per arm with ms per launch (interleaving
//                              across variants is the caller's), plus the compressor's time for the sparse variant
//   verify OPS M N K          at the timed size: poison, launch once, compare 4,096 sampled words with the exact host
//                              sum (ACCEPT/REJECT); then the negative control (poison, no launch), which must REJECT
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cmath>
#include <chrono>
#include <fstream>
#include <string>
#include <vector>

#include "cutlass/cutlass.h"
#include "cute/tensor.hpp"
#include "cutlass/numeric_types.h"
#include "cutlass/gemm/dispatch_policy.hpp"
#include "cutlass/gemm/collective/collective_builder.hpp"
#include "cutlass/epilogue/collective/collective_builder.hpp"
#include "cutlass/detail/sm100_blockscaled_layout.hpp"
#include "cutlass/gemm/device/gemm_universal_adapter.h"
#include "cutlass/gemm/kernel/gemm_universal.hpp"
#include "cutlass/util/packed_stride.hpp"
#include "cutlass/util/device_memory.h"
#ifdef VARIANT_SPARSE
#include "cutlass/transform/kernel/sparse_gemm_compressor.hpp"
#include "cutlass/transform/device/transform_universal_adapter.hpp"
#endif

using namespace cute;

#define CK(x) do { cudaError_t e_ = (x); if (e_ != cudaSuccess) { fprintf(stderr, "cuda %s at %d: %s\n", #x, __LINE__, cudaGetErrorString(e_)); exit(2); } } while (0)
#define CS(x) do { cutlass::Status s_ = (x); if (s_ != cutlass::Status::kSuccess) { fprintf(stderr, "cutlass %s at %d: %s\n", #x, __LINE__, cutlassGetStatusString(s_)); exit(2); } } while (0)

#ifdef OUT_BF16
using ElementD = cutlass::bfloat16_t;
static const char *OUT = "bf16";
#else
using ElementD = float;
static const char *OUT = "f32";
#endif
using ElementC = ElementD;
using ElementAB = cutlass::nv_float4_t<cutlass::float_e2m1_t>;
using LayoutATag = cutlass::layout::RowMajor;
using LayoutBTag = cutlass::layout::ColumnMajor;
using LayoutCTag = cutlass::layout::RowMajor;
using LayoutDTag = cutlass::layout::RowMajor;
constexpr int AlignmentD = 128 / cutlass::sizeof_bits<ElementD>::value;
constexpr int AlignmentC = AlignmentD;
constexpr int AlignmentB = 32;
using Acc = float;
using ClusterShape = Shape<_1, _1, _1>;

#if defined(VARIANT_SPARSE)
static const char *VARIANT = "sparse";
using OpClass = cutlass::arch::OpClassBlockScaledSparseTensorOp;
using TileShape = Shape<_128, _128, _256>;
using MainSched = cutlass::gemm::KernelSparseTmaWarpSpecializedNvf4Sm120;
constexpr int AlignmentA = 64;
#elif defined(VARIANT_DENSE256)
static const char *VARIANT = "dense256";
using OpClass = cutlass::arch::OpClassBlockScaledTensorOp;
using TileShape = Shape<_128, _128, _256>;
using MainSched = cutlass::gemm::collective::KernelScheduleAuto;
constexpr int AlignmentA = 32;
#else
static const char *VARIANT = "dense128";
using OpClass = cutlass::arch::OpClassBlockScaledTensorOp;
using TileShape = Shape<_128, _128, _128>;
using MainSched = cutlass::gemm::collective::KernelScheduleAuto;
constexpr int AlignmentA = 32;
#endif

using CollectiveEpilogue = typename cutlass::epilogue::collective::CollectiveBuilder<
    cutlass::arch::Sm120, OpClass, TileShape, ClusterShape, cutlass::epilogue::collective::EpilogueTileAuto,
    Acc, Acc, ElementC, LayoutCTag, AlignmentC, ElementD, LayoutDTag, AlignmentD,
    cutlass::epilogue::collective::EpilogueScheduleAuto>::CollectiveOp;
using CollectiveMainloop = typename cutlass::gemm::collective::CollectiveBuilder<
    cutlass::arch::Sm120, OpClass, ElementAB, LayoutATag, AlignmentA, ElementAB, LayoutBTag, AlignmentB, Acc,
    TileShape, ClusterShape,
    cutlass::gemm::collective::StageCountAutoCarveout<static_cast<int>(sizeof(typename CollectiveEpilogue::SharedStorage))>,
    MainSched>::CollectiveOp;
using GemmKernel = cutlass::gemm::kernel::GemmUniversal<Shape<int, int, int, int>, CollectiveMainloop, CollectiveEpilogue, void>;
using Gemm = cutlass::gemm::device::GemmUniversalAdapter<GemmKernel>;

using StrideA = typename Gemm::GemmKernel::StrideA;
using StrideB = typename Gemm::GemmKernel::StrideB;
using StrideC = typename Gemm::GemmKernel::StrideC;
using StrideD = typename Gemm::GemmKernel::StrideD;
using LayoutSFA = typename Gemm::GemmKernel::CollectiveMainloop::LayoutSFA;
using LayoutSFB = typename Gemm::GemmKernel::CollectiveMainloop::LayoutSFB;
using BlkCfg = typename Gemm::GemmKernel::CollectiveMainloop::Sm1xxBlkScaledConfig;
using DataT = typename ElementAB::DataType;
using SfT = typename ElementAB::ScaleFactorType;

static const int HALF[16] = {0, 1, 2, 3, 4, 6, 8, 12, 0, -1, -2, -3, -4, -6, -8, -12};
static double ue4m3(uint8_t b) { int e = (b >> 3) & 0xF, m = b & 7; return e ? std::ldexp(8.0 + m, e - 10) : std::ldexp((double)m, -9); }

struct Ops {
  int M0, N0, K0;
  std::vector<uint8_t> A, SA, B, SB;  // A: A′ codes (dense variants) or ΔA codes (sparse), row-major M0 x K0
  std::vector<float> C;               // the fast A0 part (M0 x N0), or empty
};

static std::vector<uint8_t> slurp(const std::string &p, size_t n) {
  std::vector<uint8_t> v(n);
  std::ifstream f(p, std::ios::binary);
  if (!f.read((char *)v.data(), n)) { fprintf(stderr, "short read %s\n", p.c_str()); exit(2); }
  return v;
}

static Ops load(const std::string &d) {
  Ops o;
  std::ifstream dims(d + "/dims.txt");
  dims >> o.M0 >> o.N0 >> o.K0;
#ifdef VARIANT_SPARSE
  o.A = slurp(d + "/DA.codes", (size_t)o.M0 * o.K0);
#else
  o.A = slurp(d + "/A.codes", (size_t)o.M0 * o.K0);
#endif
  o.SA = slurp(d + "/A.scales", (size_t)o.M0 * o.K0 / 16);
  o.B = slurp(d + "/B.codes", (size_t)o.N0 * o.K0);
  o.SB = slurp(d + "/B.scales", (size_t)o.N0 * o.K0 / 16);
  std::ifstream c(d + "/C.f32", std::ios::binary);
  if (c) { o.C.resize((size_t)o.M0 * o.N0); c.read((char *)o.C.data(), o.C.size() * 4); }
  return o;
}

struct Dev {
  int M, N, K;
  cutlass::device_memory::allocation<uint8_t> A, Ac, E, B, SFA, SFB, C, D;
  StrideA sA; StrideB sB; StrideC sC; StrideD sD;
  LayoutSFA lSFA; LayoutSFB lSFB;
#ifdef VARIANT_SPARSE
  using SparseConfig = typename Gemm::GemmKernel::CollectiveMainloop::SparseConfig;
  using LayoutA = typename Gemm::GemmKernel::CollectiveMainloop::LayoutA;
  using LayoutE = typename Gemm::GemmKernel::CollectiveMainloop::LayoutE;
  LayoutA lA; LayoutE lE;
  double compress_ms = 0;
#endif
};

// operands tiled to M x N x K from the M0 x N0 x K0 sources (rows and k wrap)
static void upload(const Ops &o, Dev &d, int M, int N, int K) {
  d.M = M; d.N = N; d.K = K;
  d.sA = cutlass::make_cute_packed_stride(StrideA{}, {M, K, 1});
  d.sB = cutlass::make_cute_packed_stride(StrideB{}, {N, K, 1});
  d.sC = cutlass::make_cute_packed_stride(StrideC{}, {M, N, 1});
  d.sD = cutlass::make_cute_packed_stride(StrideD{}, {M, N, 1});
  d.lSFA = BlkCfg::tile_atom_to_shape_SFA(make_shape(M, N, K, 1));
  d.lSFB = BlkCfg::tile_atom_to_shape_SFB(make_shape(M, N, K, 1));
  std::vector<uint8_t> a((size_t)M * K / 2), b((size_t)N * K / 2);
  for (size_t m = 0; m < (size_t)M; ++m) {
    const uint8_t *src = &o.A[(m % o.M0) * o.K0];
    for (size_t k = 0; k < (size_t)K; k += 2) a[(m * K + k) / 2] = src[k % o.K0] | (src[(k + 1) % o.K0] << 4);
  }
  for (size_t n = 0; n < (size_t)N; ++n) {
    const uint8_t *src = &o.B[(n % o.N0) * o.K0];
    for (size_t k = 0; k < (size_t)K; k += 2) b[(n * K + k) / 2] = src[k % o.K0] | (src[(k + 1) % o.K0] << 4);
  }
  std::vector<uint8_t> sfa(cute::cosize(d.lSFA), 0), sfb(cute::cosize(d.lSFB), 0);
  int nb0 = o.K0 / 16;
  for (int m = 0; m < M; ++m)
    for (int k = 0; k < K; k += 16) sfa[d.lSFA(m, k, 0)] = o.SA[(size_t)(m % o.M0) * nb0 + (k / 16) % nb0];
  for (int n = 0; n < N; ++n)
    for (int k = 0; k < K; k += 16) sfb[d.lSFB(n, k, 0)] = o.SB[(size_t)(n % o.N0) * nb0 + (k / 16) % nb0];
  d.B.reset(b.size()); d.SFA.reset(sfa.size()); d.SFB.reset(sfb.size());
  CK(cudaMemcpy(d.B.get(), b.data(), b.size(), cudaMemcpyHostToDevice));
  CK(cudaMemcpy(d.SFA.get(), sfa.data(), sfa.size(), cudaMemcpyHostToDevice));
  CK(cudaMemcpy(d.SFB.get(), sfb.data(), sfb.size(), cudaMemcpyHostToDevice));
  size_t words = (size_t)M * N;
  d.C.reset(words * sizeof(ElementC)); d.D.reset(words * sizeof(ElementD));
  std::vector<ElementC> c(words, ElementC(0.f));
  if (!o.C.empty())
    for (size_t m = 0; m < (size_t)M; ++m)
      for (size_t n = 0; n < (size_t)N; ++n) c[m * N + n] = ElementC(o.C[(m % o.M0) * o.N0 + n % o.N0]);
  CK(cudaMemcpy(d.C.get(), c.data(), words * sizeof(ElementC), cudaMemcpyHostToDevice));
  d.A.reset(a.size());
  CK(cudaMemcpy(d.A.get(), a.data(), a.size(), cudaMemcpyHostToDevice));
#ifdef VARIANT_SPARSE
  using CompUtil = cutlass::transform::kernel::StructuredSparseCompressorUtility<Shape<int, int, int, int>, DataT, LayoutATag, typename Dev::SparseConfig>;
  using CompKernel = cutlass::transform::kernel::StructuredSparseCompressor<Shape<int, int, int, int>, DataT, LayoutATag, typename Dev::SparseConfig, cutlass::arch::Sm120>;
  using Comp = cutlass::transform::device::TransformUniversalAdapter<CompKernel>;
  auto workload = make_shape(M, N, K, 1);
  CompUtil util(workload, d.sA);
  size_t na = (size_t)util.get_tensorA_m_physical() * util.get_tensorA_k_physical();
  size_t ne = (size_t)util.get_metadata_m_physical() * util.get_metadata_k_physical();
  d.lA = Dev::SparseConfig::fill_layoutA(workload);
  d.lE = Dev::SparseConfig::fill_layoutE(workload);
  d.Ac.reset((na * cutlass::sizeof_bits<DataT>::value + 7) / 8);
  d.E.reset(ne);
  cutlass::KernelHardwareInfo hw;
  hw.device_id = 0;
  hw.sm_count = cutlass::KernelHardwareInfo::query_device_multiprocessor_count(0);
  typename Comp::Arguments args{{M, N, K, 1}, {(DataT *)d.A.get(), d.sA, (DataT *)d.Ac.get(), (uint8_t *)d.E.get()}, {hw}};
  Comp comp;
  cutlass::device_memory::allocation<uint8_t> ws(Comp::get_workspace_size(args));
  CS(comp.can_implement(args));
  CS(comp.initialize(args, ws.get()));
  CS(comp.run());
  CK(cudaDeviceSynchronize());
  cudaEvent_t e0, e1;
  cudaEventCreate(&e0); cudaEventCreate(&e1);
  cudaEventRecord(e0);
  for (int r = 0; r < 5; ++r) { CS(comp.initialize(args, ws.get())); CS(comp.run()); }
  cudaEventRecord(e1); cudaEventSynchronize(e1);
  float ms; cudaEventElapsedTime(&ms, e0, e1);
  d.compress_ms = ms / 5;
#endif
}

static typename Gemm::Arguments args_of(Dev &d, float beta) {
  typename Gemm::Arguments args{
      cutlass::gemm::GemmUniversalMode::kGemm,
      {d.M, d.N, d.K, 1},
#ifdef VARIANT_SPARSE
      {(DataT *)d.Ac.get(), d.lA, (DataT *)d.B.get(), d.sB, (uint8_t *)d.E.get(), d.lE,
       (SfT *)d.SFA.get(), d.lSFA, (SfT *)d.SFB.get(), d.lSFB},
#else
      {(DataT *)d.A.get(), d.sA, (DataT *)d.B.get(), d.sB, (SfT *)d.SFA.get(), d.lSFA, (SfT *)d.SFB.get(), d.lSFB},
#endif
      {{1.f, beta}, (ElementC *)d.C.get(), d.sC, (ElementD *)d.D.get(), d.sD}};
  return args;
}

struct Runner {
  Gemm gemm;
  cutlass::device_memory::allocation<uint8_t> ws;
  typename Gemm::Arguments args;
  Runner(Dev &d, float beta) : args(args_of(d, beta)) {
    ws.reset(Gemm::get_workspace_size(args));
    CS(gemm.can_implement(args));
    CS(gemm.initialize(args, ws.get()));
  }
  void run() { CS(gemm.run()); }
};

static void poison(Dev &d) { CK(cudaMemset(d.D.get(), 0xA5, (size_t)d.M * d.N * sizeof(ElementD))); CK(cudaDeviceSynchronize()); }

static void dump(Dev &d, const std::string &p) {
  std::vector<uint8_t> h((size_t)d.M * d.N * sizeof(ElementD));
  CK(cudaMemcpy(h.data(), d.D.get(), h.size(), cudaMemcpyDeviceToHost));
  std::ofstream(p, std::ios::binary).write((char *)h.data(), h.size());
}

static double now_ms() { return std::chrono::duration<double, std::milli>(std::chrono::system_clock::now().time_since_epoch()).count(); }

// the exact word (i, j) of the tiled operands, on the host: every product is a dyadic of at most 12 significant bits and
// the operands' exponent span keeps every partial sum inside a double's 53 bits
static double exact_word(const Ops &o, int K, int i, int j, double *abs_sum) {
  int nb0 = o.K0 / 16, i0 = i % o.M0, j0 = j % o.N0;
  double w = 0, aw = 0;
  for (int b = 0; b < K / 16; ++b) {
    int b0 = b % nb0, s = 0, sa = 0;
    for (int t = 0; t < 16; ++t) {
      int p = HALF[o.A[(size_t)i0 * o.K0 + 16 * b0 + t]] * HALF[o.B[(size_t)j0 * o.K0 + 16 * b0 + t]];
      s += p; sa += std::abs(p);
    }
    double sc = 0.25 * ue4m3(o.SA[(size_t)i0 * nb0 + b0]) * ue4m3(o.SB[(size_t)j0 * nb0 + b0]);
    w += s * sc; aw += sa * sc;
  }
  *abs_sum = aw;
  return w;
}

static int verify(const Ops &o, Dev &d, float beta, const char *arm, bool launch) {
  Runner r(d, beta);
  poison(d);
  if (launch) { r.run(); CK(cudaDeviceSynchronize()); }
  std::vector<ElementD> h((size_t)d.M * d.N);
  CK(cudaMemcpy(h.data(), d.D.get(), h.size() * sizeof(ElementD), cudaMemcpyDeviceToHost));
  uint64_t x = 0x9E3779B97F4A7C15ull;
  int exact = 0, close = 0, n = 4096;
  double maxrel = 0, tol = std::ldexp(1.0, sizeof(ElementD) == 4 ? -12 : -7);
  for (int s = 0; s < n; ++s) {
    x = x * 6364136223846793005ull + 1442695040888963407ull;
    int i = (int)((x >> 33) % d.M);
    x = x * 6364136223846793005ull + 1442695040888963407ull;
    int j = (int)((x >> 33) % d.N);
    double aw;
    double w = exact_word(o, d.K, i, j, &aw);
    if (beta != 0.f && !o.C.empty()) {
      double c = (double)o.C[(size_t)(i % o.M0) * o.N0 + j % o.N0];
      w += c; aw += std::fabs(c);
    }
    double want = double(float(ElementD((float)w))), got = double(float(h[(size_t)i * d.N + j]));
    exact += (got == want);
    double rel = std::fabs(got - w) / std::fmax(aw, 1e-30);
    close += (rel <= tol);
    maxrel = std::fmax(maxrel, rel);
  }
  bool ok = close == n;
  printf("{\"mode\":\"verify\",\"variant\":\"%s\",\"out\":\"%s\",\"arm\":\"%s\",\"M\":%d,\"N\":%d,\"K\":%d,\"beta\":%g,"
         "\"launched\":%s,\"sampled\":%d,\"exact\":%d,\"close\":%d,\"max_rel\":%.3g,\"verdict\":\"%s\"}\n",
         VARIANT, OUT, arm, d.M, d.N, d.K, beta, launch ? "true" : "false", n, exact, close, maxrel, ok ? "ACCEPT" : "REJECT");
  fflush(stdout);
  return ok;
}

int main(int argc, char **argv) {
  if (argc < 4) { fprintf(stderr, "usage: check OPS OUT | time OPS M N K ITERS | verify OPS M N K\n"); return 2; }
  std::string mode = argv[1];
  Ops o = load(argv[2]);
  Dev d;
  if (mode == "check") {
    std::string out = argv[3];
    upload(o, d, o.M0, o.N0, o.K0);
    { Runner r(d, 0.f); poison(d); r.run(); CK(cudaDeviceSynchronize()); dump(d, out + "/" + VARIANT + ".D.f32"); }
#ifdef VARIANT_SPARSE
    { Runner r(d, 1.f); poison(d); r.run(); CK(cudaDeviceSynchronize()); dump(d, out + "/" + VARIANT + ".DC.f32"); }
#endif
    poison(d);
    dump(d, out + "/" + VARIANT + ".negctl.f32");
    printf("{\"mode\":\"check\",\"variant\":\"%s\",\"M\":%d,\"N\":%d,\"K\":%d}\n", VARIANT, o.M0, o.N0, o.K0);
    return 0;
  }
  int M = atoi(argv[3]), N = atoi(argv[4]), K = atoi(argv[5]);
  upload(o, d, M, N, K);
  if (mode == "verify") {
    int ok = verify(o, d, 0.f, "gemm", true);
#ifdef VARIANT_SPARSE
    ok &= verify(o, d, 1.f, "gemm+C", true);
#endif
    int neg = verify(o, d, 0.f, "negative-control", false);
    return (ok && !neg) ? 0 : 1;
  }
  int iters = atoi(argv[6]);
  std::vector<float> betas = {0.f};
#ifdef VARIANT_SPARSE
  betas.push_back(1.f);
  printf("{\"mode\":\"compress\",\"variant\":\"%s\",\"M\":%d,\"K\":%d,\"ms\":%.5f}\n", VARIANT, M, K, d.compress_ms);
#endif
  for (float beta : betas) {
    Runner r(d, beta);
    for (int w = 0; w < 5; ++w) r.run();
    CK(cudaDeviceSynchronize());
    cudaEvent_t e0, e1;
    cudaEventCreate(&e0); cudaEventCreate(&e1);
    double t0 = now_ms();
    cudaEventRecord(e0);
    for (int it = 0; it < iters; ++it) r.run();
    cudaEventRecord(e1); cudaEventSynchronize(e1);
    float ms; cudaEventElapsedTime(&ms, e0, e1);
    printf("{\"mode\":\"time\",\"variant\":\"%s\",\"out\":\"%s\",\"M\":%d,\"N\":%d,\"K\":%d,\"beta\":%g,\"iters\":%d,"
           "\"ms\":%.5f,\"t0_unix_ms\":%.0f,\"t1_unix_ms\":%.0f}\n", VARIANT, OUT, M, N, K, beta, iters, ms / iters, t0, now_ms());
    fflush(stdout);
  }
  return 0;
}
