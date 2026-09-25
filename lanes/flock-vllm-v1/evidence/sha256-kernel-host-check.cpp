#include <cstdint>
#include <cstdio>
#include <vector>
#define __device__
#define __constant__
#define __forceinline__ inline
#define __global__
#define __restrict__
static inline int __ffs(int x){ return x ? __builtin_ctz((unsigned)x)+1 : 0; }
struct D3{unsigned x;}; static D3 blockIdx{0}, blockDim{1}, threadIdx{0};
namespace vsha {
__device__ __constant__ uint32_t K[64] = {
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5, 0xd807aa98, 0x12835b01,
    0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
    0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da, 0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147,
    0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070, 0x19a4c116, 0x1e376c08,
    0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3, 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
    0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2};
constexpr int M_BASE = 512, CH_AND = 1024, MAJ_AND = 3072, ROUND_CARRY = 5120, SCHED_BITS = 92, OUT_W = 31;
constexpr uint32_t LO31 = 0x7FFFFFFFu, LO30 = 0x3FFFFFFFu;
__device__ __forceinline__ uint32_t rotr(uint32_t x, int n) { return (x >> n) | (x << (32 - n)); }
__device__ __forceinline__ void orw(uint64_t* b, long long bit, uint32_t v) {
    long long i = bit >> 6; int sh = (int)(bit & 63);
    b[i] |= (uint64_t)v << sh;
    if (sh > 32) b[i + 1] |= (uint64_t)v >> (64 - sh);
}
struct Buf { uint64_t *z, *a, *b; long long base; };
__device__ __forceinline__ void put(const Buf& o, int off, uint32_t zv, uint32_t av, uint32_t bv) {
    orw(o.z, o.base + off, zv); orw(o.a, o.base + off, av); orw(o.b, o.base + off, bv);
}
// (sum, maj1, maj2, rip) of x + y + z + w; triples [left, right, prod]
__device__ __forceinline__ uint32_t add4(uint32_t x, uint32_t y, uint32_t z, uint32_t w, uint32_t* m1, uint32_t* m2, uint32_t* rp) {
    uint32_t xz = x ^ z, yz = y ^ z, w1 = xz & yz, p1 = x ^ y ^ z, b1 = (w1 ^ z) << 1, pw = p1 ^ w, bw = b1 ^ w, w2 = pw & bw;
    uint32_t p2 = p1 ^ b1 ^ w, b2 = (w2 ^ w) << 1, sum = p2 + b2, cin = sum ^ p2 ^ b2, rl = p2 ^ cin, rr = b2 ^ cin;
    m1[0] = xz & LO31; m1[1] = yz & LO31; m1[2] = w1 & LO31;
    m2[0] = pw & LO31; m2[1] = bw & LO31; m2[2] = w2 & LO31;
    rp[0] = (rl >> 1) & LO30; rp[1] = (rr >> 1) & LO30; rp[2] = ((rl & rr) >> 1) & LO30;
    return sum;
}
__device__ __forceinline__ uint32_t add3(uint32_t x, uint32_t y, uint32_t m, uint32_t* mj, uint32_t* rp) {
    uint32_t xm = x ^ m, ym = y ^ m, w = xm & ym, p = x ^ y ^ m, bw = (w ^ m) << 1, sum = p + bw, cin = sum ^ p ^ bw;
    uint32_t rl = p ^ cin, rr = bw ^ cin;
    mj[0] = xm & LO31; mj[1] = ym & LO31; mj[2] = w & LO31;
    rp[0] = (rl >> 1) & LO30; rp[1] = (rr >> 1) & LO30; rp[2] = ((rl & rr) >> 1) & LO30;
    return sum;
}
__device__ __forceinline__ uint32_t add2(uint32_t x, uint32_t y, uint32_t* l, uint32_t* r, uint32_t* c) {
    uint32_t sum = x + y, cin = sum ^ x ^ y;
    *l = (x ^ cin) & LO31; *r = (y ^ cin) & LO31; *c = *l & *r;
    return sum;
}
}  // namespace vsha

