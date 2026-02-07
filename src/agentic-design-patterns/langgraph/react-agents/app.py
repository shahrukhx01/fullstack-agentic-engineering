import json
import logging
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from agent import stream_agent
from models import AgentStreamEvent, AgentStreamRequest, ChatMessage, SessionState

logger = logging.getLogger("react-agents")
logging.basicConfig(level=logging.INFO)


class SessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, SessionState] = {}

    def create(self) -> SessionState:
        session_id = str(uuid.uuid4())
        session = SessionState(session_id=session_id)
        self._sessions[session_id] = session
        return session

    def get(self, session_id: str) -> SessionState | None:
        return self._sessions.get(session_id)

    def upsert(self, session: SessionState) -> None:
        session.updated_at = datetime.now(timezone.utc).isoformat()
        self._sessions[session.session_id] = session


def create_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.sessions = SessionStore()
        yield

    app = FastAPI(lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,  # type: ignore
        allow_origins=[
            "http://127.0.0.1:8001",
            "http://localhost:8001",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.post("/api/v1/agent/stream")
    async def agent_stream(payload: AgentStreamRequest) -> StreamingResponse:
        store: SessionStore = app.state.sessions
        session = store.get(payload.session_id) if payload.session_id else None
        if session is None:
            session = store.create()

        session.messages.extend(payload.messages)
        store.upsert(session)

        async def event_stream() -> AsyncGenerator[bytes, None]:
            yield _encode_event(
                AgentStreamEvent(
                    type="session",
                    session_id=session.session_id,
                    created_at=session.created_at,
                )
            )

            try:
                updated_messages: list[ChatMessage] | None = None
                updated_llm_calls: int | None = None
                async for token, messages, llm_calls in stream_agent(
                    session.messages, session.llm_calls
                ):
                    if token:
                        yield _encode_event(
                            AgentStreamEvent(
                                type="token",
                                session_id=session.session_id,
                                content=token,
                            )
                        )
                    if messages is not None:
                        updated_messages = messages
                        updated_llm_calls = llm_calls

                if updated_messages is not None:
                    session.messages = updated_messages
                if updated_llm_calls is not None:
                    session.llm_calls = updated_llm_calls
                store.upsert(session)

                yield _encode_event(
                    AgentStreamEvent(
                        type="final",
                        session_id=session.session_id,
                        llm_calls=session.llm_calls,
                    )
                )
            except Exception as exc:  # pragma: no cover - stream error path
                yield _encode_event(
                    AgentStreamEvent(
                        type="error",
                        session_id=session.session_id,
                        content=str(exc),
                    )
                )

        return StreamingResponse(event_stream(), media_type="application/x-ndjson")

    return app


def _encode_event(event: AgentStreamEvent) -> bytes:
    payload = event.model_dump(exclude_none=True)
    return (json.dumps(payload) + "\n").encode("utf-8")


app = create_app()
