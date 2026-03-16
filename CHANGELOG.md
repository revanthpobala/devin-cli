# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.1] - 2026-03-16
### Added
- **Global `--json` Output**: New orchestration flag that converts *all* CLI output and API errors into pure, parseable JSON for AI agents.
- **Knowledge Get Command**: Added `devin knowledge get <id>` and `devin get-knowledge <id>` to retrieve full note content.
- Missing v1 and v3 `get_knowledge` / `create_secret` cross-compatibility polyfills.

### Fixed
- **Audit Fixes**: Resolved 13 critical bugs found during full codebase audit (indentation errors, missing returns, duplicate imports, and terminal status handling).
- **Warning Suppression**: Suppressed `urllib3` SSL warnings in JSON mode to ensure clean stdout streams.

## [1.2.0] - 2026-03-11
### Added
- `sessions create` / `create-session` now exposes all 8 previously missing v3 API parameters: `--playbook-id`, `--tag`, `--repo`, `--knowledge-id`, `--secret-id`, `--session-link`, `--attachment-url`, `--create-as-user-id`.
- Profile feedback on session create: prints which profile and API version is being used.
- Explicit warning when v3-only flags (`--advanced-mode`, `--playbook-id`, `--repo`, `--secret-id`, `--session-link`, `--attachment-url`, `--create-as-user-id`) are passed on a v1 profile — instead of silently ignored.
### Fixed
- Removed `**kwargs` anti-pattern from `v1/sessions.create_session`. Typos in keyword args now raise `TypeError` instead of silently vanishing.
- v3-only params added as explicit no-ops in v1 `create_session` so the shared CLI call site works without `TypeError`.

## [1.1.9] - 2026-03-11
### Fixed
- `devin watch` terminal status message was printed inside a `Live` context, causing output corruption. Now printed after the `Live` block exits.
- `update-playbook` was sending an empty string title when `--title` was not passed, overwriting the existing playbook title. Now only sends fields that are explicitly provided.
- `chain` used bare `resp["session_id"]` key access which would raise `KeyError` on unexpected API responses. Now uses `.get()` with an explicit error guard.

## [1.1.8] - 2026-03-11
### Added
- Restored all 0.1.x flat commands: `watch`, `status`, `open`, `message`, `terminate`, `list-sessions`, `create-session`, `upload`, `list-knowledge`, `attach`, `update-tags`, `history`, `messages`, `get-session`, `update-knowledge`, `update-playbook`, `delete-playbook`, `list-secrets`, `delete-secret`, `chain`.
- `--wait` / `-w` flag on `create-session` and `sessions create` — blocks until the session reaches a terminal status.
- `sessions watch` now displays `structured_output` inline and uses exponential backoff (caps at 30s).
- `chain` command supports both inline `--playbooks` chaining and YAML workflow files.
- `attach` command correctly embeds the uploaded file URL in the session prompt.

## [1.1.7] - 2026-03-11
### Fixed
- `knowledge list` now correctly reads `notes` key from the v3 `knowledge/notes` endpoint, with `knowledge` as fallback. Also reads `title` in addition to `name` for display.
- `schedules list` now correctly reads `schedules` key from the v3 response, with `items` as fallback.

## [1.1.6] - 2026-03-11
### Fixed
- `repos list` now correctly reads `repo_path` (the actual v3beta1 API key) and resolves indexed state from `indexing_status.indexing_enabled`.
- `sessions cost` now reads `acus_consumed` (the real v3 field name) with a fallback to `acu_used` for v1.

## [1.1.5] - 2026-03-11
### Fixed
- `repos list` table now correctly resolves repository paths by handling direct list API responses and trying `repository_path`, `full_name`, `path`, and `name` keys in sequence.
- `sessions cost` now shows an informative message when `acu_used` is `null` (v1 API sessions or service tokens without cost visibility) instead of silently displaying null.

## [1.1.4] - 2026-03-11
### Fixed
- Fixed `NameError` crash in `v1/knowledge.py` (`macro` referenced but never declared as a parameter).
- Fixed typo in advanced mode session output message.
- Removed stale inline comments from `client.py` and `cli.py`.

### Changed
- Updated README with dedicated sections for v1 legacy API support, multi-profile management, session deduplication, and environment variable reference.

## [1.1.3] - 2026-03-11
### Fixed
- `repos list` now resolves blank Path column by trying `repository_path`, `path`, and `name` keys from the API response.
- `secrets list` no longer crashes when the API returns a raw list instead of a dict with a key.
- `sessions cost <id>` now pulls cost data from the org-scoped `get_session` endpoint instead of the enterprise-only consumption path.
- `sessions insights` on v1 now displays a readable error with a hint to switch to v3 instead of a confusing JSON blob.
- `--json` flag added to `repos list` and `secrets list` for raw programmatic output.

## [1.1.2] - 2026-03-11
### Fixed
- **Critical Profile Bug**: Stopped `cli.py` from statically overriding the active user profile back to `"default"` on every boot unless the `--profile` flag is explicitly passed over the terminal.

## [1.1.1] - 2026-03-11
### Fixed
- Fixed v1 API HTTP redirects stripping authorization headers on org-scoped endpoints (403 errors).
- Fixed `devin configure` crash due to a missing `Prompt` module import.
- Fixed v1 `devin sessions messages` command by creating a polyfill data extractor for legacy payloads.
- Fixed v1 `devin sessions insights` to gracefully exit instead of throwing a generic missing endpoint error.
- Fixed v1 API payload formats by universally switching from URL-encoded `data=` to strictly typed `json=` bodies.
- Fixed message display loop to properly fallback between v3 `content` and v1 `message` string definitions.

## [1.1.0] - 2026-03-11
### Added
- **Dual-Token Profiles**: Support for securely managing Personal (`apk_user_`) and Service Account (`cog_`) tokens via the `--profile` global flag.
- **Legacy API Proxy**: Native v1 API backward compatibility routing, allowing older legacy scripts to execute gracefully over the new v3 architecture.
- **Session Deduplication (Anti-Spam)**: Built-in SHA-256 caching of previous prompts to intercept and prevent accidental duplicate session creation loops.
- **Advanced Mode Auth**: Secure web browser intersection for `advanced_mode_url` requirements when initiating CLI sessions.
- **Playbook Safeguards**: Implemented strict 500KB payload limit warnings with manual overrides for Playbook creation and updates to prevent 413 HTTP crashes.
- **Dynamic Help Menus**: Typer help commands successfully dynamically reflect `(V1 Legacy Mode)` tags based on active profile switching.
- **Global `--version`**: New binary flag reporting accurate package metadata matching PyPI.

## [0.1.0] - 2024-05-23
### Added
- Initial release
- Session management (create, list, get, terminate)
- Message sending and history viewing
- Watch command for live status polling
- File attachments
- Knowledge, Playbook, and Secret management commands
- Shell completion support
