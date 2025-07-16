"""Utils functions modules."""

import yaml


def read_yml(path):
    """Read YAML file.

    Args:
        path (str): Input path.

    Returns:
        dict: YAML dictionary.
    """
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def write_yml(path, data):
    """
    Write YAML file.

    Args:
        path (str): Path of output file.
        data (dict): Dictionary to write as YAML.
    """
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f)
