# Safety

- Place a live call only when the user names a consented E.164 number and sets `EXACTREF_LIVE=1`. The board default is fixture replay.
- Do not guess phone numbers, country codes, language, region, `plan_id`, `confirm_token`, or `run_id`.
- Do not print API keys, OAuth tokens, or raw destination numbers. Show `destinationLabel`.
- Do not put the intended identifier, private account numbers, or real customer names in the outbound task.
- Do not write `mismatch`, `spoken_only`, `conversational_confirmed`, or `unknown` into a system of record as a verified fact.
- Do not treat unsigned CALL-E webhooks as authority. Re-fetch the stored call id with the API key.
- Do not treat a local wait timeout as cancellation. CALL-E has no client cancel after accept.
- Do not invoke `track_ui_events`.
- Medical, legal, emergency, and payment-card content is out of scope.
- Mask identifiers in summaries when they are longer than four characters: keep the last four, replace the rest with `•`.
- Recurring schedules are out of scope. There is nothing to cancel except “do not press Replay / Create again.”
