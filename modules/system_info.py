import platform, getpass, sys

def system_info() -> str:
    """Return computer name, current user, and Python version."""
    return f"{platform.node()}, {getpass.getuser()}, Python {sys.version.split()[0]}"
