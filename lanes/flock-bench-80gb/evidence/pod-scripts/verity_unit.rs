//! flock-bench-80gb (verity): the census transition unit (`internal/binary-census/unit.py`, bit-exact against
//! verity.ml.tc) as a Flock block R1CS. The netlist comes from `export_unit.py`: row i is committed bit z_i with
//! (A_i . z)(B_i . z) = z_i, C = I, const wire at `useful - 1` (pinned). Copied into
//! `crates/flock-prover/src/r1cs_hashes/verity_unit.rs` by the pod script (needs the crate-private drivers).
//!
//! Witness: VUs are chains of `units_per_vu` units (c_in(0) = +0, c_in(j+1) = c_out(j)); 64 VUs are evaluated
//! bit-sliced per u64 (one lane per VU) step by step, every row's a/b/z checked (a & b == z) for all lanes, then
//! 64x64-transposed into per-instance rows. Instance id = ((g * units_per_vu) + step) * 64 + lane.
//! NOT modelled (as in flock-bench's verity_shape): the chain glue c_in(j+1) = c_out(j) and the relation-hash
//! region equality are not proved; instances are proved as an independent batch.

use std::fs;

use flock_core::{
    r1cs::{BlockR1cs, SparseBinaryMatrix, WitnessLayout},
    union::SlotWitnessDest,
};
use flock_field::F128;
use rayon::prelude::*;

use crate::r1cs_hashes::common::{
    BM_V, BmRow, build_block_r1cs_with_matrices, drive_witness_batch_major_partial_into,
};

pub const K_SKIP: usize = 6;

pub struct Netlist {
    pub name: String,
    pub k_log: usize,
    pub useful: usize,
    pub cpos: usize,
    pub n_in: usize,
    pub n_and: usize,
    pub terms: usize,
    pub op_bits: usize,
    pub c_out: Vec<usize>,
    pub kind: Vec<u8>,
    pub a_ptr: Vec<u32>,
    pub a_idx: Vec<u32>,
    pub b_ptr: Vec<u32>,
    pub b_idx: Vec<u32>,
    /// (valid?, input bytes little-endian, expected c_out)
    pub tests: Vec<(bool, Vec<u8>, u32)>,
}

impl Netlist {
    pub fn load(path: &str) -> Self {
        let text = fs::read_to_string(path).expect("read netlist");
        let mut lines = text.lines();
        assert_eq!(lines.next().unwrap(), "FLOCKUNIT 1");
        let mut hdr = std::collections::HashMap::new();
        let mut c_out = Vec::new();
        let n_rows;
        loop {
            let l = lines.next().unwrap();
            let mut it = l.split_whitespace();
            let key = it.next().unwrap();
            if key == "c_out" {
                c_out = it.map(|t| t.parse().unwrap()).collect();
            } else if key == "rows" {
                n_rows = it.next().unwrap().parse::<usize>().unwrap();
                break;
            } else {
                hdr.insert(key.to_string(), it.next().unwrap().to_string());
            }
        }
        let g = |k: &str| hdr[k].parse::<usize>().unwrap();
        let useful = g("useful");
        assert_eq!(n_rows, useful);
        let (mut kind, mut a_ptr, mut a_idx, mut b_ptr, mut b_idx) =
            (Vec::new(), vec![0u32], Vec::new(), vec![0u32], Vec::new());
        for _ in 0..n_rows {
            let l = lines.next().unwrap();
            let mut it = l.split_whitespace();
            kind.push(it.next().unwrap().as_bytes()[0]);
            let na: usize = it.next().unwrap().parse().unwrap();
            for _ in 0..na {
                a_idx.push(it.next().unwrap().parse().unwrap());
            }
            let nb: usize = it.next().unwrap().parse().unwrap();
            for _ in 0..nb {
                b_idx.push(it.next().unwrap().parse().unwrap());
            }
            a_ptr.push(a_idx.len() as u32);
            b_ptr.push(b_idx.len() as u32);
        }
        let nt: usize = lines.next().unwrap().strip_prefix("tests ").unwrap().parse().unwrap();
        let mut tests = Vec::with_capacity(nt);
        for _ in 0..nt {
            let l = lines.next().unwrap();
            let mut it = l.split_whitespace();
            let v = it.next().unwrap() == "v";
            let hex = it.next().unwrap();
            let bytes = (0..hex.len() / 2).map(|i| u8::from_str_radix(&hex[2 * i..2 * i + 2], 16).unwrap()).collect();
            let exp = u32::from_str_radix(it.next().unwrap(), 16).unwrap();
            tests.push((v, bytes, exp));
        }
        Self {
            name: hdr["pipeline"].clone(),
            k_log: g("k_log"),
            useful,
            cpos: g("const"),
            n_in: g("n_in"),
            n_and: g("n_and"),
            terms: g("terms"),
            op_bits: g("op_bits"),
            c_out,
            kind,
            a_ptr,
            a_idx,
            b_ptr,
            b_idx,
            tests,
        }
    }

