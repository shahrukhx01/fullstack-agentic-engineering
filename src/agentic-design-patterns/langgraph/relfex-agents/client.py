import json
import os
from typing import Any, cast

from dotenv import load_dotenv
from fasthtml.common import (
    Body,
    Button,
    Div,
    FastHTML,
    Form,
    Head,
    Html,
    Input,
    Script,
    Style,
    Title,
)

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

app: Any = cast(Any, FastHTML())


@app.get("/")  # type: ignore[attr-defined]
def index():
    return Html(
        Head(
            Title("Reflex Agent Chat"),
            Script(
                src="https://cdn.jsdelivr.net/npm/markdown-it@14.1.0/dist/markdown-it.min.js"
            ),
            Style("""
                body { font-family: "IBM Plex Sans", sans-serif; margin: 0; background: #f7f5f2; }
                .wrap { max-width: 880px; margin: 40px auto; padding: 24px; }
                .card { background: #ffffff; border-radius: 16px; padding: 24px; box-shadow: 0 18px 40px rgba(0,0,0,0.08); }
                .messages { display: flex; flex-direction: column; gap: 12px; min-height: 240px; }
                .msg { padding: 12px 16px; border-radius: 12px; max-width: 80%; }
                .user { align-self: flex-end; background: #2b2b2b; color: #fff; }
                .assistant { align-self: flex-start; background: #efeae1; color: #1e1e1e; }
                .input-row { display: flex; gap: 12px; margin-top: 16px; }
                .input-row input { flex: 1; padding: 12px 14px; border-radius: 10px; border: 1px solid #d2cbc2; }
                .input-row button { padding: 12px 18px; border-radius: 10px; border: none; background: #0f766e; color: #fff; }
                """),
        ),
        Body(
            Div(
                Div(
                    Div("Reflex Agent (LangGraph)", cls="title"),
                    Div(id="messages", cls="messages"),
                    Form(
                        Div(
                            Input(
                                type="text", id="input", placeholder="Ask something..."
                            ),
                            Button("Send", type="submit"),
                            cls="input-row",
                        ),
                        id="chat-form",
                    ),
                    cls="card",
                ),
                cls="wrap",
            ),
            Script(
                """
                const messages = document.getElementById("messages");
                const form = document.getElementById("chat-form");
                const input = document.getElementById("input");
                let sessionId = null;
                const apiBaseUrl = __API_BASE_URL__;
                const md = window.markdownit();
                const tokenDelayMs = 30;

                function addMessage(role, text) {
                  const div = document.createElement("div");
                  div.className = `msg ${role}`;
                  div.innerHTML = md.render(text);
                  messages.appendChild(div);
                  messages.scrollTop = messages.scrollHeight;
                  return div;
                }

                async function streamResponse(userText) {
                  const assistantNode = addMessage("assistant", "");
                  const response = await fetch(`${apiBaseUrl}/api/v1/agent/stream`, {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({
                      session_id: sessionId,
                      messages: [{role: "user", content: userText}]
                    })
                  });

                  const reader = response.body.getReader();
                  const decoder = new TextDecoder();
                  let buffer = "";

                  while (true) {
                    const {value, done} = await reader.read();
                    if (done) break;
                    buffer += decoder.decode(value, {stream: true});
                    let lines = buffer.split("\\n");
                    buffer = lines.pop();
                    for (const line of lines) {
                      if (!line.trim()) continue;
                      const event = JSON.parse(line);
                      if (event.type === "session") sessionId = event.session_id;
                      if (event.type === "token") {
                        assistantNode.textContent += (assistantNode.textContent ? " " : "") + event.content;
                        assistantNode.innerHTML = md.render(assistantNode.textContent);
                        await new Promise(resolve => setTimeout(resolve, tokenDelayMs));
                      }
                    }
                  }
                }

                form.addEventListener("submit", async (event) => {
                  event.preventDefault();
                  const text = input.value.trim();
                  if (!text) return;
                  addMessage("user", text);
                  input.value = "";
                  await streamResponse(text);
                });
                """.replace("__API_BASE_URL__", json.dumps(API_BASE_URL)),
            ),
        ),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
