
// ======================= flock-glue =======================
// Census unit witness built on the device from resident operand rows (mode 2), the host-built + uploaded
// witness (mode 1, flock-bench's port: the "before" path), and Flock-CUDA's BLAKE3 row-leaf proof (mode 0).
// Mode 3 = mode 2 with the unit witness enqueued on a side stream first, the BLAKE3 proof run while it builds,
// then the unit proof (it waits for the witness and copies it into its arena).
use flock_prover::r1cs_hashes::verity_unit::Netlist;

static UNIT_CSC: OnceLock<CscMatrices> = OnceLock::new();
static HOST_WIT: OnceLock<(Vec<F128>, Vec<F128>, Vec<F128>, Vec<u8>)> = OnceLock::new();

unsafe extern "C" {
    fn flock_cuda_prove_host(p: *const ProveParams, z: *const F128, a: *const F128, b: *const F128,
        zl: *const u8, out: *mut *mut u8, out_len: *mut usize) -> i32;
    fn flock_glue_prove_unit(p: *const ProveParams, out: *mut *mut u8, out_len: *mut usize) -> i32;
    fn flock_glue_prove_unit_pre(p: *const ProveParams, out: *mut *mut u8, out_len: *mut usize) -> i32;
    fn flock_glue_unit_witness_launch(m: i32, k_log: i32) -> i32;
    fn flock_glue_unit_setup(hdr: *const i32, gdesc: *const u32, gstart: *const u32, cols: *const u16, n_cols: i32,
        seg_end: *const i32, batch_seg: *const i32, cout: *const i32) -> i32;
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
    // level-ordered gates, A terms then B terms, own column dropped; segments = levels split to fit a batch;
    // batches = consecutive segments whose terms / gates fit the device's shared buffers
    const COLS_CAP: usize = 12288 - 4;
    const DESC_CAP: usize = 1024;
    let (mut gdesc, mut gstart, mut cols) = (Vec::<u32>::new(), vec![0u32], Vec::<u16>::new());
    let (mut seg_end, mut batch_seg) = (Vec::<i32>::new(), vec![0i32]);
    let (mut b_terms, mut b_gates) = (0usize, 0usize);
    for d in 1..=depth {
        let rows: Vec<usize> = (n_in..u).filter(|&r| r != cp && lvl[r] == d).collect();
        let mut seg_terms = 0usize;
        let mut seg_open = false;
        for &r in &rows {
            let fa: Vec<u16> = net.a[r].iter().filter(|&&c| c != r).map(|&c| c as u16).collect();
            let fb: Vec<u16> = net.b[r].iter().filter(|&&c| c != r).map(|&c| c as u16).collect();
            let t = fa.len() + fb.len();
            assert!(t <= COLS_CAP && fa.len() < 65536);
            if b_terms + t > COLS_CAP || b_gates + 1 > DESC_CAP {
                if seg_open {
                    seg_end.push(gdesc.len() as i32);
                    seg_open = false;
                }
                batch_seg.push(seg_end.len() as i32);
                b_terms = 0;
                b_gates = 0;
            }
            gdesc.push(r as u32 | ((fa.len() as u32) << 16));
            cols.extend_from_slice(&fa);
            cols.extend_from_slice(&fb);
            gstart.push(cols.len() as u32);
            b_terms += t;
            b_gates += 1;
            seg_terms += t;
            seg_open = true;
        }
        if seg_open {
            seg_end.push(gdesc.len() as i32);
        }
        let _ = seg_terms;
    }
    if *batch_seg.last().unwrap() != seg_end.len() as i32 {
        batch_seg.push(seg_end.len() as i32);
    }
    cols.extend_from_slice(&[0u16; 16]);
    let n_gates = gdesc.len();
    let n_segs = seg_end.len();
    let n_batches = batch_seg.len() - 1;
    let hdr = [u as i32, cp as i32, n_in as i32, g.n_x as i32, g.n_w as i32, g.n_c as i32, g.k as i32, g.bits as i32,
        n_gates as i32, n_segs as i32, n_batches as i32];
    let cout: Vec<i32> = g.cout.iter().map(|&c| c as i32).collect();
    let rc = unsafe {
        flock_glue_unit_setup(hdr.as_ptr(), gdesc.as_ptr(), gstart.as_ptr(), cols.as_ptr(), cols.len() as i32,
            seg_end.as_ptr(), batch_seg.as_ptr(), cout.as_ptr())
    };
    assert_eq!(rc, 0, "flock_glue_unit_setup");
    println!("VSETUP depth={depth} gates={n_gates} terms={} segments={n_segs} batches={n_batches}", cols.len() - 16);
    // critical-path proxy per segment: the slowest gate's serial term iterations at the device's lanes-per-gate
    let (mut it_n, mut it_w, mut t_n, mut g_n) = (0usize, 0usize, 0usize, 0usize);
    let mut heavy: Vec<usize> = Vec::new();
    for s in 0..n_segs {
        let (g0, g1) = (if s > 0 { seg_end[s - 1] as usize } else { 0 }, seg_end[s] as usize);
        let ng = g1 - g0;
        let mut lg = 5;
        while lg > 0 && (ng << lg) > 512 {
            lg -= 1;
        }
        let mut worst = 0usize;
        for gi in g0..g1 {
            let (st, en) = (gstart[gi] as usize, gstart[gi + 1] as usize);
            let al = (gdesc[gi] >> 16) as usize;
            worst = worst.max(al.max(en - st - al).div_ceil(1 << lg));
            heavy.push(en - st);
            if ng < 64 {
                t_n += en - st;
            }
        }
        if ng < 64 {
            it_n += worst;
            g_n += ng;
        } else {
            it_w += worst * ng.div_ceil(512 >> lg);
        }
    }
    heavy.sort_unstable_by(|a, b| b.cmp(a));
    println!("VSEGSTAT narrow: gates={g_n} terms={t_n} serial_iters={it_n}; wide serial_iters={it_w}; heaviest gates {:?}", &heavy[..8]);
    depth
}

