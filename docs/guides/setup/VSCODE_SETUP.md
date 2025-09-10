# VSCode Development Setup

This document describes the VSCode development environment setup for the MCP Server project.

## Prerequisites

- **VSCode**: Latest version with recommended extensions
- **Poetry**: Python dependency management
- **Python 3.10+**: Required for the project
- **Git**: Version control

## Getting Started

### 1. Clone and Setup
```bash
git clone https://github.com/hannesnortje/cursor.git
cd cursor
git checkout vscode-development
poetry install
```

### 2. Open in VSCode
```bash
code .
```

### 3. Install Recommended Extensions
VSCode will prompt you to install recommended extensions from `.vscode/extensions.json`:
- **ms-python.python**: Python language support
- **ms-python.black-formatter**: Code formatting
- **ms-python.flake8**: Linting
- **ms-python.mypy-type-checker**: Type checking
- **github.copilot**: AI code completion
- **github.copilot-chat**: AI chat assistance

## Development Workflow

### Python Environment
The Poetry virtual environment is automatically configured:
- **Python Path**: `/home/hannesn/.cache/pypoetry/virtualenvs/mcp-server-4zyLa6-K-py3.12/bin/python`
- **Auto-activation**: Terminal automatically activates the Poetry environment

### Code Quality Tools

#### Formatting (Black)
- **Auto-format on save**: Enabled
- **Line length**: 88 characters
- **Manual**: `Ctrl+Shift+P` → "Format Document"

#### Linting (Flake8)
- **Real-time linting**: Enabled
- **Manual**: `Ctrl+Shift+P` → "Python: Run Linting"

#### Type Checking (MyPy)
- **Mode**: Basic type checking
- **Manual**: `Ctrl+Shift+P` → "Python: Run Type Checking"

### Testing

#### Unit Tests
- **Framework**: pytest with asyncio support
- **Run all**: `Ctrl+Shift+P` → "Python: Run All Tests"
- **Run current**: `Ctrl+Shift+P` → "Python: Run Current Test File"
- **Debug**: Use the debug configuration "Python: Test Current File"

#### Available Test Categories
- **Unit Tests**: `tests/unit/` - Fast, isolated tests
- **Integration Tests**: `tests/integration/` - Component integration
- **E2E Tests**: `tests/end_to_end/` - Full system tests

### Development Scripts

Use the development script for common tasks:

```bash
./scripts/dev.sh <command>
```

Available commands:
- `format` - Format code with Black
- `lint` - Lint code with Flake8
- `typecheck` - Type check with MyPy
- `test` - Run unit tests
- `test_all` - Run all tests
- `quality` - Run all quality checks
- `server` - Start MCP server
- `clean` - Clean cache and temp files
- `deps` - Install/update dependencies

### VSCode Tasks

Use `Ctrl+Shift+P` → "Tasks: Run Task" to access:
- **Format Code**: Run Black formatter
- **Lint Code**: Run Flake8 linter
- **Type Check**: Run MyPy type checker
- **Run Unit Tests**: Execute unit test suite
- **Run All Tests**: Execute full test suite
- **Quality Check**: Run all quality tools
- **Start MCP Server**: Launch the server
- **Test LLM Coordinator**: Test coordinator functionality

### Debugging

#### Debug Configurations
Available in the Debug panel (`Ctrl+Shift+D`):
- **Python: MCP Server**: Debug the main server
- **Python: Current File**: Debug any Python file
- **Python: Test Current File**: Debug current test file
- **Python: All Tests**: Debug all tests
- **Python: LLM Coordinator Test**: Debug coordinator tests

#### Breakpoints
- Set breakpoints by clicking in the gutter
- Conditional breakpoints: Right-click → "Add Conditional Breakpoint"
- Logpoints: Right-click → "Add Logpoint"

### Git Integration

#### Pre-commit Hooks
Automatically installed and configured:
- **Code formatting**: Black
- **Linting**: Flake8
- **Type checking**: MyPy
- **Fast tests**: Unit tests only
- **File checks**: YAML, JSON, TOML validation

