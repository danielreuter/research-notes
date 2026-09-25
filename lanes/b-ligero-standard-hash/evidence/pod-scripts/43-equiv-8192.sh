#!/usr/bin/env bash
# b-ligero-standard-hash (pod, over `research pods ssh`, backgrounded; coordinator 1124Z / 1125Z, PR #21 = main bfb0b928): the
# instance-equiv/v1 document of fp8-ada-x4 at VUS (default 8192) VUs, whose `frozen` is the synthetic stream ref over [0, VUS);
# MAN = the candidate manifest prefix the result being matched carries.  The pod tree
# (5b28557b) predates PR #21, and a sweep is running from it, so main 2c92b9e3's bench/{instance_equiv,tables,views}.py are
# overlaid on a copy of verity_numerical in $W/eqov (git diff 5b28557b 2c92b9e3 touches no relchain / relations / loader file).
# Then --check, then `research data put --kind instance-equiv/v1 --meta @doc --preserve` (+ lane, + the overlay provenance).
#   base64 -d > eqmain.tgz (the three files, from `git show origin/main:...`); nohup bash 43-equiv-8192.sh > $W/equiv8192.log 2>&1 &
set -uo pipefail
W=/workspace/b-lsh; O=$W/equiv; OV=$W/eqov; mkdir -p $O
rm -rf $OV && mkdir -p $OV
cp -r /workspace/src/backends/numerical/python/verity_numerical $OV/
tar -xzf $W/eqmain.tgz -C $OV/verity_numerical/bench
sha256sum $OV/verity_numerical/bench/{instance_equiv,tables,views}.py
cd /workspace/src
source /workspace/env.sh
export PYTHONPATH="$OV:$(pwd)/packages/verity/src:$(pwd)/backends/numerical/python:$(pwd)/tools/research/src:$(pwd)"
export RESEARCH_GIT_COMMIT="5b28557b+bench@2c92b9e3"
NT=${NT:-8}; VUS=${VUS:-8192}; MAN=${MAN:-5ca6851d}
F=$O/instance-equiv-fp8-ada-x4-$VUS.json
nice -n 19 $PY -c 'import verity_numerical.bench.instance_equiv as E; print("tool from", E.__file__)'
nice -n 19 $PY -m verity_numerical.bench.instance_equiv --relation fp8-ada-x4 --vus $VUS --procs $NT --out $F
echo "derive rc=$?"
nice -n 19 $PY -m verity_numerical.bench.instance_equiv --check $F --vus $VUS --procs $NT
echo "check rc=$?"
python3 - $F $VUS $MAN > $O/meta$VUS.json <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
assert d["equal"] is True
n, man = int(sys.argv[2]), sys.argv[3]
assert d["frozen"]["range"] == [0, n] and d["candidate"]["range"] == [0, n]
assert d["candidate"]["manifest_sha256"].startswith(man)
d["lane"] = "b-ligero-standard-hash"
d["provenance"] = ("main 2c92b9e3 bench/{instance_equiv,tables,views}.py overlaid on the 5b28557b pod tree "
                   "(no relchain / relations diff between them)")
print(json.dumps(d))
PY
[ $? -eq 0 ] || { echo "not equal / wrong refs: nothing registered"; exit 1; }
set -a; . $W/r2.env; set +a
C=$W/store.pod.toml
TOOL=$(ls -td /workspace/research/tool/*/ | head -1)
PYTHONPATH=$TOOL RESEARCH_STORE=/workspace/research/store RESEARCH_STORE_CONFIG="$C" \
  python3 -m research data put --kind instance-equiv/v1 --meta @$O/meta$VUS.json --preserve 2>&1 | grep -vi secret | tail -3
echo "put rc=${PIPESTATUS[0]}"
