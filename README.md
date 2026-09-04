<p align="center">
  <img src="https://raw.githubusercontent.com/revanthpobala/devin-cli/main/assets/logo.png" alt="Devin CLI Logo" width="300">
</p>

# Devin CLI (Unofficial) — The Professional Terminal Interface for Devin AI

<p align="center">
  <a href="https://pypi.org/project/devin-cli/"><img src="https://img.shields.io/pypi/v/devin-cli.svg?style=for-the-badge&color=0294DE" alt="PyPI version"></a>
  <a href="https://pepy.tech/project/devin-cli"><img src="https://img.shields.io/pepy/dt/devin-cli?style=for-the-badge&color=4c1" alt="Downloads"></a>
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
# Interactive setup:
devin configure
# Paste your API token (apk_... or cog_...) from https://preview.devin.ai/settings
# Select API version: v3 (default) or v1 (legacy)

# Or non-interactive / CI setup:
devin configure --token "$DEVIN_API_TOKEN" --org "$DEVIN_ORG_ID" --yes
```

### 3. Your First Session
```bash
devin create-session "Identify and fix the race condition in our Redis cache layer"
devin watch
```

---

## Authentication & Usage

### AI Agent Integration (JSON Output)
For external automation and AI agent architectures relying on the CLI, `devin-cli` supports a global `--json` flag. This will suppress all visual output/terminal colors and instead uniformly return raw JSON objects for stdout and API errors, making the CLI completely deterministic to parse.
```bash
devin --json sessions create "My prompt"
# { "session_id": "...", "status": "running" }
```

### Multi-Profile Support

```bash
devin configure --profile personal
devin configure --profile service
devin --profile service sessions list
devin --profile personal sessions create "Fix the failing tests"
```

Profiles are stored in `~/.config/devin/config.json` — fully isolated including session caches and active session IDs.

### Automation & CI / CD

`devin-cli` is fully optimized for headless CI/CD runners (GitHub Actions, GitLab CI, Jenkins) and containerized workflows.

#### Precedence Resolution
Credentials and configuration resolve in a strict, predictable order:
1. **Global CLI Flags** (`--token`, `--org`, `--base-url`, `--api-version`)
2. **Environment Variables** (`DEVIN_API_TOKEN`, `DEVIN_ORG_ID`, `DEVIN_BASE_URL`, `DEVIN_API_VERSION`)
3. **Config File** (`DEVIN_CONFIG_FILE` or `~/.config/devin/config.json`)
4. **Built-in Defaults** (`base_url: https://api.devin.ai/v3`, `api_version: v3`)

#### Ephemeral Runs (Zero Disk Writes)
In CI pipelines, you do not need to create or write configuration files. Pass credentials via environment variables or root CLI flags:

```bash
# Option A: Environment variables
export DEVIN_API_TOKEN="cog_..."
export DEVIN_ORG_ID="org-..."
devin repos list --json

# Option B: Global CLI flags on-the-fly
devin --token "$DEVIN_API_TOKEN" --org "$DEVIN_ORG_ID" repos status my-org/my-repo --json
```

#### Non-Interactive Configuration
If your pipeline writes a config file, use `--yes` (or run in non-TTY environments) to disable interactive prompts:

```bash
devin configure \
  --token "$DEVIN_API_TOKEN" \
  --org "$DEVIN_ORG_ID" \
  --base-url https://api.devin.ai/v3 \
  --api-version v3 \
  --yes
```

#### Custom Config File Path
Override the default `~/.config/devin/config.json` location:

```bash
# Via flag
devin --config-file /tmp/devin-ci.json repos list

# Via environment variable
export DEVIN_CONFIG_FILE=/tmp/devin-ci.json
```

---

## 🤖 All Commands

### Flat Commands (0.1.x style — quick access)

| Command | Description |
| :--- | :--- |
| `devin create-session "<prompt>"` | Create a new session |
| `devin watch` | Live-watch the active session |
| `devin status` | One-liner status of active session |
| `devin open` | Open active session URL in browser |
| `devin message "<text>"` | Send a message to active session |
| `devin message --file prompt.txt` | Send a message from file |
| `devin terminate` | Terminate active session |
| `devin list-sessions` | List recent sessions |
| `devin upload <file>` | Upload a file to Devin |
| `devin attach <file> "<prompt>"` | Upload file + start session with it |
| `devin list-knowledge` | List knowledge notes |
| `devin update-knowledge <id>` | Update a knowledge entry |
| `devin update-tags` | Update tags on a session |
| `devin history` | Show locally cached session ID |
| `devin messages` | Show conversation history |
| `devin get-session` | Show session details + structured output |
| `devin update-playbook <id>` | Update a playbook |
| `devin delete-playbook <id>` | Delete a playbook |
| `devin list-secrets` | List organization secrets |
| `devin delete-secret <id>` | Delete a secret |
| `devin chain` | Sequential playbook orchestration |
| `devin use <session_id>` | Switch active session |
| `devin configure` | Configure API token and profile |

