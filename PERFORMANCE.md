## Renewal006 drag and latency · 2026-10-22

Owner has now accessed the live GUI and reports high delay and reversed-feeling dragging. The initial30-step native camera trace preserved all events and signs; its65-event outbound input trace measured166ms median and184ms p95 on the workstation clock. This does not identify a reversed transport axis in the owner's browser. Isaac uses right-drag for Look and Alt+left-drag for Orbit. A new per-viewer selector supports native, vertical, horizontal and both-axis reversal, persisted locally. Real native camera images verify opposite motion, and ordinary menu clicks still pass. The initial relative-motion-only candidate did not reverse the actual camera because this SDK also sends absolute cursor coordinates; it was replaced before delivery and its evidence retained privately. GPU2's test camera was restored from the immutable source camera spec; no source asset was changed.

The native CDP mouse handler measured16.66ms median/16.99ms p95 over60samples. The input queue now coalesces only adjacent pending moves with identical button/modifier state, preserving press/release/key/mode barriers. Overflow closes explicitly instead of silently dropping a release. Under the declared30-move WAN-burst replay (4ms delivery cadence,16.7ms service,3warmups+10trials), release completion waiting changes410.50→33.34ms median,410.91→33.41ms p95. This is a controlled backlog mitigation, not full native latency. A real private GitHub burst coalesced27moves, drained tozero and retained zero video errors.

Native menu click-to-visible change remains substantial: before p50/p95=566.9/668.9ms; final p50/p95=594.6/997.0ms, both10/10 successes after3warmups. Each trial intentionally includes150ms held click. These observations show **no improvement in idle-click end-to-end latency**; route/scheduling variation remains. The roughly285–293ms public RTT dominates the measured input route; decoding is about1ms. Interleaved HTTP-health route probes favored direct routing (p50/p95=413/747ms) over the inherited local proxy (990/1320ms),10successful samples each after3warmups; HTTP duration is not WebSocket RTT. Direct routing stays selected. One initial503 during reverseSSH recovery is retained privately. No general sub100ms, owner-network, or uninterrupted-session claim is made.

24Python boundary/control regressions plus JavaScript camera/GUI coordinate tests pass. [Raw evidence](benchmarks/interaction006.json). No new GPU job or deadline extension was requested; renewal006 still ends2026-10-22 19:02:24UTC.

## Renewal006 availability · 2026-10-22

This renewal ends2026-10-22 19:02:24UTC. Four actual203asset fullGUI1600x900 paths and native mouse menus passed, plus GPU0ASCII search/clear. A CPU access preflight fixed the same18620 private endpoint from404 to authenticated200 by binding the Codespace proxy to the container interface; anonymous requests redirect to GitHub sign-in. One later initialGPU1 request returned503 during a reverseSSH reconnect; its retry and the remaining views passed. This is bounded live acceptance, not uninterrupted-hour reliability. No new click-latency claim replaces the005 measurements below. [Access evidence](benchmarks/renewal006-access.json).

## Native5090 reverseSSH retest · 2026-10-22

The actual official GUI loads the203asset stage on each of four independent renderers. Full native overview is visually verified with Window menu and ASCII Stage-search input; allfour camera views and mouse menus are visually verified. Session ends2026-10-22 17:26:13UTC, including startup/retries within the originally authorized4GPU-hour budget. Two pre-render launches failed and were verified terminal before replacements; they are retained privately. No GPU development machine was started.

Stable overview input uses3warmups plus10trials.9/10successful clicks have median567.8ms and conditionalp95/maximum848.6ms;1trial timed out after6seconds. Including the censored timeout, median is583.1ms and full-distributionp95 is at least6seconds. This improves the historical successful median972.2ms, while preserving its same1/10timeout count. These are separate-session measurements with route and scheduling differences; no universal latency or single-change causal reduction is claimed. Initial publicRTT is around296ms; native inbound stream remains1600×900/H264/30fps. Decoder errors were zero in the measured interval. The warmup-era input run is retained privately and is not substituted for the stable sample.

The raw fixed-workload input record is [native5090-input.json](benchmarks/native5090-input.json). A60second static facility-camera observation stayed connected: decoded/presented 29.95/29.17fps, originalH264 payload 0.0259Mbps, publicRTT p50/p95 286/294ms, zero decoder/sequence errors. [Raw facility record](benchmarks/native5090-facility.json). No owner-browser, physical glass-to-glass, ChineseIME or mobile claim is made.

# Latency optimization · 2026-10-22

A native retest through the5090 reverseSSH relay is now recorded separately from the CPU fixtures below. Owner network latency is not measured.

| Static I/P H2641600×90030fps fixture | Input p50 | Input p95 | Timeouts |
|---|---:|---:|---:|
| OriginalSSH route and inherited browser proxy |1133ms|2017ms|0/10|
| WSS prototype, inherited browser proxy |854ms|944ms|0/10|
| WSS prototype, isolated direct browser |448ms|487ms|0/10|
| SelectedSSH direct policy, direct browser |350ms|489ms|0/10|
| Selected policy repeated |320ms|488ms|0/10|

Each run has3warmups and10measured clicks. Same fixture, resolution, frame rate, viewer, proxy endpoint and pixel-change detector. It uses60frame I/P GOPs; each click changes the synthetic menu at the next frame. These measurements do not include Isaac rendering/input. Route/browser changes were staged sequentially; process/profile restarts and changing network conditions remain confounders. The direct-policy repeat supports the result without proving a universal end-user number. The inherited system proxy was observed before making any change; global settings were left untouched.

The selected policy preserves the originalSSH architecture and changes only task-local process routing plus bounded asynchronous native statistics. The more complex WSS prototype was measured and rejected for production because the simpler candidate measured better. Its CPU echo test gave579.7→357.9ms p50,1140.6→374.6ms p95(3warmups+30samples), but echo alone did not select the final design.

The real stream-handler contention replay holds a native-statistics query for300ms and sends a mouse event while it is pending. Asynchronous/coalesced snapshots change input-delivery median300.49ms→0.038ms,3warmups+10samples. This removes an intermittent blocking source, not300ms from every click.18core auth/proxy/input tests pass, including pending-statistics input, duplicate coalescing and cancellation. A separate5test prototype boundary gate passes.

A heavier approximately1Mbps all-I fixture is retained separately:SSH1449/2879ms→WSS1024/1724ms p50/p95. It is not combined with the staticGOP or native results. A raw-browser no-decode probe lacked a surviving auth session and produced no valid result; it is excluded. One control setup failed because systemd rejected unset-style environment flags; it produced no timing sample and is retained privately.

The new native session uses an outbound5090 reverseSSH relay; the2GPUdev remainsSTOPPED. The historical native972ms median was measured on the older route, with9/10successful trials; it must not be replaced by these synthetic numbers.

## Historical GitHub session performance · 2026-10-22

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
