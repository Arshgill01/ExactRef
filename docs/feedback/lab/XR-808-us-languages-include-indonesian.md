# XR-808 — Official regions table lists Indonesian as a United States language

## Finding

The live Regions page and the integrations README (the page’s declared source) give the United States row as languages **English, Indonesian**. Indonesia’s own row is **English** only. That is inverted/wrong: US does not have Indonesian as a CALL-E locale in any other surface we read; Indonesia is the Indonesian-language country.

Docs `/regions` is generated from the README table (`calle-docs/src/regions.mjs` `REGIONS_SOURCE_URL` = the integrations README section).

## Surface / version / commit or URL

- Live https://docs.heycall-e.com/regions.md (fetched 2026-09-14), snapshotDate 2026-09-14, “22 countries”
- https://github.com/CALLE-AI/call-e-integrations README “Supported Regions and Languages” (`1ce9d77`)
- `calle-docs/src/regions.mjs` `extractRegions` / `REGIONS_README_URL`

## Expected

US: English (and any locales CALL-E actually routes, e.g. Spanish if supported). Indonesia: English and Indonesian (or Bahasa), matching the ID row’s calling code +62.

## Actual

Live `/regions.md` extract (2026-09-14):

```
| Indonesia | `ID` | +62 | English | International |
| United States of America | `US` | +1 | English, Indonesian | Local |
```

Same two rows in `integrations/README.md` (clone `1ce9d77`).

## Evidence

```
curl -sS https://docs.heycall-e.com/regions.md
# lines containing United States / Indonesia as quoted above
```

`regions.mjs` throws if the README table is missing — the bad cell is the source of truth, not a render bug.

Inferred: CALL-E does not actually offer an `id-US` locale. Observed: the published table prints Indonesian on US.

## Impact if an operator or agent trusted the current contract

An agent setting `locale: "id-ID"` or language “Indonesian” on a `region: "US"` recipient, or the reverse, gets `unsupported_language` / `unsupported_region` after a create (or a wrong-language call if the server is lenient). Onboarding “22 countries, updated September 14” looks authoritative.

## Ask

Swap the language cells (US: English; ID: English, Indonesian) or print the real locale list. Add a CI check that language names match the country row.

## Do not claim

- That we placed a US/Indonesian call.
- A specific locale tag the API accepts.
- Refile of XR-116 (E.164 length) or region GitHub issues 90 / 116 / 118 / 121.
- Refile of 109 / 123 / 126 / 127.
