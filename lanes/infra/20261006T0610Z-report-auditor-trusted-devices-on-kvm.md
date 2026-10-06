---
id: infra/20261006T0610Z-report-auditor-trusted-devices-on-kvm
campaign: proof-service
lane: infra
kind: report
status: open
repo: danielreuter/verity
origin: infra item I4 of note:verity-root/20261006T0550Z-report-proof-service-implementation
---

# What makes a certifier or memory challenger auditor-trusted on a KVM guest

## Answer

On Nebius today, nothing does. Nebius offers no confidential VMs. Its documentation, its release notes (3.0 "Aether",
Oct 2025, through 3.6, Jun 2026) and its region tables never mention SEV-SNP, TDX or GPU confidential computing
[1][2][3]. A device in the developer's project is the developer's machine: root, disk, console, network interfaces. A
device in the auditor's own project is safe from the developer, but only because Nebius is trusted as the host. The
developer then can't check it, and it can't vouch for the uplink. Our own guests confirm it: on vy-nebius-2 (infra, 6 Oct
06:12Z) the CPU flags carry neither `tdx_guest` nor `sev`/`sev_snp`, and there is no `/dev/tdx_guest` or `/dev/sev-guest`. Three things would make a device auditor-trusted:

1. a confidential VM (CVM) launched from an image the auditor measures, whose signing key is generated inside and bound
   into the attestation report;
2. a network position the developer can't route around;
3. for the challenger, a trusted clock on the node's side of any link a cheating prover could use.

Item 1 is ordinary engineering on a provider that offers CVMs. Items 2 and 3 are open problems on any rented cloud VM.
The cleanest answer to both is either auditor hardware inside the chassis, or a node CVM whose measured layer owns the
only NIC.

## (1) What exists, as of 6 Oct 2026

| Item | Fact |
| --- | --- |
| Nebius CVMs (SEV-SNP or TDX) | Not offered or announced [1][2][3] |
| `gpu-rtx6000` | Xeon 6776P (Granite Rapids), BlueField-3 400 Gbps, us-central1 in the public table [1] |
| `gpu-rtx6000-a` in uk-south2 | Not in Nebius's public tables; listed by third parties [4]. Our node 2 reports a Xeon 6776P |
| `cpu-d3` / `cpu-e2` | AMD EPYC 9654 (Genoa) / Xeon Gold 6338 (Ice Lake) [1]. No CVM mode |
| RTX PRO 6000 Blackwell Server Edition, GPU CC | Supported, single-GPU passthrough only. Multi-GPU CC not validated as of R595 [5][6][7] |
| GPU CC host CPUs | TDX on Emerald or Granite Rapids; SNP on Milan, Genoa or Turin [6] |
| A cloud with confidential RTX PRO 6000 | GCP `g4-standard-48`: one GPU, Turin, listed as "AMD SEV", GA [8][9] |

The silicon under our nodes can run TDX: Granite Rapids is on NVIDIA's list of TDX hosts for GPU CC. What's missing is
Nebius's hypervisor support, and only Nebius can add that. We should ask them whether `gpu-rtx6000-a` hosts can expose
TDX guests. We should also check a node directly: `/proc/cpuinfo` would show the `tdx_guest` or `sev_snp` flag, and
`dmesg` would show "Memory Encryption Features active". I had no node access from this VM, so neither check is run.

## (2) The attestation chain the auditor verifies, and what it buys

**SEV-SNP.** The AMD Secure Processor signs a report with the chip's VCEK. The chain runs VCEK → ASK → ARK, fetched
from AMD's KDS, and the VCEK is derived from the reported TCB (bootloader, TEE, SNP and microcode SPLs) [10][11]. The
auditor checks these fields:

- `MEASUREMENT`: the SHA-384 launch digest of firmware plus kernel, initrd and cmdline under measured direct boot.
- `ID_KEY_DIGEST` / `AUTHOR_KEY_DIGEST`: these make the image auditor-signed, because the auditor's key signs the ID
  block [12].
- `POLICY`: debug and migration off.
- `REPORTED_TCB`: against a minimum.
- `REPORT_DATA`: 64 bytes, which must hold the hash of the device's public signing key.

**TDX.** The TDX module produces a TD report, and the TD Quoting Enclave signs it into a quote. The chain runs from the
PCK certificate to Intel's SGX root CA, and TCB status (`UpToDate`, `OutOfDate`, …) comes from Intel's TCB info
[13][14]. The auditor pins `MRTD` and `RTMR0`–`RTMR3`, can carry an auditor config id in `MRCONFIGID`, and binds the key
in `REPORTDATA`. One TDX-specific catch: the quoting enclave runs on the *host*, in the QGS, so the provider must run
it [15].

