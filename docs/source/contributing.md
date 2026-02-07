# Contributing

First off, thank you for considering contributing to PyCAS-SSO! We welcome contributions of all kinds: bug reports, documentation improvements, new features, and more.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

Contribution to this project take place on its [GitHub](https://github.com/unguestapp/pycas-sso) repository.

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps which reproduce the problem**
- **Provide specific examples to demonstrate the steps**
- **Describe the behavior you observed after following the steps**
- **Explain which behavior you expected to see instead and why**
- **Include screenshots if possible**
- **Include your environment details** (Python version, OS, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

- **A clear and descriptive title**
- **A detailed description of the suggested enhancement**
- **Step-by-step description of the suggested enhancement**
- **Examples of how the feature would be used**
- **Why would this enhancement be useful to most users**

### Pull Requests

- Fill in the required template
- Follow the Python styleguide
- Include appropriate test cases
- Update documentation as needed

## Development Setup

### Prerequisites

- Python >= 3.11
- Git

### Setting Up Your Development Environment

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/your-username/pycas-sso.git
   cd pycas-sso
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies:**
   ```bash
   pip install -e ".[dev,httpx,requests,aiohttp]"
   ```

4. **Install pre-commit hooks (optional but recommended):**
   ```bash
   pip install pre-commit
   pre-commit install
   ```

### Running Tests

Run the full test suite with coverage:
```bash
pytest -vv
```

### Building Documentation

The project uses Sphinx for documentation:

```bash
cd docs
pip install -r requirements.txt
sphinx-build -b html source build/
```

Or use the autobuild feature:
```bash
sphinx-autobuild source build/
```

## Styleguide

### Python Code Style

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with the following preferences:

- Use 4 spaces for indentation (not tabs)
- Use meaningful variable names
- Add docstrings to all public functions and classes
- Use type hints where possible

### Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

Example:
```
Add support for CAS 3.0 protocol

This adds validation support for the CAS 3.0 protocol version.
Closes #123
```

### Documentation

- Use clear and concise language
- Include code examples where appropriate
- Keep documentation up-to-date with code changes
- Follow Markdown conventions

## AI-Generated Policy

### Automatic AI Generation: Not Allowed

Contributions consisting of **automatically generated code or report** from AI systems (code generation tools, ChatGPT code output, etc.) are **rejected**. We require human authorship and responsibility for all contributions.

### Intelligent AI Use: Encouraged with Safeguards

The use of AI tools in your development process is **tolerated and even encouraged** when applied intelligently and with full control:

- **AI as an assistant**: Using AI to understand code patterns, generate initial scaffolding, or suggest improvements is acceptable
- **Your responsibility**: You must thoroughly review, understand, and take ownership of any AI-assisted code before submitting
- **Quality standards**: AI-assisted code must meet the same quality, testing, and documentation standards as manually written code
- **Transparency**: If substantial portions of your PR were AI-assisted, please mention this in your PR description so reviewers are aware

### Guidelines for Responsible AI Use

1. **Review carefully**: Understand every line of code before submission
2. **Test thoroughly**: Ensure AI-generated suggestions are correct and handle edge cases
3. **Refactor if needed**: Polish code to match project standards and idioms
4. **Document your work**: Add clear comments and docstrings
5. **Be transparent**: Disclose AI assistance in PRs when significant

## Pull Request Process

1. **Before you start**
   - Check existing issues and pull requests
   - Discuss major changes in an issue first

2. **Make your changes**
   - Create a fork of the project
   - Create a feature branch: `git checkout -b feature/your-feature-name`
   - Make your changes with clear, atomic commits
   - Add tests for new functionality
   - Update documentation if needed

3. **Test your changes**
   - Run the full test suite: `pytest`
   - Ensure all tests pass
   - Check code coverage: `pytest --cov=pycas_sso`
   - Verify documentation builds correctly

4. **Commit and push**
   - If the main branch changed, rebase you feature branch before: `git rebase origin/main`
   - Push to your fork: `git push origin feature/your-feature-name`
   - Create a pull request with a clear description

5. **Code review**
   - Respond to code review feedback
   - Make requested changes in new commits
   - Keep the branch up-to-date with main

6. **Merge**
   - Ensure all checks pass
   - A maintainer will merge your PR

## Project Structure

```
pycas-sso/
├── pycas_sso/           # Main package
│   ├── cas.py          # Main CAS client
│   ├── errors.py       # Error definitions
│   ├── schemas.py      # Data schemas
│   ├── xml.py          # XML parsing utilities
│   └── clients/        # HTTP client implementations
├── tests/              # Test suite
├── docs/               # Documentation
└── pyproject.toml      # Project configuration
```

## Testing Guidelines

- Write tests for all new features
- Update existing tests when modifying functionality
- Aim for at least 80% code coverage
- Use descriptive test names: `test_<function>_<scenario>`
- Use fixtures for common test setup


## Documentation Guidelines

- Keep documentation in sync with code
- Use clear, simple language
- Include code examples
- Document all public APIs
- Add docstrings using Google-style format


## Additional Notes

### Issue and Pull Request Labels

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Improvements or additions to documentation
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention is needed
- `question`: Further information is requested

## Questions?

Feel free to open an issue or ask in discussions. We're here to help!

## License

By contributing to PyCAS-SSO, you agree that your contributions will be licensed under its BSD 3-Clause "New" or "Revised" License.