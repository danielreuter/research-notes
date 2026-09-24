# research-pod-guard credential check: runs ON the pod; prints only presence, length, a sha256 prefix and API status codes / counts.
import hashlib, json, urllib.error, urllib.request

env = dict(kv.split("=", 1) for kv in open("/proc/1/environ", "rb").read().decode(errors="replace").split("\0") if "=" in kv)
key, me = env.get("RUNPOD_API_KEY", ""), env.get("RUNPOD_POD_ID", "")
print("pod_id", me, "| key_present", bool(key), "| key_len", len(key), "| key_sha256_12", hashlib.sha256(key.encode()).hexdigest()[:12])
print("RUNPOD_* names in /proc/1/environ:", sorted(k for k in env if k.startswith("RUNPOD")))


def call(method, url, body=None):
    req = urllib.request.Request(url, data=None if body is None else json.dumps(body).encode(), method=method,
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json", "User-Agent": "research-pod-guard"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read().decode(errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors="replace")[:200]
    except Exception as e:  # noqa: BLE001
        return None, f"{type(e).__name__}: {e}"


st, body = call("GET", f"https://rest.runpod.io/v1/pods/{me}")
print("REST GET /pods/<self>:", st, (json.loads(body).get("name") if st == 200 else body[:160]))
st, body = call("GET", "https://rest.runpod.io/v1/pods")
if st == 200:
    ids = [p.get("id") for p in json.loads(body)]
    print("REST GET /pods (list):", st, "| pods visible", len(ids), "| other than self", sum(1 for i in ids if i != me))
else:
    print("REST GET /pods (list):", st, body[:160])
st, body = call("POST", "https://api.runpod.io/graphql", {"query": "query { myself { pods { id } } }"})
try:
    d = json.loads(body)
    pods = ((d.get("data") or {}).get("myself") or {}).get("pods")
    print("GraphQL myself.pods:", st, "| pods visible", None if pods is None else len(pods), "| errors", (d.get("errors") or [{}])[0].get("message") if d.get("errors") else None)
except ValueError:
    print("GraphQL myself.pods:", st, body[:160])
