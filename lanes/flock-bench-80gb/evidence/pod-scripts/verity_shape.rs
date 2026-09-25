//! flock-bench (verity): Flock prove/verify on verity's frame-v3 row-leaf batch shape.
//!
//! An instance (VU) has two leaves, an x row (role 1) and a W column (role 2), each K words of
//! 16 (BF16) or 8 (FP8) bits. The proved compressions are exactly the leaf digests' compressions:
//!   blake3-keyed/row/v2: keyed BLAKE3 of the row bytes; every chunk compression (16 per full
//!     1 KiB chunk) is proved, parents are native (as in B-Ligero);
//!   sha256/row/v1: SHA-256(prefix64 || row); the constant prefix block is a native midstate,
//!     the data blocks plus the padding block are proved.
//! Each row digest is recomputed from the proved compressions (plus the native parents / midstate)
//! and checked against the reference `blake3` / `sha2` crates before proving.
//! NOT modelled: the chaining wiring between compressions (cv_out[j] = cv_in[j+1]) and the public
//! per-row endpoints; the batch is proved as independent compressions.
//!
//! env: VS_HASH=blake3|sha2  VS_PREC=bf16|fp8  VS_K=1536  VS_NS="64 1024 4096"  VS_RUNS=3
//! Output: one `RESULT\t{json}` line per point.

use std::{
    alloc::{GlobalAlloc, Layout, System},
    env::var,
    hint::black_box,
    sync::atomic::{AtomicUsize, Ordering},
    time::Instant,
};

use flock_core::test_rng::Rng;
use flock_hash::blake3_compress;
use flock_prover::{
    challenger::FsChallenger,
    init_perf_thread_pool,
    merkle::HashKind,
    proof_io::R1csProofBundleLigerito,
    r1cs_hashes::{
        blake3::{Blake3Setup, Compression},
        sha2::{SHA256_IV, Sha256HybridSetup, sha256_compress},
    },
};
use sha2::{Digest, Sha256};

struct PeakAlloc;
static CUR: AtomicUsize = AtomicUsize::new(0);
static PEAK: AtomicUsize = AtomicUsize::new(0);
unsafe impl GlobalAlloc for PeakAlloc {
    unsafe fn alloc(&self, l: Layout) -> *mut u8 {
        let p = unsafe { System.alloc(l) };
        if !p.is_null() {
            let c = CUR.fetch_add(l.size(), Ordering::Relaxed) + l.size();
            PEAK.fetch_max(c, Ordering::Relaxed);
        }
        p
    }
    unsafe fn dealloc(&self, p: *mut u8, l: Layout) {
        unsafe { System.dealloc(p, l) };
        CUR.fetch_sub(l.size(), Ordering::Relaxed);
    }
    unsafe fn realloc(&self, p: *mut u8, l: Layout, new: usize) -> *mut u8 {
        let q = unsafe { System.realloc(p, l, new) };
        if !q.is_null() {
            if new >= l.size() {
                let c = CUR.fetch_add(new - l.size(), Ordering::Relaxed) + (new - l.size());
                PEAK.fetch_max(c, Ordering::Relaxed);
            } else {
                CUR.fetch_sub(l.size() - new, Ordering::Relaxed);
            }
        }
        q
    }
}
#[global_allocator]
static ALLOC: PeakAlloc = PeakAlloc;
fn reset_peak() {
    PEAK.store(CUR.load(Ordering::Relaxed), Ordering::Relaxed);
}
fn peak_mib() -> f64 {
    PEAK.load(Ordering::Relaxed) as f64 / (1024.0 * 1024.0)
}

const ROLE_X: u8 = 1;
const ROLE_W: u8 = 2;
const CHUNK_START: u32 = 1;
const CHUNK_END: u32 = 2;
const PARENT: u32 = 4;
const ROOT: u32 = 8;
const KEYED_HASH: u32 = 16;

fn words_le(b: &[u8]) -> [u32; 16] {
    std::array::from_fn(|i| u32::from_le_bytes(b[4 * i..4 * i + 4].try_into().unwrap()))
}
fn words_be(b: &[u8]) -> [u32; 16] {
    std::array::from_fn(|i| u32::from_be_bytes(b[4 * i..4 * i + 4].try_into().unwrap()))
}

fn blake3_key(role: u8) -> [u8; 32] {
    let mut k = [0u8; 32];
    let name: &[u8] = if role == ROLE_X { b"verity/blake3-leaf/v1/x" } else { b"verity/blake3-leaf/v1/w" };
    k[..name.len()].copy_from_slice(name);
    k
}

