"""flock-glue: patch a pristine flock b684b12 checkout (cwd = repo root) for the host-glue work.

cuda-ghash/challenger.hpp: FsChallenger::grind_pow times itself and can hand the search to a hook (GPU grinding).
cuda-ghash/prove_ffi.cu:
  - flock_cuda_prove_blake3 becomes prove_impl(mode): 0 = BLAKE3 witness kernel (upstream), 1 = host-built witness
    uploaded (flock-bench's flock_cuda_prove_host, the "before" path), 2 = census unit witness built on the device
    from resident operand rows (unit_witness.cuh);
  - n_blocks_log = m - k_log (upstream hard-codes m - 14);
  - the lincheck CSC matrices are cached per matrix (upstream: set once per process, so a unit proof and a BLAKE3
    proof could not share a process);
  - FLOCK_GLUE_PHASES=1: cudaDeviceSynchronize + print at each protocol phase boundary (diagnostic only);
  - FLOCK_GLUE_GPU_GRIND=1: Fiat-Shamir proof-of-work searched on the GPU (upstream pow_grind.cuh kernel, same
    minimal nonce as the host loop) when bits >= FLOCK_GLUE_GRIND_MIN (default 12);
  - extern "C" flock_glue_unit_setup / flock_glue_rows_upload / flock_glue_prove_unit / flock_glue_unit_witness_dump.
Idempotent (skips a file that already carries the marker).
"""
import pathlib
import shutil
import sys

HERE = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")
MARK = "flock-glue"


def sub(s, old, new, count=1):
    assert s.count(old) == count, (old[:80], s.count(old))
    return s.replace(old, new)


# ---------------- challenger.hpp ----------------
p = pathlib.Path("cuda-ghash/challenger.hpp")
s = p.read_text()
if MARK not in s:
    old = """    uint64_t grind_pow(uint32_t bits) {
        uint8_t sd[32]; { Sha256 h = hasher; h.finalize(sd); }   // fs_pow_state_digest
        uint64_t nonce = 0;
        if (bits != 0) { while (!has_leading_zero_bits(sd, nonce, bits)) nonce++; }"""
    new = """    uint64_t grind_pow(uint32_t bits) {
        uint8_t sd[32]; { Sha256 h = hasher; h.finalize(sd); }   // fs_pow_state_digest
        uint64_t nonce = 0;
        auto glue_t0 = std::chrono::steady_clock::now();   // flock-glue: grind accounting + GPU hook
        if (bits != 0 && !(flock_glue_grind_hook && flock_glue_grind_hook(sd, bits, &nonce))) {
            while (!has_leading_zero_bits(sd, nonce, bits)) nonce++;
        }
        flock_glue_grind_secs += std::chrono::duration<double>(std::chrono::steady_clock::now() - glue_t0).count();
        flock_glue_grind_calls += 1;
        flock_glue_grind_bits += bits;"""
    s = sub(s, old, new)
    i = s.index("class FsChallenger")
    s = (s[:i] + "#include <chrono>\n// flock-glue\ninline bool (*flock_glue_grind_hook)(const uint8_t* sd, uint32_t bits, uint64_t* nonce) = nullptr;\n"
         "inline double flock_glue_grind_secs = 0;\ninline long long flock_glue_grind_calls = 0, flock_glue_grind_bits = 0;\n\n" + s[i:])
    p.write_text(s)
    print("patched challenger.hpp")

shutil.copy(HERE / "unit_witness.cuh", "cuda-ghash/unit_witness.cuh")

