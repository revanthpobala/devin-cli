import warnings
import os
import sys

# Suppress urllib3 warnings early for clean JSON output
if "--json" in sys.argv or os.environ.get("DEVIN_OUTPUT_FORMAT") == "json":
    warnings.filterwarnings("ignore")
    os.environ["DEVIN_OUTPUT_FORMAT"] = "json"

import typer
import time
import json
import httpx
import functools
import yaml
import asyncio
from pathlib import Path
from typing import List, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from devin_cli.config import config
from devin_cli.api import sessions, knowledge, playbooks, secrets, attachments, repositories, schedules, organizations, members, consumption
from devin_cli.api.client import client, APIError
import webbrowser
import sys
import hashlib
import importlib.metadata
from rich.prompt import Prompt

try:
    __version__ = importlib.metadata.version("devin-cli")
except importlib.metadata.PackageNotFoundError:
    __version__ = "unknown"

# Early profile detection for accurate --help menus
if "--profile" in sys.argv:
    idx = sys.argv.index("--profile")
    if idx + 1 < len(sys.argv):
        config.active_profile = sys.argv[idx + 1]
elif "-p" in sys.argv:
    idx = sys.argv.index("-p")
    if idx + 1 < len(sys.argv):
        config.active_profile = sys.argv[idx + 1]

IS_V1 = config.api_version == "v1"
v1_tag = " [bold yellow](Legacy v1 API)[/bold yellow]" if IS_V1 else ""
v3_only = " [bold red](v3 Only)[/bold red]" if IS_V1 else ""

app = typer.Typer(
    help=f"Unofficial CLI for Devin AI{' (V1 Legacy Mode)' if IS_V1 else ' v3'}",
    no_args_is_help=True,
    rich_markup_mode="rich"
)
console = Console()

# --- Sub-Apps for Organization API ---
session_app = typer.Typer(help=f"Manage Devin sessions{v1_tag}", no_args_is_help=True)
knowledge_app = typer.Typer(help=f"Manage knowledge notes{v1_tag}", no_args_is_help=True)
playbook_app = typer.Typer(help=f"Manage team playbooks{v1_tag}", no_args_is_help=True)
secret_app = typer.Typer(help=f"Manage organization secrets{v1_tag}", no_args_is_help=True)
schedule_app = typer.Typer(help=f"Manage session schedules{v3_only}", no_args_is_help=True)
attachment_app = typer.Typer(help=f"Manage session attachments{v1_tag}", no_args_is_help=True)
repo_app = typer.Typer(help=f"Manage organization repositories{v3_only}", no_args_is_help=True)
enterprise_app = typer.Typer(help=f"Enterprise-scoped operations{v3_only}", no_args_is_help=True)

app.add_typer(session_app, name="sessions", help="Manage Devin sessions")
app.add_typer(session_app, name="session", hidden=True)
app.add_typer(knowledge_app, name="knowledge", help="Manage knowledge notes")
app.add_typer(playbook_app, name="playbooks", help="Manage team playbooks")
app.add_typer(secret_app, name="secrets", help="Manage organization secrets")
app.add_typer(schedule_app, name="schedules", help="Manage session schedules")
app.add_typer(repo_app, name="repos", help="Manage organization repositories")
app.add_typer(enterprise_app, name="enterprise", help="Enterprise management")

ASCII_LOGO = r"""
[bold cyan]
    ____             _          _________    ____
   / __ \___ _   __(_)___     / ____/ /   /  _/
  / / / / _ \ | / / / __ \   / /   / /    / /  
 / /_/ /  __/ |/ / / / / /  / /___/ /____/ /   
/_____/\___/|___/_/_/ /_/   \____/_____/___/   
[/bold cyan]
"""

@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="Configuration profile to use (e.g., service, personal)"),
    version: Optional[bool] = typer.Option(None, "--version", "-v", help="Show the application's version and exit."),
    json_format: bool = typer.Option(False, "--json", help="Output raw JSON (for AI agents & scripting)"),
):
    """
    Unofficial CLI for Devin AI v3.
    """
    if json_format:
        os.environ["DEVIN_OUTPUT_FORMAT"] = "json"
        
    if version:
        console.print(f"devin CLI version: {__version__}")
        raise typer.Exit()
        
    if profile:
        config.active_profile = profile
    if ctx.invoked_subcommand is None:
        console.print(ASCII_LOGO)

