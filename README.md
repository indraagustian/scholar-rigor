# ScholarRigor

**Multi-agent academic writing, Turnitin AI-detection calibration, PRISMA 2020 systematic review synthesis, and closed-world zero-hallucination verification suite.**

Built on a **Single Source of Truth** (`skills/` + `rules/AGENTS.md`) with zero mandatory runtime dependencies (Python 3 stdlib core; optional `pymupdf` for Turnitin PDF parsing) and thin adapters for **Google Antigravity**, **Claude Code**, **OpenAI Codex**, **Cursor**, **Gemini CLI**, and any **AgentSkills-compatible** coding agent.

---

## Core Capabilities

| Skill / Rule | Purpose | Key Features |
| :--- | :--- | :--- |
| **`anti-slop`** | Q1 IEEE / Elsevier manuscript drafting & Turnitin de-AI calibration | Extracts Turnitin highlighted blocks (`extract_turnitin.py`), audits 250-word window burstiness & discourse openers (`stylometry_audit.py`), enforces structural rhythm (`<20%` AI score target), protects LaTeX macros/citations/metrics. |
| **`anti-slop-slr`** | Systematic Literature Reviews (PRISMA 2020) | Synthesizes screening logs and extraction matrices into non-formulaic prose without inventing paper counts, years, or bibliographic keys. |
| **`verify-data`** | Closed-world grounding & integrity audit | Deterministic stdlib checks (`verify_grounding.py`) for `\cite{}` vs `.bib` keys, `\label{}`/`\ref{}` parity, numeric drift against baseline drafts, and placeholder leak scans. |
| **`rules/AGENTS.md`** | Always-on Zero-Hallucination Protocol | Enforces evidence-first workspace inspection, explicit missing-data tags (`[MISSING_IN_SOURCE: ...]`), and grounding audit tables on scientific edits. |

---

## Supported Coding Agents

ScholarRigor ships canonical AgentSkills (`SKILL.md`), thin native slash-command/rule adapters, and a one-command cross-agent installer (`scripts/install.py`):

| Agent Platform | Global Install Path | Workspace Install Path | Native Trigger / Command |
| :--- | :--- | :--- | :--- |
| **Google Antigravity** | `~/.gemini/config/plugins/scholar-rigor/` | `.agents/skills/` + `.agents/rules/zero-hallucination.md` | `/anti-slop`, `/anti-slop-slr`, `/verify-data` |
| **Claude Code** | `~/.claude/skills/` + `~/.claude/commands/` | `.claude/skills/` + `.claude/commands/` | `/anti-slop`, `/anti-slop-slr`, `/verify-data` |
| **OpenAI Codex** | `~/.codex/skills/` + `~/.codex/prompts/` | `.agents/skills/` + `AGENTS.md` | `$anti-slop` / `/prompts:anti-slop` |
| **Cursor** | Cursor Settings -> Rules (`rules/AGENTS.md`) | `.cursor/rules/*.mdc` | `@manuscript-writing.mdc` + always-on `.mdc` |
| **Gemini CLI** | `~/.gemini/commands/scholar-rigor/` + `~/.gemini/skills/` | `.gemini/commands/scholar-rigor/` + `.gemini/skills/` | `/scholar-rigor:anti-slop`, `/scholar-rigor:verify-data` |
| **Generic AgentSkills** (OpenCode, Windsurf, Cline, Goose) | `~/.agents/skills/` | `.agents/skills/` + `AGENTS.md` | Agent skill discovery / natural prompt |
| **Standalone CLI** | Any checkout | Any checkout | `python skills/.../scripts/*.py` |

