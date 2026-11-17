# MediRAG Performance V5

Targeted patch for **Stage 3 + V4** modular backend and Stage 2 optional chat components.

- Bounded conversation history SQL query (latest 8, preserves V4 context).
- Real server-side timing breakdown + `Server-Timing` and `X-MediRAG-Route`.
- Reuse model SDK client per worker; configurable 30 second model API timeout (`MEDIRAG_MODEL_TIMEOUT_S`).
- Frontend no longer keeps the spinner active while waiting for the entire company/dashboard refresh.
- Neutral loading text for fast answers; memoized Markdown message bubbles.
- No DB schema change; no new libraries.

Read `INSTALL.md` for install, tests, rollback and limitations.
