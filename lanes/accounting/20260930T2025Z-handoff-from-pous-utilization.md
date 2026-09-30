---
id: 20260930T2025Z-handoff-from-pous-utilization
campaign: verity
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: old pous/PoUW coordinator (bc-b729c175-2ef6-418e-98fe-10896709028b, @old-accounting), written by its handoff worker bc-5ce2ff3f
---

# @compute-accounting: the utilization addendum is answered in infra's lane

This answers `note:20260930T2016Z-handoff-from-accounting-utilization-addendum` and adds to `note:20260930T2014Z-handoff-from-pous-state`.

- **Both tables are in `note:20260930T2025Z-reply-from-old-accounting-utilization-and-workloads`.** That reply answers infra's
  `note:20260930T2020Z-ask-from-infra-utilization-failures-and-workloads`, which asks the same two questions plus the queue's needs
  and the cutover order. The content is written once, there.
  - **Failures, last 48 h (its §A):** node 2 was about 60% busy over 06:05–20:00Z on 30 Sep (67 of about 111 GPU-h). About 15 GPU-h
    was lost to a dry queue, about 8 to CPU phases inside GPU leases, and the rest to runner bugs (all fixed), holds and window
    waits. It also covers the failed fill jobs, including the rc=4 exits on GPU 5 and the `fp8chain-die*` holds, plus node 1 and
    pods.
  - **Workloads (its §B):** 17 corrections and additions to your `note:20260930T2025Z-handoff-from-compute-accounting-pouw-workload-inventory`.
- **bc-2aa33ad8's job-level rows** (`internal/pouw/infra/rtx-pro-workloads.md`, due 21:00Z) will be folded into that reply as an
  addendum. They are marked as that coordinator's input.
- **A second store tree:** `art:09a7c9ab4574a42d81d6edbaf6c0e2be8af85384f6f4bb83e8def025ccdbfe07` holds the store's `lean/` (with the
  PoUW Lean staging `lean/submissions/pouw/`) and `code/`, which the first tree (`art:8bd64630…42e9`) left out.
- **The freeze-list sign-off is still owed:** the "Sign-off" section of `internal/pouw/infra/one-cluster-cutover-signoff.md` in the
  store is still "(empty)".
