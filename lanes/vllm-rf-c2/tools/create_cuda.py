"""`research pods create` restricted to hosts whose driver reports one of the given CUDA versions (RunPod REST
`allowedCudaVersions`; the CLI has no flag for it).  usage: create_cuda.py 12.9,13.0 <research pods create flags>"""
import sys

from research.pods import part, runpod

versions = sys.argv[1].split(",")
_request = runpod._request


def _with_cuda(method, path, body=None):
    if method == "POST" and path == "/pods" and body is not None:
        body = {**body, "allowedCudaVersions": versions}
    return _request(method, path, body)


runpod._request = _with_cuda
sys.exit(part.main(["create", *sys.argv[2:]]))
