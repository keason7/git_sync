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
