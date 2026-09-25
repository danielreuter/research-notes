"""verity.ml: exact, hardware-faithful semantics of ML primitives, and their registrations in the Verity IR.

    verity.ml.tc      the tensor-core accumulator step (stdlib only; no IR dependency)
    verity.ml.prims   IR primitives: AmpereBF16TcDot16, HopperBF16WgmmaDot16, HopperE4m3QgmmaDot32, Bf16ToF32, F32ToBf16Rn,
                      F2fpBf16, F32ToE4m3Sat, const
    verity.ml.scalar  IR primitives: integer, bit, select and comparison operations; FP32 abs / neg / max / min / cvt.sat
    verity.ml.gemm    IR composites: DotBf16 / GemmCoordinate / Gemm parameterised by the step; GEMM_AMPERE, GEMM_HOPPER
    verity.ml.kernels numpy batch forms of the steps and GEMM coordinates (BF16, FP8 E4M3, NVFP4 / MXFP4), registered with
                      `verity.evaluation` and self-checked against `verity.ml.tc`
"""
from __future__ import annotations

__version__ = "0.1.0"
