# XR-305 — Extra-calls form cutoff is 12pm SGT on 14 Sep; Official Rules submission ends 11:45pm SGT

New. Fetched 2026-09-14. Form viewed only. Not submitted.

## Finding

The live additional-calls form tells hackathon users to request 200 calls “by September 14th at 12pm SGT” and to allow 1–5 business days. Official Rules close submissions at 14 September 11:45 **pm** SGT and say approved extra calls take one to five business days. On deadline day the form’s noon clock is already closed while Rules (and the Devpost header) still show ~11.75 hours of submission time. 1–5 business days cannot complete after noon on the last day.

## Surface / version / commit or URL

- Form (GET only): https://forms.gle/EPQttEZ1rkW8iq9q6 → https://docs.google.com/forms/d/e/1FAIpQLScmY7ybR7bvOFT63kbkdieV-WdmgSPkRxCJocSgyfAAnJUqlg/viewform
- Linked from https://call-e.devpost.com/ and Official Rules §4
- Rules HTML: https://call-e.devpost.com/rules
- Dates table: https://call-e.devpost.com/details/dates

## Expected

The form’s last-request time is printed next to Official Rules: submission 14 Sep 23:45 SGT; processing 1–5 business days; last useful request is several business days earlier. Rules prevail.

## Actual

Form `og:description` / page description (2026-09-14, no submit):

> Use this form to request 200 CALL-E calls for your Hackathon project by September 14th at 12pm SGT. Please note that additional call allocations are not guaranteed and are distributed on a first-come, first-served basis while supplies last.

> Please allow 1-5 business days for processing.

Official Rules §1 (HTML):

> Submission Period: … September 14, 2026 (11:45 pm SGT)

Official Rules §4:

> Approved additional call requests allocated to your CALL-E account are generally processed within one (1) to five (5) business days of completing the form, while supplies last.

Devpost header and dates table: `Deadline: Sep 14, 2026 @ 11:45pm SGT`.

Fetch time this lab: 2026-09-14 ~13:45 IST = 16:15 SGT. Form noon SGT had already passed. Rules / homepage deadline had not.

## Evidence

- `curl -sI` on the gle link → 302 to the viewform above.
- Form HTML title: `CALL-E Additional Calls Request Form`. Description quoted from `og:description`.
- Rules and dates table quoted in CONFIRM-XR-006.

## Impact if an operator or agent trusted the current contract

An agent that trusts only Devpost “11:45pm SGT” files the extra-calls form in the afternoon of the 14th. The form already closed at noon, or a request filed that afternoon cannot be processed in 1–5 business days before submission ends. That is a last-day lockout, not a duplicate call. Combined with XR-302/XR-303, a team that already burned the 20 free calls then retries create and places a call they cannot complete.

## Ask (docs PR outline — Devpost / form, not calle-docs)

On the form description, replace “by September 14th at 12pm SGT” with the Rules clocks printed together:

> Last request that can still be processed before submission ends must arrive several business days before 14 Sep 23:45 SGT. Official Rules: 1–5 business days. Form noon cutoff is not the submission deadline.

On Devpost “Request additional calls via this form,” add the same two clocks.

## Do not claim

- Form was not submitted. No allocation was requested.
- Not XR-006 (missing Feedback row / judging 9:00 vs 10:00).
- Do not claim Rules say 11:45 am SGT.
