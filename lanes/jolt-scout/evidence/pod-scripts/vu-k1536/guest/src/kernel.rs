//! The BF16 Ampere VU kernel, verbatim from verity backends/sp1/common/src/bare.rs lines 395-707 at 7fcedf47 (no_std: core only).
#![allow(dead_code)]
pub const K: usize = 1536;
pub const ROW_WORDS: usize = K / 4;

// --- the kernel ------------------------------------------------------------------------------------------------------

const L7F: u64 = 0x007F_007F_007F_007F;
const L80: u64 = 0x0080_0080_0080_0080;
/// Every lane's exponent field, in place.
const L7F80: u64 = 0x7F80_7F80_7F80_7F80;
/// Bit 15 of every lane: of `field << 7 + 0x80`, set iff the field is `0xFF` (a non-finite word); of
/// `field << 7 + 0x7F80`, set iff the field is non-zero (the implicit bit).
const L8000: u64 = 0x8000_8000_8000_8000;
/// Lanes 0 and 2 of a SWAR word, one byte each: two products per 64x64 -> 128 multiply.
const M02: u64 = 0x0000_00FF_0000_00FF;
/// [`M02`] at bit 10, for the multiplier: the products come out as `p << 10`, aligned for the adder.
const M02S: u64 = M02 << 10;
/// `p << 10` of a product of two 8-bit significands.
const M26: u64 = (1 << 26) - 1;
/// Exponents are biased by 252: a product's `max(ea, 1) + max(eb, 1) - 2` is its true exponent + 252.
const BIAS: i64 = 252;
/// The adder's exponent floor `-132`, biased.
const FLOOR: u64 = (-132 + BIAS) as u64;
/// The smallest normal exponent `-126`, biased.
const SUBNORMAL: u64 = (-126 + BIAS) as u64;
/// `tc_dot`'s saturation test `exp > 127`, biased.
const SATURATED: u64 = (127 + BIAS) as u64;

/// A group's result: `(-1)^neg * mag * 2^(e - BIAS - 23)`, `mag` on the 24-bit grid (`tc::Term`), `e` biased, `neg`
/// 0 or 1; `mag == 0` is `+0` with `e == 0`, so `e > SATURATED` is exactly `tc_dot`'s saturation test.
#[derive(Clone, Copy)]
struct Acc {
    neg: u64,
    e: u64,
    mag: u64,
}

const ZERO: Acc = Acc { neg: 0, e: 0, mag: 0 };

/// `BIT_LEN[i]` is the bit length of `i`.
static BIT_LEN: [u8; 256] = {
    let mut t = [0u8; 256];
    let mut i = 1;
    while i < 256 {
        t[i] = t[i >> 1] + 1;
        i += 1;
    }
    t
};

/// `SHIFT[i]` for `1 <= i = m >> 23 < 128`: `bit_length(m) - 24`, the truncating shift of `m` to 24 bits.
static SHIFT: [u8; 128] = {
    let mut t = [0u8; 128];
    let mut i = 1;
    while i < 128 {
        t[i] = BIT_LEN[i] - 1;
        i += 1;
    }
    t
};

/// Four products of a lane quadruple: significand products `<< 10`, the SWAR word of their biased exponents `<< 7`
/// (lane `j`, bits `7 ..= 15`, is product `j`'s), and the word whose bit `15 + 16 j` is product `j`'s sign.
#[inline(always)]
fn quad(x: u64, w: u64) -> ([u64; 4], u64, u64) {
    let ex = x & L7F80;
    let ew = w & L7F80;
    // 0x80 in the lanes whose exponent field is non-zero: the implicit bit
    let fx = ((ex + L7F80) & L8000) >> 8;
    let fw = ((ew + L7F80) & L8000) >> 8;
    let sx = (x & L7F) | fx;
    let sw = (w & L7F) | fw;
    // (max(e, 1) - 1) << 7 per operand, summed: at most 508 << 7 per lane, so no lane carries or borrows
    let g = ex + ew - (fx + fw);
    // low 64 bits: (p0 << 10) + (cross terms << 42), below 2^59, so the high 64 bits are exactly p2 << 10
    let t02 = (sx & M02) as u128 * ((sw << 10) & M02S) as u128;
    let t13 = ((sx >> 16) & M02) as u128 * ((sw >> 6) & M02S) as u128;
    ([t02 as u64 & M26, t13 as u64 & M26, (t02 >> 64) as u64, (t13 >> 64) as u64], g, x ^ w)
}

