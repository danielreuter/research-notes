//! flock-bench (verity): a netlist-defined boolean table on the union prover — one
//! tensor-core transition unit (the binary census's `unit.py`, exported by
//! `export_unit.py`) per 2^13-bit block, `C = I`, constant wire pinned at the
//! last useful column. Mirrors `sha2::Sha256HybridSetup` (single-slot union,
//! batch-major partial witness, CSC lincheck circuit).
//!
//! Instances are indices into the netlist's validated input vectors; the
//! witness is evaluated from the netlist rows (inputs, then rows in order).

use std::array::from_fn;

use flock_core::{
    lincheck::LincheckCircuit,
    pcs::{
        Commitment, PcsParams,
        ligerito::{LigeritoProfile, embedded_initial_k_or_default},
    },
    proof::{R1csClaim, R1csProofMergedLigerito},
    r1cs::{BlockR1cs, SparseBinaryMatrix},
    union::UnionInstance,
    verifier::{FlockVerifyError, verify_ligerito_union},
};
use flock_field::F128;
use flock_transcript::challenger::Challenger;

use crate::{
    prover::{UnionSlotProverInput, prove_fast_ligerito_union},
    r1cs_hashes::common::{BM_V, BmRow, build_block_r1cs_with_matrices, drive_witness_batch_major_partial},
    schedule::Registry,
};

pub const K_LOG: usize = 13;
pub const K_SKIP: usize = 6;

#[derive(Debug)]
pub struct Netlist {
    pub useful: usize,
    pub const_pos: usize,
    pub n_in: usize,
    pub a: Vec<Vec<usize>>,
    pub b: Vec<Vec<usize>>,
    a_off: Vec<u32>,
    a_col: Vec<u32>,
    b_off: Vec<u32>,
    b_col: Vec<u32>,
    /// (input bits LSB-first, expected z bits LSB-first), validated by the exporter.
    pub vectors: Vec<(Vec<u8>, Vec<u8>)>,
}

fn hex(s: &str) -> Vec<u8> {
    (0..s.len() / 2).map(|i| u8::from_str_radix(&s[2 * i..2 * i + 2], 16).unwrap()).collect()
}

fn bit(v: &[u8], i: usize) -> u8 {
    (v[i >> 3] >> (i & 7)) & 1
}

impl Netlist {
    pub fn load(path: &str) -> Self {
        let text = std::fs::read_to_string(path).expect("netlist");
        let mut lines = text.lines();
        let h: Vec<usize> = lines.next().unwrap().split_whitespace().map(|t| t.parse().unwrap()).collect();
        let (useful, const_pos, n_in) = (h[0], h[1], h[2]);
        let mut a = Vec::with_capacity(useful);
        let mut b = Vec::with_capacity(useful);
        for _ in 0..useful {
            let v: Vec<usize> = lines.next().unwrap().split_whitespace().map(|t| t.parse().unwrap()).collect();
            let na = v[0];
            let nb = v[1 + na];
            a.push(v[1..1 + na].to_vec());
            b.push(v[2 + na..2 + na + nb].to_vec());
        }
        let nv: usize = lines.next().unwrap().trim().parse().unwrap();
        let vectors = (0..nv)
            .map(|_| {
                let mut it = lines.next().unwrap().split_whitespace();
                (hex(it.next().unwrap()), hex(it.next().unwrap()))
            })
            .collect();
        let csr = |rows: &Vec<Vec<usize>>| {
            let mut off = vec![0u32];
            let mut col = Vec::new();
            for r in rows {
                col.extend(r.iter().map(|&c| c as u32));
                off.push(col.len() as u32);
            }
            (off, col)
        };
        let (a_off, a_col) = csr(&a);
        let (b_off, b_col) = csr(&b);
        Self { useful, const_pos, n_in, a, b, a_off, a_col, b_off, b_col, vectors }
    }

    pub fn nnz(&self) -> usize {
        self.a_col.len() + self.b_col.len()
    }

