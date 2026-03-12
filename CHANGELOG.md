# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