/// [`quad`] when every word of the quadruple is normal (exponent field `1 ..= 254`): each significand has its
/// implicit bit, so it is the word with bit 7 set, and the exponent word is `(ea + eb) << 7`, i.e. [`quad`]'s plus 2.
#[inline(always)]
fn quad_normal(x: u64, w: u64, ex: u64, ew: u64) -> ([u64; 4], u64, u64) {
    let (sx, sw) = (x | L80, w | L80);
    let t02 = (sx & M02) as u128 * ((sw << 10) & M02S) as u128;
    let t13 = ((sx >> 16) & M02) as u128 * ((sw >> 6) & M02S) as u128;
    ([t02 as u64 & M26, t13 as u64 & M26, (t02 >> 64) as u64, (t13 >> 64) as u64], ex + ew, x ^ w)
}

/// The four lanes of a [`quad`] exponent word (each below 2^9).
#[inline(always)]
fn lanes(g: u64) -> [u64; 4] {
    [(g >> 7) & 0x1FF, (g >> 23) & 0x1FF, (g >> 39) & 0x1FF, g >> 55]
}

/// Product `j`'s sign in a [`quad`] sign word.
#[inline(always)]
fn negative(s: u64, j: usize) -> bool {
    ((s << (48 - 16 * j)) as i64) < 0
}

/// The running maximum over a product: raised only by a non-zero product.  `e > mx` is rare once the accumulator
/// dominates, so it is the one branch on the common path: the zero test sits behind it, and `black_box` stops the
/// compiler from hoisting that test in front (two branches per product) or turning the update into a select.
#[inline(always)]
fn raise(mx: u64, e: u64, p: u64) -> u64 {
    if e > mx && core::hint::black_box(p) != 0 {
        e
    } else {
        mx
    }
}

/// Adds a product truncated to the group's maximum exponent `mx`: `p << 10 >> d` is zero from d = 26 (and a zero
/// product adds nothing at any d, so the wrapped `d` of a zero product above the maximum is harmless).
#[inline(always)]
fn add_term(total: i64, p: u64, e: u64, neg: bool, mx: u64) -> i64 {
    let d = mx.wrapping_sub(e);
    if d < 26 {
        let v = (p >> d) as i64;
        if neg {
            total - v
        } else {
            total + v
        }
    } else {
        total
    }
}

/// `tc::group_sum` of the accumulator and eight products (width 25, floor -132), on the terms as they come out of
/// [`quad`]: the largest exponent of a non-zero term, each term's `magnitude << 1` truncated to it, the exact sum,
/// truncating normalisation to 25 bits, denormalisation below -126, and the truncation back to 24 bits.
#[inline(always)]
fn group(acc: Acc, x0: u64, x1: u64, w0: u64, w1: u64) -> Acc {
    let (pa, ga, sa) = quad(x0, w0);
    let (pb, gb, sb) = quad(x1, w1);
    let (ea, eb) = (lanes(ga), lanes(gb));
    // a non-zero accumulator has exponent >= -126, above the floor
    let mut mx = if acc.mag != 0 { acc.e } else { FLOOR };
    for j in 0..4 {
        mx = raise(mx, ea[j], pa[j]);
    }
    for j in 0..4 {
        mx = raise(mx, eb[j], pb[j]);
    }
    let mut total: i64 = 0;
    if acc.mag != 0 {
        let d = mx - acc.e;
        if d < 26 {
            let v = ((acc.mag + acc.mag) >> d) as i64;
            total = if acc.neg != 0 { -v } else { v };
        }
    }
    for j in 0..4 {
        total = add_term(total, pa[j], ea[j], negative(sa, j), mx);
    }
    for j in 0..4 {
        total = add_term(total, pb[j], eb[j], negative(sb, j), mx);
    }
    normalize(total, mx)
}

