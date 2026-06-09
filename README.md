# The Unofficial Guide — Project 1

A retrieval-augmented generation (RAG) system over student reviews of
professors at Huston-Tillotson University. Ask a question, and the system
retrieves the most relevant review chunks, then answers using only those
chunks via Groq's `llama-3.3-70b-versatile`.

---

## Domain

Student reviews of professors at Huston-Tillotson University (an HBCU in
Austin, TX). This knowledge is valuable because the official course catalog
only lists course descriptions and prerequisites — it says nothing about
teaching style, exam difficulty, grading fairness, or workload. Students
normally rely on word-of-mouth to decide which professors to take, but that
knowledge is scattered, informal, and hard for incoming students to find. This
system consolidates it into one queryable place.

---

## Document Sources

All documents are short student reviews collected as `.txt` files in the
`data/` folder. Each file contains two reviews for the same professor and
includes the professor name, course code, a numeric rating, and free-text
review.

| #  | Source         | Type            | URL or file path        |
|----|----------------|-----------------|-------------------------|
| 1  | Student review | Programming Foundations — Jose Mauricio Antunez | data/prof_antunez.txt |
| 2  | Student review | Java Programming — Dr. Abina Primo              | data/prof_primo.txt   |
| 3  | Student review | Intro to Web Programming — Alfredo Tirado-Ramos | data/prof_tirado.txt  |
| 4  | Student review | Health & Wellness — James Kraft                 | data/prof_kraft.txt   |
| 5  | Student review | Elementary French I — Anne Cirella-Urrutia      | data/prof_cirella.txt |
| 6  | Student review | US History — Ethan Pena                         | data/prof_pena.txt    |
| 7  | Student review | Freshman Seminar — Zoe Rodriguez                | data/prof_rodriguez.txt |
| 8  | Student review | Calculus I — Dr. Farzana Hussain                | data/prof_hussain.txt |
| 9  | Student review | Physics — Engin Topkara                         | data/prof_topkara.txt |
| 10 | Student review | English Composition — Alana King                | data/prof_king.txt    |

---

## Chunking Strategy

Preprocessing happens in `ingest.py`: each `.txt` file is read as UTF-8, then
`clean_text()` strips leading/trailing whitespace from every line and drops
blank lines, so empty lines between the two reviews don't become noise in a
chunk. `chunk_text()` then performs a fixed-size character split with a sliding
window.

**Chunk size:** 200 characters

**Overlap:** 20 characters (step = 180 characters)

**Why these choices fit your documents:** The documents are very short student
reviews — each review is only 3–5 sentences. A small 200-character chunk keeps
each chunk focused on roughly one idea (e.g. exam difficulty, or teaching
style) instead of blending unrelated points. The 20-character overlap carries a
few words across each boundary so a sentence that gets split — for example
"…makes them easy / to understand…" — still has enough shared context to be
retrievable from either side.

**Final chunk count:** 38 chunks across the 10 documents (verified by running
`python ingest.py`).

---

## Sample Chunks

Five representative chunks produced by `python ingest.py`, each labeled with
its source document. They show both the strengths and a known weakness of the
fixed-size character split (see Failure Case Analysis): chunk #3 is a short
fragment, and chunks #1–#2 carry a few leftover characters from the sliding
window where a word was cut at the 200-character boundary.

