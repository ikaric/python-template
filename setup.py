#!/usr/bin/env python3
"""Project setup script - run once after cloning, then self-destructs.

This script:
1. Prompts for project name, description, author
2. Asks for project type: service (FastAPI) or library (pip package)
3. Renames folders and updates all file contents
4. Copies config examples to real files
5. Optionally strips API/Docker for library mode
6. Generates a fresh README
7. Self-destructs
"""

from __future__ import annotations

import os
import re
import shutil
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

# === Constants ===
ROOT = Path(__file__).parent.resolve()
TEMPLATE_SNAKE = "python_template"
TEMPLATE_KEBAB = "python-template"
TEMPLATE_UPPER = "PYTHON_TEMPLATE"

# Files to skip during string replacement (binary, lock files, etc.)
SKIP_PATTERNS = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "*.pyc",
    "*.pyo",
    "*.egg-info",
    "uv.lock",
    ".vscode",  # Will be created from .vscode.example
    ".env",  # Will be created from env.example
}

# Reserved names that cannot be used as project names
RESERVED_NAMES = {
    "test",
    "tests",
    "setup",
    "api",
    "src",
    "build",
    "dist",
    "config",
    "settings",
    "main",
    "app",
    "python",
    "pip",
    "uv",
}


# === Utility Functions ===
def print_header(text: str) -> None:
    """Print a styled header."""
    print(f"\n{'─' * 50}")
    print(f"  {text}")
    print(f"{'─' * 50}\n")


def print_step(text: str) -> None:
    """Print a step with checkmark."""
    print(f"  ✓ {text}")


def print_error(text: str) -> None:
    """Print an error message."""
    print(f"  ✗ Error: {text}", file=sys.stderr)


