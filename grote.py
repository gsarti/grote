import gradio as gr

textboxs = {}

with gr.Blocks(css="#warning {color: red} #info {color: yellow") as grote:
    with gr.Tabs():
        with gr.TabItem("🔠 Translate"):
            file = gr.File(
                label="Uploaded documents",
                interactive=True,
                elem_id="files_upload"
            )
            with gr.Column():
                start_btn = gr.Button("Start", variant="secondary", elem_id="start_btn")
                restart_btn = gr.Button("Restart", variant="primary", elem_id="restart_btn", visible=False)
                warn_msg = gr.Markdown("", elem_id="warning")
                info_msg = gr.Markdown("", elem_id="info")
            
            with gr.Column(visible=False) as textboxs_col:
                for i in range(10):
                    with gr.Row():
                        textboxs[f"source_{i}"] = gr.Textbox(
                            label="Source text",
                            lines=3,
                            elem_id=f"source_{i}",
                        )
                        textboxs[f"target_{i}"] = gr.Textbox(
                            label="Translation",
                            lines=3,
                            elem_id=f"source_{i}",
                        )
            done_btn = gr.Button("Done", variant="primary", elem_id="done_btn", visible=False)

        # Settings
        with gr.TabItem("⚙️ Settings"):
            with gr.Row():
                with gr.Column():
                    file_type = gr.Dropdown(label="File type", choices=["txt"], value="txt", interactive=True)
                with gr.Column():
                    source_field = gr.Textbox(label="Source field", placeholder="No field for txt files", interactive=False, max_lines=1)
                with gr.Column():
                    target_field = gr.Textbox("<INFER>", label="Target field", interactive=False, max_lines=1)
                    infer_model_id = gr.Textbox(
                        "Helsinki-NLP/opus-mt-en-it", label="Translation model", 
                        placeholder="Insert a translation model identifier from the HF Hub",
                        interactive=True,
                    )
        
    def start_fn(file: str, ext: str, model_id: str):
        if file is None:
            return {
                warn_msg: gr.update(value="ERROR: Insert a .txt file to start translating")
            }
        else:
            if not file.name.endswith(ext):
                return {
                    warn_msg: gr.update(value=f"ERROR: Invalid file format. Use a .{ext} file or change the parameter in Settings.")
                }
            return {
                textboxs_col: gr.update(visible=True),
                done_btn: gr.update(visible=True),
                start_btn: gr.update(visible=False),
                restart_btn: gr.update(visible=True),
                info_msg: gr.update(value=f"Automatic translations were performed using {model_id}")
            }
    
    def file_change_fn(file: str, ext: str):
        if not file.name.endswith(ext):
            return {
                warn_msg: gr.update(value=f"ERROR: Invalid file format. Use a .{ext} file or change the parameter in Settings.")
            }
        else:
            return ["", gr.update(variant="primary")] + ["Hello"] * 10 + ["World"] * 10
        

    start_btn.click(
        start_fn,
        inputs=[file, file_type, infer_model_id],
        outputs=[warn_msg, textboxs_col, done_btn, start_btn, restart_btn, info_msg]
    )

    file.change(
        file_change_fn,
        inputs=[file, file_type],
        outputs=[warn_msg, start_btn] + list(textboxs.values())
    )
            

if __name__ == "__main__":
    grote.launch()