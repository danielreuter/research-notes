# research-pod-guard monitor probe (runs on the pod): one line of guard state + run status + the workload's last line
import glob, json, os

R = "/workspace/research"
try:
    d = json.load(open(f"{R}/guard/state.json"))
    a = d["activity"]
    print("STATE", d["updated_utc"], d["verdict"], f"idle_min={d['idle_min']}", f"runners={a['runners']}", f"work={a['work']}",
          f"unfetched={[u['run'] for u in d['unfetched']]}", f"refusal={'yes' if d.get('refusal') else 'no'}", f"terminate={d.get('terminate')}")
except Exception as e:  # noqa: BLE001
    print("STATE unreadable", type(e).__name__, e)
for rd in sorted(glob.glob(f"{R}/runs/r*")):
    st = {}
    try:
        st = json.load(open(f"{rd}/status.json"))
    except Exception:  # noqa: BLE001
        pass
    last = ""
    for name in ("stdout.log", "workload.log", "output.log", "launcher.log"):
        p = os.path.join(rd, name)
        if os.path.exists(p):
            with open(p, "rb") as f:
                f.seek(max(0, os.path.getsize(p) - 400))
                lines = [ln for ln in f.read().decode(errors="replace").splitlines() if ln.strip()]
                last = f"{name}: {lines[-1][:140]}" if lines else name
            break
    print("RUN", os.path.basename(rd), st.get("state"), f"rc={st.get('rc')}", "fetched" if os.path.exists(f"{rd}/.fetched") else "unfetched", last)
try:
    print("LOG", open(f"{R}/guard/guard.log").read().strip().splitlines()[-1][:300])
except Exception:  # noqa: BLE001
    pass
