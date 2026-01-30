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
from devin_cli.api import sessions, knowledge, playbooks, secrets, attachments
from devin_cli.api.client import client, APIError
import functools
import sys

app = typer.Typer(help="Unofficial CLI for Devin AI", no_args_is_help=True)
console = Console()

ASCII_LOGO = r"""
[bold cyan]
    ____             _          _________    ____
   / __ \___ _   __(_)___     / ____/ /   /  _/
  / / / / _ \ | / / / __ \   / /   / /    / /  
 / /_/ /  __/ |/ / / / / /  / /___/ /____/ /   
/_____/\___/|___/_/_/ /_/   \____/_____/___/   
[/bold cyan]
"""

# Show logo on main help or empty args
if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] in ["--help", "-h"]):
    console.print(ASCII_LOGO)

@app.callback()
def main(ctx: typer.Context):
    """
    Unofficial CLI for Devin AI.
    """
    if ctx.invoked_subcommand is None and not any(arg in sys.argv for arg in ["--help", "-h"]):
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
    token: str = typer.Option(..., prompt="Devin API Token (starts with apk_user_ or apk_)", help="Your Devin API Token"),
    base_url: str = typer.Option("https://api.devin.ai/v1", prompt="Devin API Base URL", help="Devin API Base URL"),
):
    """
    Configure the CLI with your Devin API token.
    """
    if not (token.startswith("apk_user_") or token.startswith("apk_")):
        console.print("[bold red]Error:[/bold red] Invalid token format. Must start with 'apk_user_' or 'apk_'.")
        raise typer.Exit(1)
    
    config.api_token = token
    config.base_url = base_url
    console.print(f"[green]Token and Base URL saved to {config.config_file}[/green]")

@app.command()
@handle_api_error
def create_session(
    prompt: Optional[str] = typer.Argument(None, help="The prompt for the session"),
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="Read prompt from file"),
    title: Optional[str] = typer.Option(None, "--title", "-t", help="Custom session title"),
    idempotent: bool = typer.Option(False, "--idempotent", "-i", help="Idempotent creation"),
    secrets: List[str] = typer.Option(None, "--secret", "-s", help="Session secrets in KEY=VALUE format"),
    knowledge_ids: List[str] = typer.Option(None, "--knowledge-id", "-k", help="Knowledge IDs to include"),
    secret_ids: List[str] = typer.Option(None, "--secret-id", help="Stored secret IDs to include"),
    max_acu_limit: Optional[int] = typer.Option(None, "--max-acu", help="Maximum ACU limit"),
    unlisted: bool = typer.Option(False, help="Create unlisted session"),
):
    """
    Create a new Devin session.
    """
    if file:
        if not file.exists():
            console.print(f"[bold red]Error:[/bold red] File not found: {file}")
            raise typer.Exit(1)
        prompt_text = file.read_text()
    elif prompt:
        prompt_text = prompt
    else:
        console.print("[bold red]Error:[/bold red] Must provide prompt argument or --file option")
        raise typer.Exit(1)

    parsed_secrets = []
    if secrets:
        for s in secrets:
            if "=" not in s:
                console.print(f"[bold yellow]Warning:[/bold yellow] Invalid secret format '{s}', skipping. Use KEY=VALUE.")
                continue
            k, v = s.split("=", 1)
            parsed_secrets.append({"key": k, "value": v})

    with console.status("[bold green]Creating session...[/bold green]"):
        resp = sessions.create_session(
            prompt=prompt_text,
            idempotent=idempotent,
            unlisted=unlisted,
            session_secrets=parsed_secrets,
            title=title,
            knowledge_ids=knowledge_ids,
            secret_ids=secret_ids,
            max_acu_limit=max_acu_limit
        )
        session_id = resp["session_id"]
        config.current_session_id = session_id
        console.print(f"[green]Session created:[/green] {session_id} (url: {resp['url']})")

