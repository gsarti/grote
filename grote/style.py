custom_css = """
.source-textbox textarea{
    user-select: none;
    cursor: not-allowed;
    pointer-events: none;
    border-width: 0px;
    resize: none;
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