def handle_api_error(func):
    """Decorator to handle API errors gracefully."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        import os
        is_json = os.environ.get("DEVIN_OUTPUT_FORMAT") == "json"
        original_print = console.print
        try:
            if is_json:
                console.print = lambda *a, **k: None

            result = func(*args, **kwargs)
            
            if is_json:
                console.print = original_print
                if result is not None:
                    print(json.dumps(result, indent=2))
                    
            return result
        except BaseException as e:
            if is_json:
                console.print = original_print
            if isinstance(e, typer.Exit):
                raise e
            elif isinstance(e, httpx.RequestError):
                if is_json:
                    print(json.dumps({"error": "Connection error", "details": str(e)}, indent=2))
                else:
                    console.print(f"[bold red]Connection Error:[/bold red] Failed to connect to {config.base_url}")
                    console.print(f"[dim]{str(e)}[/dim]")
                raise typer.Exit(1)
            elif hasattr(e, "response"): # Standard APIError handling
                if is_json:
                    try:
                        err_json = e.response.json()
                    except Exception:
                        err_json = {"error": str(e)}
                    print(json.dumps(err_json, indent=2))
                else:
                    console.print(f"[bold red]API Error:[/bold red] {e}")
                raise typer.Exit(1)
            else:
                if is_json:
                    print(json.dumps({"error": str(e)}, indent=2))
                else:
                    console.print(f"[bold red]Error:[/bold red] {e}")
                raise typer.Exit(1)
            
    return wrapper

def get_current_session_id():
    sid = config.current_session_id
    if not sid:
        console.print("[bold red]Error:[/bold red] No active session. Create one with [bold cyan]create-session[/bold cyan] or use [bold cyan]use-session[/bold cyan].")
        raise typer.Exit(1)
    return sid

@app.command()
def configure(
    token: str = typer.Option(..., prompt="Devin API Token (starts with apk_ or cog_)", help="Your Devin API Token"),
    base_url: str = typer.Option("https://api.devin.ai/v3", prompt="Devin API Base URL", help="Devin API Base URL"),
    org_id: Optional[str] = typer.Option(None, "--org", prompt="Organization ID (optional)", help="Default Organization ID"),
    profile: Optional[str] = typer.Option(None, "--profile", help="Profile to configure (overrides global --profile)"),
):
    """
    Configure the CLI with your Devin API token and organization.
    """
    if profile:
        config.active_profile = profile
        
    if not (token.startswith("apk_") or token.startswith("cog_")):
        console.print("[bold yellow]Warning:[/bold yellow] Token format might be outdated. v3 tokens usually start with 'apk_' or 'cog_'.")
    
    api_version_prompt = Prompt.ask(f"API Version for profile '{config.active_profile}' (v3/v1)", default=config.api_version or "v3")

    if "api.devin.ai" in base_url and "v3" in base_url and api_version_prompt == "v1":
        base_url = base_url.replace("/v3", "/v1")
    elif "api.devin.ai" in base_url and "v1" in base_url and api_version_prompt == "v3":
        base_url = base_url.replace("/v1", "/v3")

    config.api_token = token
    config.base_url = base_url
    config.api_version = api_version_prompt
    if org_id:
        config.org_id = org_id
    console.print(f"[green]Configuration saved to {config.config_file}[/green]")
    return None

# --- Sessions ---
@session_app.command("create")
@handle_api_error
def create_session_cmd(
    prompt: Optional[str] = typer.Argument(None, help="The prompt for the session"),
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="Read prompt from file"),
    title: Optional[str] = typer.Option(None, "--title", "-t", help="Custom session title"),
    org: Optional[str] = typer.Option(None, "--org", help="Override organization ID"),
    max_acu: Optional[int] = typer.Option(None, "--max-acu", help="Maximum ACU limit"),
    advanced_mode: Optional[str] = typer.Option(None, "--advanced-mode", help="Advanced mode type: analyze | create_playbook | improve_playbook | batch | manage_knowledge"),
    playbook_id: Optional[str] = typer.Option(None, "--playbook-id", help="Playbook ID to apply (v3 only)"),
    child_playbook_id: Optional[str] = typer.Option(None, "--child-playbook-id", help="Playbook ID applied to each sub-session in batch mode (v3 only)"),
    tags: Optional[List[str]] = typer.Option(None, "--tag", help="Session tags (repeatable)"),
    repos: Optional[List[str]] = typer.Option(None, "--repo", help="Repository URLs to attach (v3 only, repeatable)"),
    knowledge_ids: Optional[List[str]] = typer.Option(None, "--knowledge-id", help="Knowledge IDs to attach (repeatable)"),
    secret_ids: Optional[List[str]] = typer.Option(None, "--secret-id", help="Secret IDs to inject (v3 only, repeatable)"),
    session_links: Optional[List[str]] = typer.Option(None, "--session-link", help="Session URLs to link as context (v3 only, repeatable)"),
    attachment_urls: Optional[List[str]] = typer.Option(None, "--attachment-url", help="Attachment URLs to attach (v3 only, repeatable)"),
    create_as_user_id: Optional[str] = typer.Option(None, "--create-as-user-id", help="Enterprise: create session on behalf of this user ID (v3 only)"),
    bypass_approval: bool = typer.Option(False, "--bypass-approval", help="Skip UI approval step — child sessions start immediately (v3 only)"),
    structured_output_schema: Optional[str] = typer.Option(None, "--structured-output-schema", help="JSON schema string for structured response output (v3 only)"),
    force: bool = typer.Option(False, "--force", help="Force creation even if duplicate prompt is detected"),
    wait: bool = typer.Option(False, "--wait", "-w", help="Block until the session reaches a terminal status"),
    interval: int = typer.Option(5, "--interval", help="Polling interval in seconds when --wait is used"),
):
    """Create a new Devin session."""
    if org: config.temporary_org_id = org

    api_ver = config.api_version
    console.print(f"[dim]Using profile: {config.active_profile or 'default'} ({api_ver})[/dim]")

    v3_only_used = [x for x, v in [
        ("--advanced-mode", advanced_mode),
        ("--playbook-id", playbook_id),
        ("--child-playbook-id", child_playbook_id),
        ("--repos", repos),
        ("--secret-ids", secret_ids),
        ("--session-links", session_links),
        ("--attachment-urls", attachment_urls),
        ("--create-as-user-id", create_as_user_id),
        ("--bypass-approval", bypass_approval or None),
        ("--structured-output-schema", structured_output_schema),
    ] if v]
    if api_ver == "v1" and v3_only_used:
        console.print(f"[bold yellow]Warning:[/bold yellow] The following flags are v3-only and will be ignored on a v1 profile: {', '.join(v3_only_used)}")
        console.print("  Run [bold cyan]devin configure[/bold cyan] to switch to a v3 profile.")

    if file:
        prompt_text = file.read_text()
    elif prompt:
        prompt_text = prompt
    else:
        console.print("[bold red]Error:[/bold red] Must provide prompt or --file")
        raise typer.Exit(1)

    prompt_hash = hashlib.sha256(prompt_text.encode('utf-8')).hexdigest()
    existing_sid = config.get_session_by_prompt_hash(prompt_hash)

    if existing_sid and not force:
        console.print(f"[bold yellow]Duplicate Detected:[/bold yellow] You recently created a session with this exact prompt.")
        console.print(f"Existing Session ID: [bold cyan]{existing_sid}[/bold cyan]")
        if not typer.confirm("Are you sure you want to create a duplicate session?"):
            console.print("Session creation cancelled. Use the existing session ID above to resume.")
            raise typer.Exit()

    with console.status("[bold green]Creating session...[/bold green]"):
        resp = sessions.create_session(
            prompt=prompt_text,
            title=title,
            max_acu_limit=max_acu,
            advanced_mode=advanced_mode,
            playbook_id=playbook_id,
            child_playbook_id=child_playbook_id,
            tags=tags or None,
            repos=repos or None,
            knowledge_ids=knowledge_ids or None,
            secret_ids=secret_ids or None,
            session_links=session_links or None,
            attachment_urls=attachment_urls or None,
            create_as_user_id=create_as_user_id,
            bypass_approval=bypass_approval,
            structured_output_schema=structured_output_schema,
        )
        sid = resp.get("session_id")

        if "advanced_mode_url" in resp:
            adv_url = resp["advanced_mode_url"]
            console.print(f"[bold yellow]Advanced Mode Authorization Required![/bold yellow]")
            console.print(f"Please complete the advanced mode setup in your browser:")
            console.print(f"[bold cyan]{adv_url}[/bold cyan]")
            if typer.confirm("Open browser now?"):
                import webbrowser
                webbrowser.open(adv_url)

        if sid:
            config.current_session_id = sid
            config.save_prompt_hash(prompt_hash, sid)
            console.print(f"[green]Session created:[/green] {sid}")
            console.print(f"[bold cyan]URL:[/bold cyan] {resp.get('url')}")

            if wait:
                terminal_statuses = {"stopped", "finished", "error", "cancelled", "failed"}
                console.print(f"[dim]Waiting for session to complete (polling every {interval}s)...[/dim]")
                with console.status("[bold green]Running...[/bold green]") as s:
                    while True:
                        time.sleep(interval)
                        poll = sessions.get_session(sid)
                        current_status = poll.get("status_enum", "").lower()
                        s.update(f"[bold green]Status: {current_status}[/bold green]")
                        if current_status in terminal_statuses:
                            console.print(f"[bold green]Session finished:[/bold green] {current_status}")
                            break
        else:
            console.print("[yellow]Session created, but no ID returned immediately (awaiting advanced mode setup).[/yellow]")
        
    return resp


@session_app.command("list")
@handle_api_error
def list_sessions_cmd(
    limit: int = 10,
    org: Optional[str] = typer.Option(None, "--org"),
    json_output: bool = typer.Option(False, "--json"),
):
    """List sessions."""
    if org: config.temporary_org_id = org
    resp = sessions.list_sessions(limit=limit)
    sess_list = resp.get("items", resp.get("sessions", []))
    
    if not sess_list and config.api_token and config.api_token.startswith("cog_"):
        console.print("[yellow]Warning: Service tokens (cog_) may only have visibility into sessions they explicitly created, not all organization sessions.[/yellow]")
        
    if json_output:
        console.print(json.dumps(sess_list, indent=2))
    else:
        table = Table(title="Devin Sessions")
        table.add_column("ID", style="cyan")
        table.add_column("Status", style="magenta")
        table.add_column("Title")
        for s in sess_list:
            table.add_row(s.get("session_id"), s.get("status_enum"), s.get("title") or s.get("prompt", "")[:50])
        console.print(table)
    
    return resp

@session_app.command("get")
@handle_api_error
def get_session_cmd(
    session_id: Optional[str] = typer.Argument(None),
    org: Optional[str] = typer.Option(None, "--org"),
):
    """Get detailed session info."""
    if org: config.temporary_org_id = org
    sid = session_id or get_current_session_id()
    resp = sessions.get_session(sid)
    console.print(Panel(json.dumps(resp, indent=2), title=f"Session {sid}"))
    
    return resp

@session_app.command("insights")
@handle_api_error
def session_insights_cmd(
    session_id: Optional[str] = typer.Argument(None),
    org: Optional[str] = typer.Option(None, "--org"),
):
    """Get technical insights for a session (ACUs, etc)."""
    if org: config.temporary_org_id = org
    sid = session_id or get_current_session_id()
    resp = sessions.get_session_insights(sid)
    if isinstance(resp, dict) and "error" in resp:
        console.print(f"[bold yellow]Note:[/bold yellow] {resp['error']}")
        console.print("Tip: Switch to v3 with [bold cyan]devin configure[/bold cyan] or use [bold cyan]--profile [v3-profile][/bold cyan]")
    else:
        console.print(Panel(json.dumps(resp, indent=2), title=f"Insights for {sid}"))
        
    return resp

@session_app.command("cost")
@handle_api_error
def session_cost_cmd(
    session_id: Optional[str] = typer.Argument(None, help="Specific session ID to check cost for"),
    org: Optional[str] = typer.Option(None, "--org"),
):
    """View ACU consumption."""
    if org: config.temporary_org_id = org
    if session_id:
        resp = sessions.get_session(session_id)
        acus = resp.get("acus_consumed") or resp.get("acu_used")
        cost_data = {
            "session_id": resp.get("session_id"),
            "status": resp.get("status_enum"),
            "acus_consumed": acus,
        }
        console.print(Panel(json.dumps(cost_data, indent=2), title=f"Session Cost: {session_id}"))
        if acus is None:
            console.print("[yellow]ACU data unavailable — this may be a v1 API session or a service token without cost visibility.[/yellow]")
    else:
        resp = consumption.get_daily_consumption_breakdown()
        console.print(Panel(json.dumps(resp, indent=2), title="Daily Consumption"))
        
    return resp

@session_app.command("message")
@handle_api_error
def send_message_cmd(
    text: Optional[str] = typer.Argument(None, help="Message text"),
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="Read message from file"),
    session_id: Optional[str] = typer.Option(None, "--id"),
    org: Optional[str] = typer.Option(None, "--org"),
):
    """Send a message to a session."""
    if org: config.temporary_org_id = org
    sid = session_id or get_current_session_id()
    if file:
        if not file.exists():
            console.print(f"[bold red]Error:[/bold red] File not found: {file}")
            raise typer.Exit(1)
        msg_text = file.read_text()
    elif text:
        msg_text = text
    else:
        console.print("[bold red]Error:[/bold red] Provide message text or --file")
        raise typer.Exit(1)
    sessions.send_message(sid, msg_text)
    console.print(f"[green]Message sent to {sid}[/green]")
    return None

@session_app.command("messages")
@handle_api_error
def list_messages_cmd(
    session_id: Optional[str] = typer.Argument(None),
    org: Optional[str] = typer.Option(None, "--org"),
):
    """List messages in a session."""
    if org: config.temporary_org_id = org
    sid = session_id or get_current_session_id()
    resp = sessions.get_session_messages(sid)
    msgs = resp.get("messages", [])
    for m in msgs:
        role = m.get("role", "unknown")
        content = m.get("message", "") or m.get("content", "")
        console.print(f"[bold cyan]{role}:[/bold cyan] {content}")
        console.print("---")
        
    return resp

@session_app.command("terminate")
@handle_api_error
def terminate_session_cmd(
    session_id: Optional[str] = typer.Argument(None),
    org: Optional[str] = typer.Option(None, "--org"),
):
    """Terminate an active session."""
    if org: config.temporary_org_id = org
    sid = session_id or get_current_session_id()
    if typer.confirm(f"Terminate session {sid}?"):
        sessions.terminate_session(sid)
        console.print(f"[green]Session {sid} terminated.[/green]")
    return None

# --- Knowledge ---
@knowledge_app.command("list")
@handle_api_error
def list_knowledge_cmd(org: Optional[str] = typer.Option(None, "--org")):
    """List knowledge notes."""
    if org: config.temporary_org_id = org
    resp = knowledge.list_knowledge()
    items = resp.get("notes", resp.get("knowledge", []))
    table = Table(title="Knowledge Base")
    table.add_column("ID", style="cyan")
    table.add_column("Name")
    for item in items:
        table.add_row(item.get("id"), item.get("title") or item.get("name"))
    console.print(table)

    return resp
@knowledge_app.command("create")
@handle_api_error
def create_knowledge_cmd(
    title: str, 
    body: str, 
    trigger: str = typer.Option("", "--trigger", help="Trigger description"),
    org: Optional[str] = typer.Option(None, "--org"),
):
    """Create a knowledge note."""
    if org: config.temporary_org_id = org
    resp = knowledge.create_knowledge(title=title, body=body, trigger=trigger)
    console.print(f"[green]Created note:[/green] {resp.get('id')}")
    
    return resp
    
    
@knowledge_app.command("get")
@handle_api_error
def get_knowledge_cmd(
    knowledge_id: str,
    org: Optional[str] = typer.Option(None, "--org"),
):
    """Get detailed content of a knowledge note."""
    if org: config.temporary_org_id = org
    resp = knowledge.get_knowledge(knowledge_id)
    console.print(Panel(json.dumps(resp, indent=2), title=f"Knowledge: {knowledge_id}"))
    return resp

@knowledge_app.command("delete")
@handle_api_error
def delete_knowledge_cmd(
    knowledge_id: str,
    org: Optional[str] = typer.Option(None, "--org"),
):
    """Delete a knowledge note."""
    if org: config.temporary_org_id = org
    if typer.confirm(f"Delete knowledge {knowledge_id}?"):
        knowledge.delete_knowledge(knowledge_id)
        console.print(f"[green]Knowledge {knowledge_id} deleted.[/green]")
        
    return None

# --- Playbooks ---
@playbook_app.command("list")
@handle_api_error
def list_playbooks_cmd(
    org: Optional[str] = typer.Option(None, "--org"),
    json_output: bool = typer.Option(False, "--json", help="Output raw JSON"),
):
    """List team playbooks."""
    if org: config.temporary_org_id = org
    resp = playbooks.list_playbooks()
    items = resp.get("items", []) if isinstance(resp, dict) else resp
    
    if json_output:
        console.print(json.dumps(items, indent=2))
        return

    table = Table(title="Playbooks")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Title")
    for item in items:
        if isinstance(item, dict):
            table.add_row(item.get("playbook_id", ""), item.get("title", ""))
    console.print(table)
    return resp

@playbook_app.command("update")
@handle_api_error
def update_playbook_cmd(
    playbook_id: str,
    title: str,
    body: Optional[str] = typer.Option(None, "--body"),
    macro: Optional[str] = typer.Option(None, "--macro"),
    org: Optional[str] = typer.Option(None, "--org"),
):
    """Update a team playbook."""
    body_bytes = len(body.encode('utf-8')) if body else 0
    if body_bytes > 500 * 1024:
        console.print(f"[bold yellow]Warning:[/bold yellow] Playbook body is {body_bytes / 1024:.1f}KB. Devin API may reject payloads > 500KB.")
        if not typer.confirm("Attempt to send anyway?"):
            raise typer.Exit()
            
    if org: config.temporary_org_id = org
    resp = playbooks.update_playbook(playbook_id, title=title, body=body, macro=macro)
    console.print(f"[green]Playbook updated:[/green] {playbook_id}")
    
    return resp

@playbook_app.command("create")
@handle_api_error
def create_playbook_cmd(
    title: str, 
    body: str, 
    macro: Optional[str] = None,
    org: Optional[str] = typer.Option(None, "--org"),
):
    """Create a new team playbook."""
    body_bytes = len(body.encode('utf-8')) if body else 0
    if body_bytes > 500 * 1024:
        console.print(f"[bold yellow]Warning:[/bold yellow] Playbook body is {body_bytes / 1024:.1f}KB. Devin API may reject payloads > 500KB.")
        if not typer.confirm("Attempt to send anyway?"):
            raise typer.Exit()
            
    if org: config.temporary_org_id = org
    resp = playbooks.create_playbook(title, body, macro)
    console.print(f"[green]Playbook created:[/green] {resp.get('playbook_id')}")
    
    return resp

@playbook_app.command("delete")
@handle_api_error
def delete_playbook_cmd(
    playbook_id: str,
    org: Optional[str] = typer.Option(None, "--org"),
):
    """Delete a team playbook."""
    if org: config.temporary_org_id = org
    if typer.confirm(f"Delete playbook {playbook_id}?"):
        playbooks.delete_playbook(playbook_id)
        console.print(f"[green]Playbook {playbook_id} deleted.[/green]")
    return None

# --- Secrets ---
@secret_app.command("list")
@handle_api_error
def list_secrets_cmd(
    org: Optional[str] = typer.Option(None, "--org"),
    json_output: bool = typer.Option(False, "--json"),
):
    """List organization secrets."""
    if org: config.temporary_org_id = org
    resp = secrets.list_secrets()
    if isinstance(resp, dict):
        items = resp.get("secrets", resp.get("items", []))
    elif isinstance(resp, list):
        items = resp
    else:
        console.print(f"[yellow]Unexpected response format: {type(resp).__name__}[/yellow]")
        items = []
    if json_output:
        console.print(json.dumps(items, indent=2))
        return
    table = Table(title="Secrets")
    table.add_column("ID", style="cyan")
    table.add_column("Name")
    for item in items:
        if isinstance(item, dict):
            table.add_row(item.get("id"), item.get("name"))
    console.print(table)
    return resp

@secret_app.command("delete")
@handle_api_error
def delete_secret_cmd(
    secret_id: str,
    org: Optional[str] = typer.Option(None, "--org"),
):
    """Delete an organization secret."""
    if org: config.temporary_org_id = org
    if typer.confirm(f"Delete secret {secret_id}?"):
        secrets.delete_secret(secret_id)
        console.print(f"[green]Secret {secret_id} deleted.[/green]")
    return None

@secret_app.command("create")
@handle_api_error
def create_secret_cmd(
    name: str, 
    value: str,
    org: Optional[str] = typer.Option(None, "--org"),
):
    """Create an organization secret."""
    if org: config.temporary_org_id = org
    secrets.create_secret(name, value)
    console.print(f"[green]Secret '{name}' created.[/green]")
    
    return None

# --- Schedules ---
@schedule_app.command("list")
@handle_api_error
def list_schedules_cmd(org: Optional[str] = typer.Option(None, "--org")):
    """List recurring schedules."""
    if org: config.temporary_org_id = org
    resp = schedules.list_schedules()
    items = resp.get("schedules", resp.get("items", []))
    table = Table(title="Schedules")
    table.add_column("ID", style="cyan")
    table.add_column("Title")
    table.add_column("Cron")
    for item in items:
        table.add_row(item.get("id"), item.get("title"), item.get("cron"))
    console.print(table)
    

    return resp
@schedule_app.command("create")
@handle_api_error
def create_schedule_cmd(
    prompt: str, 
    cron: str, 
    title: Optional[str] = None,
    org: Optional[str] = typer.Option(None, "--org"),
):
    """Create a recurring schedule."""
    if org: config.temporary_org_id = org
    resp = schedules.create_schedule(prompt=prompt, cron=cron, title=title)
    console.print(f"[green]Created schedule:[/green] {resp.get('id')}")

    return resp

# --- Repositories ---
@repo_app.command("list")
@handle_api_error
def list_repos_cmd(
    org: Optional[str] = typer.Option(None, "--org"),
    json_output: bool = typer.Option(False, "--json"),
):
    """List repositories indexed for Devin."""
    if org: config.temporary_org_id = org
    resp = repositories.list_repositories()
    if isinstance(resp, list):
        items = resp
    elif isinstance(resp, dict):
        items = resp.get("repositories") or resp.get("items") or resp.get("data") or []
    else:
        items = []
    if json_output:
        console.print(json.dumps(items, indent=2))
        return
    table = Table(title="Repositories")
    table.add_column("Path", style="cyan")
    table.add_column("Indexed", style="green")
    for item in items:
        path = (
            item.get("repo_path")
            or item.get("repository_path")
            or item.get("repo_name")
            or item.get("full_name")
            or item.get("path")
            or item.get("name")
            or ""
        )
        indexing_status = item.get("indexing_status") or {}
        indexed = (
            indexing_status.get("indexing_enabled")
            or item.get("is_indexed")
            or item.get("indexed")
        )
        table.add_row(path, "Yes" if indexed else "No")
    console.print(table)
    return resp

@repo_app.command("index")
@handle_api_error
def index_repo_cmd(
    path: str,
    org: Optional[str] = typer.Option(None, "--org"),
):
    """Index a repository."""
    if org: config.temporary_org_id = org
    repositories.index_repository(path)
    console.print(f"[green]Indexing started for {path}[/green]")

    return None

# --- Attachments ---
@attachment_app.command("upload")
@handle_api_error
def upload_attachment_cmd(
    path: Path,
    org: Optional[str] = typer.Option(None, "--org"),
):
    """Upload a file to Devin."""
    if org: config.temporary_org_id = org
    resp = attachments.upload_file(str(path))
    console.print(f"[green]Uploaded:[/green] {resp}")
    return resp

@attachment_app.command("download")
@handle_api_error
def download_attachment_cmd(
    uuid: str, 
    name: str, 
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
    org: Optional[str] = typer.Option(None, "--org"),
):
    """Download an attachment."""
    if org: config.temporary_org_id = org
    content = attachments.download_attachment(uuid, name)
    out_path = output or Path(name)
    out_path.write_bytes(content)
    console.print(f"[green]Downloaded to:[/green] {out_path}")

    return None

# --- Enterprise Discovery ---
@enterprise_app.command("whoami")
@handle_api_error
def whoami_cmd():
    """Show current identity details."""
    resp = members.get_self()
    console.print(Panel(json.dumps(resp, indent=2), title="Who Am I"))

    return resp
@enterprise_app.command("list-orgs")
@handle_api_error
def list_orgs_cmd():
    """List all accessible organizations."""
    resp = organizations.list_organizations()
    console.print(Panel(json.dumps(resp, indent=2), title="Organizations"))

    return resp
# --- Global Commands ---
@app.command("use")
def use_session_cmd(session_id: str):
    """Switch the current active session."""
    config.current_session_id = session_id
    console.print(f"[green]Switched to session {session_id}[/green]")
    return {"current_session_id": session_id}

@app.command("status")
@handle_api_error
def status_cmd():
    """Show the status of the current active session."""
    sid = get_current_session_id()
    resp = sessions.get_session(sid)
    status = resp.get("status_enum", "unknown")
    title  = resp.get("title") or resp.get("prompt", "")[:60]
    url    = resp.get("url", "")
    acus   = resp.get("acus_consumed") or resp.get("acu_used")

    color = {"running": "green", "stopped": "red", "paused": "yellow"}.get(status, "cyan")
    console.print(f"[bold]Session:[/bold] [cyan]{sid}[/cyan]")
    console.print(f"[bold]Status:[/bold]  [{color}]{status}[/{color}]")
    if title:
        console.print(f"[bold]Title:[/bold]   {title}")
    if acus is not None:
        console.print(f"[bold]ACUs:[/bold]    {acus}")
    if url:
        console.print(f"[bold]URL:[/bold]     [underline]{url}[/underline]")

    return resp
@app.command("open")
@handle_api_error
def open_cmd(
    session_id: Optional[str] = typer.Argument(None, help="Session ID to open (defaults to active session)"),
):
    """Open the active session in your browser."""
    sid = session_id or get_current_session_id()
    resp = sessions.get_session(sid)
    url = resp.get("url")
    if not url:
        console.print("[bold red]Error:[/bold red] No URL available for this session.")
        raise typer.Exit(1)
    webbrowser.open(url)
    console.print(f"[green]Opened:[/green] {url}")

    return resp

@session_app.command("watch")
@handle_api_error
def watch_session_cmd(
    session_id: Optional[str] = typer.Argument(None, help="Session ID to watch (defaults to active session)"),
    interval: int = typer.Option(3, "--interval", "-i", help="Polling interval in seconds"),
    org: Optional[str] = typer.Option(None, "--org"),
):
    """Live-watch a session — polls status and streams new messages."""
    if org: config.temporary_org_id = org
    sid = session_id or get_current_session_id()

    terminal_statuses = {"stopped", "finished", "error", "cancelled", "failed"}
    backoff = interval

    def build_status_panel(resp: dict) -> Panel:
        status_val = resp.get("status_enum", "unknown")
        title_val  = resp.get("title") or resp.get("prompt", "")[:60]
        acus       = resp.get("acus_consumed") or resp.get("acu_used", "n/a")
        color      = {"running": "green", "stopped": "red", "paused": "yellow",
                      "finished": "blue", "blocked": "red"}.get(status_val, "cyan")
        text = Text()
        text.append("Session: ", style="bold")
        text.append(f"{sid}\n", style="cyan")
        text.append("Status:  ", style="bold")
        text.append(f"{status_val}\n", style=color)
        if title_val:
            text.append(f"Title:   {title_val}\n")
        text.append(f"ACUs:    {acus}\n")
        so = resp.get("structured_output")
        if so:
            text.append("\nStructured Output:\n", style="bold")
            text.append(json.dumps(so, indent=2))
        text.append("\nPress Ctrl+C to stop watching.", style="dim")

    console.print(f"[bold cyan]Watching session {sid}[/bold cyan] (Ctrl+C to stop)")

    with Live(console=console, refresh_per_second=4) as live:
        try:
            while True:
                resp = sessions.get_session(sid)
                live.update(build_status_panel(resp))

                if resp.get("status_enum", "").lower() in terminal_statuses:
                    live.update(build_status_panel(resp))
                    break

                time.sleep(min(backoff, 30))
                backoff = min(backoff * 1.5, 30)
        except KeyboardInterrupt:
            console.print("\n[dim]Watch stopped.[/dim]")
            return

    console.print(f"[bold green]Session {resp.get('status_enum')}![/bold green]")
    return resp

# --- Flat top-level aliases (backward compat with 0.1.x command structure) ---

@app.command("watch", hidden=True)
@handle_api_error
def watch_cmd(
    session_id: Optional[str] = typer.Argument(None),
    interval: int = typer.Option(3, "--interval", "-i"),
):
    """Alias for: devin sessions watch"""
    watch_session_cmd(session_id=session_id, interval=interval, org=None)
    return None

@app.command("message")
@handle_api_error
def message_cmd(
    text: Optional[str] = typer.Argument(None, help="Message to send"),
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="Read message from file"),
    session_id: Optional[str] = typer.Option(None, "--id"),
):
    """Send a message to the active session."""
    sid = session_id or get_current_session_id()
    if file:
        if not file.exists():
            console.print(f"[bold red]Error:[/bold red] File not found: {file}")
            raise typer.Exit(1)
        msg_text = file.read_text()
    elif text:
        msg_text = text
    else:
        console.print("[bold red]Error:[/bold red] Provide message text or --file")
        raise typer.Exit(1)
    sessions.send_message(sid, msg_text)
    console.print(f"[green]Message sent to {sid}[/green]")
    return None

@app.command("terminate")
@handle_api_error
def terminate_cmd(
    session_id: Optional[str] = typer.Argument(None),
):
    """Terminate the active session."""
    sid = session_id or get_current_session_id()
    if typer.confirm(f"Terminate session {sid}?"):
        sessions.terminate_session(sid)
        console.print(f"[green]Session {sid} terminated.[/green]")
    return None

@app.command("list-sessions")
@handle_api_error
def list_sessions_top_cmd(
    limit: int = typer.Option(10, "--limit", "-n"),
    json_output: bool = typer.Option(False, "--json"),
):
    """List recent sessions (alias for: devin sessions list)."""
    resp = sessions.list_sessions(limit=limit)
    sess_list = resp.get("items", resp.get("sessions", []))
    if json_output:
        console.print(json.dumps(sess_list, indent=2))
        return
    table = Table(title="Devin Sessions")
    table.add_column("ID", style="cyan")
    table.add_column("Status", style="magenta")
    table.add_column("Title")
    for s in sess_list:
        table.add_row(s.get("session_id"), s.get("status_enum"), s.get("title") or s.get("prompt", "")[:50])
    console.print(table)
    return resp

@app.command("create-session")
@handle_api_error
def create_session_top_cmd(
    prompt: str = typer.Argument(..., help="The prompt for the session"),
    title: Optional[str] = typer.Option(None, "--title", "-t"),
    wait: bool = typer.Option(False, "--wait", "-w", help="Block until the session completes"),
    interval: int = typer.Option(5, "--interval"),
    force: bool = typer.Option(False, "--force"),
):
    """Create a new session (alias for: devin sessions create)."""
    create_session_cmd(prompt=prompt, file=None, title=title, org=None, max_acu=None,
                       advanced_mode=None, playbook_id=None, child_playbook_id=None,
                       tags=None, repos=None, knowledge_ids=None, secret_ids=None,
                       session_links=None, attachment_urls=None, create_as_user_id=None,
                       bypass_approval=False, structured_output_schema=None,
                       force=force, wait=wait, interval=interval)
    return None

@app.command("upload")
@handle_api_error
def upload_cmd(path: Path = typer.Argument(..., help="File to upload")):
    """Upload a file to Devin."""
    resp = attachments.upload_file(str(path))
    console.print(f"[green]Uploaded:[/green] {resp}")

    return resp
@app.command("list-knowledge")
@handle_api_error
def list_knowledge_top_cmd():
    """List knowledge notes (alias for: devin knowledge list)."""
    resp = knowledge.list_knowledge()
    items = resp.get("notes", resp.get("knowledge", []))
    table = Table(title="Knowledge Base")
    table.add_column("ID", style="cyan")
    table.add_column("Title")
    for item in items:
        table.add_row(item.get("id"), item.get("title") or item.get("name"))
    console.print(table)

    return resp
@app.command("attach")
@handle_api_error
def attach_cmd(
    file: Path = typer.Argument(..., help="Context file to upload and attach"),
    prompt: str = typer.Argument(..., help="Task prompt to include with the attachment"),
    title: Optional[str] = typer.Option(None, "--title", "-t"),
    wait: bool = typer.Option(False, "--wait", "-w"),
    interval: int = typer.Option(5, "--interval"),
):
    """Upload a context file and start a session using it."""
    with console.status("[bold green]Uploading file...[/bold green]"):
        upload_resp = attachments.upload_file(str(file))
    url = upload_resp.strip('"') if isinstance(upload_resp, str) else str(upload_resp)
    console.print(f"[green]Uploaded:[/green] {url}")
    full_prompt = f"{prompt}\n\nATTACHMENT: \"{url}\""
    create_session_cmd(prompt=full_prompt, file=None, title=title, org=None, max_acu=None,
                       advanced_mode=None, force=False, wait=wait, interval=interval)
    return None

@app.command("update-tags")
@handle_api_error
def update_tags_cmd(
    session_id: Optional[str] = typer.Argument(None),
    tags: List[str] = typer.Option(..., "--tag", "-t", help="Tags to set (can repeat)"),
):
    """Update tags for a session."""
    sid = session_id or get_current_session_id()
    sessions.update_session_tags(sid, tags)
    console.print(f"[green]Tags updated for session {sid}.[/green]")

    return None

@app.command("history")
def history_cmd():
    """Show the locally cached current session ID."""
    sid = config.current_session_id
    if sid:
        console.print(f"Current local session: [cyan]{sid}[/cyan]")
    else:
        console.print("No current local session.")
    return {"current_session_id": sid}

    return {"current_session_id": sid}

@app.command("messages")
@handle_api_error
def messages_cmd(
    session_id: Optional[str] = typer.Argument(None),
):
    """Show conversation history for a session."""
    sid = session_id or get_current_session_id()
    resp = sessions.get_session_messages(sid)
    msgs = resp.get("messages", [])
    console.print(f"[bold]Conversation for Session {sid}[/bold]")
    console.print("─" * 40)
    for m in msgs:
        role = m.get("role", "unknown")
        content = m.get("message", "") or m.get("content", "")
        console.print(f"[bold cyan]{role}:[/bold cyan] {content}")

    return resp

@app.command("get-session")
@handle_api_error
def get_session_top_cmd(
    session_id: Optional[str] = typer.Argument(None),
):
    """Get details for a session."""
    sid = session_id or get_current_session_id()
    resp = sessions.get_session(sid)
    console.print(Panel(
        f"[bold]Status:[/bold] {resp.get('status_enum')}\n"
        f"[bold]URL:[/bold] {resp.get('url')}\n"
        f"Created: {resp.get('created_at')}",
        title=f"Session {sid}"
    ))
    if "structured_output" in resp:
        console.print("[bold]Structured Output:[/bold]")
        console.print(json.dumps(resp["structured_output"], indent=2))
        
    return resp

@app.command("update-knowledge")
@handle_api_error
def update_knowledge_cmd(
    knowledge_id: str = typer.Argument(...),
    name: Optional[str] = typer.Option(None, "--name"),
    body: Optional[str] = typer.Option(None, "--body"),
    trigger: Optional[str] = typer.Option(None, "--trigger"),
):
    """Update an existing knowledge entry."""
    knowledge.update_knowledge(knowledge_id, title=name, body=body, trigger=trigger)
    console.print(f"[green]Knowledge {knowledge_id} updated.[/green]")
    return None

@app.command("get-knowledge")
@handle_api_error
def get_knowledge_top_cmd(knowledge_id: str = typer.Argument(...)):
    """Get content of a knowledge note (alias for: devin knowledge get)."""
    resp = knowledge.get_knowledge(knowledge_id)
    console.print(Panel(json.dumps(resp, indent=2), title=f"Knowledge: {knowledge_id}"))
    return resp

@app.command("update-playbook")
@handle_api_error
def update_playbook_top_cmd(
    playbook_id: str = typer.Argument(...),
    title: Optional[str] = typer.Option(None, "--title"),
    body: Optional[str] = typer.Option(None, "--body"),
    macro: Optional[str] = typer.Option(None, "--macro"),
):
    """Update an existing playbook."""
    data: dict = {}
    if title is not None:
        data["title"] = title
    if body is not None:
        data["body"] = body
    if macro is not None:
        data["macro"] = macro
    if not data:
        console.print("[yellow]Nothing to update. Pass --title, --body, or --macro.[/yellow]")
        return
    playbooks.update_playbook(playbook_id, title=title, body=body, macro=macro)
    console.print(f"[green]Playbook {playbook_id} updated.[/green]")
    return None

@app.command("delete-playbook")
@handle_api_error
def delete_playbook_top_cmd(playbook_id: str = typer.Argument(...)):
    """Delete a playbook."""
    if typer.confirm(f"Delete playbook {playbook_id}?"):
        playbooks.delete_playbook(playbook_id)
        console.print(f"[green]Playbook {playbook_id} deleted.[/green]")
    return None

@app.command("list-secrets")
@handle_api_error
def list_secrets_top_cmd():
    """List all organization secrets."""
    resp = secrets.list_secrets()
    items = resp if isinstance(resp, list) else resp.get("secrets", resp.get("items", []))
    table = Table(title="Organization Secrets")
    table.add_column("ID", style="cyan")
    table.add_column("Name")
    for item in items:
        if isinstance(item, dict):
            table.add_row(item.get("id", ""), item.get("name", ""))
    console.print(table)

    return resp
@app.command("delete-secret")
@handle_api_error
def delete_secret_top_cmd(secret_id: str = typer.Argument(...)):
    """Delete an organization secret."""
    if typer.confirm(f"Delete secret {secret_id}?"):
        secrets.delete_secret(secret_id)
        console.print(f"[green]Secret {secret_id} deleted.[/green]")
    return None

@app.command("chain")
@handle_api_error
def chain_cmd(
    prompt: Optional[str] = typer.Argument(None, help="Initial prompt"),
    playbooks_arg: Optional[str] = typer.Option(None, "--playbooks", help="Comma-separated playbook IDs"),
    file: Optional[Path] = typer.Option(None, "--file", help="Workflow YAML file"),
):
    """(Beta) Orchestrate a sequential chain of playbooks.

    Method 1 \u2014 Inline:
        devin chain "Refactor utils.py" --playbooks "lint_check,unit_tests"

    Method 2 \u2014 YAML workflow file:
        devin chain --file workflow.yml
    """
    steps = []

    if file:
        if not file.exists():
            console.print(f"[bold red]Error:[/bold red] File not found: {file}")
            raise typer.Exit(1)
        try:
            workflow = yaml.safe_load(file.read_text())
            steps = workflow.get("steps", [])
        except Exception as e:
            console.print(f"[bold red]Error parsing YAML:[/bold red] {e}")
            raise typer.Exit(1)
    elif prompt and playbooks_arg:
        pb_list = [p.strip() for p in playbooks_arg.split(",")]
        for i, pb in enumerate(pb_list):
            step_prompt = prompt if i == 0 else f"Execute playbook: {pb}"
            steps.append({"prompt": step_prompt, "playbook": pb})
    else:
        console.print("[bold red]Error:[/bold red] Provide --file OR (prompt + --playbooks)")
        raise typer.Exit(1)

    current_sid = None
    for i, step in enumerate(steps):
        step_prompt = step.get("prompt", "")
        step_pb = step.get("playbook")
        console.print(f"[bold cyan]Step {i+1}/{len(steps)}:[/bold cyan] Playbook={step_pb}")

        if i == 0:
            with console.status("Starting session..."):
                resp = sessions.create_session(prompt=step_prompt, playbook_id=step_pb)
                current_sid = resp.get("session_id")
                if not current_sid:
                    console.print("[bold red]Error:[/bold red] No session ID returned from API.")
                    raise typer.Exit(1)
                config.current_session_id = current_sid
                console.print(f"[green]Session started:[/green] {current_sid}")
        else:
            sessions.send_message(current_sid, f"{step_prompt} (Playbook: {step_pb})")

        backoff = 2
        while True:
            resp = sessions.get_session(current_sid)
            status = resp.get("status_enum", "")
            if status in {"finished", "stopped", "error"}:
                console.print(f"Step {i+1} done (status: {status}).")
                break
            time.sleep(min(backoff, 10))
            backoff = min(backoff * 1.5, 10)

    console.print("[bold green]Chain completed![/bold green]")
    return resp

if __name__ == "__main__":
    app()
