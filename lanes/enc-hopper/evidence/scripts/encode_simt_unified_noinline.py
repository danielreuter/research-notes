"""The prover's Reed-Solomon encoder on SIMT cores: BabyBear int32 Montgomery butterflies, radix-4 fused shared-memory
stages, one CUDA block per row (the measured ``backends/direct/encode/encode_ntt_simt.py`` v2/radix4 kernel of the
b-encode / b-v2 lanes, 32.2 ms per 310,602 x 4096 rows on the 4090), specialised to THIS protocol's code:

* evaluation domain the coset ``g <w_n>`` (``g = 31``, disjoint from ``H = <w_l>``; PROTOCOL.md 3 / 8b, red-team F4),
  **not** the systematic ``<w_n>`` of the shared kernel: the four coset tables are ``l^-1 (g w_n^c)^i``, ``c < 4``;
* output in the protocol's natural order (position ``i`` holds ``p(g w_n^i)``): coset ``c``, index ``j`` is written to
  position ``4 j + c`` (the shared kernel writes coset blocks) -- bit-exact with ``field.encode`` / ``eval_on_coset``;
* ZK (8b): row ``j`` is committed as ``interp_H(W_j) + Z_H s_j`` with ``deg s_j < t_pad``.  On coset ``c`` the factor
  ``Z_H(x) = x^l - 1 = g^l w_n^{c l} - 1 =: z_c`` is a CONSTANT (``w_l^{j l} = 1``), so the mask enters as
  ``z_c s_j(x)``: the kernel adds ``s_{j,i} z_c (g w_n^c)^i`` to the (bit-reversed) coefficient ``i < t_pad`` before each
  coset NTT -- 256 multiply-adds per coset per row, no second NTT, no length-``l + 256`` transform;
* optionally the natural-order coefficients ``interp_H(W_j)`` (``l^-1`` x the DIF output, bit-reversal undone on the
  store), which the ZK prover needs for the coefficient-form messages ``w`` and ``v``.

Montgomery arithmetic (``R = 2^32``) is the shared kernel's; ``K`` here is ``l`` (a power of two, ``256 <= l <=
16384``), ``n = 4 l``, ``THREADS = l / 16``.  Lane enc-hopper (H100 tuning, bit-exact with the previous kernel; v3):

* every thread owns 16 elements in every phase, so each transform is 4 radix-16 register stages (``m = K/2 ..
  THREADS``, elements ``t + THREADS s``) + three shared-memory passes of 4 stages each (stride 256, stride 16, 16
  contiguous) -- 3 shared-memory round trips per transform instead of 5, and no separate scale / copy passes: the last
  INTT pass writes the (bit-reversed, unscaled) coefficients ``cf``, each coset's first pass reads, scales and masks them;
* the shared-memory layout is XOR-swizzled (``SWZ``) so that all three pass patterns and the bit-reversed coefficient
  gather are bank-conflict-free, with 16-byte vector accesses in the contiguous pass;
* branch-free ``min``-trick reductions; twiddles from the read-only tables via ``__ldg``; ``__launch_bounds__`` caps the
  registers at 64 (one 1024-thread CTA per SM at ``l = 16384``, two 512-thread CTAs at ``l = 8192``);
* the natural-order store (position ``4 j + c``) would be 4 bytes per lane at a 16-byte stride (16 sectors x 8 bytes
  per warp store, ~0.45 ms of 1.95 ms per 3328 x 16384 rows on the H100).  ``STAGE`` (sm_80+, default): cosets 0-2 are
  parked coset-major in a per-CTA staging buffer that stays in L2 (``evict_last``; the grid is exactly the resident
  CTAs, 25 MB at l = 16384), and the coset-3 pass reads them back and writes each position's four values as one
  16-byte store (``evict_first``): every sector written once, complete.  1.99 -> 1.77 ms (the coset-major layout runs
  at 1.58); ``stage=False`` keeps the 4-byte stores with ``evict_last`` partial lines.

Grid-stride over the rows (``blocks`` = the resident CTAs with ``STAGE``, ``4 x SMs`` otherwise).  Shared memory is
dynamic (``2 l`` words: ``x``, ``cf``).  H100, 3328 rows x l = 16384: 4.55 ms (shared kernel) -> 1.77 ms plain /
1.90 ms ZK + coefficients (0.49 TB/s of codeword).
Tested bit-exact against ``field.encode`` and ``eval_on_coset`` (``encode_simt_test``); the verifier keeps the torch
encoder on its ``D`` rows.  ``encode(..., stream=)`` launches on that torch stream (hp2-host's pipelining).
"""
from __future__ import annotations

import numpy as np
import torch

from .field import GEN, P, root_of_unity

__all__ = ["LigeroEncoderSIMT", "available", "encoder_for"]

_R_MOD_P = pow(2, 32, P)
_P_INV_MOD_R = pow(P, -1, 2**32)