**NVIDIA GPU CC.** The GPU attests over SPDM to an NVIDIA-rooted device certificate, and the CVM is the trust anchor
[6]. The certifier and the challenger need no GPU. GPU CC matters only if the *worker* has to sit inside a CVM (see 3a).

**What a CVM excludes.** A CVM is built to exclude the host. Here the host is Nebius, and the developer is a *tenant*:
it controls launch, disks, VPC, routing and scheduling requests, but not the hypervisor. A CVM launched from a measured
image with no unmeasured entry point excludes both parties at the software level. "No unmeasured entry point" means no
SSH, no unmeasured cloud-init, and a dm-verity root.

Witness confidentiality points the same way. Both devices see the witness, so the *developer* must also trust that
the device doesn't leak it to the auditor. A plain VM in the auditor's project gives the developer nothing to check. A
CVM's measurement is evidence both sides read.

**What a CVM doesn't exclude:**

- **Availability.** The developer can kill or restart the device. A restart yields a fresh key and a new report, which
  the auditor sees.
- **The network path** (3a).
- **Physical attacks.** TEE.fail extracts TDX and SNP keys, attestation keys included, with a DDR5 bus interposer
  costing under $1,000. It also forges NVIDIA CC attestation. Intel and AMD place physical attacks out of scope [16][17].
  On rented cloud nodes that's Nebius's risk, but at a "developer's site" with the developer's own servers it's the
  developer's attack.

## (3) Gaps specific to the two devices

**(a) The uplink property is the developer's configuration.** On Nebius, traffic between resources in one network
always goes direct, and route tables can't change that. Security groups, public IPs and route tables are tenant-owned
and editable at any time. Audit Logs record the control-plane edits [18][19][20].

So, provider-trusted at best, the auditor could take a viewer role on the developer's project and check continuously
that:

- the node has no public IP;
- the node's security group allows egress only to the certifier;
- `0.0.0.0/0` routes to the certifier;
- no relevant edit appears in Audit Logs.

That trusts Nebius's API to be complete. Metadata, DNS, object storage and the host's BMC are all paths outside the
VPC model, and the check holds only between readings.

**Hardware-attested routes are possible only if the worker itself is in a CVM**, with a measured layer that owns the
only NIC. Two shapes:

- **Measured guest OS, confidential-containers style.** An auditor-measured kernel and agent run the developer's
  containers. The containers' only network is a socket to the certifier process in the same CVM, and the developer has
  no root. This shape is deployable on a CVM-capable cloud, and NVIDIA ships this stack with Kata [5]. Its trust rests
  on kernel isolation between container and host OS.
- **Paravisor.** The certifier runs at TDX L1 or SNP VMPL0 (an SVSM), and the developer's OS runs, with root, at L2 or
  a lower VMPL. In TDX partitioning the L1 VMM controls the L2's virtualization, so it can present the only NIC
  [21][22]. An SNP guest at a lower VMPL still drives virtio through pages shared with the host, so the SVSM would have
  to mediate page sharing. GPU passthrough into an L2 isn't offered anywhere. This shape is research-grade.

Either shape needs GPU CC. On RTX PRO 6000 that means one GPU per CVM [5][7], so a part would be one GPU. In CC mode a
GPU's DMA reaches only encrypted bounce buffers [6], so it has no side path the CVM doesn't originate. That fits "a
part is at least a whole VM", though tensor parallelism across GPUs would then cross certifiers.

**(b) The challenger's clock.** In TDX the TSC is protected by design: the TDX module owns offset and multiplier, the
frequency is fixed in `TD_PARAMS` at creation, and the guest reads it from TDX-emulated CPUID [23][24][25]. SNP's Secure
TSC is optional. With it on, RDTSC is resolved by hardware, interception terminates the guest, and Linux marks the TSC
reliable [26][27][28]. In both, the host chooses the *frequency* at launch, so the challenger must convert ticks with
the attested or firmware-reported frequency, never a paravirtual one.

A hostile scheduler (the host, or developer load on shared cores) can't make a round *look faster*, provided two rules
hold:

- the send timestamp is taken before the index can leave the device;
- the receipt timestamp is taken after the whole block is in.

Under those rules a stall only lengthens measured time. That costs availability, not soundness. The reverse order
(send, then timestamp) lets a stall shrink the measured interval, which is unsound. So the order belongs in the
challenger's specification. Against the developer on Nebius, the clock is Nebius's KVM anyway; the developer's real
lever is the challenger's *code*, which is (2)'s problem.

Microsecond timing survives in practice. On node 2, a Lean-owned loop, with responder and verifier on one node and
pinned cores, measured a p99.9 of 99.5 µs idle and 140.7 µs under load, against Δ = 0.5 ms
(note `memory-accounting/pous-timing-loop-node`).

