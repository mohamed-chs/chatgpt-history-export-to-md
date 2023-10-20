"""Module to setup the virtual environment and install requirements."""

import os
import sys
import venv
from pathlib import Path

BASE_DIR: Path = Path(__file__).parent.resolve()
VENV_DIR = BASE_DIR / ".venv"


def create_virtual_environment() -> None:
    """Create a virtual environment in the project directory."""
    env_builder = venv.EnvBuilder(with_pip=True)
    env_builder.create(env_dir=VENV_DIR)


def pip_install_requirements() -> None:
    """Install requirements from requirements.txt."""
    pip_exe: Path = (
        VENV_DIR / "bin" / "pip"
        if sys.platform != "win32"
        else VENV_DIR / "Scripts" / "pip.exe"
    )

    # Install requirements
    os.system(command=f"{pip_exe} install -r requirements.txt")


if __name__ == "__main__":
    if sys.version_info < (3, 10):
        print(
            "Python 3.10 or higher is required to run this program.\n"
            "Please download the latest version of Python at :\n"
            "https://www.python.org/downloads/ 🔗, and try again.\n"
            "Exiting...",
        )
        sys.exit(1)

    print("Creating virtual environment...\n")
    create_virtual_environment()
    print("Installing requirements... (This may take a minute..)\n")
    pip_install_requirements()

    print(
        "\nSetup completed successfully!\n"
        "\nTo activate the virtual environment, "
        "use the following command based on your platform:",
    )
    if sys.platform == "win32":
        print(
            "\nFor Command Prompt:\n.venv\\Scripts\\activate.bat\n"
            "\nFor PowerShell:\n.venv\\Scripts\\Activate.ps1\n",
        )
    else:
        print("\nsource .venv/bin/activate\n")
