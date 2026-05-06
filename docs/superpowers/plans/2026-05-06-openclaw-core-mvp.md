# OpenClaw Core MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first testable OpenClaw Core that parses fixed Korean commands, applies mode and safety rules, writes structured logs, and runs through a console mock loop.

**Architecture:** Keep Discord, STT, and Windows control behind boundaries while implementing the core behavior first. The MVP creates a parser, gate, core orchestrator, logger, fakeable controller interface, and console entrypoint.

**Tech Stack:** Python, pytest, python-dotenv, dataclasses, JSONL logs.

---

## File Structure

- Create `pyproject.toml`: package metadata and pytest configuration.
- Create `requirements.txt`: MVP runtime and test dependencies.
- Create `openclaw_discord/__main__.py`: `python -m openclaw_discord` entrypoint.
- Create `openclaw_discord/commands.py`: command model and exact Korean parser.
- Create `openclaw_discord/core.py`: mode state, safety checks, confirmation flow, and orchestration.
- Create `openclaw_discord/logging.py`: JSONL and text log writer.
- Create `openclaw_discord/controllers.py`: controller protocol and dry-run controller.
- Create `openclaw_discord/config.py`: `.env` settings loader.
- Create `tests/test_commands.py`: parser tests.
- Create `tests/test_core.py`: mode, permission, confirmation, and controller routing tests.
- Create `tests/test_logging.py`: JSONL and text log tests.

### Task 1: Project Skeleton

**Files:**
- Create: `pyproject.toml`
- Create: `requirements.txt`
- Create: `openclaw_discord/__init__.py`

- [ ] **Step 1: Add project metadata and dependencies**

Create a Python package named `openclaw_discord` with pytest configured to discover tests under `tests`.

- [ ] **Step 2: Install dependencies**

Run: `python -m pip install -r requirements.txt`

- [ ] **Step 3: Verify empty test discovery**

Run: `python -m pytest`

Expected: pytest exits successfully or reports no tests before test files are added.

### Task 2: Fixed Korean Command Parser

**Files:**
- Create: `tests/test_commands.py`
- Create: `openclaw_discord/commands.py`

- [ ] **Step 1: Write failing parser tests**

Cover exact parsing for `클로 온`, `클로 오프`, `메모장 열어`, `왼쪽 클릭`, `복사`, and `안녕하세요 입력`. Cover unknown text rejection.

- [ ] **Step 2: Run parser tests to verify RED**

Run: `python -m pytest tests/test_commands.py -q`

Expected: import failure because `openclaw_discord.commands` does not exist.

- [ ] **Step 3: Implement minimal parser**

Create typed command objects with `kind`, `action`, and optional `payload`.

- [ ] **Step 4: Run parser tests to verify GREEN**

Run: `python -m pytest tests/test_commands.py -q`

Expected: all parser tests pass.

### Task 3: Core Safety and Mode Flow

**Files:**
- Create: `tests/test_core.py`
- Create: `openclaw_discord/core.py`
- Create: `openclaw_discord/controllers.py`

- [ ] **Step 1: Write failing core tests**

Cover owner-only command handling, mode-off blocking, `클로 온`, `클로 오프`, controller routing while mode is on, and confirmation for `창 닫아`.

- [ ] **Step 2: Run core tests to verify RED**

Run: `python -m pytest tests/test_core.py -q`

Expected: import failure because `openclaw_discord.core` does not exist.

- [ ] **Step 3: Implement minimal core**

Add `OpenClawCore`, `CommandContext`, `CommandResult`, and a dry-run controller protocol.

- [ ] **Step 4: Run core tests to verify GREEN**

Run: `python -m pytest tests/test_core.py -q`

Expected: all core tests pass.

### Task 4: Structured Logging

**Files:**
- Create: `tests/test_logging.py`
- Create: `openclaw_discord/logging.py`

- [ ] **Step 1: Write failing logging tests**

Cover JSONL event output and text log tags `[VOICE]`, `[OK]`, `[FAIL]`, and `[BLOCKED]`.

- [ ] **Step 2: Run logging tests to verify RED**

Run: `python -m pytest tests/test_logging.py -q`

Expected: import failure because `openclaw_discord.logging` does not exist.

- [ ] **Step 3: Implement minimal log writer**

Add `OpenClawLogger` that writes one JSONL file and one text log file.

- [ ] **Step 4: Run logging tests to verify GREEN**

Run: `python -m pytest tests/test_logging.py -q`

Expected: all logging tests pass.

### Task 5: Console Mock Entrypoint

**Files:**
- Create: `openclaw_discord/__main__.py`
- Create: `openclaw_discord/config.py`

- [ ] **Step 1: Add config loader**

Read `.env` values and provide defaults for local console mode.

- [ ] **Step 2: Add console loop**

Accept typed Korean commands, process them through `OpenClawCore`, print the result, and stop on `exit`.

- [ ] **Step 3: Verify package entrypoint**

Run: `python -m openclaw_discord --help`

Expected: usage text prints without starting the loop.

### Task 6: Final Verification and Commit

**Files:**
- Modify: all files from Tasks 1-5

- [ ] **Step 1: Run full tests**

Run: `python -m pytest`

Expected: all tests pass.

- [ ] **Step 2: Check Git status**

Run: `git status --short`

Expected: only intentional files changed plus pre-existing untracked `discord.patch.json5`.

- [ ] **Step 3: Commit**

Run:

```bash
git add pyproject.toml requirements.txt openclaw_discord tests docs/superpowers/plans/2026-05-06-openclaw-core-mvp.md
git commit -m "feat: add openclaw core mvp"
```

