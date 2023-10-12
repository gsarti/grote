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

    # for target_textbox in tc.get_target_textboxes():
    #    target_textbox.input(

    #    )


if __name__ == "__main__":
    demo.queue().launch(debug=True)