@app.command()
@handle_api_error
def list_sessions(
    limit: int = typer.Option(10, help="Number of sessions to list"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """
    List your Devin sessions.
    """
    resp = sessions.list_sessions(limit=limit)
    sess_list = resp.get("sessions", [])
    
    if json_output:
        console.print(json.dumps(sess_list, indent=2))
        return

    table = Table(title="Devin Sessions")
    table.add_column("ID", style="cyan")
    table.add_column("Status", style="magenta")
    table.add_column("Title")
    table.add_column("Created At", style="dim")

    for s in sess_list:
        table.add_row(
            s.get("session_id"),
            s.get("status_enum"),
            s.get("title") or s.get("prompt", "")[:50],
            s.get("created_at")
        )
    console.print(table)

@app.command()
@handle_api_error
def get_session(
    session_id: Optional[str] = typer.Argument(None, help="Session ID (defaults to current)"),
):
    """
    Get details for a session.
    """
    sid = session_id or get_current_session_id()
    resp = sessions.get_session(sid)
    console.print(Panel(
        f"[bold]Status:[/bold] {resp.get('status_enum')}\n"
        f"[bold]URL:[/bold] {resp.get('url')}\n"
        f"[bold]Created:[/bold] {resp.get('created_at')}",
        title=f"Session {sid}"
    ))
    
    # recursive structured output display could be complex, keeping it simple for now
    if "structured_output" in resp:
            console.print("[bold]Structured Output:[/bold]")
            console.print(json.dumps(resp["structured_output"], indent=2))

@app.command()
@handle_api_error
def message(
    text: Optional[str] = typer.Argument(None, help="Message text"),
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="Read message from file"),
    session_id: Optional[str] = typer.Option(None, "--session-id", help="Target session ID"),
):
    """
    Send a message to a session.
    """
    sid = session_id or get_current_session_id()
    if file:
        if not file.exists():
            console.print(f"[bold red]Error:[/bold red] File not found: {file}")
            raise typer.Exit(1)
        msg_text = file.read_text()
    elif text:
        msg_text = text
    else:
        console.print("[bold red]Error:[/bold red] Must provide message text or --file")
        raise typer.Exit(1)

    sessions.send_message(sid, msg_text)
    console.print(f"[green]Message sent to session {sid}[/green]")

@app.command()
@handle_api_error
def watch(
    session_id: Optional[str] = typer.Argument(None, help="Session ID (defaults to current)"),
):
    """
    Watch a session's progress live.
    """
    sid = session_id or get_current_session_id()
    console.print(f"Watching session {sid}. Press Ctrl+C to stop.")
    
    backoff = 1
    try:
        with Live(console=console, refresh_per_second=4) as live:
            while True:
                resp = sessions.get_session(sid)
                status = resp.get("status_enum")
                
                content = Text()
                content.append(f"Status: {status}\n", style="bold magenta")
                
                so = resp.get("structured_output")
                if so:
                    content.append(json.dumps(so, indent=2))
                else:
                    content.append("(No structured output yet)")
                
                live.update(Panel(content, title=f"Session {sid}"))

                if status in ["blocked", "finished"]:
                    console.print(f"[bold green]Session {status}![/bold green]")
                    break
                
                time.sleep(min(backoff, 30))
                backoff = min(backoff * 1.5, 30)
                
    except KeyboardInterrupt:
        console.print("\nStopped watching.")

@app.command()
@handle_api_error
def update_tags(
    session_id: Optional[str] = typer.Argument(None, help="Session ID (defaults to current)"),
    tags: List[str] = typer.Option(..., "--tag", "-t", help="Tags to set (overwrites existing)"),
):
    """Update tags for a session."""
    sid = session_id or get_current_session_id()
    resp = sessions.update_session_tags(sid, tags)
    console.print(f"[green]Tags updated for session {sid}.[/green]")

@app.command()
@handle_api_error
def terminate(
    session_id: Optional[str] = typer.Argument(None, help="Session ID (defaults to current)"),
):
    """
    Terminate a session.
    """
    sid = session_id or get_current_session_id()
    if typer.confirm(f"Are you sure you want to terminate session {sid}?"):
        sessions.terminate_session(sid)
        console.print(f"[green]Session {sid} terminated.[/green]")

# ... (rest of the file remains same, adding update-knowledge/playbook below create commands)


@app.command()
@handle_api_error
def upload(
    file: Path = typer.Argument(..., help="File to upload"),
):
    """
    Upload a file to Devin (returns attachment URL).
    """
    resp = attachments.upload_file(str(file))
    # API returns raw string URL in response body, sometimes quoted?
    # Let's clean it up if it's JSON string
    url = resp
    if isinstance(resp, str):
        url = resp.strip('"')
        
    console.print(f"[green]File uploaded:[/green] {url}")
    return url

@app.command()
@handle_api_error
def attach(
    file: Path = typer.Argument(..., help="File to attach"),
    prompt: str = typer.Argument(..., help="Prompt for the session"),
):
    """
    Upload a file and create a session with it attached.
    """
    # Use api modules directly to avoid typer recursion issues
    resp = attachments.upload_file(str(file))
    url = resp if isinstance(resp, str) else str(resp)
    url = url.strip('"')
    
    full_prompt = f"{prompt}\n\nATTACHMENT: \"{url}\""
    
    with console.status("[bold green]Creating session with attachment...[/bold green]"):
        resp = sessions.create_session(prompt=full_prompt)
        session_id = resp["session_id"]
        config.current_session_id = session_id
        console.print(f"[green]Session created:[/green] {session_id} (url: {resp['url']})")

@app.command()
def use_session(session_id: str):
    """
    Switch the current active session.
    """
    config.current_session_id = session_id
    console.print(f"[green]Switched to session {session_id}[/green]")

@app.command()
@handle_api_error
def open():
    """
    Open the current session in your browser.
    """
    sid = get_current_session_id()
    resp = sessions.get_session(sid)
    url = resp.get("url")
    if url:
        webbrowser.open(url)
        console.print(f"Opening {url}...")
    else:
        console.print("[yellow]No URL found for this session.[/yellow]")

@app.command()
@handle_api_error
def status():
    """
    Get the status of the current session.
    """
    sid = get_current_session_id()
    resp = sessions.get_session(sid)
    console.print(f"Session {sid}: [bold {GetStatusColor(resp.get('status_enum'))}]{resp.get('status_enum')}[/]")

def GetStatusColor(status):
    if status == 'working': return 'green'
    if status == 'blocked': return 'red'
    if status == 'finished': return 'blue'
    return 'white'

@app.command()
def history():
    """
    Show locally known recent sessions (placeholder).
    """
    sid = config.current_session_id
    if sid:
        console.print(f"Current local session: {sid}")
    else:
        console.print("No current local session.")

@app.command()
@handle_api_error
def messages(
    session_id: Optional[str] = typer.Argument(None, help="Session ID"),
):
    """
    Show conversation history for a session.
    """
    sid = session_id or get_current_session_id()
    resp = sessions.get_session(sid)
    msgs = resp.get("messages", [])
    console.print(f"[bold]Conversation for Session {sid}[/bold]")
    console.print("─────────────────────────")
    for m in msgs:
            console.print(m)


# Knowledge Commands
@app.command()
@handle_api_error
def list_knowledge():
    """List all knowledge entries."""
    resp = knowledge.list_knowledge()
    items = resp.get("knowledge", [])
    table = Table(title="Knowledge Base")
    table.add_column("ID", style="cyan")
    table.add_column("Name")
    table.add_column("Created At", style="dim")
    for item in items:
        table.add_row(item.get("id"), item.get("name"), item.get("created_at"))
    console.print(table)

@app.command()
@handle_api_error
def create_knowledge(
    name: str = typer.Argument(..., help="Name of the knowledge entry"),
    body: str = typer.Argument(..., help="Content/Body of the knowledge"),
    trigger_description: str = typer.Argument(..., help="Description of when this knowledge should be used"),
):
    """Create a new knowledge entry."""
    resp = knowledge.create_knowledge(name, body, trigger_description)
    console.print(f"[green]Knowledge created:[/green] {resp.get('id') or resp}")

@app.command()
@handle_api_error
def update_knowledge(
    knowledge_id: str = typer.Argument(..., help="ID of the knowledge to update"),
    name: Optional[str] = typer.Option(None, help="New name"),
    body: Optional[str] = typer.Option(None, help="New content/body"),
    trigger: Optional[str] = typer.Option(None, "--trigger", help="New trigger description"),
):
    """Update an existing knowledge entry."""
    resp = knowledge.update_knowledge(knowledge_id, name=name, body=body, trigger_description=trigger)
    console.print(f"[green]Knowledge {knowledge_id} updated.[/green]")

@app.command()
@handle_api_error
def delete_knowledge(knowledge_id: str):
    """Delete a knowledge entry."""
    if typer.confirm(f"Are you sure you want to delete knowledge {knowledge_id}?"):
        knowledge.delete_knowledge(knowledge_id)
        console.print(f"[green]Knowledge {knowledge_id} deleted.[/green]")

# Playbook Commands
@app.command()
@handle_api_error
def list_playbooks():
    """List all playbooks."""
    resp = playbooks.list_playbooks()
    if isinstance(resp, list):
        table = Table(title="Playbooks")
        table.add_column("ID", style="cyan")
        table.add_column("Title")
        table.add_column("Macro")
        for item in resp:
             table.add_row(item.get("playbook_id"), item.get("title"), item.get("macro") or "-")
        console.print(table)
    else:
        console.print(json.dumps(resp, indent=2))

@app.command()
@handle_api_error
def create_playbook(
    title: str = typer.Argument(..., help="Title of the playbook"),
    body: str = typer.Argument(..., help="Instructions/Body of the playbook"),
    macro: Optional[str] = typer.Option(None, help="Associated macro name"),
):
    """Create a new team playbook."""
    resp = playbooks.create_playbook(title, body, macro)
    console.print(f"[green]Playbook created:[/green] {resp.get('playbook_id') or resp}")

@app.command()
@handle_api_error
def update_playbook(
    playbook_id: str = typer.Argument(..., help="ID of the playbook to update"),
    title: Optional[str] = typer.Option(None, help="New title"),
    body: Optional[str] = typer.Option(None, help="New instructions"),
    macro: Optional[str] = typer.Option(None, help="New macro name"),
):
    """Update an existing team playbook."""
    resp = playbooks.update_playbook(playbook_id, title=title, body=body, macro=macro)
    console.print(f"[green]Playbook {playbook_id} updated.[/green]")

@app.command()
@handle_api_error
def delete_playbook(playbook_id: str):
    """Delete a team playbook."""
    if typer.confirm(f"Are you sure you want to delete playbook {playbook_id}?"):
        playbooks.delete_playbook(playbook_id)
        console.print(f"[green]Playbook {playbook_id} deleted.[/green]")

# Secret Commands
@app.command()
@handle_api_error
def list_secrets():
    """List all organization secrets."""
    resp = secrets.list_secrets()
    if isinstance(resp, list):
         table = Table(title="Organization Secrets")
         table.add_column("ID", style="cyan")
         table.add_column("Name")
         for item in resp:
              table.add_row(item.get("id"), item.get("name"))
         console.print(table)
    else:
        console.print(json.dumps(resp, indent=2))

@app.command()
@handle_api_error
def delete_secret(secret_id: str):
    """Delete an organization secret."""
    if typer.confirm(f"Are you sure you want to delete secret {secret_id}?"):
        secrets.delete_secret(secret_id)
        console.print(f"[green]Secret {secret_id} deleted.[/green]")

# Chain Command
@app.command()
@handle_api_error
def chain(
    prompt: Optional[str] = typer.Argument(None, help="Initial prompt"),
    playbooks_arg: Optional[str] = typer.Option(None, "--playbooks", help="Comma-separated playbook IDs"),
    file: Optional[Path] = typer.Option(None, "--file", help="Workflow YAML file"),
):
    """
    (Beta) Run a chain of playbooks.
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
        k_list = [p.strip() for p in playbooks_arg.split(",")]
        # For inline chain, we assume same prompt? Or maybe prompt is just for first?
        # The prompt is used to start the session.
        # Then we apply playbooks? 
        # Wait, create_session takes ONE playbook_id.
        # So chain probably means:
        # 1. Create session with prompt + playbook[0]
        # 2. Wait for finish
        # 3. Message session "Proceed with playbook <playbook[1]>"? 
        # Or maybe we can't "apply" a playbook mid-session via API easily unless we use message instructions.
        # "Use playbook X" might be a natural language instruction Devin understands if it has access to playbooks.
        # Let's assume we pass prompt for step 1, then for subsequent steps we pass "Execute playbook X".
        
        for i, pb in enumerate(k_list):
            step_prompt = prompt if i == 0 else f"Execute playbook: {pb}"
            steps.append({"prompt": step_prompt, "playbook": pb})
    else:
        console.print("[bold red]Error:[/bold red] Must provide --file OR (prompt and --playbooks)")
        raise typer.Exit(1)

    # Execute Chain
    current_sid = None
    
    for i, step in enumerate(steps):
        step_prompt = step.get("prompt", "")
        step_pb = step.get("playbook")
        
        console.print(f"[bold cyan]Step {i+1}/{len(steps)}:[/bold cyan] Playbook={step_pb}")
        
        if i == 0:
            # Create session
            with console.status(f"Starting session with playbook {step_pb}..."):
                resp = sessions.create_session(prompt=step_prompt, playbook_id=step_pb)
                current_sid = resp["session_id"]
                config.current_session_id = current_sid
                console.print(f"[green]Session started:[/green] {current_sid}")
        else:
            # Send message
             # Note: API does not have "switch playbook" endpoint. 
             # We just send a message. Hope Devin understands "Use playbook X".
             # Actually, if we want to change playbook strictly, maybe we can't?
             # But the user asked for "chaining".
             # Let's assume sending a message is the way.
             console.print(f"Sending instruction for next step...")
             sessions.send_message(current_sid, f"{step_prompt} (Playbook: {step_pb})")

        # Watch
        console.print(f"Watching step {i+1}...")
        backoff = 1
        while True:
            resp = sessions.get_session(current_sid)
            status = resp.get("status_enum")
            if status in ["blocked", "finished"]:
                console.print(f"Step {i+1} finished (status: {status}).")
                break
            time.sleep(min(backoff, 10))
            backoff *= 1.5

    console.print("[bold green]Chain completed![/bold green]")

if __name__ == "__main__":
    app()