# === Validation ===
def validate_name(name: str) -> tuple[bool, str]:
    """Validate project name.

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name:
        return False, "Name cannot be empty"

    if not re.match(r"^[a-z][a-z0-9_]*$", name):
        return False, "Name must start with lowercase letter and contain only lowercase letters, numbers, and underscores"

    if name in RESERVED_NAMES:
        return False, f"'{name}' is a reserved name"

    if len(name) > 50:
        return False, "Name is too long (max 50 characters)"

    return True, ""


# === User Input ===
def prompt_user() -> dict[str, Any]:
    """Gather project configuration from user."""
    print_header("Python Template Setup")

    # Project name
    while True:
        name = input("Project name (lowercase, underscores ok): ").strip()
        is_valid, error = validate_name(name)
        if is_valid:
            break
        print_error(error)

    # Description
    description = input("Description [A Python project]: ").strip()
    if not description:
        description = "A Python project"

    # Author
    author = input("Author (Name <email>) []: ").strip()

    # Project type
    print("\nProject type:")
    print("  [1] service  - FastAPI web service with Docker")
    print("  [2] library  - Pip-installable package (no API/Docker)")

    while True:
        choice = input("\nChoice [1]: ").strip()
        if choice in ("", "1"):
            mode = "service"
            break
        elif choice == "2":
            mode = "library"
            break
        else:
            print_error("Please enter 1 or 2")

    return {
        "name": name,
        "description": description,
        "author": author,
        "mode": mode,
    }


# === File Discovery ===
def should_skip(path: Path) -> bool:
    """Check if a path should be skipped during processing."""
    path_str = str(path)
    for pattern in SKIP_PATTERNS:
        if pattern.startswith("*"):
            # Glob pattern
            if path.match(pattern):
                return True
        else:
            # Directory/file name
            if pattern in path_str.split(os.sep):
                return True
    return False


def get_all_files() -> list[Path]:
    """Get all files that need string replacement."""
    files = []
    for path in ROOT.rglob("*"):
        if path.is_file() and not should_skip(path):
            # Skip binary files
            try:
                path.read_text(encoding="utf-8")
                files.append(path)
            except (UnicodeDecodeError, PermissionError):
                pass
    return files


# === String Replacement ===
def rename_in_file(path: Path, replacements: dict[str, str]) -> bool:
    """Replace all patterns in a single file.

    Returns:
        True if file was modified, False otherwise
    """
    try:
        content = path.read_text(encoding="utf-8")
        original = content

        for old, new in replacements.items():
            content = content.replace(old, new)

        if content != original:
            path.write_text(content, encoding="utf-8")
            return True
        return False
    except (UnicodeDecodeError, PermissionError):
        return False


# === Folder Operations ===
def rename_folder(old: Path, new: Path) -> None:
    """Rename a folder.

    If the destination already exists (from a previous interrupted run),
    remove it first to ensure clean rename.
    """
    if new.exists():
        shutil.rmtree(str(new))
    if old.exists():
        shutil.move(str(old), str(new))


# === Copy Operations ===
def copy_examples() -> None:
    """Copy .vscode.example -> .vscode, env.example -> .env"""
    # Copy .vscode.example -> .vscode
    vscode_example = ROOT / ".vscode.example"
    vscode_target = ROOT / ".vscode"
    if vscode_example.exists() and not vscode_target.exists():
        shutil.copytree(str(vscode_example), str(vscode_target))

    # Copy env.example -> .env
    env_example = ROOT / "env.example"
    env_target = ROOT / ".env"
    if env_example.exists() and not env_target.exists():
        shutil.copy2(str(env_example), str(env_target))


# === Delete Operations ===
def delete_paths(paths: list[Path]) -> None:
    """Delete files and folders."""
    for path in paths:
        if path.exists():
            if path.is_dir():
                shutil.rmtree(str(path))
            else:
                path.unlink()


# === Library Mode Stripping ===
def strip_for_library(snake_name: str) -> None:
    """Remove API/Docker components for library mode."""
    # Files and folders to delete
    paths_to_delete = [
        # API layer
        ROOT / "src" / snake_name / "api",
        ROOT / "src" / snake_name / "debug.py",
        # Docker files
        ROOT / "Dockerfile",
        ROOT / "docker-compose.yml",
        ROOT / ".dockerignore",
        # Item example files (depend on API schemas)
        ROOT / "src" / snake_name / "repositories" / "items.py",
        ROOT / "src" / snake_name / "services" / "items.py",
        ROOT / "src" / snake_name / "models" / "items.py",
        # Tests that depend on API
        ROOT / "tests" / "test_health.py",
        ROOT / "tests" / "test_items.py",
    ]

    delete_paths(paths_to_delete)

    # Update __init__.py files to remove Item imports
    update_init_files_for_library(snake_name)

    # Update pyproject.toml
    update_pyproject_for_library()

    # Update Makefile
    update_makefile_for_library(snake_name)

    # Update .pre-commit-config.yaml
    update_precommit_for_library()

    # Regenerate conftest.py
    regenerate_conftest()

    # Create a sample test file
    create_sample_test(snake_name)


def update_init_files_for_library(snake_name: str) -> None:
    """Update __init__.py files to remove Item-related imports."""
    # Update repositories/__init__.py
    repos_init = ROOT / "src" / snake_name / "repositories" / "__init__.py"
    repos_init.write_text('''"""Repository layer for data access.

