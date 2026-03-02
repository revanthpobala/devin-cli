<p align="center">
  <img src="https://raw.githubusercontent.com/revanthpobala/devin-cli/main/assets/logo.png" alt="Devin CLI Logo" width="300">
</p>

# Devin CLI (Unofficial) — The Professional Terminal Interface for Devin AI

<p align="center">
  <a href="https://pypi.org/project/devin-cli/"><img src="https://img.shields.io/pypi/v/devin-cli.svg?style=for-the-badge&color=0294DE" alt="PyPI version"></a>
  <a href="https://github.com/revanthpobala/homebrew-tap"><img src="https://img.shields.io/badge/Homebrew-Tap-orange?style=for-the-badge&logo=homebrew" alt="Homebrew Tap"></a>
  <a href="https://github.com/revanthpobala/devin-cli/actions/workflows/pypi-publish.yml"><img src="https://github.com/revanthpobala/devin-cli/actions/workflows/pypi-publish.yml/badge.svg" alt="Build Status"></a>
</p>

> **The first unofficial CLI for the world's first AI Software Engineer. Now fully upgraded to Devin API v3.**

Devin CLI is designed for high-velocity engineering teams. It strips away the friction of the web UI, allowing you to orchestrate autonomous agents, manage complex contexts, and automate multi-step development workflows through a robust, terminal-first interface. Built for performance, SEO, and developer productivity.

---

## ⚡ Quick Start

### 1. Installation

**Recommended: Via Homebrew (macOS)**
```bash
brew tap revanthpobala/tap
brew install devin-cli
```

**Via pipx (Isolated environment)**
```bash
pipx install devin-cli
```

**Via pip**
```bash
pip install devin-cli
```

### 2. Configuration
```bash
devin configure
# Paste your v3 API token (apk_... or cog_...) from https://preview.devin.ai/settings
# Optionally configure your Organization ID here.
```

### 3. Your First Session
```bash
devin sessions create -t "Identify and fix the race condition in our Redis cache layer"
```

---

## 🛠 Command Cheat Sheet (v3 Architecture)

The v3 architecture introduces a modular, hierarchical CLI structure focusing on enterprise features, secrets, and organizational management. Every sub-command supports the `--org` flag to override your active organization on the fly. 

| Category | Commands | Description |
| :--- | :--- | :--- |
| **Sessions** | `create`, `list`, `get`, `insights`, `cost`, `messages`, `message`, `terminate` | Core agent lifecycle and analytics. |
| **Knowledge** | `list`, `create`, `delete` | Manage organizational context and AI memory. |
| **Playbooks** | `list`, `create`, `delete` | Automate complex, multi-step agent workflows. |
| **Secrets** | `list`, `create`, `delete` | Manage API keys passing to Devin sessions. |
| **Schedules** | `list`, `create` | Schedule recurring autonomous tasks via CRON. |
| **Repositories** | `list`, `index` | Force indexing of Git repositories. |
| **Attachments** | `upload`, `download` | Transfer context files seamlessly. |
| **Enterprise** | `whoami`, `list-orgs` | Administrative identity discovery. |
| **Global** | `configure`, `use` | CLI setup and active session swapping. |

### Example Automations

**Blocking Call for CI/CD:**
```bash
# Trigger Devin and wait for unit tests to be fixed
devin sessions create "Fix the failing authentication tests" 
echo "Devin finished. Running integration tests..."
npm test
```

**Audit Subsystem Costs:**
```bash
# Get ACU consumption for a specific incident
devin sessions cost --id <SESSION_ID>
```

---

## 📟 Integration & Environment Variables

Devin CLI is designed for CI/CD. Use environment variables to bypass the `configure` step entirely.

- `DEVIN_API_TOKEN`: Your API token.
- `DEVIN_ORG_ID`: Your target organization ID.
- `DEVIN_BASE_URL`: (Optional) Overrides the standard `https://api.devin.ai/v3`.

```yaml
# Example GitHub Action Step
env:
  DEVIN_API_TOKEN: ${{ secrets.DEVIN_API_TOKEN }}
  DEVIN_ORG_ID: ${{ secrets.DEVIN_ORG_ID }}
run: |
  devin sessions create "Review PR #${{ github.event.pull_request.number }}"
```

---

## ⚙️ Engineering Specs
- **Architecture**: Complete Devin API `v3` Support (including `v3beta1` and `enterprise` endpoints).
- **Config Storage**: `~/.config/devin/config.json`
- **Platform Support**: Linux, macOS, WSL2

---

## 🧪 Developer Hub
```bash
# Setup
pip install -e ".[dev]"

# Test Suite (100% path coverage)
PYTHONPATH=src python3 -m pytest
```

---

## 📄 License
MIT. **Devin CLI** is an unofficial community project and is not affiliated with Cognition AI.
