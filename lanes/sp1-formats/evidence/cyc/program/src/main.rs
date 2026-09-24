//! Scratch guest: `format: u8 || n: u32 LE || x block || W block` -> every VU's public word (u32 LE) committed.
#![no_main]
sp1_zkvm::entrypoint!(main);

use veritor_zk_common::{nvfp4, tc_fp8, tc_hopper_bf16};

pub fn main() {
    println!("cycle-tracker-report-start: io");
    let input = sp1_zkvm::io::read_vec();
    println!("cycle-tracker-report-end: io");
    let format = input[0];
    let n = u32::from_le_bytes([input[1], input[2], input[3], input[4]]) as usize;
    let rb = match format {
        1 => tc_hopper_bf16::ROW_BYTES,
        2 | 3 => tc_fp8::K_VU,
        4 => nvfp4::ROW_BYTES,
        _ => panic!("format"),
    };
    let (x, w) = input[5..].split_at(n * rb);
    let mut out: Vec<u8> = Vec::with_capacity(4 * n);
    println!("cycle-tracker-report-start: vu");
    for i in 0..n {
        let (xr, wr) = (&x[i * rb..(i + 1) * rb], &w[i * rb..(i + 1) * rb]);
        let y = match format {
            1 => tc_hopper_bf16::vu_bytes(xr, wr).map(u32::from),
            2 => tc_fp8::vu_ada(xr, wr),
            3 => tc_fp8::vu_hopper(xr, wr),
            _ => nvfp4::vu(xr, wr),
        }
        .expect("outside the model");
        out.extend_from_slice(&y.to_le_bytes());
    }
    println!("cycle-tracker-report-end: vu");
    sp1_zkvm::io::commit_slice(&out);
    sp1_zkvm::syscalls::syscall_halt(0);
}
