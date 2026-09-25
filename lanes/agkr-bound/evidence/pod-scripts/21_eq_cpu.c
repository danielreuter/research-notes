// agkr-bound: the survey §3.8 link's dense check on the CPU (the verifier's O(N) part, and a CPU prover's): eq(r, i)
// over GF(2^128) (x^128 + x^7 + x^2 + x + 1, PCLMULQDQ) for i < 2^m by doubling, then c_i = sum_t rho_t bit_t(eq_i) in
// BabyBear^6 with 16 byte tables, then sum_i c_i b_i.  Random public-coin values; a cost model, not the protocol.
//   gcc -O3 -march=native -fopenmp 21_eq_cpu.c -o eq_cpu && OMP_NUM_THREADS=T ./eq_cpu N
#include <immintrin.h>
#include <omp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define P 2013265921ULL
typedef struct { uint64_t lo, hi; } g128;

static inline g128 gmul(g128 a, g128 b) {
    __m128i A = _mm_set_epi64x(a.hi, a.lo), B = _mm_set_epi64x(b.hi, b.lo);
    __m128i t0 = _mm_clmulepi64_si128(A, B, 0x00), t3 = _mm_clmulepi64_si128(A, B, 0x11);
    __m128i t1 = _mm_xor_si128(_mm_clmulepi64_si128(A, B, 0x10), _mm_clmulepi64_si128(A, B, 0x01));
    __m128i lo = _mm_xor_si128(t0, _mm_slli_si128(t1, 8)), hi = _mm_xor_si128(t3, _mm_srli_si128(t1, 8));
    // reduce hi * x^128 = hi * (x^7 + x^2 + x + 1)
    __m128i R = _mm_set_epi64x(0, 0x87);
    __m128i h0 = _mm_clmulepi64_si128(hi, R, 0x00), h1 = _mm_clmulepi64_si128(hi, R, 0x01);
    lo = _mm_xor_si128(lo, _mm_xor_si128(h0, _mm_slli_si128(h1, 8)));
    __m128i c = _mm_clmulepi64_si128(_mm_srli_si128(h1, 8), R, 0x00);
    lo = _mm_xor_si128(lo, c);
    g128 r = {(uint64_t)_mm_cvtsi128_si64(lo), (uint64_t)_mm_extract_epi64(lo, 1)};
    return r;
}

static uint64_t s = 0x9E3779B97F4A7C15ULL;
static uint64_t rnd(void) { s ^= s << 13; s ^= s >> 7; s ^= s << 17; return s; }
static double now(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec + 1e-9 * t.tv_nsec; }

int main(int argc, char **argv) {
    uint64_t N = argc > 1 ? strtoull(argv[1], 0, 10) : 393216ULL * 512;
    int m = 0;
    while ((1ULL << m) < N) m++;
    g128 *t = aligned_alloc(64, sizeof(g128) << m);
    g128 r[64];
    for (int j = 0; j < m; j++) { r[j].lo = rnd(); r[j].hi = rnd(); }
    uint64_t rho[128][6];
    for (int i = 0; i < 128; i++) for (int k = 0; k < 6; k++) rho[i][k] = rnd() % P;
    static uint64_t U[16][256][6];
    for (int k = 0; k < 16; k++) for (int b = 0; b < 256; b++) for (int e = 0; e < 6; e++) {
        uint64_t a = 0;
        for (int q = 0; q < 8; q++) if ((b >> q) & 1) a += rho[8 * k + q][e];
        U[k][b][e] = a % P;
    }
    uint8_t *bits = malloc(N);
    for (uint64_t i = 0; i < N; i++) bits[i] = rnd() & 1;
    for (int rep = 0; rep < 3; rep++) {
        double t0 = now();
        t[0].lo = 1; t[0].hi = 0;
        for (int j = 0; j < m; j++) {
            uint64_t h = 1ULL << j;
            g128 rj = r[j];
            #pragma omp parallel for schedule(static)
            for (uint64_t i = 0; i < h; i++) {
                g128 p = gmul(t[i], rj);
                t[i + h] = p;
                t[i].lo ^= p.lo; t[i].hi ^= p.hi;
            }
        }
        double t1 = now();
        uint64_t acc[6] = {0};
        #pragma omp parallel
        {
            uint64_t a[6] = {0};
            #pragma omp for schedule(static)
            for (uint64_t i = 0; i < N; i++) {
                const uint8_t *by = (const uint8_t *)&t[i];
                uint64_t c[6] = {0};
                for (int k = 0; k < 16; k++) for (int e = 0; e < 6; e++) c[e] += U[k][by[k]][e];
                if (bits[i]) for (int e = 0; e < 6; e++) a[e] = (a[e] + c[e] % P) % P;
            }
            #pragma omp critical
            for (int e = 0; e < 6; e++) acc[e] = (acc[e] + a[e]) % P;
        }
        double t2 = now();
        printf("RESULT N %llu m %d threads %d eq_s %.4f coef_ip_s %.4f total_s %.4f acc0 %llu\n", (unsigned long long)N, m,
               omp_get_max_threads(), t1 - t0, t2 - t1, t2 - t0, (unsigned long long)acc[0]);
        fflush(stdout);
    }
    // spot check eq(r, i) against the product formula
    uint64_t idx[3] = {0, N / 3, N - 1};
    for (int q = 0; q < 3; q++) {
        g128 w = {1, 0};
        for (int j = 0; j < m; j++) {
            g128 f = r[j];
            if (!((idx[q] >> j) & 1)) f.lo ^= 1;
            w = gmul(w, f);
        }
        if (w.lo != t[idx[q]].lo || w.hi != t[idx[q]].hi) { printf("eq mismatch at %llu\n", (unsigned long long)idx[q]); return 1; }
    }
    printf("eq spot checks OK\n");
    return 0;
}