fn glue_profile() -> flock_prover::pcs::ligerito::LigeritoProfile {
    match env_or("GLUE_PROFILE", "fast").as_str() {
        "fast100" => flock_prover::pcs::ligerito::LigeritoProfile::Fast100,
        "fast" => Default::default(),
        p => panic!("GLUE_PROFILE {p}: fast | fast100"),
    }
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
    verify_ligerito(art.r1cs, &art.commitment, &art.proof, &lc, &art.pcs_params, &mut ch).map(|_| ()).map_err(|e| format!("{e:?}"))
}

fn tamper_rejected(art: &GpuArtifacts) -> bool {
    let lc = SparseMatrixCircuit::new(&art.r1cs.a_0, &art.r1cs.b_0).with_const_pin(art.r1cs.const_pin);
    let mut bad = art.proof.clone();
    bad.pcs_open.ligerito.final_proof.yr[0].lo ^= 1;
    let mut ch = FsChallenger::with_hash(DOMAIN, CUDA_HASH);
    let r1 = verify_ligerito(art.r1cs, &art.commitment, &bad, &lc, &art.pcs_params, &mut ch).is_err();
    let mut bad = art.proof.clone();
    bad.zerocheck.multilinear_rounds[0].0.hi ^= 1;
    let mut ch = FsChallenger::with_hash(DOMAIN, CUDA_HASH);
    let r2 = verify_ligerito(art.r1cs, &art.commitment, &bad, &lc, &art.pcs_params, &mut ch).is_err();
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
    let (mut hz, mut ha, mut hb, mut hzl) = (vec![F128 { lo: 0, hi: 0 }; len], vec![F128 { lo: 0, hi: 0 }; len], vec![F128 { lo: 0, hi: 0 }; len], vec![0u8; len * 16]);
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
    let art = gpu_prove_with(stmt((1, nbl), || unit_r1cs(&g, nbl)), &UNIT_CSC, 2, None);
    verify_art(&art).expect("device-witness proof must verify");
    println!("VCHECK proof verified m={m} prove_s={:.4}", art.prove_secs);
    assert!(tamper_rejected(&art), "proof tamper accepted");
    println!("VCHECK proof tampers rejected");
    let (x2, w2) = gen_rows(&g, n_vu, 20260925, true);
    upload_rows(&g, &x2, &w2, n_vu);
    let art = gpu_prove_with(stmt((1, nbl), || unit_r1cs(&g, nbl)), &UNIT_CSC, 2, None);
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
    let nbl: usize = std::env::var("GLUE_UNIT_NBL").map_or_else(|_| nbl_for(n_vu * g.upv), |s| s.parse().unwrap());
    assert!(1usize << nbl >= n_vu * g.upv);
    let m = 13 + nbl;
    if mode >= 2 {
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
    let unit = || gpu_prove_with(stmt((1, nbl), || unit_r1cs(&g, nbl)), &UNIT_CSC, mode, None);
    let b3 = || gpu_prove(b3_nbl, None);
    let launch = || assert_eq!(unsafe { flock_glue_unit_witness_launch(m as i32, 13) }, 0, "unit witness launch");
    assert!(mode != 3 || b3_nbl > 0, "mode 3 overlaps the unit witness with the BLAKE3 proof");
    // warm-up (arena, twiddles, matrices, zerocheck tables)
    if mode == 3 {
        launch();
        let _ = b3();
    }
    let a = unit();
    if b3_nbl > 0 && mode != 3 {
        let _ = b3();
    }
    match verify_art(&a) {
        Ok(()) => println!("VWARM unit verified"),
        Err(e) => println!("VWARM unit REJECTED: {e}"),
    }
    // one batch = GLUE_FLOCK_REPS full (unit, BLAKE3) proof pairs; flock-128-r2 = 2 reps under GLUE_PROFILE=fast100
    // (cost stand-in: both reps share the FS domain, so they are identical proofs; the unit witness is built once)
    let fr: usize = env_or("GLUE_FLOCK_REPS", "1").parse().unwrap();
    let mut e2e = Vec::new();
    let mut ffi = Vec::new();
    let mut pw = Vec::new();
    for rep in 0..reps {
        let t0 = Instant::now();
        let (mut arts, mut parse) = (Vec::new(), 0.0);
        if mode == 3 {
            launch();
        }
        for _ in 0..fr {
            if mode == 3 {
                arts.push(("b3", b3()));
                parse += LAST_HOST.lock().unwrap().1;
            }
            arts.push(("unit", unit()));
            parse += LAST_HOST.lock().unwrap().1;
            if mode != 3 && b3_nbl > 0 {
                arts.push(("b3", b3()));
                parse += LAST_HOST.lock().unwrap().1;
            }
        }
        let t_all = t0.elapsed().as_secs_f64();
        // prover wall: from the batch start until the last proof's bytes are back (host stream parse excluded)
        let prover = t_all - parse;
        pw.push(prover);
        let f: f64 = arts.iter().map(|(_, a)| a.prove_secs).sum();
        let mut vs = Vec::new();
        let mut all_ok = true;
        for (tag, a) in &arts {
            match verify_art(a) {
                Ok(()) => vs.push(format!("{tag}=ok")),
                Err(e) => {
                    all_ok = false;
                    vs.push(format!("{tag}=REJECTED {e}"));
                }
            }
        }
        let secs: Vec<String> = arts.iter().map(|(tag, a)| format!("{tag}:{:.4}", a.prove_secs)).collect();
        println!("VGLUE rep={rep} m={m} b3_nbl={b3_nbl} flock_reps={fr} ffi=[{}] ffi_sum={f:.4} prover_wall={prover:.4} call_e2e={t_all:.4} verify=[{}]",
            secs.join(" "), vs.join(" "));
        if !plant {
            assert!(all_ok, "a proof failed to verify");
        }
        e2e.push(t_all);
        ffi.push(f);
    }
    e2e.sort_by(|a, b| a.partial_cmp(b).unwrap());
    ffi.sort_by(|a, b| a.partial_cmp(b).unwrap());
    pw.sort_by(|a, b| a.partial_cmp(b).unwrap());
    println!("VSUMMARY pipe={} profile={} flock_reps={fr} mode={mode} n_vu={n_vu} m={m} b3_nbl={b3_nbl} reps={reps} ffi_sum_median={:.4} ffi_sum_min={:.4} prover_wall_median={:.4} call_e2e_median={:.4}",
        env_or("VU_NAME", "?"), env_or("GLUE_PROFILE", "fast"), ffi[reps / 2], ffi[0], pw[reps / 2], e2e[reps / 2]);
}