The repository pattern separates data access logic from business logic,
making it easy to swap storage backends (in-memory, MongoDB, PostgreSQL, etc.).
"""

from __future__ import annotations

from {name}.repositories.base import BaseRepository
from {name}.repositories.memory import InMemoryRepository

__all__ = [
    "BaseRepository",
    "InMemoryRepository",
]
'''.replace("{name}", snake_name), encoding="utf-8")

    # Update services/__init__.py
    services_init = ROOT / "src" / snake_name / "services" / "__init__.py"
    services_init.write_text('''"""Services package - business logic layer."""

from {name}.services.base import BaseService

__all__ = ["BaseService"]
'''.replace("{name}", snake_name), encoding="utf-8")

    # Update models/__init__.py
    models_init = ROOT / "src" / snake_name / "models" / "__init__.py"
    models_init.write_text('''"""Domain models package."""

from __future__ import annotations

# Add your domain models here
''', encoding="utf-8")


def update_pyproject_for_library() -> None:
    """Remove API-related dependencies from pyproject.toml."""
    pyproject = ROOT / "pyproject.toml"
    content = pyproject.read_text(encoding="utf-8")

    # Remove API dependencies
    deps_to_remove = [
        '    "fastapi>=0.115.0",\n',
        '    "pydantic-settings>=2.7.0",\n',
        '    "uvicorn>=0.34.0",\n',
    ]
    for dep in deps_to_remove:
        content = content.replace(dep, "")

    # Remove dev dependencies
    dev_deps_to_remove = [
        '    "debugpy>=1.8.0",\n',
        '    "httpx>=0.28.0",\n',
    ]
    for dep in dev_deps_to_remove:
        content = content.replace(dep, "")

    # Remove Docker files from sdist include
    content = content.replace('    "Dockerfile",\n', "")
    content = content.replace('    ".dockerignore",\n', "")

    # Remove per-file-ignores for api/exceptions.py (doesn't exist in library mode)
    # This handles the pattern with the renamed package name
    content = re.sub(
        r'\[tool\.ruff\.lint\.per-file-ignores\]\n"src/[^/]+/api/exceptions\.py" = \["N818"\].*?\n',
        "",
        content,
    )

    pyproject.write_text(content, encoding="utf-8")


def update_makefile_for_library(snake_name: str) -> None:
    """Remove Docker/server targets from Makefile."""
    makefile = ROOT / "Makefile"

    # New Makefile content for library mode
    library_makefile = f'''SHELL := /bin/bash

UV ?= uv
VENV ?= .venv
BIN := $(VENV)/bin

.PHONY: help venv install install-dev test lint format typecheck check pre-commit clean

help:
\t@echo "Setup:"
\t@echo "  venv         Create virtualenv with uv in $(VENV)"
\t@echo "  install      Install package (production) into venv"
\t@echo "  install-dev  Install package + dev dependencies into venv"
\t@echo ""
\t@echo "Development:"
\t@echo "  test         Run test suite with coverage"
\t@echo "  lint         Lint code with ruff"
\t@echo "  format       Format code with ruff"
\t@echo "  typecheck    Type check with mypy"
\t@echo "  check        Run lint, typecheck, and test"
\t@echo "  pre-commit   Run pre-commit hooks on all files"
\t@echo ""
\t@echo "Maintenance:"
\t@echo "  clean        Remove build artifacts and venv"

venv:
\t$(UV) venv $(VENV)

install: venv
\t$(UV) pip install -e .

install-dev: venv
\t$(UV) pip install -e ".[dev]"

test:
\t$(UV) run --extra dev pytest --cov={snake_name}

lint:
\t$(UV) run --extra dev ruff check src/ tests/

format:
\t$(UV) run --extra dev ruff format src/ tests/

typecheck:
\t$(UV) run --extra dev mypy src/

check: lint typecheck test

pre-commit:
\t$(UV) run --extra dev pre-commit run --all-files

clean:
\trm -rf $(VENV) build dist *.egg-info .pytest_cache .coverage coverage.xml htmlcov .ruff_cache
'''

    makefile.write_text(library_makefile, encoding="utf-8")


def update_precommit_for_library() -> None:
    """Remove FastAPI from mypy additional_dependencies."""
    precommit = ROOT / ".pre-commit-config.yaml"
    content = precommit.read_text(encoding="utf-8")

    # Remove fastapi from additional_dependencies
    content = content.replace("          - fastapi>=0.115.0\n", "")

    precommit.write_text(content, encoding="utf-8")


def regenerate_conftest() -> None:
    """Create minimal conftest.py for library mode."""
    conftest = ROOT / "tests" / "conftest.py"
    content = '''"""Pytest fixtures for testing."""

from __future__ import annotations

# Add project-specific fixtures here
'''
    conftest.write_text(content, encoding="utf-8")


def create_sample_test(snake_name: str) -> None:
    """Create a sample test file for library mode."""
    test_file = ROOT / "tests" / "test_sample.py"
    content = f'''"""Sample tests for {snake_name}."""

from __future__ import annotations


def test_import() -> None:
    """Test that the package can be imported."""
    import {snake_name}

    assert hasattr({snake_name}, "__version__")
'''
    test_file.write_text(content, encoding="utf-8")


# === README Generation ===
def generate_readme(config: dict[str, Any], is_library: bool) -> None:
    """Generate minimal project README."""
    name = config["name"]
    kebab_name = name.replace("_", "-")
    description = config["description"]

    if is_library:
        readme_content = f'''# {kebab_name}

{description}

## Installation

```bash
pip install {kebab_name}
```

Or for development:

```bash
git clone https://github.com/your-username/{kebab_name}.git
cd {kebab_name}
make install-dev
```

## Usage

```python
from {name} import ...
```

## Development

```bash
make install-dev  # Install with dev dependencies
make test         # Run tests
make check        # Run lint, typecheck, and tests
```

## License

MIT License
'''
    else:
        readme_content = f'''# {kebab_name}

{description}

## Quick Start

```bash
# Install dependencies
make install-dev

# Copy environment config
cp env.example .env

# Start development server
make dev
```

Open http://127.0.0.1:8000/docs for the API documentation.

## Development

```bash
make dev          # Run with hot reload
make test         # Run tests
make check        # Run lint, typecheck, and tests
make docker-dev   # Run in Docker with debugpy
```

Run `make help` for all available commands.

## Project Structure

```
{kebab_name}/
├── src/{name}/
│   ├── api/           # HTTP layer (routes, schemas)
│   ├── services/      # Business logic
│   ├── repositories/  # Data access
│   └── models/        # Domain entities
├── tests/
├── Dockerfile
└── docker-compose.yml
```

## License

MIT License
'''

    readme = ROOT / "README.md"
    readme.write_text(readme_content, encoding="utf-8")


# === Main ===
def main() -> None:
    """Run the setup process."""
    config = prompt_user()

    # Derive name variants
    snake_name = config["name"]
    kebab_name = snake_name.replace("_", "-")
    upper_name = snake_name.upper()

    is_library = config["mode"] == "library"
    mode_str = "library" if is_library else "service"

    print_header(f"Creating {snake_name} ({mode_str} mode)")

    # Build replacements dict
    replacements = {
        TEMPLATE_SNAKE: snake_name,
        TEMPLATE_KEBAB: kebab_name,
        TEMPLATE_UPPER: upper_name,
    }

    # 1. Rename source folder first
    old_src = ROOT / "src" / TEMPLATE_SNAKE
    new_src = ROOT / "src" / snake_name
    if old_src.exists():
        rename_folder(old_src, new_src)
        print_step(f"Renamed src/{TEMPLATE_SNAKE} -> src/{snake_name}")

    # 2. Replace strings in all files
    files = get_all_files()
    modified_count = 0
    for file in files:
        if rename_in_file(file, replacements):
            modified_count += 1
    print_step(f"Updated {modified_count} files")

    # 3. Copy examples
    copy_examples()
    print_step("Copied .vscode.example -> .vscode")
    print_step("Copied env.example -> .env")

    # 4. Delete example files
    delete_paths([ROOT / ".vscode.example", ROOT / "env.example"])
    print_step("Removed .vscode.example")
    print_step("Removed env.example")

    # 5. Library mode stripping
    if is_library:
        strip_for_library(snake_name)
        print_step("Removed API layer (src/{}/api)".format(snake_name))
        print_step("Removed Docker files")
        print_step("Updated pyproject.toml for library")
        print_step("Updated Makefile for library")
        print_step("Created sample test file")

    # 6. Update pyproject.toml metadata
    pyproject = ROOT / "pyproject.toml"
    content = pyproject.read_text(encoding="utf-8")

    # Update description
    content = re.sub(
        r'description = ".*?"',
        f'description = "{config["description"]}"',
        content,
    )

    # Update authors if provided (must be table format for pyproject.toml)
    if config["author"]:
        # Parse author into name and email if format is "Name <email>"
        author = config["author"]
        email_match = re.match(r"(.+?)\s*<(.+?)>", author)
        if email_match:
            name, email = email_match.groups()
            author_entry = f'{{name = "{name.strip()}", email = "{email.strip()}"}}'
        else:
            author_entry = f'{{name = "{author}"}}'
        content = re.sub(
            r"authors = \[\]",
            f"authors = [{author_entry}]",
            content,
        )

    pyproject.write_text(content, encoding="utf-8")
    print_step("Updated pyproject.toml metadata")

    # 7. Generate new README
    generate_readme(config, is_library)
    print_step("Generated README.md")

    # 8. Delete uv.lock (will be regenerated)
    uv_lock = ROOT / "uv.lock"
    if uv_lock.exists():
        uv_lock.unlink()
        print_step("Removed uv.lock (will be regenerated)")

    # 9. Delete LICENSE if user wants to change it
    # (Keep it for now, user can replace)

    # 10. Self-destruct
    setup_script = ROOT / "setup.py"
    if setup_script.exists():
        setup_script.unlink()
        print_step("Removed setup.py")

    # Done!
    print_header("Setup Complete!")
    if is_library:
        print("Next steps:")
        print("  make install-dev")
        print("  make check")
    else:
        print("Next steps:")
        print("  make install-dev")
        print("  make dev")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
        sys.exit(1)