#### Branch Strategy
- **main**: Stable production code
- **llm-implementation**: Latest stable features
- **vscode-development**: VSCode-specific development
- **feature/***: New feature development

### Project Structure

```
.
├── .vscode/                    # VSCode configuration
│   ├── settings.json          # Editor settings
│   ├── launch.json            # Debug configurations
│   ├── tasks.json             # Task definitions
│   └── extensions.json        # Recommended extensions
├── scripts/                   # Development scripts
│   └── dev.sh                 # Main development script
├── src/                       # Source code
│   ├── agents/                # Agent implementations
│   ├── communication/         # Communication system
│   ├── database/              # Database and storage
│   ├── dashboard/             # Web dashboard
│   ├── llm/                   # LLM integration
│   ├── mcp_tools/             # MCP tool implementations
│   └── security/              # Security features
├── tests/                     # Test suite
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   └── end_to_end/            # E2E tests
├── protocol_server.py         # Main MCP server
├── pyproject.toml             # Poetry configuration
├── pytest.ini                # Test configuration
└── .pre-commit-config.yaml    # Git hooks
```

## Testing Integration

### Running Tests in VSCode

#### Using Test Explorer
1. Open Test Explorer (`Ctrl+Shift+E` → Test tab)
2. Tests are automatically discovered
3. Click play button to run tests
4. Click debug button to debug tests

#### Using Command Palette
- `Ctrl+Shift+P` → "Python: Run All Tests"
- `Ctrl+Shift+P` → "Python: Run Current Test File"
- `Ctrl+Shift+P` → "Python: Debug All Tests"

#### Using Terminal
```bash
# Run unit tests
poetry run pytest tests/unit/ -v

# Run with coverage
poetry run pytest tests/unit/ --cov=src

# Run specific test
poetry run pytest tests/unit/test_enhanced_server.py::test_coordinator_chat -v
```

### Writing Tests

#### Test Structure
```python
import pytest
from src.agents.coordinator.coordinator_agent import CoordinatorAgent

@pytest.mark.asyncio
async def test_coordinator_functionality():
    """Test coordinator agent functionality."""
    coordinator = CoordinatorAgent()
    result = await coordinator.process_message("test")
    assert result["success"] is True
```

#### Test Categories
Use pytest markers:
```python
@pytest.mark.unit
@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.mcp
```

## Performance Monitoring

### Built-in Monitoring
- **Memory usage**: Tracked during development
- **Response times**: Measured for all operations
- **Error rates**: Monitored and logged

### Profiling
```bash
# Profile specific function
poetry run python -m cProfile -o profile.stats script.py

# View profile results
poetry run python -c "import pstats; pstats.Stats('profile.stats').sort_stats('cumulative').print_stats(20)"
```

## Troubleshooting

### Common Issues

#### Import Errors
- Ensure `PYTHONPATH` includes project root
- Check virtual environment activation
- Verify dependencies are installed: `poetry install`

#### Test Failures
- Check async test configuration in `pytest.ini`
- Ensure `pytest-asyncio` is installed
- Verify test database isolation

#### Type Checking Issues
- Update type stubs: `poetry run mypy --install-types`
- Check `mypy.ini` configuration
- Use `# type: ignore` for external library issues

#### Linting Errors
- Check `.flake8` configuration
- Use `# noqa: <code>` to ignore specific lines
- Ensure consistent code style with Black

### Getting Help

1. Check the main documentation in `docs/`
2. Review test files for usage examples
3. Use GitHub Copilot Chat for specific questions
4. Refer to the implementation progress in `docs/implementation/IMPLEMENTATION_PROGRESS.md`

## Next Steps

1. **Familiarize** with the codebase structure
2. **Run** the quality check: `./scripts/dev.sh quality`
3. **Start** the MCP server: `./scripts/dev.sh server`
4. **Begin** development with proper testing and linting

The VSCode environment is now fully configured for productive development of the MCP Server project!
