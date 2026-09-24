"""lane fp4-decode-2: relay a file to a pod through R2 when the laptop -> pod ssh path is slow (the 5090's ~20 KB/s).

    set -a; source ~/.config/verity/r2.env; set +a
    PYTHONPATH=~/projects/verity-main-wt/qol/tools/research/src python relay.py FILE KEY   -> prints a presigned GET URL (1 h)

Uploads FILE to s3://$R2_BUCKET/KEY with the store's SigV4 client (research.store.remote_s3.S3Remote.put: conditional
create) and presigns a GET (SigV4 query auth, UNSIGNED-PAYLOAD) the pod fetches with curl.  No credential leaves the laptop.
"""
from __future__ import annotations

import os
import sys
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

from research.store.remote_s3 import S3Remote, canonical_query, canonical_request, signature, string_to_sign, uri_encode


def presign_get(r: S3Remote, key: str, expires: int = 3600) -> str:
    amz = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    scope = f"{amz[:8]}/{r.region}/s3/aws4_request"
    q = {"X-Amz-Algorithm": "AWS4-HMAC-SHA256", "X-Amz-Credential": f"{r.access_key}/{scope}", "X-Amz-Date": amz,
         "X-Amz-Expires": str(expires), "X-Amz-SignedHeaders": "host"}
    path = r._path(key)
    creq = canonical_request("GET", path, q, {"host": r.host}, "UNSIGNED-PAYLOAD")
    sig = signature(r.secret_key, amz[:8], r.region, string_to_sign(amz, scope, creq))
    return f"{r.scheme}://{r.host}{uri_encode(path, keep_slash=True)}?{canonical_query(q)}&X-Amz-Signature={sig}"


def main() -> int:
    src, key = Path(sys.argv[1]), sys.argv[2]
    r = S3Remote(os.environ["R2_ENDPOINT"], os.environ["R2_BUCKET"], os.environ["AWS_ACCESS_KEY_ID"], os.environ["AWS_SECRET_ACCESS_KEY"])
    res = r.put(key, src)
    print(f"put {key}: {res.get('action')} {src.stat().st_size} B", file=sys.stderr)
    print(presign_get(r, key))
    return 0


if __name__ == "__main__":
    sys.exit(main())
