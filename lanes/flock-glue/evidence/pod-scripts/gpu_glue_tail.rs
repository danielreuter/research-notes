
// ======================= flock-glue =======================
// Census unit witness built on the device from resident operand rows (mode 2), the host-built + uploaded
// witness (mode 1, flock-bench's port: the "before" path), and Flock-CUDA's BLAKE3 row-leaf proof (mode 0).
use flock_prover::r1cs_hashes::verity_unit::Netlist;

static UNIT_CSC: OnceLock<CscMatrices> = OnceLock::new();
static HOST_WIT: OnceLock<(Vec<F128>, Vec<F128>, Vec<F128>, Vec<u8>)> = OnceLock::new();

unsafe extern "C" {
    fn flock_cuda_prove_host(p: *const ProveParams, z: *const F128, a: *const F128, b: *const F128,
        zl: *const u8, out: *mut *mut u8, out_len: *mut usize) -> i32;
    fn flock_glue_prove_unit(p: *const ProveParams, out: *mut *mut u8, out_len: *mut usize) -> i32;
    fn flock_glue_unit_setup(hdr: *const i32, lvl_off: *const i32, lvl_rows: *const i32, n_lvl_rows: i32,
        a_off: *const i32, a_col: *const u16, a_nnz: i32, b_off: *const i32, b_col: *const u16, b_nnz: i32,
        cout: *const i32) -> i32;
    fn flock_glue_rows_upload(x: *const u8, w: *const u8, elem_bytes: i32, n_vu: i32, units_per_vu: i32, row_len: i32) -> i32;
    fn flock_glue_unit_witness_dump(m: i32, k_log: i32, z: *mut F128, a: *mut F128, b: *mut F128, zl: *mut u8,
        secs: *mut f64) -> i32;
}

/// (k operand elements per side, bits per element, bytes per element, units per VU); K = 1536 per VU.
fn pipe_params(name: &str) -> (usize, usize, usize, usize) {
    match name {
        "ampere_bf16" | "hopper_bf16" => (16, 16, 2, 96),
        "ada_e4m3" | "hopper_e4m3" => (32, 8, 1, 48),
        _ => panic!("unknown pipe {name}"),
    }
}

struct Glue {
    net: Netlist,
    cout: Vec<usize>,
    n_x: usize,
    n_w: usize,
    n_c: usize,
    k: usize,
    bits: usize,
    eb: usize,
    upv: usize,
}

fn env_or(k: &str, d: &str) -> String {
    std::env::var(k).unwrap_or_else(|_| d.to_string())
}

fn load_glue() -> Glue {
    let path = std::env::var("VU_NETLIST").expect("VU_NETLIST");
    let name = std::env::var("VU_NAME").expect("VU_NAME");
    let net = Netlist::load(&path);
    assert_eq!(net.self_check(), 0, "netlist self-check");
    let text = std::fs::read_to_string(&path).unwrap();
    let h: Vec<usize> = text.lines().next().unwrap().split_whitespace().map(|t| t.parse().unwrap()).collect();
    let cl = text.lines().find(|l| l.starts_with("COUT ")).expect("COUT line (flock-glue export_unit.py)");
    let cout: Vec<usize> = cl.split_whitespace().skip(1).map(|t| t.parse().unwrap()).collect();
    assert_eq!(cout.len(), 32);
    let (k, bits, eb, upv) = pipe_params(&name);
    assert_eq!(h[3], k * bits);
    Glue { net, cout, n_x: h[3], n_w: h[4], n_c: h[5], k, bits, eb, upv }
}

