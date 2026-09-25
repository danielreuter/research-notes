// flock-glue: on-device witness for the binary-census transition unit (flock-bench's export_unit.py netlist,
// C = I, k_log = 13), derived from instance operands already resident on the device.
//
// Instance operands: x rows and W columns, n_vu rows of row_len elements (BF16 = 2 bytes, FP8 = 1 byte);
// unit u of VU v reads elements [u*k, (u+1)*k) of x row v and W column v; c_in(0) = +0 and c_in(u+1) =
// c_out(u) (the chain is evaluated here, not proved: chain glue is not in the Flock statement).
//
// One CTA per 32 VUs, bit-sliced (bit l of every shared word = VU 32*cta + l), walking its 32 chains unit by
// unit: operands -> input wires by warp ballot; AND / assertion / copy rows in level order, the netlist streamed
// through shared memory in batches (a batch = consecutive level segments whose column lists fit the buffer; a
// __syncthreads after each segment), so no gate waits on an L2 round trip; then (z, a, b) per row transposed to
// Flock's block-major RowMajor layout (block = u*n_vu + v, 128 u64 per block) by ballot. The gates' a / b words go
// through a per-CTA global scratch. Semantics match verity_unit.rs::Netlist::eval8: rows in order, a row's own
// column reads 0 (assertion rows), inputs and the constant row have a = b = z. Extra CTAs write the zero-input
// unit into the padding blocks [n_vu*units, n_total).
#pragma once
#include <cstdint>

typedef unsigned long long uw_u64;

#define UW_K_LOG 13
#define UW_K (1 << UW_K_LOG)
#define UW_WORDS (UW_K / 64)
#define UW_THREADS 256
#define UW_WARPS (UW_THREADS / 32)
#define UW_WIDE 64            // segments at least this wide: one thread per row; narrower: one warp per row
#define UW_COLS_CAP 12288     // u16 column terms per batch
#define UW_DESC_CAP 1024      // gates per batch
#define UW_MAX_SEGS 1024
#define UW_MAX_BATCHES 256

__device__ unsigned long long uw_prof[8];   // cycles in CTA 0: input, copy, narrow, wide, output; [5] narrow segs, [6] wide segs
#define UW_PROF(slot) do { if (prof) { long long _t = clock64(); uw_prof[slot] += _t - prof_t; prof_t = _t; } } while (0)

struct UnitNetDev {
    int useful, const_pos, n_in, n_x, n_w, n_c;
    int k, bits;              // operand elements per unit (per side), bits per element
    int n_gates, n_segs, n_batches;
    const uint32_t* gdesc;    // [n_gates] row | a_len << 16, level order
    const uint32_t* gstart;   // [n_gates + 1] first column term (A terms then B terms), own column removed
    const uint16_t* cols;
    const int* seg_end;       // [n_segs] gate end of each segment (a segment = one level or part of one)
    const int* batch_seg;     // [n_batches + 1] segment ranges
    int cout[32];
};

struct UwSmem {
    uint32_t zs[UW_K];
    uint16_t cols[UW_COLS_CAP + 4];
    uint32_t desc[UW_DESC_CAP];
    uint32_t start[UW_DESC_CAP + 1];
    int seg_end[UW_MAX_SEGS];
    int batch_seg[UW_MAX_BATCHES + 1];
    uint32_t cbuf[32];
};

__device__ __forceinline__ uint32_t uw_xor_thread(const uint32_t* zs, const uint16_t* c, int s, int e) {
    uint32_t x = 0;
    for (int i = s; i < e; i++) x ^= zs[c[i]];
    return x;
}

__device__ __forceinline__ uint32_t uw_xor_warp(const uint32_t* zs, const uint16_t* c, int s, int e, int lane) {
    uint32_t x = 0;
    for (int i = s + lane; i < e; i += 32) x ^= zs[c[i]];
    return __reduce_xor_sync(0xffffffffu, x);
}

