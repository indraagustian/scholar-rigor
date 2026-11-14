#!/usr/bin/env python3
"""
Cross-agent installer for ScholarRigor (scholar-rigor).

Installs skills, command adapters, and zero-hallucination rules for:
  - Google Antigravity
  - Claude Code
  - OpenAI Codex
  - Cursor
  - Gemini CLI
  - Generic AgentSkills-compatible agents (.agents/skills/ + AGENTS.md)

Uses Python 3 standard library only (zero third-party dependencies).
"""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys


SUPPORTED_AGENTS = (
    "antigravity",
    "claude",
    "codex",
    "cursor",
    "gemini",
    "agentskills",
)

SKILL_NAMES = ("anti-slop", "anti-slop-slr", "verify-data")


def ignore_junk(_directory: str, names: list[str]) -> set[str]:
    """Ignore Python cache artifacts during directory copies."""
    ignored: set[str] = set()
    for name in names:
        if name == "__pycache__" or name.endswith((".pyc", ".pyo")):
            ignored.add(name)
    return ignored


def ensure_dir(path: Path, dry_run: bool) -> None:
    """Create directory if needed unless running in dry-run mode."""
    if not dry_run:
        path.mkdir(parents=True, exist_ok=True)


def copy_file(
    src: Path,
    dst: Path,
    *,
    dry_run: bool,
    force: bool = True,
    skip_if_exists: bool = False,
) -> None:
    """Copy a single file with dry-run and non-destructive overwrite handling."""
    if not src.exists():
        print(f"[WARN] Missing source file: {src}", file=sys.stderr)
        return

    if dst.exists() and skip_if_exists and not force:
        print(f"[SKIP] {dst} already exists (re-run with --force to overwrite)")
        return

    action = "DRY-RUN" if dry_run else "COPY"
    print(f"[{action}] {src} -> {dst}")
    if not dry_run:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def write_text(
    text: str,
    dst: Path,
    *,
    dry_run: bool,
    force: bool = True,
    skip_if_exists: bool = False,
    label: str = "generated content",
) -> None:
    """Write text content to destination path with dry-run support."""
    if dst.exists() and skip_if_exists and not force:
        print(f"[SKIP] {dst} already exists (re-run with --force to overwrite)")
        return

    action = "DRY-RUN" if dry_run else "WRITE"
    print(f"[{action}] {label} -> {dst}")
    if not dry_run:
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(text, encoding="utf-8")


def copy_tree(src: Path, dst: Path, *, dry_run: bool) -> None:
    """Recursively copy a directory tree, updating existing files cleanly."""
    if not src.exists():
        print(f"[WARN] Missing source directory: {src}", file=sys.stderr)
        return

    action = "DRY-RUN" if dry_run else "SYNC"
    print(f"[{action}] {src} -> {dst}")
    if not dry_run:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src, dst, dirs_exist_ok=True, ignore=ignore_junk)


def install_skills(repo_root: Path, skills_dst: Path, *, dry_run: bool) -> None:
    """Copy all bundled ScholarRigor skills into a target skills root."""
    for skill in SKILL_NAMES:
        copy_tree(repo_root / "skills" / skill, skills_dst / skill, dry_run=dry_run)


def install_instruction_file(
    src: Path,
    dst: Path,
    *,
    with_instructions: bool,
    force: bool,
    dry_run: bool,
) -> None:
    """Optionally install a root instruction file without clobbering user edits."""
    if not with_instructions:
        print(
            f"[INFO] Instruction file not auto-copied to {dst}. "
            f"Pass --with-instructions or merge {src.name} manually."
        )
        return
    copy_file(src, dst, dry_run=dry_run, force=force, skip_if_exists=True)


