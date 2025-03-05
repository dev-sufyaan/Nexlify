# Suppress GTK accessibility warnings
import os
os.environ['NO_AT_BRIDGE'] = '1'

import sys
import time
import queue
import json
import re
import base64
import webbrowser
import threading
import requests
import google.generativeai as genai
from datetime import datetime
from io import BytesIO
from PySide6.QtCore import (
    Qt, QTimer, QRect, QObject, QThread, QPropertyAnimation, QEasingCurve,
    QSequentialAnimationGroup, QParallelAnimationGroup, QSize, Signal, Slot, QMetaObject, QPoint, QEvent, QAbstractAnimation
)
from PySide6.QtGui import QAction, QFontMetrics, QPainter, QPixmap, QIcon, QFont, QColor, QPalette, QSyntaxHighlighter, QTextCharFormat, QGuiApplication
from PySide6.QtWidgets import (
    QApplication, QWidget, QFrame, QVBoxLayout, QHBoxLayout,
    QComboBox, QLineEdit, QToolButton, QPushButton, QScrollArea,
    QSizePolicy, QLabel, QSpacerItem, QSizeGrip, QMenu, QGroupBox,
    QFormLayout, QSpinBox, QCheckBox, QWidgetAction, QStackedWidget, QStyle, QStyledItemDelegate, QToolTip, QTextEdit, QGraphicsOpacityEffect,
    QDialog, QDialogButtonBox, QSystemTrayIcon
)
from dotenv import load_dotenv, set_key, find_dotenv

load_dotenv()

# ==================== GLOBALS & DEFAULTS  ====================
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

conversation_messages = []
MODEL_OPTIONS = ["Gemini", "Gemini Lite", "R1 Groq", "Mistral", "Llama", "R1", "DS-V3"]
CURRENT_MODEL_INDEX = 0
CURRENT_MODEL = MODEL_OPTIONS[CURRENT_MODEL_INDEX]

# ANSI color codes for console printing
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
CYAN = "\033[36m"
MAGENTA = "\033[35m"
RESET = "\033[0m"

last_main_geometry = None
last_chat_geometry = None

# ======= ELEGANT DARK THEME COLOR PALETTE =======
BG_COLOR = "#1E1E1E"         # Dark Background
BUBBLE_USER_COLOR = "#333333"   # User Bubble - Slightly lighter than BG
BUBBLE_AI_COLOR = "#282828"     # AI Bubble -  Mid-tone grey
TEXT_COLOR_PRIMARY = "#EEEEEE"   # Primary Text - Light, almost white
TEXT_COLOR_SECONDARY = "#AAAAAA" # Secondary Text -  Softer light grey
INPUT_BG_COLOR = "#2A2A2A"     # Input Background - Slightly lighter than BG
INPUT_TEXT_COLOR = "#EEEEEE"    # Input Text - Light
BORDER_COLOR = "#555555"       # Subtle Border/Divider
BUTTON_HOVER_COLOR = "#444444"  # Button Hover
SCROLLBAR_BG_COLOR = "#333333" # Scrollbar Background
SCROLLBAR_HANDLE_COLOR = "#666666"# Scrollbar Handle
CLOSE_BUTTON_BG = "#AA0000"      # Close Button - Dark Red
CLOSE_BUTTON_HOVER = "#FF0000"   # Close Button Hover - Bright Red
FRAME_BG_COLOR = "rgba(30, 30, 30, 0.9)" # Frame Background - Semi-opaque dark grey
MODEL_BUTTON_HOVER = "#444444"   # Model Button Hover
CODE_BLOCK_BG = "#1A1A1A"      # Code Block Background - Darker than bubble
CODE_BLOCK_BORDER = "#444444"  # Code Block Border - Subtle border
CODE_TEXT_COLOR = "#D4D4D4"    # Code Text - Slightly gray-white
CODE_COMMENT_COLOR = "#6A9955"  # Code Comments - Green
CODE_KEYWORD_COLOR = "#569CD6"  # Code Keywords - Blue
CODE_STRING_COLOR = "#CE9178"   # Code Strings - Orange-Brown

# =============== EMBEDDED ICONS FOR CROSS-PLATFORM SUPPORT ===============

# Base64 encoded Nexlify logo - provides a reliable fallback when logo.png isn't found
NEXLIFY_ICON_B64 = """
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
"""

def get_embedded_icon():
    """Returns a QIcon from the base64-encoded logo"""
    try:
        # Decode the base64 string to binary data
        icon_data = base64.b64decode(NEXLIFY_ICON_B64)
        # Create a QPixmap from the binary data
        pixmap = QPixmap()
        pixmap.loadFromData(icon_data)
        return QIcon(pixmap)
    except Exception as e:
        print(f"{RED}Error creating embedded icon: {e}{RESET}")
        return None

# =============== FUNCTIONALITY: SIMPLIFIED CONFIG ===============

def load_config():
    """Loads basic config from .nexlify."""
    config_file = ".nexlify"
    if not os.path.exists(config_file):
        return
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
        global CURRENT_MODEL_INDEX, CURRENT_MODEL
        CURRENT_MODEL_INDEX = config.get("CURRENT_MODEL_INDEX", CURRENT_MODEL_INDEX)
        CURRENT_MODEL = MODEL_OPTIONS[CURRENT_MODEL_INDEX]
    except Exception as e:
        print(f"{RED}Error loading config: {e}{RESET}")

def save_config():
    """Saves basic config to .nexlify."""
    config_file = ".nexlify"
    try:
        config = {
            "CURRENT_MODEL_INDEX": CURRENT_MODEL_INDEX
        }
        with open(config_file, "w", newline="", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"{RED}Error saving config: {e}{RESET}")

# =============== CODE BLOCK HANDLING ===============

