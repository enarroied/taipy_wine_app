from pathlib import Path

import yaml


def read_yaml_list(file_path: str | Path) -> list:
    """
    Reads a YAML file using pathlib and returns a list.
    """
    path = Path(file_path)

    if not path.is_file():
        print(f"Error: The path '{path}' is not a valid file.")
        return []

    try:
        with path.open("r", encoding="utf-8") as yaml_file:
            data = yaml.safe_load(yaml_file)

        if data is None:
            return []

        if isinstance(data, list):
            return data

        print(f"Warning: Data in {path.name} was {type(data)}, wrapping in list.")
        return [data]

    except yaml.YAMLError as exc:
        print(f"Error: YAML syntax error in {path.name}: {exc}")
        return []
    except Exception as e:
        print(f"Unexpected error reading {path.name}: {e}")
        return []