def install_antigravity(
    repo_root: Path,
    scope: str,
    target: Path,
    *,
    dry_run: bool,
    force: bool,
    with_instructions: bool,
) -> None:
    """Install ScholarRigor as a global Antigravity plugin or workspace .agents kit."""
    print("\n=== Google Antigravity ===")
    if scope == "global":
        plugin_dir = Path.home() / ".gemini" / "config" / "plugins" / "scholar-rigor"
        copy_file(repo_root / "plugin.json", plugin_dir / "plugin.json", dry_run=dry_run)
        if (repo_root / "README.md").exists():
            copy_file(repo_root / "README.md", plugin_dir / "README.md", dry_run=dry_run)
        # Global Antigravity plugin rules must be plain Markdown without YAML frontmatter.
        copy_file(
            repo_root / "rules" / "AGENTS.md",
            plugin_dir / "rules" / "AGENTS.md",
            dry_run=dry_run,
        )
        install_skills(repo_root, plugin_dir / "skills", dry_run=dry_run)
    else:
        agents_dir = target / ".agents"
        install_skills(repo_root, agents_dir / "skills", dry_run=dry_run)
        rule_text = (repo_root / "rules" / "AGENTS.md").read_text(encoding="utf-8")
        workspace_rule = f"---\ntrigger: always_on\n---\n\n{rule_text}"
        write_text(
            workspace_rule,
            agents_dir / "rules" / "zero-hallucination.md",
            dry_run=dry_run,
            force=force,
            skip_if_exists=False,
            label="workspace always_on rule (from rules/AGENTS.md)",
        )
        install_instruction_file(
            repo_root / "AGENTS.md",
            target / "AGENTS.md",
            with_instructions=with_instructions,
            force=force,
            dry_run=dry_run,
        )


def install_claude(
    repo_root: Path,
    scope: str,
    target: Path,
    *,
    dry_run: bool,
    force: bool,
    with_instructions: bool,
) -> None:
    """Install skills, slash commands, and optional CLAUDE.md for Claude Code."""
    print("\n=== Claude Code ===")
    base = Path.home() / ".claude" if scope == "global" else target / ".claude"
    install_skills(repo_root, base / "skills", dry_run=dry_run)
    cmd_src = repo_root / "adapters" / "claude-code" / "commands"
    for md_file in sorted(cmd_src.glob("*.md")):
        copy_file(md_file, base / "commands" / md_file.name, dry_run=dry_run)
    inst_dst = base / "CLAUDE.md" if scope == "global" else target / "CLAUDE.md"
    install_instruction_file(
        repo_root / "CLAUDE.md",
        inst_dst,
        with_instructions=with_instructions,
        force=force,
        dry_run=dry_run,
    )


def install_codex(
    repo_root: Path,
    scope: str,
    target: Path,
    *,
    dry_run: bool,
    force: bool,
    with_instructions: bool,
) -> None:
    """Install skills, custom prompts, and optional AGENTS.md for OpenAI Codex."""
    print("\n=== OpenAI Codex ===")
    if scope == "global":
        codex_home = Path.home() / ".codex"
        install_skills(repo_root, codex_home / "skills", dry_run=dry_run)
        cmd_src = repo_root / "adapters" / "claude-code" / "commands"
        for md_file in sorted(cmd_src.glob("*.md")):
            copy_file(md_file, codex_home / "prompts" / md_file.name, dry_run=dry_run)
        install_instruction_file(
            repo_root / "AGENTS.md",
            codex_home / "AGENTS.md",
            with_instructions=with_instructions,
            force=force,
            dry_run=dry_run,
        )
    else:
        install_skills(repo_root, target / ".agents" / "skills", dry_run=dry_run)
        print(
            "[INFO] Codex custom prompts are user-level (~/.codex/prompts/). "
            "Run with --agent codex --scope global to install slash prompts."
        )
        install_instruction_file(
            repo_root / "AGENTS.md",
            target / "AGENTS.md",
            with_instructions=with_instructions,
            force=force,
            dry_run=dry_run,
        )


def install_cursor(
    repo_root: Path,
    scope: str,
    target: Path,
    *,
    dry_run: bool,
    force: bool,
    with_instructions: bool,
) -> None:
    """Install .cursor/rules/*.mdc project rules (workspace scope)."""
    print("\n=== Cursor ===")
    if scope == "global":
        print(
            "[NOTE] Cursor stores global User Rules inside the Cursor app UI rather than dotfiles.\n"
            "       Use `--agent cursor --scope workspace --target <project-dir>` to install .cursor/rules/*.mdc,\n"
            "       or paste rules/AGENTS.md into Cursor Settings -> Rules."
        )
        return

    rules_src = repo_root / "adapters" / "cursor" / "rules"
    rules_dst = target / ".cursor" / "rules"
    for mdc_file in sorted(rules_src.glob("*.mdc")):
        copy_file(mdc_file, rules_dst / mdc_file.name, dry_run=dry_run)
    install_instruction_file(
        repo_root / "AGENTS.md",
        target / "AGENTS.md",
        with_instructions=with_instructions,
        force=force,
        dry_run=dry_run,
    )


