import base64
import json
import sys

import typer
from auto_name_enum import AutoNameEnum, auto

try:
    import yaml
except ImportError:
    yaml = None

app = typer.Typer()

class Mode(AutoNameEnum):
    JSON = auto()
    YAML = auto()


#@app.callback(invoke_without_command=True)
@app.command()
def pretty(
    input_mode: Mode = Mode.JSON,
    output_mode: Mode = Mode.JSON,
):
    text = sys.stdin.read()
    match input_mode:
        case Mode.JSON:
            payload = json.loads(text)
        case Mode.YAML:
            if not yaml:
                print("Not installed with the `yaml` option. Aborting...", file=sys.stderr)
                sys.exit(1)
            payload = yaml.safe_load(text)
        case _:
            raise RuntimeError("This should not be possible")

    data = {k: base64.b64decode(v).decode("utf-8") for (k, v) in payload["data"].items()}
    match output_mode:
        case Mode.JSON:
            print(json.dumps(data, indent=2))
        case Mode.YAML:
            if not yaml:
                print("Not installed with the `yaml` option. Aborting...", file=sys.stderr)
                sys.exit(1)
            print(yaml.dump(data))
