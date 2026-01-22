# Contributing to Employee Onboarding Agentic AI

Thank you for considering contributing to this project! 🎉

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Clear title** and description
- **Steps to reproduce** the behavior
- **Expected behavior**
- **Actual behavior**
- **Environment** (OS, Python version, dependencies)
- **Error logs** or screenshots

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear title** and description
- **Use case** - why is this enhancement needed?
- **Proposed solution** - how would you implement it?
- **Alternatives** - what other solutions did you consider?

### Pull Requests

1. **Fork** the repository
2. **Create branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make changes** following coding standards
4. **Add tests** for new functionality
5. **Run tests** to ensure nothing breaks:
   ```bash
   pytest tests/ -v --cov
   ```
6. **Commit** with conventional commit messages:
   ```bash
   git commit -m "feat: add new agent capability"
   ```
7. **Push** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
8. **Open Pull Request** with clear description

## Development Setup

### 1. Clone Repository
```bash
git clone https://github.com/agentic-hr-solutions/HR-Agent.git
cd HR-Agent/backend
```

### 2. Create Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -e ".[dev]"
```

### 4. Run Tests
```bash
pytest tests/ -v
```

## Coding Standards

### Python Style Guide

- Follow **PEP 8** style guide
- Use **type hints** for all functions
- Maximum line length: **100 characters**
- Use **ruff** for linting:
  ```bash
  ruff check backend/
  ruff format backend/
  ```

### Type Checking

- Use **pyright** for static type checking:
  ```bash
  pyright backend/
  ```
- All new code must pass type checking

### Testing Requirements

- **Unit tests** for all new functions
- **Integration tests** for workflows
- **Minimum coverage**: 80%
- Tests must pass before PR is merged

### Commit Message Convention

Use conventional commits:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `test`: Adding tests
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `chore`: Maintenance tasks

**Examples:**
```bash
feat(agents): add Slack notification agent
fix(api): resolve CORS preflight issue
docs(readme): update deployment instructions
test(cosmos): add integration tests for DB client
```

## Project Structure

```
backend/
├── agents/           # Agent implementations
├── integrations/     # External service integrations
├── tests/           # All test files
├── function_app.py  # Azure Functions entry
└── pyproject.toml   # Dependencies
```

### Adding New Agents

1. Create agent file in `backend/agents/`
2. Implement agent function following pattern:
   ```python
   def agent_name(state: OnboardingState) -> OnboardingState:
       """Agent description."""
       # Implementation
       return state
   ```
3. Add agent to LangGraph in `graph.py`
4. Create tests in `tests/test_agents/`
5. Update documentation

### Adding New Integrations

1. Create module in `backend/integrations/`
2. Implement client with environment configuration
3. Add singleton pattern if applicable
4. Create tests in `tests/`
5. Update `.env.example`

## Questions?

- **GitHub Issues**: [Report bugs or request features](https://github.com/agentic-hr-solutions/HR-Agent/issues)
- **Discussions**: [Ask questions or share ideas](https://github.com/agentic-hr-solutions/HR-Agent/discussions)

## Recognition

Contributors will be acknowledged in:
- README.md Contributors section
- Release notes for significant contributions

Thank you for contributing! 🙏