### Sessions (`devin sessions <cmd>`)

| Command | Key Flags | Description |
| :--- | :--- | :--- |
| `create` | see below | Create a session |
| `list` | `--limit`, `--json` | List sessions |
| `get` | `[session_id]` | Get session details |
| `watch` | `--interval` | Live-watch with exponential backoff |
| `message` | `[text]`, `--file` | Send message or file to session |
| `messages` | `[session_id]` | Full conversation history |
| `terminate` | `[session_id]` | Terminate a session |
| `insights` | `[session_id]` | ACU / performance insights (v3) |
| `cost` | `[session_id]` | ACU consumption |

> **Note for Service Tokens (`cog_`):** When retrieving a specific session via `devin sessions get <id>`, the CLI automatically falls back to filtering the org-wide `sessions list` via a `?session_ids=[<id>]` query parameter to gracefully bypass the `403 Forbidden` error natively returned by the direct API endpoint for service accounts.

#### `sessions create` / `create-session` — Full Flag Reference

| Flag | Type | Description |
| :--- | :--- | :--- |
| `[prompt]` | arg | Task prompt |
| `--file`, `-f` | path | Read prompt from file |
| `--title`, `-t` | str | Custom session title |
| `--devin-mode`, `--mode`, `--model` | str | Agent mode / model: `normal` \| `fast` \| `lite` \| `ultra` \| `fusion` (v3) |
| `--platform` | str | VM platform (e.g. `windows`) or outpost pool (v3) |
| `--resumable` / `--no-resumable` | flag | Preserve session VM state after stopping (v3) |
| `--wait`, `-w` | flag | Block until session finishes |
| `--interval` | int | Polling interval for `--wait` (default: 5s) |
| `--max-acu` | int | ACU spend cap |
| `--force` | flag | Skip duplicate prompt detection |
| `--advanced-mode` | str | `analyze` \| `create_playbook` \| `improve_playbook` \| `batch` \| `manage_knowledge` |
| `--playbook-id` | str | Playbook to apply (v3) |
| `--child-playbook-id` | str | Playbook for each sub-session in `batch` mode (v3) |
| `--bypass-approval` | flag | Skip UI approval — child sessions start immediately (v3) |
| `--tag` | str (repeatable) | Session tags |
| `--repo` | str (repeatable) | Repo URLs to attach (v3) |
| `--knowledge-id` | str (repeatable) | Knowledge IDs to inject |
| `--secret-id` | str (repeatable) | Secret IDs to inject (v3) |
| `--session-secret` | str (repeatable) | Temporary session secret `KEY=VALUE` (v3) |
| `--session-link` | str (repeatable) | Session URLs as context (v3) |
| `--attachment-url` | str (repeatable) | Attachment URLs (v3) |
| `--structured-output-schema` | str | JSON schema for structured response (v3) |
| `--structured-output-required` | flag | Require structured output tool call (v3) |
| `--create-as-user-id` | str | Enterprise: impersonate a user (v3) |
| `--org` | str | Override org ID |

#### Full Batch Automation Example
```bash
# No browser interaction required
devin sessions create \
  --devin-mode fast \
  --advanced-mode batch \
  --playbook-id <orchestrator-id> \
  --child-playbook-id <worker-id> \
  --bypass-approval \
  "Process each file in the attached CSV"
```

### PR Reviews (`devin pr-reviews <cmd>`)

| Command | Key Flags | Description |
| :--- | :--- | :--- |
| `trigger` | `--pr-url` | Trigger a Devin code review for a pull request |
| `get` | `--pr-url`, `--repo-path`, `--pr-number` | Get latest review status for a pull request |

### Organization Session Tags (`devin tags <cmd>`)

| Command | Description |
| :--- | :--- |
| `list` | List allowed session tags for the organization |
| `append` | Append tags to organization allowed list (`--tag`) |
| `replace` | Replace full set of allowed tags (`--tag`) |
| `clear` | Clear all allowed tags |

### Snapshot Blueprints (`devin blueprints <cmd>`)

| Command | Description |
| :--- | :--- |
| `list` | List snapshot blueprints for the organization |
| `trigger-build` | Trigger a manual snapshot build |
| `list-builds` | List history of snapshot builds |

