"""Gradio RAG app over Huston-Tillotson professor reviews.

Retrieves the most relevant review chunks (embed.py), asks Groq's
llama-3.3-70b-versatile to answer using only those chunks, and shows the
answer alongside the source .txt files it drew from.
"""

import os

import gradio as gr
from dotenv import load_dotenv
from groq import Groq

from embed import retrieve

load_dotenv()

GROQ_MODEL = "llama-3.3-70b-versatile"
SYSTEM_PROMPT = (
    "Answer the question using only the information in the provided documents. "
    "If the documents don't contain enough information to answer, say I don't "
    "have enough information on that."
)

_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def answer_question(question):
    """Return (answer, sources) for a user question using retrieved context."""
    question = (question or "").strip()
    if not question:
        return "Please enter a question.", ""

    chunks = retrieve(question, top_k=4)
    if not chunks:
        return "I don't have enough information on that.", ""

    # Build the grounding context, labelling each chunk with its source file.
    context = "\n\n".join(
        f"[Source: {c['source']}]\n{c['text']}" for c in chunks
    )

    user_message = (
        f"Documents:\n{context}\n\n"
        f"Question: {question}"
    )

    response = _client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.2,
    )
    answer = response.choices[0].message.content

    # Source attribution: list the distinct .txt files used, in order.
    seen = []
    for c in chunks:
        if c["source"] not in seen:
            seen.append(c["source"])
    sources = "\n".join(f"- {name}" for name in seen)

    return answer, sources


def build_ui():
    with gr.Blocks(title="The Unofficial Guide — HT Professor Reviews") as demo:
        gr.Markdown(
            "# The Unofficial Guide\n"
            "Ask about professors at Huston-Tillotson University. "
            "Answers are grounded only in collected student reviews."
        )
        question = gr.Textbox(
            label="Your question",
            placeholder="e.g. What do students say about Antunez?",
        )
        ask_btn = gr.Button("Ask", variant="primary")
        answer = gr.Textbox(label="Answer", lines=6)
        sources = gr.Textbox(label="Sources (.txt files used)", lines=4)

        ask_btn.click(answer_question, inputs=question, outputs=[answer, sources])
        question.submit(answer_question, inputs=question, outputs=[answer, sources])

    return demo


if __name__ == "__main__":
    build_ui().launch(server_name="localhost", server_port=7860)
