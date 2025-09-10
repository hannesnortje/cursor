#!/bin/bash

# Ollama Docker Management Script
# Easy commands to manage local LLM service

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_usage() {
    echo "🤖 Ollama Docker Management for MCP Server"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  start-gpu      Start Ollama with GPU support (recommended)"
    echo "  start-cpu      Start Ollama with CPU only"
    echo "  setup          Download and setup models (run after start)"
    echo "  stop           Stop Ollama service"
    echo "  restart        Restart Ollama service"
    echo "  status         Check service status"
    echo "  logs           Show service logs"
    echo "  models         List available models"
    echo "  pull [model]   Pull a specific model"
    echo "  clean          Remove all data and start fresh"
    echo "  test           Test the LLM service"
    echo ""
    echo "Examples:"
    echo "  $0 start-gpu                    # Start with GPU (fastest)"
    echo "  $0 start-cpu                    # Start CPU-only (slower but works everywhere)"
    echo "  $0 setup                        # Setup default models"
    echo "  $0 pull llama3.1:8b             # Pull a specific model"
    echo "  $0 test                         # Test the service"
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker is not installed or not in PATH${NC}"
        exit 1
    fi

    if ! docker info &> /dev/null; then
        echo -e "${RED}❌ Docker is not running or you don't have permission${NC}"
        echo "Try: sudo systemctl start docker"
        exit 1
    fi
}

check_gpu() {
    if command -v nvidia-smi &> /dev/null; then
        echo -e "${GREEN}✅ NVIDIA GPU detected${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  No NVIDIA GPU detected, will use CPU mode${NC}"
        return 1
    fi
}

start_ollama() {
    local profile=$1

    echo -e "${BLUE}🚀 Starting Ollama with $profile support...${NC}"

    cd "$PROJECT_DIR"

    if [ "$profile" = "gpu" ]; then
        if check_gpu; then
            docker compose --profile gpu up -d ollama
        else
            echo -e "${YELLOW}⚠️  GPU not available, falling back to CPU mode${NC}"
            docker compose --profile cpu up -d ollama-cpu
        fi
    else
        docker compose --profile cpu up -d ollama-cpu
    fi

    echo -e "${GREEN}✅ Ollama started successfully!${NC}"
    echo -e "${BLUE}📍 Service available at: http://localhost:11434${NC}"

    # Wait for service to be ready
    echo -e "${YELLOW}⏳ Waiting for service to be ready...${NC}"
    sleep 5

    for i in {1..12}; do
        if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Service is ready!${NC}"
            return 0
        fi
        echo -n "."
        sleep 5
    done

    echo -e "${RED}❌ Service did not start properly${NC}"
    docker compose logs
    return 1
}

setup_models() {
    echo -e "${BLUE}📦 Setting up default models...${NC}"

    cd "$PROJECT_DIR"

    # Check if Ollama is running
    if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo -e "${RED}❌ Ollama is not running. Start it first with: $0 start-gpu${NC}"
        exit 1
    fi

    echo -e "${BLUE}📥 Downloading efficient models...${NC}"

    # Pull models directly using docker exec
    models=("llama3.2:3b" "codellama:7b" "mistral:7b")

    for model in "${models[@]}"; do
        echo -e "${YELLOW}📥 Pulling $model...${NC}"
        if docker compose exec ollama ollama pull "$model" 2>/dev/null || \
           docker compose exec ollama-cpu ollama pull "$model" 2>/dev/null; then
            echo -e "${GREEN}✅ Successfully pulled: $model${NC}"
        else
            echo -e "${RED}❌ Failed to pull: $model${NC}"
        fi
    done

    echo -e "${GREEN}🎉 Model setup complete!${NC}"
    list_models
}

stop_ollama() {
    echo -e "${YELLOW}🛑 Stopping Ollama service...${NC}"
    cd "$PROJECT_DIR"
    docker compose down
    echo -e "${GREEN}✅ Ollama stopped${NC}"
}

restart_ollama() {
    stop_ollama
    sleep 2
    start_ollama "gpu"
}

