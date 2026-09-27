"""Scale configurations for the algorithm registry.

A ``ModelConfig`` fixes the *architecture* (published dimensions where a real model is named); a
``Workload`` fixes how much data one accumulated weight version processes (tokens ``Q``, sequence length
``S``, population size, ...).  Algorithms are factories ``(ModelConfig, Workload) -> circuit``, so the
same algorithm can be instantiated at any scale.

Every named config records where its numbers come from (``source``).  Dimensions marked ``approx`` are
simplifications of the real architecture (e.g. DeepSeek's MLA attention is represented as GQA with the
same KV width); they affect operator shapes, not the analysis method.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace


@dataclass(frozen=True)
class ModelConfig:
    name: str
    layers: int
    d: int                      # residual width
    ffn: int                    # MLP hidden width (per expert for MoE)
    heads: int
    kv_heads: int
    head_dim: int
    vocab: int
    experts: int = 1            # routed experts per MoE layer (1 = dense)
    topk: int = 1               # active experts per token
    shared_experts: int = 0     # always-on experts (DeepSeek style), each of width ``ffn``
    dense_layers: int = 0       # leading dense layers in an otherwise-MoE stack
    elem_bytes: int = 2         # bytes per activation/weight element (BF16)
    source: str = ""
    notes: str = ""

    @property
    def attn_out(self) -> int:
        return self.heads * self.head_dim

    @property
    def kv_width(self) -> int:
        return self.kv_heads * self.head_dim

    # --- parameter counts (elements) -----------------------------------------------------------------
    def attn_params_per_layer(self) -> int:
        return self.d * self.attn_out * 2 + self.d * self.kv_width * 2

    def mlp_params_dense_layer(self) -> int:
        return 3 * self.d * self.ffn

    def mlp_params_moe_layer(self) -> int:
        return 3 * self.d * self.ffn * (self.experts + self.shared_experts) + self.d * self.experts

    def active_mlp_params_moe_layer(self) -> int:
        return 3 * self.d * self.ffn * (self.topk + self.shared_experts) + self.d * self.experts

    @property
    def moe_layers(self) -> int:
        return 0 if self.experts == 1 else self.layers - self.dense_layers

    def total_params(self) -> int:
        n = self.vocab * self.d * 2  # embedding + LM head (untied)
        n += self.layers * (self.attn_params_per_layer() + 2 * self.d)
        n += (self.layers - self.moe_layers) * self.mlp_params_dense_layer()
        n += self.moe_layers * self.mlp_params_moe_layer()
        return n

    def active_params(self) -> int:
        n = self.vocab * self.d  # LM head (embedding gather is not a multiply)
        n += self.layers * (self.attn_params_per_layer() + 2 * self.d)
        n += (self.layers - self.moe_layers) * self.mlp_params_dense_layer()
        n += self.moe_layers * self.active_mlp_params_moe_layer()
        return n

    def weight_bytes(self) -> int:
        return self.total_params() * self.elem_bytes


@dataclass(frozen=True)
class Workload:
    """How one accumulated weight version is used.

    ``tokens``: token positions processed per weight version (the reuse ``Q``); ``seq``: sequence length
    (``tokens`` must be a multiple of ``seq``); ``population``: ES population size; ``rank``: adapter rank
    for LoRA-style algorithms; ``adapted``: which projections carry adapters; ``local_steps``: chained
    optimiser steps inside one circuit (local SGD / DiLoCo); ``gen_tokens``: generated tokens per RL
    sequence (the remainder of ``seq`` is prompt)."""
    tokens: int
    seq: int
    population: int = 1
    rank: int = 16
    adapted: tuple[str, ...] = ("q", "k", "v", "o", "g", "u", "d")
    adapted_layers: int | None = None  # None = all layers
    local_steps: int = 1
    gen_tokens: int | None = None
    chunk: int = 16  # MAC chunk width in the IR (16 = tensor-core-shaped transition, 1 = scalar)

    @property
    def nseq(self) -> int:
        assert self.tokens % self.seq == 0, (self.tokens, self.seq)
        return self.tokens // self.seq


def _cfg(**kw) -> ModelConfig:
    return ModelConfig(**kw)


MODELS: dict[str, ModelConfig] = {
    # -- dense Llama-3 family (config.json dimensions) ---------------------------------------------------
    "llama3-1b": _cfg(name="llama3-1b", layers=16, d=2048, ffn=8192, heads=32, kv_heads=8, head_dim=64,
                      vocab=128256, source="meta-llama/Llama-3.2-1B config.json"),
    "llama3-8b": _cfg(name="llama3-8b", layers=32, d=4096, ffn=14336, heads=32, kv_heads=8, head_dim=128,
                      vocab=128256, source="meta-llama/Llama-3.1-8B config.json"),
    "llama3-70b": _cfg(name="llama3-70b", layers=80, d=8192, ffn=28672, heads=64, kv_heads=8, head_dim=128,
                       vocab=128256, source="meta-llama/Llama-3.1-70B config.json"),
    "llama3-405b": _cfg(name="llama3-405b", layers=126, d=16384, ffn=53248, heads=128, kv_heads=8, head_dim=128,
                        vocab=128256, source="meta-llama/Llama-3.1-405B config.json"),
    # -- mixture of experts --------------------------------------------------------------------------------
    "mixtral-8x7b": _cfg(name="mixtral-8x7b", layers=32, d=4096, ffn=14336, heads=32, kv_heads=8, head_dim=128,
                         vocab=32000, experts=8, topk=2, source="mistralai/Mixtral-8x7B-v0.1 config.json"),
    "deepseek-v3": _cfg(name="deepseek-v3", layers=61, d=7168, ffn=2048, heads=128, kv_heads=16, head_dim=128,
                        vocab=129280, experts=256, topk=8, shared_experts=1, dense_layers=3,
                        source="deepseek-ai/DeepSeek-V3 config.json",
                        notes="approx: MLA represented as GQA with 16 KV heads (kv width 2048); the 3 dense "
                              "layers use ffn 18432 in the real model, here the MoE width for uniformity"),
    "qwen3-235b-a22b": _cfg(name="qwen3-235b-a22b", layers=94, d=4096, ffn=1536, heads=64, kv_heads=4, head_dim=128,
                            vocab=151936, experts=128, topk=8, source="Qwen/Qwen3-235B-A22B config.json"),
    # -- tiny shapes for the exact solver and unit tests ---------------------------------------------------
    "tiny": _cfg(name="tiny", layers=1, d=4, ffn=4, heads=1, kv_heads=1, head_dim=4, vocab=8,
                 source="synthetic (exact-solver scale)"),
    "tiny2": _cfg(name="tiny2", layers=2, d=4, ffn=8, heads=2, kv_heads=1, head_dim=2, vocab=8,
                  source="synthetic (exact-solver scale)"),
    "small": _cfg(name="small", layers=2, d=64, ffn=128, heads=2, kv_heads=1, head_dim=32, vocab=256,
                  source="synthetic (smoke-test scale)"),
    "tiny-moe": _cfg(name="tiny-moe", layers=2, d=4, ffn=4, heads=1, kv_heads=1, head_dim=4, vocab=8, experts=4,
                     topk=2, shared_experts=1, dense_layers=1, source="synthetic (exact-solver scale)"),
    "small-moe": _cfg(name="small-moe", layers=2, d=64, ffn=64, heads=2, kv_heads=1, head_dim=32, vocab=256,
                      experts=8, topk=2, source="synthetic (smoke-test scale)"),
}


def model(name: str, **overrides) -> ModelConfig:
    return replace(MODELS[name], **overrides) if overrides else MODELS[name]


__all__ = ["ModelConfig", "Workload", "MODELS", "model"]
