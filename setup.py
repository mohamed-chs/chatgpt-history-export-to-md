"""Module to setup the virtual environment and install requirements."""

import os
import sys
import venv
from pathlib import Path

BASE_DIR: Path = Path(__file__).parent.resolve()
VENV_DIR: Path = BASE_DIR / ".venv"


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
    print("Creating virtual environment...\n")
    create_virtual_environment()
    print("Installing requirements... (This may take a minute..)\n")
    pip_install_requirements()

    print(
        "\nSetup completed successfully!\n"
        "\nTo activate the virtual environment, "
        "use the following command based on your platform:\n",
    )
    if sys.platform == "win32":
        print(
            "\nFor Command Prompt:\n\t.venv\\Scripts\\activate.bat\n"
            "\nFor PowerShell:\n\t.venv\\Scripts\\Activate.ps1\n",
        )
    else:
        print("\n\tsource .venv/bin/activate\n")