class CodeBlockWidget(QFrame):
    """A widget for displaying code blocks with syntax highlighting and copy functionality."""
    def __init__(self, code_text, language="", parent=None):
        super().__init__(parent)
        self.code_text = code_text
        self.language = language
        self.setup_ui()

    def setup_ui(self):
        self.setObjectName("CodeBlockFrame")
        self.setStyleSheet(f"""
            QFrame#CodeBlockFrame {{
                background-color: {CODE_BLOCK_BG};
                border: 1px solid {CODE_BLOCK_BORDER};
                border-radius: 4px;
                padding: 0px;
                margin: 4px 0px;
            }}
        """)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header with language and copy button
        header = QFrame()
        header.setStyleSheet(f"""
            background-color: {BUBBLE_USER_COLOR};
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(8, 3, 8, 3)

        # Language label
        lang_label = QLabel(self.language if self.language else "code")
        lang_label.setStyleSheet(f"color: {TEXT_COLOR_SECONDARY}; font-size: 10px;")
        header_layout.addWidget(lang_label)

        header_layout.addStretch()

        # Copy button
        self.copy_button = QToolButton()
        self.copy_button.setText("📋")
        self.copy_button.setToolTip("Copy code")
        self.copy_button.setStyleSheet(f"""
            QToolButton {{
                background-color: transparent;
                border: none;
                color: {TEXT_COLOR_SECONDARY};
                font-size: 12px;
                padding: 0px;
            }}
            QToolButton:hover {{
                color: {TEXT_COLOR_PRIMARY};
            }}
        """)
        self.copy_button.clicked.connect(self.copy_code_to_clipboard)
        header_layout.addWidget(self.copy_button)

        main_layout.addWidget(header)

        # Code content
        self.code_edit = QTextEdit()
        self.code_edit.setReadOnly(True)
        self.code_edit.setPlainText(self.code_text)
        self.code_edit.setStyleSheet(f"""
            QTextEdit {{
                background-color: {CODE_BLOCK_BG};
                color: {CODE_TEXT_COLOR};
                border: none;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                padding: 8px;
                selection-background-color: #264F78;
            }}
        """)

        # Set a fixed height based on the content with padding for scrollbar
        line_count = len(self.code_text.splitlines()) + 1
        line_height = QFontMetrics(self.code_edit.font()).height()
        max_height = min(line_count * line_height + 20, 300)  # Limit to 300px max
        self.code_edit.setFixedHeight(max_height)

        main_layout.addWidget(self.code_edit)

    def copy_code_to_clipboard(self):
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(self.code_text)

        # Show a brief "Copied!" message
        original_text = self.copy_button.text()
        self.copy_button.setText("✓")
        QTimer.singleShot(1000, lambda: self.copy_button.setText(original_text))


def parse_text_for_code_blocks(text):
    """
    Parse text to identify code blocks marked with triple backticks.
    Returns a list of tuples (is_code, content, language)
    """
    pattern = r'```(\w*)\n([\s\S]*?)```'
    parts = []

    last_end = 0
    for match in re.finditer(pattern, text):
        # Add text before the code block
        if match.start() > last_end:
            parts.append((False, text[last_end:match.start()], None))

        # Add the code block
        language = match.group(1).strip()
        code = match.group(2)
        parts.append((True, code, language))

        last_end = match.end()

    # Add any remaining text after the last code block
    if last_end < len(text):
        parts.append((False, text[last_end:], None))

    # If no code blocks were found, return the entire text
    if not parts:
        parts.append((False, text, None))

    return parts


# =============== SETTINGS DIALOG ===============

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nexlify Settings")
        self.setFixedSize(380, 210)  # Fixed compact size
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Create main frame with border radius
        self.main_frame = QFrame(self)
        self.main_frame.setObjectName("SettingsFrame")
        self.main_frame.setStyleSheet(f"""
            QFrame#SettingsFrame {{
                background-color: {BG_COLOR};
                border-radius: 10px;
                border: 1px solid {BORDER_COLOR};
            }}
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.main_frame)

        # Content layout
        layout = QVBoxLayout(self.main_frame)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Title and close button
        title_layout = QHBoxLayout()
        title_label = QLabel("API Keys")
        title_label.setStyleSheet(f"color: {TEXT_COLOR_PRIMARY}; font-size: 14px; font-weight: bold;")

        close_button = QPushButton("✕")
        close_button.setFixedSize(20, 20)
        close_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {CLOSE_BUTTON_BG};
                color: {TEXT_COLOR_PRIMARY};
                border: none;
                border-radius: 10px;
                font-size: 10px;
                padding: 0;
            }}
            QPushButton:hover {{ background-color: {CLOSE_BUTTON_HOVER}; }}
        """)
        close_button.clicked.connect(self.reject)

        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(close_button)
        layout.addLayout(title_layout)

        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(8)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form_layout.setLabelAlignment(Qt.AlignRight)

        # Google API Key
        self.google_api_key = QLineEdit()
        self.google_api_key.setEchoMode(QLineEdit.Password)
        self.google_api_key.setText(os.getenv("GOOGLE_API_KEY", ""))
        self.google_api_key.setStyleSheet(f"""
            QLineEdit {{
                background-color: {INPUT_BG_COLOR};
                color: {INPUT_TEXT_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 5px;
                padding: 5px;
                font-size: 12px;
                height: 24px;
            }}
        """)
        form_layout.addRow("Google:", self.google_api_key)

        # Groq API Key
        self.groq_api_key = QLineEdit()
        self.groq_api_key.setEchoMode(QLineEdit.Password)
        self.groq_api_key.setText(os.getenv("GROQ_API_KEY", ""))
        self.groq_api_key.setStyleSheet(f"""
            QLineEdit {{
                background-color: {INPUT_BG_COLOR};
                color: {INPUT_TEXT_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 5px;
                padding: 5px;
                font-size: 12px;
                height: 24px;
            }}
        """)
        form_layout.addRow("Groq:", self.groq_api_key)

        # OpenRouter API Key
        self.openrouter_api_key = QLineEdit()
        self.openrouter_api_key.setEchoMode(QLineEdit.Password)
        self.openrouter_api_key.setText(os.getenv("OPENROUTER_API_KEY", ""))
        self.openrouter_api_key.setStyleSheet(f"""
            QLineEdit {{
                background-color: {INPUT_BG_COLOR};
                color: {INPUT_TEXT_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 5px;
                padding: 5px;
                font-size: 12px;
                height: 24px;
            }}
        """)
        form_layout.addRow("OpenRouter:", self.openrouter_api_key)

        layout.addLayout(form_layout)

        # Add spacer
        layout.addStretch()

        # Save button
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)

        self.save_button = QPushButton("Save")
        self.save_button.setFixedSize(80, 28)
        self.save_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {BUBBLE_USER_COLOR};
                color: {TEXT_COLOR_PRIMARY};
                border: none;
                border-radius: 5px;
                padding: 5px;
                font-size: 12px;
            }}
            QPushButton:hover {{ background-color: {BUTTON_HOVER_COLOR}; }}
        """)
        self.save_button.clicked.connect(self.save_settings)

        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        layout.addLayout(button_layout)

        # Set label style
        self.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_COLOR_SECONDARY};
                font-size: 12px;
            }}
        """)

        # Shadow effect
        self.setGraphicsEffect(self.create_shadow_effect())

    def create_shadow_effect(self):
        shadow = QGraphicsOpacityEffect()
        shadow.setOpacity(0.99)
        return shadow

    def save_settings(self):
        # Get the .env file path
        env_path = find_dotenv()
        if not env_path:
            # If .env doesn't exist, create it in the current directory
            env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
            open(env_path, 'a').close()  # Create empty file if doesn't exist

        # Update global variables
        global GOOGLE_API_KEY, GROQ_API_KEY, OPENROUTER_API_KEY
        GOOGLE_API_KEY = self.google_api_key.text()
        GROQ_API_KEY = self.groq_api_key.text()
        OPENROUTER_API_KEY = self.openrouter_api_key.text()

        # Update .env file
        try:
            # Write the API keys to .env file
            with open(env_path, 'w') as f:
                f.write(f"GOOGLE_API_KEY={GOOGLE_API_KEY}\n")
                f.write(f"GROQ_API_KEY={GROQ_API_KEY}\n")
                f.write(f"OPENROUTER_API_KEY={OPENROUTER_API_KEY}\n")

            print(f"{GREEN}API keys saved successfully{RESET}")
            self.accept()
        except Exception as e:
            print(f"{RED}Error saving API keys: {e}{RESET}")
            self.reject()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragPos = event.globalPosition().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if hasattr(self, '_dragPos') and self._dragPos is not None and event.buttons() & Qt.LeftButton:
            delta = event.globalPosition().toPoint() - self._dragPos
            self.move(self.pos() + delta)
            self._dragPos = event.globalPosition().toPoint()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if hasattr(self, '_dragPos'):
            self._dragPos = None
        super().mouseReleaseEvent(event)

# =============== UI ELEMENTS ===============

class ChatBubble(QFrame):
    def __init__(self, text, role="user", parent=None):
        super().__init__(parent)
        self.text = text
        self.role = role
        self.setObjectName("ChatBubble")
        bg_color = BUBBLE_AI_COLOR if self.role == "assistant" else BUBBLE_USER_COLOR

        # Parse the content for any code blocks
        self.parts = parse_text_for_code_blocks(text)

        self.setStyleSheet(f"""
            QFrame#ChatBubble {{
                background-color: {bg_color};
                border-radius: 8px;
                padding: 8px 10px;
                border: 1px solid {BORDER_COLOR};
            }}
            QLabel {{
                color: {TEXT_COLOR_PRIMARY};
                font-size: 14px;
                background-color: transparent;
            }}
        """)

        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)  # Add some spacing between segments

        # Process each part (either text or code block)
        for is_code, content, language in self.parts:
            if is_code:
                # Create code block widget
                code_block = CodeBlockWidget(content, language, self)
                layout.addWidget(code_block)
            else:
                # Create regular text label
                text_label = QLabel(content, self)
                text_label.setWordWrap(True)
                text_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
                layout.addWidget(text_label)

class LoadingBubble(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("LoadingBubble")
        self.setMinimumWidth(36)
        self.setStyleSheet(f"""
            QFrame#LoadingBubble {{
                background-color: {BUBBLE_AI_COLOR};
                border-radius: 8px; /* Less rounded */
                padding: 8px 10px;
                border: 1px solid {BORDER_COLOR};
            }}
            QLabel {{
                color: {TEXT_COLOR_PRIMARY};
                font-size: 14px;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.label = QLabel("", self)
        self.label.setWordWrap(True)
        layout.addWidget(self.label)
        self.states = [".", "..", "...", "....", "....."]
        self.index = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_dots)
        self.timer.start(500)

    def update_dots(self):
        self.label.setText(self.states[self.index])
        self.index = (self.index + 1) % len(self.states)

    def stop_animation(self):
        self.timer.stop()

class ChatArea(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ChatArea")
        self.setStyleSheet(f"QWidget#ChatArea {{ background-color: transparent; }}")
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignTop)
        self.layout.setSpacing(10) # Increased spacing between messages
        self.layout.setContentsMargins(15, 15, 15, 15) # Adjusted margins

    def add_message(self, text, role="user", engine=None):
        bubble = ChatBubble(text, role=role, parent=self)
        available_width = (self.width() - 120) if self.width() > 120 else 380 # Adjusted width calculation for margins
        bubble.setMaximumWidth(available_width)

        bubble.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        bubble.adjustSize()

        extra_padding = 0
        bubble.setMinimumHeight(bubble.sizeHint().height() + extra_padding)
        bubble.updateGeometry()

        if role == "assistant":
            header_text = engine if engine else "Nexlify" # Updated header
            header_alignment = Qt.AlignLeft
        else:
            header_text = "You"
            header_alignment = Qt.AlignRight

        header_label = QLabel(header_text)
        header_label.setStyleSheet(f"color: {TEXT_COLOR_SECONDARY}; font-size: 11px;") # Softer header text
        header_label.setAlignment(header_alignment)

        hbox = QHBoxLayout()
        if role == "assistant":
            hbox.setContentsMargins(0, 0, 80, 0) # Adjusted margins for alignment
            hbox.setAlignment(Qt.AlignLeft)
        else:
            hbox.setContentsMargins(80, 0, 0, 0) # Adjusted margins for alignment
            hbox.setAlignment(Qt.AlignRight)
        hbox.addWidget(bubble)

        bubble_container = QWidget()
        bubble_container.setLayout(hbox)

        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(2) # Spacing between header and bubble
        vbox.addWidget(header_label)
        vbox.addWidget(bubble_container)

        index = self.layout.count()
        self.layout.insertWidget(index, container)

    def add_loading_bubble(self):
        lb = LoadingBubble(parent=self)
        available_width = (self.width() - 120) if self.width() > 120 else 380 # Adjusted width calculation
        lb.setMaximumWidth(available_width)
        header_label = QLabel(CURRENT_MODEL) # Model name as header for loading
        header_label.setStyleSheet(f"color: {TEXT_COLOR_SECONDARY}; font-size: 11px;") # Softer header text
        header_label.setAlignment(Qt.AlignLeft)
        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 80, 0) # Adjusted margins
        hbox.setAlignment(Qt.AlignLeft)
        hbox.addWidget(lb)
        bubble_container = QWidget()
        bubble_container.setLayout(hbox)
        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(2) # Spacing between header and bubble
        vbox.addWidget(header_label)
        vbox.addWidget(bubble_container)
        index = self.layout.count()
        self.layout.insertWidget(index, container)
        return container, lb

    def resizeEvent(self, event):
        super().resizeEvent(event)
        new_max = (self.width() - 120) if self.width() > 120 else 380 # Adjusted width calculation
        for i in range(self.layout.count()):
            container = self.layout.itemAt(i).widget()
            if container:
                vlayout = container.layout()
                if vlayout is not None and vlayout.count() >= 2:
                    bubble_container = vlayout.itemAt(1).widget()
                    if bubble_container and bubble_container.layout() is not None and bubble_container.layout().count() > 0:
                        bubble = bubble_container.layout().itemAt(0).widget()
                        if bubble:
                            bubble.setMaximumWidth(new_max)
                            bubble.updateGeometry()

