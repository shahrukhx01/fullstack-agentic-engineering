import operator
import os
from pathlib import Path
from typing import Annotated, Any, AsyncGenerator, TypedDict

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.messages import (
    AIMessage,
    AnyMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langgraph.graph import END, START, StateGraph

from models import ChatMessage
from tools import orders, product_inquiry, returns, shipping

PROMPT_PATH = Path(__file__).with_name("prompt.md")


def _load_system_prompt() -> str:
    try:
        return PROMPT_PATH.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return "You are a helpful assistant tasked with performing arithmetic on a set of inputs."


SYSTEM_PROMPT = _load_system_prompt()


load_dotenv()

BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")

if not BASE_URL or not API_KEY or not MODEL_NAME:
    raise RuntimeError("Missing BASE_URL, API_KEY, or MODEL_NAME in environment.")

if BASE_URL.endswith("/chat/completions"):
    BASE_URL = BASE_URL[: -len("/chat/completions")]

model = init_chat_model(
    MODEL_NAME,
    temperature=0,
    base_url=BASE_URL,
    api_key=API_KEY,
    model_provider="openai",
    streaming=True,
)


TOOLS = [orders, returns, product_inquiry, shipping]
TOOLS_BY_NAME = {tool.name: tool for tool in TOOLS}
MODEL_WITH_TOOLS = model.bind_tools(TOOLS)


class MessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    llm_calls: int


def llm_call(state: dict):
    """LLM decides whether to call a tool or not."""

    return {
        "messages": [
            MODEL_WITH_TOOLS.invoke(
                [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
            )
        ],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


def tool_node(state: dict):
    """Performs the tool call."""

    result = []
    last_message = state["messages"][-1]
    if not isinstance(last_message, AIMessage) or not last_message.tool_calls:
        return {"messages": result}
    for tool_call in last_message.tool_calls:
        tool = TOOLS_BY_NAME[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])
        result.append(
            ToolMessage(content=str(observation), tool_call_id=tool_call["id"])
        )
    return {"messages": result}


def build_agent():
    agent_builder = StateGraph(MessagesState)  # type: ignore
    agent_builder.add_node("llm_call", llm_call)
    agent_builder.add_node("llm_result", llm_call)
    agent_builder.add_node("tool_node", tool_node)
    agent_builder.add_edge(START, "llm_call")
    agent_builder.add_edge("llm_call", "tool_node")
    agent_builder.add_edge("tool_node", "llm_result")
    agent_builder.add_edge("llm_result", END)
    return agent_builder.compile()


AGENT = build_agent()


def _to_lc_messages(messages: list[ChatMessage]) -> list[AnyMessage]:
    lc_messages: list[AnyMessage] = []
    for msg in messages:
        if msg.role == "user":
            lc_messages.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            lc_messages.append(AIMessage(content=msg.content))
        elif msg.role == "system":
            lc_messages.append(SystemMessage(content=msg.content))
        elif msg.role == "tool":
            lc_messages.append(
                ToolMessage(content=msg.content, tool_call_id=msg.name or "tool")
            )
    return lc_messages


def _content_to_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    return str(content)


def _from_lc_messages(messages: list[AnyMessage]) -> list[ChatMessage]:
    converted: list[ChatMessage] = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            converted.append(
                ChatMessage(role="user", content=_content_to_text(msg.content))
            )
        elif isinstance(msg, AIMessage):
            converted.append(
                ChatMessage(role="assistant", content=_content_to_text(msg.content))
            )
        elif isinstance(msg, SystemMessage):
            converted.append(
                ChatMessage(role="system", content=_content_to_text(msg.content))
            )
        elif isinstance(msg, ToolMessage):
            converted.append(
                ChatMessage(
                    role="tool",
                    content=_content_to_text(msg.content),
                    name=getattr(msg, "tool_call_id", None),
                )
            )
    return converted


def run_agent(
    messages: list[ChatMessage], llm_calls: int
) -> tuple[list[ChatMessage], int]:
    lc_messages = _to_lc_messages(messages)
    result = AGENT.invoke({"messages": lc_messages, "llm_calls": llm_calls})
    updated_messages = _from_lc_messages(result["messages"])
    return updated_messages, result.get("llm_calls", llm_calls)


async def stream_agent(
    messages: list[ChatMessage], llm_calls: int
) -> AsyncGenerator[tuple[str | None, list[ChatMessage] | None, int | None], None]:
    lc_messages = _to_lc_messages(messages)
    last_state: dict[str, Any] = {"messages": lc_messages, "llm_calls": llm_calls}

    async for mode, chunk in AGENT.astream(
        {"messages": lc_messages, "llm_calls": llm_calls},
        stream_mode=["messages", "values"],
    ):
        if mode == "messages":
            message_chunk, _metadata = chunk
            content = getattr(message_chunk, "content", None)
            if content:
                yield str(content), None, None
        elif mode == "values":
            if isinstance(chunk, dict) and "messages" in chunk:
                last_state = chunk

    updated_messages = _from_lc_messages(last_state.get("messages", []))
    updated_llm_calls = last_state.get("llm_calls", llm_calls)
    yield None, updated_messages, updated_llm_calls
