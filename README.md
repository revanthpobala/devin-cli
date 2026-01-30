<p align="center">
  <img src="https://raw.githubusercontent.com/revanthpobala/devin-cli/main/assets/logo.png" alt="Devin CLI Logo" width="300">
</p>

# Devin CLI (Unofficial) — The Professional Terminal Interface for Devin AI

<p align="center">
  <a href="https://pypi.org/project/devin-cli/"><img src="https://img.shields.io/pypi/v/devin-cli.svg?style=for-the-badge&color=0294DE" alt="PyPI version"></a>
  <a href="https://github.com/revanthpobala/devin-cli/actions/workflows/pypi-publish.yml"><img src="https://github.com/revanthpobala/devin-cli/actions/workflows/pypi-publish.yml/badge.svg" alt="Build Status"></a>
</p>

> **The first unofficial CLI for the world's first AI Software Engineer.**

Devin CLI is designed for high-velocity engineering teams. It strips away the friction of the web UI, allowing you to orchestrate autonomous agents, manage complex contexts, and automate multi-step development workflows through a robust, terminal-first interface.

---

## ⚡ Quick Start

### 1. Installation
```bash
# Recommended: Install via pipx for an isolated environment
pipx install devin-cli 

# Or via standard pip
pip install devin-cli
```

### 2. Configuration
```bash
devin configure
# Paste your API token from https://preview.devin.ai/settings
```

### 3. Your First Session
```bash
devin create-session "Identify and fix the race condition in our Redis cache layer"
devin watch
```

---

## 🛠 Command Cheat Sheet

### Core Workflow
| Command | Example Usage |
| :--- | :--- |
| **`create-session`** | `devin create-session "Refactor the Auth module"` |
| **`list-sessions`** | `devin list-sessions --limit 10` |
| **`watch`** | `devin watch` (Live terminal monitoring) |
| **`message`** | `devin message "Actually, use the standard library instead of the third-party package"` |
| **`open`** | `devin open` (Jump to the web UI) |
| **`status`** | `devin status` (Quick pulse check) |
| **`terminate`** | `devin terminate` |

### Context & Assets
| Command | Example Usage |
| :--- | :--- |
| **`attach`** | `devin attach ./specs/v2.md "Implement the new billing logic"` |
| **`upload`** | `devin upload ./db_dump.sql` |
| **`list-knowledge`** | `devin list-knowledge` |

## 🛠 Detailed Command Reference

Every command supports the `--help` flag for real-time documentation. Below is an exhaustive reference for the core engineering workflow.

<details>
<summary><b>🚀 create-session</b> — Start a new autonomous agent</summary>

```text
Usage: devin create-session [OPTIONS] [PROMPT]

Options:
  -t, --title TEXT          Custom session title
  -f, --file PATH           Read prompt from file
  -s, --secret KEY=VALUE    Inject session-specific secrets
  -k, --knowledge-id TEXT   Knowledge IDs to include
  --secret-id TEXT          Stored secret IDs to include
  --max-acu INTEGER         Maximum ACU limit
  --unlisted                Create unlisted session
  -i, --idempotent          Idempotent creation
```
</details>

<details>
<summary><b>🔗 chain</b> — Orchestrate multi-step workflows (Beta)</summary>

```text
Usage: devin chain [OPTIONS] [PROMPT]

Options:
  --playbooks TEXT          Comma-separated playbook IDs
  -f, --file PATH           Workflow YAML file
```
</details>

<details>
<summary><b>📎 attach</b> — Upload context and initiate task</summary>

```text
Usage: devin attach [OPTIONS] FILE PROMPT

Arguments:
  FILE    File to upload and link (ZIP, PDF, Codebase) [required]
  PROMPT  Initial instruction for Devin [required]
```
</details>

<details>
<summary><b>📋 list-sessions</b> — Manage your active agents</summary>

```text
Usage: devin list-sessions [OPTIONS]

Options:
  --limit INTEGER           Number of sessions to list [default: 10]
  --json                    Output as machine-readable JSON
```
</details>

<details>
<summary><b>⚙️ configure</b> — Setup your environment</summary>

```text
Usage: devin configure [OPTIONS]

Initializes your local config with the DEVIN_API_TOKEN.
```
</details>

<details>
<summary><b>👀 watch</b> — Terminal-native live monitoring</summary>

```text
Usage: devin watch [OPTIONS] [SESSION_ID]

Streams the live logs and terminal output from Devin directly to your console.
```
</details>

<details>
<summary><b>🛑 terminate</b> — Stop an active agent</summary>

```text
Usage: devin terminate [OPTIONS] [SESSION_ID]

Permanently stops a session and releases all associated resources.
```
</details>

<details>
<summary><b>🌐 open</b> — Jump to the Web UI</summary>

```text
Usage: devin open [OPTIONS] [SESSION_ID]

Instantly opens the specified session in your default web browser for visual debugging.
```
</details>

<details>
<summary><b>🧠 Knowledge & Playbooks</b> — Advanced CRUD</summary>

| Command | Purpose |
| :--- | :--- |
| `list-knowledge` | View all shared organizational context. |
| `create-knowledge` | Add new documentation or code references. |
| `update-knowledge` | Refresh existing context. |
| `list-playbooks` | View all available team playbooks. |
| `create-playbook` | Design a new standardized workflow. |

</details>

---

## 📟 Integration & Automation

### GitHub Actions Integration
Devin CLI is designed for CI/CD. Use environment variables to bypass the `configure` step.
```bash
# Example GitHub Action Step
env:
  DEVIN_API_TOKEN: ${{ secrets.DEVIN_API_TOKEN }}
run: |
  devin create-session "Review PR #${{ github.event.pull_request.number }}" --unlisted
```

### Advanced Scripting
Pipe Devin's intelligence into your existing toolchain.
```bash
# Close all blocked sessions
devin list-sessions --json | jq -r '.[] | select(.status_enum=="blocked") | .session_id' | xargs -I {} devin terminate {}
```

---

## ⚙️ Engineering Specs
- **Config Storage**: `~/.config/devin/config.json`
- **Environment Variables**: `DEVIN_API_TOKEN`, `DEVIN_BASE_URL`
- **Platform Support**: Linux, macOS, WSL2

---

## 🧪 Developer Hub
```bash
# Setup
pip install -e ".[dev]"

# Test Suite (100% path coverage)
PYTHONPATH=src pytest
```

---

## 📄 License
MIT. **Devin CLI** is an unofficial community project and is not affiliated with Cognition AI.

---
<!-- SEO Keywords: Devin AI, AI Software Engineer, Autonomous AI Agent, Devin CLI, Terminal AI, Coding Agent, AI Orchestration, Software Engineering Automation, GitHub Actions AI, Cognition AI, Devin API -->
