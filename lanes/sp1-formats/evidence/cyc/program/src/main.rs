//! Scratch guest: `format: u8 || 3 zero bytes || n: u32 LE || x block || W block` -> every VU's public word (u32 LE)
//! committed.  The blocks start 8-byte aligned (SP1 aligns every `read_vec` buffer), as in the bare guest.
#![no_main]
sp1_zkvm::entrypoint!(main);

use veritor_zk_common::{nvfp4, tc_fp8, tc_hopper_bf16};

pub fn main() {
    println!("cycle-tracker-report-start: io");
    let input = sp1_zkvm::io::read_vec();
    println!("cycle-tracker-report-end: io");
    let format = input[0];
    let n = u32::from_le_bytes([input[4], input[5], input[6], input[7]]) as usize;
    let rb = match format {
        1 => tc_hopper_bf16::ROW_BYTES,
        2 | 3 => tc_fp8::K_VU,
        4 => nvfp4::ROW_BYTES,
        _ => panic!("format"),
    };
    let (x, w) = input[8..8 + 2 * n * rb].split_at(n * rb);
    // SAFETY: every bit pattern is a u64; misalignment is checked
    let (xh, xw, _) = unsafe { x.align_to::<u64>() };
    let (wh, ww, _) = unsafe { w.align_to::<u64>() };
    assert!(xh.is_empty() && wh.is_empty());
    let rw = rb / 8;
    let mut out: Vec<u8> = Vec::with_capacity(4 * n);
    println!("cycle-tracker-report-start: vu");
    for i in 0..n {
        let (xr, wr) = (&x[i * rb..(i + 1) * rb], &w[i * rb..(i + 1) * rb]);
        let y = match format {
            1 => tc_hopper_bf16::vu_words(&xw[i * rw..(i + 1) * rw], &ww[i * rw..(i + 1) * rw]).map(u32::from),
            2 => tc_fp8::vu_ada_views(xr, wr, &xw[i * rw..(i + 1) * rw], &ww[i * rw..(i + 1) * rw]),
            3 => tc_fp8::vu_hopper_views(xr, wr, &xw[i * rw..(i + 1) * rw], &ww[i * rw..(i + 1) * rw]),
            _ => nvfp4::vu(xr, wr),
        }
        .expect("outside the model");
        out.extend_from_slice(&y.to_le_bytes());
    }
    println!("cycle-tracker-report-end: vu");
    sp1_zkvm::io::commit_slice(&out);
    sp1_zkvm::syscalls::syscall_halt(0);
}
