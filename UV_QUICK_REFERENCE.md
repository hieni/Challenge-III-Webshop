# UV Package Manager - Quick Reference Guide

## What is UV?

UV is a modern, extremely fast Python package installer and resolver written in Rust. It's designed as a drop-in replacement for pip and pip-tools, offering 10-100x faster installation speeds.

## Installation

### Windows (PowerShell)
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### macOS/Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Verify Installation
```powershell
uv --version
```

---

## Common Commands

### Virtual Environment Management

```powershell
# Create new virtual environment
uv venv

# Create with specific Python version
uv venv --python 3.13

# Create in custom location
uv venv .venv

# Activate (Windows)
.venv\Scripts\Activate.ps1

# Activate (macOS/Linux)
source .venv/bin/activate
```

### Package Installation

```powershell
# Install from pyproject.toml (editable mode)
uv pip install -e .

# Install from pyproject.toml (non-editable)
uv pip install .

# Install from requirements.txt
uv pip install -r requirements.txt

# Install specific package
uv pip install django

# Install specific version
uv pip install django==5.2.8

# Install with extras
uv pip install -e ".[dev]"
```

### Dependency Management

```powershell
# Sync exact versions from lock file
uv pip sync

# Compile dependencies to requirements.txt
uv pip compile pyproject.toml -o requirements.txt

# Compile with extras
uv pip compile pyproject.toml --extra dev -o requirements-dev.txt

# Update all dependencies
uv pip install --upgrade -e .

# Update specific package
uv pip install --upgrade django
```

### Package Information

```powershell
# List installed packages
uv pip list

# Show package details
uv pip show django

# Freeze current environment
uv pip freeze

# Check for outdated packages
uv pip list --outdated
```

### Uninstallation

```powershell
# Uninstall package
uv pip uninstall django

# Uninstall from requirements
uv pip uninstall -r requirements.txt
```

---

## Project Setup Workflows

### Starting New Project

```powershell
# 1. Create project directory
mkdir my-project
cd my-project

# 2. Create virtual environment
uv venv

# 3. Activate environment
.venv\Scripts\Activate.ps1

# 4. Create pyproject.toml
# (see example below)

# 5. Install project
uv pip install -e .
```

### Cloning Existing Project

```powershell
# 1. Clone repository
git clone <repo-url>
cd <project>

# 2. Create virtual environment
uv venv

# 3. Activate environment
.venv\Scripts\Activate.ps1

# 4. Install dependencies
uv pip install -e .

# OR sync from lock file for exact versions
uv pip sync
```

### Adding Dependencies

```powershell
# Method 1: Edit pyproject.toml manually
# Add to [project.dependencies] section
dependencies = [
    "django>=5.2.8",
    "new-package>=1.0.0",  # <-- Add here
]

# Then install
uv pip install -e .

# Method 2: Use uv add (if available in your UV version)
uv add new-package

# Generate updated requirements.txt
uv pip compile pyproject.toml -o requirements.txt
```

---

## pyproject.toml Example

### Minimal Configuration
```toml
[project]
name = "my-project"
version = "1.0.0"
requires-python = ">=3.13"
dependencies = [
    "django>=5.2.8",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### Complete Configuration
```toml
[project]
name = "webshop-backend"
version = "1.0.0"
description = "Django webshop backend"
readme = "README.md"
requires-python = ">=3.13"
license = {text = "MIT"}
authors = [
    {name = "Dev Team", email = "dev@example.com"}
]
keywords = ["django", "webshop", "api"]

dependencies = [
    "django>=5.2.8",
    "psycopg2-binary>=2.9.9",
    "gunicorn>=22.0.0",
]

