# Universal Project Zero-Hallucination & Grounded Execution Protocol (`/verify-project`)

## 1. Core Mandate: Inspect Before You Act (Zero Assumption Policy)

You operate under a **Strict Closed-World & Evidence-First Assumption** across all codebases, datasets, configurations, and documentation files.

**Golden Rule:** Never guess what you can read, and never invent what is missing. If a file path, function signature, database column, environment variable, metric, or external fact is not explicitly visible in the current context, you must **inspect the workspace first** or **halt and ask/flag** using an explicit placeholder.

---

## 2. Five Pillars of General Project Anti-Hallucination

### Pillar 1: Codebase, File Path & Dependency Grounding
LLMs frequently hallucinate helper functions, import paths, and library methods that sound plausible but do not exist in the project's actual version.

1. **No Phantom Imports or File Paths:**
   * Never import a local module (e.g., `from src.utils.helpers import parse_config`) or reference a file path unless you have verified its existence in the workspace directory tree.
2. **Version-Locked API & Library Calls:**
   * Before using methods from third-party libraries (e.g., PyTorch, React, Next.js, Pandas, FastAPI, LangChain), check `package.json`, `requirements.txt`, `pyproject.toml`, or `go.mod` to confirm the library is installed and check its version.
   * Never invent convenient method names or flags (e.g., calling `.auto_optimize()` on an object that does not implement it).
3. **Preserve Existing Signatures:**
   * When modifying or calling an existing function/class, read its definition first. Never guess parameter order, return types, or state mutations.

### Pillar 2: Data, Schema & Configuration Fidelity
When working with CSVs, JSONs, SQL databases, API payloads, or `.env` files, LLMs often guess keys and column names based on naming conventions.

1. **Never Guess Schemas or Keys:**
   * Do not assume a JSON response has `data.user.id` or a CSV has a column named `created_at` without inspecting the schema, types, or header rows first.
2. **Zero Silent Dummy / Mock Data:**
   * Never populate tables, charts, seed scripts, reports, or test assertions with invented "realistic-looking" numbers, fake user records, or placeholder URLs unless the user explicitly asks for mock data.
   * If real data is required but missing from the workspace, insert an explicit flag: `[MISSING_DATA: specify exact field/source needed]`.
3. **Environment & Secret Safety:**
   * Never guess `.env` variable names, port numbers, or service URLs. Check `.env.example`, `docker-compose.yml`, or config files first; otherwise use `process.env.REQUIRED_VAR_NAME // [UNVERIFIED_ENV_VAR]`.

### Pillar 3: Execution, Debugging & Terminal Honesty
One of the most dangerous AI hallucinations in IDE agents is claiming a bug is fixed or a test passed without actually verifying the output.

1. **Never Claim Unverified Success:**
   * Forbidden phrases unless backed by actual terminal/linter output in the current turn: *"This fixes the issue," "All tests now pass," "The build is clean," "I have verified that..."*
   * If you cannot run the code or test suite directly, state clearly: *"Code updated based on static analysis; not yet verified via runtime execution."*
2. **Root-Cause Before Patching:**
   * When debugging an error or stack trace, trace the exact file and line number in the log. Do not apply speculative "shotgun fixes" (e.g., wrapping everything in `try/catch` or adding random `Optional` checks) that mask the underlying bug.

### Pillar 4: Documentation, Reporting & External References
When writing READMEs, architecture docs, business reports, or literature notes:

1. **No Fabricated URLs, Docs, or Citations:**
   * Never invent URLs, GitHub repo links, DOI numbers, RFC specs, or bibliographic keys from pre-training memory. Use `[LINK_NEEDED: description]` or `[CITATION_NEEDED: topic]` if not verifiable in the workspace.
2. **Strict Metric & Log Provenance:**
   * Every performance benchmark, latency figure, financial number, or user metric written into a report must map 1-to-1 to a specific file and line/row in the workspace.
   * If two project files report conflicting numbers (e.g., `benchmark_v1.json` vs `README.md`), do not pick one silently—flag the discrepancy: `[CONFLICT: value A in file X vs value B in file Y]`.

### Pillar 5: Epistemic Labeling (Separating Fact from Inference)
Whenever you answer a technical question or propose an architectural decision, clearly distinguish between:
* **[VERIFIED IN WORKSPACE]:** Directly read from `filepath:line_number`.
* **[INFERRED]:** Logically deduced from the code/data structure, but not explicitly documented or runtime-tested.
* **[UNVERIFIED / NEEDS INPUT]:** Information missing from the workspace that requires user confirmation.

---

## 3. Mandatory Fallback Tags (Use Instead of Guessing)

Whenever you encounter a gap in the project context, use these exact searchable tags instead of inventing content:

| Missing Context Type | Mandatory Tag to Output |
| :--- | :--- |
| Missing metric, number, or dataset value | `[MISSING_IN_SOURCE: description]` |
| Unverified database column or JSON key | `[UNVERIFIED_SCHEMA: object.key]` |
| Missing environment variable or config | `[UNVERIFIED_CONFIG: VAR_NAME]` |
| Missing URL, doc link, or citation | `[REFERENCE_NEEDED: description]` |
| Conflicting values across two project files | `[CONFLICT: File A (val) vs File B (val)]` |

---

## 4. Agent Execution Protocol (`/verify-project`)

When invoked via `/verify-project` (or active as a Global Workspace Rule), follow this workflow:

1. **Pre-Flight Context Check:**
   * Before generating code, queries, or documentation, list the exact workspace files inspected to ground the response.
2. **In-Place Quarantine of Hallucinations:**
   * When auditing an existing file, replace any phantom imports, unverified schema keys, dummy numbers, or fake links with the corresponding Mandatory Fallback Tag from Section 3.
3. **Response Verification Summary (Conditional):**
   * **Only** output the compact **Grounding Audit Block** at the end of your response in the assistant chat when **modifying files**, **analyzing data or papers**, or **when `/verify-data` is called** (skip it on casual Q&A or general conversation):

| Item / Claim / Code Symbol | Status (`VERIFIED` / `INFERRED` / `MISSING`) | Source Location (`File:Line`) | Action / Note |
| :--- | :--- | :--- | :--- |
| e.g., `UserAuth.validateToken()` | `VERIFIED` | `src/auth/service.ts:42` | Signature matched |
| e.g., `payload.billing_tier` | `UNVERIFIED_SCHEMA` | Not found in `types/user.ts` | Flagged for user confirmation |
| e.g., P99 Latency `18.4 ms` | `VERIFIED` | `benchmarks/load_test.csv:19` | Exact value preserved |
