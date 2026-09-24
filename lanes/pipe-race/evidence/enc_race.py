"""Kernel-level reproduction: the SAME LigeroEncoderSIMT object launched concurrently on two CUDA streams (as the
pipelined prover does for two in-flight sub-batches) vs. the sequential reference.  Any mismatch = the scratch race."""
import sys, time
import torch
from backends.direct.ligero.encode_simt import encoder_for
from backends.direct.ligero.field import P

l = int(sys.argv[1]) if len(sys.argv) > 1 else 16384
R = int(sys.argv[2]) if len(sys.argv) > 2 else 3769
trials = int(sys.argv[3]) if len(sys.argv) > 3 else 20
t_pad = int(sys.argv[4]) if len(sys.argv) > 4 else 0
dev = "cuda"
enc = encoder_for(l, 4 * l, t_pad, dev)
print(f"encoder l={l} n={4*l} t_pad={t_pad} blocks={enc.blocks} threads={enc.threads} cf_global={enc.cf_global} stage={enc.stage}", flush=True)
g = torch.Generator(device=dev).manual_seed(1)
rows = [torch.randint(0, P, (R, l), dtype=torch.int64, device=dev, generator=g) for _ in range(2)]
masks = [torch.randint(0, P, (R, t_pad), dtype=torch.int64, device=dev, generator=g) for _ in range(2)] if t_pad else [None, None]
ref = [enc.encode(r, m)[0].clone() for r, m in zip(rows, masks)]
torch.cuda.synchronize()
# sequential determinism
for i in range(2):
    assert torch.equal(enc.encode(rows[i], masks[i])[0], ref[i])
torch.cuda.synchronize()
streams = [torch.cuda.Stream(), torch.cuda.Stream()]
bad_trials = 0
bad_rows = 0
t0 = time.perf_counter()
for t in range(trials):
    outs = []
    for i in range(2):
        with torch.cuda.stream(streams[i]):
            outs.append(enc.encode(rows[i], masks[i])[0])
    torch.cuda.synchronize()
    nb = sum(int((o != r).any(1).sum()) for o, r in zip(outs, ref))
    if nb:
        bad_trials += 1
        bad_rows += nb
print(f"RESULT l={l} R={R} t_pad={t_pad}: {bad_trials}/{trials} concurrent trials produced wrong codewords ({bad_rows} bad rows of {2*R*trials}); {time.perf_counter()-t0:.1f}s", flush=True)
sys.exit(1 if bad_trials else 0)
