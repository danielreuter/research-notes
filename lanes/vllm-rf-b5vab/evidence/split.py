"""Split engine/vllm_adapter.py into engine/ modules, moving every top-level statement verbatim (with its attached comments)."""
import ast
import sys
from pathlib import Path

PKG = Path(sys.argv[1])  # integrations/vllm/verity_vllm/engine
SRC = (PKG / "vllm_adapter.py").read_text()
LINES = SRC.splitlines()

PLACE = {
    "build": ["CASE", "case_of", "Engine", "EXECUTION_ENFORCE_EAGER", "execution_label_of", "effective_execution_doc", "parse_target_arg",
              "target_of_workload", "parse_engine_args", "prepare_compiled_process_cache", "engine_kwargs_for", "build_engine",
              "vllm_has_flashinfer", "observed_flash_attn_version", "target_mismatches", "resolved_async_scheduling", "compilation_facts"],
    "code_identity": ["_VERITY_INDUCTOR_DIR_MARK", "CUBIN_DENY_LIST", "_CUBIN_DENY_PREFIX", "CUBIN_CODE_IDENTITY_RULE", "_PATH_STRING_RE",
                      "cubin_section_denied", "_elf_section_bytes", "cubin_sections", "_split_path_strings", "cubin_section_detail",
                      "cubin_code_sha256", "cubin_code_sha256_normalized", "_TRITON_CACHE_INDEX", "_triton_cache_files", "_binary_identity",
                      "loaded_code_objects", "loaded_code_objects_delta", "generated_kernels_of_this_process"],
    "run_facts": ["ACCEPTED", "ACCEPTED_PROFILE_ID", "ACCEPTED_RECORD", "profile_manifest", "model_config_subset", "host_doc", "versions_doc"],
    "pinned": ["PinnedArena", "spanned_bytes", "storage_bytes_view"],
    "capture": ["SCHEMA", "ObserverConfig", "_Step", "Capture", "make_header"],
    "vllm_adapter": ["load_workload", "ACCEPTED_TOKENS", "execution_of_workload", "sampling_params", "run_requests", "throwaway_requests"],
}

HEAD = {}
HEAD["build"] = '''"""Build the vLLM engine under the frozen profile κ, and read back what the built engine executes.

`profile.apply_env()`, `cp = checkpoint_for(case, manifests/checkpoints.json)` (case B0 = SmolLM2-135M, B1 = Qwen2.5-1.5B),
`LLM(**engine_kwargs(cp, replay=False, enforce_eager=True), enable_prefix_caching=False, ...)`, `runner = get_model_runner(llm)`
(DESIGN §1 / §10).  The row's declared execution decides `enforce_eager`, and a declared `TargetProfile` adds its engine args and
environment knobs; after the build the effective execution, compilation, attention version and async-scheduling mode are read back
from the engine's `vllm_config` and checked against the declaration.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch

from verity_vllm.engine import env as engine_env
'''
HEAD["code_identity"] = '''"""Code identity of what this process executes: the ELF sections of a compiled cubin (identity = every section except a
deny-list), the Inductor code objects loaded in this process with their Triton binaries and executed autotune configs, and the
Inductor output code the process compiled.
"""

from __future__ import annotations

import json
import os
from typing import Any

from verity_vllm.engine import env as engine_env
'''
HEAD["pinned"] = '''"""Pinned host memory for the capture's asynchronous D2H copies, and the storage byte range a tensor view spans."""

from __future__ import annotations

import torch
'''
HEAD["run_facts"] = '''"""What a run records about its engine and host: the profile manifest and profile id (built as the production recorder
builds them; fields that necessarily differ from the accepted record's manifest are listed in the notes), the model config subset,
and the versions and host documents.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any

import numpy as np
import torch

from verity_vllm.engine.build import (Engine, compilation_facts, observed_flash_attn_version, resolved_async_scheduling,
                                      vllm_has_flashinfer)
from verity_vllm.engine.code_identity import generated_kernels_of_this_process
'''


def _capture_head() -> str:
    doc = LINES[:43]
    assert doc[0].startswith('"""vLLM adapter (runtime side)') and doc[9].startswith("Step observation.") and doc[42].endswith('"""')
    body = "\n".join(doc[9:])
    return ('"""Observe the in-process V2 `GPUModelRunner` step by step into the raw observation log (the capture), and build the run\n'
            'header the log opens with.\n\n' + body + '''

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import numpy as np
import torch

from verity_vllm.observe.events import (Event, Note, Root, RunEnd, RunHeader, SampleEnd, StepEnd, StepLink, StepStart, StorageAlloc,
                     ViewDesc)
from verity_vllm.observe.log import LogWriter
from verity_vllm.observe.observer import EmptyMode, ModuleNamer, Observer, Recorder, reenter_impl_name
from verity_vllm.observe.storage import StorageAdapter
from verity_vllm.observe import triton_adapter

from verity_vllm.engine import hooks
from verity_vllm.engine.build import Engine
from verity_vllm.engine.pinned import PinnedArena, spanned_bytes, storage_bytes_view
from verity_vllm.engine.run_facts import model_config_subset, profile_manifest
''')