**(c) Placement next to the node.** Nebius has no host-affinity API. GPU clusters give InfiniBand locality, and
`gpu-rtx6000` isn't GPU-cluster-compatible anyway [1][29]. The CPU platforms are different hardware, so a `cpu-d3` or
`cpu-e2` auditor VM can never share the node's host.

Off-node placement costs soundness margin, not just latency. Any off-node RTT must go into PoUS's `rtt_allowance`, and
that is slack a cheating prover can spend reaching storage outside the node. So on Nebius **the challenger must run
inside the node VM**, and sound placement there needs a separate trust domain inside the node CVM, as in (a).

Secure TSC can *detect* co-residence between two SNP guests (TsCupid), but AMD calls that outside its threat model
[30]. It's a heuristic, not a placement guarantee.

## (4) Alternatives

**Auditor hardware in the chassis.** A BlueField-3 in zero-trust (restricted) mode can be the node's only NIC. The host
then can't flash its firmware, own its ports or reach RShim; management goes over the DPU's BMC and out-of-band port;
and the DPU attests its firmware through DICE/SPDM to an NVIDIA root [31][32][33]. A DPU sits on PCIe in the same
chassis, so one device can be both certifier and memory challenger, on the right side of the isolation boundary.

The costs:

- a card per node, installed in hardware the developer owns or colocates (Nebius's nodes already carry a BlueField-3,
  but it's Nebius's);
- auditor secure-boot keys for the DPU's Arm OS, since DICE covers firmware, not the application;
- a physical audit that it is the only uplink, including the host BMC's port;
- tamper evidence.

**An inline auditor appliance** in colocation, between the node and the developer's firewall, is simpler to trust.
It's the auditor's box under seal. But it sits outside the chassis, so the challenger pays a cable RTT, a few µs on a
direct link. Both hardware options rule out rented cloud nodes.

**A different cloud.** GCP Confidential G4 gives a single-GPU RTX PRO 6000 CVM today [8][9]. Confirm that "AMD SEV"
there means SEV-SNP reports, since plain SEV lacks SNP's integrity and attestation. GCP also offers TDX with H100 on
`a3-highgpu-1g` [9]. This settles (2) and (3b), but not (3a) or (3c) unless the worker moves into the CVM.

**Bare metal on a CVM-capable host** (Granite Rapids or Turin) is the other route. The developer is then the host, which
is exactly the threat model CVMs are built for, apart from the physical caveat.

## (5) Recommendation

**Now, on Nebius:**

- **Build both devices as measured images.** Reproducible build, dm-verity root, no SSH, key generated at boot, image
  digest published. Moving to a CVM is then a launch change, not a redesign.
- **Run the challenger inside the node VM,** on a reserved core, with the timestamp order of (3b) in its
  specification.
- **Run the certifier as a VM in a project the auditor owns.** On the developer's side: no public IP on the node, a
  security group allowing egress only to the certifier, and a route of `0.0.0.0/0` to it. The auditor gets read access
  to the developer's VPC configuration and Audit Logs.
- **Say plainly that this is trust in Nebius and in our own operation,** not attestation.
- **Ask Nebius** about TDX on `gpu-rtx6000-a`.

**Needs a different provider or hardware.** An auditor-verifiable device needs a CVM platform: GCP Confidential G4, or
bare metal where we run KVM with TDX or SNP. An auditor-verifiable uplink and placement need either the worker inside
an auditor-measured CVM (one GPU per part on RTX PRO 6000) or auditor hardware in the chassis (BlueField zero-trust)
or on the wire (an appliance) in colocation.

**Named assumptions a protocol states meanwhile.** Each is a `Prop` taken as a hypothesis. The ids follow
`verity.claims`'s kebab-case, beside `honest-verifier`.

- **`honest-certifier`.** The deployed certifier runs the pinned code, so the network warden's W1–W6 (`Regenerates`,
  `Padded`, `Packed`, `Allocated`, `UntimedStatus`, `FailClosed`, `JitterBounded`) hold of the real device. Its
  signing key exists only inside it.
- **`certifier-mediation`.** Every byte entering or leaving the part crosses a certifier. There is no other NIC,
  public IP, provider-service path or BMC channel.
- **`honest-challenger`.** The challenger runs the pinned code. Its coin tree is committed before setup and stays
  secret until each reveal, and its key exists only inside it.
- **`challenger-clock`.** The clock is monotone with rate within ε of nominal, and the signed send and receipt times
  bracket the reveal and the full block.
- **`challenger-colocated`.** The only path from challenger to part is node-internal, and `rtt_allowance` covers that
  path alone.
- **For the CVM route, in `verity.claims`'s `<property>/<instance>` form:** `tee-integrity/amd-sev-snp` or
  `tee-integrity/intel-tdx` (vendor root honest, TCB at or above the pinned minimum, no physical attacker), plus
  `honest-provider/nebius` for the interim provider-trusted deployment.

