"""Utils functions modules."""

import platform
from hashlib import sha256

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


def get_hashed_machine_id():
    """Get current hashed machine id.

    Raises:
        NameError: Unknown OS.

    Returns:
        str: Hashed id.
    """
    os = platform.system()

    if os == "Linux":
        with open("/etc/machine-id", "r", encoding="utf-8") as f:
            machine_id = f.read().strip()

        return sha256(str(machine_id).encode()).hexdigest()
    else:
        raise NameError(f"Unknown OS: {os}")