/// Upload the netlist tables once (level schedule, CSR without own-column terms, c_out columns).
fn setup_device(g: &Glue) -> usize {
    let net = &g.net;
    let (u, cp, n_in) = (net.useful, net.const_pos, net.n_in);
    let mut lvl = vec![0usize; u];
    for r in n_in..u {
        if r == cp {
            continue;
        }
        let mut m = 0;
        for &c in net.a[r].iter().chain(net.b[r].iter()) {
            if c == r {
                continue;
            }
            assert!(c < r || c == cp, "forward reference row {r} -> {c}");
            m = m.max(lvl[c]);
        }
        lvl[r] = m + 1;
    }
    let depth = *lvl.iter().max().unwrap();
    let mut lvl_off = vec![0i32];
    let mut lvl_rows = Vec::new();
    for d in 1..=depth {
        for r in n_in..u {
            if r != cp && lvl[r] == d {
                lvl_rows.push(r as i32);
            }
        }
        lvl_off.push(lvl_rows.len() as i32);
    }
    let csr = |rows: &Vec<Vec<usize>>| {
        let mut off = vec![0i32];
        let mut col = Vec::new();
        for (r, row) in rows.iter().enumerate() {
            col.extend(row.iter().filter(|&&c| c != r).map(|&c| c as u16));
            off.push(col.len() as i32);
        }
        (off, col)
    };
    let (a_off, a_col) = csr(&net.a);
    let (b_off, b_col) = csr(&net.b);
    let hdr = [u as i32, cp as i32, n_in as i32, g.n_x as i32, g.n_w as i32, g.n_c as i32, g.k as i32, g.bits as i32, depth as i32];
    let cout: Vec<i32> = g.cout.iter().map(|&c| c as i32).collect();
    let rc = unsafe {
        flock_glue_unit_setup(hdr.as_ptr(), lvl_off.as_ptr(), lvl_rows.as_ptr(), lvl_rows.len() as i32, a_off.as_ptr(),
            a_col.as_ptr(), a_col.len() as i32, b_off.as_ptr(), b_col.as_ptr(), b_col.len() as i32, cout.as_ptr())
    };
    assert_eq!(rc, 0, "flock_glue_unit_setup");
    println!("VSETUP depth={depth} rows={} nnz={}", lvl_rows.len(), a_col.len() + b_col.len());
    depth
}

fn splitmix(s: &mut u64) -> u64 {
    *s = s.wrapping_add(0x9E3779B97F4A7C15);
    let mut z = *s;
    z = (z ^ (z >> 30)).wrapping_mul(0xBF58476D1CE4E5B9);
    z = (z ^ (z >> 27)).wrapping_mul(0x94D049BB133111EB);
    z ^ (z >> 31)
}

/// Finite operands whose 1536-term chained sums stay finite (the unit asserts a finite accumulator).
fn gen_rows(g: &Glue, n_vu: usize, seed: u64, plant_nan: bool) -> (Vec<u8>, Vec<u8>) {
    let row_len = g.k * g.upv;
    let n = n_vu * row_len;
    let mut s = seed;
    let mut one = |s: &mut u64| -> u16 {
        let r = splitmix(s);
        if g.eb == 2 {
            let sign = (r & 1) as u16;
            let pick = (r >> 1) % 100;
            let e: u16 = if pick < 10 { 0 } else if pick < 20 { 1 + ((r >> 8) % 12) as u16 } else { 112 + ((r >> 8) % 29) as u16 };
            let m = if (r >> 20) % 100 < 8 { 0 } else { ((r >> 32) & 0x7f) as u16 };
            (sign << 15) | (e << 7) | m
        } else {
            let mut w = (r & 0xff) as u16;
            let mut k = 8;
            while (w & 0x7f) == 0x7f {
                w = ((r >> k) & 0xff) as u16;
                k += 8;
                if k > 56 {
                    w = 0x38;
                }
            }
            w
        }
    };
    let mut x = vec![0u8; n * g.eb];
    let mut w = vec![0u8; n * g.eb];
    for i in 0..n {
        let (a, b) = (one(&mut s), one(&mut s));
        if g.eb == 2 {
            x[2 * i..2 * i + 2].copy_from_slice(&a.to_le_bytes());
            w[2 * i..2 * i + 2].copy_from_slice(&b.to_le_bytes());
        } else {
            x[i] = a as u8;
            w[i] = b as u8;
        }
    }
    if plant_nan {
        let i = (n_vu / 2) * row_len + 7;
        if g.eb == 2 {
            x[2 * i..2 * i + 2].copy_from_slice(&0x7FC0u16.to_le_bytes());
        } else {
            x[i] = 0x7F;
        }
        println!("VPLANT NaN operand at VU {} element 7 (unit 0)", n_vu / 2);
    }
    (x, w)
}

