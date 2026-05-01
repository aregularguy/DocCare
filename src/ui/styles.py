"""Professional light theme styles for DentNest (inspired by Cursor UI)."""

# Color Palette - Light Theme
COLORS = {
    # Sidebar — deep ocean blue (professional medical SaaS)
    'sidebar_bg': '#0F2942',
    'sidebar_hover': '#1A3A5C',
    'sidebar_active': '#1E4976',
    'sidebar_active_border': '#38BDF8',
    'sidebar_text': '#FFFFFF',
    'sidebar_text_secondary': '#94B8D4',
    'sidebar_border': '#1E3A5A',

    # Main content
    'main_bg': '#FFFFFF',
    'content_bg': '#FAFAFA',
    'card_bg': '#FFFFFF',

    # Primary colors
    'primary': '#007AFF',        # Blue
    'primary_hover': '#0051D5',
    'primary_light': '#E5F0FF',

    # Status colors
    'success': '#34C759',        # Green
    'success_light': '#E8F8EC',
    'warning': '#FF9500',        # Orange
    'warning_light': '#FFF3E0',
    'danger': '#FF3B30',         # Red
    'danger_light': '#FFE5E5',
    'info': '#5856D6',           # Purple
    'info_light': '#F0EFFF',

    # Text
    'text_primary': '#1D1D1F',
    'text_secondary': '#86868B',
    'text_tertiary': '#C7C7CC',

    # Borders
    'border': '#E5E5EA',
    'border_light': '#F2F2F7',

    # Input fields
    'input_bg': '#FFFFFF',
    'input_border': '#D2D2D7',
    'input_border_focus': '#007AFF',
}

# Font settings
FONTS = {
    'family': 'Ubuntu, Nunito, Segoe UI, -apple-system, sans-serif',
    'size_small': '11px',
    'size_normal': '13px',
    'size_medium': '14px',
    'size_large': '16px',
    'size_xlarge': '20px',
    'size_title': '24px',
    'weight_normal': '400',
    'weight_medium': '500',
    'weight_semibold': '600',
    'weight_bold': '700',
}