def install_gemini(
    repo_root: Path,
    scope: str,
    target: Path,
    *,
    dry_run: bool,
    force: bool,
    with_instructions: bool,
) -> None:
    """Install TOML slash commands, skills, and optional GEMINI.md for Gemini CLI."""
    print("\n=== Gemini CLI ===")
    base = Path.home() / ".gemini" if scope == "global" else target / ".gemini"
    cmd_src = repo_root / "adapters" / "gemini-cli" / "commands"
    cmd_dst = base / "commands" / "scholar-rigor"
    for toml_file in sorted(cmd_src.glob("*.toml")):
        copy_file(toml_file, cmd_dst / toml_file.name, dry_run=dry_run)
    install_skills(repo_root, base / "skills", dry_run=dry_run)
    inst_dst = base / "GEMINI.md" if scope == "global" else target / "GEMINI.md"
    install_instruction_file(
        repo_root / "GEMINI.md",
        inst_dst,
        with_instructions=with_instructions,
        force=force,
        dry_run=dry_run,
    )


def install_agentskills(
    repo_root: Path,
    scope: str,
    target: Path,
    *,
    dry_run: bool,
    force: bool,
    with_instructions: bool,
) -> None:
    """Install portable AgentSkills directory (.agents/skills/) and AGENTS.md."""
    print("\n=== Generic AgentSkills (.agents/skills + AGENTS.md) ===")
    if scope == "global":
        skills_dst = Path.home() / ".agents" / "skills"
        inst_dst = Path.home() / ".agents" / "AGENTS.md"
    else:
        skills_dst = target / ".agents" / "skills"
        inst_dst = target / "AGENTS.md"
    install_skills(repo_root, skills_dst, dry_run=dry_run)
    install_instruction_file(
        repo_root / "AGENTS.md",
        inst_dst,
        with_instructions=with_instructions,
        force=force,
        dry_run=dry_run,
    )


INSTALLERS = {
    "antigravity": install_antigravity,
    "claude": install_claude,
    "codex": install_codex,
    "cursor": install_cursor,
    "gemini": install_gemini,
    "agentskills": install_agentskills,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install ScholarRigor skills, commands, and zero-hallucination rules."
    )
    parser.add_argument(
        "--agent",
        required=True,
        choices=[*SUPPORTED_AGENTS, "all"],
        help="Target agent platform or 'all'.",
    )
    parser.add_argument(
        "--scope",
        default="global",
        choices=["global", "workspace"],
        help="Install into user home config ('global') or a project repo ('workspace').",
    )
    parser.add_argument(
        "--target",
        type=Path,
        default=Path.cwd(),
        help="Target repository directory when --scope workspace (defaults to cwd).",
    )
    parser.add_argument(
        "--with-instructions",
        action="store_true",
        help="Also install root instruction files (AGENTS.md / CLAUDE.md / GEMINI.md) if absent.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing root instruction files when --with-instructions is set.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned filesystem actions without writing files.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parent.parent

    if not (repo_root / "skills").is_dir() or not (repo_root / "rules" / "AGENTS.md").is_file():
        print(
            f"[ERROR] Invalid scholar-rigor repository layout at {repo_root}",
            file=sys.stderr,
        )
        return 1

    target = args.target.resolve()
    if args.scope == "workspace" and not target.exists():
        if args.dry_run:
            print(f"[DRY-RUN] Would create target workspace directory: {target}")
        else:
            target.mkdir(parents=True, exist_ok=True)

    selected = list(SUPPORTED_AGENTS) if args.agent == "all" else [args.agent]
    print(f"ScholarRigor Installer | scope={args.scope} | dry_run={args.dry_run}")
    if args.scope == "workspace":
        print(f"Target workspace: {target}")

    for agent_name in selected:
        INSTALLERS[agent_name](
            repo_root,
            args.scope,
            target,
            dry_run=args.dry_run,
            force=args.force,
            with_instructions=args.with_instructions,
        )

    print("\nDone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