__global__ void pure_sha256_witness(const uint32_t* __restrict__ cv, const uint32_t* __restrict__ msg, long long n_comp, int slots,
                                    int k_log, uint64_t* z, uint64_t* a, uint64_t* b) {
    using namespace vsha;
    long long ci = (long long)blockIdx.x * blockDim.x + threadIdx.x;
    if (ci >= n_comp) return;
    Buf o{z, a, b, ((ci / slots) << k_log) + ((ci % slots) << 15)};
    uint32_t h[8], W[64];
    for (int i = 0; i < 8; i++) h[i] = cv[ci * 8 + i];
    for (int i = 0; i < 16; i++) W[i] = msg[ci * 16 + i];
    int round_base[65];
    {
        int acc = ROUND_CARRY;
        for (int r = 0; r < 64; r++) { round_base[r] = acc; acc += 184 + (31 - (__ffs((int)K[r]) - 1 + 1)); }
        round_base[64] = acc;
    }
    const int SCHED = round_base[64], E_NEW = SCHED + 48 * SCHED_BITS, A_NEW = E_NEW + 32 * 32, OUT_CARRY = A_NEW + 32 * 32;
    const int ZC = OUT_CARRY + 8 * OUT_W;
    orw(z, o.base + ZC, 1); orw(a, o.base + ZC, 1); orw(b, o.base + ZC, 1);
    for (int w = 0; w < 8; w++) put(o, 32 * w, h[w], h[w], 0xFFFFFFFFu);
    for (int i = 0; i < 16; i++) put(o, M_BASE + 32 * i, W[i], W[i], 0xFFFFFFFFu);
    uint32_t m1[3], m2[3], rp[3];
    for (int t = 16; t < 64; t++) {
        uint32_t s1 = rotr(W[t - 2], 17) ^ rotr(W[t - 2], 19) ^ (W[t - 2] >> 10);
        uint32_t s0 = rotr(W[t - 15], 7) ^ rotr(W[t - 15], 18) ^ (W[t - 15] >> 3);
        W[t] = add4(s1, s0, W[t - 7], W[t - 16], m1, m2, rp);
        int base = SCHED + (t - 16) * SCHED_BITS;
        put(o, base + 0, m1[2], m1[0], m1[1]);
        put(o, base + 31, m2[2], m2[0], m2[1]);
        put(o, base + 62, rp[2], rp[0], rp[1]);
    }
    uint32_t A = h[0], B = h[1], Cc = h[2], D = h[3], E = h[4], F = h[5], G = h[6], H = h[7];
    for (int r = 0; r < 64; r++) {
        uint32_t fg = F ^ G, ch_and = E & fg;
        put(o, CH_AND + 32 * r, ch_and, E, fg);
        uint32_t ch_out = ch_and ^ G;
        uint32_t ba = B ^ A, ca = Cc ^ A, maj_and = ba & ca;
        put(o, MAJ_AND + 32 * r, maj_and, ba, ca);
        uint32_t maj_out = maj_and ^ A;
        int rb = round_base[r];
        // hk = H + K[r]: aux products for bits t..30, shifted down (t = trailing_zeros(K[r]) + 1)
        uint32_t kl, kr, kc;
        uint32_t hk = add2(K[r], H, &kl, &kr, &kc);
        int tt = __ffs((int)K[r]);
        uint32_t km = (1u << (31 - tt)) - 1;
        put(o, rb + 184, (kc >> tt) & km, (kl >> tt) & km, (kr >> tt) & km);
        uint32_t S1 = rotr(E, 6) ^ rotr(E, 11) ^ rotr(E, 25), S0 = rotr(A, 2) ^ rotr(A, 13) ^ rotr(A, 22);
        uint32_t t1 = add4(hk, S1, ch_out, W[r], m1, m2, rp);
        put(o, rb + 0, m1[2], m1[0], m1[1]);
        put(o, rb + 31, m2[2], m2[0], m2[1]);
        put(o, rb + 62, rp[2], rp[0], rp[1]);
        uint32_t am[3], ar[3];
        uint32_t a_new = add3(t1, S0, maj_out, am, ar);
        put(o, rb + 92, am[2], am[0], am[1]);
        put(o, rb + 123, ar[2], ar[0], ar[1]);
        uint32_t el, er, ec;
        uint32_t e_new = add2(D, t1, &el, &er, &ec);
        put(o, rb + 153, ec, el, er);
        if (r & 1) {
            put(o, A_NEW + 32 * (r / 2), a_new, a_new, 0xFFFFFFFFu);
            put(o, E_NEW + 32 * (r / 2), e_new, e_new, 0xFFFFFFFFu);
        }
        H = G; G = F; F = E; E = e_new; D = Cc; Cc = B; B = A; A = a_new;
    }
    const uint32_t fin[8] = {A, B, Cc, D, E, F, G, H};
    for (int w = 0; w < 8; w++) {
        uint32_t l, r, c;
        uint32_t sum = add2(fin[w], h[w], &l, &r, &c);
        put(o, OUT_CARRY + OUT_W * w, c, l, r);
        put(o, 256 + 32 * w, sum, sum, 0xFFFFFFFFu);
    }
}


int main(int argc,char**argv){
  FILE*f=fopen(argv[1],"rb"); long long n; fread(&n,8,1,f);
  std::vector<uint32_t> cv(n*8), msg(n*16); fread(cv.data(),4,n*8,f); fread(msg.data(),4,n*16,f);
  int slots=(int)n, k_log=0; while((1LL<<k_log) < (n<<15)) k_log++;
  size_t words=(size_t)1<<(k_log-6);
  std::vector<uint64_t> z(words),a(words),b(words);
  for(long long ci=0;ci<n;ci++){ blockIdx.x=(unsigned)ci; pure_sha256_witness(cv.data(),msg.data(),n,slots,k_log,z.data(),a.data(),b.data()); }
  std::vector<uint64_t> rz(n*512),ra(n*512),rb(n*512); fread(rz.data(),8,n*512,f); fread(ra.data(),8,n*512,f); fread(rb.data(),8,n*512,f);
  long long bad=0; for(long long i=0;i<n*512;i++){ if(z[i]!=rz[i]||a[i]!=ra[i]||b[i]!=rb[i]) { if(bad<5) printf("diff word %lld (comp %lld bit %lld): z %llx/%llx a %llx/%llx b %llx/%llx\n",i,i/512,(i%512)*64,(unsigned long long)z[i],(unsigned long long)rz[i],(unsigned long long)a[i],(unsigned long long)ra[i],(unsigned long long)b[i],(unsigned long long)rb[i]); bad++; } }
  printf("compressions %lld, differing words %lld\n", n, bad); return bad!=0;
}