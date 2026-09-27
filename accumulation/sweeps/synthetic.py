"""Sweeps-local synthetic architecture family (not in ``configs.py``): ~1.07e9 non-embedding parameters held (roughly)
fixed while ``d_model`` / ``layers`` / ``d_ff`` / ``heads`` vary, to see whether width, depth or ``P`` drives ``b_train``.
``vocab = 8192`` keeps the embedding + head (``2 V d``) a small, ``d``-dependent part of ``P`` (1.6 %-6 %).

``model_cfg(name)`` resolves a name in ``configs.MODELS`` or here.
"""

from __future__ import annotations

from accumulation.configs import MODELS, ModelConfig

V = 8192


def _syn(name, layers, d, ffn, heads, head_dim, notes) -> ModelConfig:
    return ModelConfig(name=name, layers=layers, d=d, ffn=ffn, heads=heads, kv_heads=heads, head_dim=head_dim, vocab=V,
                       source="synthetic (sweeps/synthetic.py)", notes=notes)


SYNTHETIC: dict[str, ModelConfig] = {
    # per-layer params = 4 d^2 (attention, MHA) + 3 d ffn (SwiGLU MLP); layers x per-layer ~ 1.07e9 unless noted
    "syn-base":        _syn("syn-base", 16, 2048, 8192, 16, 128, "1B-like reference: 16 x (16.8M attn + 50.3M mlp)"),
    "syn-wide":        _syn("syn-wide", 4, 4096, 16384, 32, 128, "2x width, 1/4 depth, same P: 4 x 268M"),
    "syn-deep":        _syn("syn-deep", 64, 1024, 4096, 8, 128, "1/2 width, 4x depth, same P: 64 x 16.8M"),
    "syn-ffn":         _syn("syn-ffn", 8, 2048, 19456, 16, 128, "MLP-heavy: 8 x (16.8M attn + 119.5M mlp) = 1.09e9"),
    "syn-attn":        _syn("syn-attn", 16, 2048, 2048, 48, 128, "attention-heavy (48 heads, AO = 3d): 16 x (50.3M attn + 12.6M mlp) = 1.0e9"),
    "syn-manyheads":   _syn("syn-manyheads", 16, 2048, 8192, 64, 32, "control: same shapes as syn-base, 64 heads of 32 (same MACs, same P)"),
}


def model_cfg(name: str) -> ModelConfig:
    if name in MODELS:
        return MODELS[name]
    if name in SYNTHETIC:
        return SYNTHETIC[name]
    raise KeyError(f"unknown model {name!r} (configs.MODELS or sweeps.synthetic.SYNTHETIC)")


def all_models() -> dict[str, ModelConfig]:
    return {**MODELS, **SYNTHETIC}
