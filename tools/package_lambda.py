from pathlib import Path
import shutil
import subprocess
import sys
import zipfile


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "lambda"
BUILD = ROOT / "build" / "lambda"
OUTPUT = ROOT / "lambda.zip"


def main():
    if BUILD.exists():
        shutil.rmtree(BUILD)
    BUILD.mkdir(parents=True)

    requirements = SOURCE / "requirements.txt"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "--no-cache-dir",
            "--upgrade",
            "--only-binary=:all:",
            "--platform",
            "manylinux2014_x86_64",
            "--implementation",
            "cp",
            "--python-version",
            "3.12",
            "--target",
            str(BUILD),
            "-r",
            str(requirements),
        ],
        check=True,
    )
    shutil.copy2(SOURCE / "handler.py", BUILD / "handler.py")

    with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in BUILD.rglob("*"):
            if path.is_file():
                archive.write(path, path.relative_to(BUILD))

    print(f"Created {OUTPUT}")


if __name__ == "__main__":
    main()