fn upload_rows(g: &Glue, x: &[u8], w: &[u8], n_vu: usize) {
    let rc = unsafe { flock_glue_rows_upload(x.as_ptr(), w.as_ptr(), g.eb as i32, n_vu as i32, g.upv as i32, (g.k * g.upv) as i32) };
    assert_eq!(rc, 0, "rows upload");
}

fn nbl_for(n_units: usize) -> usize {
    n_units.max(8).next_power_of_two().trailing_zeros() as usize
}

/// Host reference: chained VUs through Netlist::eval_bits, block = u * n_vu + v, zero-input padding.
fn host_blocks(g: &Glue, x: &[u8], w: &[u8], n_vu: usize, nbl: usize) -> Vec<[Vec<u64>; 3]> {
    let words = (1usize << 13) / 64;
    let n_total = 1usize << nbl;
    let pack = |z: &[u8], a: &[u8], b: &[u8]| -> [Vec<u64>; 3] {
        let mut out: [Vec<u64>; 3] = std::array::from_fn(|_| vec![0u64; words]);
        for (t, src) in [z, a, b].iter().enumerate() {
            for (i, &bit) in src.iter().enumerate() {
                out[t][i >> 6] |= (bit as u64) << (i & 63);
            }
        }
        out
    };
    let (zz, za, zb) = g.net.eval_bits(&vec![0u8; g.net.n_in]);
    let pad = pack(&zz, &za, &zb);
    let mut blocks: Vec<[Vec<u64>; 3]> = (0..n_total).map(|_| pad.clone()).collect();
    let row_len = g.k * g.upv;
    let elem = |buf: &[u8], i: usize| -> u32 { if g.eb == 2 { u16::from_le_bytes([buf[2 * i], buf[2 * i + 1]]) as u32 } else { buf[i] as u32 } };
    for v in 0..n_vu {
        let mut c = [0u8; 32];
        for u in 0..g.upv {
            let mut inp = Vec::with_capacity(g.net.n_in);
            for side in [x, w] {
                for e in 0..g.k {
                    let val = elem(side, v * row_len + u * g.k + e);
                    for t in 0..g.bits {
                        inp.push(((val >> t) & 1) as u8);
                    }
                }
            }
            inp.extend_from_slice(&c);
            let (z, a, b) = g.net.eval_bits(&inp);
            for j in 0..32 {
                c[j] = z[g.cout[j]];
            }
            blocks[u * n_vu + v] = pack(&z, &a, &b);
        }
    }
    blocks
}

fn unit_r1cs(g: &Glue, nbl: usize) -> BlockR1cs {
    g.net.block_r1cs(nbl)
}

fn verify_art(art: &GpuArtifacts) -> Result<(), String> {
    let lc = SparseMatrixCircuit::new(&art.r1cs.a_0, &art.r1cs.b_0).with_const_pin(art.r1cs.const_pin);
    let mut ch = FsChallenger::with_hash(DOMAIN, CUDA_HASH);
    verify_ligerito(&art.r1cs, &art.commitment, &art.proof, &lc, &art.pcs_params, &mut ch).map(|_| ()).map_err(|e| format!("{e:?}"))
}

fn tamper_rejected(art: &GpuArtifacts) -> bool {
    let lc = SparseMatrixCircuit::new(&art.r1cs.a_0, &art.r1cs.b_0).with_const_pin(art.r1cs.const_pin);
    let mut bad = art.proof.clone();
    bad.pcs_open.ligerito.final_proof.yr[0].lo ^= 1;
    let mut ch = FsChallenger::with_hash(DOMAIN, CUDA_HASH);
    let r1 = verify_ligerito(&art.r1cs, &art.commitment, &bad, &lc, &art.pcs_params, &mut ch).is_err();
    let mut bad = art.proof.clone();
    bad.zerocheck.multilinear_rounds[0].0.hi ^= 1;
    let mut ch = FsChallenger::with_hash(DOMAIN, CUDA_HASH);
    let r2 = verify_ligerito(&art.r1cs, &art.commitment, &bad, &lc, &art.pcs_params, &mut ch).is_err();
    r1 && r2
}

