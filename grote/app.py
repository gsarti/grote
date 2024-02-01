import gradio as gr
import huggingface_hub

from grote.collections import LoadComponents, TranslateComponents
from grote.config import CONFIG as cfg
from grote.event_logging import HuggingFaceDatasetEventSaver


def make_demo():
    if cfg.hf_token is not None:
        huggingface_hub.login(token=cfg.hf_token, write_permission=True)
        hf_writer = HuggingFaceDatasetEventSaver(cfg.hf_token, cfg.event_logs_hf_dataset_id, private=True)
    else:
        hf_writer = None
        gr.Warning("No Hugging Face token was found. Logging is disabled.")

    with gr.Blocks(theme=gr.themes.Default(primary_hue="red", secondary_hue="pink")) as demo:
        # logo = gr.Markdown(f"<img src='{cfg.grote_logo_path}' width=100 height=100/>")
        with gr.Tabs():
            with gr.TabItem(cfg.translate_tab_label):
                lc = LoadComponents.build()
                tc = TranslateComponents.build()
                out_state: gr.State = gr.State({"events": []})

        # Setup writer
        if hf_writer is not None:
            feature_names = ["time", "login_code", "text_id", "event_type", "text"]
            features = {name: {"dtype": "string", "_type": "Value"} for name in feature_names}
            hf_writer.setup(cfg.event_logs_local_dir, features)

        # Event Listeners
        tc.reload_btn.click(None, js="window.location.reload()")
        lc.set_listeners(tc, out_state)
        tc.set_listeners(out_state, lc.state, hf_writer)
    return demo


def main():
    make_demo().queue(api_open=False).launch(
        show_api=False,
        # favicon_path=cfg.grote_icon_path,
    )


if __name__ == "__main__":
    main()
