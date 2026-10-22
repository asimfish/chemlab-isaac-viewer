Refs: T-588

Status: reviewable latency optimization; real Isaac GPU acceptance pending.

Selected task-local direct routing for GitHubSSH/port/health processes and isolatedChromium; global desktop settings and existing user browsers unchanged. Preserve originalSSH architecture. Statistics snapshots are asynchronous, bounded to1inflight, coalesced and canceled ondisconnect.

CPU staticI/P H2641600×90030fps fixture,3warmups+10trials: original1133/2017ms→selected350/489ms p50/p95; direct repeat320/488ms,0timeouts/decodererrors. More complex WSS candidate measured448/487ms with directbrowser and remains only private spike evidence. Real-handler stats contention300.49→0.038ms.18core tests plus5private spike tests pass. These are not new Isaac latency numbers.

Owner authorized4GPU1hour; previousGPUjobSucceeded, private2GPUdevSTOPPED, no assignedCPU-only offering, personaljobSSH/terminalunsupported. Additional temporarydev startup choice pending; noGPUjob/devstart submitted. CPU profiling uses one existing2coreCodespace with a30min stop deadline. Keep task incomplete until actualnative input is measured after approved private access recovery.
