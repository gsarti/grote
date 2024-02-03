import gradio as gr

from grote.collections import LoadComponents, TranslateComponents
from grote.config import CONFIG as cfg
from grote.event_logging import EventLogger
from grote.style import custom_css

event_logger = EventLogger(
    cfg.hf_token, cfg.event_logs_hf_dataset_id, private=True, logging_dir=cfg.event_logs_local_dir
)


def make_demo():
    with gr.Blocks(theme=gr.themes.Default(primary_hue="red", secondary_hue="pink"), css=custom_css) as demo:
        lc = LoadComponents.build()
        tc = TranslateComponents.build()
        out_state: gr.State = gr.State({"events": []})

        # Event Listeners
        tc.reload_btn.click(None, js="window.location.reload()")
        lc.set_listeners(tc, out_state)
        tc.set_listeners(out_state, lc.state, event_logger)
    return demo


demo = make_demo()


def main():
    demo.queue(api_open=False).launch(show_api=False)


if __name__ == "__main__":
    main()