    /// Evaluate 8 instances bit-sliced (bit j of each byte = instance j): (z, a, b) per row.
    pub fn eval8(&self, ids: [usize; BM_V], z: &mut [u8], av: &mut [u8], bv: &mut [u8]) {
        for i in 0..self.n_in {
            let mut x = 0u8;
            for (j, &id) in ids.iter().enumerate() {
                x |= bit(&self.vectors[id].0, i) << j;
            }
            z[i] = x;
            av[i] = x;
            bv[i] = x;
        }
        z[self.n_in..self.useful].fill(0);
        let c = self.const_pos;
        z[c] = 0xFF;
        av[c] = 0xFF;
        bv[c] = 0xFF;
        for i in self.n_in..self.useful {
            if i == c {
                continue;
            }
            let mut x = 0u8;
            for &k in &self.a_col[self.a_off[i] as usize..self.a_off[i + 1] as usize] {
                x ^= z[k as usize];
            }
            let mut y = 0u8;
            for &k in &self.b_col[self.b_off[i] as usize..self.b_off[i + 1] as usize] {
                y ^= z[k as usize];
            }
            av[i] = x;
            bv[i] = y;
            z[i] = x & y;
        }
    }

    /// Recompute every exported vector's z and re-check (a & b) = z; returns mismatching vectors.
    pub fn self_check(&self) -> usize {
        let u = self.useful;
        let nv = self.vectors.len();
        let (mut z, mut a, mut b) = (vec![0u8; u], vec![0u8; u], vec![0u8; u]);
        let mut bad = 0;
        for g in (0..nv).step_by(BM_V) {
            let ids: [usize; BM_V] = from_fn(|j| (g + j) % nv);
            self.eval8(ids, &mut z, &mut a, &mut b);
            for j in 0..BM_V.min(nv - g) {
                let want = &self.vectors[g + j].1;
                let ok = (0..u).all(|i| ((z[i] >> j) & 1) == bit(want, i) && (((a[i] & b[i]) >> j) & 1) == bit(want, i));
                if !ok {
                    bad += 1;
                }
            }
        }
        bad
    }

    fn build_group(&self, ids: [&u32; BM_V], rz: &mut [BmRow], ra: &mut [BmRow], rb: &mut [BmRow]) {
        thread_local! {
            static BUF: std::cell::RefCell<(Vec<u8>, Vec<u8>, Vec<u8>)> =
                const { std::cell::RefCell::new((Vec::new(), Vec::new(), Vec::new())) };
        }
        BUF.with(|buf| {
            let (z, a, b) = &mut *buf.borrow_mut();
            z.resize(self.useful, 0);
            a.resize(self.useful, 0);
            b.resize(self.useful, 0);
            let nv = self.vectors.len();
            self.eval8(from_fn(|j| *ids[j] as usize % nv), z, a, b);
            for (src, dst) in [(&*z, &mut *rz), (&*a, &mut *ra), (&*b, &mut *rb)] {
                for (i, &v) in src.iter().enumerate() {
                    if v == 0 {
                        continue;
                    }
                    let (w, s) = (i >> 6, i & 63);
                    for j in 0..BM_V {
                        dst[w][j] |= (((v >> j) & 1) as u64) << s;
                    }
                }
            }
        });
    }
}

impl Netlist {
    /// The unit as a plain (non-union, RowMajor) block R1CS, for `prove_ligerito` and Flock-CUDA.
    pub fn block_r1cs(&self, n_blocks_log: usize) -> BlockR1cs {
        let k = 1usize << K_LOG;
        let pad = |rows: &Vec<Vec<usize>>| {
            let mut r = rows.clone();
            r.resize(k, Vec::new());
            SparseBinaryMatrix::new(k, k, r)
        };
        build_block_r1cs_with_matrices(n_blocks_log, K_LOG, K_SKIP, self.useful, pad(&self.a), pad(&self.b), Some(self.const_pos))
    }

