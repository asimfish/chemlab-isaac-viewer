# Performance · 2026-10-21

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

## Accepted changes

The initial main-thread canvas-copy client accumulated multi-second latency and eventually tripped a600-frame queue limit. A diagnostic with drawing disabled sustained the full30fps; the native video-track sink then sustained all received frames without decoder error for this observation. It copies the original encoded H264 instead of JPEG conversion or an additional encoder. App loop settings were verified at30fps in all four worker receipts, without altering physics, SDK or original gallery.

## Practical limits

The public test used a random in-memory bearer on a temporary tunnel. The delivery URL uses owner email OTP; that interactive login needs the owner. RTT is not a one-way or glass-to-glass measure. Click latency starts at the browser pointer event and ends at the first changed video presentation, excluding physical-device/OS delay. The static bitrate does not predict orbiting or animation. Browser presentation is lower than decoding because delivery is bursty; stale decoded display frames are discarded while every encoded reference frame remains in order.

A domestic gateway or a suitably located GitHub Codespace needs its own measurement. GitHub authorization is complete. A2-core Southeast Asia relay passed SSH and HTTP health checks, but actual video/input tests did not complete before the GPU session ended. An Origin rewrite rejection was identified and a compatibility fix has local regression coverage. Both Codespaces are stopped; GitHub server latency remains unmeasured. Do not promise that changing hosting providers will reduce latency before comparing it.
