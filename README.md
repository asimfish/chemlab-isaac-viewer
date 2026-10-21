# ChemLab · Isaac Sim browser access

Full NVIDIA Isaac Sim GUI, with203 ChemLab asset roots in16 exhibition halls. Four GPUs host four independent editable sessions. Physics is paused for visual inspection.

This repository hosts the public entry and the original-H264 browser transport source. GPU rendering stays in a finite Zenith training job. GitHub Pages serves static files; it cannot run the GPU or native UDP relay.

## Current development session

The current GPU allocation ends **2026-10-22 00:11:55 Asia/Taipei**. The entry page records the current authenticated gateway. A working static entry does not imply that an expired GPU session is still running.

Use current Chrome or Edge. The viewer requires WebCodecs and MediaStreamTrackGenerator. Each GPU admits one browser viewer. Close the viewer or use Disconnect before switching devices. Audio and mobile touch controls are not verified.

## GitHub server option

[Create a Codespace for this repository](https://codespaces.new/asimfish/chemlab-isaac-viewer)

Codespaces provides a temporary CPU machine and owner-authenticated HTTPS port forwarding. It can host a relay; it does not replace the four Pro6000 GPUs. Keep the forwarded port **private** so GitHub sign-in protects the native Script Editor and mounted data.

The deployment operator needs GitHub OAuth `codespace` permission. The owner has completed that authorization. The first minimal container lacked SSH and was stopped. The pinned SSH feature in this configuration fixes that prerequisite; the replacement relay is being verified. GitHub personal accounts include a monthly allowance; availability and remaining allowance must be checked in the owner's billing settings. A2-core instance is priced at$0.18/hour outside included usage; no budget or account billing setting is changed by this repository.

The operator uses one active2-core Codespace, keep port18620 private, and create a bounded SSH reverse forward from that machine to the existing local GUI gateway. Both the relay and the GPU session must stop at their recorded deadlines. Do not expose raw CDP or Isaac signaling publicly.

## Transport

Isaac Sim NVENC H264 → private WebRTC/SSH transport → official NVIDIA SDK in isolated Chromium → copied encoded access units → authenticated TLS WebSocket → WebCodecs → native browser video track.

The bridge copies Annex-B access units without JPEG conversion or another video encoder. It preserves the native Kit interface and forwards normalized input through the official SDK. TCP relay paths can introduce head-of-line blocking; a direct authenticated WSS + UDP/TURN route is a future alternative when a suitable public gateway and compatible Kit version exist.

## Local verification

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m unittest discover -s server -p test_boundary.py
node --check site/viewer.js
```

Source is a bounded deployment prototype. `server/bridge.py` expects the existing loopback NVIDIA client on18600 and an isolated Chromium CDP listener on18619. Its public listener must remain loopback behind verified authentication. The recorded deployment deadline is intentional. Never place Zenith credentials in this repository, client JavaScript, URLs, or the GPU job.

See `PERFORMANCE.md` for measurements and limitations. Assets, SDK binaries, authentication credentials and browser profiles are excluded. ChemLab asset files retain their upstream licenses and are not redistributed here.

The SSH server feature is pinned to its OCI digest. `server/github_proxy.py` runs behind private GitHub port18620 and forwards only to loopback18622, connected to the origin by SSH reverse forwarding. `T588_CODE_HOST` and `T588_ORIGIN_HOST` select exact deployment hostnames. The proxy validates Origin and strips GitHub tokens/cookies before forwarding. Its lifetime is clamped to the GPU deadline.