fn words_of(v: &[F128]) -> Vec<u64> {
    v.iter().flat_map(|f| [f.lo, f.hi]).collect()
}

/// Device witness == host reference (bit for bit, z / a / b / z_lincheck); device proof verifies; proof tampers and a
/// planted NaN operand are rejected.  env: VU_NETLIST VU_NAME VU_NVU (default 64)
#[test]
#[ignore]
fn glue_check() {
    let _l = GPU_TEST_LOCK.lock().unwrap();
    let g = load_glue();
    setup_device(&g);
    let n_vu: usize = env_or("VU_NVU", "64").parse().unwrap();
    let nbl = nbl_for(n_vu * g.upv);
    let m = 13 + nbl;
    let (x, w) = gen_rows(&g, n_vu, 20260925, false);
    upload_rows(&g, &x, &w, n_vu);
    let len = 1usize << (m - 7);
    let (mut hz, mut ha, mut hb, mut hzl) = (vec![F128::ZERO; len], vec![F128::ZERO; len], vec![F128::ZERO; len], vec![0u8; len * 16]);
    let mut secs = 0f64;
    let rc = unsafe { flock_glue_unit_witness_dump(m as i32, 13, hz.as_mut_ptr(), ha.as_mut_ptr(), hb.as_mut_ptr(), hzl.as_mut_ptr(), &mut secs) };
    assert_eq!(rc, 0);
    let t = Instant::now();
    let blocks = host_blocks(&g, &x, &w, n_vu, nbl);
    let (rz, ra, rb, rzl) = Netlist::witness_from_blocks(&blocks, nbl);
    let host_s = t.elapsed().as_secs_f64();
    let mism = |d: &[u64], r: &[u64]| d.iter().zip(r.iter()).filter(|(a, b)| a != b).count();
    let (mz, ma, mb) = (mism(&words_of(&hz), &words_of(&rz)), mism(&words_of(&ha), &words_of(&ra)), mism(&words_of(&hb), &words_of(&rb)));
    let mzl = hzl.iter().zip(rzl.iter()).filter(|(a, b)| a != b).count();
    println!("VCHECK m={m} n_vu={n_vu} device_witness_s={secs:.5} host_ref_s={host_s:.2} mismatched_words z={mz} a={ma} b={mb} zl_bytes={mzl}");
    assert!(mz + ma + mb + mzl == 0, "device witness differs from the host reference");
    let art = gpu_prove_with(unit_r1cs(&g, nbl), &UNIT_CSC, 2, None);
    verify_art(&art).expect("device-witness proof must verify");
    println!("VCHECK proof verified m={m} prove_s={:.4}", art.prove_secs);
    assert!(tamper_rejected(&art), "proof tamper accepted");
    println!("VCHECK proof tampers rejected");
    let (x2, w2) = gen_rows(&g, n_vu, 20260925, true);
    upload_rows(&g, &x2, &w2, n_vu);
    let art = gpu_prove_with(unit_r1cs(&g, nbl), &UNIT_CSC, 2, None);
    match verify_art(&art) {
        Err(e) => println!("VNAN planted-NaN witness rejected: {e}"),
        Ok(()) => panic!("planted-NaN witness ACCEPTED"),
    }
}