__global__ void __launch_bounds__(UW_THREADS)
unit_witness_chain(UnitNetDev N, const uint8_t* __restrict__ x_rows, const uint8_t* __restrict__ w_cols,
                   int elem_bytes, int n_vu, int units_per_vu, int row_len, long long n_total,
                   uw_u64* __restrict__ z, uw_u64* __restrict__ a, uw_u64* __restrict__ b,
                   uint32_t* __restrict__ scratch) {
    extern __shared__ __align__(16) unsigned char uw_raw[];
    UwSmem& S = *reinterpret_cast<UwSmem*>(uw_raw);
    uint32_t* zs = S.zs;
    const int tid = threadIdx.x, lane = tid & 31, warp = tid >> 5;
    const int n_vu_ctas = (n_vu + 31) / 32;
    const bool pad = (int)blockIdx.x >= n_vu_ctas;
    const long long n_units = (long long)n_vu * units_per_vu;
    const long long n_padblk = n_total - n_units;
    const int n_pad_ctas = (int)gridDim.x - n_vu_ctas;
    long long pad_lo = 0, pad_hi = 0;
    if (pad) {
        long long per = (n_padblk + n_pad_ctas - 1) / n_pad_ctas;
        pad_lo = n_units + per * ((int)blockIdx.x - n_vu_ctas);
        pad_hi = pad_lo + per < n_total ? pad_lo + per : n_total;
    }
    uint32_t* scr_a = scratch + (size_t)blockIdx.x * 2 * UW_K;
    uint32_t* scr_b = scr_a + UW_K;
    const int U = pad ? 1 : units_per_vu;
    const bool prof = blockIdx.x == 0 && tid == 0;
    long long prof_t = clock64();
    const int v = (int)blockIdx.x * 32 + lane;
    const bool vv = !pad && v < n_vu;
    for (int i = tid; i < UW_K; i += UW_THREADS) zs[i] = 0;
    for (int i = tid; i < N.n_segs; i += UW_THREADS) S.seg_end[i] = N.seg_end[i];
    for (int i = tid; i <= N.n_batches; i += UW_THREADS) S.batch_seg[i] = N.batch_seg[i];
    if (tid < 32) S.cbuf[tid] = 0;
    __syncthreads();
    for (int u = 0; u < U; u++) {
        if (!pad) {
            for (int e = warp; e < 2 * N.k; e += UW_WARPS) {
                const int side = e >= N.k, ei = e - side * N.k;
                const uint8_t* src = side ? w_cols : x_rows;
                uint32_t val = 0;
                if (vv) {
                    long long idx = (long long)v * row_len + (long long)u * N.k + ei;
                    val = elem_bytes == 2 ? ((const uint16_t*)src)[idx] : src[idx];
                }
                const int base = side * N.n_x + ei * N.bits;
                for (int t = 0; t < N.bits; t++) {
                    uint32_t word = __ballot_sync(0xffffffffu, (val >> t) & 1);
                    if (lane == 0) zs[base + t] = word;
                }
            }
            if (tid < 32) zs[N.n_x + N.n_w + tid] = S.cbuf[tid];
        }
        if (tid == 0) zs[N.const_pos] = 0xffffffffu;
        __syncthreads();
        UW_PROF(0);
        for (int bt = 0; bt < N.n_batches; bt++) {
            const int s_lo = S.batch_seg[bt], s_hi = S.batch_seg[bt + 1];
            const int g0 = s_lo ? S.seg_end[s_lo - 1] : 0, g1 = S.seg_end[s_hi - 1];
            const uint32_t c0 = __ldg(N.gstart + g0) & ~1u, c1 = __ldg(N.gstart + g1);
            const uint32_t* src32 = reinterpret_cast<const uint32_t*>(N.cols) + c0 / 2;
            uint32_t* dst32 = reinterpret_cast<uint32_t*>(S.cols);
            for (int i = tid; i < (int)((c1 - c0 + 1) / 2); i += UW_THREADS) dst32[i] = __ldg(src32 + i);
            for (int i = tid; i < g1 - g0; i += UW_THREADS) S.desc[i] = __ldg(N.gdesc + g0 + i);
            for (int i = tid; i <= g1 - g0; i += UW_THREADS) S.start[i] = __ldg(N.gstart + g0 + i) - c0;
            __syncthreads();
            UW_PROF(1);
            for (int sg = s_lo; sg < s_hi; sg++) {
                const int e0 = (sg ? S.seg_end[sg - 1] : 0) - g0, e1 = S.seg_end[sg] - g0;
                if (e1 - e0 >= UW_WIDE) {
                    for (int i = e0 + tid; i < e1; i += UW_THREADS) {
                        const uint32_t d = S.desc[i];
                        const int r = d & 0xffff, st = S.start[i], mid = st + (d >> 16), en = S.start[i + 1];
                        const uint32_t av = uw_xor_thread(zs, S.cols, st, mid), bv = uw_xor_thread(zs, S.cols, mid, en);
                        zs[r] = av & bv; scr_a[r] = av; scr_b[r] = bv;
                    }
                } else {
                    for (int i = e0 + warp; i < e1; i += UW_WARPS) {
                        const uint32_t d = S.desc[i];
                        const int r = d & 0xffff, st = S.start[i], mid = st + (d >> 16), en = S.start[i + 1];
                        const uint32_t av = uw_xor_warp(zs, S.cols, st, mid, lane), bv = uw_xor_warp(zs, S.cols, mid, en, lane);
                        if (lane == 0) { zs[r] = av & bv; scr_a[r] = av; scr_b[r] = bv; }
                    }
                }
                __syncthreads();
                if (prof) uw_prof[(e1 - e0 >= UW_WIDE) ? 6 : 5] += 1;
                UW_PROF((e1 - e0 >= UW_WIDE) ? 3 : 2);
            }
        }
        for (int c = warp; c < UW_WORDS; c += UW_WARPS) {
            uint32_t zw[2], aw[2], bw[2];
#pragma unroll
            for (int h = 0; h < 2; h++) {
                const int r = c * 64 + h * 32 + lane;
                uint32_t zz = 0, aa = 0, bb = 0;
                if (r < N.useful) {
                    zz = zs[r];
                    if (r < N.n_in || r == N.const_pos) { aa = zz; bb = zz; }
                    else { aa = scr_a[r]; bb = scr_b[r]; }
                }
                zw[h] = zz; aw[h] = aa; bw[h] = bb;
            }
            uw_u64 Z = 0, A = 0, B = 0;
            if (!pad) {
#pragma unroll 4
                for (int l = 0; l < 32; l++) {
                    uint32_t z0 = __ballot_sync(0xffffffffu, (zw[0] >> l) & 1), z1 = __ballot_sync(0xffffffffu, (zw[1] >> l) & 1);
                    uint32_t a0 = __ballot_sync(0xffffffffu, (aw[0] >> l) & 1), a1 = __ballot_sync(0xffffffffu, (aw[1] >> l) & 1);
                    uint32_t b0 = __ballot_sync(0xffffffffu, (bw[0] >> l) & 1), b1 = __ballot_sync(0xffffffffu, (bw[1] >> l) & 1);
                    if (lane == l) {
                        Z = z0 | ((uw_u64)z1 << 32); A = a0 | ((uw_u64)a1 << 32); B = b0 | ((uw_u64)b1 << 32);
                    }
                }
                if (vv) {
                    const long long blk = (long long)u * n_vu + v;
                    z[blk * UW_WORDS + c] = Z; a[blk * UW_WORDS + c] = A; b[blk * UW_WORDS + c] = B;
                }
            } else {
                // every lane holds the same zero-input instance: bit 0 of each word
                uint32_t z0 = __ballot_sync(0xffffffffu, zw[0] & 1), z1 = __ballot_sync(0xffffffffu, zw[1] & 1);
                uint32_t a0 = __ballot_sync(0xffffffffu, aw[0] & 1), a1 = __ballot_sync(0xffffffffu, aw[1] & 1);
                uint32_t b0 = __ballot_sync(0xffffffffu, bw[0] & 1), b1 = __ballot_sync(0xffffffffu, bw[1] & 1);
                Z = z0 | ((uw_u64)z1 << 32); A = a0 | ((uw_u64)a1 << 32); B = b0 | ((uw_u64)b1 << 32);
                for (long long blk = pad_lo + lane; blk < pad_hi; blk += 32) {
                    z[blk * UW_WORDS + c] = Z; a[blk * UW_WORDS + c] = A; b[blk * UW_WORDS + c] = B;
                }
            }
        }
        __syncthreads();
        UW_PROF(4);
        if (tid < 32) S.cbuf[tid] = zs[N.cout[tid]];
        __syncthreads();
    }
}