/// [`group`] on sixteen normal words (94.6% of the frozen set's groups): no product is zero, so the maximum is one
/// rare branch per product (`black_box` keeps it a branch: the select the compiler would make costs two moves more
/// per product), and the decode is [`quad_normal`]'s.  Exponents are carried plus 2 up to the normalisation; the
/// shifts `mx - e` are the same.
#[inline(always)]
fn group_normal(acc: Acc, x0: u64, x1: u64, w0: u64, w1: u64, e: [u64; 4]) -> Acc {
    let (pa, ga, sa) = quad_normal(x0, w0, e[0], e[2]);
    let (pb, gb, sb) = quad_normal(x1, w1, e[1], e[3]);
    let (ea, eb) = (lanes(ga), lanes(gb));
    let mut mx = (if acc.mag != 0 { acc.e } else { FLOOR }) + 2;
    for j in 0..4 {
        if ea[j] > mx {
            mx = core::hint::black_box(ea[j]);
        }
    }
    for j in 0..4 {
        if eb[j] > mx {
            mx = core::hint::black_box(eb[j]);
        }
    }
    let mut total: i64 = 0;
    if acc.mag != 0 {
        let d = mx - acc.e - 2;
        if d < 26 {
            let v = ((acc.mag + acc.mag) >> d) as i64;
            total = if acc.neg != 0 { -v } else { v };
        }
    }
    for j in 0..4 {
        total = add_term(total, pa[j], ea[j], negative(sa, j), mx);
    }
    for j in 0..4 {
        total = add_term(total, pb[j], eb[j], negative(sb, j), mx);
    }
    normalize(total, mx - 2)
}

/// One group of the chain, or `None` where one of its sixteen words is non-finite.  Bit 15 of a lane of
/// `field << 7 + 0x7F80` is set iff the field is non-zero, of `field << 7 + 0x80` iff it is `0xFF`: all-normal groups
/// take [`group_normal`], the rest (zeros, subnormals) [`group`].
#[inline(always)]
fn group_checked(acc: Acc, x0: u64, x1: u64, w0: u64, w1: u64) -> Option<Acc> {
    let e = [x0 & L7F80, x1 & L7F80, w0 & L7F80, w1 & L7F80];
    let nonzero = (e[0] + L7F80) & (e[1] + L7F80) & (e[2] + L7F80) & (e[3] + L7F80);
    let infinite = (e[0] + L80) | (e[1] + L80) | (e[2] + L80) | (e[3] + L80);
    if (!nonzero | infinite) & L8000 == 0 {
        Some(group_normal(acc, x0, x1, w0, w1, e))
    } else if infinite & L8000 == 0 {
        Some(group(acc, x0, x1, w0, w1))
    } else {
        None
    }
}

/// `group_sum`'s tail on the biased maximum exponent `mx`: `|total| < 9 * 2^26`, so the bit length is at most 30.  The
/// usual sum is at least 2^23 and its exponent normal: then the truncation to 24 bits is one right shift by
/// `bit_length - 24` and the exponent is `mx + bit_length - 25`.  Everything else is [`normalize_slow`]'s.
#[inline(always)]
fn normalize(total: i64, mx: u64) -> Acc {
    let m = total.unsigned_abs();
    let top = m >> 23;
    if top != 0 {
        let shift = SHIFT[top as usize & 127] as u64;
        let e = mx + shift - 1;
        if e >= SUBNORMAL {
            return Acc { neg: (total < 0) as u64, e, mag: m >> shift };
        }
    }
    let (e, mag) = normalize_slow(total, mx);
    Acc { neg: (total < 0 && mag != 0) as u64, e, mag }
}