class ChatDialog(QWidget):
    def __init__(self, host_window):
        global conversation_messages
        super().__init__()
        self.host_window = host_window
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.main_frame = QFrame()
        self.main_frame.setObjectName("ChatDialogFrame")
        self.main_frame.setStyleSheet(f"""
            QFrame#ChatDialogFrame {{
                background-color: {FRAME_BG_COLOR};
                border-radius: 12px; /* Slightly more rounded frame */
            }}
        """)

        main_layout = QVBoxLayout(self.main_frame)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.chat_area = ChatArea()
        self.scroll = QScrollArea()
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.chat_area)
        self.scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background: transparent;
            }}
            QScrollBar:vertical {{
                background: {SCROLLBAR_BG_COLOR};
                width: 6px; /* Thinner scrollbar */
                margin: 40px 0 0 0;
                border-radius: 3px;
            }}
            QScrollBar::handle:vertical {{
                background: {SCROLLBAR_HANDLE_COLOR};
                border-radius: 3px;
            }}
            QScrollBar::sub-page:vertical, QScrollBar::add-page:vertical {{
                background: {SCROLLBAR_BG_COLOR};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                height: 0;
                width: 0;
            }}
        """)
        self.scroll.viewport().setStyleSheet("background: transparent;")

        self.reply_frame = QFrame()
        self.reply_frame.setObjectName("ChatReplyFrame")
        self.reply_frame.setStyleSheet(f"""
            QFrame#ChatReplyFrame {{
                background-color: transparent;
                padding: 10px 15px; /* Padding around input area */
            }}
            QLineEdit {{
                background-color: {INPUT_BG_COLOR};
                color: {INPUT_TEXT_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 6px; /* Slightly rounded input */
                padding: 8px; /* Adjusted input padding */
                font-size: 14px;
            }}
            QToolButton {{
                background-color: transparent; /* No background for send button */
                border: none;
                color: {TEXT_COLOR_PRIMARY};
                padding: 6px 10px;
                border-radius: 6px;
                font-size: 16px; /* Slightly larger send icon */
            }}
            QToolButton:hover {{ background-color: {BUTTON_HOVER_COLOR}; border-radius: 6px; }}
        """)
        reply_layout = QHBoxLayout(self.reply_frame)
        reply_layout.setContentsMargins(0, 0, 0, 0)
        reply_layout.setSpacing(10) # Spacing between input and send button
        self.reply_line = QLineEdit()
        self.reply_line.setPlaceholderText("Type your message...")
        reply_layout.addWidget(self.reply_line, stretch=1)
        self.reply_send_button = QToolButton()
        self.reply_send_button.setText("↑") # Using simple arrow for send
        self.reply_send_button.setToolTip("Send Message")
        reply_layout.addWidget(self.reply_send_button)
        self.reply_send_button.clicked.connect(self.handle_reply_send)
        self.reply_line.returnPressed.connect(self.handle_reply_send)

        main_layout.addWidget(self.scroll)
        main_layout.addWidget(self.reply_frame)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(self.main_frame)

        self.setMinimumHeight(300)
        self.setMinimumWidth(350) # Slightly wider default width
        self.resize(450, 350) # Adjusted default size
        self.size_grip = QSizeGrip(self)
        self.size_grip.setFixedSize(20, 20) # Smaller size grip

        # Set a default font for a cleaner look (Roboto Light)
        app_font = QFont("Roboto", 10) # Use "Roboto" font family
        app_font.setWeight(QFont.Weight.Light) # Set weight to Light
        self.setFont(app_font)
        self.chat_area.setFont(app_font)
        self.reply_line.setFont(app_font)
        self.reply_send_button.setFont(app_font)

        # Initialize with a system message
        conversation_messages = [{"role": "system", "content": "You are a helpful assistant."}]

    def showEvent(self, event):
        super().showEvent(event)
        if self.host_window and hasattr(self.host_window, "update_chat_toggle_button"):
            self.host_window.update_chat_toggle_button()

    def hideEvent(self, event):
        super().hideEvent(event)
        if self.host_window and hasattr(self.host_window, "update_chat_toggle_button"):
            self.host_window.update_chat_toggle_button()

    def resizeEvent(self, event):
        global last_chat_geometry
        super().resizeEvent(event)
        self.size_grip.move(self.width() - self.size_grip.width() - 5, # Adjusted size grip position
                            self.height() - self.size_grip.height() - 5)
        last_chat_geometry = self.geometry()

    def scroll_to_bottom(self):
        QTimer.singleShot(50, lambda: self.scroll.verticalScrollBar().setValue(
            self.scroll.verticalScrollBar().maximum() + 50
        ))

    def add_message(self, text, role="user", engine=None):
        self.chat_area.add_message(text, role=role, engine=engine)
        self.scroll_to_bottom()

    def add_loading_bubble(self):
        container, lb = self.chat_area.add_loading_bubble()
        self.scroll_to_bottom()
        return container, lb

    def reposition(self):
        if not self.host_window:
            return

        host_geom = self.host_window.geometry()
        dialog_geom = self.geometry()

        target_x = host_geom.x() + (host_geom.width() - dialog_geom.width()) // 2
        target_y = host_geom.y() + host_geom.height() + 5 # Slightly more offset

        animation = QPropertyAnimation(self, b"pos")
        animation.setDuration(250) # Slightly faster animation
        animation.setStartValue(self.pos())
        animation.setEndValue(QPoint(target_x, target_y))
        animation.setEasingCurve(QEasingCurve.OutCubic)
        animation.start()

        self._reposition_animation = animation

    def clear_chat(self):
        layout = self.chat_area.layout
        while layout.count() > 0:
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def handle_reply_send(self):
        text = self.reply_line.text().strip()
        if text:
            global CURRENT_MODEL
            self.add_message(text, role="user")
            self.reply_line.clear()
            container, lb = self.add_loading_bubble()
            def do_ai_work():
                try:
                    ai_reply = self.get_ai_response(text)
                except Exception as e:
                    print(f"{RED}Error in AI thread:", e)
                    ai_reply = f"[Error: {e}]"
                self.host_window.response_ready.emit(ai_reply, container, lb)
            th = threading.Thread(target=do_ai_work, daemon=True)
            th.start()

    def get_ai_response(self, prompt):
        global CURRENT_MODEL
        selected_model = CURRENT_MODEL
        if selected_model == "Gemini":
            return self.get_gemini_response(prompt)
        elif selected_model == "Gemini Lite":
            return self.get_gemini_lite_response(prompt)
        elif selected_model == "R1 Groq":
            return self.get_groq_response(prompt)
        elif selected_model == "Mistral":
            return self.get_mistral_response(prompt)
        elif selected_model == "Llama":
            return self.get_llama_response(prompt)
        elif selected_model == "R1":
            return self.get_r1_response(prompt)
        elif selected_model == "DS-V3":
            return self.get_dsv3_response(prompt)
        else:
            return "Invalid model selected."

    def get_gemini_response(self, prompt):
        global GOOGLE_API_KEY
        genai.configure(api_key=GOOGLE_API_KEY)
        gemini_model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')
        try:
            response = gemini_model.generate_content(prompt)
            ai_response = response.text
            return ai_response
        except Exception as e:
            error_message = f"Error from Gemini API: {e}"
            print(error_message)
            return error_message

    def get_gemini_lite_response(self, prompt):
        global GOOGLE_API_KEY
        genai.configure(api_key=GOOGLE_API_KEY)
        gemini_lite_model = genai.GenerativeModel('gemini-2.0-flash-lite-001')
        try:
            response = gemini_lite_model.generate_content(prompt)
            ai_response = response.text
            return ai_response
        except Exception as e:
            error_message = f"Error from Gemini Lite API: {e}"
            print(error_message)
            return error_message

    def get_groq_response(self, prompt):
        global GROQ_API_KEY
        try:
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "Deepseek-R1-Distill-Qwen-32b",
                "messages": [{"role": "user", "content": prompt}]
            }
            response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
            response.raise_for_status()
            ai_response_data = response.json()
            ai_response = ai_response_data['choices'][0]['message']['content']
            return ai_response
        except requests.exceptions.RequestException as e:
            error_message = f"Error from Groq API: {e}"
            print(error_message)
            return error_message
        except KeyError as e:
            error_message = f"Error parsing Groq response (KeyError): {e}"
            print(error_message)
            return error_message
        except Exception as e:
            error_message = f"Unexpected error with Groq API: {e}"
            print(error_message)
            return error_message

    def get_mistral_response(self, prompt):
        global OPENROUTER_API_KEY
        if not OPENROUTER_API_KEY:
            error_message = "OPENROUTER_API_KEY is not set in environment variables."
            print(f"{RED}{error_message}{RESET}")
            return error_message
        try:
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "cognitivecomputations/dolphin3.0-r1-mistral-24b:free",
                "messages": [{"role": "user", "content": prompt}]
            }
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
            response.raise_for_status()
            ai_response_data = response.json()
            ai_response = ai_response_data['choices'][0]['message']['content']
            return ai_response
        except requests.exceptions.RequestException as e:
            error_message = f"Error from OpenRouter API: {e}"
            print(f"{RED}{error_message}{RESET}")
            return error_message
        except KeyError as e:
            error_message = f"Error parsing OpenRouter response (KeyError): {e}"
            print(f"{RED}{error_message}{RESET}")
            return error_message
        except Exception as e:
            error_message = f"Unexpected error with OpenRouter API: {e}"
            print(f"{RED}{error_message}{RESET}")
            return error_message

    def get_llama_response(self, prompt):
        global OPENROUTER_API_KEY
        if not OPENROUTER_API_KEY:
            error_message = "OPENROUTER_API_KEY is not set in environment variables."
            print(f"{RED}{error_message}{RESET}")
            return error_message
        try:
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "meta-llama/llama-3.3-70b-instruct:free",
                "messages": [{"role": "user", "content": prompt}]
            }
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
            response.raise_for_status()
            ai_response_data = response.json()
            ai_response = ai_response_data['choices'][0]['message']['content']
            return ai_response
        except requests.exceptions.RequestException as e:
            error_message = f"Error from OpenRouter API: {e}"
            print(f"{RED}{error_message}{RESET}")
            return error_message
        except KeyError as e:
            error_message = f"Error parsing OpenRouter response (KeyError): {e}"
            print(f"{RED}{error_message}{RESET}")
            return error_message
        except Exception as e:
            error_message = f"Unexpected error with OpenRouter API: {e}"
            print(f"{RED}{error_message}{RESET}")
            return error_message

    def get_r1_response(self, prompt):
        global OPENROUTER_API_KEY
        if not OPENROUTER_API_KEY:
            error_message = "OPENROUTER_API_KEY is not set in environment variables."
            print(f"{RED}{error_message}{RESET}")
            return error_message
        try:
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "deepseek/deepseek-r1:free",
                "messages": [{"role": "user", "content": prompt}]
            }
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
            response.raise_for_status()
            ai_response_data = response.json()
            ai_response = ai_response_data['choices'][0]['message']['content']
            return ai_response
        except requests.exceptions.RequestException as e:
            error_message = f"Error from OpenRouter API: {e}"
            print(f"{RED}{error_message}{RESET}")
            return error_message
        except KeyError as e:
            error_message = f"Error parsing OpenRouter response (KeyError): {e}"
            print(f"{RED}{error_message}{RESET}")
            return error_message
        except Exception as e:
            error_message = f"Unexpected error with OpenRouter API: {e}"
            print(f"{RED}{error_message}{RESET}")
            return error_message

    def get_dsv3_response(self, prompt):
        global OPENROUTER_API_KEY
        if not OPENROUTER_API_KEY:
            error_message = "OPENROUTER_API_KEY is not set in environment variables."
            print(f"{RED}{error_message}{RESET}")
            return error_message
        try:
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "deepseek/deepseek-chat:free",
                "messages": [{"role": "user", "content": prompt}]
            }
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
            response.raise_for_status()
            ai_response_data = response.json()
            ai_response = ai_response_data['choices'][0]['message']['content']
            return ai_response
        except requests.exceptions.RequestException as e:
            error_message = f"Error from OpenRouter API: {e}"
            print(f"{RED}{error_message}{RESET}")
            return error_message
        except KeyError as e:
            error_message = f"Error parsing OpenRouter response (KeyError): {e}"
            print(f"{RED}{error_message}{RESET}")
            return error_message
        except Exception as e:
            error_message = f"Unexpected error with OpenRouter API: {e}"
            print(f"{RED}{error_message}{RESET}")
            return error_message

class BottomBubble(QFrame):
    send_message = Signal(str)
    open_settings = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("BottomBubble")
        self.setFixedHeight(50) # Reduced height

        self.setStyleSheet(f"""
            QFrame#BottomBubble {{
                background-color: {BG_COLOR};
                border-radius: 10px; /* Less rounded bottom bubble */
                padding: 5px; /* Reduced padding */
            }}
            QLineEdit {{
                background-color: {INPUT_BG_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 5px; /* Less rounded input */
                color: {INPUT_TEXT_COLOR};
                padding: 6px 8px;
                font-size: 14px;
            }}
            QLineEdit:focus {{ border: 1px solid {TEXT_COLOR_SECONDARY}; }}
            QToolButton#ModelButton {{ /* Style for the Model Button */
                background-color: transparent;
                border: none;
                color: {TEXT_COLOR_SECONDARY};
                font-size: 13px; /* Slightly smaller model text */
                padding: 2px 6px;
                border-radius: 5px;
            }}
            QToolButton#ModelButton:hover {{
                background-color: {MODEL_BUTTON_HOVER};
                border-radius: 5px;
            }}
            QToolButton#SendButton, QToolButton#SettingsButton {{ /* Style for the Send and Settings Buttons */
                background-color: transparent;
                border: none;
                color: {TEXT_COLOR_PRIMARY};
                font-size: 16px;
                padding: 2px 6px;
                border-radius: 5px;
            }}
            QToolButton#SendButton:hover, QToolButton#SettingsButton:hover {{
                background-color: {BUTTON_HOVER_COLOR};
                border-radius: 5px;
            }}
            QLabel#LogoLabel {{ /* Style for logo label */
                padding: 2px;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5) # Reduced margins
        layout.setSpacing(8) # Reduced spacing

        # Add Logo Label with embedded icon if file not found
        self.logo_label = QLabel()
        self.logo_label.setObjectName("LogoLabel")
        icon = self.load_app_logo()
        if icon:
            pixmap = icon.pixmap(24, 24)
            self.logo_label.setPixmap(pixmap)
        else:
            self.logo_label.setText("Nexlify")
            self.logo_label.setStyleSheet(f"color: {TEXT_COLOR_PRIMARY}; font-weight: bold;")

        self.logo_label.setToolTip("Nexlify by sufyxxn")
        layout.addWidget(self.logo_label)

        # Add Settings Button next to logo
        self.settings_button = QToolButton()
        self.settings_button.setObjectName("SettingsButton")
        self.settings_button.setText("⚙") # Gear icon for settings
        self.settings_button.setToolTip("Settings")
        self.settings_button.clicked.connect(self.on_settings_clicked)
        layout.addWidget(self.settings_button)

        # Add Spacer after logo and settings
        layout.addItem(QSpacerItem(5, 0, QSizePolicy.Fixed, QSizePolicy.Minimum))

        self.model_button = QToolButton()
        self.model_button.setObjectName("ModelButton")
        self.model_button.setText(CURRENT_MODEL)
        self.model_button.setToolTip("Click to switch model")
        self.model_button.clicked.connect(self.cycle_model)
        layout.addWidget(self.model_button)

        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("Enter prompt...")
        layout.addWidget(self.input_line, stretch=1)

        self.send_button = QToolButton()
        self.send_button.setObjectName("SendButton")
        self.send_button.setText("↑") # Simple arrow icon
        self.send_button.setToolTip("Send")
        self.send_button.clicked.connect(self.handle_send)
        layout.addWidget(self.send_button)

        self.input_line.returnPressed.connect(self.handle_send)

    def load_app_logo(self):
        """Load application logo with fallbacks"""
        # Try to load from file first
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            logo_path = os.path.join(script_dir, "logo.png")
            if os.path.exists(logo_path):
                return QIcon(logo_path)
        except Exception as e:
            print(f"{YELLOW}Could not load logo from file: {e}{RESET}")

        # If file loading fails, use embedded icon
        return get_embedded_icon()

    def on_settings_clicked(self):
        self.open_settings.emit()

    def handle_send(self):
        global CURRENT_MODEL
        text = self.input_line.text().strip()
        if text:
            self.send_message.emit(text)
            self.input_line.clear()

    def update_model_display(self):
        metrics = QFontMetrics(self.model_button.font())
        elided = metrics.elidedText(CURRENT_MODEL, Qt.ElideRight, self.model_button.width())
        self.model_button.setText(elided)

    def cycle_model(self):
        global CURRENT_MODEL_INDEX, CURRENT_MODEL, MODEL_OPTIONS
        CURRENT_MODEL_INDEX = (CURRENT_MODEL_INDEX + 1) % len(MODEL_OPTIONS)
        CURRENT_MODEL = MODEL_OPTIONS[CURRENT_MODEL_INDEX]
        self.update_model_display()
        save_config()