    pub fn nnz(&self) -> usize {
        self.a_idx.len() + self.b_idx.len()
    }

    pub fn block_r1cs(&self, n_blocks_log: usize) -> BlockR1cs {
        let k = 1usize << self.k_log;
        let mut a_rows = vec![Vec::new(); k];
        let mut b_rows = vec![Vec::new(); k];
        for i in 0..self.useful {
            a_rows[i] = self.a_idx[self.a_ptr[i] as usize..self.a_ptr[i + 1] as usize].iter().map(|&x| x as usize).collect();
            b_rows[i] = self.b_idx[self.b_ptr[i] as usize..self.b_ptr[i + 1] as usize].iter().map(|&x| x as usize).collect();
        }
        let mut r = build_block_r1cs_with_matrices(
            n_blocks_log,
            self.k_log,
            K_SKIP,
            self.useful,
            SparseBinaryMatrix::new(k, k, a_rows),
            SparseBinaryMatrix::new(k, k, b_rows),
            Some(self.cpos),
        );
        r.layout = WitnessLayout::BatchMajor;
        r
    }

    #[inline]
    fn xor_list(val: &[u64], idx: &[u32]) -> u64 {
        let mut x = 0u64;
        for &i in idx {
            x ^= unsafe { *val.get_unchecked(i as usize) };
        }
        x
    }

    /// Evaluate one 64-lane block. `val[..n_in]` holds the input planes. Fills z (val), a, b; returns the lane
    /// mask of rows violating a & b == z (0 for a satisfying witness).
    pub fn eval_block(&self, val: &mut [u64], a: &mut [u64], b: &mut [u64]) -> u64 {
        let u = self.useful;
        val[self.cpos] = !0;
        for i in self.n_in..u {
            let ai = Self::xor_list(val, &self.a_idx[self.a_ptr[i] as usize..self.a_ptr[i + 1] as usize]);
            let bi = Self::xor_list(val, &self.b_idx[self.b_ptr[i] as usize..self.b_ptr[i + 1] as usize]);
            a[i] = ai;
            b[i] = bi;
            match self.kind[i] {
                b'a' => val[i] = ai & bi,
                b'c' => val[i] = ai,
                b'k' => val[i] = !0,
                k => panic!("row kind {k}"),
            }
        }
        let mut bad = 0u64;
        for i in 0..self.n_in {
            a[i] = Self::xor_list(val, &self.a_idx[self.a_ptr[i] as usize..self.a_ptr[i + 1] as usize]);
            b[i] = Self::xor_list(val, &self.b_idx[self.b_ptr[i] as usize..self.b_ptr[i + 1] as usize]);
        }
        for i in 0..u {
            bad |= (a[i] & b[i]) ^ val[i];
        }
        bad
    }