/// End to end per VU batch: unit proof (mode GLUE_MODE: 2 device witness, 1 host witness + upload) then the BLAKE3
/// row-leaf proof (Flock-CUDA's own device witness) at GLUE_B3_NBL (0 = skip). Every proof is verified (outside the
/// timed region).  env: VU_NETLIST VU_NAME VU_NVU GLUE_MODE GLUE_B3_NBL GLUE_REPS GLUE_PLANT_NAN
#[test]
#[ignore]
fn glue_bench() {
    let _l = GPU_TEST_LOCK.lock().unwrap();
    let g = load_glue();
    let mode: u32 = env_or("GLUE_MODE", "2").parse().unwrap();
    let n_vu: usize = env_or("VU_NVU", "4096").parse().unwrap();
    let b3_nbl: usize = env_or("GLUE_B3_NBL", "0").parse().unwrap();
    let reps: usize = env_or("GLUE_REPS", "5").parse().unwrap();
    let plant = env_or("GLUE_PLANT_NAN", "0") == "1";
    let nbl = nbl_for(n_vu * g.upv);
    let m = 13 + nbl;
    if mode == 2 {
        setup_device(&g);
        let (x, w) = gen_rows(&g, n_vu, 20260925, plant);
        upload_rows(&g, &x, &w, n_vu);
        let mut secs = 0f64;
        let rc = unsafe { flock_glue_unit_witness_dump(m as i32, 13, null_mut(), null_mut(), null_mut(), null_mut(), &mut secs) };
        assert_eq!(rc, 0);
        println!("VWIT device unit witness m={m} n_vu={n_vu} {secs:.5} s (standalone, incl. lincheck transpose)");
    } else {
        let t = Instant::now();
        let hw = g.net.witness_row_major(nbl);
        println!("VWIT host_witness_s={:.4} (flock-bench tiled vectors)", t.elapsed().as_secs_f64());
        HOST_WIT.set(hw).ok();
    }
    let unit = || gpu_prove_with(unit_r1cs(&g, nbl), &UNIT_CSC, mode, None);
    let b3 = || gpu_prove(b3_nbl, None);
    // warm-up (arena, twiddles, matrices, zerocheck tables)
    let a = unit();
    if b3_nbl > 0 {
        let _ = b3();
    }
    match verify_art(&a) {
        Ok(()) => println!("VWARM unit verified"),
        Err(e) => println!("VWARM unit REJECTED: {e}"),
    }
    let mut e2e = Vec::new();
    let mut ffi = Vec::new();
    for rep in 0..reps {
        let t0 = Instant::now();
        let ua = unit();
        let t_unit = t0.elapsed().as_secs_f64();
        let ba = if b3_nbl > 0 { Some(b3()) } else { None };
        let t_all = t0.elapsed().as_secs_f64();
        let uv = verify_art(&ua);
        let bv = ba.as_ref().map(verify_art);
        let f = ua.prove_secs + ba.as_ref().map_or(0.0, |b| b.prove_secs);
        println!(
            "VGLUE rep={rep} m={m} b3_nbl={b3_nbl} unit_ffi={:.4} b3_ffi={:.4} ffi_sum={f:.4} call_unit={t_unit:.4} call_e2e={t_all:.4} unit_verify={} b3_verify={}",
            ua.prove_secs,
            ba.as_ref().map_or(0.0, |b| b.prove_secs),
            if uv.is_ok() { "ok".to_string() } else { format!("REJECTED {:?}", uv.err()) },
            match bv { None => "-".to_string(), Some(Ok(())) => "ok".to_string(), Some(Err(e)) => format!("REJECTED {e}") },
        );
        if !plant {
            assert!(uv.is_ok() && bv.as_ref().map_or(true, |r| r.is_ok()), "a proof failed to verify");
        }
        e2e.push(t_all);
        ffi.push(f);
    }
    e2e.sort_by(|a, b| a.partial_cmp(b).unwrap());
    ffi.sort_by(|a, b| a.partial_cmp(b).unwrap());
    println!("VSUMMARY pipe={} mode={mode} n_vu={n_vu} m={m} b3_nbl={b3_nbl} reps={reps} ffi_sum_median={:.4} ffi_sum_min={:.4} call_e2e_median={:.4}",
        env_or("VU_NAME", "?"), ffi[reps / 2], ffi[0], e2e[reps / 2]);
}