    /// RowMajor packed (z, a, b, z_lincheck) with every one of the 2^n_blocks_log blocks a real
    /// instance (vector id = block index mod #vectors), from per-vector blocks evaluated once.
    pub fn witness_row_major(&self, n_blocks_log: usize) -> (Vec<F128>, Vec<F128>, Vec<F128>, Vec<u8>) {
        let u = self.useful;
        let nv = self.vectors.len();
        let words = (1usize << K_LOG) / 64;
        let mut pre: Vec<[Vec<u64>; 3]> = Vec::with_capacity(nv);
        let (mut z, mut a, mut b) = (vec![0u8; u], vec![0u8; u], vec![0u8; u]);
        for g in (0..nv).step_by(BM_V) {
            self.eval8(from_fn(|j| (g + j) % nv), &mut z, &mut a, &mut b);
            for j in 0..BM_V.min(nv - g) {
                let blk: [Vec<u64>; 3] = from_fn(|t| {
                    let src = [&z, &a, &b][t];
                    let mut w = vec![0u64; words];
                    for i in 0..u {
                        w[i >> 6] |= (((src[i] >> j) & 1) as u64) << (i & 63);
                    }
                    w
                });
                pre.push(blk);
            }
        }
        let ids: Vec<usize> = (0..1usize << n_blocks_log).map(|i| i % nv).collect();
        crate::r1cs_hashes::common::drive_witness_packed_and_lincheck(&ids, None, n_blocks_log, K_LOG, |&id, zw, aw, bw| {
            zw.copy_from_slice(&pre[id][0]);
            aw.copy_from_slice(&pre[id][1]);
            bw.copy_from_slice(&pre[id][2]);
        })
    }
}

/// The BLAKE3 row-leaf table (slot 0, k = 2^14) and the unit table (slot 1, k = 2^13) in ONE union
/// proof (one commitment, one opening), as `mixed::MixedSetup` does for SHA-256 + BLAKE3. The
/// glue between them (chains, relation-leaf region equality, public endpoints) is not modelled.
#[derive(Debug)]
pub struct CombinedSetup {
    pub nu: usize,
    pub net: Netlist,
    pub blake3_r1cs: BlockR1cs,
    pub unit_r1cs: BlockR1cs,
    pub registry: Registry,
}

impl CombinedSetup {
    pub fn new(net: Netlist, max_count: usize) -> Self {
        let nu = min_n_blocks_log(max_count);
        let blake3_r1cs = crate::r1cs_hashes::blake3::build_block_r1cs(nu);
        let unit_r1cs = net.block_r1cs(nu);
        blake3_r1cs.csc_lincheck_circuit();
        unit_r1cs.csc_lincheck_circuit();
        let registry = Registry::new(
            vec![
                crate::schedule::TableType::from_block_r1cs(&blake3_r1cs),
                crate::schedule::TableType::from_block_r1cs(&unit_r1cs),
            ],
            nu,
        );
        let _ = registry.digest();
        Self { nu, net, blake3_r1cs, unit_r1cs, registry }
    }

    pub fn pcs_params(&self, counts: [usize; 2]) -> PcsParams {
        let profile = LigeritoProfile::Fast;
        let union = UnionInstance::new(&self.registry, counts.to_vec());
        let lb = embedded_initial_k_or_default(union.dense_m(), profile);
        PcsParams {
            m: union.dense_m(),
            log_inv_rate: profile.log_inv_rate(),
            log_batch_size: lb,
            profile,
            num_lanes: union.commit_lanes(lb),
            merkle_hash: Default::default(),
        }
    }

    pub fn prove<Ch: Challenger>(
        &self,
        blake3_inputs: &[crate::r1cs_hashes::blake3::Compression],
        ids: &[u32],
        challenger: &mut Ch,
    ) -> (R1csProofMergedLigerito, Commitment, R1csClaim) {
        let counts = [blake3_inputs.len(), ids.len()];
        let union = UnionInstance::new(&self.registry, counts.to_vec());
        let pcs_params = self.pcs_params(counts);
        let (nu, net) = (self.nu, &self.net);
        let slots = vec![
            UnionSlotProverInput::in_place(
                move |dst| crate::r1cs_hashes::blake3::generate_witness_batch_major_partial_into(blake3_inputs, nu, dst),
                self.blake3_r1cs.csc_lincheck_circuit(),
            ),
            UnionSlotProverInput::in_place(
                move |dst| {
                    crate::r1cs_hashes::common::drive_witness_batch_major_partial_into(
                        ids,
                        nu,
                        K_LOG,
                        net.useful,
                        dst,
                        |g, rz, ra, rb| net.build_group(g, rz, ra, rb),
                    )
                },
                self.unit_r1cs.csc_lincheck_circuit(),
            ),
        ];
        prove_fast_ligerito_union(&union, &pcs_params, slots, challenger)
    }