// Lincheck stripe for k_log = 13: byte (group g, bit i) = bit i of blocks 8g..8g+7 (blake3_lincheck_transpose, K = 8192).
__global__ void unit_lincheck_transpose(const uw_u64* __restrict__ z, long long n_total, uint8_t* __restrict__ z_lincheck) {
    long long total = (n_total / 8) * (long long)UW_WORDS;
    long long stride = (long long)gridDim.x * blockDim.x;
    for (long long tid = (long long)blockIdx.x * blockDim.x + threadIdx.x; tid < total; tid += stride) {
        long long g = tid / UW_WORDS;
        int i = (int)(tid - g * UW_WORDS);
        uw_u64 lanes[8];
#pragma unroll
        for (int ln = 0; ln < 8; ln++) lanes[ln] = z[(8 * g + ln) * (long long)UW_WORDS + i];
        uw_u64* dst = (uw_u64*)(z_lincheck + g * (long long)UW_K + (long long)i * 64);
#pragma unroll
        for (int b_chunk = 0; b_chunk < 8; b_chunk++) {
            uw_u64 src = 0;
#pragma unroll
            for (int r = 0; r < 8; r++) src |= ((lanes[r] >> (8 * b_chunk)) & 0xFFull) << (8 * r);
            dst[b_chunk] = b3_transpose8(src);
        }
    }
}