HEAD["capture"] = _capture_head()
HEAD["vllm_adapter"] = '''"""vLLM adapter (runtime side): load a workload, and drive its requests through a built engine.

The engine is built in `engine.build`, the capture and its run header are in `engine.capture`, the run's profile manifest and
versions in `engine.run_facts`, and code identity in `engine.code_identity`; the stages reach all of them through this module's
names.  `load_workload` and what it calls stay in this file: tests execute them from its source, without importing torch.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from verity_vllm.engine.arrivals import run_requests_arrivals  # [coverage D87] step-indexed arrivals (torch-free module, unit-tested)
from verity_vllm.observe import chunks as _chunks  # [chunked 2026-09-17] prefill-chunk / token-step attribution (torch-free, unit-tested)
from verity_vllm.engine.build import (CASE, EXECUTION_ENFORCE_EAGER, Engine, build_engine, case_of, compilation_facts,  # noqa: F401
                                      effective_execution_doc, engine_kwargs_for, execution_label_of, observed_flash_attn_version,
                                      parse_engine_args, parse_target_arg, prepare_compiled_process_cache, resolved_async_scheduling,
                                      target_mismatches, target_of_workload, vllm_has_flashinfer)
from verity_vllm.engine.code_identity import (_VERITY_INDUCTOR_DIR_MARK, CUBIN_CODE_IDENTITY_RULE, CUBIN_DENY_LIST,  # noqa: F401
                                              cubin_code_sha256, cubin_code_sha256_normalized, cubin_section_denied,
                                              cubin_section_detail, cubin_sections, generated_kernels_of_this_process,
                                              loaded_code_objects, loaded_code_objects_delta)
from verity_vllm.engine.run_facts import (ACCEPTED, ACCEPTED_PROFILE_ID, ACCEPTED_RECORD, host_doc, model_config_subset,  # noqa: F401
                                          profile_manifest, versions_doc)
from verity_vllm.engine.pinned import PinnedArena, spanned_bytes, storage_bytes_view  # noqa: F401
from verity_vllm.engine.capture import SCHEMA, Capture, ObserverConfig, RunHeader, make_header  # noqa: F401
'''


def names_of(n: ast.stmt) -> list[str]:
    if isinstance(n, (ast.FunctionDef, ast.ClassDef)):
        return [n.name]
    if isinstance(n, ast.Assign):
        return [t.id for t in n.targets]
    if isinstance(n, ast.AnnAssign):
        return [n.target.id]
    raise ValueError(ast.dump(n)[:80])


def segments():
    """(names, first line, last line, blank lines before) per movable top-level statement; lines 1-based, leading comments attached."""
    tree = ast.parse(SRC)
    out = []
    prev_end = 0
    for n in tree.body:
        start = min([n.lineno] + [d.lineno for d in getattr(n, "decorator_list", [])])
        if isinstance(n, (ast.Import, ast.ImportFrom)) or (isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant)):
            prev_end = n.end_lineno
            continue
        s = start
        while s - 2 >= 0 and LINES[s - 2].startswith("#") and s - 1 > prev_end:
            s -= 1
        blanks = 0
        k = s - 1
        while k - 1 >= prev_end and LINES[k - 1].strip() == "":
            blanks += 1
            k -= 1
        out.append((names_of(n), s, n.end_lineno, blanks))
        prev_end = n.end_lineno
    return out


def main() -> None:
    segs = segments()
    where = {nm: mod for mod, nms in PLACE.items() for nm in nms}
    seen = [nm for names, *_ in segs for nm in names]
    assert sorted(seen) == sorted(where), (set(seen) ^ set(where))
    for mod in PLACE:
        parts = [HEAD[mod].rstrip("\n")]
        last = None
        for i, (names, s, e, blanks) in enumerate(segs):
            if where[names[0]] != mod:
                continue
            gap = blanks if (last is not None and last == i - 1) else 2
            parts.append("\n" * gap + "\n".join(LINES[s - 1:e]))
            last = i
        (PKG / f"{mod}.py").write_text("\n".join(parts) + "\n")
        print(f"{mod}.py: {len(chr(10).join(parts).splitlines()) + 0} lines")


if __name__ == "__main__":
    main()
