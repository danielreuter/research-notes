"""Registry of training/inference algorithms as Verity IR circuit factories.

An *algorithm* is a factory ``(ModelConfig, Workload) -> root composite`` plus a *role* for every root
parameter.  The role is what makes the circuit an object of accumulation analysis:

======================  ==================================================================================
role                    meaning
======================  ==================================================================================
``fixed``               prescribed input fixed independently of this evaluation (registered weights, the
                        constant ``ids`` vector, hash counters).  Free at every RU boundary.
``accumulated``         the changing model state (weights produced by earlier training).  Every RU that
                        uses it must receive it as runtime input; its bytes are the state-loading floor ``P``.
``carried``             non-fixed state that is *not declared* as model weights (an activation-carried
                        adapter, a "context" that is really a parameter).  Charged exactly like
                        ``accumulated`` by the input accounting -- that is the point of the red team.
``token``               token ids / targets / advantages (4 bytes each, paid once).
``seed``                small non-fixed inputs (ES seeds, learning rate, sigma).
======================  ==================================================================================

Every factory is built from the composites in :mod:`accumulation.algorithms.transformer` and
:mod:`accumulation.ir.blocks`; the root body is ordinary explicit dataflow, so the op-graph extractor sees
exactly the matmuls the algorithm performs.  Statics (dimensions, tokens, population, rank, ...) come from
the config objects, so the same factory instantiates a 4-dimensional toy and a 405B model.

Usage::

    from accumulation.algorithms.registry import ALGORITHMS, build
    prog = build("pretrain-dense", model("llama3-8b"), Workload(tokens=4096, seq=32))
    prog.program      # verity_ir.Program
    prog.roles        # {"Wq": "accumulated", "toks": "token", ...}
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from verity_ir import Array, Program, Tuple, bind
from verity_ir.defs import CompositeDefinition
from verity_ir.refs import Coll, concat, tuple_of

from accumulation.configs import ModelConfig, Workload
from accumulation.ir import blocks as K
from accumulation.ir import prims as P
from accumulation.ir.blocks import transpose
from accumulation.ir.prims import V16, V32
from accumulation.algorithms import transformer as T

W = lambda n, k: Array(n, Array(k, V16))  # noqa: E731  out-major weight matrix type


# ---------------------------------------------------------------------------------------------------------
# registry plumbing
# ---------------------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Algorithm:
    """One registered algorithm family."""
    name: str
    family: str
    summary: str
    build: Callable[[ModelConfig, Workload], "BuiltProgram"] = field(repr=False)
    supports: Callable[[ModelConfig, Workload], str | None] = field(repr=False, default=lambda c, w: None)
    simplifications: tuple[str, ...] = ()


@dataclass
class BuiltProgram:
    """A lowered program together with the analysis metadata the factory knows."""
    algorithm: str
    model: ModelConfig
    workload: Workload
    program: Program
    roles: dict[str, str]
    param_names: tuple[str, ...]
    notes: dict = field(default_factory=dict)

    def state_bytes(self) -> int:
        """Bytes of ``accumulated``/``carried`` root parameters (one copy = the state-loading floor P)."""
        tot = 0
        params, _ = self.program.fn.signature()
        for name, t in params:
            if self.roles.get(name) in ("accumulated", "carried"):
                tot += t.leaves * (t.homogeneous_width() or 16) // 8
        return tot

    def param_bytes(self, role: str) -> int:
        tot = 0
        params, _ = self.program.fn.signature()
        for name, t in params:
            if self.roles.get(name) == role:
                tot += t.leaves * (t.homogeneous_width() or 16) // 8
        return tot


ALGORITHMS: dict[str, Algorithm] = {}


def algorithm(name: str, family: str, summary: str, simplifications: tuple[str, ...] = (),
              supports: Callable[[ModelConfig, Workload], str | None] | None = None):
    """Decorator registering ``fn(cfg, wl) -> (params, roles, body)`` as an algorithm factory.

    ``params`` is the root signature ``((name, type), ...)``, ``roles`` maps names to roles, and
    ``body(B, *args) -> Coll`` builds the root dataflow."""

    def deco(fn):
        def build(cfg: ModelConfig, wl: Workload) -> BuiltProgram:
            why = supports(cfg, wl) if supports else None
            if why:
                raise ValueError(f"{name} does not support {cfg.name}/{wl}: {why}")
            params, roles, body, ret, notes = fn(cfg, wl)
            defn = CompositeDefinition(f"Acc[{name}]", 1, (), lambda S: (params, ret), lambda B, S, *a: body(B, *a),
                                       doc=summary, register=False)
            prog = Program(bind(defn))
            return BuiltProgram(name, cfg, wl, prog, roles, tuple(n for n, _ in params), notes)

        ALGORITHMS[name] = Algorithm(name, family, summary, build, supports or (lambda c, w: None), simplifications)
        return fn

    return deco


def build(name: str, cfg: ModelConfig, wl: Workload) -> BuiltProgram:
    return ALGORITHMS[name].build(cfg, wl)


# ---------------------------------------------------------------------------------------------------------
# shared pieces
# ---------------------------------------------------------------------------------------------------------

def _dense_names() -> tuple[str, ...]:
    return ("g1", "Wq", "Wk", "Wv", "Wo", "g2", "Wg", "Wu", "Wd")


def _layer_types(cfg: ModelConfig, L: int) -> dict[str, Array]:
    D, F, AO, KW = cfg.d, cfg.ffn, cfg.attn_out, cfg.kv_width
    per = {"g1": Array(D, V16), "Wq": W(AO, D), "Wk": W(KW, D), "Wv": W(KW, D), "Wo": W(D, AO), "g2": Array(D, V16),
           "Wg": W(F, D), "Wu": W(F, D), "Wd": W(D, F)}
    return {k: Array(L, t) for k, t in per.items()}


def _head_types(cfg: ModelConfig) -> list[tuple[str, Array]]:
    return [("tableT", W(cfg.d, cfg.vocab)), ("gf", Array(cfg.d, V16)), ("Wh", W(cfg.vocab, cfg.d))]


def _block_statics(cfg: ModelConfig, wl: Workload, Q: int) -> dict:
    return dict(Q=Q, S=wl.seq, D=cfg.d, FF=cfg.ffn, NH=cfg.heads, KVH=cfg.kv_heads, DH=cfg.head_dim, CH=wl.chunk)


def _mm(M, N, Kd, CH):
    return T._mm(M, N, Kd, CH)


def _mmT(M, N, Kd, CH):
    return T._mmT(M, N, Kd, CH)


def _stack(parts: list[Coll], L: int) -> Coll:
    """``L`` equally-typed collections -> ``Array<L, T>`` (references only)."""
    return Coll(Array(L, parts[0].type), concat([p.refs for p in parts]))


def _embed(B, cfg, wl, Q, toks, tableT):
    return B.call(bind(K.EmbedBatch, Q=Q, V=cfg.vocab, D=cfg.d), toks, tableT)


def _dense_forward(B, cfg, wl, Q, layers, toks, tableT, weights: dict[str, Coll], gf, Wh):
    """embedding -> ``layers`` dense blocks -> final norm -> logits.  Returns (layer_inputs, xn, logits)."""
    x = _embed(B, cfg, wl, Q, toks, tableT)
    xs = []
    st = _block_statics(cfg, wl, Q)
    for l in range(layers):
        xs.append(x)
        x = B.call(bind(T.Block, **st), x, *[weights[k][l] for k in _dense_names()])
    xn = B.call(bind(K.RmsNormBatch, Q=Q, K=cfg.d), x, gf)
    logits = B.call(_mm(Q, cfg.vocab, cfg.d, wl.chunk), xn, Wh)
    return xs, xn, logits


def _head_backward(B, cfg, wl, Q, xn, logits, targets, ids, gf, Wh, adv: Coll | None = None):
    """loss gradient at the logits (optionally advantage-scaled) and its backward through the LM head and
    final norm gain.  Returns (dx, dWh, dgf)."""
    dl = B.call(bind(K.LossGradBatch, Q=Q, V=cfg.vocab), logits, targets, ids)
    if adv is not None:
        dl = B.call(bind(K.RowScaleBatch, Q=Q, K=cfg.vocab), dl, adv)
    dxn = B.call(_mm(Q, cfg.d, cfg.vocab, wl.chunk), dl, transpose(Wh))                # dgrad through the head
    dWh = B.call(_mmT(cfg.vocab, cfg.d, Q, wl.chunk), dl, xn)     # wgrad of the head
    dgf = B.call(bind(K.ColSumBatch, Q=Q, K=cfg.d), B.call(bind(K.MulBatch, Q=Q, K=cfg.d), dxn, xn))
    dx = B.call(bind(K.GainBatch, Q=Q, K=cfg.d), dxn, gf)
    return dx, dWh, dgf


def _dense_backward(B, cfg, wl, Q, layers, xs, weights, dx, lowest: int = 0):
    """``BlockBwd`` from the top layer down to ``lowest``; returns per-layer gradient dicts (top first)."""
    st = _block_statics(cfg, wl, Q)
    grads = {}
    for l in reversed(range(lowest, layers)):
        out = B.call(bind(T.BlockBwd, **st), xs[l], *[weights[k][l] for k in _dense_names()], dx)
        dx = out[0]
        grads[l] = {k: out[i + 1] for i, k in enumerate(_dense_names())}
    return dx, grads


def _sgd_all(B, weights: dict[str, Coll], grads: dict[int, dict[str, Coll]], layers: int, lr, names) -> dict[str, Coll]:
    """apply ``W - lr*G`` to every layer's tensors; layers without gradients pass through unchanged."""
    new = {}
    for k in names:
        parts = []
        for l in range(layers):
            if l in grads:
                parts.append(_sgd(B, weights[k][l], grads[l][k], lr))
            else:
                parts.append(weights[k][l])
        new[k] = _stack(parts, layers)
    return new


