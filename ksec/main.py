"""
Provide a tool for showing decoded kubernetes secrets printed by kubectl.
"""

import base64
import json
import sys
from types import ModuleType
from typing import Annotated

import typer
from auto_name_enum import AutoNameEnum, auto
from rich import print
from rich.console import Console
from thefuzz import process

yaml: ModuleType | None
try:
    import yaml
except ImportError:
    yaml = None


app = typer.Typer(rich_markup_mode="rich")


class Mode(AutoNameEnum):
    JSON = auto()
    YAML = auto()


def boom(message: str):
    print(
        f"[bold yellow]{message}[/bold yellow]. [bold red]Aborting...[/bold red]", file=sys.stderr
    )
    sys.exit(1)


def ghost(message):
    console = Console()
    with console.screen():
        console.print(f"{message}\n\n(Press <ctrl-c> to exit)")
        try:
            while True:
                from time import sleep

                sleep(0.1)
        except KeyboardInterrupt:
            pass


@app.command()
def pretty(
    mode: Annotated[
        Mode,
        typer.Option(
            "--mode",
            "-m",
            case_sensitive=False,
            help="""
            Set the format that should be processed from stdin.
            [yellow]YAML mode requires installation with the yaml flag.[/yellow]
            """,
        ),
    ] = Mode.JSON,
    full: Annotated[
        bool,
        typer.Option(
            "--full",
            "-f",
            help="Include all the metadata for the secrets, not just the data",
        ),
    ] = False,
    ephemeral: Annotated[
        bool,
        typer.Option(
            "--ephemeral",
            "-e",
            help="Show the output in a temporary buffer that will be cleared upon exit.",
        ),
    ] = False,
    search: Annotated[
        str | None,
        typer.Argument(
            help="Match a named secret data item using fuzzy search",
        ),
    ] = None,
):
    """
    Display decoded kubernetes secrets printed by kubectl.

    Example usage:

        kubectl get secret my-secret -o json | ksec
    """

    text = sys.stdin.read()
    payload: dict = {}
    match mode:
        case Mode.JSON:
            payload = json.loads(text)
        case Mode.YAML:
            if not yaml:
                boom("Not installed with the `yaml` option")

            # Make mypy happy
            assert yaml is not None

            payload = yaml.safe_load(text)
        case _:
            boom(f"Unmatched mode {mode}. This should not be possible!")

    data = {k: base64.b64decode(v).decode("utf-8") for (k, v) in payload["data"].items()}
    target = data

    if full and search:
        boom("You cannont specify --full with a search term")
    elif full:
        payload["data"] = data
        target = payload
    elif search:
        (hit, _) = process.extractOne(search, data.keys())
        target = {hit: data[hit]}

    printer = print if not ephemeral else ghost
    match mode:
        case Mode.JSON:
            printer(json.dumps(target, indent=2))
        case Mode.YAML:
            if not yaml:
                boom("Not installed with the `yaml` option")
                sys.exit(1)
            printer(yaml.dump(target))
