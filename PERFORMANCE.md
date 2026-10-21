# GitHub session performance · 2026-10-22

Workstation Chromium140, Isaac fullGUI1600×900, native30fps, fixed facility camera in the203asset gallery. Private2core SoutheastAsia Codespaces route over reverseSSH, without Cloudflare in the data path. End-user network is not measured.

| Metric | Measured result |
|---|---:|
| Connection age at final sample | 314.6s |
| Frozen steady observation | 60.0s |
| Decoded / presented rate in that interval | 29.90 / 22.82fps |
| Original H264 payload, static scene only | 0.0236Mbps |
| Public RTT p50 / p95, sliding samples | 363 / 939ms |
| Native private WebRTC RTT, latest | 18.0ms |
| Receive→decode p50 / p95 | 0.8999999761581421 / 2.899999976158142ms |
| Sequence / decoder errors | 0 |
| Connected at final sample | yes |

Overview native menu input:3warmups plus10measured trials;9successful,1timeout at6seconds. Successful samples median972.2ms, conditionalp951315.8ms. That conditional percentile excludes the timeout and must not be presented as the full distribution. An earlier harness omitted the pressed-button mask and its13null trials are invalid timing data; they are retained as a failed test, not performance evidence. Mouse menus and ASCII typing in Stage search were visually checked; search was cleared. Escape did not dismiss the Window menu in this Kit session; clicking the menu or outside closes it.

The connection remained active for the reported age, including the static observation. This does not prove uninterrupted4hour reliability. One earlier approximately146second disconnect is retained; later metrics expose close code/reason, and server congestion is logged without dropping H264 reference frames. Reconnect from the viewer if the network closes it. Audio, mobile input and Chinese IME are unverified.

The browser uses the original encoded stream and a native video track. No JPEG conversion or second video encoder is used. Sender-task exceptions are now retrieved during disconnect cleanup. RTT is not one-way or physical glass-to-glass latency. Bitrate is for a static scene, not orbiting or animation. The current facility-camera interval differs from the previous overview-camera Cloudflare observation, so these rows do not establish a causal hosting-provider speedup.

## Historical Cloudflare baseline · 2026-10-21

Frozen workload: complete203-asset gallery overview, official full GUI1600×900, physical GPU0, app loop30fps, workstation Chromium140, Cloudflare LAX HTTP/2 path. These are workstation measurements, not the end user's network.

| Metric | Result |
|---|---:|
| Observation | 463.8s |
| Native private WebRTC RTT, latest sample | 25.0ms |
| Public WebSocket RTT p50 / p95 | 607 / 1435ms |
| Browser receive→decode p50 / p95 | 1.0 / 3.5ms |
| Click→first presented menu change p50 / p95 | 1200.2 / 2267.3ms |
| Native input trials | 3warmups + 10measured |
| Decoded / presented rate | 29.8 / 19.9fps |
| H264 bitrate, static gallery only | 0.035Mbps |
| Sequence / decoder errors | 0 |


The earlier canvas-copy client accumulated latency; the native video-track sink eliminated that decoder backlog for the measured intervals. The old GPU session expired normally. Current timing is reported separately above.