    pub fn verify<Ch: Challenger>(
        &self,
        counts: [usize; 2],
        commitment: &Commitment,
        proof: &R1csProofMergedLigerito,
        challenger: &mut Ch,
    ) -> Result<R1csClaim, FlockVerifyError> {
        let union = UnionInstance::new(&self.registry, counts.to_vec());
        let circuits: [&dyn LincheckCircuit; 2] =
            [self.blake3_r1cs.csc_lincheck_circuit(), self.unit_r1cs.csc_lincheck_circuit()];
        verify_ligerito_union(&union, &circuits, commitment, proof, &self.pcs_params(counts), challenger)
    }
}

pub fn min_n_blocks_log(n: usize) -> usize {
    n.max(8).next_power_of_two().trailing_zeros() as usize
}

#[derive(Debug)]
pub struct VerityUnitSetup {
    pub n_units: usize,
    pub net: Netlist,
    pub r1cs: BlockR1cs,
    pub registry: Registry,
    pub pcs_params: PcsParams,
}

impl VerityUnitSetup {
    pub fn new(net: Netlist, n_units: usize) -> Self {
        assert!(n_units >= 1);
        let profile = LigeritoProfile::Fast;
        let n_log = min_n_blocks_log(n_units);
        let k = 1usize << K_LOG;
        let pad = |rows: &Vec<Vec<usize>>| {
            let mut r = rows.clone();
            r.resize(k, Vec::new());
            SparseBinaryMatrix::new(k, k, r)
        };
        let r1cs = build_block_r1cs_with_matrices(
            n_log,
            K_LOG,
            K_SKIP,
            net.useful,
            pad(&net.a),
            pad(&net.b),
            Some(net.const_pos),
        );
        r1cs.csc_lincheck_circuit();
        flock_core::scratch::prewarm_prover(r1cs.m);
        let registry = Registry::new(vec![crate::schedule::TableType::from_block_r1cs(&r1cs)], n_log);
        let _ = registry.digest();
        let pcs_params = {
            let union = UnionInstance::new(&registry, vec![n_units]);
            let m = union.dense_m();
            let batch = embedded_initial_k_or_default(m, profile);
            PcsParams {
                m,
                log_inv_rate: profile.log_inv_rate(),
                log_batch_size: batch,
                profile,
                num_lanes: union.commit_lanes(batch),
                merkle_hash: Default::default(),
            }
        };
        Self { n_units, net, r1cs, registry, pcs_params }
    }

    pub fn m(&self) -> usize {
        self.r1cs.m
    }
    pub fn n_blocks_log(&self) -> usize {
        self.r1cs.m - self.r1cs.k_log
    }

    pub fn witness(&self, ids: &[u32]) -> (Vec<F128>, Vec<F128>, Vec<F128>, Vec<u8>) {
        let net = &self.net;
        drive_witness_batch_major_partial(ids, self.n_blocks_log(), K_LOG, net.useful, |g, rz, ra, rb| {
            net.build_group(g, rz, ra, rb)
        })
    }

    pub fn prove_fast<Ch: Challenger>(
        &self,
        ids: &[u32],
        challenger: &mut Ch,
    ) -> (R1csProofMergedLigerito, Commitment, R1csClaim) {
        assert_eq!(ids.len(), self.n_units);
        let union = UnionInstance::new(&self.registry, vec![self.n_units]);
        let slot = UnionSlotProverInput::new(self.witness(ids), self.r1cs.csc_lincheck_circuit());
        prove_fast_ligerito_union(&union, &self.pcs_params, vec![slot], challenger)
    }

    pub fn verify<Ch: Challenger>(
        &self,
        commitment: &Commitment,
        proof: &R1csProofMergedLigerito,
        challenger: &mut Ch,
    ) -> Result<R1csClaim, FlockVerifyError> {
        let union = UnionInstance::new(&self.registry, vec![self.n_units]);
        let circuit = self.r1cs.csc_lincheck_circuit();
        let circs: [&dyn LincheckCircuit; 1] = [circuit];
        verify_ligerito_union(&union, &circs, commitment, proof, &self.pcs_params, challenger)
    }
}