def _sgd(B, Wc: Coll, G: Coll, lr) -> Coll:
    t = Wc.type
    if isinstance(t.elem, Array) and isinstance(t.elem.elem, Array):   # per-expert stacks: flatten to a matrix
        flat = Array(t.n * t.elem.n, t.elem.elem)
        return _sgd(B, Wc.reshape(flat), G.reshape(flat), lr).reshape(t)
    if isinstance(t.elem, Array):
        return B.call(bind(K.SgdUpdate, N=t.n, K=t.elem.n), Wc, G, lr)
    return B.call(bind(K.SgdUpdate, N=1, K=t.n), Wc.reshape(Array(1, t)), G.reshape(Array(1, t)), lr).reshape(t)


def _base_params(cfg: ModelConfig, wl: Workload, Q: int, layers: int, with_targets: bool):
    params = [("toks", Array(Q, V32))]
    if with_targets:
        params.append(("targets", Array(Q, V32)))
    params += _head_types(cfg)
    params += list(_layer_types(cfg, layers).items())
    params.append(("ids", Array(cfg.vocab, V32)))
    return params


def _roles(params, default: str, **overrides) -> dict[str, str]:
    r = {n: default for n, _ in params}
    r.update({"toks": "token", "targets": "token", "ids": "fixed", "lr": "seed", "adv": "token", "sigma": "seed",
              "seeds": "seed", "ctrs": "fixed"})
    r.update({n: "fixed" for n, _ in params if n.startswith("ctr_")})  # ES counters are fixed constants
    r.update(overrides)
    return {n: r[n] for n, _ in params}


