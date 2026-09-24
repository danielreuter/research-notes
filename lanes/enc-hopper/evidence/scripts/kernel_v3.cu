#define P 2013265921u
#define PINV %(pinv)du        /* p^{-1} mod 2^32 */
#define K %(k)d
#define LOGK %(logk)d
#define THREADS %(threads)d
#define LOGT %(logt)d          /* K = 16 THREADS: 16 elements per thread in every phase */
#define TP %(tp)d              /* mask coefficients per row (0: no mask) */
#define KINV_MONT %(kinv_mont)du

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
            const unsigned w = __ldg(&tw[m + (idx & (m - 1))]);
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
    #pragma unroll
    for (int g = 0; g < (16 >> R); ++g) {
        const int q = t + THREADS * g;
        const int base = group_base<R, S0>(q);
        unsigned e[1 << R];
        #pragma unroll
        for (int k = 0; k < (1 << R); ++k) e[k] = buf[SWZ(base + (k << S0))];
        if (DIF) stages_dif<R, S0, S0 + R - 1, true>(e, base, tw); else stages_dit<R, S0, S0, false>(e, base, tw);
        #pragma unroll
        for (int k = 0; k < (1 << R); ++k) buf[SWZ(base + (k << S0))] = e[k];
    }
}

__device__ __forceinline__ void ld16(const unsigned* buf, int base, unsigned* e) {
    #pragma unroll
    for (int j = 0; j < 4; ++j) {
        const uint4 v = *reinterpret_cast<const uint4*>(buf + SWZ(base + 4 * j));
        e[4 * j] = v.x; e[4 * j + 1] = v.y; e[4 * j + 2] = v.z; e[4 * j + 3] = v.w;
    }
}
__device__ __forceinline__ void st16(unsigned* buf, int base, const unsigned* e) {
    #pragma unroll
    for (int j = 0; j < 4; ++j)
        *reinterpret_cast<uint4*>(buf + SWZ(base + 4 * j)) = make_uint4(e[4 * j], e[4 * j + 1], e[4 * j + 2], e[4 * j + 3]);
}

/* dynamic shared memory: x[K] (the working row), cf[K] (the INTT coefficients, bit-reversed, unscaled), both swizzled */
extern "C" __global__ void __launch_bounds__(THREADS)
rs_encode_ligero(const unsigned* __restrict__ in, unsigned* __restrict__ out, unsigned* __restrict__ coef_out,
                 const unsigned* __restrict__ mask,
                 const unsigned* __restrict__ tw_inv, const unsigned* __restrict__ tw_fwd,
                 const unsigned* __restrict__ coset_tw,   /* 4 x K: l^{-1} (g w_n^c)^i at bit-reversed position, Montgomery */
                 const unsigned* __restrict__ mask_tw,    /* 4 x TP: z_c (g w_n^c)^i, Montgomery */
                 int rows)
{
    extern __shared__ unsigned x[];
    unsigned* cf = x + K;
    unsigned r[16];
    const int t = threadIdx.x;
    for (int row = blockIdx.x; row < rows; row += gridDim.x) {
        const unsigned* src = in + (size_t)row * K;
        unsigned* dst = out + (size_t)row * (4 * K);
        /* ---- INTT (DIF): register stages m = K/2 .. THREADS on the 16 elements t + THREADS s ---- */
        #pragma unroll
        for (int s = 0; s < 16; ++s) r[s] = __ldg(&src[t + THREADS * s]);
        stages_dif<4, LOGT, LOGK - 1, true>(r, t, tw_inv);
        #pragma unroll
        for (int s = 0; s < 16; ++s) x[SWZ(t + THREADS * s)] = r[s];
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
               contiguous bytes); the gather cf[brev(j)] is conflict-free under SWZ with lanes on bits 0-2 and
               LOGK-4, LOGK-3 of the vector index (fixed lane -> J mapping for THREADS >= 32) */
            unsigned* cd = coef_out + (size_t)row * K;
            #pragma unroll
            for (int s = 0; s < 4; ++s) {
                int J;
                if constexpr (LOGT >= 5) J = (t & 7) | ((t >> 5) << 3) | (s << (LOGT - 2)) | (((t >> 3) & 3) << LOGT);
                else J = t + THREADS * s;
                unsigned v[4];
                #pragma unroll
                for (int w = 0; w < 4; ++w) {
                    const int pos = __brev((unsigned)(4 * J + w)) >> (32 - LOGK);
                    v[w] = mont_mul(cf[SWZ(pos)], KINV_MONT);
                }
                *reinterpret_cast<uint4*>(cd + 4 * J) = make_uint4(v[0], v[1], v[2], v[3]);
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
                    const unsigned* mk = mask + (size_t)row * TP;
                    const unsigned* mt = mask_tw + (size_t)c * TP;
                    #pragma unroll
                    for (int k = 0; k < 16; ++k) {
                        const int i = __brev((unsigned)(base + k)) >> (32 - LOGK);
                        if (i < TP) e[k] = add_p(e[k], mont_mul(__ldg(&mk[i]), __ldg(&mt[i])));
                    }
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
            for (int s = 0; s < 16; ++s) r[s] = x[SWZ(t + THREADS * s)];
            stages_dit<4, LOGT, LOGT, false>(r, t, tw_fwd);
            /* natural protocol order: p(g w_n^{4 j + c}) at position 4 j + c */
            #pragma unroll
            for (int s = 0; s < 16; ++s) dst[((size_t)(t + THREADS * s) << 2) | c] = r[s];
        }
        __syncthreads();      /* x, cf are reused by the next row */
    }
}