### Knowledge (`devin knowledge <cmd>`)

| Command | Description |
| :--- | :--- |
| `list` | List all knowledge notes |
| `create` | Create a knowledge note |
| `delete <id>` | Delete a knowledge note |

### Playbooks (`devin playbooks <cmd>`)

| Command | Description |
| :--- | :--- |
| `list` | List all playbooks |
| `create` | Create a playbook |
| `update <id>` | Update a playbook |
| `delete <id>` | Delete a playbook |

### Secrets (`devin secrets <cmd>`)

| Command | Description |
| :--- | :--- |
| `list` | List organization secrets |
| `create` | Create a secret |
| `delete <id>` | Delete a secret |

### Schedules (`devin schedules <cmd>`)

| Command | Description |
| :--- | :--- |
| `list` | List schedules |
| `create` | Create a CRON schedule |

### Repositories (`devin repos <cmd>`)

| Command | Description |
| :--- | :--- |
| `list` | List indexed repositories |
| `index` | Force-index a repository |

### Attachments (`devin attachments <cmd>`)

| Command | Description |
| :--- | :--- |
| `upload <file>` | Upload a file |
| `download <id>` | Download an attachment |

### Enterprise Management (`devin enterprise <cmd>`)

| Command Group / Command | Description |
| :--- | :--- |
| `whoami` | Show current identity |
| `list-orgs` | List accessible organizations |
| `queue` | Get session queue health status |
| `audit-logs` | List enterprise audit logs (`--limit`, `--order`) |
| `ip-access-list` | `list` \| `add` \| `replace` \| `clear` enterprise IP allowlists |
| `guardrails` | `list` guardrail violations (`--session-id`, `--guardrail-id`) |
| `code-scans` | `findings` \| `metrics` \| `remediate` code scan findings |
| `service-users` | `list` service users, `create-key`, `rotate-key`, `revoke-key` |

### Chain (`devin chain`)

Orchestrate a sequential pipeline of playbooks:

```bash
# Inline
devin chain "Refactor utils.py" --playbooks "lint_check,unit_tests"

# YAML workflow file
devin chain --file workflow.yml
```

---

## 🛡 Session Deduplication

The CLI caches a SHA-256 hash of your last 50 prompts per profile. Duplicate prompts are caught before wasting ACUs:

```
Duplicate Detected: You recently created a session with this exact prompt.
Existing Session ID: abc123...
Are you sure you want to create a duplicate session? [y/N]
```

Use `--force` to bypass.

---

## 📟 CI/CD Integration

```yaml
env:
  DEVIN_API_TOKEN: ${{ secrets.DEVIN_API_TOKEN }}
  DEVIN_ORG_ID: ${{ secrets.DEVIN_ORG_ID }}
run: |
  devin create-session "Review PR #${{ github.event.pull_request.number }}" --wait
```

**Environment variables:**

| Variable | Description |
| :--- | :--- |
| `DEVIN_API_TOKEN` | API token (overrides config) |
| `DEVIN_ORG_ID` | Organization ID |
| `DEVIN_BASE_URL` | Override base URL |
| `DEVIN_API_VERSION` | Set `v1` or `v3` without configuring |

---

## 🕹 v1 / v3 Profile Compatibility

| Feature | v1 | v3 |
| :--- | :---: | :---: |
| Sessions (create, list, get, terminate) | ✅ | ✅ |
| Knowledge (create, update, delete) | ✅ | ✅ |
| Playbooks (create, update, delete) | ✅ | ✅ |
| Secrets (list, create, delete) | ✅ | ✅ |
| Attachments (upload, download) | ✅ | ✅ |
| Advanced Mode (`--advanced-mode`) | ⚠️ warned | ✅ |
| Batch sessions (`--bypass-approval`) | ⚠️ warned | ✅ |
| Session Insights | ❌ | ✅ |
| Schedules | ❌ | ✅ |
| Repositories | ❌ | ✅ |
| Enterprise endpoints | ❌ | ✅ |

> v3-only flags are accepted but ignored on v1 profiles — the CLI prints a clear warning listing exactly which flags were dropped.

---

## ⚙️ Engineering Specs

- **Architecture**: Full v3 API support (`v3beta1` + `enterprise`) + v1 legacy proxy
- **Config**: `~/.config/devin/config.json`
- **Platform**: Linux, macOS, WSL2
- **Python**: 3.9+

---

## 🧪 Developer Hub

```bash
pip install -e ".[dev]"
PYTHONPATH=src python3 -m pytest
```

---

## 📄 License

MIT. **Devin CLI** is an unofficial community project and is not affiliated with Cognition AI.
