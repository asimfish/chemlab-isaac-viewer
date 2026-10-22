# Experimental low-latency transport · T-588

This candidate carries the original encodedH264 over WebRTC/SRTP and carries native mouse/keyboard events over an ordered data channel. GitHub Codespaces is used only for authenticated signaling. If direct ICE cannot connect, a domestic authenticated TURN endpoint carries encrypted media/control. The existing production gateway remains available as a separate compatibility path when a GPU session is active.

Status: CPU protocol and forced-relay validation passed. Real cross-network5090↔workstation direct ICE failed despite server-reflexive candidates. A reachable domestic public IPv4/UDP endpoint or explicit5090 UDP forwarding is missing; no public candidate has been deployed. GPU006 expired normally and was verified Succeeded; no new GPU task was started. Native60fps, owner-network latency, packet-loss recovery, long-session reliability and public TURN deployment remain unverified. Do not substitute the CPU measurements for those gates.

## Measured CPU gate

Same1600×900 preencoded synthetic menu,60fps,3warmups+10measured inputs per protocol:

| Local protocol | Input p50 | p95 | Success |
|---|---:|---:|---:|
| ExistingWebSocket |34.8ms|36.1ms|10/10|
| DirectWebRTC |28.4ms|35.6ms|10/10|
| AuthenticatedTURN, forced relay |38.0ms|58.9ms|10/10|

The forced-relay185second interval stayed connected at60fps with zero packet loss, dropped frames or freezes. Data-channel RTT p50/p95 was1/1ms. Wrong TURN credentials were rejected; valid credentials allocated a relay. These local results show protocol feasibility, not the user's expected WAN latency or a causal improvement over the prior native594.6ms click median. [Sanitized raw results](../../benchmarks/webrtc007-local.json).

## Relay endpoint required

A domestic2vCPU/2GiB Linux server with a real publicIPv4 is sufficient as a proposed relay shape; capacity and performance must still be measured on the supplied host. It does not require a GPU. Open UDP/TCP3478 and UDP49152–49215; optional TLS5349 uses the exact supplied certificate/key paths. An equivalent one-to-one port mapping on5090 must include both the listener and complete relay range. A public SSH gateway alone does not supply these UDP mappings. Keep the relay close to the user's ISP/region and measure it before another GPU allocation.

Install a maintained coturn package appropriate to that server. Set `T588_TURN_SHARED_SECRET` through the launch environment and run:

```sh
python3 relay_launcher.py --binary /usr/bin/turnserver \
  --public-ip YOUR_PUBLIC_IPV4 --relay-ip LOCAL_INTERFACE_IPV4 --seconds 3600
```

The launcher creates an anonymous memory-backed configuration descriptor, passes no shared key on the command line, strips unrelated credentials from the child environment, applies REST authentication/quotas/bandwidth bounds, blocks private/multicast/metadata peers, disables the admin CLI/TCP relay allocations, and enforces a finite deadline. It does not change a firewall or purchase a host. TLS is optional and uses `--cert /exact/fullchain.pem --key /exact/key.pem`; the launcher never uploads either file. The old Ubuntu lab binary was extracted only into the task directory and bound only to loopback; it is excluded from this package and is not a production recommendation.

## Candidate integration

Use a new isolated Python environment and `pip install -r requirements.txt`. Set the actual live job's `T588_SESSION_DEADLINE` and `T588_GPU_DEADLINE` from its manifest, the exact private hostname in `T588_RTC_HOST`, and the following environment values:

```text
T588_TURN_URLS=["turn:YOUR_PUBLIC_IPV4:3478?transport=udp","turn:YOUR_PUBLIC_IPV4:3478?transport=tcp"]
T588_TURN_SHARED_SECRET=<injected securely; same relay key>
T588_FORCE_RELAY=1
```

Run `python3 server.py` on loopback18626. It consumes the existing private native bridge on18620 and preserves one viewer per GPU. The initial native keyframe is forwarded as an AVPacket with its RTP time base; H264 reference order is retained. Backlog closes a session instead of discarding reference frames. An independent upstream heartbeat keeps the native view alive while data-channel pings are answered locally.

Keep18626 behind the private Codespaces authentication edge. `server/github_proxy.py` now accepts `T588_CODE_PORT=18626` and `T588_UPSTREAM_PORT=18627` while retaining its existing18620/18622defaults. In the Codespace container set the exact Code/Origin hostname, `T588_CODE_BIND=0.0.0.0`, and the manifest deadline. Reverse-forward only Codespace loopback18627 to workstation loopback18626, and verify the forwarded18626port remains private, anonymous access is denied, and Host/Origin/credential stripping still passes. `/config` returns session-expiring TURN credentials only through this authenticated edge; the shared relay key stays server-side. CDP/raw GPU ports remain private. No signaling credential or private key is included here.

The future GPU profile must set both the Isaac app/timeline and official NVIDIA SDK request to60fps; the previous native profile caps both at30. That native GPU change is not yet accepted. Validate full camera/menu/keyboard interaction, move-to-visible p50/p95, decoder/packet-loss behavior and a long observation on the actual route before switching the user to this candidate.

## Verification

```sh
python3 -m unittest discover -s . -p 'test_*.py' -v
node --check client.js
```

The12candidate configuration/protocol tests pass, alongside26existing boundary/input/proxy tests and JavaScript camera-coordinate tests. Source packet bytes/time-base/wrap, expired GPU rejection, invalid offers, Host/Origin, expiring HMAC credentials, public-IP enforcement, bounded ports and private-peer denial are covered. The previously missing Python `os.memfd_create` is handled through the same Linux libc API; no plaintext secret file fallback is used.
