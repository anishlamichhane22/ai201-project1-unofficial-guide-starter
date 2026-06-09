# Demo Video Script — The Unofficial Guide

**Target length:** 3–5 minutes. Record screen + microphone.
**Before you start:** activate the venv and launch the app, then wait for the
`Running on local URL: http://localhost:7860` line (takes ~60s — it's loading
the model, not frozen). Open http://localhost:7860 in your browser.

```powershell
.\.venv\Scripts\activate
python app.py
```

**Recording tool:** Windows Game Bar (`Win + Alt + R` to start/stop, saves to
`Videos\Captures`) — make sure the mic is on. Or OBS / Loom.

**Rubric requirements this script covers:**
1. ✅ At least 3 different queries with source citations visible
2. ✅ One query where retrieval works well (narrate why)
3. ✅ One query where the system struggles/fails (narrate what went wrong)
4. ✅ Walkthrough of the evaluation report

---

## [0:00–0:30] Intro

> "This is The Unofficial Guide, a Retrieval-Augmented Generation system over
> student reviews of professors at Huston-Tillotson University. You ask a
> plain-language question, it retrieves the most relevant review chunks from a
> ChromaDB vector store, and answers using only those chunks — with the source
> files cited every time."

---

## [0:30–1:15] Query 1 — good retrieval

**Type:** `Is Tirado-Ramos good for beginners in web programming?`

> "The answer says yes — he starts from the basics and it's good for beginners.
> The Sources box shows it pulled from prof_tirado.txt, the correct file.
> Retrieval worked well here because the query's intent — 'beginners' —
> semantically matched phrasing like 'starts from scratch, anyone can follow
> along,' even though the query shares no exact keywords with the review."

---

## [1:15–2:00] Query 2 — another working query

**Type:** `What do students say about the Freshman Seminar?`

> "It correctly summarizes that the Freshman Seminar is helpful for new students
> — clubs, events, campus life — and cites prof_rodriguez.txt as the source."

---

## [2:00–2:50] Query 3 — the failure case (most important)

**Type:** `How difficult are Dr. Primo's exams?`

> "The answer is correct — the exams are very hard and you need to study a lot.
> But look at the Sources: it lists prof_primo.txt PLUS prof_antunez.txt and
> prof_pena.txt, which aren't about Dr. Primo. This is my documented failure
> case. Retrieval uses a fixed top_k of 4 with no relevance threshold, and since
> each professor only has about 3–4 short chunks, the 4-chunk window is forced
> to pull in off-target files. The LLM correctly ignored them in the answer, but
> they still show up in the source attribution. The fix would be a distance
> cutoff so weak matches are dropped before listing sources."

---

## [2:50–3:20] Out-of-scope refusal

**Type:** `Which dining hall has the best food on campus?`

> "There are no dining documents in the corpus, so the system correctly refuses:
> 'I don't have enough information on that.' That's the grounding instruction in
> the system prompt working — it won't make something up from the model's
> general knowledge."

---

## [3:20–4:00] Evaluation report walkthrough

Switch to the README (in your editor or on GitHub) and scroll to the
**Evaluation Report** and **Failure Case Analysis** sections.

> "Here's my evaluation report. All 5 test questions came back accurate, but I
> rated retrieval as only partially relevant — because of the top_k issue I just
> showed live, off-target files appear in the source list. The Failure Case
> Analysis explains the root cause, ties it to the retrieval stage, and
> describes the fix. That honest limitation is the most important thing I
> learned building this."

---

## Tips
- Keep it 3–5 minutes. Practice the Query 3 failure explanation once.
- Make sure the **Sources box is visible** for every query — graders check for
  citations.
- Narrate meaning, not navigation. Don't say "now I click Ask"; say what the
  result shows and why.
