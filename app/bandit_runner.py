import subprocess  # nosec B404
import sys


def main():
    sys.exit(subprocess.call(["bandit", "-r", "app/", "database/"]))  # nosec B603 B607  # noqa: S607