_SRC = r"""
#define P 2013265921u
#define PINV %(pinv)du        /* p^{-1} mod 2^32 */
#define K %(k)d
#define LOGK %(logk)d
#define THREADS %(threads)d
#define LOGT %(logt)d          /* K = 16 THREADS: 16 elements per thread in every phase */
#define TP %(tp)d              /* mask coefficients per row (0: no mask) */
#define KINV_MONT %(kinv_mont)du
#define K_MONT %(k_mont)du     /* l R mod p */
/* rows >= rows_eval come as int64 coefficient vectors c[0 .. K + TP) (the ZK mask rows) instead of evaluations on
   H: cf <- l c (no INTT), the high part enters like the mask with x^l = z_c + 1 (mask_tw1).  One launch encodes the
   witness rows and the mask rows (the latter ride in the grid-stride tail) */
#define CF_GLOBAL %(cf_global)d /* 1: the coefficient buffer cf lives in a per-CTA global scratch (L2) instead of shared memory --
                                  for parts whose shared memory per block is < 2 l words (l = 16384 on Ada / consumer Blackwell) */
#define STAGE %(stage)d        /* 1: cosets 0-2 are parked coset-major in a per-CTA L2-resident staging buffer (full sectors,
                                  evict_last); coset 3 reads them back and writes every position's 4 cosets as one 16-byte
                                  store (full sectors, evict_first) -- instead of 4-byte stores at a 16-byte stride */

/* [0, p) in, [0, p) out; the wrapped-difference min selects the reduced value (2 instructions, no predicate) */
__device__ __forceinline__ unsigned add_p(unsigned a, unsigned b) { unsigned s = a + b; return min(s, s - P); }
__device__ __forceinline__ unsigned sub_p(unsigned a, unsigned b) { unsigned d = a - b; return min(d, d + P); }
/* a in [0,p), w = w' R mod p (Montgomery): a w' mod p.  x = a w < p 2^32; t = x p^{-1} mod 2^32; (x - t p) / 2^32 =
   hi(x) - hi(t p) in (-p, p): min(r, r + p) picks the representative in [0, p). */
__device__ __forceinline__ unsigned mont_mul(unsigned a, unsigned w) {
    unsigned long long x = (unsigned long long)a * w;
    unsigned lo = (unsigned)x, hi = (unsigned)(x >> 32);
    unsigned t = lo * PINV;
    unsigned u = __umulhi(t, P);
    unsigned r = hi - u;
    return min(r, r + P);
}

/* Shared-memory bank swizzle: word a lives at SWZ(a).  Bits 0-1 are kept (16-byte vectors stay whole and aligned),
   bits 2-4 (the bank group) are XORed with bits 5-7, 8 and 9-11, so that every access pattern of the kernel is
   conflict-free: 16 contiguous words per thread as four uint4 (pass A: a quarter-warp's chunks land in 8 distinct
   bank groups), stride-16 words across 256-blocks (pass B: the two half-warps flip bit 4), lane-consecutive words
   (pass C, the register phases: a constant XOR inside a 32-word window), and the bit-reversed coefficient gather
   (lanes differ in bits 0-1 and 9-11).  Both buffers (x and cf) use it. */
__device__ __forceinline__ int SWZ(int a) {
    return a ^ (((((a >> 5) ^ (a >> 9)) & 7) ^ (((a >> 8) & 1) << 2)) << 2);
}
/* SWZ is XOR-linear (a ^ L(a), L linear over GF(2)): SWZ(base | off) = SWZ(base) ^ SWZ(off) when base and off have
   disjoint bits -- the per-thread SWZ(base) is computed once, the per-element SWZ(off) is a compile-time constant. */

/* twiddle load ptxas cannot hoist out of the row loop (inlined, it kept ~70 row-invariant twiddles in registers and
   spilled 250 B at the 64-register cap of a 1024-thread CTA; the tables are L1/L2-resident anyway) */
__device__ __forceinline__ unsigned ldtw(const unsigned* p) {
    unsigned v;
    asm volatile("ld.global.nc.u32 %%0, [%%1];" : "=r"(v) : "l"(p));
    return v;
}

/* One radix-2 stage m = 2^SM on the 2^R register elements e[k] of a group whose element k sits at index
   base + (k << S0) (S0 <= SM < S0 + R); tt = index & (m - 1) is the twiddle position.  DIF (inverse, tw_inv):
   (a, c) -> (a + c, (a - c) w); DIT (forward, tw_fwd): (a, c) -> (a + c w, a - c w).  Same butterflies and twiddles
   as main's kernel, only regrouped -- the field values are canonical, so the output is bit-identical. */
template <int R, int S0, int SM, bool DIF>
__device__ __forceinline__ void stage(unsigned* e, int base, const unsigned* __restrict__ tw) {
    constexpr int m = 1 << SM, step = 1 << (SM - S0);
    #pragma unroll
    for (int k = 0; k < (1 << R); ++k) {
        if (!(k & step)) {
            const int idx = base + (k << S0);
            const unsigned w = ldtw(&tw[m + (idx & (m - 1))]);
            if (DIF) { const unsigned a = e[k], c = e[k + step]; e[k] = add_p(a, c); e[k + step] = mont_mul(sub_p(a, c), w); }
            else     { const unsigned a = e[k], c = mont_mul(e[k + step], w); e[k] = add_p(a, c); e[k + step] = sub_p(a, c); }
        }
    }
}
/* all R stages of a group: DIF from the top stage down, DIT from the bottom stage up */
template <int R, int S0, int SM, bool DIF>
__device__ __forceinline__ void stages_dif(unsigned* e, int base, const unsigned* __restrict__ tw) {
    if constexpr (SM >= S0) { stage<R, S0, SM, true>(e, base, tw); stages_dif<R, S0, SM - 1, true>(e, base, tw); }
}
template <int R, int S0, int SM, bool DIF>
__device__ __forceinline__ void stages_dit(unsigned* e, int base, const unsigned* __restrict__ tw) {
    if constexpr (SM < S0 + R) { stage<R, S0, SM, false>(e, base, tw); stages_dit<R, S0, SM + 1, false>(e, base, tw); }
}

/* group base for the g-th group of this thread in a pass over stages [S0, S0 + R): the group index q enumerates the
   K / 2^R groups; its bits [S0, S0 + R) are the in-group element index */
template <int R, int S0>
__device__ __forceinline__ int group_base(int q) { return ((q >> S0) << (S0 + R)) | (q & ((1 << S0) - 1)); }

/* strided pass over stages [S0, S0 + R) of buffer buf (R <= 4, S0 >= 4: element k of a group at base + (k << S0)) */
template <int R, int S0, bool DIF>
__device__ __forceinline__ void pass_strided(unsigned* buf, const unsigned* __restrict__ tw, int t) {
    #pragma unroll 1          /* unrolled, ptxas front-loads all groups' loads and spills 180 B at 64 registers */
    for (int g = 0; g < (16 >> R); ++g) {
        const int q = t + THREADS * g;
        const int base = group_base<R, S0>(q);
        unsigned e[1 << R];
        const int sb = SWZ(base);
        #pragma unroll
        for (int k = 0; k < (1 << R); ++k) e[k] = buf[sb ^ SWZ(k << S0)];
        if (DIF) stages_dif<R, S0, S0 + R - 1, true>(e, base, tw); else stages_dit<R, S0, S0, false>(e, base, tw);
        #pragma unroll
        for (int k = 0; k < (1 << R); ++k) buf[sb ^ SWZ(k << S0)] = e[k];
    }
}

__device__ __forceinline__ void ld16(const unsigned* buf, int base, unsigned* e) {
    const int sb = SWZ(base);
    #pragma unroll
    for (int j = 0; j < 4; ++j) {
        const uint4 v = *reinterpret_cast<const uint4*>(buf + (sb ^ SWZ(4 * j)));
        e[4 * j] = v.x; e[4 * j + 1] = v.y; e[4 * j + 2] = v.z; e[4 * j + 3] = v.w;
    }
}
__device__ __forceinline__ void st16(unsigned* buf, int base, const unsigned* e) {
    const int sb = SWZ(base);
    #pragma unroll
    for (int j = 0; j < 4; ++j)
        *reinterpret_cast<uint4*>(buf + (sb ^ SWZ(4 * j))) = make_uint4(e[4 * j], e[4 * j + 1], e[4 * j + 2], e[4 * j + 3]);
}

/* One row.  CIN: a coefficient-form row (no INTT; src = int64 coefficients c[0 .. K + TP), 2 words per element;
   mask_tw = the x^l table).  x, cf are the CTA's shared / scratch buffers. */
template <bool CIN>
__device__ __forceinline__ void row_body(int row, const unsigned* __restrict__ src, unsigned* __restrict__ dst,
                 unsigned* __restrict__ coef_out, const unsigned* __restrict__ mask,
                 const unsigned* __restrict__ tw_inv, const unsigned* __restrict__ tw_fwd,
                 const unsigned* __restrict__ coset_tw, const unsigned* __restrict__ mask_tw,
                 int in_wide, int coef_stride, int coef_wide,
                 unsigned* __restrict__ cf_scratch, unsigned* __restrict__ stg)
{
    extern __shared__ unsigned x[];
#if CF_GLOBAL
    unsigned* cf = cf_scratch + (size_t)blockIdx.x * K;
#else
    unsigned* cf = x + K;
#endif
    unsigned r[16];
    const int t = threadIdx.x;
        const int st = SWZ(t);
        if constexpr (CIN) {
        /* coefficient rows: cf[brev(j)] = l c_j -- what the INTT of the row's evaluations would have left (unscaled,
           bit-reversed); the stores scatter (a few rows: the ZK mask rows), the loads are coalesced 8-byte strides */
        #pragma unroll
        for (int s = 0; s < 16; ++s) {
            const int j = t + THREADS * s;
            cf[SWZ(__brev((unsigned)j) >> (32 - LOGK))] = mont_mul(__ldg(&src[2 * j]), K_MONT);
        }
        __syncthreads();
        } else {
        /* ---- INTT (DIF): register stages m = K/2 .. THREADS on the 16 elements t + THREADS s ---- */
        #pragma unroll
        for (int s = 0; s < 16; ++s) r[s] = __ldg(&src[(t + THREADS * s) << in_wide]);
        stages_dif<4, LOGT, LOGK - 1, true>(r, t, tw_inv);
        #pragma unroll
        for (int s = 0; s < 16; ++s) x[st ^ SWZ(THREADS * s)] = r[s];
        __syncthreads();
        /* pass C': stages LOGT-1 .. 8 (radix 2^(LOGT-8)), lane-consecutive groups at stride 256 */
        if constexpr (LOGT > 8) { pass_strided<LOGT - 8, 8, true>(x, tw_inv, t); __syncthreads(); }
        /* pass B': stages 7 .. 4, stride-16 groups inside 256-blocks */
        if constexpr (LOGT > 4) { pass_strided<(LOGT < 8 ? LOGT - 4 : 4), 4, true>(x, tw_inv, t); __syncthreads(); }
        /* pass A': stages 3 .. 0 on 16 contiguous elements; the result (bit-reversed, unscaled coefficients) -> cf */
        {
            const int base = t << 4;
            unsigned e[16];
            ld16(x, base, e);
            stages_dif<4, 0, 3, true>(e, base, tw_inv);
            st16(cf, base, e);
        }
        __syncthreads();
        if (coef_out != 0) {
            /* natural-order l^-1 interp_H(W_j): each lane stores 4 consecutive coefficients as one uint4 (8 lanes = 128
               contiguous bytes; int64 output: two uint4 with zero high words, 256 bytes); the gather cf[brev(j)] is
               conflict-free under SWZ with lanes on bits 0-2 and LOGK-4, LOGK-3 of the vector index (fixed lane -> J
               mapping for THREADS >= 32) */
            unsigned* cd = coef_out + (size_t)row * coef_stride;
            #pragma unroll
            for (int s = 0; s < 4; ++s) {
                int J;
                if constexpr (LOGT >= 5) J = (t & 7) | ((t >> 5) << 3) | (s << (LOGT - 2)) | (((t >> 3) & 3) << LOGT);
                else J = t + THREADS * s;
                unsigned v[4];
                const int sp = SWZ(__brev((unsigned)(4 * J)) >> (32 - LOGK));
                #pragma unroll
                for (int w = 0; w < 4; ++w) v[w] = mont_mul(cf[sp ^ SWZ((((w & 1) << 1) | (w >> 1)) << (LOGK - 2))], KINV_MONT);   /* brev(w) */
                if (coef_wide) {
                    *reinterpret_cast<uint4*>(cd + 8 * J) = make_uint4(v[0], 0u, v[1], 0u);
                    *reinterpret_cast<uint4*>(cd + 8 * J + 4) = make_uint4(v[2], 0u, v[3], 0u);
                } else {
                    *reinterpret_cast<uint4*>(cd + 4 * J) = make_uint4(v[0], v[1], v[2], v[3]);
                }
            }
        }
        }
        /* ---- the four coset NTTs (DIT) ---- */
        #pragma unroll 1
        for (int c = 0; c < 4; ++c) {
            const unsigned* ct = coset_tw + (size_t)c * K;
            if (c > 0) __syncthreads();          /* the previous coset's register stages have consumed x */
            /* pass A: 16 contiguous coefficients, scaled by the coset table (+ the mask term z_c s_i (g w_n^c)^i at
               coefficient i < TP, i.e. at bit-reversed position), stages 0 .. 3, -> x */
            {
                const int base = t << 4;
                unsigned e[16];
                ld16(cf, base, e);
                #pragma unroll
                for (int j = 0; j < 4; ++j) {
                    const uint4 cw = __ldg(reinterpret_cast<const uint4*>(ct + base + 4 * j));
                    e[4 * j] = mont_mul(e[4 * j], cw.x); e[4 * j + 1] = mont_mul(e[4 * j + 1], cw.y);
                    e[4 * j + 2] = mont_mul(e[4 * j + 2], cw.z); e[4 * j + 3] = mont_mul(e[4 * j + 3], cw.w);
                }
#if TP > 0
                {
                    /* coefficient rows: c[K + i], the int64 row's high part (low words, stride 2) with the x^l table */
                    const unsigned* mk = CIN ? src + 2 * K : mask + (size_t)row * TP;
                    constexpr int mks = CIN ? 2 : 1;
#define MASKLD(i) __ldg(&mk[mks * (i)])
                    const unsigned* mt = mask_tw + (size_t)c * TP;          /* the caller passes mask_tw1 for CIN */
#if (TP & (TP - 1)) == 0 && TP <= K / 16
                    /* i = brev(pos) < TP  <=>  pos mod (K / TP) == 0: only element 0 of every (K / TP / 16)-th thread */
                    if ((base & (K / TP - 1)) == 0) {
                        const int i = __brev((unsigned)base) >> (32 - LOGK);
                        e[0] = add_p(e[0], mont_mul(MASKLD(i), __ldg(&mt[i])));
                    }
#else
                    #pragma unroll
                    for (int k = 0; k < 16; ++k) {
                        const int i = __brev((unsigned)(base + k)) >> (32 - LOGK);
                        if (i < TP) e[k] = add_p(e[k], mont_mul(MASKLD(i), __ldg(&mt[i])));
                    }
#endif
#undef MASKLD
                }
#endif
                stages_dit<4, 0, 0, false>(e, base, tw_fwd);
                st16(x, base, e);
            }
            __syncthreads();
            /* pass B: stages 4 .. 7 */
            if constexpr (LOGT > 4) { pass_strided<(LOGT < 8 ? LOGT - 4 : 4), 4, false>(x, tw_fwd, t); __syncthreads(); }
            /* pass C: stages 8 .. LOGT-1 */
            if constexpr (LOGT > 8) { pass_strided<LOGT - 8, 8, false>(x, tw_fwd, t); __syncthreads(); }
            /* register stages m = THREADS .. K/2 */
            #pragma unroll
            for (int s = 0; s < 16; ++s) r[s] = x[st ^ SWZ(THREADS * s)];
            stages_dit<4, LOGT, LOGT, false>(r, t, tw_fwd);
            /* natural protocol order: p(g w_n^{4 j + c}) at position 4 j + c. */
#if STAGE && __CUDA_ARCH__ >= 800
            /* cosets 0-2: coset-major into this CTA's staging buffer (a warp store = 128 contiguous bytes, kept in
               L2); coset 3: the same thread reads its own three staged values back (same addresses, program order)
               and writes the position's four cosets as one 16-byte store -> every sector written once, complete */
            unsigned* sg = stg + (size_t)blockIdx.x * (3 * K);
            unsigned long long pol;
            if (c < 3) {
                asm volatile("createpolicy.fractional.L2::evict_last.b64 %%0, 1.0;" : "=l"(pol));
                #pragma unroll
                for (int s = 0; s < 16; ++s) {
                    unsigned* a = sg + c * K + t + THREADS * s;
                    asm volatile("st.global.L2::cache_hint.u32 [%%0], %%1, %%2;" :: "l"(a), "r"(r[s]), "l"(pol) : "memory");
                }
            } else {
                asm volatile("createpolicy.fractional.L2::evict_first.b64 %%0, 1.0;" : "=l"(pol));
                #pragma unroll 4                 /* 12 loads in flight per group; the full unroll spills (64-register cap) */
                for (int s = 0; s < 16; ++s) {
                    const int i = t + THREADS * s;
                    const unsigned v0 = sg[i], v1 = sg[K + i], v2 = sg[2 * K + i];
                    unsigned* a = dst + ((size_t)i << 2);
                    asm volatile("st.global.L2::cache_hint.v4.u32 [%%0], {%%1, %%2, %%3, %%4}, %%5;"
                                 :: "l"(a), "r"(v0), "r"(v1), "r"(v2), "r"(r[s]), "l"(pol) : "memory");
                }
            }
#elif __CUDA_ARCH__ >= 800
            /* Each warp store touches 16 sectors with 8 B each; the sector is completed by the other three cosets
               ~100 us later, so keep the partial lines in L2 (evict_last) instead of writing them back three times
               (-5%% on the H100). */
            unsigned long long pol;
            asm volatile("createpolicy.fractional.L2::evict_last.b64 %%0, 1.0;" : "=l"(pol));
            #pragma unroll
            for (int s = 0; s < 16; ++s) {
                unsigned* a = dst + (((size_t)(t + THREADS * s)) << 2) + c;
                asm volatile("st.global.L2::cache_hint.u32 [%%0], %%1, %%2;" :: "l"(a), "r"(r[s]), "l"(pol) : "memory");
            }
#else
            #pragma unroll
            for (int s = 0; s < 16; ++s) dst[((size_t)(t + THREADS * s) << 2) | c] = r[s];
#endif
        }
}

/* the coefficient rows (a few per launch) out of line, so that their path does not add register pressure to the
   evaluation rows' (inlined, both paths spilled 136-192 B at the 64-register cap) */
__device__ __noinline__ void coef_row_body(int row, const unsigned* __restrict__ src, unsigned* __restrict__ dst,
                 const unsigned* __restrict__ tw_inv, const unsigned* __restrict__ tw_fwd,
                 const unsigned* __restrict__ coset_tw, const unsigned* __restrict__ mask_tw1,
                 unsigned* __restrict__ cf_scratch, unsigned* __restrict__ stg)
{
    row_body<true>(row, src, dst, 0, 0, tw_inv, tw_fwd, coset_tw, mask_tw1, 0, 0, 0, cf_scratch, stg);
}

/* dynamic shared memory: x[K] (the working row), cf[K] (the INTT coefficients, bit-reversed, unscaled), both swizzled.
   THREADS <= 512 (l <= 8192): two CTAs per SM fit in shared memory; cap the registers at 64 so they also fit in the
   register file (l = 8192 on the H100: 1.16 -> 0.99 ms for 3328 rows). */
extern "C" __global__ void __launch_bounds__(THREADS, (THREADS <= 512 ? 2 : 1))
rs_encode_ligero(const unsigned* __restrict__ in, unsigned* __restrict__ out, unsigned* __restrict__ coef_out,
                 const unsigned* __restrict__ mask,
                 const unsigned* __restrict__ tw_inv, const unsigned* __restrict__ tw_fwd,
                 const unsigned* __restrict__ coset_tw,   /* 4 x K: l^{-1} (g w_n^c)^i at bit-reversed position, Montgomery */
                 const unsigned* __restrict__ mask_tw,    /* 4 x TP: z_c (g w_n^c)^i, Montgomery */
                 const unsigned* __restrict__ mask_tw1,   /* 4 x TP: (z_c + 1) (g w_n^c)^i (coefficient rows) */
                 int rows,                                 /* evaluation rows + coefficient rows */
                 int rows_eval,                            /* rows [0, rows_eval) are evaluations, the rest coefficients */
                 const unsigned* __restrict__ cin,         /* the coefficient rows, int64 (2 words per element) */
                 int cin_stride,                           /* their row stride in 32-bit words */
                 int in_stride,                            /* row stride of `in` in 32-bit words */
                 int in_wide,                              /* 1: the evaluation rows are int64 (low words read; no int32 copy) */
                 int coef_stride,                          /* row stride of coef_out in 32-bit words */
                 int coef_wide,                            /* 1: coef_out is int64 (low word = value, high word 0) */
                 unsigned* __restrict__ cf_scratch,        /* CF_GLOBAL: gridDim.x x K words */
                 unsigned* __restrict__ stg)               /* STAGE: gridDim.x x 3 K words */
{
    for (int row = blockIdx.x; row < rows; row += gridDim.x) {
        unsigned* dst = out + (size_t)row * (4 * K);
        if (row >= rows_eval)                                                      /* uniform over the CTA */
            coef_row_body(row, cin + (size_t)(row - rows_eval) * cin_stride, dst, tw_inv, tw_fwd, coset_tw, mask_tw1,
                          cf_scratch, stg);
        else
            row_body<false>(row, in + (size_t)row * in_stride, dst, coef_out, mask, tw_inv, tw_fwd, coset_tw, mask_tw,
                            in_wide, coef_stride, coef_wide, cf_scratch, stg);
        __syncthreads();      /* x, cf are reused by the next row */
    }
}
"""