> **Safe Instruction Defaults:** Root instruction files (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`) are **not** overwritten by default during installation. Pass `--with-instructions` (plus `--force` only if replacing an existing file) or merge them manually.

---

## Quick Installation

Clone the repository once:

```bash
git clone https://github.com/indraagustian/scholar-rigor.git
cd scholar-rigor
```

Optional dependency (only required if you parse Turnitin AI Report PDFs with `extract_turnitin.py`):

```bash
pip install -r requirements.txt
```

### One-Command Installer (`scripts/install.py`)

Preview any install safely with `--dry-run`:

```bash
# Install globally for your preferred agent
python scripts/install.py --agent antigravity --scope global
python scripts/install.py --agent claude --scope global
python scripts/install.py --agent codex --scope global
python scripts/install.py --agent gemini --scope global

# Install globally across all supported agents at once
python scripts/install.py --agent all --scope global --dry-run
python scripts/install.py --agent all --scope global

# Install into a specific LaTeX / Markdown paper repository (includes Cursor .cursor/rules/*.mdc)
python scripts/install.py --agent all --scope workspace --target /path/to/your-paper --with-instructions
```

Installer flags:
- `--agent {antigravity,claude,codex,cursor,gemini,agentskills,all}`: Target agent platform.
- `--scope {global,workspace}`: Install in user home config (`global`) or project repo (`workspace`).
- `--target <dir>`: Target project directory when `--scope workspace` (defaults to current working directory).
- `--with-instructions`: Also write `AGENTS.md` / `CLAUDE.md` / `GEMINI.md` if missing.
- `--force`: Overwrite existing root instruction files when `--with-instructions` is active.
- `--dry-run`: Print every planned action without modifying the filesystem.

---

## Manual Setup per Agent

If you prefer not to run `scripts/install.py`:

<details>
<summary><strong>Google Antigravity (Plugin or Workspace)</strong></summary>

- **Global plugin:** Copy `plugin.json`, `README.md`, `rules/AGENTS.md` (plain Markdown, no frontmatter), and `skills/` into `~/.gemini/config/plugins/scholar-rigor/`.
- **Workspace kit:** Copy `skills/*` into `<repo>/.agents/skills/` and copy `rules/AGENTS.md` into `<repo>/.agents/rules/zero-hallucination.md` prepended with:
  ```markdown
  ---
  trigger: always_on
  ---
  ```

</details>

<details>
<summary><strong>Claude Code</strong></summary>

- Copy `skills/*` to `~/.claude/skills/` (or `<repo>/.claude/skills/`).
- Copy `adapters/claude-code/commands/*.md` to `~/.claude/commands/` (or `<repo>/.claude/commands/`).
- Optionally merge `CLAUDE.md` into `~/.claude/CLAUDE.md` or `<repo>/CLAUDE.md`.

</details>

<details>
<summary><strong>OpenAI Codex</strong></summary>

- Copy `skills/*` to `~/.codex/skills/` (global) or `<repo>/.agents/skills/` (workspace).
- Copy `adapters/claude-code/commands/*.md` to `~/.codex/prompts/`.
- Optionally merge `AGENTS.md` into `~/.codex/AGENTS.md` or `<repo>/AGENTS.md`.

</details>

<details>
<summary><strong>Cursor</strong></summary>

- Copy `adapters/cursor/rules/*.mdc` into `<repo>/.cursor/rules/`.
- For global user rules across all Cursor workspaces, paste the contents of `rules/AGENTS.md` into **Cursor Settings -> Rules**.

</details>

<details>
<summary><strong>Gemini CLI</strong></summary>

- Copy `adapters/gemini-cli/commands/*.toml` into `~/.gemini/commands/scholar-rigor/` (or `<repo>/.gemini/commands/scholar-rigor/`).
- Copy `skills/*` into `~/.gemini/skills/` (or `<repo>/.gemini/skills/`).
- Optionally merge `GEMINI.md` into `~/.gemini/GEMINI.md` or `<repo>/GEMINI.md`.

</details>

---

## Usage Workflows & Examples

See [`examples/prompts.md`](examples/prompts.md) for copy-paste prompts per agent and [`examples/sample_audit.md`](examples/sample_audit.md) for a before/after structural revision walkthrough.

### Recommended Iteration Loop (Turnitin `<20%` Target)

1. **Extract Flagged Blocks (`extract_turnitin.py`)**
   ```bash
   python skills/anti-slop/scripts/extract_turnitin.py turnitin_report.pdf --full
   ```
   Parses highlighted spans and section proportions directly from the PDF instead of guessing which paragraphs triggered the detector.

2. **Surgical Structural Rewrite (`anti-slop`)**
   - Modify **only** flagged paragraphs; leave unflagged sections untouched so clean human blocks remain intact.
   - Break uniform 16–24 word sentence strings into sharp alternations: short empirical pivots (`5–11` words) followed by mechanism-rich technical explanations (`28–45+` words).
   - Remove formulaic sentence-initial discourse markers (`In addition,`, `Furthermore,`, `On the other hand,`, `To address this issue,`). Link sentences through shared technical nouns, equations, tensor shapes, or quantitative contrasts.

3. **Local Stylometry & Grounding Gate (`stylometry_audit.py` + `verify_grounding.py`)**
   ```bash
   python skills/anti-slop/scripts/stylometry_audit.py main_revised.tex --baseline main_original.tex --window 250
   python skills/verify-data/scripts/verify_grounding.py main_revised.tex --bib references.bib --baseline main_original.tex
   ```
   Confirms high length burstiness (`std`, `CV`), low formulaic opener density, intact `\cite{}` keys, balanced `\label{}`/`\ref{}`, and zero invented metrics before uploading a new draft to Turnitin.

---

## Turnitin Calibration Lessons (What Actually Triggers Flags)

See [`skills/anti-slop/references/turnitin_lessons.md`](skills/anti-slop/references/turnitin_lessons.md) for full details distilled from empirical Turnitin AI Writing reports:

- **250-word sliding windows:** Turnitin evaluates local paragraph blocks rather than isolated sentences. Fixing 3 sentences in a 250-word uniform block often leaves the window flagged until adjacent transitions are broken up.
- **Synonym swapping is insufficient:** Changing adjectives (`"effectively improves"` -> `"substantially enhances"`) leaves underlying syntax cadence untouched and barely lowers detection scores.
- **LaTeX & bibliography immunity:** Never fabricate data, drop `\cite{}` entries, alter equation labels, or change reported benchmark precision to satisfy style targets.

---

## Repository Structure

```text
scholar-rigor/
├── plugin.json                              # Google Antigravity plugin manifest
├── AGENTS.md                                # Root instructions (Codex / Antigravity / generic)
├── CLAUDE.md                                # Root instructions (Claude Code)
├── GEMINI.md                                # Root instructions (Gemini CLI)
├── requirements.txt                         # Optional pymupdf dependency for PDF parsing
├── LICENSE                                  # MIT License
├── rules/
│   └── AGENTS.md                            # Always-on closed-world zero-hallucination rule
├── skills/
│   ├── anti-slop/
│   │   ├── SKILL.md
│   │   ├── references/turnitin_lessons.md
│   │   └── scripts/
│   │       ├── extract_turnitin.py          # Turnitin highlight & score extractor (PyMuPDF)
│   │       └── stylometry_audit.py          # Local burstiness & opener audit (stdlib)
│   ├── anti-slop-slr/
│   │   └── SKILL.md                         # PRISMA 2020 SLR synthesis skill
│   └── verify-data/
│       ├── SKILL.md
│       └── scripts/
│           └── verify_grounding.py          # LaTeX citation/label/metric audit (stdlib)
├── adapters/
│   ├── claude-code/commands/                # .md slash commands (Claude Code & Codex prompts)
│   ├── cursor/rules/                        # .mdc project rules (Cursor)
│   └── gemini-cli/commands/                 # .toml slash commands (Gemini CLI)
├── scripts/
│   └── install.py                           # Cross-agent global/workspace installer (stdlib)
└── examples/
    ├── prompts.md                           # Per-agent prompt examples
    └── sample_audit.md                      # Before/after structural rewrite & audit sample
```

---

## License

MIT — see [`LICENSE`](LICENSE).
