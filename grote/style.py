custom_css = """
.textbox-prevent-copy textarea{
    user-select: none;
    cursor: not-allowed;
    pointer-events: none;
    border-width: 0px;
    resize: none;
}
.source-text textarea {
    border-width: 0px;
    resize: none;
}
.footer-custom-block {
    margin-top: 20px;
    display: flex;
    justify-content: center;
    align-items: center;
}
.footer-custom-block b {
    margin-right: 10px;
}
.footer-custom-block img {
    margin-right: 15px;
}
"""

ensure_dark_theme_js = """
function refresh() {
    const url = new URL(window.location);

    if (url.searchParams.get('__theme') !== 'dark') {
        url.searchParams.set('__theme', 'dark');
        window.location.href = url.href;
    }
}
"""

# launch default browser dialog when the window is refreshed/closed
prevent_data_loss_js = """
function prevent_reload() {
    window.onbeforeunload = () => true;
}
"""
