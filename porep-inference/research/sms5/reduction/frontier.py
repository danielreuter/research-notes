#!/usr/bin/env python3
"""
Closed-form numbers quoted in reduction.md sections 1, 3 (Lemma 3) and Theorem 2.

  * frontier: bits the adversary must save for s/w in [0.90, 0.97] and for eps = 5 %
  * truncation saving log2 T + 2 and the online budget T_Delta per block per GPU
  * two-layer ("backwards") route of Lemma 3: saving 2 log2 T' - 2 delta - 3 with
    T' = T / C_LLL(delta), C_LLL from an L^2-style cost n^4 B^2 (bit ops) with
    n = w / delta, B = n w / 2 bits, one decode = 2 w^2 bit ops; crossover T where
    it beats truncation
  * max omega(N) for a w-bit N and the fibre bound 2^(4 + 2 omega) of Theorem 2
"""
import math

def primes_upto(n):
    s = bytearray([1]) * (n + 1); s[0] = s[1] = 0
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = bytearray(len(s[i * i::i]))
    return [i for i, v in enumerate(s) if v]

def max_omega(w):
    P, k = 1, 0
    for p in primes_upto(10 ** 5):
        if P * p >= 2 ** w: return k
        P *= p; k += 1

def decode_bitops(w): return 2 * w * w

def c_lll_decodes(w, delta):
    n = max(3, round(w / delta)); B = n * w // 2
    return n ** 4 * B ** 2 / decode_bitops(w), n

if __name__ == "__main__":
    for w in (2048, 3072):
        print(f"w = {w}: 5% = {0.05 * w:.0f} bits; s/w = 0.97 -> drop {0.03 * w:.0f}; 0.90 -> drop {0.10 * w:.0f}")
        for lgT in (13, 20, 30):
            print(f"   truncation at T = 2^{lgT}: saving {lgT + 2} bits, s/w = {1 - (lgT + 2) / w:.4f}")
    R = 4e9  # 2048-bit squarings per second per GPU (spec A2's 1e10 at 1279 bits, scaled)
    for D in (0.25e-3, 1e-3):
        for G in (1, 100):
            print(f"   Delta = {D * 1e3:.2f} ms, {G:3d} GPU(s): T per block = 2^{math.log2(R * D * G / 2 / 200):.1f}")
    w = 2048
    print("two-layer route (Lemma 3): delta, n, log2 C_LLL (decodes), crossover log2 T, saving at T=2^30")
    best = None
    for delta in (4, 8, 16, 32, 64, 128, 256, 341):
        C, n = c_lll_decodes(w, delta)
        cross = 2 * math.log2(C) + 2 * delta + 5
        sav30 = 2 * (30 - math.log2(C)) - 2 * delta - 3
        best = min(best, cross) if best else cross
        print(f"   delta = {delta:3d}  n = {n:3d}  log2 C = {math.log2(C):5.1f}  crossover 2^{cross:5.1f}  saving@2^30 = {sav30:7.1f}")
    print(f"   minimum crossover ~ 2^{best:.0f}")
    for w in (2048, 3072):
        k = max_omega(w)
        print(f"w = {w}: max omega(N) = {k}, fibre <= 2^{4 + 2 * k}, tag attacker needs s >= {4 + 2 * k + 128} bits = {(4 + 2 * k + 128) / w:.3f} w")
