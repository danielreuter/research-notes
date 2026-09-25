import sys
from pathlib import Path

d = Path(sys.argv[1]) / "integrations/vllm/tests/lint"


def sub(p, old, new):
    s = (d / p).read_text()
    assert old in s, (p, old[:60])
    (d / p).write_text(s.replace(old, new))


sub("test_p06_one_cli.py", """Shell checks cover every ``*.sh`` under ``verity_vllm/`` (``ops/`` and the tap build scripts); counts are per script.
``pipeline/cli.py`` does not exist yet, so every ``main-block`` and ``argparse`` is a violation today; once it exists,
it is the one file in ``CLI_OWNERS``.  Not checked: the ``[project.scripts]`` entry that installs the CLI.""",
    """Shell checks cover every ``*.sh`` under ``verity_vllm/`` (``ops/`` and the tap build scripts); counts are per script.
``pipeline/cli.py``, the one parser, is the one file in ``CLI_OWNERS``.  Not checked: the ``[project.scripts]`` entry
that installs the CLI.""")
sub("test_p06_one_cli.py", """CLI_OWNERS: frozenset[str] = frozenset()      # verity_vllm/pipeline/cli.py, once it exists""",
    """CLI_OWNERS: frozenset[str] = frozenset({"verity_vllm/pipeline/cli.py"})""")
sub("test_p07_declared_inputs.py", """``pipeline/cli.py`` and ``engine/env.py`` (which writes vLLM's pins from config) do not exist yet, so every
``environ`` use is a violation today; once they exist they are ``ENV_OWNERS``.  The rule's torch-stub test (the plan
digest is the same with torch present and stubbed out) is not a lint.""",
    """``ENV_OWNERS`` may read the environment and name machine paths: ``pipeline/cli.py`` turns both into declared inputs
(option defaults, ``config.RunEnv``).  ``engine/env.py`` (which writes vLLM's pins from config) joins it once it exists.
The rule's torch-stub test (the plan digest is the same with torch present and stubbed out) is not a lint.""")
sub("test_p07_declared_inputs.py", """ENV_OWNERS: frozenset[str] = frozenset()      # verity_vllm/pipeline/cli.py, verity_vllm/engine/env.py""",
    """ENV_OWNERS: frozenset[str] = frozenset({"verity_vllm/pipeline/cli.py"})""")
sub("test_p07_declared_inputs.py", """        if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in docs:
            m = MACHINE_PATH.match(node.value)""",
    """        if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in docs and rel not in ENV_OWNERS:
            m = MACHINE_PATH.match(node.value)""")
print("ok")