show_status() {
    echo -e "${BLUE}📊 Ollama Service Status${NC}"
    echo ""

    cd "$PROJECT_DIR"

    # Check if containers are running
    if docker compose ps | grep -q "Up"; then
        echo -e "${GREEN}✅ Ollama container is running${NC}"

        # Check if service is responding
        if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Ollama API is responding${NC}"
            echo -e "${BLUE}📍 Available at: http://localhost:11434${NC}"
        else
            echo -e "${RED}❌ Ollama API is not responding${NC}"
        fi
    else
        echo -e "${RED}❌ Ollama container is not running${NC}"
    fi

    echo ""
    docker compose ps
}

show_logs() {
    echo -e "${BLUE}📋 Ollama Service Logs${NC}"
    cd "$PROJECT_DIR"
    docker compose logs -f --tail=50
}

list_models() {
    echo -e "${BLUE}📚 Available Models${NC}"

    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        if docker compose exec ollama ollama list 2>/dev/null; then
            :
        elif docker compose exec ollama-cpu ollama list 2>/dev/null; then
            :
        else
            echo -e "${RED}❌ Could not list models${NC}"
        fi
    else
        echo -e "${RED}❌ Ollama service is not running${NC}"
    fi
}

pull_model() {
    local model=$1

    if [ -z "$model" ]; then
        echo -e "${RED}❌ Please specify a model to pull${NC}"
        echo "Example: $0 pull llama3.1:8b"
        exit 1
    fi

    echo -e "${YELLOW}📥 Pulling model: $model${NC}"

    if docker compose exec ollama ollama pull "$model" 2>/dev/null || \
       docker compose exec ollama-cpu ollama pull "$model" 2>/dev/null; then
        echo -e "${GREEN}✅ Successfully pulled: $model${NC}"
    else
        echo -e "${RED}❌ Failed to pull: $model${NC}"
    fi
}

clean_ollama() {
    echo -e "${YELLOW}🧹 Cleaning up Ollama data...${NC}"
    read -p "This will remove all downloaded models. Are you sure? (y/N): " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd "$PROJECT_DIR"
        docker compose down -v
        docker volume rm cursor_ollama_data 2>/dev/null || true
        echo -e "${GREEN}✅ Cleanup complete${NC}"
    else
        echo -e "${BLUE}ℹ️  Cleanup cancelled${NC}"
    fi
}

test_service() {
    echo -e "${BLUE}🧪 Testing Ollama service...${NC}"

    # Test API connection
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo -e "${GREEN}✅ API connection working${NC}"
    else
        echo -e "${RED}❌ API not responding${NC}"
        return 1
    fi

    # Test model generation
    echo -e "${YELLOW}🤖 Testing model generation...${NC}"

    # Try with the smallest model first
    models=("llama3.2:3b" "codellama:7b" "mistral:7b")

    for model in "${models[@]}"; do
        echo -e "${YELLOW}Testing $model...${NC}"

        result=$(docker compose exec ollama ollama run "$model" "Hello! Respond with just 'Working'" 2>/dev/null || \
                docker compose exec ollama-cpu ollama run "$model" "Hello! Respond with just 'Working'" 2>/dev/null || \
                echo "Failed")

        if [[ "$result" == *"Working"* ]] || [[ "$result" == *"working"* ]]; then
            echo -e "${GREEN}✅ $model is working correctly${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠️  $model response: $result${NC}"
        fi
    done

    echo -e "${RED}❌ No models responded correctly${NC}"
    return 1
}

# Main script logic
case "${1:-}" in
    start-gpu)
        check_docker
        start_ollama "gpu"
        ;;
    start-cpu)
        check_docker
        start_ollama "cpu"
        ;;
    setup)
        check_docker
        setup_models
        ;;
    stop)
        check_docker
        stop_ollama
        ;;
    restart)
        check_docker
        restart_ollama
        ;;
    status)
        check_docker
        show_status
        ;;
    logs)
        check_docker
        show_logs
        ;;
    models)
        check_docker
        list_models
        ;;
    pull)
        check_docker
        pull_model "$2"
        ;;
    clean)
        check_docker
        clean_ollama
        ;;
    test)
        check_docker
        test_service
        ;;
    "")
        print_usage
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        echo ""
        print_usage
        exit 1
        ;;
esac
