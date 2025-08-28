# Contributing to HashSmith

Thank you for your interest in contributing to HashSmith! This document covers setup, testing, project structure, and contribution guidelines.

## 📚 Project Structure

```
hashsmith/
├── src/hashsmith/           # Main package
│   ├── patterns/            # Pattern engine
│   ├── attacks/             # Attack implementations
│   └── core/                # Hashcat integration
├── tests/                   # Test suites
├── attack_files/            # Generated wordlists
└── workspace/               # Working directory
```

## 🧪 Testing

Ensure you have all development dependencies installed (pytest, etc.).

```bash
# Run all tests
pdm run test

# Run tests with coverage
pdm run test-cov

# Run a specific test file or suite
pdm run pytest tests/test_transform_behavior.py -v
```

## 🔧 Code Quality & Linting

This project uses modern Python tooling for code quality:

- **Black**: Code formatting with single-quote preference
- **Ruff**: Fast linting with comprehensive rule set
- **MyPy**: Static type checking

```bash
# Format code with Black
pdm run format

# Lint code with Ruff
pdm run lint

# Type check with MyPy
pdm run typecheck

# Run all quality checks
pdm run lint && pdm run typecheck && pdm run format
```

## ⚙️ Development Setup

1. **Install dependencies**:
   ```bash
   pdm install
   ```
2. **Install development dependencies**:
   ```bash
   pdm install --dev
   ```
3. **Activate virtual environment**:
   ```bash
   pdm venv activate
   ```
4. **Run linting and tests frequently** as you develop new features.

---

By contributing, you agree that your submissions will be licensed under the MIT license. 