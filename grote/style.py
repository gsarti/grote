custom_css = """
.source-textbox textarea{
    user-select: none;
    cursor: not-allowed;
    pointer-events: none;
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