inline int unit_witness_pad_ctas(long long n_units, long long n_total) {
    long long pad = n_total - n_units;
    if (pad <= 0) return 0;
    long long c = (pad + 2047) / 2048;
    return (int)(c < 128 ? c : 128);
}

inline cudaError_t launch_unit_witness(const UnitNetDev& N, const uint8_t* x_rows, const uint8_t* w_cols, int elem_bytes,
                                       int n_vu, int units_per_vu, int row_len, long long n_total,
                                       uw_u64* z, uw_u64* a, uw_u64* b, uint8_t* z_lincheck, cudaStream_t st = 0) {
    static bool attr = false;
    static uint32_t* scratch = nullptr;
    static size_t scratch_ctas = 0;
    if (!attr) {
        cudaError_t e = cudaFuncSetAttribute(unit_witness_chain, cudaFuncAttributeMaxDynamicSharedMemorySize, (int)sizeof(UwSmem));
        if (e != cudaSuccess) return e;
        attr = true;
    }
    long long n_units = (long long)n_vu * units_per_vu;
    if (n_units > n_total || N.n_segs > UW_MAX_SEGS || N.n_batches > UW_MAX_BATCHES) return cudaErrorInvalidValue;
    int ctas = (n_vu + 31) / 32 + unit_witness_pad_ctas(n_units, n_total);
    if ((size_t)ctas > scratch_ctas) {
        if (scratch) { cudaError_t e = cudaFree(scratch); if (e != cudaSuccess) return e; }
        cudaError_t e = cudaMalloc(&scratch, (size_t)ctas * 2 * UW_K * sizeof(uint32_t));
        if (e != cudaSuccess) return e;
        scratch_ctas = ctas;
    }
    unit_witness_chain<<<ctas, UW_THREADS, sizeof(UwSmem), st>>>(N, x_rows, w_cols, elem_bytes, n_vu, units_per_vu, row_len,
                                                                n_total, z, a, b, scratch);
    cudaError_t e = cudaGetLastError();
    if (e != cudaSuccess) return e;
    long long total = (n_total / 8) * (long long)UW_WORDS;
    unit_lincheck_transpose<<<(unsigned)((total + 255) / 256), 256, 0, st>>>(z, n_total, z_lincheck);
    return cudaGetLastError();
}
