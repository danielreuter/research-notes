//! flock-bench (verity): ONE Flock union proof of the BLAKE3 row-leaf compressions (keyed BLAKE3
//! `blake3-keyed/row/v2`, x row + W column per VU, K = 1536) plus the binary-census transition units
//! (VU_UPV per VU) of the same VUs. Not modelled: chain glue, relation-leaf region equality, public
//! endpoints (so this is the two tables' cost, no glue). Leaf digests are checked against the `blake3`
//! crate for a sample of rows.
//!
//! env: VU_NETLIST VU_NAME VU_UPV (96 BF16 / 48 FP8) VU_WORD_BITS (16 / 8) VU_NS VU_RUNS
//! Output: one `RESULT\t{json}` line per point.

use std::{env::var, hint::black_box, time::Instant};

use flock_core::test_rng::Rng;
use flock_hash::blake3_compress;
use flock_prover::{
    challenger::FsChallenger,
    init_perf_thread_pool,
    merkle::HashKind,
    proof_io::R1csProofBundleLigerito,
    r1cs_hashes::{
        blake3::Compression,
        verity_unit::{CombinedSetup, Netlist},
    },
};

const CHUNK_START: u32 = 1;
const CHUNK_END: u32 = 2;
const PARENT: u32 = 4;
const ROOT: u32 = 8;
const KEYED_HASH: u32 = 16;

fn words_le(b: &[u8]) -> [u32; 16] {
    std::array::from_fn(|i| u32::from_le_bytes(b[4 * i..4 * i + 4].try_into().unwrap()))
}

fn blake3_key(role: u8) -> [u8; 32] {
    let mut k = [0u8; 32];
    let name: &[u8] = if role == 1 { b"verity/blake3-leaf/v1/x" } else { b"verity/blake3-leaf/v1/w" };
    k[..name.len()].copy_from_slice(name);
    k
}

fn blake3_row(row: &[u8], role: u8, out: &mut Vec<Compression>) -> [u8; 32] {
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

fn main() {
    let _ = init_perf_thread_pool();
    let path = var("VU_NETLIST").expect("VU_NETLIST");
    let name = var("VU_NAME").unwrap_or_else(|_| "unit".into());
    let upv: usize = var("VU_UPV").ok().and_then(|s| s.parse().ok()).unwrap_or(96);
    let word_bits: usize = var("VU_WORD_BITS").ok().and_then(|s| s.parse().ok()).unwrap_or(16);
    let runs: usize = var("VU_RUNS").ok().and_then(|s| s.parse().ok()).unwrap_or(3);
    let k = 1536usize;
    let ns: Vec<usize> = var("VU_NS")
        .unwrap_or_else(|_| "64 1024 4096".into())
        .split([' ', ','])
        .filter(|t| !t.is_empty())
        .map(|t| t.parse().unwrap())
        .collect();
    let threads = rayon::current_num_threads();
    for &n in &ns {
        let net = Netlist::load(&path);
        assert_eq!(net.self_check(), 0);
        let nv = net.vectors.len() as u32;
        let n_units = n * upv;
        let ids: Vec<u32> = (0..n_units as u32).map(|i| i % nv).collect();
        let mut rng = Rng::new(0x7E81_7700 ^ n as u64 ^ ((word_bits as u64) << 32));
        let mut b3: Vec<Compression> = Vec::new();
        let mut checked = 0;
        for inst in 0..n {
            for role in [1u8, 2u8] {
                let mut row = vec![0u8; k * word_bits / 8];
                rng.fill_bytes(&mut row);
                let d = blake3_row(&row, role, &mut b3);
                if inst < 16 || inst % 97 == 0 {
                    assert_eq!(d, *blake3::keyed_hash(&blake3_key(role), &row).as_bytes());
                    checked += 1;
                }
            }
        }
        let n_comp = b3.len();
        let t_setup = Instant::now();
        let setup = CombinedSetup::new(net, n_comp.max(n_units));
        let setup_s = t_setup.elapsed().as_secs_f64();
        let counts = [n_comp, n_units];
        let m = setup.pcs_params(counts).m;
        eprintln!("{name} n_vu={n} comp={n_comp} units={n_units} nu={} dense_m={m} setup={setup_s:.2}s", setup.nu);
        let fs = || FsChallenger::with_hash(b"flock-bench-v0", HashKind::default());
        let (p, _, _) = setup.prove(&b3, &ids, &mut fs());
        black_box(&p);
        drop(p);
        let mut ts = Vec::new();
        for _ in 0..runs {
            let t0 = Instant::now();
            let (p, _, _) = setup.prove(&b3, &ids, &mut fs());
            ts.push(t0.elapsed().as_secs_f64());
            black_box(&p);
        }
        let (proof, commitment, _) = setup.prove(&b3, &ids, &mut fs());
        let t = Instant::now();
        setup.verify(counts, &commitment, &proof, &mut fs()).expect("combined verify failed");
        let verify_s = t.elapsed().as_secs_f64();
        let size = R1csProofBundleLigerito { commitment, proof }.to_bytes().len();
        let best = ts.iter().cloned().fold(f64::INFINITY, f64::min);
        let tss: Vec<String> = ts.iter().map(|t| format!("{t:.4}")).collect();
        println!(
            "RESULT\t{{\"combined\":\"blake3+{name}\",\"n_vu\":{n},\"n_comp\":{n_comp},\"n_units\":{n_units},\"nu\":{},\"dense_m\":{m},\
             \"threads\":{threads},\"prove_best_s\":{best:.4},\"prove_runs_s\":[{}],\"verify_s\":{verify_s:.4},\"proof_bytes\":{size},\
             \"digests_checked\":{checked}}}",
            setup.nu,
            tss.join(",")
        );
    }
}
