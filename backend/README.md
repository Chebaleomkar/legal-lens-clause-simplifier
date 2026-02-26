---
title: Legal Lens - Clause Simplifier API
emoji: ⚖️
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
---

# Legal Lens - Clause Simplifier API

FastAPI backend for simplifying complicated legal clauses into plain English, powered by a fine-tuned **Gemma-2b** model with LoRA adapters.

## Model

- **Base Model**: [google/gemma-2b](https://huggingface.co/google/gemma-2b)
- **Fine-tuned Adapter**: [Agent-Omkar/legal-lens-clause-simplifier](https://huggingface.co/Agent-Omkar/legal-lens-clause-simplifier)

## API Endpoints

### `GET /health`
Check if the model is loaded and ready.

### `POST /simplify`
Simplify a legal clause.

**Request Body:**
```json
{
  "clause": "In witness whereof, the parties hereto have executed this Agreement as of the date first above written.",
  "max_new_tokens": 128,
  "temperature": 0.3
}
```

**Response:**
```json
{
  "simplified_text": "Both parties have signed this agreement on the date written above."
}
```

## Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Run the API directly
python -m uvicorn main:app --host 0.0.0.0 --port 7860
```

Then visit the Swagger docs at [http://127.0.0.1:7860/docs](http://127.0.0.1:7860/docs).
