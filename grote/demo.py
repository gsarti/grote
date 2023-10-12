import gradio as gr

from grote.collections import LoadComponents, TranslateComponents
from grote.utils import CONFIG as cfg

with gr.Blocks(theme=gr.themes.Default(primary_hue="red", secondary_hue="pink")) as demo:
    # logo = gr.Markdown("<img src='file/assets/grote_logo.png' width=400 height=200/>")
    with gr.Tabs():
        with gr.TabItem(cfg.translate_tab_label):
            lc = LoadComponents.build()
            tc = TranslateComponents.build()
            out_state: gr.State = gr.State({})

    # Event Listeners
    lc.set_loading_listeners(tc, out_state)
    lc.clear_changes_listener(tc, out_state)
    tc.reload_btn.click(None, _js="window.location.reload()")
    # tc.set_editing_listeners(out_state)


def main():
    demo.queue().launch(debug=True)


if __name__ == "__main__":
    main()
