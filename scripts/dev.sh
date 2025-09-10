#!/bin/bash
# Development scripts for MCP Server project

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE} MCP Server Development Scripts${NC}"
    echo -e "${BLUE}========================================${NC}"
}

# Format code
format() {
    echo -e "${YELLOW}🎨 Formatting code with Black...${NC}"
    poetry run black .
    echo -e "${GREEN}✅ Code formatting complete${NC}"
}

# Lint code
lint() {
    echo -e "${YELLOW}🔍 Linting code with Flake8...${NC}"
    poetry run flake8 .
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Linting passed${NC}"
    else
        echo -e "${RED}❌ Linting failed${NC}"
        return 1
    fi
}

# Type check
typecheck() {
    echo -e "${YELLOW}🔧 Type checking with MyPy...${NC}"
    poetry run mypy src/ --ignore-missing-imports
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Type checking passed${NC}"
    else
        echo -e "${RED}❌ Type checking failed${NC}"
        return 1
    fi
}

# Run tests
test() {
    echo -e "${YELLOW}🧪 Running tests...${NC}"
    poetry run pytest tests/unit/ -v
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Unit tests passed${NC}"
    else
        echo -e "${RED}❌ Unit tests failed${NC}"
        return 1
    fi
}

# Run integration tests
test_integration() {
    echo -e "${YELLOW}🧪 Running integration tests...${NC}"
    poetry run pytest tests/integration/ -v --tb=short
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Integration tests passed${NC}"
    else
        echo -e "${RED}❌ Integration tests failed${NC}"
        return 1
    fi
}

# Run all tests
test_all() {
    echo -e "${YELLOW}🧪 Running all tests...${NC}"
    poetry run pytest tests/ -v --tb=short
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ All tests passed${NC}"
    else
        echo -e "${RED}❌ Some tests failed${NC}"
        return 1
    fi
}

# Quality check (format, lint, typecheck, test)
quality() {
    print_header
    echo -e "${YELLOW}🔍 Running quality checks...${NC}"

    format || return 1
    lint || return 1
    typecheck || return 1
    test || return 1

    echo -e "${GREEN}✅ All quality checks passed!${NC}"
}

# Start MCP server
server() {
    echo -e "${YELLOW}🚀 Starting MCP Server...${NC}"
    poetry run python protocol_server.py
}

# Test LLM coordinator
test_llm() {
    echo -e "${YELLOW}🤖 Testing LLM Coordinator...${NC}"
    poetry run python test_llm_coordinator_real.py
}

# Development server with auto-reload (for dashboard)
dev() {
    echo -e "${YELLOW}🔧 Starting development environment...${NC}"
    echo -e "${BLUE}MCP Server will start on default ports${NC}"
    echo -e "${BLUE}Dashboard will be available at http://localhost:5000${NC}"
    poetry run python protocol_server.py
}

# Clean cache and temporary files
clean() {
    echo -e "${YELLOW}🧹 Cleaning cache and temporary files...${NC}"
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type f -name "*.pyo" -delete 2>/dev/null || true
    echo -e "${GREEN}✅ Cleanup complete${NC}"
}

# Install/update dependencies
deps() {
    echo -e "${YELLOW}📦 Installing/updating dependencies...${NC}"
    poetry install
    poetry run pre-commit install
    echo -e "${GREEN}✅ Dependencies updated${NC}"
}

# Show help
help() {
    print_header
    echo -e "${YELLOW}Available commands:${NC}"
    echo -e "  ${BLUE}format${NC}          Format code with Black"
    echo -e "  ${BLUE}lint${NC}            Lint code with Flake8"
    echo -e "  ${BLUE}typecheck${NC}       Type check with MyPy"
    echo -e "  ${BLUE}test${NC}            Run unit tests"
    echo -e "  ${BLUE}test_integration${NC} Run integration tests"
    echo -e "  ${BLUE}test_all${NC}        Run all tests"
    echo -e "  ${BLUE}quality${NC}         Run all quality checks"
    echo -e "  ${BLUE}server${NC}          Start MCP server"
    echo -e "  ${BLUE}test_llm${NC}        Test LLM coordinator"
    echo -e "  ${BLUE}dev${NC}             Start development environment"
    echo -e "  ${BLUE}clean${NC}           Clean cache and temporary files"
    echo -e "  ${BLUE}deps${NC}            Install/update dependencies"
    echo -e "  ${BLUE}help${NC}            Show this help message"
    echo
    echo -e "${YELLOW}Usage:${NC}"
    echo -e "  ./scripts/dev.sh <command>"
    echo -e "  chmod +x scripts/dev.sh && ./scripts/dev.sh quality"
}

# Main script logic
case "${1:-help}" in
    format)
        format
        ;;
    lint)
        lint
        ;;
    typecheck)
        typecheck
        ;;
    test)
        test
        ;;
    test_integration)
        test_integration
        ;;
    test_all)
        test_all
        ;;
    quality)
        quality
        ;;
    server)
        server
        ;;
    test_llm)
        test_llm
        ;;
    dev)
        dev
        ;;
    clean)
        clean
        ;;
    deps)
        deps
        ;;
    help|*)
        help
        ;;
esac
