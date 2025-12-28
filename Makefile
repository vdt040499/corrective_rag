# Makefile for RAG Project

.PHONY: help install dev test clean run-api run-cli demo format lint

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	uv sync

dev:  ## Install development dependencies
	uv add --dev pytest black flake8 mypy

test:  ## Run tests
	uv run pytest tests/ -v

clean:  ## Clean up generated files
	rm -rf chroma_db/
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +

run-api:  ## Start the FastAPI server
	uv run python main.py

run-cli:  ## Show CLI help
	uv run python cli.py --help

demo:  ## Run the demo script
	uv run python examples/demo.py

demo-openai:  ## Run the OpenAI embeddings demo
	uv run python examples/demo_openai.py

format:  ## Format code with black
	uv run black src/ tests/ examples/ *.py

lint:  ## Lint code with flake8
	uv run flake8 src/ tests/ examples/ *.py

type-check:  ## Type check with mypy
	uv run mypy src/

status:  ## Check system status
	uv run python cli.py status

interactive:  ## Start interactive mode
	uv run python cli.py interactive

reset:  ## Reset vector store
	uv run python cli.py reset

# Example commands
add-samples:  ## Add sample documents
	uv run python cli.py add-directory examples/sample_documents

query-sample:  ## Run a sample query
	uv run python cli.py query "What is Python used for?"