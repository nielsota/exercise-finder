# Exercise Finder (MathWizard)

Quick command reference using the `mw` CLI.

## Workflow Steps

### 1. Extract questions from exam images

Parse exam images and compile to JSONL:

```bash
uv run mw extract from-images --exam-dir data/questions-images/VW-1025-a-18-1-o
uv run mw extract from-images --exam-dir data/questions-images/VW-1025-a-18-2-o
uv run mw extract from-images --exam-dir data/questions-images/VW-1025-a-19-1-o
```

This writes to `data/questions-extracted/` by default.

### 2. Create and populate vector store

**Create vector store (do once):**
```bash
uv run mw vectorstore create --name examstore24122025
```

Note the returned vector store ID (e.g., `vs_694b9b4403e881918fd7b5c04a301771`)

**Add extracted questions to vector store:**
```bash
uv run mw vectorstore add 
```

Processes all JSONL files in `data/questions-extracted/` by default.

### 3. Query and use

**CLI search:**
```bash
uv run mw vectorstore fetch --vector-store-id <INSERT_ID> --query "parametric equations" --exam-dir data/questions-images/VW-1025-a-18-1-o
```

**Web UI (recommended):**
```bash
uv run mw ui start --vector-store-id <INSERT_ID> --exams-root data/questions-images
```

Access at http://localhost:8000 for interactive search with image display.