/// Chunk compressions of keyed BLAKE3(row); returns the digest recomputed with native parents.
fn blake3_row(row: &[u8], role: u8, out: &mut Vec<Compression>) -> [u8; 32] {
    assert!(row.len() % 64 == 0 && !row.is_empty());
    let key = blake3_key(role);
    let kw: [u32; 8] = std::array::from_fn(|i| u32::from_le_bytes(key[4 * i..4 * i + 4].try_into().unwrap()));
    let n_chunks = row.len().div_ceil(1024);
    let mut cvs: Vec<[u32; 8]> = Vec::with_capacity(n_chunks);
    for c in 0..n_chunks {
        let chunk = &row[c * 1024..row.len().min((c + 1) * 1024)];
        let nb = chunk.len() / 64;
        let mut cv = kw;
        for j in 0..nb {
            let mut flags = KEYED_HASH;
            if j == 0 {
                flags |= CHUNK_START;
            }
            if j == nb - 1 {
                flags |= CHUNK_END;
                if n_chunks == 1 {
                    flags |= ROOT;
                }
            }
            let m = words_le(&chunk[64 * j..64 * j + 64]);
            out.push((cv, m, c as u64, 64, flags));
            let o = blake3_compress(&cv, &m, c as u64, 64, flags);
            cv = std::array::from_fn(|i| o[i]);
        }
        cvs.push(cv);
    }
    // BLAKE3 tree: merge the largest power-of-two left subtree first.
    fn merge(kw: &[u32; 8], cvs: &[[u32; 8]], root: bool) -> [u32; 8] {
        if cvs.len() == 1 {
            return cvs[0];
        }
        let left_n = 1usize << (usize::BITS - 1 - (cvs.len() - 1).leading_zeros());
        let l = merge(kw, &cvs[..left_n], false);
        let r = merge(kw, &cvs[left_n..], false);
        let mut m = [0u32; 16];
        m[..8].copy_from_slice(&l);
        m[8..].copy_from_slice(&r);
        let o = blake3_compress(kw, &m, 0, 64, KEYED_HASH | PARENT | if root { ROOT } else { 0 });
        std::array::from_fn(|i| o[i])
    }
    let d = merge(&kw, &cvs, true);
    let mut b = [0u8; 32];
    for i in 0..8 {
        b[4 * i..4 * i + 4].copy_from_slice(&d[i].to_le_bytes());
    }
    b
}

fn sha256_prefix(role: u8, word_bits: u8, n_words: u32) -> [u8; 64] {
    let mut p = [0u8; 64];
    let tag = b"verity/sha256-row/v1\0";
    p[..tag.len()].copy_from_slice(tag);
    p[tag.len()] = role;
    p[tag.len() + 1] = word_bits;
    p[tag.len() + 2..tag.len() + 6].copy_from_slice(&n_words.to_be_bytes());
    p
}

/// Data + padding compressions of SHA-256(prefix || row) from the native prefix midstate.
fn sha2_row(row: &[u8], role: u8, word_bits: u8, n_words: u32, out: &mut Vec<([u32; 8], [u32; 16])>) -> [u8; 32] {
    let prefix = sha256_prefix(role, word_bits, n_words);
    let mut h = sha256_compress(&SHA256_IV, &words_be(&prefix));
    let total_bits = ((64 + row.len()) as u64) * 8;
    let mut msg = row.to_vec();
    msg.push(0x80);
    while msg.len() % 64 != 56 {
        msg.push(0);
    }
    msg.extend_from_slice(&total_bits.to_be_bytes());
    for blk in msg.chunks(64) {
        let m = words_be(blk);
        out.push((h, m));
        h = sha256_compress(&h, &m);
    }
    let mut b = [0u8; 32];
    for i in 0..8 {
        b[4 * i..4 * i + 4].copy_from_slice(&h[i].to_be_bytes());
    }
    b
}

