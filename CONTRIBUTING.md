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
dotenv pdm run pytest

# Run a specific test file or suite
pdm run pytest tests/test_transform_behavior.py -v
```

## ⚙️ Development Setup

1. **Install dependencies**:
   ```bash
   pdm install
   ```
2. **Activate virtual environment**:
   ```bash
   pdm venv activate
   ```
3. **Run tests frequently** as you develop new features.

---

By contributing, you agree that your submissions will be licensed under the MIT license. 