1. **[prof_antunez.txt #0]** — "Professor: Jose Mauricio Antunez / Course:
   Programming Foundations (COSC-1312-1) / Rating: 5/5 / Review: Great
   professor. I really liked the way he teaches — he explains concepts clearly
   and makes them easy"
2. **[prof_antunez.txt #1]** — "and makes them easy to understand. Exams and
   assignments were fair and well structured. Took away a lot from this course
   and learned a lot about programming. Would highly recommend. Professor: Jose
   M"
3. **[prof_antunez.txt #2]** — "d. Professor: Jose Mauricio Antunez / Course:
   Programming Foundations (COSC-1312-1) / Rating: 5/5 / Review: One of the best
   professors at HT for CS. Very patient and makes sure every student
   understands bef"
4. **[prof_antunez.txt #3]** — "dent understands before moving on. Would take
   again."
5. **[prof_cirella.txt #0]** — "Professor: Anne V. Cirella-Urrutia / Course:
   Elementary French I (FREN-1311-2) / Rating: 5/5 / Review: Amazing French
   class. It was not just about learning the language but also about French
   culture which m"

Each chunk keeps its source professor and course code at the top, so even a
mid-review chunk stays attributable to the right document.

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` via the `sentence-transformers` library,
running locally. Chunks are embedded once at import time in `embed.py` and
stored in an in-memory ChromaDB collection; retrieval uses cosine/L2 distance
over the query embedding with `top_k = 4`.

**Production tradeoff reflection:** `all-MiniLM-L6-v2` is fast, free, and runs
locally with no API key, which is ideal for a small project like this. If I
were deploying for real users and cost weren't a constraint, I'd weigh a few
tradeoffs. (1) **Accuracy** — a larger hosted model such as OpenAI's
`text-embedding-3-small/large` generally produces stronger semantic separation,
which would help with the near-duplicate-phrasing problem these short reviews
have (many reviews say "great professor, explains clearly"). (2) **Multilingual
support** — MiniLM is English-centric; if HT's student body needed Spanish or
French support, a multilingual model would matter. (3) **Context length** — not
a concern here since chunks are tiny, but it would matter for longer documents.
(4) **Latency / local vs. hosted** — the local model avoids API round-trips,
but a hosted model adds network latency and a per-call cost that scales with
traffic. For this domain the accuracy gain is the main reason I'd switch.

---

## Retrieval Test Results

Three evaluation queries were run through `retrieve(query, top_k=4)` in
`embed.py`. In every case the **top-ranked chunk came from the correct
professor's review file**; off-target files (e.g. `prof_king.txt`) only appeared
in the lower-ranked slots, which is the fixed-`top_k` behavior discussed in the
Failure Case Analysis.

**Query 1 — "What do students say about Antunez's teaching style?"**
Top retrieved chunk (`prof_antunez.txt`): *"Great professor. I really liked the
way he teaches — he explains concepts clearly and makes them easy [to
understand]…"*
*Why relevant:* The query never uses the words in the review, yet semantic
search matches "teaching style" to text describing **how** he teaches (explains
clearly, patient, students understand before moving on). This is exactly the
strength of embedding-based retrieval over keyword search.

**Query 2 — "How difficult are Dr. Primo's exams?"**
Top retrieved chunk (`prof_primo.txt`): *"Exams are very hard and challenging.
She is a good teacher but be prepared to study a lot…"*
*Why relevant:* The chunk directly addresses exam difficulty for the exact
professor named in the query — both the professor entity and the "difficulty"
concept match.

**Query 3 — "Is Tirado-Ramos good for beginners in web programming?"**
Top retrieved chunk (`prof_tirado.txt`): *"Great professor for beginners. Starts
from scratch so anyone can follow along… Good introduction to web development."*
*Why relevant:* The query's intent (suitability for beginners) maps onto
"beginners / starts from scratch / anyone can follow along," and the course
context (web programming) matches the chunk's domain.

---

## Grounded Generation

**System prompt grounding instruction:** The system prompt in `app.py` is:

> "Answer the question using only the information in the provided documents. If
> the documents don't contain enough information to answer, say I don't have
> enough information on that."

Beyond the instruction, grounding is enforced structurally:

- The user message is built as `Documents:\n{context}\n\nQuestion: {question}`,
  so the only knowledge the model sees is the retrieved chunks.
- Each chunk is prefixed with a `[Source: <filename>]` label before being
  joined, so the model is told which file every piece of context came from.
- If retrieval returns nothing, `answer_question()` short-circuits and returns
  "I don't have enough information on that." without ever calling the LLM.
- Generation runs at `temperature=0.2` to keep the model close to the source
  text rather than improvising.

**How source attribution is surfaced in the response:** After generation, the
app collects the distinct source filenames from the retrieved chunks (in order,
de-duplicated) and displays them in a separate "Sources (.txt files used)"
textbox in the Gradio UI, so the user can see exactly which review files the
answer was drawn from.

---

## Example Responses

Two in-scope responses (with source attribution visible) and one out-of-scope
query, captured from the live system.

**In-scope #1**
Question: *"What do students say about Antunez's teaching style?"*
Answer: *"Students say Professor Antunez explains concepts clearly and makes
them easy to understand, is very patient, and ensures every student understands
before moving on. His exams and assignments are described as fair and
well-structured, and students highly recommend him."*
Sources: `prof_antunez.txt`, `prof_king.txt`

**In-scope #2**
Question: *"How difficult are Dr. Primo's exams?"*
Answer: *"Dr. Primo's exams are really difficult, very hard and challenging
according to the reviews. Students are advised to be prepared to study a lot."*
Sources: `prof_primo.txt`, `prof_antunez.txt`, `prof_pena.txt`

**Out-of-scope (refusal)**
Question: *"Which dining hall has the best food on campus?"*
Answer: *"I don't have enough information on that."*
The corpus contains only professor reviews — no dining content — so the
grounding instruction in the system prompt (which tells the model to say exactly
this when the documents don't cover the question) forces a refusal instead of a
guessed answer from the model's general knowledge.

---

## Query Interface

The interface is a **Gradio web app** (`app.py`), launched with `python app.py`
and served at `http://localhost:7860`.

**Input field:**
- *Your question* — a single textbox where the user types a plain-language
  question. Submitting (Enter) or clicking **Ask** triggers the query.

**Output fields:**
- *Answer* — a multi-line textbox showing the grounded LLM answer.
- *Sources (.txt files used)* — a multi-line textbox listing the distinct review
  files the answer drew from.

**Sample interaction transcript:**
```
Your question:  What do students say about the Freshman Seminar?

Answer:         Students say the Freshman Seminar (UNIV-1102-8) with Professor
                Zoe Rodriguez is "really helpful" and a "must for all freshmen."
                They learned about the university, clubs, events, resources, and
                campus life, and describe the professor as very welcoming. Rated
                5/5.

Sources:        - prof_rodriguez.txt
                - prof_hussain.txt
```

---

## Evaluation Report

The five planning-doc questions were run through the live system
(`answer_question()`). Responses below are summarized; sources are the files
the retriever returned.

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What do students say about Antunez's teaching style? | Explains concepts clearly, patient, fair exams, highly recommended | Says he explains concepts clearly and is easy to understand, very patient, ensures students understand before moving on, fair/well-structured exams, highly recommended. Sources: prof_antunez.txt, prof_king.txt | Partially relevant (correct file + 1 off-target) | Accurate |
| 2 | How difficult are Dr. Primo's exams? | Exams are very tough; you must study a lot | Exams are really difficult, very hard and challenging; be prepared to study a lot. Sources: prof_primo.txt, prof_antunez.txt, prof_pena.txt | Partially relevant (correct file + 2 off-target) | Accurate |
| 3 | Is Tirado-Ramos good for beginners in web programming? | Yes — starts from the basics, good for beginners | Yes; starts from the basics, explains clearly, approachable for anyone starting web dev. Sources: prof_tirado.txt, prof_primo.txt | Partially relevant (correct file + 1 off-target) | Accurate |
| 4 | What is Dr. Hussain's Calculus class like? | Great professor, thorough, keeps students informed about campus events | Calculus is tough but she makes it manageable, thorough and patient, ensures understanding, keeps students informed about campus events; rated 4/5. Sources: prof_hussain.txt, prof_king.txt | Partially relevant (correct file + 1 off-target) | Accurate |
| 5 | What do students say about the Freshman Seminar? | Very helpful, teaches campus life, clubs, events | "Really helpful," a "must for all freshmen," teaches about clubs/events/resources/campus life, professor is welcoming; rated 5/5. Sources: prof_rodriguez.txt, prof_hussain.txt | Partially relevant (correct file + 1 off-target) | Accurate |

**Retrieval quality:** Partially relevant — the correct professor's file ranked
first in every case, but because `top_k` is fixed at 4 with no relevance
filter, off-target files appear in the source list (see Failure Case below).

**Response accuracy:** Accurate — for all five questions the generated answer
matched the expected content and stayed grounded in the reviews. The model did
not pull in details from the off-target chunks, which suggests it ignored the
weakly-related context.

---

## Failure Case Analysis

**Question that failed:** "What do students say about Antunez's teaching style?"
(and the same pattern appears on Q2, Q4, and Q5).

**What the system returned:** The *answer text* was correct, but the **Sources**
panel listed `prof_king.txt` alongside the correct `prof_antunez.txt`. On Q2 it
listed both `prof_antunez.txt` and `prof_pena.txt` as sources for a question
that is only about Dr. Primo.

**Root cause (tied to a specific pipeline stage):** This is a **retrieval +
attribution** problem, not a generation problem. `retrieve()` in `embed.py`
always returns exactly `top_k = 4` chunks and there is **no distance / relevance
threshold**. The reviews are short and use very similar language ("great
professor," "explains clearly," "highly recommend"), so several unrelated
professors' chunks land close in embedding space. Since the relevant professor
only has ~3–4 chunks total, the 4-chunk window is forced to include at least one
chunk from a different file. `answer_question()` then lists the source file of
*every* returned chunk, so an off-target file shows up in the attribution even
though the LLM (correctly) didn't use it.

**What you would change to fix it:** Add a relevance cutoff in `retrieve()` —
drop any chunk whose distance exceeds a threshold before returning — and/or
only list a file in the Sources panel if at least one of its chunks falls under
that threshold. A complementary fix is to embed at the whole-review level (or
prepend the professor name to every chunk) so that short, similarly-worded
reviews separate more cleanly in embedding space.

---

## Spec Reflection

**One way the spec helped you during implementation:** The planning doc forced
me to commit to concrete chunking parameters (200 chars / 20 overlap) *and a
justification* before writing `chunk_text()`. Because I had already reasoned
that the documents were short 3–5 sentence reviews, I didn't waste time
experimenting with large 500–1000 character chunks that would have merged
unrelated reviews together. The pre-written evaluation questions also gave me a
ready-made test harness — I ran exactly those five questions to validate the
end-to-end pipeline instead of inventing tests after the fact.

**One way your implementation diverged from the spec, and why:** The plan only
described retrieval and never named a generation model; in the actual build I
added Groq's `llama-3.3-70b-versatile` for answer synthesis plus a Gradio UI,
which the plan didn't specify. I also discovered during evaluation that the
fixed `top_k = 4` retrieval the plan assumed produces off-target sources for
these very short documents — a real behavior the plan's "weak embeddings" and
"missing context at chunk boundaries" risks only partly anticipated. That
divergence is documented in the Failure Case Analysis above rather than silently
"fixed," since the grounded answers themselves remained accurate.

---

## AI Usage

**Instance 1**

- *What I gave the AI:* The Chunking Strategy section from `planning.md`
  (200-character chunks, 20-character overlap, short-review rationale) and asked
  it to implement `chunk_text()` and `load_and_chunk_documents()` in
  `ingest.py`.
- *What it produced:* A sliding-window character splitter with a `step =
  chunk_size - overlap` loop, plus a loader that cleans whitespace and emits
  `{source, chunk_index, text}` dicts.
- *What I changed or overrode:* I kept the 200/20 sizing from my plan rather
  than a larger default, and confirmed the chunk count (38) by running
  `python ingest.py` before trusting it. I also verified the cleaning step
  dropped blank lines so the two reviews per file didn't bleed together.

**Instance 2**

- *What I gave the AI:* The five evaluation questions and the live system
  output, and asked it to assess retrieval quality honestly.
- *What it produced:* An evaluation table that initially rated everything
  "Relevant / Accurate."
- *What I changed or overrode:* I overrode the retrieval rating to "Partially
  relevant" after noticing the Sources panel listed off-target files
  (`prof_king.txt`, `prof_pena.txt`). That observation became the Failure Case
  Analysis, which traces the issue to the fixed `top_k = 4` with no relevance
  threshold rather than to the LLM — a distinction the first draft glossed over.
