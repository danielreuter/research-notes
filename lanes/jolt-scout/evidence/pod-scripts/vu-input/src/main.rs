//! jolt-scout: write the `vu_batch(rows, y, mode)` guest input exactly as jolt-sdk's host does (postcard of each
//! argument, concatenated), with the same synthetic rows and seeds as vu-k1536's host, for PR #1618's `profile`.
//! Usage: vu-input <B> <mode> <out-file>
#[path = "../../vu-k1536/guest/src/kernel.rs"]
mod kernel;

fn xorshift(s: &mut u64) -> u64 {
    *s ^= *s << 13;
    *s ^= *s >> 7;
    *s ^= *s << 17;
    *s
}

fn word(s: &mut u64) -> u64 {
    let r = xorshift(s);
    if r & 0xFF == 0 {
        return 0;
    }
    let sign = (r >> 8) & 1;
    let exp = 118 + (r >> 9) % 19;
    let man = (r >> 20) & 0x7F;
    (sign << 15) | (exp << 7) | man
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let (n, mode): (usize, u8) = (a[1].parse().unwrap(), a[2].parse().unwrap());
    let rw = kernel::ROW_WORDS;
    let mut s = (0x5eed_0000 + n as u64) | 1;
    let (mut rows, mut y) = (Vec::<u64>::with_capacity(n * 2 * rw), Vec::<u16>::with_capacity(n));
    while y.len() < n {
        let vu: Vec<u64> = (0..2 * rw)
            .map(|_| word(&mut s) | word(&mut s) << 16 | word(&mut s) << 32 | word(&mut s) << 48)
            .collect();
        if let Some(out) = kernel::check_vu(&vu[..rw], &vu[rw..]) {
            rows.extend_from_slice(&vu);
            y.push(out);
        }
    }
    let bytes = serde_bytes::ByteBuf::from(rows.iter().flat_map(|w| w.to_le_bytes()).collect::<Vec<u8>>());
    let mut out = postcard::to_stdvec(&bytes).unwrap();
    out.extend(postcard::to_stdvec(&y).unwrap());
    out.extend(postcard::to_stdvec(&mode).unwrap());
    std::fs::write(&a[3], &out).unwrap();
    println!("VU_INPUT B={n} mode={mode} bytes={}", out.len());
}
