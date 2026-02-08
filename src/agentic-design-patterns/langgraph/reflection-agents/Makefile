.PHONY: up down client-up client-down server-up server-down venv

PID_DIR := .pids
CLIENT_PID := $(PID_DIR)/client.pid
SERVER_PID := $(PID_DIR)/server.pid
LOG_DIR := .logs
CLIENT_LOG := $(LOG_DIR)/client.log
SERVER_LOG := $(LOG_DIR)/server.log
VENV_DIR := .venv
UV_CACHE_DIR := .uv-cache

up: server-up client-up

down: client-down server-down

client-up: venv
	@mkdir -p $(PID_DIR) $(LOG_DIR)
	@if [ -f $(CLIENT_PID) ] && kill -0 $$(cat $(CLIENT_PID)) 2>/dev/null; then \
		echo "Client already running (pid $$(cat $(CLIENT_PID)))"; \
	else \
		UV_CACHE_DIR=$(UV_CACHE_DIR) API_BASE_URL=http://localhost:8000 uv run uvicorn client:app --host 0.0.0.0 --port 8001 >> $(CLIENT_LOG) 2>&1 & echo $$! > $(CLIENT_PID); \
		uv run python -c 'from rich.console import Console; from rich.panel import Panel; console=Console(); console.print(Panel("\n".join(["[bold cyan]Client running[/bold cyan]","[bold]UI:[/bold] http://localhost:8001","[bold]API:[/bold] http://localhost:8000","[bold]Docs:[/bold] http://localhost:8000/docs","[bold]Logs:[/bold] $(CLIENT_LOG)"]), title="Reflex Agent Client", border_style="cyan"))'; \
	fi

client-down:
	@if [ -f $(CLIENT_PID) ]; then \
		kill $$(cat $(CLIENT_PID)) 2>/dev/null || true; \
		rm -f $(CLIENT_PID); \
		echo "Client stopped"; \
	else \
		echo "Client not running"; \
	fi

server-up: venv
	@mkdir -p $(PID_DIR) $(LOG_DIR)
	@if [ -f $(SERVER_PID) ] && kill -0 $$(cat $(SERVER_PID)) 2>/dev/null; then \
		echo "Server already running (pid $$(cat $(SERVER_PID)))"; \
	else \
		UV_CACHE_DIR=$(UV_CACHE_DIR) uv run uvicorn app:app --host 0.0.0.0 --port 8000 >> $(SERVER_LOG) 2>&1 & echo $$! > $(SERVER_PID); \
		uv run python -c 'from rich.console import Console; from rich.panel import Panel; console=Console(); console.print(Panel("\n".join(["[bold green]Server running[/bold green]","[bold]API:[/bold] http://localhost:8000","[bold]Docs:[/bold] http://localhost:8000/docs","[bold]Redoc:[/bold] http://localhost:8000/redoc","[bold]Logs:[/bold] $(SERVER_LOG)"]), title="Reflex Agent API", border_style="green"))'; \
	fi

server-down:
	@if [ -f $(SERVER_PID) ]; then \
		kill $$(cat $(SERVER_PID)) 2>/dev/null || true; \
		rm -f $(SERVER_PID); \
		echo "Server stopped"; \
	else \
		echo "Server not running"; \
	fi

venv:
	@if [ ! -d $(VENV_DIR) ]; then \
		uv venv; \
	fi
	@UV_CACHE_DIR=$(UV_CACHE_DIR) uv sync
