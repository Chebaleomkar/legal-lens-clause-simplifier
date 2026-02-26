import gradio as gr
import requests
import json

# API Configuration
API_URL = "https://agent-omkar-legal-lens-api.hf.space"

def simplify_clause(clause, temperature):
    if not clause.strip():
        return "Please enter a legal clause to simplify."
    
    payload = {
        "clause": clause,
        "temperature": float(temperature),
        "max_new_tokens": 256
    }
    
    try:
        response = requests.post(f"{API_URL}/simplify", json=payload, timeout=30)
        if response.status_code == 200:
            return response.json().get("simplified_text", "Error: No simplified text found.")
        else:
            return f"Error: Backend returned {response.status_code}\n{response.text}"
    except Exception as e:
        return f"Error connecting to backend: {str(e)}"

# Custom Theme and UI
with gr.Blocks(theme=gr.themes.Soft(primary_hue="blue", secondary_hue="indigo")) as demo:
    gr.Markdown("# ⚖️ Legal Lens | AI Clause Simplifier")
    gr.Markdown("Translate complex legal jargon into plain, easy-to-understand English.")
    
    with gr.Row():
        with gr.Column():
            input_text = gr.Textbox(
                label="Legal Clause", 
                placeholder="Paste your complex legal clause here...",
                lines=10
            )
            temp_slider = gr.Slider(
                minimum=0.1, 
                maximum=1.0, 
                value=0.3, 
                step=0.1, 
                label="Creativity (Temperature)"
            )
            submit_btn = gr.Button("✨ Simplify Now", variant="primary")
            
        with gr.Column():
            output_text = gr.Textbox(
                label="Simplified English",
                lines=12,
                interactive=False
            )
            gr.Markdown("---")
            gr.Markdown("*Note: This tool uses a fine-tuned Gemma-2b model. Use for informational purposes only.*")

    submit_btn.click(
        fn=simplify_clause,
        inputs=[input_text, temp_slider],
        outputs=output_text
    )

if __name__ == "__main__":
    demo.launch()