    /// Bit-exact check of the exported test vectors (valid: c_out matches verity.ml.tc and every row holds;
    /// negative: some row fails). Returns (valid_ok, valid_total, neg_rejected, neg_total).
    pub fn check_tests(&self) -> (usize, usize, usize, usize) {
        let u = self.useful;
        let (mut vok, mut vt, mut nrej, mut nt) = (0, 0, 0, 0);
        for chunk in self.tests.chunks(64) {
            let mut val = vec![0u64; u];
            let mut a = vec![0u64; u];
            let mut b = vec![0u64; u];
            for (lane, (_, bytes, _)) in chunk.iter().enumerate() {
                for bit in 0..self.n_in {
                    if bytes[bit / 8] >> (bit % 8) & 1 == 1 {
                        val[bit] |= 1 << lane;
                    }
                }
            }
            let bad = self.eval_block(&mut val, &mut a, &mut b);
            for (lane, (v, _, exp)) in chunk.iter().enumerate() {
                let mut got = 0u32;
                for (j, &p) in self.c_out.iter().enumerate() {
                    got |= ((val[p] >> lane & 1) as u32) << j;
                }
                let lane_bad = bad >> lane & 1 == 1;
                if *v {
                    vt += 1;
                    if !lane_bad && got == *exp {
                        vok += 1;
                    }
                } else {
                    nt += 1;
                    if lane_bad {
                        nrej += 1;
                    }
                }
            }
        }
        (vok, vt, nrej, nt)
    }
}

#[inline]
fn transpose64(a: &mut [u64; 64]) {
    let mut j = 32usize;
    let mut m: u64 = 0x0000_0000_FFFF_FFFF;
    while j != 0 {
        let mut k = 0usize;
        while k < 64 {
            let t = ((a[k] >> j) ^ a[k + j]) & m;
            a[k] ^= t << j;
            a[k + j] ^= t;
            k = (k + j + 1) & !j;
        }
        j >>= 1;
        m ^= m << j;
    }
}

pub fn transpose64_selftest() {
    let mut s = 0x1234_5678_9abc_def0u64;
    let mut a = [0u64; 64];
    for x in a.iter_mut() {
        s ^= s << 13;
        s ^= s >> 7;
        s ^= s << 17;
        *x = s;
    }
    let orig = a;
    transpose64(&mut a);
    for i in 0..64 {
        for j in 0..64 {
            assert_eq!(orig[i] >> j & 1, a[j] >> i & 1, "transpose64");
        }
    }
}

/// Per-instance packed rows: `words` u64 per instance (slot bits LSB-first), for z, a, b.
pub struct UnitWitness {
    pub n_inst: usize,
    pub words: usize,
    pub z: Vec<u64>,
    pub a: Vec<u64>,
    pub b: Vec<u64>,
}

struct Xs(u64);
impl Xs {
    #[inline]
    fn next(&mut self) -> u64 {
        self.0 = self.0.wrapping_add(0x9E37_79B9_7F4A_7C15);
        let mut z = self.0;
        z = (z ^ (z >> 30)).wrapping_mul(0xBF58_476D_1CE4_E5B9);
        z = (z ^ (z >> 27)).wrapping_mul(0x94D0_49BB_1331_11EB);
        z ^ (z >> 31)
    }
}

impl Netlist {
    /// Operand planes: random sign/mantissa; exponent held finite and non-saturating
    /// (BF16: e in [120, 127]; E4M3: e in [0, 7]).
    fn fill_inputs(&self, val: &mut [u64], rng: &mut Xs) {
        let nb = self.op_bits;
        let (man, exp) = if nb == 16 { (7, 8) } else { (3, 4) };
        for t in 0..2 * self.terms {
            let base = t * nb;
            for bit in 0..nb {
                let v = if bit < man {
                    rng.next()
                } else if bit < man + exp {
                    let e = bit - man;
                    if nb == 16 {
                        match e {
                            0..=2 => rng.next(),
                            3..=6 => !0,
                            _ => 0,
                        }
                    } else if e < 3 {
                        rng.next()
                    } else {
                        0
                    }
                } else {
                    rng.next()
                };
                val[base + bit] = v;
            }
        }
    }