class BottomBubbleWindow(QWidget):
    global last_chat_geometry
    response_ready = Signal(str, object, object)

    def __init__(self):
        global last_main_geometry, last_chat_geometry
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.response_ready.connect(self.update_ai_reply)
        self.setStyleSheet(f"QWidget {{ background-color: {BG_COLOR}; }}")

        self.chat_dialog = ChatDialog(host_window=self)
        if last_chat_geometry:
            self.chat_dialog.setGeometry(last_chat_geometry)
        self.chat_dialog.hide()

        if last_main_geometry is not None:
            self.setGeometry(last_main_geometry)
        self.resize(450, 80) # Reduced initial height
        self._dragPos = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0) # Minimal margins for main window
        layout.setSpacing(0)
        layout.addStretch()

        self.bottom_bubble = BottomBubble(self)
        layout.addWidget(self.bottom_bubble)
        self.bottom_bubble.update_model_display()

        # Connect settings button signal
        self.bottom_bubble.open_settings
        # Connect settings button signal
        self.bottom_bubble.open_settings.connect(self.show_settings_dialog)

        self.close_button = QPushButton("✕", self)
        self.close_button.setToolTip("Close")
        self.close_button.setFixedSize(20, 20) # Smaller close button
        self.close_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {CLOSE_BUTTON_BG};
                border: none;
                color: {TEXT_COLOR_PRIMARY};
                border-radius: 10px;
                font-size: 10px;
            }}
            QPushButton:hover {{ background-color: {CLOSE_BUTTON_HOVER}; }}
        """)
        self.close_button.clicked.connect(self.close_all)

        self.chat_dialog = ChatDialog(host_window=self)
        if last_chat_geometry:
            self.chat_dialog.setGeometry(last_chat_geometry)
        self.chat_dialog.hide()

        self.bottom_bubble.send_message.connect(self.on_message_sent)

    def show_settings_dialog(self):
        dialog = SettingsDialog(self)
        # Calculate position to center dialog over the main window
        dialog_pos = self.mapToGlobal(QPoint(
            (self.width() - dialog.width()) // 2,
            (self.height() - dialog.height()) // 2 - 50  # Slightly above center
        ))
        dialog.move(dialog_pos)
        dialog.exec()
        # After dialog closes, reload API keys in case they were changed
        global GOOGLE_API_KEY, GROQ_API_KEY, OPENROUTER_API_KEY
        load_dotenv(override=True)
        GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

    def close_all(self):
        self.chat_dialog.hide()
        self.close()

    def resizeEvent(self, event):
        global last_main_geometry, last_chat_geometry
        super().resizeEvent(event)
        last_main_geometry = self.geometry()
        if self.chat_dialog.isVisible():
            last_chat_geometry = self.chat_dialog.geometry()
        self.close_button.move(self.width() - self.close_button.width() - 3, 3) # Adjusted close button position
        self.update_chat_dialog_geometry()
        self.bottom_bubble.update_model_display()

    def moveEvent(self, event):
        global last_main_geometry, last_chat_geometry
        super().moveEvent(event)
        last_main_geometry = self.geometry()
        if self.chat_dialog.isVisible():
            last_chat_geometry = self.chat_dialog.geometry()
        self.update_chat_dialog_geometry()

    def update_chat_dialog_geometry(self):
        if self.chat_dialog.isVisible():
            self.chat_dialog.reposition()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragPos = event.globalPosition().toPoint()
        super().mousePressEvent(event)
        if self.chat_dialog.isVisible():
            self.chat_dialog.raise_()
            self.chat_dialog.activateWindow()
        self.raise_()
        self.activateWindow()

    def mouseMoveEvent(self, event):
        if self._dragPos is not None and event.buttons() & Qt.LeftButton:
            delta = event.globalPosition().toPoint() - self._dragPos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self._dragPos = event.globalPosition().toPoint()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._dragPos = None
        super().mouseReleaseEvent(event)

    def on_message_sent(self, text):
        window_is_visible = self.isVisible()

        if window_is_visible and not self.chat_dialog.isVisible():
            self.chat_dialog.show()
            self.chat_dialog.reposition()

        self.chat_dialog.clear_chat()
        self.chat_dialog.add_message(text, role="user")

        QTimer.singleShot(100, lambda: self.chat_dialog.reply_line.setFocus())
        container, lb = self.chat_dialog.add_loading_bubble()

        threading.Thread(
            target=self.process_ai_reply,
            args=(text, container, lb),
            daemon=True
        ).start()

    def process_ai_reply(self, text, container, lb):
        try:
            ai_reply = self.chat_dialog.get_ai_response(text)
        except Exception as e:
            print(f"{RED}Error in AI thread: {e}")
            ai_reply = f"[Error: {e}]"
        self.response_ready.emit(ai_reply, container, lb)

    @Slot(str, object, object)
    def update_ai_reply(self, ai_reply, container, lb):
        global CURRENT_MODEL
        if lb is not None:
            lb.stop_animation()

        self.chat_dialog.chat_area.layout.removeWidget(container)
        container.deleteLater()

        # Add the formatted message with code blocks support
        self.chat_dialog.add_message(ai_reply, role="assistant", engine=CURRENT_MODEL)


# =============== SYSTEM TRAY IMPLEMENTATION ===============
class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, icon, parent=None):
        super().__init__(icon, parent)
        self.menu = QMenu(parent)

        show_action = QAction("Show/Hide Nexlify", self)
        show_action.triggered.connect(toggle_window)

        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.open_settings)

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.quit)

        self.menu.addAction(show_action)
        self.menu.addAction(settings_action)
        self.menu.addSeparator()
        self.menu.addAction(quit_action)

        self.setContextMenu(self.menu)
        self.activated.connect(self.on_tray_activated)
        self.setToolTip("Nexlify AI Assistant")

    def open_settings(self):
        global current_window
        if current_window:
            current_window.show_settings_dialog()
        else:
            toggle_window()
            QTimer.singleShot(500, lambda: current_window.show_settings_dialog())

    def on_tray_activated(self, reason):
        # Toggle window when clicking the tray icon
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            toggle_window()


# =============== TOGGLE WINDOW ===============

current_window = None
def toggle_window():
    global current_window, last_main_geometry, last_chat_geometry
    try:
        if current_window is None:
            current_window = BottomBubbleWindow()
            if last_main_geometry is not None:
                current_window.setGeometry(last_main_geometry)
            if last_chat_geometry is not None and current_window.chat_dialog.isVisible():
                current_window.chat_dialog.setGeometry(last_chat_geometry)
            current_window.show()
            current_window.raise_()
            current_window.activateWindow()
            current_window.bottom_bubble.input_line.setFocus()
            if current_window.chat_dialog.isVisible():
                current_window.chat_dialog.raise_()
        else:
            if current_window.isVisible():
                last_main_geometry = current_window.geometry()
                if current_window.chat_dialog.isVisible():
                    last_chat_geometry = current_window.chat_dialog.geometry()
                    current_window.chat_dialog.hide()
                current_window.hide()
            else:
                current_window.show()
                current_window.raise_()
                current_window.activateWindow()
                current_window.bottom_bubble.input_line.setFocus()
    except RuntimeError:
        current_window = BottomBubbleWindow()
        if last_main_geometry is not None:
            current_window.setGeometry(last_main_geometry)
        if last_chat_geometry is not None and current_window.chat_dialog.isVisible():
            current_window.chat_dialog.setGeometry(last_chat_geometry)
        current_window.show()
        current_window.raise_()
        current_window.activateWindow()
        current_window.bottom_bubble.input_line.setFocus()


# =============== MAIN ENTRY POINT ===============

def main():
    """
    Main function to launch the Nexlify application.
    No root privileges required - uses only system tray functionality.
    Modified: 2025-03-05 09:06:05 by sufyxxn
    """
    load_config()
    app = QApplication(sys.argv)

    # Set application information for Windows taskbar
    app.setApplicationName("Nexlify")
    app.setApplicationDisplayName("Nexlify AI Assistant")
    app.setOrganizationName("sufyxxn")
    app.setOrganizationDomain("nexlify.ai")

    # --- Cross-platform icon loading with multiple fallbacks ---
    icon = None

    # Try option 1: Load from file path
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(script_dir, "logo.png")

        if os.path.exists(logo_path):
            print(f"Loading icon from: {logo_path}")
            icon = QIcon(logo_path)
            if icon.isNull():
                print(f"{RED}Icon loaded but is null/empty{RESET}")
                icon = None
        else:
            print(f"{RED}Logo file not found at: {logo_path}{RESET}")
    except Exception as e:
        print(f"{RED}Error loading icon from file: {e}{RESET}")

    # Try option 2: Use embedded icon
    if icon is None or icon.isNull():
        print(f"{YELLOW}Using embedded icon{RESET}")
        icon = get_embedded_icon()

    # Try option 3: Last resort - create a basic icon
    if icon is None or icon.isNull():
        print(f"{RED}Creating basic fallback icon{RESET}")
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor("#2A2A2A"))  # Use app color scheme
        icon = QIcon(pixmap)

    # Set the application icon
    app.setWindowIcon(icon)

    # Create system tray icon
    tray_icon = SystemTrayIcon(icon)

    # Ensure the tray icon is visible and valid
    if not tray_icon.icon().isNull():
        tray_icon.show()
    else:
        print(f"{RED}Warning: System tray icon appears to be null{RESET}")
        # Final attempt - use a simple colored icon
        emergency_pixmap = QPixmap(32, 32)
        emergency_pixmap.fill(QColor("#1E1E1E"))
        tray_icon.setIcon(QIcon(emergency_pixmap))
        tray_icon.show()

    app.setQuitOnLastWindowClosed(False)  # Don't quit when all windows are closed
    print(f"{GREEN}Nexlify is running! Click the system tray icon to access the app.{RESET}")
    print(f"Current Date and Time (UTC): 2025-03-05 09:06:05")
    print(f"Current User: sufyxxn")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()