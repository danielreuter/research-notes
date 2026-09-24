//! Scratch: execute (or prove with `prove`) the first N VUs of an sp1-format-instances/v1 file; check every committed y.
//!     sp1f-cyc-script FILE N [prove]
use std::time::Instant;

use sp1_sdk::prelude::*;
use sp1_sdk::ProverClient;

const ELF: Elf = include_elf!("sp1f-cyc-program");

#[tokio::main]
async fn main() {
    let args: Vec<String> = std::env::args().collect();
    let data = std::fs::read(&args[1]).unwrap();
    let n: usize = args[2].parse().unwrap();
    let prove = args.get(3).map(|s| s == "prove").unwrap_or(false);
    assert_eq!(&data[..8], b"VYSP1FI\x01");
    let hl = u32::from_le_bytes(data[8..12].try_into().unwrap()) as usize;
    let h: serde_json::Value = serde_json::from_slice(&data[12..12 + hl]).unwrap();
    let (total, rb, yb) = (h["n"].as_u64().unwrap() as usize, h["row_bytes"].as_u64().unwrap() as usize, h["y_bytes"].as_u64().unwrap() as usize);
    let o = 12 + hl;
    let (x, w, y) = (&data[o..o + total * rb], &data[o + total * rb..o + 2 * total * rb], &data[o + 2 * total * rb..]);
    let format = h["format"].as_str().unwrap().to_string();
    let id: u8 = match format.as_str() { "bf16-hopper" => 1, "fp8-ada" => 2, "fp8-hopper" => 3, "fp4-nvf4" => 4, _ => panic!() };
    let mut input = vec![id, 0, 0, 0];
    input.extend_from_slice(&(n as u32).to_le_bytes());
    input.extend_from_slice(&x[..n * rb]);
    input.extend_from_slice(&w[..n * rb]);
    let mut stdin = SP1Stdin::new();
    stdin.write_vec(input);
    let check = |pv: &[u8]| -> usize {
        (0..n).filter(|&i| {
            let mut e = [0u8; 4];
            e[..yb].copy_from_slice(&y[i * yb..(i + 1) * yb]);
            pv[4 * i..4 * i + 4] == e
        }).count()
    };
    let t = Instant::now();
    let (pv, report) = if prove {
        let client = ProverClient::from_env().await;
        let r = client.execute(ELF, stdin.clone()).await.unwrap();
        let ts = Instant::now();
        let pk = client.setup(ELF).await.unwrap();
        let setup_s = ts.elapsed().as_secs_f64();
        let tp = Instant::now();
        let proof = client.prove(&pk, stdin).core().await.unwrap();
        let prove_s = tp.elapsed().as_secs_f64();
        let tv = Instant::now();
        client.verify(&proof, pk.verifying_key(), None).unwrap();
        let verify_s = tv.elapsed().as_secs_f64();
        println!("{}", serde_json::json!({"setup_s": setup_s, "prove_s": prove_s, "verify_s": verify_s}));
        r
    } else {
        let client = ProverClient::builder().mock().build().await;
        client.execute(ELF, stdin).await.unwrap()
    };
    let secs = t.elapsed().as_secs_f64();
    let cycles = report.total_instruction_count();
    let tracker: std::collections::BTreeMap<String, u64> = report.cycle_tracker.iter().map(|(k, v)| (k.clone(), *v)).collect();
    println!("{}", serde_json::json!({
        "format": format, "n": n, "exit_code": report.exit_code, "total_cycles": cycles,
        "cycles_per_vu": cycles as f64 / n as f64, "tracker": tracker, "y_match": check(pv.as_slice()), "seconds": secs,
    }));
}
