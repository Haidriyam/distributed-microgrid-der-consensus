![Microgrid DER Consensus CI](https://github.com/Haidriyam/distributed-microgrid-der-consensus/actions/workflows/devsecops-ci.yml/badge.svg)

# Byzantine-Resilient Distributed Secondary Frequency & SoC Consensus

A distributed control testbed for converter-interfaced islanded AC microgrids. It implements primary $P\text{--}f$ droop dynamics and a Weighted Mean Subsequence Reduced (W-MSR) consensus filter to guarantee secondary frequency restoration and battery State-of-Charge (SoC) balancing under active False Data Injection (FDI) attacks.

```text
[ Inverter Agent i ] ──► (Broadcast Telemetry: f, SoC) ──► [ Mesh Network ]
         │                                                      │
         ▼                                                      ▼
[ Primary Droop: P-f ] ◄── [ W-MSR Consensus Filter ] ◄── (Adversary Node: +5 Hz FDI)
                               (Trims Extremes)