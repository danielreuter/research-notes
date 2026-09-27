#!/usr/bin/env python3
"""red-team-flock-3: a cell's shared-NAT placement (PR #91's NAT exception, S1-S5 + U1-U3 + R1) from the runs' own records.

For each role, three independent pod ids must agree: the probe's (`placement.json`, RUNPOD_POD_ID from /proc/1/environ), the
research runner's (`execution.remote.pod_id` of the attempt) and the plan's; two boot ids (the probe's and the runner's
`job.json` environment) must equal the plan's. Then, from the runs' own probes and the plan's machine ids: machine ids and boot
ids recorded and different, both pods bare metal (no hypervisor flag, a non-hypervisor DMI sys_vendor), the DMI uuid unreadable
or different, one public IP, the prover's link `<verifier pod>.runpod.internal` in 10/8 with no resolution error and a 10/8
source, all 30 TCP connects on that address succeeding with median >= 0.1 ms; `placement.assess` (PR #91, PL=path) re-run on
those values finds no problem; the cell's recorded evidence equals them.

  nat_check.py ART...     (PL=/tmp/rtf3/placement_852816d6.py)    -> one NATCELL json line per cell
"""
import importlib.util
import ipaddress
import json
import os
import subprocess
import sys
from pathlib import Path

TREES = Path.home() / ".research/store/trees"
NET10 = ipaddress.ip_network("10.0.0.0/8")


def sh(*a):
    return subprocess.run(["research", *a], capture_output=True, text=True).stdout


def meta_of(art):
    return next(json.loads(l.split(None, 1)[1]) for l in sh("data", "show", art).splitlines() if l.startswith("meta"))


def attempt(run):
    d = {}
    for l in sh("data", "show", run).splitlines():
        k, _, v = l.partition(" ")
        if k in ("outputs", "execution", "source", "status"):
            try:
                d[k] = json.loads(v.strip())
            except ValueError:
                d[k] = v.strip()
    return d


def tree(art):
    sh("data", "fetch", art)
    return next(TREES.glob(art[4:] + "*"))


def in10(ip):
    try:
        return ip is not None and ipaddress.ip_address(ip) in NET10
    except ValueError:
        return False


def main():
    spec = importlib.util.spec_from_file_location("pl91", os.environ.get("PL", "/tmp/rtf3/placement_852816d6.py"))
    PL = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(PL)
    for art in sys.argv[1:]:
        m = meta_of(art)
        cp = m["cell"]["placement"]
        plan = cp.get("plan") or {}
        c, rec = {}, {}
        for role in ("prover", "verifier"):
            run = m["derived_from"][f"{role}_run"]
            at = attempt(run)
            t = tree(at["outputs"]["run_record"])
            pj = json.loads((t / "placement.json").read_text())
            env = json.loads((t / "job.json").read_text()).get("environment") or {}
            runner_pod = ((at.get("execution") or {}).get("remote") or {}).get("pod_id")
            p = plan.get(role) or {}
            c[f"U3_{role}_pod_id_probe=runner=plan"] = bool(pj.get("pod_id")) and pj.get("pod_id") == runner_pod == p.get("pod_id")
            c[f"{role}_boot_id_probe=job=plan"] = bool(pj.get("boot_id")) and pj.get("boot_id") == env.get("boot_id") == p.get("boot_id")
            c[f"S1_{role}_bare_metal"] = pj.get("hypervisor") is False and bool(pj.get("sys_vendor")) and not PL.is_hypervisor_vendor(pj["sys_vendor"])
            rec[role] = {**pj, "machine_id": p.get("machine_id"), "_runner_pod": runner_pod, "_run": run, "_commit": (at.get("source") or {}).get("commit")}
        pr, vr = rec["prover"], rec["verifier"]
        c["machine_ids_differ"] = bool(pr["machine_id"] and vr["machine_id"]) and pr["machine_id"] != vr["machine_id"]
        c["boot_ids_differ"] = pr["boot_id"] != vr["boot_id"]
        c["U2_uuid_unreadable_or_differ"] = (pr.get("product_uuid") is None and vr.get("product_uuid") is None) or \
            (bool(pr.get("product_uuid")) and bool(vr.get("product_uuid")) and pr["product_uuid"] != vr["product_uuid"])
        c["shared_public_ip"] = bool(pr.get("public_ip")) and pr["public_ip"] == vr.get("public_ip") and cp.get("shared_public_ip") is True
        link = pr.get("link") or {}
        host = (link.get("peer") or "").rpartition(":")[0]
        c["S3_link_global_network"] = host == f"{vr['pod_id']}.runpod.internal" and in10(link.get("peer_ip")) and in10(link.get("source_ip")) \
            and not link.get("error")
        rtt = link.get("rtt") or {}
        c["S4_R1_rtt"] = str(rtt.get("method", "")).startswith("tcp-connect") and rtt.get("n") == 30 and rtt.get("failed") == 0 \
            and rtt.get("target_ip") == link.get("peer_ip") and rtt.get("target") == f"{host}:22" and (rtt.get("median_ms") or 0) >= PL.RTT_FLOOR_MS
        strip = lambda x: {k: v for k, v in x.items() if not k.startswith("_") and k != "link"}  # noqa: E731
        a = PL.assess(strip(pr), strip(vr), link)
        c["assess_PR91_no_problems"] = a["problems"] == [] and a["shared_public_ip"] is True
        ev = cp.get("separation") or {}
        c["S5_record_matches"] = (ev.get("machine_id") == [pr["machine_id"], vr["machine_id"]] and ev.get("boot_id") == [pr["boot_id"], vr["boot_id"]]
                                  and ev.get("product_uuid") == [pr.get("product_uuid") or "unreadable", vr.get("product_uuid") or "unreadable"]
                                  and (ev.get("link") or {}).get("address") == link.get("peer_ip") and (ev.get("rtt") or {}).get("median_ms") == rtt.get("median_ms"))
        out = {"cell": art[:12], "ok": all(c.values()), "checks": c, "assess_problems": a["problems"],
               "prover": {k: pr.get(k) for k in ("pod_id", "machine_id", "boot_id", "sys_vendor", "product_name", "cpu_model", "public_ip", "_commit")},
               "verifier": {k: vr.get(k) for k in ("pod_id", "machine_id", "boot_id", "sys_vendor", "product_name", "cpu_model", "public_ip", "_commit")},
               "link": {"peer": link.get("peer"), "peer_ip": link.get("peer_ip"), "source_ip": link.get("source_ip")},
               "rtt": {k: rtt.get(k) for k in ("median_ms", "min_ms", "n", "failed")},
               "cell_link_error": (cp.get("link") or {}).get("error")}
        print("NATCELL\t" + json.dumps(out), flush=True)


if __name__ == "__main__":
    main()
