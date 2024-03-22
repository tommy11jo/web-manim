import os
import platform
import subprocess as sp
from pathlib import Path


def open_file(file_path, in_browser=False):
    current_os = platform.system()
    if current_os == "Windows":
        os.startfile(file_path if not in_browser else file_path.parent)
    else:
        if current_os == "Linux":
            commands = ["xdg-open"]
            file_path = file_path if not in_browser else file_path.parent
        elif current_os.startswith("CYGWIN"):
            commands = ["cygstart"]
            file_path = file_path if not in_browser else file_path.parent
        elif current_os == "Darwin":
            commands = ["open"] if not in_browser else ["open", "-R"]
        else:
            raise OSError("Unable to identify your operating system...")
        commands.append(file_path)
        sp.Popen(commands)


def add_extension_if_not_present(file_name: Path, extension: str) -> Path:
    if file_name.suffix != extension:
        return file_name.with_suffix(file_name.suffix + extension)
    else:
        return file_name


def guarantee_existence(path: Path) -> Path:
    if not path.exists():
        path.mkdir(parents=True)
    return path.resolve(strict=True)
