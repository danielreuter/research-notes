"""red-team-flock-3: adversarial AttentionHead_v3{T, D=64, BN=128} instances (flat leaves q[64] | k[T*64] | v[T*64], bf16 words).

Categories: typical, extreme_scores (scores near and past the f32 range: saturated QK dots), nan_inf (sprinkled NaN / inf in
q, k, v), all_neg_inf (every score -inf: the all-masked row), subnormal (subnormal and tiny q, k, v: FTZ in the tail), one_hot
(one dominant key; tied maxima), v_extreme (max-magnitude V: saturated P.V accumulators, inf * 0 rescales), zeros (zero and
-0 operands), uniform_bits (every word uniform over 16 bits).
"""
import numpy as np

D = 64
CATEGORIES = ("typical", "extreme_scores", "nan_inf", "all_neg_inf", "subnormal", "one_hot", "v_extreme", "zeros", "uniform_bits")


def bf16(x):
    """float32 array -> bf16 words (round to nearest even), NaN kept as 0x7FC0."""
    u = np.asarray(x, dtype=np.float32).view(np.uint32).astype(np.uint64)
    nan = ((u & 0x7F800000) == 0x7F800000) & ((u & 0x7FFFFF) != 0)
    r = ((u + 0x7FFF + ((u >> 16) & 1)) >> 16) & 0xFFFF
    return np.where(nan, 0x7FC0, r).astype(np.uint64)


def _words(rng, shape, lo_exp, hi_exp):
    s = rng.integers(0, 2, shape, dtype=np.uint64) << 15
    e = rng.integers(lo_exp, hi_exp + 1, shape, dtype=np.uint64) << 7
    m = rng.integers(0, 128, shape, dtype=np.uint64)
    return s | e | m


SPECIAL = np.array([0x7F80, 0xFF80, 0x7FC0, 0xFFC0, 0x7F81, 0xFFFF, 0x7FA0], dtype=np.uint64)


def instances(T, n, seed, cat):
    rng = np.random.default_rng([seed, T, CATEGORIES.index(cat)])
    q = np.empty((n, D), dtype=np.uint64); k = np.empty((n, T, D), dtype=np.uint64); v = np.empty((n, T, D), dtype=np.uint64)
    for i in range(n):
        if cat == "typical":
            q[i] = bf16(rng.normal(0, 1.5, D)); k[i] = bf16(rng.normal(0, 1.5, (T, D))); v[i] = bf16(rng.normal(0, 0.5, (T, D)))
        elif cat == "extreme_scores":
            # scores around 2^(2e-...) with e per instance: from exp2 underflow to QK-dot saturation
            e = int(rng.integers(127 + 10, 127 + 66))
            q[i] = _words(rng, D, e - 3, e); k[i] = _words(rng, (T, D), e - 3, e); v[i] = bf16(rng.normal(0, 1, (T, D)))
            if i % 3 == 0:   # one key's score much larger than the rest
                k[i][rng.integers(0, T)] = q[i] ^ 0   # s = |q|^2 > 0, largest
        elif cat == "nan_inf":
            q[i] = bf16(rng.normal(0, 1.5, D)); k[i] = bf16(rng.normal(0, 1.5, (T, D))); v[i] = bf16(rng.normal(0, 0.5, (T, D)))
            for arr in (q[i], k[i].reshape(-1), v[i].reshape(-1)):
                m = rng.random(arr.shape) < (0.02 if arr.size > D else 0.03)
                arr[m] = rng.choice(SPECIAL, int(m.sum()))
            if i % 4 == 0:
                k[i][rng.integers(0, T)][rng.integers(0, D)] = 0x7FC0          # one NaN score
            if i % 4 == 1:
                v[i][rng.integers(0, T)][rng.integers(0, D)] = 0x7F80          # an inf value
        elif cat == "all_neg_inf":
            q[i] = bf16(rng.normal(0, 1, D)); k[i] = bf16(np.abs(rng.normal(0, 1, (T, D))) + 0.1); v[i] = bf16(rng.normal(0, 1, (T, D)))
            j = int(rng.integers(0, D))
            q[i][j] = 0xFF80 if i % 2 == 0 else 0x7F80                        # -inf (or +inf)
            k[i][:, j] = bf16(np.abs(rng.normal(0, 1, T)) + 0.5) | (0 if i % 2 == 0 else 0x8000)   # the same-sign partner: every score -inf
        elif cat == "subnormal":
            q[i] = _words(rng, D, 0, 3); k[i] = _words(rng, (T, D), 0, 3); v[i] = _words(rng, (T, D), 0, 2)
            if i % 2:
                q[i] = _words(rng, D, 60, 64); k[i] = _words(rng, (T, D), 0, 1)   # products near the 2^-132 floor
        elif cat == "one_hot":
            q[i] = bf16(rng.normal(0, 1, D)); k[i] = bf16(rng.normal(0, 0.05, (T, D))); v[i] = bf16(rng.normal(0, 1, (T, D)))
            hot = rng.choice(T, size=min(T, 1 + i % 3), replace=False)     # 1, 2 or 3 identical keys: tied maxima
            qf = (np.asarray(q[i], dtype=np.uint32) << 16).view(np.float32)
            for h in hot:
                k[i][h] = bf16(qf * np.float32((1.0, 8.0, 64.0)[i % 3]))      # the others' p from 2^-12 down to exact underflow
        elif cat == "v_extreme":
            q[i] = bf16(rng.normal(0, 1, D)); k[i] = bf16(rng.normal(0, 1, (T, D)))
            v[i] = np.where(rng.random((T, D)) < 0.5, 0x7F7F, 0xFF7F).astype(np.uint64)
            if i % 2:
                v[i] = np.full((T, D), 0x7F7F, dtype=np.uint64)
        elif cat == "zeros":
            q[i] = np.where(rng.random(D) < 0.5, 0x0000, 0x8000); k[i] = bf16(rng.normal(0, 1, (T, D)))
            v[i] = np.where(rng.random((T, D)) < 0.5, 0x0000, 0x8000)
            if i % 2:
                q[i] = bf16(rng.normal(0, 1, D)); k[i] = np.where(rng.random((T, D)) < 0.5, 0x0000, 0x8000)
        elif cat == "uniform_bits":
            q[i] = rng.integers(0, 1 << 16, D, dtype=np.uint64); k[i] = rng.integers(0, 1 << 16, (T, D), dtype=np.uint64)
            v[i] = rng.integers(0, 1 << 16, (T, D), dtype=np.uint64)
        else:
            raise ValueError(cat)
    return np.concatenate([q, k.reshape(n, -1), v.reshape(n, -1)], axis=1).astype(np.uint64)
