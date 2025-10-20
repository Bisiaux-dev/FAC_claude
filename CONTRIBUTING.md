# Contributing to CRM Automation

Thank you for your interest in contributing to CRM Automation! This document provides guidelines for contributing to the project.

## 🤝 How to Contribute

### Reporting Issues

If you find a bug or have a feature request:

1. Check if the issue already exists in [GitHub Issues](https://github.com/yourusername/rs_crm_automation/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - Environment details (Python version, OS, etc.)
   - Screenshots if applicable

### Submitting Changes

1. **Fork the repository**
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Follow code style guidelines** (see below)
5. **Add tests** for new functionality
6. **Run tests** to ensure nothing breaks:
   ```bash
   pytest tests/ -v
   flake8 src/
   ```
7. **Commit your changes**:
   ```bash
   git commit -m "Add feature: description"
   ```
8. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
9. **Create a Pull Request** with:
   - Description of changes
   - Related issue number (if applicable)
   - Screenshots/examples (if applicable)

## 📝 Code Style Guidelines

### Python Style

- Follow [PEP 8](https://pep8.org/)
- Maximum line length: 120 characters
- Use type hints where appropriate
- Use docstrings for all functions and classes

Example:
```python
def extract_data(svg_file: str) -> Dict[str, Any]:
    """
    Extract data from SVG file.

    Args:
        svg_file: Path to SVG file

    Returns:
        Dictionary containing extracted data
    """
    pass
```

### Git Commit Messages

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit first line to 72 characters
- Reference issues and pull requests

Examples:
- `Add email notification feature`
- `Fix SVG parser for nested elements`
- `Update documentation for GitHub Actions setup`
- `Refactor extraction logic (#42)`

### Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring
- `test/description` - Adding tests

## 🧪 Testing

### Running Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_parser.py -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# Linting
flake8 src/
```

### Writing Tests

- Add tests for all new functionality
- Aim for >80% code coverage
- Use descriptive test names
- Include edge cases

Example:
```python
def test_extract_title_from_svg():
    """Test title extraction from SVG file"""
    svg_file = "tests/fixtures/sample.svg"
    title, _, _, _ = extract_highcharts_data(svg_file)
    assert title == "Expected Title"
```

## 📚 Documentation

### Code Documentation

- Add docstrings to all public functions
- Include type hints
- Provide usage examples

### README Updates

- Update README.md for new features
- Add examples and screenshots
- Update configuration instructions

## 🔒 Security

- Never commit credentials or secrets
- Use `.env` files for local configuration
- Update `.gitignore` for sensitive files
- Follow security best practices in SECURITY.md

## 🎯 Development Workflow

### Setting Up Development Environment

```bash
# Clone your fork
git clone https://github.com/yourusername/rs_crm_automation.git
cd rs_crm_automation_V0.1

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-cov flake8

# Configure pre-commit hooks (optional)
pip install pre-commit
pre-commit install
```

### Before Submitting PR

Checklist:
- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Documentation updated
- [ ] No sensitive data in commits
- [ ] Branch is up to date with main
- [ ] Commit messages are clear

## 💡 Feature Requests

We welcome feature requests! Please:

1. Check existing issues first
2. Provide clear use case
3. Explain expected behavior
4. Consider implementation approach

## 🐛 Bug Reports

Good bug reports include:

1. **Summary**: Brief description
2. **Steps to reproduce**: Exact steps
3. **Expected behavior**: What should happen
4. **Actual behavior**: What actually happens
5. **Environment**: Python version, OS, etc.
6. **Logs/Screenshots**: If applicable

## 📞 Getting Help

- **GitHub Issues**: For bugs and features
- **GitHub Discussions**: For questions and ideas
- **Email**: bisiaux.pierre@outlook.fr

## 🏆 Recognition

Contributors will be acknowledged in:
- README.md contributors section
- Release notes
- GitHub contributors page

## 📜 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors.

### Expected Behavior

- Be respectful and considerate
- Welcome newcomers
- Accept constructive criticism
- Focus on what's best for the project

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or insulting comments
- Publishing others' private information
- Other unprofessional conduct

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to CRM Automation! 🎉
