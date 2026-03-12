<p align="center">
  <img src="https://raw.githubusercontent.com/revanthpobala/devin-cli/main/assets/logo.png" alt="Devin CLI Logo" width="300">
</p>

# Devin CLI (Unofficial) — The Professional Terminal Interface for Devin AI

<p align="center">
  <a href="https://pypi.org/project/devin-cli/"><img src="https://img.shields.io/pypi/v/devin-cli.svg?style=for-the-badge&color=0294DE" alt="PyPI version"></a>
  <a href="https://github.com/revanthpobala/homebrew-tap"><img src="https://img.shields.io/badge/Homebrew-Tap-orange?style=for-the-badge&logo=homebrew" alt="Homebrew Tap"></a>
  <a href="https://github.com/revanthpobala/devin-cli/actions/workflows/pypi-publish.yml"><img src="https://github.com/revanthpobala/devin-cli/actions/workflows/pypi-publish.yml/badge.svg" alt="Build Status"></a>
</p>

> **The first unofficial CLI for the world's first AI Software Engineer. Supports both the modern v3 API and the legacy v1 API with full multi-profile management.**

Devin CLI is designed for high-velocity engineering teams. It strips away the friction of the web UI, allowing you to orchestrate autonomous agents, manage complex contexts, and automate multi-step development workflows through a robust, terminal-first interface.

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
# Paste your API token (apk_... or cog_...) from https://preview.devin.ai/settings
# Select API version: v3 (default) or v1 (legacy)
```

### 3. Your First Session
```bash
devin sessions create "Identify and fix the race condition in our Redis cache layer"
```

---

## 🔑 Multi-Profile Support

The CLI supports multiple named profiles, letting you manage separate tokens, organizations, and API versions from a single install.

```bash
# Configure your personal v3 profile
devin configure --profile personal

# Configure a service account profile
devin configure --profile service

# Switch profiles at runtime
devin --profile service sessions list
devin --profile personal sessions create "Fix the failing tests"
```

Profiles are stored in `~/.config/devin/config.json` and are fully isolated — including their session deduplication caches and active session IDs.

---

## 🕹 Legacy v1 API Support

If you are running an older integration against the original Devin API v1 endpoints, the CLI acts as a transparent proxy and routes calls to the correct v1 URLs without breaking your v3 integrations.

**To configure a v1 profile:**
```bash
devin configure --profile legacy
# When prompted for API Version, enter: v1
# Set Base URL to: https://api.devin.ai/v1
```

**To use the v1 profile:**
```bash
devin --profile legacy sessions create "Run the migration script"
devin --profile legacy sessions list
```

**What works in v1:**

| Feature | v1 | v3 |
| :--- | :---: | :---: |
| Sessions (create, list, get, terminate) | ✅ | ✅ |
| Knowledge (create, update, delete) | ✅ | ✅ |
| Playbooks (create, update, delete) | ✅ | ✅ |
| Secrets (list, create, delete) | ✅ | ✅ |
| Attachments (upload, download) | ✅ | ✅ |
| Session Insights | ❌ | ✅ |
| Schedules | ❌ | ✅ |
| Repositories | ❌ | ✅ |
| Enterprise endpoints | ❌ | ✅ |

> The help menu will show `(Legacy v1 API)` and `(v3 Only)` tags next to commands when a v1 profile is active.

---

## 🛠 Command Reference

Every sub-command supports the `--org` flag to override your active organization on the fly.

| Category | Commands | Description |
| :--- | :--- | :--- |
| **Sessions** | `create`, `list`, `get`, `insights`, `cost`, `messages`, `message`, `terminate` | Core agent lifecycle and analytics. |
| **Knowledge** | `list`, `create`, `delete` | Manage organizational context and AI memory. |
| **Playbooks** | `list`, `create`, `update`, `delete` | Automate complex, multi-step agent workflows. |
| **Secrets** | `list`, `create`, `delete` | Pass API keys and credentials to Devin sessions. |
| **Schedules** | `list`, `create` | Schedule recurring autonomous tasks via CRON. |
| **Repositories** | `list`, `index` | Force indexing of Git repositories for Devin context. |
| **Attachments** | `upload`, `download` | Transfer context files seamlessly. |
| **Enterprise** | `whoami`, `list-orgs` | Administrative identity discovery. |
| **Global** | `configure`, `use` | CLI setup and active session management. |

### Key Flags

| Flag | Description |
| :--- | :--- |
| `--profile <name>` | Select a named configuration profile |
| `--org <id>` | Override the active organization for a single command |
| `--json` | Output raw JSON (available on `sessions list`, `repos list`, `secrets list`) |
| `--force` | Skip duplicate session detection and create anyway |
| `--advanced-mode` | Request an advanced mode session requiring browser auth |

---

## 🛡 Session Deduplication

The CLI caches a SHA-256 hash of your last 50 prompts per profile. If you attempt to launch a session with an identical prompt, the CLI halts and alerts you before wasting ACUs:

```
Duplicate Detected: You recently created a session with this exact prompt.
Existing Session ID: abc123...
Are you sure you want to create a duplicate session? [y/N]
```

Use `--force` to bypass this check.

---

## 📟 CI/CD Integration

```yaml
# Example GitHub Action Step
env:
  DEVIN_API_TOKEN: ${{ secrets.DEVIN_API_TOKEN }}
  DEVIN_ORG_ID: ${{ secrets.DEVIN_ORG_ID }}
run: |
  devin sessions create "Review PR #${{ github.event.pull_request.number }}"
```

**Supported environment variables:**

| Variable | Description |
| :--- | :--- |
| `DEVIN_API_TOKEN` | Your API token (overrides config file) |
| `DEVIN_ORG_ID` | Your organization ID |
| `DEVIN_BASE_URL` | Override the default base URL |
| `DEVIN_API_VERSION` | Set `v1` or `v3` without configuring |

---

## ⚙️ Engineering Specs

- **Architecture**: Full v3 API support (including `v3beta1` and `enterprise` endpoints) + v1 legacy proxy
- **Config Storage**: `~/.config/devin/config.json`
- **Platform Support**: Linux, macOS, WSL2
- **Python**: 3.9+

---

## 🧪 Developer Hub

```bash
# Setup
pip install -e ".[dev]"

# Test Suite
PYTHONPATH=src python3 -m pytest
```

---

## 📄 License

MIT. **Devin CLI** is an unofficial community project and is not affiliated with Cognition AI.
