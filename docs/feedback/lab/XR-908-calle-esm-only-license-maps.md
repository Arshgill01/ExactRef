# XR-908 — `@call-e/calle@0.7.0` is ESM-only (`require` throws), ships no LICENSE, declaration maps point at missing `src/`

## Finding

`npx @arethetypeswrong/cli --pack` on a fresh `npm pack` of `@call-e/calle@0.7.0`: CJS resolution is “ESM (dynamic import only)”. `require('@call-e/calle')` under Node 22 throws `ERR_PACKAGE_PATH_NOT_EXPORTED`. `publint` is clean. The tarball has no `LICENSE`, no `engines`, no `.js` sourcemaps; every `.d.ts` has `//# sourceMappingURL=*.d.ts.map` whose `sources` are `../src/*.ts` — files that are **not** in the pack. Git `v0.7.0` exists; git HEAD is unpublished `0.7.1` (XR-802). `sideEffects: false` and `files: [dist, README, package.json]` — tests/`.env` are **not** shipped (clean).

## Surface / version / commit or URL

- npm `@call-e/calle@0.7.0` tarball `call-e-calle-0.7.0.tgz` (26 files, 26.4 kB)
- Git `server-sdk-typescript` `2808e21` (`version: 0.7.1`, `files` includes `LICENSE`)
- attw 2026-09-14; Node v22

## Expected

Either a dual `exports.require` / CJS build, or README + `engines` saying “ESM only, Node ≥ 18/22”. MIT `LICENSE` in the tarball. Declaration maps omitted, or `src/` shipped, or `declarationMap: false`.

## Actual

**Observed** attw:

```text
⚠️ A require call resolved to an ESM JavaScript file ...
node16 (from CJS) │ ⚠️ ESM (dynamic import only)
```

**Observed**

```text
node --input-type=commonjs -e "require('@call-e/calle')"
# ERR_PACKAGE_PATH_NOT_EXPORTED No "exports" main defined in .../@call-e/calle/package.json

node --input-type=module -e "import * as x from '@call-e/calle'"
# ESM_OK [CalleClient, CalleAPIError, ...]
```

**Observed** `package.json`: `type: module`, `exports["."]: { types, import }` only, `license` field **absent**, `engines` **absent**. `tar -tzf` has no `LICENSE` / `src/` / tests. `index.d.ts.map` → `"sources":["../src/index.ts"]`.

`publint`: “All good!”

## Evidence

`/tmp/calle-lab/pkg/calle/` pack + attw + publint + cjs-test install of the tarball.

## Impact if an operator or agent trusted the current contract

CommonJS workers (`require`, older ts-node, some serverless) cannot load the SDK and “fall back” to raw `fetch` / a second create. Go-to-definition opens a missing `src/index.ts`. Downstream legal scanners report “no license file” on 0.7.0 even though git 0.7.1 added one.

## Ask

Publish 0.7.1 (or a 0.7.0 patch) with `LICENSE`, `engines.node`, and either CJS exports or an explicit “ESM only” README sentence. Stop emitting `.d.ts.map` in the pack (`declarationMap: false`) or include `src`.

## Do not claim

Refile of XR-701 (two `calle` bins) or XR-802 (unpublished 0.7.1 API fixes). That CJS is promised in the README (it never shows `require`).
