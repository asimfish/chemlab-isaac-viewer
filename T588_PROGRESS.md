Refs: T-588

Status: review; overall public delivery remains incomplete.

The owner completed Codespaces authorization. The first2-core container lacked SSH and was stopped before its replacement was created. The pinned SSH feature in the replacement worked; private18620 forwarding and reverse-SSH health checks passed. Both task-owned Codespaces are now Shutdown, and all six task-local gateway/transport services are inactive after the2026-10-22 00:11:55 deadline. The provider replica of job-4dn2pzj5s7f4 is Succeeded with ended_at1792599120000 (00:12:00 Taipei), so the old allocation is terminal. No new GPU allocation was submitted.

The GitHub browser route exposed a proxy Origin rewrite: legitimate requests became https://localhost:18620 while foreign Origin stayed unchanged. The exact normalized Origin is now allowed; foreign origins, missing WebSocket Origin and expired sessions remain rejected. Eight proxy live-socket tests plus eight original gateway tests pass. This establishes local boundary behavior, not browser GPU acceptance. The last browser run failed around expiry and its evidence is retained.

The fixed GitHub Pages entry is explicitly offline. Existing Cloudflare performance results belong only to that measured path. Renewal duration is awaiting the owner's choice. Follow up with old-job terminal verification, a new immutable30fps GPU bundle, four real GitHub video/input checks and separate GitHub latency measurements before enabling links.
