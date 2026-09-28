"""`research pods create ...` with RunPod's allowedCudaVersions set (driver 580 / CUDA >= 12.9 hosts); the CLI has no flag.

usage: python3 create_cuda.py 12.9,13.0 <research pods create args...>
"""
import sys

from research.pods import runpod

versions = sys.argv[1].split(",")
_request = runpod._request


def _with_cuda(method, path, body=None):
    if method == "POST" and path == "/pods" and body is not None and body.get("computeType") == "GPU":
        body = {**body, "allowedCudaVersions": versions}
    return _request(method, path, body)


runpod._request = _with_cuda

from research.cli import main  # noqa: E402

sys.argv = ["research", "pods", "create", *sys.argv[2:]]
sys.exit(main())
