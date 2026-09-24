---
id: vllm-refactor/gate-a-credential-route
lane: vllm-refactor
kind: rule
from: vllm-coordinator (Cursor agent bc-ba6cec03), owner-approved 2026-09-24
created: 2026-09-24T19:42Z
---
# Gate (a) fixtures: mint your own short-lived read-only R2 credential, prefetch, delete it

This is the owner-approved interim route for the regression gate's fixtures. It replaces "pass the credential through ssh stdin, never write it to disk" and a1's `/root/r2ro.env` left on its pod until it expired.

1. **Mint your own credential on the laptop.** Pods don't have the parent keys. Pipe it straight onto **your own** pod so it never lands in a transcript, log or command line:

   ~~~sh
   ( set -a; . ~/.config/verity/r2.env; set +a
     ~/.research/bin/research data mint-credential --permission object-read-only --ttl 1h --via local --env ) \
   | ssh <your pod ssh args> 'umask 077; cat > /root/<lane>-r2ro.env'
   ~~~

2. **Prefetch every regression row's fixtures into your pod's store** while the credential is valid. Use a1's method: `research data fetch <art> --to <tmp>` caches blobs and manifests in `$RESEARCH_STORE`, and the gate's own fetch later builds the trees from local blobs. On the pod:

   ~~~sh
   T=<your tree>; L=/workspace/<lane>; mkdir -p $L
   set -a; . /root/<lane>-r2ro.env; set +a
   export PATH=/workspace/venv312/bin:$PATH PYTHONPATH=$T/tools/research/src
   export RESEARCH_STORE=/workspace/research/store RESEARCH_STORE_CONFIG=$T/tools/research/store.pod.toml
   python - "$T" > $L/prefetch.txt <<'PY'
   import sys, tomllib
   f = tomllib.load(open(sys.argv[1] + "/integrations/vllm/tests/regression/fixtures.toml", "rb"))
   for k, v in f.get("artifacts", {}).items():
       if v: print("top", k, v)
   for rid, r in f["rows"].items():
       for k, v in r.get("artifacts", {}).items():
           if v: print(r.get("row", rid), k, v)
   PY
   while read -r row kind art; do
     d=$L/prefetch_tmp/$row-$kind; rm -rf "$d"
     python -m research.cli data fetch "$art" --to "$d" >/dev/null 2>$L/prefetch.$row-$kind.err && echo "ok $row $kind" || echo "FAIL $row $kind"
     rm -rf "$d"
   done < $L/prefetch.txt
   rm -f /root/<lane>-r2ro.env
   ~~~

3. **Delete the credential right after the fetch**; the last line of the script above does it. Then run gate (a) with no credential. Take a1's `vllm-rf-a1/baseline-gate_a.sh` without its `. /root/r2ro.env` line. a1 found that once the blobs are local, gate (a) needs no credential. If a row still fails with a missing blob, mint a fresh credential, fetch that row, and delete the credential again.

- **Never copy or reuse another lane's credential**, including a1's `/root/r2ro.env`.
- Keep the credential off the laptop's disk, and never print it.
- **Tooling gap:** the long-term fix is for `research run` to pull a run's inputs onto the pod itself. It's recorded in `kb/ops-tools.md`.
