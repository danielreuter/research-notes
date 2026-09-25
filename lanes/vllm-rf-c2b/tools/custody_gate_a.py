# On vyv-rf-c2-reg: R2 custody for a run published before --custody-r2 existed (its local attempt names no run record, and
# attempts are immutable). Push the attempt as it is, then put and push a separate run-record/v1 artifact of the whole run dir.
# env: /root/r2custody.env sourced (minted, delete-free), RESEARCH_STORE, RESEARCH_STORE_CONFIG=<src>/tools/research/store.pod.toml.
import json
import sys
from pathlib import Path

from research.store import attempt as A
from research.store import custody as CU
from research.store import preserved as P

run_id = sys.argv[1]
d = Path("/workspace/research/runs") / run_id
st = A.open_store(None, None)
out = {"run_id": run_id, "remote": str(getattr(st, "remote", None))}
out["attempt_push_errors"] = CU.push_run(st, run_id)
chk = P.check(st, [run_id], mode="head")
out["attempt_preserved"] = chk["preserved"]
rr = CU.put_run_record(st, d, run_id)
rep = st.push(rr, preserve=True)
out["run_record"] = rr
out["run_record_preserved"] = bool(rep.get("preserved"))
out["run_record_errors"] = rep.get("errors")
want = {f.path: (f.bytes, f.sha256) for f in (st.get_manifest(rr).payload.files or [])}
have = {rel: ((d / rel).stat().st_size, CU._sha256(d / rel)) for rel in CU.run_files(d)}
out["run_record_files"] = len(want)
out["run_record_matches_dir"] = want == have
print(json.dumps(out, indent=1, default=str))