def _powers(w: int, count: int) -> np.ndarray:
    out = np.empty(count, dtype=np.uint64)
    out[0] = 1
    step, cur = 1, w % P
    while step < count:
        m = min(step, count - step)
        out[step:step + m] = (out[:m] * np.uint64(cur)) % np.uint64(P)
        step *= 2
        cur = cur * cur % P
    return out


def _bitrev(n: int) -> np.ndarray:
    bits = n.bit_length() - 1
    idx = np.arange(n, dtype=np.int64)
    rev = np.zeros(n, dtype=np.int64)
    for b in range(bits):
        rev |= ((idx >> b) & 1) << (bits - 1 - b)
    return rev


def _mont(a: np.ndarray) -> np.ndarray:
    return ((a % np.uint64(P)) * np.uint64(_R_MOD_P) % np.uint64(P)).astype(np.uint32)


def tables(l: int, n: int, t_pad: int) -> dict[str, np.ndarray]:
    """Stage twiddles (DIF inverse / DIT forward over ``<w_l>``), the four coset tables ``l^-1 (g w_n^c)^i`` at
    bit-reversed position, and the mask tables ``z_c (g w_n^c)^i`` (``i < t_pad``), all Montgomery uint32."""
    assert n == 4 * l
    wn = root_of_unity(n)
    wl = pow(wn, 4, P)
    wl_inv = pow(wl, -1, P)
    tw_fwd = np.zeros(l, dtype=np.uint64)
    tw_inv = np.zeros(l, dtype=np.uint64)
    m = 1
    while m < l:
        tw_fwd[m:2 * m] = _powers(pow(wl, l // (2 * m), P), m)
        tw_inv[m:2 * m] = _powers(pow(wl_inv, l // (2 * m), P), m)
        m *= 2
    rev = _bitrev(l)
    linv = pow(l, -1, P)
    cos, msk, msk1 = [], [], []
    for c in range(4):
        base = GEN * pow(wn, c, P) % P
        pw = _powers(base, l)
        cos.append(((pw * np.uint64(linv)) % np.uint64(P))[rev])
        if t_pad:
            xl = pow(base, l, P)                  # x^l on coset c (constant: w_l^{j l} = 1)
            z_c = (xl - 1) % P                    # Z_H(x) = x^l - 1
            assert z_c != 0
            msk.append((pw[:t_pad] * np.uint64(z_c)) % np.uint64(P))
            msk1.append((pw[:t_pad] * np.uint64(xl)) % np.uint64(P))    # coefficient rows: c_lo(x) + x^l c_hi(x)
    return {"tw_fwd": _mont(tw_fwd), "tw_inv": _mont(tw_inv), "coset": _mont(np.concatenate(cos)),
            "mask": _mont(np.concatenate(msk)) if t_pad else np.zeros(1, dtype=np.uint32),
            "mask1": _mont(np.concatenate(msk1)) if t_pad else np.zeros(1, dtype=np.uint32),
            "kinv_mont": int(_mont(np.array([linv], dtype=np.uint64))[0]),
            "k_mont": int(_mont(np.array([l], dtype=np.uint64))[0])}


def available() -> bool:
    try:
        import cupy  # noqa: F401
        return torch.cuda.is_available()
    except Exception:  # noqa: BLE001
        return False


class LigeroEncoderSIMT:
    """``encode(rows (R, l) int64/int32 torch on the device, mask (R, t_pad) or None, want_coefs) -> (U (R, n) int32,
    coefs (R, l) int32 | None)`` in the protocol's domain and order."""

    def __init__(self, l: int, n: int, t_pad: int = 0, device="cuda", threads: int | None = None,
                 cf_global: bool | None = None, stage: bool | None = None):
        import cupy as cp

        if n != 4 * l or l & (l - 1) or l < 256 or l > 16384:
            raise ValueError("the kernel is specialised to n = 4 l, l a power of two in [256, 16384]")
        self.cp, self.l, self.n, self.t_pad, self.device = cp, l, n, t_pad, torch.device(device)
        threads = threads or l // 16
        if threads != l // 16:
            raise ValueError("the kernel holds 16 elements per thread: threads = l / 16")
        self.threads = threads
        tabs = tables(l, n, t_pad)
        self._params = {"pinv": _P_INV_MOD_R, "k": l, "logk": l.bit_length() - 1, "threads": threads,
                        "logt": threads.bit_length() - 1, "tp": t_pad, "kinv_mont": tabs["kinv_mont"],
                        "k_mont": tabs["k_mont"], "cf_global": 0, "stage": 0}
        with cp.cuda.Device(self.device.index or 0):
            props = cp.cuda.runtime.getDeviceProperties(self.device.index or 0)
        sms = props["multiProcessorCount"]
        # x + cf (both bank-swizzled) in shared memory when the part allows (H100 227 KiB, A100 163 KiB per block);
        # otherwise (Ada / consumer Blackwell: 99 KiB) cf goes to a per-CTA L2-resident scratch (about +15 percent on the H100)
        self.cf_global = bool(cf_global) if cf_global is not None else 4 * (2 * l) > props["sharedMemPerBlockOptin"]
        self._params["cf_global"] = int(self.cf_global)
        self.smem = 4 * (l if self.cf_global else 2 * l)
        # STAGE (sm_80+): the staging buffer must stay L2-resident, so the grid is exactly the resident CTAs (one
        # 1024-thread CTA per SM, two of <= 512 threads): 3 l words each, 25 MB at l = 16384 on the H100 (50 MB L2)
        self.stage = (bool(stage) if stage is not None else props["major"] >= 8)
        self._params["stage"] = int(self.stage)
        resident = 1 if threads > 512 else 2
        self.blocks = sms * (resident if self.stage else (1 if self.cf_global else 4))
        self.kernel = self._compile()
        with cp.cuda.Device(self.device.index or 0):
            self.tw_fwd = cp.asarray(tabs["tw_fwd"])
            self.tw_inv = cp.asarray(tabs["tw_inv"])
            self.coset = cp.asarray(tabs["coset"])
            self.mask_tw = cp.asarray(tabs["mask"])
            self.mask_tw1 = cp.asarray(tabs["mask1"])
            self.cf_scratch = cp.empty(self.blocks * l if self.cf_global else 1, dtype=cp.uint32)
            self.stg = cp.empty(self.blocks * 3 * l if self.stage else 1, dtype=cp.uint32)

    def _compile(self):
        k = self.cp.RawKernel(_SRC % self._params, "rs_encode_ligero", options=("-std=c++17",))
        if self.smem > 48 * 1024:
            k.max_dynamic_shared_size_bytes = self.smem
        return k

    def _u32(self, t: torch.Tensor):
        return self.cp.asarray(t).view(self.cp.uint32)

    def _launch(self, kernel, R: int, args, stream):
        # torch's current stream vs cupy's: launch on torch's stream (or the given one -- hp2-host's pipelining)
        import warnings
        ts = stream if stream is not None else torch.cuda.current_stream(self.device)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            cstream = self.cp.cuda.ExternalStream(ts.cuda_stream)
        with cstream:
            kernel((min(self.blocks, R),), (self.threads,), args, shared_mem=self.smem)

    def _check_out(self, out: torch.Tensor | None, R: int) -> torch.Tensor:
        if out is None:
            out = torch.empty((R, self.n), dtype=torch.int32, device=self.device)
        elif out.shape != (R, self.n) or out.dtype != torch.int32 or not out.is_contiguous():
            raise ValueError("out must be a contiguous (R, n) int32 tensor")
        return out

    def _check_coef_rows(self, coefs: torch.Tensor) -> torch.Tensor:
        if coefs.shape[1:] != (self.l + self.t_pad,) or coefs.stride(1) != 1:
            raise ValueError("coefficient rows must be (R, l + t_pad) with contiguous rows")
        return coefs if coefs.dtype == torch.int64 else coefs.to(torch.int64)

    def encode(self, rows: torch.Tensor, mask: torch.Tensor | None = None, want_coefs: bool = False,
               out: torch.Tensor | None = None, stream: torch.cuda.Stream | None = None,
               coefs_out: torch.Tensor | None = None, coef_rows: torch.Tensor | None = None):
        """``coefs_out``: optional (R, l) int32 or int64 tensor for the natural-order coefficients (rows contiguous,
        any row stride -- e.g. the ``[:m, :l]`` view of the prover's (M, k) int64 coefficient matrix, so that no
        int32 -> int64 copy follows); implies ``want_coefs``.  ``coef_rows``: optional (R2, l + t_pad) int64
        coefficient-form rows (the ZK mask rows, see ``encode_coefs``) encoded in the same launch into
        ``out[R:R + R2]`` (they ride in the grid-stride tail: ~free next to a separate 36-row launch)."""
        R = rows.shape[0]
        if rows.shape != (R, self.l):
            raise ValueError(rows.shape)
        if (mask is not None) != (self.t_pad > 0):
            raise ValueError("mask must be given iff the encoder was built with t_pad > 0")
        if rows.dtype not in (torch.int32, torch.int64):
            rows = rows.to(torch.int64)
        rows = rows.contiguous()                  # int64 rows are read in place (low words: values < p < 2^31)
        in_wide = rows.dtype == torch.int64
        R2 = 0
        if coef_rows is not None:
            coef_rows = self._check_coef_rows(coef_rows)
            R2 = coef_rows.shape[0]
        out = self._check_out(out, R + R2)
        if coefs_out is not None:
            if coefs_out.shape != (R, self.l) or coefs_out.stride(1) != 1 or coefs_out.dtype not in (torch.int32, torch.int64):
                raise ValueError("coefs_out must be an (R, l) int32/int64 tensor with contiguous rows")
            coefs = coefs_out
        else:
            coefs = torch.empty((R, self.l), dtype=torch.int32, device=self.device) if want_coefs else None
        if mask is not None:
            if mask.shape != (R, self.t_pad):
                raise ValueError(mask.shape)
            mask32 = (mask if mask.dtype == torch.int32 else mask.to(torch.int32)).contiguous()
            mask_arg = self._u32(mask32)
        else:
            mask_arg = self.tw_fwd            # unused: TP = 0
        if coefs is not None:
            wide = coefs.dtype == torch.int64
            coef_arg, coef_stride = np.uint64(coefs.data_ptr()), coefs.stride(0) * (2 if wide else 1)
        else:
            coef_arg, coef_stride, wide = np.uint64(0), self.l, False
        cin_arg = np.uint64(coef_rows.data_ptr()) if R2 else np.uint64(0)
        cin_stride = coef_rows.stride(0) * 2 if R2 else 0
        self._launch(self.kernel, R + R2, (np.uint64(rows.data_ptr()), self._u32(out), coef_arg, mask_arg, self.tw_inv,
                                           self.tw_fwd, self.coset, self.mask_tw, self.mask_tw1, np.int32(R + R2),
                                           np.int32(R), cin_arg, np.int32(cin_stride),
                                           np.int32(self.l * (2 if in_wide else 1)), np.int32(int(in_wide)),
                                           np.int32(coef_stride), np.int32(int(wide)), self.cf_scratch, self.stg), stream)
        return out, coefs

    def encode_coefs(self, coefs: torch.Tensor, out: torch.Tensor | None = None,
                     stream: torch.cuda.Stream | None = None) -> torch.Tensor:
        """Evaluate coefficient rows on the code's domain: ``coefs`` (R, l + t_pad) int64 on the device (rows contiguous,
        any row stride), degree < k -- the ZK mask rows -- -> ``out`` (R, n) int32, bit-exact with
        ``eval_on_coset(coefs, n)``.  On coset ``c`` the high part enters as ``x^l c_hi(x)`` with the constant
        ``x^l = z_c + 1`` (the same fold-in as the witness mask, one table apart); no INTT."""
        coefs = self._check_coef_rows(coefs)
        R = coefs.shape[0]
        out = self._check_out(out, R)
        self._launch(self.kernel, R, (np.uint64(0), self._u32(out), np.uint64(0), self.tw_fwd, self.tw_inv, self.tw_fwd,
                                      self.coset, self.mask_tw, self.mask_tw1, np.int32(R), np.int32(0),
                                      np.uint64(coefs.data_ptr()), np.int32(coefs.stride(0) * 2),
                                      np.int32(0), np.int32(0), np.int32(self.l), np.int32(0),
                                      self.cf_scratch, self.stg), stream)
        return out


_ENC: dict = {}


def encoder_for(l: int, n: int, t_pad: int, device) -> LigeroEncoderSIMT:
    key = (l, n, t_pad, str(device))
    e = _ENC.get(key)
    if e is None:
        e = LigeroEncoderSIMT(l, n, t_pad, device)
        _ENC[key] = e
    return e