# ---------------- prove_ffi.cu ----------------
p = pathlib.Path("cuda-ghash/prove_ffi.cu")
s = p.read_text()
if MARK not in s:
    s = sub(s, '#include "blake3_witness.cuh"\n', '#include "blake3_witness.cuh"\n#include "unit_witness.cuh"   // flock-glue\n#include <chrono>\n')
    helpers = r'''
// ---- flock-glue: phase timers, GPU grinding hook, resident unit netlist + operand rows ----
static bool glue_env(const char* k) { const char* v = getenv(k); return v && v[0] && v[0] != '0'; }
static bool g_phases = glue_env("FLOCK_GLUE_PHASES");
static std::chrono::steady_clock::time_point g_ph_t;
static double g_ph_g = 0;
static void glue_phase(const char* name) {
    if (!g_phases) return;
    cudaDeviceSynchronize();
    auto t = std::chrono::steady_clock::now();
    printf("PHASE %-12s %.4f s  (grind %.4f s)\n", name, std::chrono::duration<double>(t - g_ph_t).count(),
           flock_glue_grind_secs - g_ph_g);
    g_ph_t = t; g_ph_g = flock_glue_grind_secs;
}
static bool glue_gpu_grind(const uint8_t* sd, uint32_t bits, uint64_t* nonce) {
    static int min_bits = getenv("FLOCK_GLUE_GRIND_MIN") ? atoi(getenv("FLOCK_GLUE_GRIND_MIN")) : 12;
    if ((int)bits < min_bits || bits > 64) return false;
    static uint8_t* d_sd = nullptr; static unsigned long long* d_best = nullptr;
    static uint8_t* h_sd = nullptr; static unsigned long long* h_best = nullptr;
    if (!d_sd) {
        if (cudaMalloc(&d_sd, 32) || cudaMalloc(&d_best, 8) || cudaMallocHost(&h_sd, 32) || cudaMallocHost(&h_best, 8)) return false;
    }
    memcpy(h_sd, sd, 32);
    if (cudaMemcpyAsync(d_sd, h_sd, 32, cudaMemcpyHostToDevice)) return false;
    const uint64_t chunk = 1ull << (bits + 3 > 20 ? bits + 3 : 20);
    for (uint64_t start = 0;; start += chunk) {
        if (cudaMemsetAsync(d_best, 0xff, 8)) return false;
        search_sha256_proof_of_work_nonce<<<1024, 256>>>(d_sd, start, chunk, bits, d_best);
        if (cudaMemcpy(h_best, d_best, 8, cudaMemcpyDeviceToHost)) return false;
        if (*h_best != ULLONG_MAX) { *nonce = *h_best; return true; }
    }
}
static UnitNetDev g_net{};
static bool g_net_ok = false;
static uint8_t *g_dx = nullptr, *g_dw = nullptr;
static int g_eb = 0, g_nvu = 0, g_upv = 0, g_rowlen = 0;
'''
    s = sub(s, "cudaError_t lig_arena_alloc(void** p, size_t bytes)", helpers + "\ncudaError_t lig_arena_alloc(void** p, size_t bytes)")
    s = sub(s, "int flock_cuda_prove_blake3(const FlockCudaProveParams* P, uint8_t** out, size_t* out_len) {",
            "static int prove_impl(const FlockCudaProveParams* P, uint8_t** out, size_t* out_len, int mode,\n"
            "                      const F128* hz, const F128* ha, const F128* hb, const uint8_t* hzl) {\n"
            "    if (glue_env(\"FLOCK_GLUE_GPU_GRIND\")) flock_glue_grind_hook = glue_gpu_grind;\n"
            "    const double glue_g0 = flock_glue_grind_secs; const long long glue_c0 = flock_glue_grind_calls, glue_b0 = flock_glue_grind_bits;\n"
            "    auto glue_t0 = std::chrono::steady_clock::now(); g_ph_t = glue_t0; g_ph_g = flock_glue_grind_secs;")
    s = sub(s, "    const int n_blocks_log = m - 14;", "    const int n_blocks_log = m - k_log;")
    blk = "    {\n        uint32_t *d_cv, *d_m, *d_blen, *d_flags; b3u64* d_ctr;"
    s = sub(s, blk, """    if (mode == 2) {
        if (!g_net_ok || !g_dx || k_log != UW_K_LOG) { printf("FFI: unit netlist / rows not set (or k_log %d)\\n", k_log); return 106; }
        CK(launch_unit_witness(g_net, g_dx, g_dw, g_eb, g_nvu, g_upv, g_rowlen, n_total,
                               (uw_u64*)df, (uw_u64*)d_a, (uw_u64*)d_b, d_zlin));
    } else if (mode == 1) {
        auto tu0 = std::chrono::steady_clock::now();
        CK(cudaMemcpy(df, hz, len * sizeof(F128), cudaMemcpyHostToDevice));
        CK(cudaMemcpy(d_a, ha, len * sizeof(F128), cudaMemcpyHostToDevice));
        CK(cudaMemcpy(d_b, hb, len * sizeof(F128), cudaMemcpyHostToDevice));
        CK(cudaMemcpy(d_zlin, hzl, (size_t)len * 16, cudaMemcpyHostToDevice));
        CK(cudaDeviceSynchronize());
        printf("FFI: host witness upload %.4f s (%.3f GB)\\n", std::chrono::duration<double>(std::chrono::steady_clock::now() - tu0).count(), 4.0 * (double)len * 16 / 1e9);
    } else {
        uint32_t *d_cv, *d_m, *d_blen, *d_flags; b3u64* d_ctr;""")
    s = sub(s, "    if (P->dump_z_path && P->dump_z_path[0]) {", '    glue_phase("witness");\n    if (P->dump_z_path && P->dump_z_path[0]) {')
    s = sub(s, "    // ================= challenger + statement binding", '    glue_phase("commit");\n    // ================= challenger + statement binding')
    s = sub(s, "    ffi_free(d_a); ffi_free(d_b);\n    // zerocheck proof section", '    glue_phase("zerocheck");\n    ffi_free(d_a); ffi_free(d_b);\n    // zerocheck proof section')
    s = sub(s, "    ffi_free(d_zlin);\n    // lincheck proof section", '    glue_phase("lincheck");\n    ffi_free(d_zlin);\n    // lincheck proof section')
    s = sub(s, "    // ================= ligerito recursion", '    glue_phase("ring-switch");\n    // ================= ligerito recursion')
    s = sub(s, "    *out_len = W.buf.size();", '''    glue_phase("ligerito");
    *out_len = W.buf.size();''')
    s = sub(s, "    CK(device_arena.finish());\n    return 0;\n}", '''    CK(device_arena.finish());
    printf("FFI: mode %d m %d prove %.4f s, grind %.4f s over %lld sites (%lld bits)\\n", mode, m,
           std::chrono::duration<double>(std::chrono::steady_clock::now() - glue_t0).count(),
           flock_glue_grind_secs - glue_g0, flock_glue_grind_calls - glue_c0, flock_glue_grind_bits - glue_b0);
    return 0;
}''')
    # per-matrix CSC cache instead of once-per-process
    i0 = s.index("        static std::once_flag matrix_setup_once;")
    i1 = s.index("            return 104;\n        }\n", i0) + len("            return 104;\n        }\n")
    s = s[:i0] + """        struct GlueMat { uint32_t *acp, *ar, *bcp, *br; };
        static std::map<const uint32_t*, GlueMat> glue_mats;   // flock-glue: one entry per circuit
        auto gm = glue_mats.find(P->a_col_ptr);
        if (gm == glue_mats.end()) {
            GlueMat g{};
            CK(cudaMalloc(&g.acp, (K + 1) * sizeof(uint32_t)));
            CK(cudaMalloc(&g.ar, (P->a_nnz ? P->a_nnz : 1) * sizeof(uint32_t)));
            CK(cudaMalloc(&g.bcp, (K + 1) * sizeof(uint32_t)));
            CK(cudaMalloc(&g.br, (P->b_nnz ? P->b_nnz : 1) * sizeof(uint32_t)));
            CK(cudaMemcpy(g.acp, P->a_col_ptr, (K + 1) * sizeof(uint32_t), cudaMemcpyHostToDevice));
            if (P->a_nnz) CK(cudaMemcpy(g.ar, P->a_rows, P->a_nnz * sizeof(uint32_t), cudaMemcpyHostToDevice));
            CK(cudaMemcpy(g.bcp, P->b_col_ptr, (K + 1) * sizeof(uint32_t), cudaMemcpyHostToDevice));
            if (P->b_nnz) CK(cudaMemcpy(g.br, P->b_rows, P->b_nnz * sizeof(uint32_t), cudaMemcpyHostToDevice));
            gm = glue_mats.emplace(P->a_col_ptr, g).first;
        }
        uint32_t *d_acp = gm->second.acp, *d_ar = gm->second.ar, *d_bcp = gm->second.bcp, *d_br = gm->second.br;
""" + s[i1:]
    api = r'''
int flock_cuda_prove_blake3(const FlockCudaProveParams* P, uint8_t** out, size_t* out_len) {
    return prove_impl(P, out, out_len, 0, nullptr, nullptr, nullptr, nullptr);
}
int flock_cuda_prove_host(const FlockCudaProveParams* P, const F128* z, const F128* a, const F128* b,
                          const uint8_t* zl, uint8_t** out, size_t* out_len) {
    return prove_impl(P, out, out_len, 1, z, a, b, zl);
}
int flock_glue_prove_unit(const FlockCudaProveParams* P, uint8_t** out, size_t* out_len) {
    return prove_impl(P, out, out_len, 2, nullptr, nullptr, nullptr, nullptr);
}
// hdr = useful, const_pos, n_in, n_x, n_w, n_c, k, bits, depth
int flock_glue_unit_setup(const int* hdr, const int* lvl_off, const int* lvl_rows, int n_lvl_rows,
                          const int* a_off, const uint16_t* a_col, int a_nnz,
                          const int* b_off, const uint16_t* b_col, int b_nnz, const int* cout) {
    UnitNetDev N{};
    N.useful = hdr[0]; N.const_pos = hdr[1]; N.n_in = hdr[2]; N.n_x = hdr[3]; N.n_w = hdr[4]; N.n_c = hdr[5];
    N.k = hdr[6]; N.bits = hdr[7]; N.depth = hdr[8];
    if (N.useful > UW_K || N.n_c != 32) return 107;
    int *d_lo, *d_lr, *d_ao, *d_bo; uint16_t *d_ac, *d_bc;
    CK(cudaMalloc(&d_lo, (N.depth + 1) * sizeof(int))); CK(cudaMalloc(&d_lr, (n_lvl_rows ? n_lvl_rows : 1) * sizeof(int)));
    CK(cudaMalloc(&d_ao, (N.useful + 1) * sizeof(int))); CK(cudaMalloc(&d_bo, (N.useful + 1) * sizeof(int)));
    CK(cudaMalloc(&d_ac, (a_nnz ? a_nnz : 1) * 2)); CK(cudaMalloc(&d_bc, (b_nnz ? b_nnz : 1) * 2));
    CK(cudaMemcpy(d_lo, lvl_off, (N.depth + 1) * sizeof(int), cudaMemcpyHostToDevice));
    CK(cudaMemcpy(d_lr, lvl_rows, n_lvl_rows * sizeof(int), cudaMemcpyHostToDevice));
    CK(cudaMemcpy(d_ao, a_off, (N.useful + 1) * sizeof(int), cudaMemcpyHostToDevice));
    CK(cudaMemcpy(d_bo, b_off, (N.useful + 1) * sizeof(int), cudaMemcpyHostToDevice));
    CK(cudaMemcpy(d_ac, a_col, a_nnz * 2, cudaMemcpyHostToDevice));
    CK(cudaMemcpy(d_bc, b_col, b_nnz * 2, cudaMemcpyHostToDevice));
    N.lvl_off = d_lo; N.lvl_rows = d_lr; N.a_off = d_ao; N.a_col = d_ac; N.b_off = d_bo; N.b_col = d_bc;
    for (int i = 0; i < 32; i++) N.cout[i] = cout[i];
    g_net = N; g_net_ok = true;
    return 0;
}
// The instance operands (x rows, W columns) as they would sit on the device after the matmul: uploaded once.
int flock_glue_rows_upload(const uint8_t* x, const uint8_t* w, int elem_bytes, int n_vu, int units_per_vu, int row_len) {
    if (g_dx) { CK(cudaFree(g_dx)); CK(cudaFree(g_dw)); g_dx = g_dw = nullptr; }
    size_t bytes = (size_t)n_vu * row_len * elem_bytes;
    CK(cudaMalloc(&g_dx, bytes)); CK(cudaMalloc(&g_dw, bytes));
    CK(cudaMemcpy(g_dx, x, bytes, cudaMemcpyHostToDevice)); CK(cudaMemcpy(g_dw, w, bytes, cudaMemcpyHostToDevice));
    g_eb = elem_bytes; g_nvu = n_vu; g_upv = units_per_vu; g_rowlen = row_len;
    return 0;
}
// Device witness only (timed, synchronized), copied back for the host cross-check. Host buffers may be NULL.
int flock_glue_unit_witness_dump(int m, int k_log, F128* hz, F128* ha, F128* hb, uint8_t* hzl, double* secs) {
    if (!g_net_ok || !g_dx || k_log != UW_K_LOG) return 106;
    long long len = 1LL << (m - 7), n_total = 1LL << (m - k_log);
    F128 *df, *da, *db; uint8_t* dzl;
    CK(cudaMalloc(&df, len * 16)); CK(cudaMalloc(&da, len * 16)); CK(cudaMalloc(&db, len * 16)); CK(cudaMalloc(&dzl, len * 16));
    CK(launch_unit_witness(g_net, g_dx, g_dw, g_eb, g_nvu, g_upv, g_rowlen, n_total, (uw_u64*)df, (uw_u64*)da, (uw_u64*)db, dzl));
    CK(cudaDeviceSynchronize());
    auto t0 = std::chrono::steady_clock::now();
    CK(launch_unit_witness(g_net, g_dx, g_dw, g_eb, g_nvu, g_upv, g_rowlen, n_total, (uw_u64*)df, (uw_u64*)da, (uw_u64*)db, dzl));
    CK(cudaDeviceSynchronize());
    *secs = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
    if (hz) { CK(cudaMemcpy(hz, df, len * 16, cudaMemcpyDeviceToHost)); CK(cudaMemcpy(ha, da, len * 16, cudaMemcpyDeviceToHost));
              CK(cudaMemcpy(hb, db, len * 16, cudaMemcpyDeviceToHost)); CK(cudaMemcpy(hzl, dzl, len * 16, cudaMemcpyDeviceToHost)); }
    CK(cudaFree(df)); CK(cudaFree(da)); CK(cudaFree(db)); CK(cudaFree(dzl));
    return 0;
}
'''
    s = sub(s, '} // extern "C"', api + '} // extern "C"')
    s = "// flock-glue patched (see lanes/flock-glue/evidence/pod-scripts/patch_ffi.py)\n" + s
    p.write_text(s)
    print("patched prove_ffi.cu")
