import os
import sys
import venv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
VENV_DIR = os.path.join(BASE_DIR, ".venv")


def create_virtual_environment():
    # Create virtual environment
    env_builder = venv.EnvBuilder(with_pip=True)
    env_builder.create(VENV_DIR)


def pip_install_requirements():
    pip_exe = (
        os.path.join(VENV_DIR, "bin", "pip")
        if sys.platform != "win32"
        else os.path.join(VENV_DIR, "Scripts", "pip.exe")
    )

    # Install requirements
    os.system(f"{pip_exe} install -r requirements.txt")


if __name__ == "__main__":
    print("Creating virtual environment...\n")
    create_virtual_environment()
    print("Installing requirements... (This may take a minute..)\n")
    pip_install_requirements()

    # Post-setup instructions
    print("\nSetup completed successfully!")
    print(
        "\nTo activate the virtual environment, use the following command based on your platform:"
    )
    if sys.platform == "win32":
        print("\nFor Command Prompt:\n.venv\\Scripts\\activate.bat")
        print("\nFor PowerShell:\n.venv\\Scripts\\Activate.ps1")
    else:
        print("\nsource .venv/bin/activate")
