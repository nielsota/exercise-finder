# RAG improvements (return full question text)

## What’s happening now (likely)

- Your vector store is built from raw PDFs in `data/questions/` (see `src/exercise_finder/vectordb/main.py`).
- `FileSearchTool(..., include_search_results=True)` feeds the model **search result chunks** from those PDFs (see `src/exercise_finder/agents/question.py`).
- Vector-store search results are typically *chunked excerpts* of the underlying file, not the full document, and a single question can easily span multiple chunks/pages.
- Your system prompt doesn’t require “verbatim full question” output, so the model often copies only the best-matching excerpt and returns a partial question.

Net: the model is doing what it can with partial evidence (a chunk), so you get partial questions.

---

## Highest-impact improvements (in order)

### 1) Index “question-sized” documents instead of whole PDFs

Goal: make “one retrieval result == one full question”.

Recommended pipeline:

1. Extract PDF text (and ideally structure: page numbers, line breaks, headings).
2. Split into individual questions (by patterns like `Vraag 1`, `Opgave`, numbering, or exam-specific delimiters).
3. Store each question as its own text document (e.g., `.md`, `.txt`, or JSONL records).
4. Attach rich metadata per question:
   - `exam_level`, `year`, `tijdvak` (you already have this via `Exam.from_file_path`)
   - `question_number` (and subparts like `a`, `b`, … if applicable)
   - `page_start`, `page_end`
   - `source_pdf_filename`

Why it works: retrieval no longer needs “context expansion” across chunks; the returned text already contains the entire question.

If you want to keep PDFs for provenance, index the extracted question text but keep pointers back to the PDF pages.

### 2) If you must keep PDFs: add context expansion across adjacent chunks

Goal: when a top hit is only part of a question, automatically fetch more surrounding text.

Approach options:

- Increase `max_num_results` and then **group results by file**; for the best file, concatenate multiple top chunks (and/or chunks with close offsets) until you reach an end marker (next question header) or a max character limit.
- Use a 2-step agent flow:
  1) “Locator” step: identify `source_pdf` + `page`/`question_number` from retrieved snippet(s).
  2) “Extractor” step: fetch the relevant page(s) (or pre-extracted per-page text) and return the full question verbatim.

This is less robust than question-sized indexing, but it can work without rebuilding your dataset format.

### 3) Make “return the entire question” an explicit contract

Update the question agent instructions to require:

- Return the question text **verbatim** and **complete**, including all subparts.
- If the retrieved content is incomplete, the agent must retrieve additional context (more hits / adjacent chunks) before answering.
- Include a “completion check” heuristic, e.g.:
  - If question ends mid-sentence, or contains dangling `a.` / `b.` markers, treat as incomplete.
  - If it references a figure/table but none is included, mark as possibly incomplete and fetch more context.

Also consider extending the output schema beyond:

- `question`: full text
- `exam`: metadata

Add (even if optional):

- `source`: `{file_name, pages, question_number}`
- `confidence`: `"high" | "medium" | "low"`
- `notes`: brief reason when incomplete

The schema nudges the model toward grounded, complete extraction rather than “best effort paraphrase”.

### 4) Improve retrieval quality (so the *right* question is found)

Once completeness is solved, these help match accuracy:

- Query rewriting: generate 3–5 query variants (keywords, Dutch/English synonyms, math terms) and union the results.
- Re-ranking: run a second-stage ranker (LLM or embedding similarity) over the top N retrieved candidates and pick the best.
- Metadata filtering: if users mention “VWO 2022 tijdvak 2”, apply filters so search happens within the right subset.
- Increase recall: raise `max_num_results` and then select final candidate(s) after re-ranking.

### 5) Make PDFs more searchable (if continuing with PDFs)

PDF retrieval quality depends heavily on text extraction:

- Ensure PDFs have embedded text (not scanned images). If scanned, run OCR first.
- Normalize layout artifacts (hyphenation, headers/footers, page numbers) before indexing.
- Preserve line breaks/indentation when it encodes structure (subparts a/b/c, given/asked, etc.).

---

## Practical debugging checklist (quick wins)

- Log what `FileSearchTool` actually returns (how many chunks, from which file, and the raw text excerpt).
- Check whether the returned excerpt contains the full question in the PDF; if not, it’s a chunking/adjacent-context issue.
- Try a “known question” query and see if results include multiple chunks from the same PDF—if yes, concatenation/context expansion is the simplest fix.
- Validate whether your PDFs are text-searchable; if the extracted text is garbled or missing, do OCR or extract via a better PDF parser.

---

## Suggested target behavior (definition of done)

For any user query:

1. Retrieve top candidates.
2. Select a single question “record” (ideally already question-sized).
3. Return full question text verbatim + exam metadata.
4. If confidence is low or extraction is incomplete, return a structured “needs more context” response (or trigger automatic expansion).