## Sources

1. Nebius, VM types: https://docs.nebius.com/compute/virtual-machines/types ; regions: https://docs.nebius.com/overview/regions
2. Nebius AI Cloud 3.0 "Aether": https://nebius.com/newsroom/nebius-introduces-nebius-ai-cloud-3-0-aether-delivering-enterprise-grade-security-compliance-and-control-for-ai-deployment-at-scale
3. Nebius AI Cloud 3.6: https://nebius.com/newsroom/nebius-ai-cloud-3-6-strengthens-developer-experience-and-governance-for-production-operations
4. GPU Finder, Nebius listings: https://gpufinder.dev/providers/nebius
5. NVIDIA Confidential Containers, supported platforms: https://docs.nvidia.com/datacenter/cloud-native/confidential-containers/latest/supported-platforms.html
6. NVIDIA CC deployment guide (Hopper and Blackwell): https://docs.nvidia.com/cc-deployment-guide-tdx.pdf
7. Super Protocol, GPU and CPU TEE requirements (R580–R595 notes): https://superprotocol.com/resources/gpu-cpu-tee-requirements
8. GCP, Confidential VM with GPU: https://docs.cloud.google.com/confidential-computing/confidential-vm/docs/create-a-confidential-vm-instance-with-gpu
9. GCP, Confidential VM supported configurations: https://cloud.google.com/confidential-computing/confidential-vm/docs/supported-configurations
10. AMD, VCEK and KDS interface: https://docs.amd.com/api/khub/documents/U5H~LHvkigTowyppBkpyrA/content
11. IETF draft, CoRIM profile for SNP reports: https://www.ietf.org/archive/id/draft-deeglaze-amd-sev-snp-corim-profile-02.html
12. `sev` crate, AttestationReport fields: https://docs.rs/sev/latest/sev/firmware/guest/struct.AttestationReport.html
13. Intel TDX DCAP quote library API: https://download.01.org/intel-sgx/latest/dcap-latest/linux/docs/Intel_TDX_DCAP_Quoting_Library_API.pdf
14. Intel Trust Authority claims (TCB status): https://portal.trustauthority.intel.com/eat_profile.html
15. Intel TDX enabling guide, host setup (QGS on the same host): https://cc-enabling.trustedservices.intel.com/intel-tdx-enabling-guide/05/host_os_setup/
16. TEE.fail: https://tee.fail/
17. Intel advisory INTEL-2025-10-28-001: https://www.intel.com/content/www/us/en/security-center/announcement/intel-security-announcement-2025-10-28-001.html
18. Nebius, routing overview: https://docs.nebius.com/vpc/routing/overview
19. Nebius, security groups: https://docs.nebius.com/vpc/security-groups/manage
20. Nebius, Audit Logs: https://docs.nebius.com/audit-logs/events/view
21. Intel, TDX module TD partitioning spec: https://cdrdv2.intel.com/v1/dl/getContent/773039
22. LKML, SVSM and VMPL / TD partitioning discussion: https://lkml.iu.edu/2402.2/01206.html
23. LKML, KVM protected TSC (TDX mandates it, SNP optional): https://lists.openwall.net/linux-kernel/2025/03/14/1436
24. Linux `tdx_arch.h` (TSC frequency in TD_PARAMS): https://github.com/torvalds/linux/blob/840ef6c7/arch/x86/kvm/vmx/tdx_arch.h
25. LKML, TDX CPUID-based TSC calibration: https://lkml.iu.edu/hypermail/linux/kernel/2501.3/07628.html
26. AMD, Secure TSC for SNP guests (LPC 2023): https://lpc.events/event/17/contributions/1525/attachments/1351/2702/Secure%20TSC%20for%20AMD%20SEV-SNP%20guests.pdf
27. LKML, Secure TSC: terminate on RDTSC interception: https://lkml.iu.edu/2311.3/04409.html
28. Patchew, Secure TSC marked reliable: https://patchew.org/linux/20250106124633.1418972-1-nikunj@amd.com/20250106124633.1418972-10-nikunj@amd.com/
29. Nebius, GPU clusters: https://docs.nebius.com/compute/clusters/gpu
30. Juffinger, Neela, Gruss, "Not So Secure TSC": https://gruss.cc/files/securetsc.pdf
31. NVIDIA DOCA, BlueField modes (zero trust): https://networking-docs.nvidia.com/doca/archive/3-5-0/bluefield-modes-of-operation
32. NVIDIA, BlueField-3 attestation certificates: https://networking-docs.nvidia.com/dpunicattestation/6.0/bluefield-3-certificates
33. NVIDIA, DPF zero-trust deployment guide: https://networking-docs.nvidia.com/sol/rdg-for-dpf-zero-trust-dpf-zt
