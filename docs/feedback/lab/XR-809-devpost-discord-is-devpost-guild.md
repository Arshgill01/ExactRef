# XR-809 — Devpost “Discord” lands on the Devpost guild; CALL-E’s guild is a different invite

## Finding

Two public Discord invite codes are both labeled as the place to get CALL-E help. They resolve to **different guilds**.

| Invite | Where it is linked | Discord API `guild.name` / `guild.id` |
| --- | --- | --- |
| `discord.com/invite/HP4BhW3hnp` | Devpost homepage; resources page footer “Discord” | **Devpost** / `861966823054639134` (~66k members) |
| `discord.gg/6AbXUzUV8w` | Integrations README; resources “CALL-E Discord community!” | **CALL-E** / `1493880186826133504` (~715 members) |

Official Rules / quickstart testing-hotline chatter lives on the CALL-E server (quickstart links a channel under guild `1493880186826133504`). Homepage Discord does not.

## Surface / version / commit or URL

- https://call-e.devpost.com/ (fetched 2026-09-14) footer Discord = `HP4BhW3hnp`
- https://call-e.devpost.com/resources “Contact Us & Support Channels” = `6AbXUzUV8w`; footer Discord = `HP4BhW3hnp`
- https://github.com/CALLE-AI/call-e-integrations README header + Community = `6AbXUzUV8w`
- Public Discord invite metadata: `GET https://discord.com/api/v9/invites/{code}?with_counts=true` (no join, no post)

## Expected

Every contest “Discord” control would open the CALL-E hackathon server. Footer and “CALL-E Discord community” would be the same guild.

## Actual

Read-only invite lookup 2026-09-14:

```
6AbXUzUV8w → guild_id 1493880186826133504 guild_name CALL-E approximate_member_count 715
HP4BhW3hnp → guild_id 861966823054639134 guild_name Devpost approximate_member_count 66821
```

Resources page HTML contains both hrefs. Homepage contains only the Devpost guild invite.

## Evidence

- `curl` of homepage + `/resources` (200)
- Discord API 200 JSON fields above (no tokens, no message content)
- integrations README lines 13 and 503

XR-006 (dates table vs Feedback Period) remains true; this is not that card.

## Impact if an operator or agent trusted the current contract

A hackathon team that clicks the Devpost header/footer Discord never reaches CALL-E staff, the testing-hotline thread, or product support. They ask in the general Devpost server. Feedback Period work (Most Valuable Feedback) that depends on Discord answers is delayed or posted in the wrong place.

## Ask

Point every Devpost Discord control at `discord.gg/6AbXUzUV8w` (or one canonical CALL-E invite). Keep the Devpost community link labeled “Devpost Discord,” not “Discord.”

## Do not claim

- That we posted in either Discord.
- Member counts as a prize metric beyond the lookup.
- Refile of XR-006 (dates) or XR-305 (extra-calls form).
- Refile of 109 / 123 / 126 / 127.
