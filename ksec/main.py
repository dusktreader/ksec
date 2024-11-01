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
        f"[bold yellow]{message}[/bold yellow]. [bold red]Aborting...[/bold red]",
        file=sys.stderr
    )
    sys.exit(1)


@app.command()
def pretty(
    mode: Annotated[Mode, typer.Option(
        "--mode",
        "-m",
        case_sensitive=False,
        help="""
            Set the format that should be processed from stdin.
            [yellow]YAML mode requires installation with the yaml flag.[/yellow]
            """,
    )] = Mode.JSON,
    full: Annotated[bool, typer.Option(
        "--full",
        "-f",
    )]= False,
):
    """
    Display decoded kubernetes secrets printed by kubectl.

    Example usage:

        kubectl get secret my-secret -o json | ksec
    """

    text = sys.stdin.read()
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
            raise RuntimeError("This should not be possible")

    data = {k: base64.b64decode(v).decode("utf-8") for (k, v) in payload["data"].items()}
    target = data
    if full:
        payload["data"] = data
        target = payload
    match mode:
        case Mode.JSON:
            print(json.dumps(target, indent=2))
        case Mode.YAML:
            if not yaml:
                boom("Not installed with the `yaml` option")
                sys.exit(1)
            print(yaml.dump(target))