    pub fn gen_witness(&self, n_vus: usize, units_per_vu: usize, seed: u64) -> UnitWitness {
        assert!(n_vus % 64 == 0);
        let words = self.useful.div_ceil(64);
        let n_inst = n_vus * units_per_vu;
        let mut w = UnitWitness {
            n_inst,
            words,
            z: vec![0u64; n_inst * words],
            a: vec![0u64; n_inst * words],
            b: vec![0u64; n_inst * words],
        };
        let per_g = units_per_vu * 64 * words;
        let c_in_base = 2 * self.terms * self.op_bits;
        assert_eq!(c_in_base + 32, self.n_in);
        w.z.par_chunks_mut(per_g)
            .zip(w.a.par_chunks_mut(per_g))
            .zip(w.b.par_chunks_mut(per_g))
            .enumerate()
            .for_each(|(g, ((zg, ag), bg))| {
                let mut rng = Xs(seed ^ (g as u64).wrapping_mul(0xD6E8_FEB8_6659_FD93));
                let pad = words * 64;
                let mut val = vec![0u64; pad];
                let mut a = vec![0u64; pad];
                let mut b = vec![0u64; pad];
                let mut c = [0u64; 32];
                let mut blk = [0u64; 64];
                for s in 0..units_per_vu {
                    val.fill(0);
                    self.fill_inputs(&mut val, &mut rng);
                    val[c_in_base..c_in_base + 32].copy_from_slice(&c);
                    let bad = self.eval_block(&mut val, &mut a, &mut b);
                    assert_eq!(bad, 0, "unsatisfied row (assertion fired?) g={g} step={s}");
                    for (j, &p) in self.c_out.iter().enumerate() {
                        c[j] = val[p];
                    }
                    let inst0 = s * 64;
                    for (src, dst) in [(&val, &mut *zg), (&a, &mut *ag), (&b, &mut *bg)] {
                        for wd in 0..words {
                            blk.copy_from_slice(&src[wd * 64..wd * 64 + 64]);
                            transpose64(&mut blk);
                            for lane in 0..64 {
                                dst[(inst0 + lane) * words + wd] = blk[lane];
                            }
                        }
                    }
                }
            });
        w
    }

    /// The slot's batch-major witness, written in place (union assembly path).
    pub fn witness_into(&self, w: &UnitWitness, n_blocks_log: usize, dst: SlotWitnessDest<'_>) -> Vec<u8> {
        let idx: Vec<u32> = (0..w.n_inst as u32).collect();
        let words = w.words;
        drive_witness_batch_major_partial_into(
            &idx,
            n_blocks_log,
            self.k_log,
            self.useful,
            dst,
            |group: [&u32; BM_V], rz: &mut [BmRow], ra: &mut [BmRow], rb: &mut [BmRow]| {
                for (j, &&inst) in group.iter().enumerate() {
                    let o = inst as usize * words;
                    for wd in 0..words {
                        rz[wd][j] = w.z[o + wd];
                        ra[wd][j] = w.a[o + wd];
                        rb[wd][j] = w.b[o + wd];
                    }
                }
            },
        )
    }

    /// Allocating variant (for callers that want the `(z, a, b, stripe)` tuple).
    pub fn witness_alloc(&self, w: &UnitWitness, n_blocks_log: usize) -> (Vec<F128>, Vec<F128>, Vec<F128>, Vec<u8>) {
        let total = 1usize << (n_blocks_log + self.k_log - 7);
        let mut z = vec![F128::ZERO; total];
        let mut a = vec![F128::ZERO; total];
        let mut b = vec![F128::ZERO; total];
        let s = self.witness_into(
            w,
            n_blocks_log,
            SlotWitnessDest { z: &mut z, a: &mut a, b: &mut b, elide_padding_writes: false, dead_padding_unread: false },
        );
        (z, a, b, s)
    }
}