/// [`normalize`] in general, as `(e, mag)` (two registers, so the accumulator never goes through memory): normalising
/// to 25 bits, denormalising below -126 and truncating to 24 bits are three truncating shifts of one non-negative
/// integer, so they are one shift by their sum (a left shift where the sum is negative, exact).
#[cold]
#[inline(never)]
fn normalize_slow(total: i64, mx: u64) -> (u64, u64) {
    if total == 0 {
        return (0, 0);
    }
    let m = total.unsigned_abs();
    let (mut v, mut bits) = (m, 0u64);
    if v >> 16 != 0 {
        v >>= 16;
        bits += 16;
    }
    if v >> 8 != 0 {
        v >>= 8;
        bits += 8;
    }
    let bits = bits + BIT_LEN[v as usize & 255] as u64;
    // mx >= FLOOR = 120, so this does not wrap
    let e = mx + bits - 25;
    let (e, shift) = if e >= SUBNORMAL { (e, bits as i64 - 24) } else { (SUBNORMAL, bits as i64 - 24 + (SUBNORMAL - e) as i64) };
    let mag = if shift >= 0 { m >> shift } else { m << -shift };
    if mag == 0 {
        return (0, 0);
    }
    (e, mag)
}

/// `f32_to_bf16(pack_fp32(acc))` for a finite result.
fn to_bf16(acc: Acc) -> u16 {
    if acc.mag == 0 {
        return 0;
    }
    let mut field = acc.e as i64 - BIAS + 127;
    if acc.mag & (1 << 23) == 0 {
        field -= 1;
    }
    let bits = (acc.neg << 31) | ((field as u64) << 23) | (acc.mag & 0x7F_FFFF);
    (((bits + 0x7FFF + ((bits >> 16) & 1)) >> 16) & 0xFFFF) as u16
}

/// The BF16 infinity of a sign (the cast of the FP32 infinity a saturating last step returns).
fn infinity(neg: u64) -> u16 {
    0x7F80 | ((neg as u16) << 15)
}

/// One VU: the output word of the chain on an x row and a W row given as [`ROW_WORDS`] u64 words each (word `k` of
/// the row is bits `16 (k % 4) ..` of u64 `k / 4`), or `None` where the chain rejects.  Words `0..1528` must all be
/// finite (every one is examined before any valid output); words `1528..1536` only when the last step's first group
/// does not saturate.  A saturation before the last step rejects.
pub fn check_vu(x: &[u64], w: &[u64]) -> Option<u16> {
    let x: &[u64; ROW_WORDS] = x.try_into().ok()?;
    let w: &[u64; ROW_WORDS] = w.try_into().ok()?;
    let mut acc = ZERO;
    // every outcome before the last step is a rejection, so a non-finite word and a saturation may reject in either
    // order; in the last step the first group's words are examined before its saturation, the second group's only
    // after the first did not saturate
    for step in 0..K / 16 - 1 {
        let i = 4 * step;
        acc = group_checked(acc, x[i], x[i + 1], w[i], w[i + 1])?;
        if acc.e > SATURATED {
            return None;
        }
        acc = group_checked(acc, x[i + 2], x[i + 3], w[i + 2], w[i + 3])?;
        if acc.e > SATURATED {
            return None;
        }
    }
    let i = ROW_WORDS - 4;
    acc = group_checked(acc, x[i], x[i + 1], w[i], w[i + 1])?;
    if acc.e > SATURATED {
        return Some(infinity(acc.neg));
    }
    acc = group_checked(acc, x[i + 2], x[i + 3], w[i + 2], w[i + 3])?;
    if acc.e > SATURATED {
        return Some(infinity(acc.neg));
    }
    Some(to_bf16(acc))
}
