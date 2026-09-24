"""Merkle leaves: two columns per thread (two independent Blake3 chains interleaved for ILP) vs the current one."""
import time, re, numpy as np, torch, cupy as cp
from backends.direct.ligero import commit_gpu as cg
from backends.direct.ligero.field import P
dev = torch.device("cuda")
def timeit(fn, reps=9):
    fn(); torch.cuda.synchronize(); ts = []
    for _ in range(reps):
        torch.cuda.synchronize(); t0 = time.perf_counter(); fn(); torch.cuda.synchronize(); ts.append(time.perf_counter() - t0)
    ts.sort(); return ts[len(ts)//2]
R, N = 3328, 65536
g = torch.Generator().manual_seed(7)
U = torch.randint(0, P, (R, N), generator=g, dtype=torch.int64).to(torch.int32).to(dev)
ref = torch.as_tensor(cg.leaves(U), device=dev).view(torch.int32); torch.cuda.synchronize()
nchunks = (R + 255) // 256
S = cg._SRC
# --- the 2-column kernel: lane owns columns col0 = 64 b + lane and col1 = col0 + 32
K2 = r'''
__device__ __forceinline__ void compress2(u32 cvA[8], const u32 blkA[16], u32 cvB[8], const u32 blkB[16], u64 counter, u32 block_len, u32 flags) {
    constexpr int SCHED[7][16] = {
        {0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15},
        {2,6,3,10,7,0,4,13,1,11,12,5,9,14,15,8},
        {3,4,10,12,13,2,7,14,6,5,9,0,11,15,8,1},
        {10,7,12,9,14,3,13,15,4,0,11,2,5,8,1,6},
        {12,13,9,11,15,10,14,8,7,2,5,3,0,1,6,4},
        {9,14,11,5,8,12,15,1,13,3,0,10,2,6,4,7},
        {11,15,5,0,1,9,8,6,14,10,2,12,3,4,7,13}};
    u32 s[16], q[16];
    #pragma unroll
    for (int i = 0; i < 8; ++i) { s[i] = cvA[i]; q[i] = cvB[i]; }
    s[8] = q[8] = 0x6A09E667u; s[9] = q[9] = 0xBB67AE85u; s[10] = q[10] = 0x3C6EF372u; s[11] = q[11] = 0xA54FF53Au;
    s[12] = q[12] = (u32)counter; s[13] = q[13] = (u32)(counter >> 32); s[14] = q[14] = block_len; s[15] = q[15] = flags;
    #pragma unroll
    for (int r = 0; r < 7; ++r) {
        g(s,0,4, 8,12, blkA[SCHED[r][0]],  blkA[SCHED[r][1]]);  g(q,0,4, 8,12, blkB[SCHED[r][0]],  blkB[SCHED[r][1]]);
        g(s,1,5, 9,13, blkA[SCHED[r][2]],  blkA[SCHED[r][3]]);  g(q,1,5, 9,13, blkB[SCHED[r][2]],  blkB[SCHED[r][3]]);
        g(s,2,6,10,14, blkA[SCHED[r][4]],  blkA[SCHED[r][5]]);  g(q,2,6,10,14, blkB[SCHED[r][4]],  blkB[SCHED[r][5]]);
        g(s,3,7,11,15, blkA[SCHED[r][6]],  blkA[SCHED[r][7]]);  g(q,3,7,11,15, blkB[SCHED[r][6]],  blkB[SCHED[r][7]]);
        g(s,0,5,10,15, blkA[SCHED[r][8]],  blkA[SCHED[r][9]]);  g(q,0,5,10,15, blkB[SCHED[r][8]],  blkB[SCHED[r][9]]);
        g(s,1,6,11,12, blkA[SCHED[r][10]], blkA[SCHED[r][11]]); g(q,1,6,11,12, blkB[SCHED[r][10]], blkB[SCHED[r][11]]);
        g(s,2,7, 8,13, blkA[SCHED[r][12]], blkA[SCHED[r][13]]); g(q,2,7, 8,13, blkB[SCHED[r][12]], blkB[SCHED[r][13]]);
        g(s,3,4, 9,14, blkA[SCHED[r][14]], blkA[SCHED[r][15]]); g(q,3,4, 9,14, blkB[SCHED[r][14]], blkB[SCHED[r][15]]);
    }
    #pragma unroll
    for (int i = 0; i < 8; ++i) { cvA[i] = s[i] ^ s[i + 8]; cvB[i] = q[i] ^ q[i + 8]; }
}

extern "C" __global__ void __launch_bounds__(512, LB2)
blake3_leaves2(const u32* __restrict__ U, int rows, int N, int nchunks, u32* __restrict__ out)
{
    __shared__ u32 cvs[16][8][64];
    const int lane = threadIdx.x & 31, w = threadIdx.x >> 5;
    const int col = blockIdx.x * 64 + lane;            /* and col + 32 */
    if (w < nchunks && col + 32 < N) {
        const int row0 = w * ROWS_PER_CHUNK;
        int words = rows - row0; if (words > ROWS_PER_CHUNK) words = ROWS_PER_CHUNK;
        const int nblocks = (words + 15) >> 4;
        const u32* p = U + (size_t)row0 * N + col;
        u32 cvA[8], cvB[8]; iv(cvA); iv(cvB);
        u32 blkA[16], blkB[16];
        for (int b = 0; b < nblocks; ++b) {
            const int have = min(words - b * 16, 16);
            const u32* q = p + (size_t)b * 16 * N;
            #pragma unroll
            for (int j = 0; j < 16; ++j) { blkA[j] = (j < have) ? __ldg(q + (size_t)j * N) : 0u; blkB[j] = (j < have) ? __ldg(q + (size_t)j * N + 32) : 0u; }
            u32 flags = 0;
            if (b == 0) flags |= CHUNK_START;
            if (b == nblocks - 1) { flags |= CHUNK_END; if (nchunks == 1) flags |= ROOT; }
            compress2(cvA, blkA, cvB, blkB, (u64)w, (u32)have * 4u, flags);
        }
        #pragma unroll
        for (int i = 0; i < 8; ++i) { cvs[w][i][lane] = cvA[i]; cvs[w][i][lane + 32] = cvB[i]; }
    }
    if (nchunks > 1) {
        __syncthreads();
        int count = nchunks;
        while (count > 1) {
            const int npairs = count >> 1, nout = (count + 1) >> 1;
            const bool pair = (w < npairs) && (col + 32 < N);
            u32 cvA[8], cvB[8];
            if (pair) {
                u32 blkA[16], blkB[16];
                #pragma unroll
                for (int i = 0; i < 8; ++i) { blkA[i] = cvs[2 * w][i][lane]; blkA[8 + i] = cvs[2 * w + 1][i][lane];
                                              blkB[i] = cvs[2 * w][i][lane + 32]; blkB[8 + i] = cvs[2 * w + 1][i][lane + 32]; }
                iv(cvA); iv(cvB);
                compress2(cvA, blkA, cvB, blkB, 0ull, 64u, (count == 2) ? (PARENT | ROOT) : PARENT);
            }
            __syncthreads();
            if (pair) {
                #pragma unroll
                for (int i = 0; i < 8; ++i) { cvs[w][i][lane] = cvA[i]; cvs[w][i][lane + 32] = cvB[i]; }
            } else if (w == npairs && (count & 1) && col + 32 < N) {
                #pragma unroll
                for (int i = 0; i < 8; ++i) { cvs[w][i][lane] = cvs[count - 1][i][lane]; cvs[w][i][lane + 32] = cvs[count - 1][i][lane + 32]; }
            }
            __syncthreads();
            count = nout;
        }
    }
    if (w == 0 && col + 32 < N) {
        u32* o = out + (size_t)col * 8; u32* o2 = out + (size_t)(col + 32) * 8;
        #pragma unroll
        for (int i = 0; i < 8; ++i) { o[i] = cvs[0][i][lane]; o2[i] = cvs[0][i][lane + 32]; }
    }
}
'''
def run(name, src, fn="blake3_leaves", cols=32, lb2=1, prefetch=0):
    try:
        mod = cp.RawModule(code=src, options=("-std=c++17", f"-DPREFETCH={prefetch}", f"-DLB2={lb2}")); k = mod.get_function(fn)
    except Exception as e:
        print(f"{name:44s} COMPILE FAIL {str(e)[:600]}"); return
    out = torch.empty((N, 8), dtype=torch.int32, device=dev)
    Ucp = cp.asarray(U).view(cp.uint32); O = cp.asarray(out).view(cp.uint32)
    th = 32 * nchunks; bl = (N + cols - 1) // cols
    go = lambda: k((bl,), (th,), (Ucp, np.int32(R), np.int32(N), np.int32(nchunks), O))
    t = timeit(go); same = bool(torch.equal(out, ref))
    print(f"{name:44s} {t*1e3:7.3f} ms ({R*N*4/t/1e9:6.0f} GB/s) regs={k.num_regs} local={k.local_size_bytes} {'bit-exact' if same else 'DIFFERS !!!'}", flush=True)
run("leaves (current, 1 column/thread)", S)
for lb in (1, 2):
    run(f"leaves2 (2 columns/thread, launch_bounds(512,{lb}))", S + K2, fn="blake3_leaves2", cols=64, lb2=lb)
