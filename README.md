Steps

1. For each exam, parse the exam images and compile JSONL
    - uv run exercise-finder images-to-questions --exam-dir data/questions-images/VW-1025-a-18-1-o
    - uv run exercise-finder images-to-questions --exam-dir data/questions-images/VW-1025-a-18-2-o
    - uv run exercise-finder images-to-questions --exam-dir data/questions-images/VW-1025-a-19-1-o 

This will write to the data/questions-extracted directory by default 

1. For each JSONL in data/questions-extracted/

    **Do once**: 
        - uv run exercise-finder vectorstore-create --name examstore24122025

        fetch id from here: vs_694b9b4403e881918fd7b5c04a301771

    **Then let run over directory (default: questions-extracted):**
        - uv run exercise-finder vectorstore-add --vector-store-id vs_694b9b4403e881918fd7b5c04a301771

2. Now can try to fetch a few questions:
    **CLI fetch (prints JSON with image paths)**
    
    - uv run exercise-finder vectorstore-fetch --vector-store-id <INSERT_ID> --query "parametric equations" --exam-dir data/questions-images/VW-1025-a-18-1-o

    **Web UI (works across all exams)**
    - uv run exercise-finder ui --vector-store-id <INSERT_ID> --exams-root data/questions-images
