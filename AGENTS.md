# Project Structure

Fullstack agentic engineering is a comprehensive collection of Agentic AI project implementation encompassing various agentic design patterns, observability tools, multi-agent systems etc. Each recipe is self-contained with its own README.md and virtual environment. For package management `uv` python's package manager is used throughout the project.

# Codebase Guidelines

For each agentic recipe implementation, FastAPI framework is used to serve the agent at server-side. For client-side, we FastHTML framework is used for UI creation for streaming chat clients. Make the the generated FastAPI app is compact and following files each time:

- app.py -> For main FastAPI and endpoint serving. Ensure for each new request a new session identifier is assigned and then the client should use the assigned session identifier for subsequent messages. Furthermore, the server should main in-memory store of all user sessions, model this also in models.py and init this on webserver startup. Also, the main endpoint for this will be `api/v1/agent/stream`.
- models.py -> For request and response models
- agent.py -> Implements the main agentic design pattern discussed in the context of one specific agentic framework i.e. langgraph, autogen etc.
- client.py -> For connecting to agent endpoints using the FastHTML UI supporting token streaming for chat.
- prompt.md -> Detailed system prompt for the agent, details the role, actions, guidlines and task specifications for the agent.
- pyproject.toml -> Always use python version >= 3.13 and add a one-liner description based on the current agentic recipe.
- Makefile -> Always create `Makefile` for spinning-up both client and server at the same time and shutting them down together. So overall, add options:
    - make up (spins up both client and server)
    - make down (spins down both client and server)
    - make client-up (spins up client)
    - make client-down (spins down client)
    - make server-up (spins up  server)
    - make server-down (spins down server)


# Pre-commit 
Always setup the following pre-commit hooks when setting a new agentic recipe.
- ruff linter
- ty type checker
- isort formatter
- black formatter
