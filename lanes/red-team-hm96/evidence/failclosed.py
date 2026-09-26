"""red-team-hm96 (PR #93): the #88 fail-open probe against head: an hm96 committer committing through commit_block_offline."""
import hashlib, json, os, random
os.environ["VERITY_RETAIN"] = "host"
from verity_vllm.commit import hiding
from verity_vllm.commit.committer.native_host import NativeHostCommitter, TensorMeta
c = NativeHostCommitter(None, run_id="rt93", chunk=256, hash_threads=1, program_digest=hashlib.sha256(b"p").digest(), leaf_scheme=hiding.NAME)
del os.environ["VERITY_RETAIN"]
s = bytes(random.Random(5).randbytes(256 * 6 - 40))
m = [TensorMeta(0, "layer0.op", "uint8", (len(s),), len(s), 256, 0, 6)]; m[0].dev_off = 0
out = {}
try:
    c.commit_block_offline(0, s, m); out["commit_block_offline"] = "accepted"
    try:
        c.finalize(); out["finalize"] = "accepted"
    except Exception as e:
        out["finalize"] = f"refused: {type(e).__name__}: {str(e)[:120]}"
except Exception as e:
    out["commit_block_offline"] = f"refused: {type(e).__name__}: {str(e)[:160]}"
try:
    from verity_vllm.commit.committer.native_collect import NativeCollectCommitter
    try:
        NativeCollectCommitter(None, gpu_tree=False, native_worker=True, leaf_scheme=hiding.NAME); out["native_collect"] = "accepted"
    except Exception as e:
        out["native_collect"] = f"refused: {type(e).__name__}: {str(e)[:160]}"
except Exception as e:
    out["native_collect"] = f"import failed: {e!r}"[:160]
print(json.dumps(out, indent=1))
