
// ---- flock-glue additions (appended to flock-bench's verity_unit.rs) ----
impl Netlist {
    /// One instance from explicit input bits (0/1 per input), eval8 semantics: (z, a, b) per row as 0/1.
    pub fn eval_bits(&self, inputs: &[u8]) -> (Vec<u8>, Vec<u8>, Vec<u8>) {
        let u = self.useful;
        let (mut z, mut av, mut bv) = (vec![0u8; u], vec![0u8; u], vec![0u8; u]);
        for i in 0..self.n_in {
            z[i] = inputs[i];
            av[i] = inputs[i];
            bv[i] = inputs[i];
        }
        let c = self.const_pos;
        z[c] = 1;
        av[c] = 1;
        bv[c] = 1;
        for i in self.n_in..u {
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
        (z, av, bv)
    }

    /// Pack per-block (z, a, b) words (K/64 u64 each) with the same driver the host witnesses use.
    pub fn witness_from_blocks(blocks: &[[Vec<u64>; 3]], n_blocks_log: usize) -> (Vec<F128>, Vec<F128>, Vec<F128>, Vec<u8>) {
        let ids: Vec<usize> = (0..1usize << n_blocks_log).collect();
        crate::r1cs_hashes::common::drive_witness_packed_and_lincheck(&ids, None, n_blocks_log, K_LOG, |&id, zw, aw, bw| {
            zw.copy_from_slice(&blocks[id][0]);
            aw.copy_from_slice(&blocks[id][1]);
            bw.copy_from_slice(&blocks[id][2]);
        })
    }
}
