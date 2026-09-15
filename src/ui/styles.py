"""Professional light theme styles for DentNest (inspired by Cursor UI)."""
import os

# Arrow icons for combo/spin/date boxes (QSS needs forward slashes)
ICON_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources", "icons"
).replace("\\", "/")

# Color Palette - Light Theme
COLORS = {
    # Sidebar — deep ocean blue (professional medical SaaS)
    'sidebar_bg': '#1F4E5A',
    'sidebar_hover': '#28606D',
    'sidebar_active': '#2F7382',
    'sidebar_active_border': '#3AA9BA',
    'sidebar_text': '#FFFFFF',
    'sidebar_text_secondary': '#A9CBD2',
    'sidebar_border': '#2A5D69',

    # Main content
    'main_bg': '#FFFFFF',
    'content_bg': '#F4F7F8',
    'card_bg': '#FFFFFF',

    # Primary colors
    'primary': '#1F8A9E',        # Blue
    'primary_hover': '#16707F',
    'primary_light': '#E3F3F6',

    # Status colors
    'success': '#2E9E6B',        # Green
    'success_light': '#E6F5EE',
    'warning': '#C98A2E',        # Orange
    'warning_light': '#FBF1E1',
    'danger': '#D0534F',         # Red
    'danger_light': '#FBEBEA',
    'info': '#6E72B8',           # Purple
    'info_light': '#EEEFF8',

    # Text
    'text_primary': '#1E2B32',
    'text_secondary': '#5B6B73',
    'text_tertiary': '#A9B6BC',

    # Borders
    'border': '#DDE5E8',
    'border_light': '#EEF3F4',

    # Input fields
    'input_bg': '#FFFFFF',
    'input_border': '#CFDADE',
    'input_border_focus': '#1F8A9E',
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

    /* Soft mist page ground; cards/inputs/tables paint their own white.
       Plain containers stay transparent so labels inside white cards don't
       get grey patches. */
    QMainWindow {{
        background-color: {COLORS['content_bg']};
    }}

    QWidget {{
        background-color: transparent;
        color: {COLORS['text_primary']};
    }}

    QStackedWidget, QScrollArea, QScrollArea > QWidget > QWidget {{
        background-color: {COLORS['content_bg']};
    }}

    /* Top-level and popup surfaces need an explicit fill */
    QDialog, QMessageBox, QMenu, QCalendarWidget, QComboBoxPrivateContainer {{
        background-color: {COLORS['card_bg']};
    }}

    QAbstractItemView, QListView {{
        background-color: {COLORS['card_bg']};
    }}

    QToolTip {{
        background-color: {COLORS['card_bg']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['border']};
        padding: 4px 8px;
    }}

    /* Unstyled buttons in message boxes / dialog button rows would inherit the
       transparent QWidget ground and render dark; give them a light surface.
       Scoped so page buttons keep their own inline styles and sizes. */
    QMessageBox QPushButton, QDialogButtonBox QPushButton {{
        background-color: {COLORS['card_bg']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['input_border']};
        border-radius: 6px;
        padding: 6px 16px;
        min-width: 72px;
    }}

    QMessageBox QPushButton:hover, QDialogButtonBox QPushButton:hover {{
        background-color: {COLORS['primary_light']};
        border-color: {COLORS['primary']};
        color: {COLORS['primary']};
    }}

    QMessageBox QPushButton:default, QDialogButtonBox QPushButton:default {{
        border-color: {COLORS['primary']};
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

    /* Explicit SVG arrows: Fusion's default arrows render as squares once boxes are styled */
    QComboBox::drop-down, QDateEdit::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: center right;
        width: 28px;
        border: none;
        background: transparent;
    }}

    QComboBox::down-arrow, QDateEdit::down-arrow {{
        image: url({ICON_DIR}/chevron-down.svg);
        width: 12px;
        height: 12px;
    }}

    QSpinBox::up-button, QDoubleSpinBox::up-button {{
        subcontrol-origin: border;
        subcontrol-position: top right;
        width: 22px;
        border: none;
        background: transparent;
    }}

    QSpinBox::down-button, QDoubleSpinBox::down-button {{
        subcontrol-origin: border;
        subcontrol-position: bottom right;
        width: 22px;
        border: none;
        background: transparent;
    }}

    QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{
        image: url({ICON_DIR}/chevron-up.svg);
        width: 10px;
        height: 10px;
    }}

    QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{
        image: url({ICON_DIR}/chevron-down.svg);
        width: 10px;
        height: 10px;
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
        border: 1px solid #DDE5E8;
        border-radius: 10px;
        gridline-color: {COLORS['border_light']};
        font-size: {FONTS['size_medium']};
        alternate-background-color: #F4F7F8;
    }}

    QTableWidget::item {{
        padding: 10px 14px;
        min-height: 40px;
        border: none;
    }}

    QTableWidget::item:hover {{
        background-color: #EEF7F9;
    }}

    QTableWidget::item:selected {{
        background-color: #CDEAF0;
        color: #1F4E5A;
    }}

    QHeaderView::section {{
        background-color: #E3F3F6;
        color: #2A6674;
        padding: 10px;
        border: none;
        border-bottom: 2px solid #3AA9BA;
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
    'prescriptions':'📋',
    'analytics':    '📊',
    'settings':     '⚙️',
    'export':       '📤',
}
