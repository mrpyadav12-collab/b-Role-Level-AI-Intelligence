# Model and library inventory

| Library / model | Purpose | Version | License | Open-source / free-tier / locally runnable | Notes |
|---|---|---:|---|---|---|
| FastAPI | Python API backend | current | MIT | Open-source | Used for REST endpoints |
| SQLite | Local relational database | built-in | Public domain | Open-source | Used for persistent storage |
| httpx | HTTP client | current | BSD-3-Clause | Open-source | Used for AI gateway calls |
| pytest | Testing | current | MIT | Open-source | Used for unit and API tests |
| Next.js | Frontend framework | 16 | MIT | Open-source | Used for UI |
| React | UI library | 19 | MIT | Open-source | Used for dashboard components |
| TypeScript | Frontend typing | current | Apache 2.0 | Open-source | Used for dev safety |
| Tailwind CSS | Styling | current | MIT | Open-source | Used for UI styling |
| shadcn/ui patterns | UI system patterns | current | MIT | Open-source | Used for design consistency |

## AI model note
The app is designed to use an OpenAI-compatible gateway, but it falls back gracefully if unavailable. No paid dependency is required for the demo path.
