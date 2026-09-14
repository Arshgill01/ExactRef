# ExactRef context

ExactRef is not a calling desk. It is the write-gate after a CALL-E call that produced an identifier.

The only writable provenance is `independently_verified`: a human typed the value and claimed a second channel. Readback-plus-yes is `conversational_confirmed`. A one-character substitution against an intended value is `mismatch` even when the recipient said yes.

An `exception` is the operational event that produced one or more identifier writes. `OH-01` is the off-hire exception from the 2026-09-05 live call. OffHire Desk is not a product in this tree. It is retired theater. The exception remains.

Do not leak intended identifiers into outbound tasks. Do not treat `queued` plus attempt activity as idle. Do not treat a local wait timeout as hangup. Do not invoke undocumented MCP tools.
