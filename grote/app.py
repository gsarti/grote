from pathlib import Path

import gradio as gr

from grote.collections import LoadComponents, TranslateComponents
from grote.config import CONFIG as cfg
from grote.event_logging import EventLogger
from grote.style import custom_css, ensure_dark_theme_js

event_logger = EventLogger(
    cfg.hf_token, cfg.event_logs_hf_dataset_id, private=True, logging_dir=cfg.event_logs_local_dir
)


def make_demo():
    with gr.Blocks(
        theme=gr.themes.Default(primary_hue="red", secondary_hue="pink"), css=custom_css, js=ensure_dark_theme_js
    ) as demo:
        gr.HTML('<img src="file/assets/img/grote_logo.png" width=200px />')
        lc = LoadComponents.build()
        tc = TranslateComponents.build()
        out_state: gr.State = gr.State({"events": []})

        # Event Listeners
        tc.reload_btn.click(None, js="window.location.reload()")
        lc.set_listeners(tc, out_state)
        tc.set_listeners(out_state, lc.state, event_logger)
        with gr.Row(elem_classes="footer-container"):
            with gr.Row(elem_classes="footer-custom-block"):
                with gr.Column(scale=0.31, min_width=200):
                    gr.Markdown(
                        """<b>Built by <a href="https://gsarti.com" target="_blank">Gabriele Sarti</a> with the support of</b>"""
                    )
                with gr.Column(scale=0.23, min_width=120):
                    gr.Markdown(
                        """<a href='https://www.rug.nl/research/clcg/research/cl/' target='_blank'><img src="file/assets/img/rug_logo_white_contour.png" width=170px /></a>"""
                    )
                with gr.Column(scale=0.23, min_width=120):
                    gr.Markdown(
                        """<a href='https://projects.illc.uva.nl/indeep/' target='_blank'><img src="file/assets/img/indeep_logo_white_contour.png" width=100px /></a>"""
                    )
                with gr.Column(scale=0.23, min_width=120):
                    gr.Markdown(
                        """<a href='https://imminent.translated.com/' target='_blank'><img src="file/assets/img/imminent_logo_white_contour.png" width=150px /></a>"""
                    )

    return demo


demo = make_demo()


def main():
    current_file_path = Path(__file__).resolve()
    img_path = (current_file_path.parent / ".." / "assets" / "img").resolve()
    demo.queue(api_open=False).launch(show_api=False, allowed_paths=[img_path])


if __name__ == "__main__":
    main()