def _dense_only(cfg: ModelConfig, wl: Workload) -> str | None:
    if cfg.experts != 1:
        return "dense-only factory (use the -moe variant)"
    if wl.tokens % wl.seq:
        return "tokens must be a multiple of seq"
    return None


def _moe_only(cfg: ModelConfig, wl: Workload) -> str | None:
    if cfg.experts == 1:
        return "MoE-only factory"
    if wl.tokens % wl.seq or wl.tokens % cfg.experts:
        return "tokens must be a multiple of seq and of the expert count"
    return None


def _split_dense(field: str):
    """``supports`` for factories that split the tokens into ``wl.<field>`` equal chunks of whole sequences
    (local SGD steps, ES population members)."""
    def check(cfg: ModelConfig, wl: Workload) -> str | None:
        why = _dense_only(cfg, wl)
        if why:
            return why
        n = getattr(wl, field)
        if wl.tokens % n or (wl.tokens // n) % wl.seq:
            return f"tokens must be a multiple of {field} x seq"
        return None
    return check


# ---------------------------------------------------------------------------------------------------------
# inference
# ---------------------------------------------------------------------------------------------------------

@algorithm("inference-dense", "inference",
           "dense forward pass with registered (fixed) weights; the adversary-favourable baseline: no "
           "accumulated state, so the only unavoidable runtime input is the token ids",
           supports=_dense_only)
def inference_dense(cfg: ModelConfig, wl: Workload):
    Q, L = wl.tokens, cfg.layers
    params = _base_params(cfg, wl, Q, L, with_targets=False)

    def body(B, toks, tableT, gf, Wh, *rest):
        weights = dict(zip(_dense_names(), rest[:9]))
        _, _, logits = _dense_forward(B, cfg, wl, Q, L, toks, tableT, weights, gf, Wh)
        return logits

    return params, _roles(params, "fixed"), body, W(Q, cfg.vocab), {}


def _decode_T(wl: Workload) -> int:
    """generated tokens per sequence (``gen_tokens``; default ``seq // 8``, at least 1)."""
    return wl.gen_tokens if wl.gen_tokens is not None else max(1, wl.seq // 8)


def _decode_only(cfg: ModelConfig, wl: Workload) -> str | None:
    if cfg.experts != 1:
        return "dense-only factory"
    T = _decode_T(wl)
    if T < 1:
        return "gen_tokens must be >= 1"
    if wl.tokens % T:
        return f"tokens must be a multiple of gen_tokens={T} (one block of generated tokens per sequence)"
    return None


@algorithm("inference-decode", "inference",
           "autoregressive decode with a KV cache and registered (fixed) weights: tokens = B*T new tokens "
           "(T per sequence, teacher-forced) pass through embedding, every layer's norms / q,k,v,o projections / "
           "MLP on the T rows, and attention against the S cached keys/values of their sequence (a runtime "
           "input, role token); the new tokens' keys/values are emitted as the cache append; final norm, LM head",
           simplifications=("teacher forcing: the T generated tokens of a sequence are given as input ids and "
                            "processed as one block (T query rows per matmul), not one at a time",
                            "the T queries of a sequence share one read of the S-row KV cache (the cache is one "
                            "runtime input per layer and sequence, not re-supplied per generated token)",
                            "attention is over the S cached positions only: the new tokens' own keys/values are "
                            "projected and emitted (cache append) but not attended over -- drops T/(S+T) of the "
                            "attention work (~11% at the default T = S/8) and with it the causal mask inside the "
                            "block (attention over the cache needs none)",
                            "no sampling: the logits are the output (the argmax/sample is not a matmul)"),
           supports=_decode_only)
def inference_decode(cfg: ModelConfig, wl: Workload):
    Q, L, S, KW = wl.tokens, cfg.layers, wl.seq, cfg.kv_width
    Tg = _decode_T(wl)
    NB = Q // Tg
    params = _base_params(cfg, wl, Q, L, with_targets=False)
    cache_t = Array(L, Array(NB, Array(S, Array(KW, V16))))
    params += [("K_cache", cache_t), ("V_cache", cache_t)]
    st = dict(_block_statics(cfg, wl, Q), T=Tg)

    def body(B, toks, tableT, gf, Wh, *rest):
        weights = dict(zip(_dense_names(), rest[:9]))
        Kc, Vc = rest[10], rest[11]                       # rest[9] = ids (unused fixed constant)
        x = _embed(B, cfg, wl, Q, toks, tableT)
        k_new, v_new = [], []
        for l in range(L):
            out = B.call(bind(T.DecodeBlock, **st), x, *[weights[k][l] for k in _dense_names()], Kc[l], Vc[l])
            x = out[0]
            k_new.append(out[1])
            v_new.append(out[2])
        xn = B.call(bind(K.RmsNormBatch, Q=Q, K=cfg.d), x, gf)
        logits = B.call(_mm(Q, cfg.vocab, cfg.d, wl.chunk), xn, Wh)
        return tuple_of(logits, _stack(k_new, L), _stack(v_new, L))

    ret = Tuple(W(Q, cfg.vocab), Array(L, W(Q, KW)), Array(L, W(Q, KW)))
    notes = {"gen_tokens_per_seq": Tg, "sequences": NB, "context": S,
             "kv_cache_bytes": 2 * cache_t.leaves * 2}
    return params, _roles(params, "fixed", K_cache="token", V_cache="token"), body, ret, notes


def _session_PT(wl: Workload) -> tuple[int, int]:
    """(prompt tokens, generated tokens) per sequence: ``seq = P + T``, ``T = gen_tokens`` (default ``seq // 8``)."""
    T = _decode_T(wl)
    return wl.seq - T, T


def _session_only(cfg: ModelConfig, wl: Workload) -> str | None:
    if cfg.experts != 1:
        return "dense-only factory"
    P, T = _session_PT(wl)
    if T < 1 or P < 1:
        return f"seq={wl.seq} must split into a prompt and gen_tokens={T} (both >= 1)"
    if wl.tokens % wl.seq:
        return "tokens must be a multiple of seq (whole sessions)"
    return None


@algorithm("inference-session", "inference",
           "one honest inference session per sequence with registered (fixed) weights: prefill over the P prompt "
           "tokens (dense blocks that also emit their K/V rows) followed by teacher-forced decode of the T "
           "generated tokens whose queries attend over the prompt's K/V; the KV cache is internal (an op output "
           "consumed by the decode blocks), so the only runtime input is the token ids (prompt + generated)",
           simplifications=("teacher forcing: the T generated tokens of a sequence are given as input ids and "
                            "decoded as one block (T query rows per matmul), not one at a time",
                            "decode attention is over the P prompt positions only: the new tokens' keys/values are "
                            "projected and emitted (cache append) but not attended over -- drops T*T/(P*P + T*(P+T)) "
                            "of the session's attention MACs (~2% at the default T = seq/8) and with it the causal mask "
                            "inside the decode block; prefill attention is full P x P (no causal mask) as elsewhere",
                            "no sampling: the logits (prompt and generated positions) are the output"),
           supports=_session_only)
def inference_session(cfg: ModelConfig, wl: Workload):
    Q, L, KW = wl.tokens, cfg.layers, cfg.kv_width
    P, Tg = _session_PT(wl)
    nseq = Q // wl.seq
    Qp, Qd = nseq * P, nseq * Tg
    params = _base_params(cfg, wl, Q, L, with_targets=False)
    st_p = dict(_block_statics(cfg, wl, Qp), S=P)          # prefill: nseq sequences of P prompt rows
    st_d = dict(_block_statics(cfg, wl, Qd), S=P, T=Tg)    # decode: nseq x T new rows against P cached rows

    def body(B, toks, tableT, gf, Wh, *rest):
        weights = dict(zip(_dense_names(), rest[:9]))
        s = wl.seq
        toks_p = Coll(Array(Qp, V32), concat([toks[b * s:b * s + P].refs for b in range(nseq)]))
        toks_d = Coll(Array(Qd, V32), concat([toks[b * s + P:(b + 1) * s].refs for b in range(nseq)]))
        xp = _embed(B, cfg, wl, Qp, toks_p, tableT)
        xd = _embed(B, cfg, wl, Qd, toks_d, tableT)
        k_new, v_new = [], []
        for l in range(L):
            wl_ = [weights[k][l] for k in _dense_names()]
            outp = B.call(bind(T.BlockKV, **st_p), xp, *wl_)
            xp, kc, vc = outp[0], outp[1], outp[2]
            outd = B.call(bind(T.DecodeBlock, **st_d), xd, *wl_,
                          kc.reshape(Array(nseq, Array(P, Array(KW, V16)))), vc.reshape(Array(nseq, Array(P, Array(KW, V16)))))
            xd = outd[0]
            k_new.append(outd[1])
            v_new.append(outd[2])
        xnp = B.call(bind(K.RmsNormBatch, Q=Qp, K=cfg.d), xp, gf)
        xnd = B.call(bind(K.RmsNormBatch, Q=Qd, K=cfg.d), xd, gf)
        logits_p = B.call(_mm(Qp, cfg.vocab, cfg.d, wl.chunk), xnp, Wh)
        logits_d = B.call(_mm(Qd, cfg.vocab, cfg.d, wl.chunk), xnd, Wh)
        return tuple_of(logits_p, logits_d, _stack(k_new, L), _stack(v_new, L))

    ret = Tuple(W(Qp, cfg.vocab), W(Qd, cfg.vocab), Array(L, W(Qd, KW)), Array(L, W(Qd, KW)))
    notes = {"prompt_tokens_per_seq": P, "gen_tokens_per_seq": Tg, "sequences": nseq,
             "internal_kv_cache_bytes": 2 * L * Qp * KW * 2}
    return params, _roles(params, "fixed"), body, ret, notes


@algorithm("forward-nonfixed", "inference",
           "the same dense forward pass but with the weights declared as a *new* (accumulated) model "
           "version: pure weight reuse with no backward pass -- the P/X regime in isolation",
           supports=_dense_only)
def forward_nonfixed(cfg: ModelConfig, wl: Workload):
    params, roles, body, ret, notes = inference_dense(cfg, wl)
    return params, _roles(params, "accumulated"), body, ret, notes


@algorithm("inference-moe", "inference", "MoE forward pass with fixed weights (static balanced routing)",
           supports=_moe_only)
def inference_moe(cfg: ModelConfig, wl: Workload):
    params, roles, body, ret, notes = _moe_factory(cfg, wl, train=False)
    return params, _roles(params, "fixed"), body, ret, notes


@algorithm("forward-nonfixed-moe", "inference",
           "the same MoE forward pass (same static balanced routing trace) with every weight -- router, experts, "
           "attention, shared -- declared as a new (accumulated) model version: dynamic rollout generation for MoE",
           supports=_moe_only)
def forward_nonfixed_moe(cfg: ModelConfig, wl: Workload):
    params, roles, body, ret, notes = _moe_factory(cfg, wl, train=False)
    return params, _roles(params, "accumulated"), body, ret, notes


# ---------------------------------------------------------------------------------------------------------
# pretraining (dense / MoE), local SGD
# ---------------------------------------------------------------------------------------------------------

def _train_step(B, cfg, wl, Q, layers, toks, targets, tableT, weights, gf, Wh, ids, lr, adv=None):
    xs, xn, logits = _dense_forward(B, cfg, wl, Q, layers, toks, tableT, weights, gf, Wh)
    dx, dWh, dgf = _head_backward(B, cfg, wl, Q, xn, logits, targets, ids, gf, Wh, adv)
    _, grads = _dense_backward(B, cfg, wl, Q, layers, xs, weights, dx)
    new = _sgd_all(B, weights, grads, layers, lr, _dense_names())
    new_gf = _sgd(B, gf, dgf, lr)
    new_Wh = _sgd(B, Wh, dWh, lr)
    return new, new_gf, new_Wh


def _train_ret(cfg, layers):
    lt = _layer_types(cfg, layers)
    return Tuple(Array(cfg.d, V16), W(cfg.vocab, cfg.d), *[lt[k] for k in _dense_names()])


@algorithm("pretrain-dense", "pretrain",
           "one synchronous SGD step of dense pretraining: forward over Q tokens, cross-entropy gradient, "
           "full backward (activation checkpointing: forward recomputed inside each block backward), and "
           "the weight update; embedding table is accumulated state without a scatter update",
           simplifications=("embedding gradient (scatter-add) not modelled", "optimizer = SGD (Adam differs "
                            "only in elementwise work)", "attention is full (no causal mask)"),
           supports=_dense_only)
def pretrain_dense(cfg: ModelConfig, wl: Workload):
    Q, L = wl.tokens, cfg.layers
    params = _base_params(cfg, wl, Q, L, with_targets=True) + [("lr", V32)]

    def body(B, toks, targets, tableT, gf, Wh, *rest):
        weights = dict(zip(_dense_names(), rest[:9]))
        ids, lr = rest[9], rest[10]
        new, new_gf, new_Wh = _train_step(B, cfg, wl, Q, L, toks, targets, tableT, weights, gf, Wh, ids, lr)
        return tuple_of(new_gf, new_Wh, *[new[k] for k in _dense_names()])

    return params, _roles(params, "accumulated"), body, _train_ret(cfg, L), {}


@algorithm("local-sgd", "pretrain",
           "H chained SGD steps inside one circuit (local SGD / DiLoCo inner loop): each step's forward "
           "uses the weights produced by the previous step, so the intermediate weight versions never "
           "have to be supplied as inputs",
           supports=_split_dense("local_steps"))
def local_sgd(cfg: ModelConfig, wl: Workload):
    Q, L, H = wl.tokens, cfg.layers, wl.local_steps
    assert Q % H == 0 and (Q // H) % wl.seq == 0, "tokens must split into local_steps x seq multiples"
    q = Q // H
    params = _base_params(cfg, wl, Q, L, with_targets=True) + [("lr", V32)]

    def body(B, toks, targets, tableT, gf, Wh, *rest):
        weights = dict(zip(_dense_names(), rest[:9]))
        ids, lr = rest[9], rest[10]
        for h in range(H):
            weights, gf, Wh = _train_step(B, cfg, wl, q, L, toks[h * q:(h + 1) * q], targets[h * q:(h + 1) * q],
                                          tableT, weights, gf, Wh, ids, lr)
        return tuple_of(gf, Wh, *[weights[k] for k in _dense_names()])

    return params, _roles(params, "accumulated"), body, _train_ret(cfg, L), {"local_steps": H, "tokens_per_step": q}


def _moe_factory(cfg: ModelConfig, wl: Workload, train: bool):
    """MoE forward; with ``train`` also the full backward (LM head, ``MoeBlockBwd`` per MoE layer with
    activation-checkpoint recompute, ``BlockBwd`` per leading dense layer) and the SGD update of every
    weight, mirroring ``pretrain-dense``."""
    Q, L, E, F, D = wl.tokens, cfg.layers, cfg.experts, cfg.ffn, cfg.d
    Ld = cfg.dense_layers
    Lm = L - Ld
    Sx = cfg.shared_experts
    params = [("toks", Array(Q, V32))]
    if train:
        params.append(("targets", Array(Q, V32)))
    params += _head_types(cfg)
    attn = {k: t for k, t in _layer_types(cfg, L).items() if k in ("g1", "Wq", "Wk", "Wv", "Wo", "g2")}
    params += list(attn.items())
    if Ld:
        params += [("Wgd", Array(Ld, W(F, D))), ("Wud", Array(Ld, W(F, D))), ("Wdd", Array(Ld, W(D, F)))]
    params += [("Wr", Array(Lm, W(E, D))), ("Wg", Array(Lm, Array(E, W(F, D)))), ("Wu", Array(Lm, Array(E, W(F, D)))),
               ("Wd", Array(Lm, Array(E, W(D, F))))]
    if Sx:
        params += [("Wsg", Array(Lm, W(Sx * F, D))), ("Wsu", Array(Lm, W(Sx * F, D))), ("Wsd", Array(Lm, W(D, Sx * F)))]
    params.append(("ids", Array(cfg.vocab, V32)))
    if train:
        params.append(("lr", V32))
    names = [n for n, _ in params]
    st = _block_statics(cfg, wl, Q)
    nseq = Q // wl.seq
    AO, KW, CH = cfg.attn_out, cfg.kv_width, wl.chunk
    attn_names = ("g1", "Wq", "Wk", "Wv", "Wo", "g2")
    dense_mlp = ("Wgd", "Wud", "Wdd") if Ld else ()
    moe_names = ("Wr", "Wg", "Wu", "Wd") + (("Wsg", "Wsu", "Wsd") if Sx else ())
    bwd_st = dict(st, E=E, TOPK=cfg.topk, SX=Sx)

    def body(B, *args):
        a = dict(zip(names, args))
        x = _embed(B, cfg, wl, Q, a["toks"], a["tableT"])
        xs = []
        for l in range(L):
            xs.append(x)
            if l < Ld:
                x = B.call(bind(T.Block, **st), x, a["g1"][l], a["Wq"][l], a["Wk"][l], a["Wv"][l], a["Wo"][l], a["g2"][l],
                           a["Wgd"][l], a["Wud"][l], a["Wdd"][l])
                continue
            m = l - Ld
            xn = B.call(bind(K.RmsNormBatch, Q=Q, K=D), x, a["g1"][l])
            q = B.call(_mm(Q, AO, D, CH), xn, a["Wq"][l])
            k = B.call(_mm(Q, KW, D, CH), xn, a["Wk"][l])
            v = B.call(_mm(Q, KW, D, CH), xn, a["Wv"][l])
            att = B.batch(bind(T.AttnSeq, S=wl.seq, NH=cfg.heads, KVH=cfg.kv_heads, DH=cfg.head_dim, CH=CH),
                          q.reshape(Array(nseq, Array(wl.seq, Array(AO, V16)))),
                          k.reshape(Array(nseq, Array(wl.seq, Array(KW, V16)))),
                          v.reshape(Array(nseq, Array(wl.seq, Array(KW, V16)))), axes=(0, 0, 0))
            att = att.reshape(Array(Q, Array(AO, V16)))
            o = B.call(_mm(Q, D, AO, CH), att, a["Wo"][l])
            x2 = B.call(bind(K.AddBatch, Q=Q, K=D), x, o)
            xn2 = B.call(bind(K.RmsNormBatch, Q=Q, K=D), x2, a["g2"][l])
            mo = B.call(bind(T.MoeMlp, Q=Q, D=D, FF=F, E=E, TOPK=cfg.topk, CH=CH), xn2, a["Wr"][m], a["Wg"][m], a["Wu"][m], a["Wd"][m])
            if Sx:
                so = B.call(bind(T.ExpertMlp, M=Q, D=D, FF=Sx * F, CH=CH), xn2, a["Wsg"][m], a["Wsu"][m], a["Wsd"][m])
                mo = B.call(bind(K.AddBatch, Q=Q, K=D), mo, so)
            x = B.call(bind(K.AddBatch, Q=Q, K=D), x2, mo)
        xn = B.call(bind(K.RmsNormBatch, Q=Q, K=D), x, a["gf"])
        logits = B.call(_mm(Q, cfg.vocab, D, CH), xn, a["Wh"])
        if not train:
            return logits
        dx, dWh, dgf = _head_backward(B, cfg, wl, Q, xn, logits, a["targets"], a["ids"], a["gf"], a["Wh"])
        # backward through the layers (top first), collecting per-layer gradients
        grads: dict[int, dict[str, Coll]] = {}
        for l in reversed(range(L)):
            if l < Ld:
                out = B.call(bind(T.BlockBwd, **st), xs[l], *[a[k][l] for k in attn_names[:6]],
                             a["Wgd"][l], a["Wud"][l], a["Wdd"][l], dx)
                dx = out[0]
                grads[l] = dict(zip(attn_names + dense_mlp, [out[i + 1] for i in range(9)]))
            else:
                m = l - Ld
                out = B.call(bind(T.MoeBlockBwd, **bwd_st), xs[l], *[a[k][l] for k in attn_names],
                             *[a[k][m] for k in moe_names], dx)
                dx = out[0]
                grads[l] = dict(zip(attn_names + moe_names, [out[i + 1] for i in range(6 + len(moe_names))]))
        lr = a["lr"]
        new_attn = _sgd_all(B, {k: a[k] for k in attn_names}, grads, L, lr, attn_names)
        new_dense = {k: _stack([_sgd(B, a[k][l], grads[l][k], lr) for l in range(Ld)], Ld) for k in dense_mlp} if Ld else {}
        new_moe = {k: _stack([_sgd(B, a[k][m], grads[Ld + m][k], lr) for m in range(Lm)], Lm) for k in moe_names}
        return tuple_of(_sgd(B, a["gf"], dgf, lr), _sgd(B, a["Wh"], dWh, lr),
                        *[new_attn[k] for k in attn_names], *[new_dense[k] for k in dense_mlp],
                        *[new_moe[k] for k in moe_names])

    if train:
        types = dict(params)
        ret = Tuple(Array(D, V16), W(cfg.vocab, D), *[types[k] for k in attn_names],
                    *[types[k] for k in dense_mlp], *[types[k] for k in moe_names])
    else:
        ret = W(Q, cfg.vocab)
    return params, _roles(params, "accumulated"), body, ret, {}


@algorithm("pretrain-moe", "pretrain",
           "one SGD step of MoE pretraining: full forward (router, top-k experts with static balanced "
           "routing, shared experts), cross-entropy gradient, full backward (activation checkpointing; "
           "expert dgrad/wgrad per expert, combine and softmax-router backward) and the weight update",
           simplifications=("routing is a static balanced assignment (the data-dependent gather is a "
                            "permutation of token rows; MACs are those of balanced top-k routing)",
                            "embedding gradient (scatter-add) not modelled", "optimizer = SGD",
                            "attention is full (no causal mask)"),
           supports=_moe_only)
def pretrain_moe(cfg: ModelConfig, wl: Workload):
    return _moe_factory(cfg, wl, train=True)


# ---------------------------------------------------------------------------------------------------------
# LoRA / PEFT and the hidden-adapter red team
# ---------------------------------------------------------------------------------------------------------

_ADAPTER_OF = {"q": ("Aq", "Bq"), "k": ("Ak", "Bk"), "v": ("Av", "Bv"), "o": ("Ao", "Bo"), "g": ("Ag", "Bg"),
               "u": ("Au", "Bu"), "d": ("Ad", "Bd")}


def _lora_factory(cfg: ModelConfig, wl: Workload, adapter_role: str):
    Q, L, r = wl.tokens, cfg.layers, wl.rank
    La = L if wl.adapted_layers is None else min(wl.adapted_layers, L)
    lowest = L - La
    D, F, AO, KW = cfg.d, cfg.ffn, cfg.attn_out, cfg.kv_width
    params = _base_params(cfg, wl, Q, L, with_targets=True) + [("lr", V32)]
    ad_types = {"Aq": W(r, D), "Bq": W(AO, r), "Ak": W(r, D), "Bk": W(KW, r), "Av": W(r, D), "Bv": W(KW, r),
                "Ao": W(r, AO), "Bo": W(D, r), "Ag": W(r, D), "Bg": W(F, r), "Au": W(r, D), "Bu": W(F, r),
                "Ad": W(r, F), "Bd": W(D, r)}
    params += [(k, Array(La, t)) for k, t in ad_types.items()]
    active = {n for p in wl.adapted for n in _ADAPTER_OF[p]}
    roles = _roles(params, "fixed", **{n: (adapter_role if n in active else "fixed") for n in ad_types})
    st = dict(_block_statics(cfg, wl, Q), R=r)
    names = [n for n, _ in params]

    def body(B, *args):
        a = dict(zip(names, args))
        weights = {k: a[k] for k in _dense_names()}
        x = _embed(B, cfg, wl, Q, a["toks"], a["tableT"])
        xs = []
        for l in range(L):
            xs.append(x)
            if l < lowest:
                x = B.call(bind(T.Block, **_block_statics(cfg, wl, Q)), x, *[weights[k][l] for k in _dense_names()])
            else:
                j = l - lowest
                x = B.call(bind(T.LoraBlock, **st), x, *[weights[k][l] for k in _dense_names()],
                           *[a[k][j] for k in T.LORA_ADAPTER_NAMES])
        xn = B.call(bind(K.RmsNormBatch, Q=Q, K=D), x, a["gf"])
        logits = B.call(_mm(Q, cfg.vocab, D, wl.chunk), xn, a["Wh"])
        dl = B.call(bind(K.LossGradBatch, Q=Q, V=cfg.vocab), logits, a["targets"], a["ids"])
        dxn = B.call(_mm(Q, D, cfg.vocab, wl.chunk), dl, transpose(a["Wh"]))           # fixed-weight dgrad
        dx = B.call(bind(K.GainBatch, Q=Q, K=D), dxn, a["gf"])
        new_ad = {k: [] for k in T.LORA_ADAPTER_NAMES}
        for l in reversed(range(lowest, L)):
            j = l - lowest
            out = B.call(bind(T.LoraBlockBwd, **st), xs[l], *[weights[k][l] for k in _dense_names()],
                         *[a[k][j] for k in T.LORA_ADAPTER_NAMES], dx)
            dx = out[0]
            for i, k in enumerate(T.LORA_ADAPTER_NAMES):
                if k in active:
                    new_ad[k].append(_sgd(B, a[k][j], out[i + 1], a["lr"]))
                else:
                    new_ad[k].append(a[k][j])
        return tuple_of(*[_stack(new_ad[k][::-1], La) for k in T.LORA_ADAPTER_NAMES])

    ret = Tuple(*[Array(La, ad_types[k]) for k in T.LORA_ADAPTER_NAMES])
    notes = {"adapted_layers": La, "adapted_projections": wl.adapted, "rank": r,
             "adapter_elements": sum(ad_types[n].leaves for n in active) * La}
    return params, roles, body, ret, notes


@algorithm("lora", "peft",
           "LoRA fine-tuning: frozen (fixed) base weights, rank-r adapters on the chosen projections of the "
           "last `adapted_layers` layers; backward flows through the frozen base (fixed-weight dgrad) down "
           "to the lowest adapted layer; only adapter gradients/updates are formed",
           simplifications=("inactive adapter slots are present but fixed (zero-work would need a different block)",),
           supports=_dense_only)
def lora(cfg: ModelConfig, wl: Workload):
    return _lora_factory(cfg, wl, adapter_role="accumulated")


@algorithm("hidden-adapter", "red-team",
           "the 50%-fixed-matmul red team: identical dataflow to `lora`, but the adapters are *not declared* "
           "as model weights -- they are carried non-fixed inputs that look like context.  Every matmul with "
           "a registered weight is fixed-weight, so a fixed-matmul-fraction policy is satisfied while the "
           "circuit trains and re-emits the carried state",
           supports=_dense_only)
def hidden_adapter(cfg: ModelConfig, wl: Workload):
    return _lora_factory(cfg, wl, adapter_role="carried")


# ---------------------------------------------------------------------------------------------------------
# RL (policy gradient on generated tokens)
# ---------------------------------------------------------------------------------------------------------

@algorithm("rl-policy-gradient", "rl",
           "one policy-gradient step: the policy's forward pass over prompt+generated tokens (generation is "
           "represented teacher-forced over the sampled tokens, which are runtime inputs), advantage-weighted "
           "cross-entropy gradient at the generated positions, full backward and SGD update",
           simplifications=("autoregressive decode is represented as one teacher-forced forward over the "
                            "sampled tokens (same weight MACs, larger row counts per matmul than decode)",
                            "reward model / value network not modelled"),
           supports=_dense_only)
def rl_policy_gradient(cfg: ModelConfig, wl: Workload):
    Q, L = wl.tokens, cfg.layers
    params = _base_params(cfg, wl, Q, L, with_targets=False) + [("adv", Array(Q, V16)), ("lr", V32)]

    def body(B, toks, tableT, gf, Wh, *rest):
        weights = dict(zip(_dense_names(), rest[:9]))
        ids, adv, lr = rest[9], rest[10], rest[11]
        new, new_gf, new_Wh = _train_step(B, cfg, wl, Q, L, toks, toks, tableT, weights, gf, Wh, ids, lr, adv=adv)
        return tuple_of(new_gf, new_Wh, *[new[k] for k in _dense_names()])

    gen = wl.gen_tokens if wl.gen_tokens is not None else wl.seq // 2
    return params, _roles(params, "accumulated"), body, _train_ret(cfg, L), {"gen_tokens_per_seq": gen}


# ---------------------------------------------------------------------------------------------------------
# evolution strategies
# ---------------------------------------------------------------------------------------------------------

@algorithm("es", "evolutionary",
           "one evolution-strategies generation: P population members, each a seed-perturbed copy of the "
           "accumulated weights (noise regenerated from a 32-bit seed, never supplied), each evaluated with a "
           "forward pass over Q/P tokens; rewards fold back into the weights through reward-weighted noise",
           simplifications=("reward = summed loss-gradient magnitude proxy (a scalar per member)",
                            "counters for the hash are a fixed constant input",
                            "embedding table and final-norm gain are not perturbed"),
           supports=_split_dense("population"))
def es(cfg: ModelConfig, wl: Workload):
    Q, L, Pn = wl.tokens, cfg.layers, wl.population
    assert Q % Pn == 0 and (Q // Pn) % wl.seq == 0, "tokens must split into population x seq multiples"
    q = Q // Pn
    lt = _layer_types(cfg, L)
    params = _base_params(cfg, wl, Q, L, with_targets=True)
    params += [("seeds", Array(Pn, V32)), ("sigma", V32)]
    # counters: one V32 per weight element, as a fixed constant (free); shaped like each flattened tensor
    ctr_types = {k: Array(t.n * t.elem.n, Array(t.elem.elem.n, V32)) for k, t in lt.items() if isinstance(t.elem.elem, Array)}
    ctr_types["Wh"] = Array(cfg.vocab, Array(cfg.d, V32))
    params += [(f"ctr_{k}", t) for k, t in ctr_types.items()]
    names = [n for n, _ in params]
    mats = [k for k in _dense_names() if k not in ("g1", "g2")]

    def flat(c: Coll) -> Coll:
        t = c.type
        return c.reshape(Array(t.n * t.elem.n, t.elem.elem))

    def body(B, *args):
        a = dict(zip(names, args))
        weights = {k: a[k] for k in _dense_names()}
        Wh = a["Wh"]
        coefs = []
        for p in range(Pn):
            seed = a["seeds"][p]
            pw = {}
            for k in mats:
                f = flat(weights[k])
                pw[k] = B.call(bind(K.Perturb, N=f.type.n, K=f.type.elem.n), f, seed, a[f"ctr_{k}"], a["sigma"]).reshape(weights[k].type)
            pw["g1"], pw["g2"] = weights["g1"], weights["g2"]
            pWh = B.call(bind(K.Perturb, N=cfg.vocab, K=cfg.d), Wh, seed, a["ctr_Wh"], a["sigma"])
            _, _, logits = _dense_forward(B, cfg, wl, q, L, a["toks"][p * q:(p + 1) * q], a["tableT"], pw, a["gf"], pWh)
            dl = B.call(bind(K.LossGradBatch, Q=q, V=cfg.vocab), logits, a["targets"][p * q:(p + 1) * q], a["ids"])
            col = B.call(bind(K.ColSumBatch, Q=q, K=cfg.vocab), dl)                       # V-vector
            rew = B.call(bind(K.ColSum, Q=cfg.vocab), col)                                 # scalar V16
            coefs.append(B.call(P.Widen32, rew))
        for p in range(Pn):
            seed = a["seeds"][p]
            for k in mats:
                f = flat(weights[k])
                weights[k] = B.call(bind(K.EsUpdate, N=f.type.n, K=f.type.elem.n), f, seed, a[f"ctr_{k}"], coefs[p]).reshape(weights[k].type)
            Wh = B.call(bind(K.EsUpdate, N=cfg.vocab, K=cfg.d), Wh, seed, a["ctr_Wh"], coefs[p])
        return tuple_of(a["gf"], Wh, *[weights[k] for k in _dense_names()])

    return params, _roles(params, "accumulated"), body, _train_ret(cfg, L), {"population": Pn, "tokens_per_member": q}


__all__ = ["Algorithm", "BuiltProgram", "ALGORITHMS", "algorithm", "build"]
