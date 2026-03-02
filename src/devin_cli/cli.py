import typer
import time
import json
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
import functools
import sys

app = typer.Typer(
    help="Unofficial CLI for Devin AI v3",
    no_args_is_help=True,
    rich_markup_mode="rich"
)
console = Console()

# --- Sub-Apps for Organization API ---
session_app = typer.Typer(help="Manage Devin sessions", no_args_is_help=True)
knowledge_app = typer.Typer(help="Manage knowledge notes", no_args_is_help=True)
playbook_app = typer.Typer(help="Manage team playbooks", no_args_is_help=True)
secret_app = typer.Typer(help="Manage organization secrets", no_args_is_help=True)
schedule_app = typer.Typer(help="Manage session schedules", no_args_is_help=True)
attachment_app = typer.Typer(help="Manage session attachments", no_args_is_help=True)
repo_app = typer.Typer(help="Manage organization repositories", no_args_is_help=True)
enterprise_app = typer.Typer(help="Enterprise-scoped operations", no_args_is_help=True)

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

@app.callback()
def main(ctx: typer.Context):
    """
    Unofficial CLI for Devin AI v3.
    """
    if ctx.invoked_subcommand is None:
        console.print(ASCII_LOGO)

def handle_api_error(func):
    """Decorator to handle API errors gracefully."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except APIError as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            if e.status_code == 401:
                console.print("Tip: Check your API token with 'devin configure'.")
            raise typer.Exit(1)
        except Exception as e:
            console.print(f"[bold red]Unexpected Error:[/bold red] {e}")
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
):
    """
    Configure the CLI with your Devin API token and organization.
    """
    # Validation based on v3 requirements
    if not (token.startswith("apk_") or token.startswith("cog_")):
        console.print("[bold yellow]Warning:[/bold yellow] Token format might be outdated. v3 tokens usually start with 'apk_' or 'cog_'.")
    
    config.api_token = token
    config.base_url = base_url
    if org_id:
        config.org_id = org_id
    console.print(f"[green]Configuration saved to {config.config_file}[/green]")

# --- Sessions ---
@session_app.command("create")
@handle_api_error
def create_session_cmd(
    prompt: Optional[str] = typer.Argument(None, help="The prompt for the session"),
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="Read prompt from file"),
    title: Optional[str] = typer.Option(None, "--title", "-t", help="Custom session title"),
    org: Optional[str] = typer.Option(None, "--org", help="Override organization ID"),
    max_acu: Optional[int] = typer.Option(None, "--max-acu", help="Maximum ACU limit"),
):
    """Create a new Devin session."""
    if org: config.temporary_org_id = org
    if file:
        prompt_text = file.read_text()
    elif prompt:
        prompt_text = prompt
    else:
        console.print("[bold red]Error:[/bold red] Must provide prompt or --file")
        raise typer.Exit(1)

    with console.status("[bold green]Creating session...[/bold green]"):
        resp = sessions.create_session(prompt=prompt_text, title=title, max_acu_limit=max_acu)
        sid = resp["session_id"]
        config.current_session_id = sid
        console.print(f"[green]Session created:[/green] {sid}")
        console.print(f"[bold cyan]URL:[/bold cyan] {resp.get('url')}")

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
    sess_list = resp.get("sessions", [])
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
    console.print(Panel(json.dumps(resp, indent=2), title=f"Insights for {sid}"))

@session_app.command("cost")
@handle_api_error
def session_cost_cmd(
    session_id: Optional[str] = typer.Option(None, "--id"),
    org: Optional[str] = typer.Option(None, "--org"),
):
    """View ACU consumption."""
    if org: config.temporary_org_id = org
    if session_id:
        resp = consumption.get_session_consumption(session_id)
    else:
        resp = consumption.get_daily_consumption_breakdown()
    console.print(Panel(json.dumps(resp, indent=2), title="Consumption Data"))

@session_app.command("message")
@handle_api_error
def send_message_cmd(
    text: str = typer.Argument(...),
    session_id: Optional[str] = typer.Option(None, "--id"),
    org: Optional[str] = typer.Option(None, "--org"),
):
    """Send a message to a session."""
    if org: config.temporary_org_id = org
    sid = session_id or get_current_session_id()
    sessions.send_message(sid, text)
    console.print(f"[green]Message sent to {sid}[/green]")

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
        content = m.get("content", "")
        console.print(f"[bold cyan]{role}:[/bold cyan] {content}")
        console.print("---")

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

# --- Knowledge ---
@knowledge_app.command("list")
@handle_api_error
def list_knowledge_cmd(org: Optional[str] = typer.Option(None, "--org")):
    """List knowledge notes."""
    if org: config.temporary_org_id = org
    resp = knowledge.list_knowledge()
    items = resp.get("knowledge", [])
    table = Table(title="Knowledge Base")
    table.add_column("ID", style="cyan")
    table.add_column("Name")
    for item in items:
        table.add_row(item.get("id"), item.get("name"))
    console.print(table)

@knowledge_app.command("create")
@handle_api_error
def create_knowledge_cmd(
    title: str, 
    body: str, 
    org: Optional[str] = typer.Option(None, "--org"),
):
    """Create a knowledge note."""
    if org: config.temporary_org_id = org
    resp = knowledge.create_knowledge(title, body)
    console.print(f"[green]Created note:[/green] {resp.get('id')}")

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

# --- Playbooks ---
@playbook_app.command("list")
@handle_api_error
def list_playbooks_cmd(org: Optional[str] = typer.Option(None, "--org")):
    """List team playbooks."""
    if org: config.temporary_org_id = org
    resp = playbooks.list_playbooks()
    table = Table(title="Playbooks")
    table.add_column("ID", style="cyan")
    table.add_column("Title")
    for item in resp:
        table.add_row(item.get("playbook_id"), item.get("title"))
    console.print(table)

@playbook_app.command("create")
@handle_api_error
def create_playbook_cmd(
    title: str, 
    body: str, 
    macro: Optional[str] = None,
    org: Optional[str] = typer.Option(None, "--org"),
):
    """Create a new team playbook."""
    if org: config.temporary_org_id = org
    resp = playbooks.create_playbook(title, body, macro)
    console.print(f"[green]Playbook created:[/green] {resp.get('playbook_id')}")

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

# --- Secrets ---
@secret_app.command("list")
@handle_api_error
def list_secrets_cmd(org: Optional[str] = typer.Option(None, "--org")):
    """List organization secrets."""
    if org: config.temporary_org_id = org
    resp = secrets.list_secrets()
    table = Table(title="Secrets")
    table.add_column("ID", style="cyan")
    table.add_column("Name")
    for item in resp:
        table.add_row(item.get("id"), item.get("name"))
    console.print(table)

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

# --- Schedules ---
@schedule_app.command("list")
@handle_api_error
def list_schedules_cmd(org: Optional[str] = typer.Option(None, "--org")):
    """List recurring schedules."""
    if org: config.temporary_org_id = org
    resp = schedules.list_schedules()
    items = resp.get("items", [])
    table = Table(title="Schedules")
    table.add_column("ID", style="cyan")
    table.add_column("Title")
    table.add_column("Cron")
    for item in items:
        table.add_row(item.get("id"), item.get("title"), item.get("cron"))
    console.print(table)

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

# --- Repositories ---
@repo_app.command("list")
@handle_api_error
def list_repos_cmd(org: Optional[str] = typer.Option(None, "--org")):
    """List repositories indexed for Devin."""
    if org: config.temporary_org_id = org
    resp = repositories.list_repositories()
    items = resp.get("items", [])
    table = Table(title="Repositories")
    table.add_column("Path", style="cyan")
    table.add_column("Indexed", style="green")
    for item in items:
        table.add_row(item.get("repository_path"), "Yes" if item.get("is_indexed") else "No")
    console.print(table)

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

# --- Enterprise Discovery ---
@enterprise_app.command("whoami")
@handle_api_error
def whoami_cmd():
    """Show current identity details."""
    resp = members.get_self()
    console.print(Panel(json.dumps(resp, indent=2), title="Who Am I"))

@enterprise_app.command("list-orgs")
@handle_api_error
def list_orgs_cmd():
    """List all accessible organizations."""
    resp = organizations.list_organizations()
    console.print(Panel(json.dumps(resp, indent=2), title="Organizations"))

# --- Global Commands ---
@app.command("use")
def use_session_cmd(session_id: str):
    """Switch the current active session."""
    config.current_session_id = session_id
    console.print(f"[green]Switched to session {session_id}[/green]")

if __name__ == "__main__":
    app()
