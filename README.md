# ChemLab · Isaac Sim browser access

Full NVIDIA Isaac Sim GUI, with203 ChemLab asset roots in16 exhibition halls. Four GPUs host four independent editable sessions. Physics is paused for visual inspection.

This repository hosts the public entry and the original-H264 browser transport source. GPU rendering stays in a finite Zenith training job. GitHub Pages serves static files; it cannot run the GPU or native UDP relay.

## Current development session

The owner renewed the four-GPU allocation for4hours. **Current end:2026-10-22 04:42:04 Asia/Taipei.** Rendering job `job-3gjzfw7ab6jp` uses immutable bundle013, native30fps and four independent203-root galleries. The old allocation is terminal; no overlap was created. The replacement2-core Asia Codespace is active and the first failed container stays stopped.

Stable entry: https://asimfish.github.io/chemlab-isaac-viewer/

Private GitHub viewer: https://t588-isaac-relay002-jjjrvw46r6q52qjv-18620.app.github.dev/?gpu=0

Sign in as `asimfish`, accept the Codespaces Continue screen when shown, then click Connect. This is an interactive native GUI streamed to the browser, with mouse menus and ASCII text entry verified. The entry disables its links after the recorded deadline.

Use current Chrome or Edge. The viewer requires WebCodecs and MediaStreamTrackGenerator. Each GPU admits one browser viewer. Close the viewer or use Disconnect before switching devices. Audio and mobile touch controls are not verified.

## GitHub server option

The operator has already provisioned the task-owned relay; do not create duplicate machines from the entry page.

Codespaces provides a temporary CPU machine and owner-authenticated HTTPS port forwarding. It can host a relay; it does not replace the four Pro6000 GPUs. Keep the forwarded port **private** so GitHub sign-in protects the native Script Editor and mounted data.

The deployment operator needs GitHub OAuth `codespace` permission. The owner has completed that authorization. The first minimal container lacked SSH and was stopped. The pinned SSH feature in this configuration fixes that prerequisite; the replacement relay in Southeast Asia passed SSH and private-port HTTP health checks. GitHub rewrites legitimate HTTPS Origin to `https://localhost:18620`; the proxy now accepts that exact value while rejecting foreign origins. The previous session expired before GPU verification. The4hour renewal now displays all four real GUI views through GitHub, and mouse menus plus ASCII text entry have been exercised. A steady-media observation and latency limits are recorded in PERFORMANCE.md. GitHub personal accounts include a monthly allowance; availability and remaining allowance must be checked in the owner's billing settings. A2-core instance is priced at$0.18/hour outside included usage; no budget or account billing setting is changed by this repository.

The operator uses one active2-core Codespace, keep port18620 private, and create a bounded SSH reverse forward from that machine to the existing local GUI gateway. Both the relay and the GPU session must stop at their recorded deadlines. Do not expose raw CDP or Isaac signaling publicly.

## Transport

Isaac Sim NVENC H264 → private WebRTC/SSH transport → official NVIDIA SDK in isolated Chromium → copied encoded access units → authenticated TLS WebSocket → WebCodecs → native browser video track.

The bridge copies Annex-B access units without JPEG conversion or another video encoder. It preserves the native Kit interface and forwards normalized input through the official SDK. TCP relay paths can introduce head-of-line blocking; a direct authenticated WSS + UDP/TURN route is a future alternative when a suitable public gateway and compatible Kit version exist.

## Local verification

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m unittest discover -s server -p 'test_*.py'
node --check site/viewer.js
```

Source is a bounded deployment prototype. `server/bridge.py` expects the existing loopback NVIDIA client on18600 and an isolated Chromium CDP listener on18619. Its public listener must remain loopback behind verified authentication. The recorded deployment deadline is intentional. Never place Zenith credentials in this repository, client JavaScript, URLs, or the GPU job.

See `PERFORMANCE.md` for measurements and limitations. Assets, SDK binaries, authentication credentials and browser profiles are excluded. ChemLab asset files retain their upstream licenses and are not redistributed here.

The SSH server feature is pinned to its OCI digest. `server/github_proxy.py` runs behind private GitHub port18620 and forwards only to loopback18622, connected to the origin by SSH reverse forwarding. `T588_CODE_HOST` and `T588_ORIGIN_HOST` select exact deployment hostnames. The proxy validates Origin and strips GitHub tokens/cookies before forwarding. Its lifetime is clamped to the GPU deadline.

## Session limits and follow-up

The launcher uses `--seconds 14400`; time starts when the job entrypoint starts, including initialization. Worker readiness does not prove video acceptance, which is checked separately. Workstation services, the origin and Codespaces proxy use the provider manifest deadline; a separate timer stops the Codespace. Original gallery/assets and source environments are preserved. The4hour renewal is a new job because the previous job had already ended.

The private GitHub route replaces the earlier Cloudflare data path. No Cloudflare hop carries this session's video. `T588_SESSION_DEADLINE` must match the cloud manifest and `T588_PUBLIC_HOST`/`T588_ORIGIN_HOST` the configured GitHub hostname. SSH uses a task-local key and only its public half is registered. Codespaces retains its30minute idle setting; a bounded SSH terminal performs real health checks throughout the authorized debug window. The documented PATCH did not change that field; no account-wide setting was changed. See [GitHub idle behavior](https://docs.github.com/en/codespaces/setting-your-user-preferences/setting-your-timeout-period-for-github-codespaces).

Observed ASCII typing in the native Stage search field works. Escape did not dismiss the native Window menu in this Kit session; clicking the menu again or outside closes it. Chinese IME, audio and mobile controls are unverified. The Stage search was cleared after testing. Network congestion can close the stream deliberately rather than discard H264 reference frames; reconnect from the viewer if needed. One earlier roughly146second disconnect is retained and is not a claim of4hour continuous connection reliability. The long observation is bounded evidence, not a guarantee on the end user's network.
