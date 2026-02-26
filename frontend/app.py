import gradio as gr
import requests

# API Configuration
API_URL = "https://agent-omkar-legal-lens-api.hf.space"

EXAMPLES = [
    ["In witness whereof, the parties hereto have executed this Agreement as of the date first above written."],
    ["Notwithstanding any provision herein to the contrary, the indemnifying party shall hold harmless the indemnified party from any and all claims, damages, losses, costs, and expenses."],
    ["The lessee shall not assign, sublease, or otherwise transfer any interest in the demised premises without the prior written consent of the lessor."],
]

def check_api_status():
    """Check if the backend API is running."""
    try:
        resp = requests.get(f"{API_URL}/health", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return f"✅ API Online | Device: {data.get('device', 'unknown')}"
        return "⚠️ API returned non-200 status"
    except Exception:
        return "❌ API Offline or Still Loading"

def simplify_clause(clause, temperature):
    """Send clause to API and return simplified version."""
    if not clause or not clause.strip():
        return "⚠️ Please enter a legal clause to simplify."

    payload = {
        "clause": clause.strip(),
        "temperature": float(temperature),
        "max_new_tokens": 256
    }

    try:
        response = requests.post(f"{API_URL}/simplify", json=payload, timeout=60)
        if response.status_code == 200:
            result = response.json().get("simplified_text", "")
            return result if result else "No simplification returned."
        elif response.status_code == 503:
            return "⏳ Model is still loading. Please wait a minute and try again."
        else:
            return f"Error {response.status_code}: {response.text}"
    except requests.exceptions.Timeout:
        return "⏱️ Request timed out. The model may be loading — please try again."
    except Exception as e:
        return f"Connection error: {str(e)}"

# Build the Gradio UI
with gr.Blocks(title="Legal Lens | AI Clause Simplifier") as demo:

    gr.Markdown(
        """
        # ⚖️ Legal Lens
        ### Simplify complex legal clauses into plain English
        Powered by a fine-tuned **Gemma-2b** model with LoRA adapters.
        """
    )

    status_text = gr.Textbox(
        label="API Status",
        value=check_api_status,
        interactive=False,
        max_lines=1
    )

    with gr.Row(equal_height=True):
        with gr.Column():
            input_text = gr.Textbox(
                label="📜 Legal Clause",
                placeholder="Paste your complex legal clause here...",
                lines=8,
                max_lines=15
            )
            temp_slider = gr.Slider(
                minimum=0.1,
                maximum=1.0,
                value=0.3,
                step=0.1,
                label="🎨 Creativity (Temperature)",
                info="Lower = more precise, Higher = more creative"
            )
            submit_btn = gr.Button("✨ Simplify Now", variant="primary", size="lg")

        with gr.Column():
            output_text = gr.Textbox(
                label="📝 Plain English",
                lines=8,
                max_lines=15,
                interactive=False
            )

    gr.Examples(
        examples=EXAMPLES,
        inputs=input_text,
        label="💡 Try these examples"
    )

    submit_btn.click(
        fn=simplify_clause,
        inputs=[input_text, temp_slider],
        outputs=output_text
    )

    gr.Markdown(
        """
        ---
        **Disclaimer:** This tool is for informational purposes only and does not constitute legal advice.

        🔗 [Model](https://huggingface.co/Agent-Omkar/legal-lens-clause-simplifier) · [API](https://huggingface.co/spaces/Agent-Omkar/legal-lens-api) · [GitHub](https://github.com/Chebaleomkar/legal-lens-clause-simplifier)
        """
    )

if __name__ == "__main__":
    demo.launch()
