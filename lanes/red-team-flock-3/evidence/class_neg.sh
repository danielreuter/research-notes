#!/usr/bin/env bash
# red-team-flock-3: flock-ir-frame --class (PR #54 @ 4eb3b991, key-count class pins), CPU, on the verifier's own staged files.
#   class_neg.sh BIN FILES_DIR CLASS_DIR TABLES
# FILES_DIR: cap-t129/ (frame-4.bin, net.txt), cap-t128/ (frame-2.bin, net.txt), net-t130.txt; CLASS_DIR: class-{1-128,129-256}.json
set -uo pipefail
B=$1; F=$2; C=$3; TB=$4; O=${RESEARCH_RUN_DIR:-/tmp/rtf3/classneg}/out; mkdir -p $O; E=$(cd "$(dirname "$0")" && pwd)
F129=$(ls $F/cap-t129/frame-*.bin); N129=$F/cap-t129/net.txt; F128=$(ls $F/cap-t128/frame-*.bin); N128=$F/cap-t128/net.txt; N130=$F/net-t130.txt
M=$C/class-129-256.json; MLO=$C/class-1-128.json
pin() { sha256sum "$1" | cut -c1-64; }
lc() {  # tag want(0 accept / 2 refuse) instances netlist manifest pin
  $B loadcheck --instances $3 --netlist $4 --class $5 --pin $6 --tables $TB > $O/L-$1.txt 2>&1; local rc=$?
  local ok=$([ $rc = $2 ] && echo PASS || echo FAIL)
  echo "== L-$1 want=$2 rc=$rc $ok $(grep -h 'REFUSED' $O/L-$1.txt | head -1 | cut -c1-220)"
}
python3 - "$M" "$O" "$N129" <<'EOF'
import hashlib, json, sys
src, out, n129 = sys.argv[1:4]
b = open(src, "rb").read(); m = json.loads(b)
def w(name, obj=None, raw=None):
    open(f"{out}/{name}.json", "wb").write(raw if raw is not None else (json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n").encode())
x = json.loads(b); del x["nets"]["200"]; w("missing_t200", x)
x = json.loads(b); x["nets"]["257"] = x["nets"]["256"]; w("extra_t257", x)
x = json.loads(b); x["T"] = [129, 257]; w("range_widened", x)
x = json.loads(b); x["words_per_key"] = 32; w("words_per_key_32", x)
# a forged T=129 netlist: every positive tail constant x100 in its CUT line (as the producer's eps_forged_tail_words)
t = open(n129).read(); head, cut = t.rsplit("\nCUT ", 1); c = json.loads(cut)
import struct
for op in c["tail"]:
    if op[1] == "Const":
        f = struct.unpack("<f", struct.pack("<I", op[2] & 0xFFFFFFFF))[0]
        if f > 0 and f == f and f != float("inf"):
            op[2] = struct.unpack("<I", struct.pack("<f", f * 100.0))[0]
ft = head + "\nCUT " + json.dumps(c, separators=(",", ":")) + ("\n" if t.endswith("\n") else "")
open(f"{out}/net-t129-forged.txt", "w").write(ft)
x = json.loads(b); x["nets"]["129"] = hashlib.sha256(ft.encode()).hexdigest(); w("forged_net129", x)
w("whitespace", raw=json.dumps(m, sort_keys=True, indent=1).encode())
# duplicate key in nets: "129" first honest, then T=130's netlist sha (serde keeps one of them silently)
n130 = json.loads(b)["nets"]["130"]
dup = b.decode().replace('"129":"' + m["nets"]["129"] + '"', '"129":"' + m["nets"]["129"] + '","129":"' + n130 + '"', 1)
w("duplicate_129", raw=dup.encode())
print("MANIFESTS written")
EOF
lc honest 0 $F129 $N129 $M $(pin $M)
lc wrong_pin_other_class 2 $F129 $N129 $M $(pin $MLO)
lc file_outside_class 2 $F129 $N129 $MLO $(pin $MLO)
lc t128_file_in_129_class 2 $F128 $N128 $M $(pin $M)
lc t130_netlist_for_t129_file 2 $F129 $N130 $M $(pin $M)
lc missing_t200 2 $F129 $N129 $O/missing_t200.json $(pin $O/missing_t200.json)
lc extra_t257 2 $F129 $N129 $O/extra_t257.json $(pin $O/extra_t257.json)
lc range_widened 2 $F129 $N129 $O/range_widened.json $(pin $O/range_widened.json)
lc words_per_key_32 2 $F129 $N129 $O/words_per_key_32.json $(pin $O/words_per_key_32.json)
lc forged_manifest_under_honest_pin 2 $F129 $O/net-t129-forged.txt $O/forged_net129.json $(pin $M)
lc forged_manifest_under_its_own_pin_CP1 0 $F129 $O/net-t129-forged.txt $O/forged_net129.json $(pin $O/forged_net129.json)
lc noncanonical_whitespace_CP2 0 $F129 $N129 $O/whitespace.json $(pin $O/whitespace.json)
lc duplicate_key_honest_net 0 $F129 $N129 $O/duplicate_129.json $(pin $O/duplicate_129.json)
lc duplicate_key_t130_net 2 $F129 $N130 $O/duplicate_129.json $(pin $O/duplicate_129.json)
# the producer's selftest (every case) under the class pin
$B selftest --instances $F129 --netlist $N129 --class $M --pin $(pin $M) --tables $TB > $O/S-class-t129.txt 2>&1
echo "== S-class-t129 $(grep -h '^SELFTEST' $O/S-class-t129.txt | cut -c1-200) pass=$(grep -c '"pass":true' $O/S-class-t129.txt)"; grep -h '"pass":false' $O/S-class-t129.txt | cut -c1-250
# live sessions against a class verifier
sess() {  # tag prover-args...
  local tag=$1; shift; local port=$((7700 + RANDOM % 200))
  $B serve --listen 127.0.0.1:$port --out $O/sess-$tag --instances $F129 --netlist $N129 --class $M --pin $(pin $M) --tables $TB --sessions 1 > $O/serve-$tag.txt 2>&1 &
  local sp=$!; sleep 5
  timeout 900 $B prove --verifier 127.0.0.1:$port --instances $F129 --netlist $N129 --tables $TB "$@" > $O/prove-$tag.txt 2>&1
  sleep 2; kill $sp 2>/dev/null; wait $sp 2>/dev/null
  echo "== X-$tag $(grep -ho '"accepted":[a-z]*' $O/prove-$tag.txt | head -1) $(grep -h 'SESSION' $O/serve-$tag.txt | grep -o '"accepted":[a-z]*\|"aborted":"[^"]\{0,60\}' | tr '\n' ' ') $(grep -h 'REFUSED' $O/prove-$tag.txt | head -1 | cut -c1-160)"
}
sess honest_class --class $M
sess prover_without_class
sess prover_whitespace_manifest --class $O/whitespace.json
sess prover_other_class --class $MLO
true