fn main() {
    let _ = init_perf_thread_pool();
    let hash = var("VS_HASH").unwrap_or_else(|_| "blake3".into());
    let prec = var("VS_PREC").unwrap_or_else(|_| "bf16".into());
    let k: usize = var("VS_K").ok().and_then(|s| s.parse().ok()).unwrap_or(1536);
    let runs: usize = var("VS_RUNS").ok().and_then(|s| s.parse().ok()).unwrap_or(3);
    let ns: Vec<usize> = var("VS_NS")
        .unwrap_or_else(|_| "64 1024 4096".into())
        .split([' ', ','])
        .filter(|t| !t.is_empty())
        .map(|t| t.parse().unwrap())
        .collect();
    let word_bits: u8 = match prec.as_str() {
        "bf16" => 16,
        "fp8" => 8,
        p => panic!("VS_PREC must be bf16 or fp8, got {p}"),
    };
    let threads = rayon::current_num_threads();
    let row_len = k * word_bits as usize / 8;
    for &n in &ns {
        let mut rng = Rng::new(0x7E81_7700 ^ n as u64 ^ ((word_bits as u64) << 32));
        let mut b3: Vec<Compression> = Vec::new();
        let mut s2: Vec<([u32; 8], [u32; 16])> = Vec::new();
        let t_leaf = Instant::now();
        let mut checked = 0usize;
        for inst in 0..n {
            for role in [ROLE_X, ROLE_W] {
                let mut row = vec![0u8; row_len];
                rng.fill_bytes(&mut row);
                if hash == "blake3" {
                    let d = blake3_row(&row, role, &mut b3);
                    if inst < 64 || inst % 97 == 0 {
                        assert_eq!(d, *blake3::keyed_hash(&blake3_key(role), &row).as_bytes(), "blake3 row digest");
                        checked += 1;
                    }
                } else {
                    let d = sha2_row(&row, role, word_bits, k as u32, &mut s2);
                    if inst < 64 || inst % 97 == 0 {
                        let mut hh = Sha256::new();
                        hh.update(sha256_prefix(role, word_bits, k as u32));
                        hh.update(&row);
                        assert_eq!(d.as_slice(), hh.finalize().as_slice(), "sha256 row digest");
                        checked += 1;
                    }
                }
            }
        }
        let leaf_s = t_leaf.elapsed().as_secs_f64();
        let n_comp = if hash == "blake3" { b3.len() } else { s2.len() };
        let fs = || FsChallenger::with_hash(b"flock-bench-v0", HashKind::default());
        let t_setup = Instant::now();
        let (m, slots, best, verify_s, size, peak, times);
        if hash == "blake3" {
            let setup = Blake3Setup::new(n_comp);
            let setup_s = t_setup.elapsed().as_secs_f64();
            m = setup.m();
            slots = setup.n_block_slots();
            eprintln!("setup {setup_s:.3}s m={m} slots={slots} n_comp={n_comp}");
            let (p, _, _) = setup.prove_fast(&b3, &mut fs());
            black_box(&p);
            let mut ts = Vec::new();
            for _ in 0..runs {
                let t0 = Instant::now();
                let (p, _, _) = setup.prove_fast(&b3, &mut fs());
                ts.push(t0.elapsed().as_secs_f64());
                black_box(&p);
            }
            reset_peak();
            let base = CUR.load(Ordering::Relaxed) as f64 / 1048576.0;
            let (proof, commitment, _) = setup.prove_fast(&b3, &mut fs());
            peak = peak_mib() - base;
            let t = Instant::now();
            setup.verify(&commitment, &proof, &mut fs()).expect("verify failed");
            verify_s = t.elapsed().as_secs_f64();
            size = R1csProofBundleLigerito { commitment, proof }.to_bytes().len();
            best = ts.iter().cloned().fold(f64::INFINITY, f64::min);
            times = ts;
        } else {
            let setup = Sha256HybridSetup::new(n_comp);
            let setup_s = t_setup.elapsed().as_secs_f64();
            m = setup.m();
            slots = setup.n_block_slots();
            eprintln!("setup {setup_s:.3}s m={m} slots={slots} n_comp={n_comp}");
            let (p, _, _) = setup.prove_fast(&s2, &mut fs());
            black_box(&p);
            let mut ts = Vec::new();
            for _ in 0..runs {
                let t0 = Instant::now();
                let (p, _, _) = setup.prove_fast(&s2, &mut fs());
                ts.push(t0.elapsed().as_secs_f64());
                black_box(&p);
            }
            reset_peak();
            let base = CUR.load(Ordering::Relaxed) as f64 / 1048576.0;
            let (proof, commitment, _) = setup.prove_fast(&s2, &mut fs());
            peak = peak_mib() - base;
            let t = Instant::now();
            setup.verify(&commitment, &proof, &mut fs()).expect("verify failed");
            verify_s = t.elapsed().as_secs_f64();
            size = R1csProofBundleLigerito { commitment, proof }.to_bytes().len();
            best = ts.iter().cloned().fold(f64::INFINITY, f64::min);
            times = ts;
        }
        let ts: Vec<String> = times.iter().map(|t| format!("{t:.4}")).collect();
        println!(
            "RESULT\t{{\"hash\":\"{hash}\",\"prec\":\"{prec}\",\"k\":{k},\"n_inst\":{n},\"n_rows\":{},\"n_comp\":{n_comp},\
             \"comp_per_inst\":{},\"m\":{m},\"slots\":{slots},\"threads\":{threads},\"prove_best_s\":{best:.4},\
             \"prove_runs_s\":[{}],\"verify_s\":{verify_s:.4},\"proof_bytes\":{size},\"peak_heap_mib\":{peak:.1},\"peak_heap_abs_mib\":{:.1},\
             \"leaf_witness_native_s\":{leaf_s:.4},\"digests_checked\":{checked},\"comp_per_s\":{:.0}}}",
            2 * n,
            n_comp / n,
            ts.join(","),
            peak_mib(),
            n_comp as f64 / best
        );
    }
}
