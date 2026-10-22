# ChemLab · Isaac Sim browser access

The current4GPU gallery session ends2026-10-23 03:02:24Asia/Taipei (2026-10-22 19:02:24UTC). Open https://asimfish.github.io/chemlab-isaac-viewer/; links disable automatically at expiry.

This project streams the complete official NVIDIA Isaac Sim GUI with203ChemLab assets in16halls. Four GPUs provide independent editable sessions; the originalH264 stream is relayed without JPEG conversion or another video encoder. The private GitHub Codespaces port requires owner login. GitHubPages hosts only the entry/source.

## Latency changes

1. The native-statistics snapshot now runs asynchronously, with at most one outstanding snapshot. A slow query cannot hold mouse/keyboard messages in the receive loop. Repeated requests coalesce; disconnect cancels the task.
2. Task-owned GitHub SSH/port/health commands and isolated test Chromium now default to direct transport. This removes the workstation's manually configured local proxy from these processes. Desktop/global proxy settings and existing user browsers are unchanged. `T588_PROXY_MODE=system` restores the inherited proxy for networks that require it.

A CPU replay of the real stream handler shows300.49ms→0.038ms median input delivery when a300ms statistics query is pending. A controlled1600×90030fps I/P video fixture through the actual gateway/viewer improves from1133ms to350ms median; a second direct run gives320ms. Both direct runs have10/10 successful measured input trials after3warmups, andp95≈489ms. These are synthetic results, **not** a new native Isaac latency claim. See PERFORMANCE.md and ADR-005.md.

The native retest now uses an outbound reverseSSH connection from the owned training task to the existing5090 host. No additional GPU development machine is started. The client generates its ephemeral SSH key inside its own container; only the public key is registered on the relay. Loopback-only fixed ports, command restrictions and an expiring public-key authorization bound this route. The task and local relay services retain the original one-hour budget. Renewal006 was submitted after the previous005 provider terminal and cleanup were verified. Before allocation, authenticated access and the exact tar CPU SSH lifecycle were tested. A redundant SSH-banner probe failure was caught and removed during CPU preparation. See ADR-006.md.

## Use and deployment

When a GPU session is live, open the stable entry in current Chrome/Edge, sign in as `asimfish`, accept the Codespaces Continue screen if shown, then click Connect. Each GPU admits one viewer. Click inside the picture for native mouse/keyboard control. ASCII text and menus were tested in the previous native session; ChineseIME/audio/mobile remain unverified. Escape did not dismiss the native Window menu in the observed Kit session; click outside or click the menu again.

`server/bridge.py` expects the official NVIDIA browser client on loopback18600 and an isolated ChromiumCDP listener on18619. Bind the gateway only toloopback18620 behind the verified authentication edge. `server/github_proxy.py` validates the configured public/localHost and normalized HTTPSOrigin, strips GitHub tokens/cookies and forwards only toloopback18622. Do not expose CDP or the raw job signaling ports publicly.

`T588_SESSION_DEADLINE` must match the provider manifest. Set `T588_PUBLIC_HOST`, `T588_CODE_HOST` and `T588_ORIGIN_HOST` to the exact deployment hostnames. Keep all services and the Codespace stop timer bounded to that deadline. In the Codespace container set `T588_CODE_BIND=0.0.0.0` so the GitHub forwarding agent can reach the service; the standalone default remains loopback. The forwarded port stays private and root CDP/bridge listeners stay on loopback. The GPU launcher uses finite `--seconds`; elapsed initialization is part of that window. Native30fps is set on both the timeline and app loop. Never put Zenith credentials in code, GitHub, browser URLs or the GPU job. SSH private keys remain local.

For a task-owned transport command, the standalone wrapper applies the measured policy without changing the shell or desktop:

```sh
python3 server/transport_policy.py gh codespace ssh -c YOUR_CODESPACE -- ...
```

For an isolated Chromium test profile, use `--no-proxy-server`. This flag is optional configuration for a dedicated test process; the application cannot change the end user's browser routing. On networks requiring a proxy, retain it and measure that route separately.

## Verification

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m unittest discover -s server -p 'test_*.py'
.venv/bin/python benchmarks/control_benchmark.py /tmp/t588-control-replay.json
node --check site/viewer.js
```

18core authentication/proxy/control tests pass. A separately rejectedWSS-multiplex spike has5additional local protocol tests and measured evidence in the private task artifacts; its complexity is not required by the selected policy. The2core Asia Codespace is reused for CPU-only profiling and stopped afterwards. Assets, NVIDIA SDK binaries, credentials and browser profiles are excluded; upstream asset licenses remain unchanged.
