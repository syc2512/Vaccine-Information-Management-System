BUTTON_STYLE = {
    'font': ('SimHei', 12),
    'width': 18,
    'height': 2,
    'bg': '#1E90FF',
    'fg': 'white',
    'bd': 0,
    'cursor': 'hand2',
    'activebackground': '#1874CD',
    'activeforeground': 'white',
    'relief': 'flat',
    'highlightthickness': 0
}

MENU_BUTTON_STYLE = {
    'font': ('SimHei', 11),
    'width': 16,
    'height': 2,
    'bg': '#f0f0f0',
    'fg': '#333333',
    'bd': 1,
    'cursor': 'hand2',
    'activebackground': '#E0E0E0',
    'relief': 'flat',
    'highlightthickness': 0
}

EXIT_BUTTON_STYLE = {
    **MENU_BUTTON_STYLE,
    'bg': '#FF6347',
    'fg': 'white',
    'activebackground': '#CC4433'
}

LOGIN_TITLE_FONT = ('Roboto', 24, 'bold')
LOGIN_LABEL_FONT = ('Roboto', 14)
LOGIN_ENTRY_FONT = ('Roboto', 14)

HEADER_TITLE_FONT = ('SimHei', 24, 'bold')
NAV_FONT = ('SimHei', 12, 'bold')
PAGE_TITLE_FONT = ('SimHei', 18, 'bold')

FORM_LABEL_FONT = ('SimHei', 12)
FORM_ENTRY_FONT = ('SimHei', 12)
SUBMIT_BTN_FONT = ('SimHei', 14)

COLORS = {
    'primary_bg': '#f5f5f5',
    'header_bg': '#333333',
    'nav_bg': '#444444',
    'menu_bg': '#E8E8E8',
    'content_bg': '#FFFFFF',
    'primary_text': '#333333',
    'secondary_text': '#666666',
    'hint_text': '#999999',
    'accent_color': '#FF9900',
    'button_blue': '#1E90FF',
    'success_green': '#00CC00',
    'error_red': '#FF6347',
    'border_gray': '#CCCCCC',
    'light_gray': '#F5F5F5'
}

WINDOW_SIZES = {
    'login': '1000x600',
    'main': '1200x700'
}