[project.optional-dependencies]
dev = [
    "django-debug-toolbar>=4.3.0",
    "ipython>=8.20.0",
    "pytest>=8.0.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["shop", "webshop"]
```

---

## UV vs pip Comparison

| Feature | UV | pip |
|---------|----|----- |
| **Speed** | 10-100x faster | Baseline |
| **Dependency Resolution** | Advanced SAT solver | Basic resolver |
| **Lock Files** | Native support | Requires pip-tools |
| **Virtual Environments** | `uv venv` built-in | Separate `venv` module |
| **Written In** | Rust | Python |
| **Memory Usage** | Low | Higher |
| **Parallel Downloads** | Yes | Limited |
| **Cache** | Efficient global cache | Basic cache |

---

## Troubleshooting

### UV Command Not Found
```powershell
# Restart PowerShell or terminal
# OR manually add to PATH (Windows)
$env:PATH += ";$env:USERPROFILE\.cargo\bin"
```

### Permission Errors (Windows)
```powershell
# Run PowerShell as Administrator
# OR change execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Conflicting Dependencies
```powershell
# UV has better resolution than pip
# Check output for conflicts
uv pip install -e .

# Force reinstall all packages
uv pip install --force-reinstall -e .
```

### Virtual Environment Not Activating
```powershell
# Windows: Ensure you use correct path
.\.venv\Scripts\Activate.ps1

# If blocked by execution policy:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\.venv\Scripts\Activate.ps1
```

### Slow First Run
```powershell
# UV builds a global cache
# First run downloads everything
# Subsequent runs are much faster
```

---

## Best Practices

1. **Always use virtual environments**
   ```powershell
   uv venv
   .venv\Scripts\Activate.ps1
   ```

2. **Use pyproject.toml for project config**
   - Modern standard (PEP 621)
   - Single source of truth
   - Better tool support

3. **Commit lock files**
   ```powershell
   uv pip freeze > uv.lock
   git add uv.lock
   ```

4. **Separate dev dependencies**
   ```toml
   [project.optional-dependencies]
   dev = ["pytest", "black", "mypy"]
   ```

5. **Use editable installs for development**
   ```powershell
   uv pip install -e .
   ```

6. **Pin versions in production**
   ```powershell
   uv pip compile pyproject.toml -o requirements.txt
   ```

---

## Migration from pip

### From requirements.txt to pyproject.toml

**Old way (requirements.txt)**:
```txt
django==5.2.8
psycopg2-binary==2.9.9
```

**New way (pyproject.toml)**:
```toml
[project]
dependencies = [
    "django>=5.2.8",
    "psycopg2-binary>=2.9.9",
]
```

### Commands Migration

| pip command | UV equivalent |
|-------------|---------------|
| `pip install -r requirements.txt` | `uv pip install -r requirements.txt` |
| `pip install django` | `uv pip install django` |
| `pip list` | `uv pip list` |
| `pip freeze` | `uv pip freeze` |
| `pip show django` | `uv pip show django` |
| `python -m venv .venv` | `uv venv` |

Just replace `pip` with `uv pip`!

---

## Resources

- **UV Documentation**: https://docs.astral.sh/uv/
- **PyPA Packaging Guide**: https://packaging.python.org/
- **PEP 621 (pyproject.toml)**: https://peps.python.org/pep-0621/
- **UV GitHub**: https://github.com/astral-sh/uv

---

## Quick Command Cheatsheet

```powershell
# Setup
uv venv                          # Create venv
.venv\Scripts\Activate.ps1       # Activate (Windows)
uv pip install -e .              # Install project

# Add packages
uv pip install <package>         # Add package
uv pip install -e ".[dev]"       # Install with dev extras

# Update
uv pip install --upgrade <pkg>   # Update package
uv pip install --upgrade -e .    # Update all

# Info
uv pip list                      # List packages
uv pip show <package>            # Package details
uv pip freeze                    # Export versions

# Lock
uv pip freeze > uv.lock          # Create lock file
uv pip sync                      # Install from lock

# Clean
uv pip uninstall <package>       # Remove package
deactivate                       # Exit venv
```

---

**Remember**: UV is a drop-in replacement for pip. Almost all pip commands work with `uv pip`!