# Get the complete stylesheet
def get_stylesheet():
    """Get the complete QSS stylesheet for the application."""

    return f"""
    /* Global Styles */
    * {{
        font-family: {FONTS['family']};
        font-size: {FONTS['size_normal']};
        color: {COLORS['text_primary']};
    }}

    QMainWindow {{
        background-color: {COLORS['main_bg']};
    }}

    QWidget {{
        background-color: {COLORS['main_bg']};
        color: {COLORS['text_primary']};
    }}

    /* ── Sidebar: override global QWidget white bg/dark text for all children ── */
    #sidebar,
    #sidebar QWidget,
    #sidebar QScrollArea,
    #sidebar QScrollArea > QWidget,
    #sidebar QScrollArea > QWidget > QWidget {{
        background-color: {COLORS['sidebar_bg']};
        color: {COLORS['sidebar_text']};
    }}

    #sidebar {{
        border-right: 1px solid {COLORS['sidebar_border']};
    }}

    #sidebar_header {{
        background-color: {COLORS['sidebar_bg']};
        padding: 14px 12px;
        border-bottom: 1px solid {COLORS['sidebar_border']};
    }}

    #app_title {{
        font-size: 14px;
        font-weight: 700;
        color: #FFFFFF;
        background-color: {COLORS['sidebar_bg']};
    }}

    #app_subtitle {{
        font-size: 10px;
        color: {COLORS['sidebar_text_secondary']};
        background-color: {COLORS['sidebar_bg']};
    }}

    /* Nav items are now QWidget-based (NavItem class) — styled inline in Python */

    /* Separator Line */
    QFrame#separator {{
        background-color: {COLORS['sidebar_border']};
        max-height: 1px;
        margin: 6px 0px;
    }}

    /* Content Area */
    #content_area {{
        background-color: {COLORS['content_bg']};
        padding: 0px;
    }}

    /* Card/Panel Styles */
    QFrame#card {{
        background-color: {COLORS['card_bg']};
        border: 1px solid {COLORS['border']};
        border-radius: 12px;
        padding: 20px;
    }}

    /* Metric Card Styles */
    QFrame#metric_card {{
        background-color: {COLORS['card_bg']};
        border: 1px solid {COLORS['border']};
        border-radius: 10px;
        padding: 16px;
    }}

    QLabel#metric_value {{
        font-size: {FONTS['size_title']};
        font-weight: {FONTS['weight_bold']};
        color: {COLORS['text_primary']};
    }}

    QLabel#metric_label {{
        font-size: {FONTS['size_small']};
        color: {COLORS['text_secondary']};
        font-weight: {FONTS['weight_medium']};
    }}

    /* Button Styles */
    QPushButton#primary_button {{
        background-color: {COLORS['primary']};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: {FONTS['weight_semibold']};
        font-size: {FONTS['size_medium']};
    }}

    QPushButton#primary_button:hover {{
        background-color: {COLORS['primary_hover']};
    }}

    QPushButton#primary_button:pressed {{
        background-color: {COLORS['primary_hover']};
    }}

    QPushButton#secondary_button {{
        background-color: transparent;
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: {FONTS['weight_medium']};
    }}

    QPushButton#secondary_button:hover {{
        background-color: {COLORS['primary_light']};
        border-color: {COLORS['primary']};
        color: {COLORS['primary']};
    }}

    QPushButton#success_button {{
        background-color: {COLORS['success']};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: {FONTS['weight_semibold']};
    }}

    QPushButton#danger_button {{
        background-color: {COLORS['danger']};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: {FONTS['weight_semibold']};
    }}

    /* Input Field Styles */
    QLineEdit {{
        background-color: {COLORS['input_bg']};
        border: 1px solid {COLORS['input_border']};
        border-radius: 6px;
        padding: 12px 16px;
        font-size: {FONTS['size_medium']};
        selection-background-color: {COLORS['primary_light']};
        min-height: 20px;
    }}

    QLineEdit:focus {{
        border: 2px solid {COLORS['input_border_focus']};
        padding: 11px 15px;
    }}

    QTextEdit {{
        background-color: {COLORS['input_bg']};
        border: 1px solid {COLORS['input_border']};
        border-radius: 6px;
        padding: 12px 16px;
        font-size: {FONTS['size_medium']};
        selection-background-color: {COLORS['primary_light']};
    }}

    QTextEdit:hover {{
        background-color: {COLORS['primary_light']};
        border: 1px solid {COLORS['primary']};
    }}

    QTextEdit:focus {{
        border: 2px solid {COLORS['input_border_focus']};
        padding: 11px 15px;
    }}

    QSpinBox, QDoubleSpinBox {{
        background-color: {COLORS['input_bg']};
        border: 1px solid {COLORS['input_border']};
        border-radius: 6px;
        padding: 12px 16px;
        font-size: {FONTS['size_medium']};
        min-height: 20px;
    }}

    QSpinBox:hover, QDoubleSpinBox:hover {{
        background-color: {COLORS['primary_light']};
        border: 1px solid {COLORS['primary']};
    }}

    QSpinBox:focus, QDoubleSpinBox:focus {{
        border: 2px solid {COLORS['input_border_focus']};
        padding: 11px 15px;
    }}

    /* ComboBox Styles */
    QComboBox {{
        background-color: {COLORS['input_bg']};
        border: 1px solid {COLORS['input_border']};
        border-radius: 6px;
        padding: 12px 16px;
        font-size: {FONTS['size_medium']};
        min-height: 20px;
    }}

    QComboBox:hover {{
        background-color: {COLORS['primary_light']};
        border: 1px solid {COLORS['primary']};
    }}

    QComboBox:focus {{
        border: 2px solid {COLORS['input_border_focus']};
        padding: 11px 15px;
    }}

    QComboBox::drop-down {{
        border: none;
        padding-right: 12px;
        width: 30px;
    }}

    QComboBox::down-arrow {{
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 7px solid {COLORS['text_secondary']};
        margin-right: 8px;
    }}

    QComboBox::down-arrow:hover {{
        border-top: 7px solid {COLORS['primary']};
    }}

    QComboBox QAbstractItemView {{
        background-color: {COLORS['card_bg']};
        border: 2px solid {COLORS['primary']};
        border-radius: 8px;
        selection-background-color: {COLORS['primary']};
        selection-color: white;
        padding: 6px;
        outline: none;
    }}

    QComboBox QAbstractItemView::item {{
        padding: 10px 12px;
        border-radius: 4px;
        min-height: 20px;
    }}

    QComboBox QAbstractItemView::item:hover {{
        background-color: {COLORS['primary_light']};
        color: {COLORS['primary']};
    }}

    QComboBox QAbstractItemView::item:selected {{
        background-color: {COLORS['primary']};
        color: white;
    }}

    /* DateEdit Styles */
    QDateEdit {{
        background-color: {COLORS['input_bg']};
        border: 1px solid {COLORS['input_border']};
        border-radius: 6px;
        padding: 12px 16px;
        font-size: {FONTS['size_medium']};
        min-height: 20px;
    }}

    QDateEdit:hover {{
        background-color: {COLORS['primary_light']};
        border: 1px solid {COLORS['primary']};
    }}

    QDateEdit:focus {{
        border: 2px solid {COLORS['input_border_focus']};
        padding: 11px 15px;
    }}

    /* Table Styles */
    QTableWidget {{
        background-color: {COLORS['card_bg']};
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        gridline-color: {COLORS['border_light']};
        font-size: {FONTS['size_medium']};
        alternate-background-color: #FAFAFA;
    }}

    QTableWidget::item {{
        padding: 10px 14px;
        min-height: 40px;
        border: none;
    }}

    QTableWidget::item:hover {{
        background-color: #F0F9FF;
    }}

    QTableWidget::item:selected {{
        background-color: #DBEAFE;
        color: #0F2942;
    }}

    QHeaderView::section {{
        background-color: #EFF6FF;
        color: #1A4A7A;
        padding: 10px;
        border: none;
        border-bottom: 2px solid #38BDF8;
        font-weight: {FONTS['weight_semibold']};
        font-size: {FONTS['size_small']};
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}

    /* ScrollBar Styles */
    QScrollBar:vertical {{
        background-color: {COLORS['content_bg']};
        width: 12px;
        border-radius: 6px;
    }}

    QScrollBar::handle:vertical {{
        background-color: {COLORS['border']};
        border-radius: 6px;
        min-height: 30px;
    }}

    QScrollBar::handle:vertical:hover {{
        background-color: {COLORS['text_tertiary']};
    }}

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}

    QScrollBar:horizontal {{
        background-color: {COLORS['content_bg']};
        height: 12px;
        border-radius: 6px;
    }}

    QScrollBar::handle:horizontal {{
        background-color: {COLORS['border']};
        border-radius: 6px;
        min-width: 30px;
    }}

    QScrollBar::handle:horizontal:hover {{
        background-color: {COLORS['text_tertiary']};
    }}

    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}

    /* Label Styles */
    QLabel#page_title {{
        font-size: {FONTS['size_title']};
        font-weight: {FONTS['weight_bold']};
        color: {COLORS['text_primary']};
    }}

    QLabel#section_title {{
        font-size: {FONTS['size_large']};
        font-weight: {FONTS['weight_semibold']};
        color: {COLORS['text_primary']};
    }}

    QLabel#form_label {{
        font-size: {FONTS['size_medium']};
        font-weight: {FONTS['weight_medium']};
        color: {COLORS['text_primary']};
        margin-bottom: 4px;
    }}

    QLabel#error_label {{
        color: {COLORS['danger']};
        font-size: {FONTS['size_small']};
    }}

    QLabel#success_label {{
        color: {COLORS['success']};
        font-size: {FONTS['size_small']};
    }}

    /* Dialog Styles */
    QDialog {{
        background-color: {COLORS['main_bg']};
    }}

    /* Tab Widget Styles */
    QTabWidget::pane {{
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        background-color: {COLORS['card_bg']};
    }}

    QTabBar::tab {{
        background-color: transparent;
        color: {COLORS['text_secondary']};
        padding: 10px 20px;
        border: none;
        font-weight: {FONTS['weight_medium']};
    }}

    QTabBar::tab:selected {{
        color: {COLORS['primary']};
        border-bottom: 2px solid {COLORS['primary']};
        font-weight: {FONTS['weight_semibold']};
    }}

    QTabBar::tab:hover {{
        color: {COLORS['text_primary']};
    }}
    """

# Icon paths or Unicode symbols for navigation
NAV_ICONS = {
    'dashboard':    '🏠',
    'patients':     '👥',
    'treatments':   '🦷',
    'payments':     '💳',
    'due_payments': '⏳',
    'prescriptions':'📋',
    'analytics':    '📊',
    'settings':     '⚙️',
    'export':       '📤',
}
