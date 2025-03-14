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
    QSequentialAnimationGroup, QParallelAnimationGroup, QSize, Signal, Slot, QMetaObject, QPoint, QEvent, QAbstractAnimation, QStringListModel
)
from PySide6.QtGui import QAction, QFontMetrics, QPainter, QPixmap, QIcon, QFont, QColor, QPalette, QSyntaxHighlighter, QTextCharFormat, QGuiApplication, QTextCursor
from PySide6.QtWidgets import (
    QApplication, QWidget, QFrame, QVBoxLayout, QHBoxLayout,
    QComboBox, QLineEdit, QToolButton, QPushButton, QScrollArea,
    QSizePolicy, QLabel, QSpacerItem, QSizeGrip, QMenu, QGroupBox,
    QFormLayout, QSpinBox, QCheckBox, QWidgetAction, QStackedWidget, QStyle, QStyledItemDelegate, QToolTip, QTextEdit, QGraphicsOpacityEffect,
    QDialog, QDialogButtonBox, QSystemTrayIcon, QListWidget, QListWidgetItem, QListView, QCompleter
)
from dotenv import load_dotenv, set_key, find_dotenv


import markdown
import pickle
import uuid

# Create history folder
HISTORY_FOLDER = "history"
if not os.path.exists(HISTORY_FOLDER):
    os.makedirs(HISTORY_FOLDER)

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

conversation_messages = []
MODEL_OPTIONS = ["Gemini", "Gemini Lite", "R1 Groq", "Mistral", "Llama", "R1", "DS-V3", "QwQ"]
CURRENT_MODEL_INDEX = 0
CURRENT_MODEL = MODEL_OPTIONS[CURRENT_MODEL_INDEX]
ENABLE_SEARCH = True  # Default to True for online search
ENABLE_UPTIME_OPTIMIZER = True  # Default to True for uptime optimization

GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
CYAN = "\033[36m"
MAGENTA = "\033[35m"
RESET = "\033[0m"

last_main_geometry = None
last_chat_geometry = None

BG_COLOR = "#1E1E1E"
BUBBLE_USER_COLOR = "#333333"
BUBBLE_AI_COLOR = "#282828"
TEXT_COLOR_PRIMARY = "#EEEEEE"
TEXT_COLOR_SECONDARY = "#AAAAAA"
INPUT_BG_COLOR = "#2A2A2A"
INPUT_TEXT_COLOR = "#EEEEEE"
BORDER_COLOR = "#555555"
BUTTON_HOVER_COLOR = "#444444"
SCROLLBAR_BG_COLOR = "#333333"
SCROLLBAR_HANDLE_COLOR = "#666666"
CLOSE_BUTTON_BG = "#AA0000"
CLOSE_BUTTON_HOVER = "#FF0000"
FRAME_BG_COLOR = "rgba(30, 30, 30, 0.9)"
MODEL_BUTTON_HOVER = "#444444"
CODE_BLOCK_BG = "#1A1A1A"
CODE_BLOCK_BORDER = "#444444"
CODE_TEXT_COLOR = "#D4D4D4"
CODE_COMMENT_COLOR = "#6A9955"
CODE_KEYWORD_COLOR = "#569CD6"
CODE_STRING_COLOR = "#CE9178"

NEXLIFY_ICON_B64 = """
iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAG+ElEQVR4nO2bWYwUVRSGv1NdPTPdDcywDIuA7LKJIBiDIBoQgkYlokSJRhP1SXzQF2MkPqjxwQRjAokajYlGE8EFJMimgMiiIsgiwyLCwAwwzNZd1eXDuVXTM/RMV1VXD8bkT1VO6u5z7zn33HPPuQV9CGOiJ0C/VIRoz9D2GjtGBsAAc4GZwb2yAHsE2ABsMwK3IADGxMxke2t7SuJ7A4AQWAmsBOYkad8KrANWA7uDdJwxAMbE5gGrgRmpyHUDwr3AUmB60r9PAY8D25z3BwZgTGwhslzn9YawMTEXeAu4sJuyR4DVQKvzIGMAxkQt4E1gXjZ6jIluwPeAxUCPKgbYCTxjZ/u9DABoQAuSPrAACLtVZkzsMLAMKOhB3xpgjRGVcQIWw7xyVwJXZqtJQO4B5neT6x8BpRpQgEw7bkqxjHEDUBx876oDZaLSduJ3Z8p1BoCNrWPAnciKnYn2G2wASmxbXQj8gQDZCnzTjY5uVK4Ayuw29LDRl/ZfVgCDBiCjjHAOGBOOT/gU6Ovpqyd6nkCFdROABiTpGYsYLQCpOYAQsAOoylI+a0xNgGolMqUKu9E3AXgEuMD+3I6ksr8AR4F6oMH+3wqoCDC6GKgCxiD5fVuw/lLEXzwSfNcUNDbZ/4SCvgvsuiLAwELkbYWCPluCOloCHQ4ITQiQGmCv/b0JGDatodWmg5J4cwxYCAxNou0R4CdgB3J1bQa+BO4LSgwE+iPhYgpwYTCpHf6gW+6ydj9jTOwosBn4EHgdkRQG9gPvAz8AjwH3ApcCU5FIftE24i8dBHYKvDGxRmAD8BbwDoJ+aJBPtOBx9/2MAhgbHw9cnwKE5YgDc8jppwB4HngCuBu4KqOeI8B/QsZ8YBHwQErCrAEIAZchG5aLgdu7KVeC+I1bcISNif0G3NSNKGP/pidzn1H+akzsTGBxrwSIg0zk0sHAvX0g2wB1wDvIXfKvQKujfpTIDN8rzZjYMeA1ZET+FUAQmf2At4H7e1H8pB7i+pFJuxg4B3gJuDCDiciIbGH/IvJ1UF+gOxMu6NDaCfwOfJ+thlQ5FANIuu5BdiExJVsZRxaZAOiDdnlRYLvCu02SoDzg+8MYnhdx+iAUIMs9ha7jnZgKHAn8DIygseSyDsmTwBOalU4eHcwUkzZY8vVA4dxzz6JaA3a7AeAWgfEOUjMORyUOY67zZN0aOyXHQ3s2dcAJwK5VtxicjEdzi0JRqnMNrBcDSJofBhtoPXmnu8KwHDgKns5dEhQZhMygJcn0eHgDUvD5xwkArpnqoPooxyZSZ4ExiELY5n9bsA+Nwze9auSNbeWvDWaiGxyNrRVaO1vMwjwoSyMfEoQ9AgBFpGwNmf0T2QJPAo8h4zgJNuasUgaCHInGBs/DInRz9jtfIdYn5YWhYEyIMszRUdUFxQgDm0Mbv7NkPJs/dJ1iFleHoTleQ347fjeEWSRXB4ICHTILkBWfAMyanFzjX5ASRjGp0kaCbADcdReUDOidg7zE6rNIXlj4IH3IwHVoRrgFWPi30ToPLnIDtK9tjaOpwrbTRcZE7uqwvABZWaYQBrwF/CiMfE1wCJjYjGE922BN0c8+lWagYM8jC6BGfHYA7IoHSkk3R6g2RGwsTkM4woxg26Lpq0jGsy+IkQKZCE7x8PCxJ5GdoTPEYf4IzJSOdcC4FvgMWPi64H1KJdEedwSRv67stB/OsGrgmzZg+W9FrizAuPpBHn3BwGiDJiAWG4dsgD+ARwOI7PHajv/fxr4FJlulgA3ArObfC+TWX+DLKDe0AXIV8CnwJMIiAeAeWHE3K1JIvQO7hqYdmr8NOlJirC/0EXryKNwyZQwsBAJcOnUfwD4BQ299fPNWpMiD6PfzgE5lO8XQgxblwg/gGxje6OjHnF+gIDQKadxnk3lOZb1Ic9i+iPOK9VJrhbZvqbeIXZDjQjXZQjYvtJypL1mSxgmIhtXn5zbQkKsi8PJabg+80rEdnuiZUD/MAyIWYcQYB6S6ep/5r4X2o54+obg3mZb2opIDvbDHLJrhcDgSISx69Zl/R5P3m6DRlnhOgXyjq5Ypo0iiIccbC8yc9Q2R74UWNIY50AJFHV6qfC970NqGs6CTxAKTsNGA6/u3/3t/IJIrm0jiytpVqgUabPGCCgAw0vjBU3eb3vH1vSkFwZFogrSkLJiv2UBmk9fp6G7gGij8vLI18AlwJV5a/I52Q2rVGYJxARJlMaj0WrL8562LE8DT2m9I34UaAqdBCCrgFJlWZ6ylgJLtHZHSCmFpeIgbwXeC0WjsxCPXGKlsQvVWGmeBrZrfTIjpmpXdYExJv7vz/IU4gSfzuYTAOwf53Cpf/ri3Jj4OKATCIeUZR1Tlv9lbx1m+mRO636wFVLKL1JK3aS1vpTC2YAWBVXR9UXRHOv6BMTpTBdSyl8QiUR+NuZUT7f/A+8mkUBfqLg0AAAAAElFTkSuQmCC
"""

def get_embedded_icon():
    try:
        icon_data = base64.b64decode(NEXLIFY_ICON_B64)
        pixmap = QPixmap()
        pixmap.loadFromData(icon_data)
        return QIcon(pixmap)
    except Exception as e:
        print(f"{RED}Error creating embedded icon: {e}{RESET}")
        return None

def load_config():
    config_file = ".nexlify"
    if not os.path.exists(config_file):
        return
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
        global CURRENT_MODEL_INDEX, CURRENT_MODEL, ENABLE_SEARCH, ENABLE_UPTIME_OPTIMIZER
        CURRENT_MODEL_INDEX = config.get("CURRENT_MODEL_INDEX", CURRENT_MODEL_INDEX)
        CURRENT_MODEL = MODEL_OPTIONS[CURRENT_MODEL_INDEX]
        ENABLE_SEARCH = config.get("ENABLE_SEARCH", True)  # Default to True
        ENABLE_UPTIME_OPTIMIZER = config.get("ENABLE_UPTIME_OPTIMIZER", True)  # Default to True
    except Exception as e:
        print(f"{RED}Error loading config: {e}{RESET}")

def save_config():
    config_file = ".nexlify"
    try:
        global ENABLE_SEARCH, ENABLE_UPTIME_OPTIMIZER
        config = {
            "CURRENT_MODEL_INDEX": CURRENT_MODEL_INDEX,
            "ENABLE_SEARCH": ENABLE_SEARCH,
            "ENABLE_UPTIME_OPTIMIZER": ENABLE_UPTIME_OPTIMIZER
        }
        with open(config_file, "w", newline="", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"{RED}Error saving config: {e}{RESET}")

class CodeBlockWidget(QFrame):
    def __init__(self, code_text, language="", parent=None):
        super().__init__(parent)
        self.code_text = code_text
        self.language = language
        self.setup_ui()

    def setup_ui(self):
        # Create a minimal code block that matches the chat UI and example
        self.setObjectName("codeBlock")
        self.setStyleSheet("""
            #codeBlock {
                background-color: #1e1e1e;
                border-radius: 4px;
                border: 1px solid #333333;
                margin: 4px 0;
            }
            QLabel#languageLabel {
                color: #cccccc;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-size: 11px;
                padding: 3px 8px;
                background-color: #2a2a2a;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                border-bottom: 1px solid #333333;
            }
            QTextEdit#codeTextEdit {
                background-color: transparent;
                color: #e0e0e0;
                border: none;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 13px;
                selection-background-color: #3a3d41;
                padding: 8px;
                line-height: 1.4;
            }
            QPushButton#copyButton {
                background-color: transparent;
                color: #888888;
                border: none;
                padding: 2px 6px;
                font-size: 11px;
                margin-right: 4px;
            }
            QPushButton#copyButton:hover {
                color: #ffffff;
            }
        """)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header with language label and copy button
        header = QWidget()
        header.setObjectName("codeHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)

        # Language label (left side)
        lang_display = self.language.capitalize() if self.language else "Code"
        self.language_label = QLabel(lang_display)
        self.language_label.setObjectName("languageLabel")
        header_layout.addWidget(self.language_label)

        header_layout.addStretch()

        # Copy button (right side)
        self.copy_button = QPushButton("Copy")
        self.copy_button.setObjectName("copyButton")
        self.copy_button.setCursor(Qt.PointingHandCursor)
        self.copy_button.clicked.connect(self.copy_code_to_clipboard)
        header_layout.addWidget(self.copy_button)

        layout.addWidget(header)

        # Code text area
        self.code_text_edit = QTextEdit()
        self.code_text_edit.setObjectName("codeTextEdit")
        self.code_text_edit.setReadOnly(True)
        self.code_text_edit.setPlainText(self.code_text)
        self.code_text_edit.setLineWrapMode(QTextEdit.NoWrap)

        # Set a reasonable height based on content
        lines = self.code_text.count('\n') + 1
        line_height = 18  # Approximate height of a line in pixels

        # Calculate height: min 2 lines, max 15 lines, or actual content
        min_height = max(2 * line_height, min(lines * line_height, 15 * line_height))
        self.code_text_edit.setMinimumHeight(min_height)

        # Add subtle padding to the text edit
        self.code_text_edit.document().setDocumentMargin(8)

        layout.addWidget(self.code_text_edit)

        # Apply syntax highlighting if language is specified
        if self.language:
            self.apply_syntax_highlighting(self.language)

    def apply_syntax_highlighting(self, language):
        # Basic syntax highlighting for common languages
        language = language.lower()

        if language in ["python", "py"]:
            # Python syntax highlighting
            keywords = ["def", "class", "import", "from", "if", "elif", "else", "for", "while",
                       "return", "try", "except", "finally", "with", "as", "and", "or", "not", "in", "is", "None", "True", "False"]
            self.highlight_keywords(keywords, QColor("#569cd6"))  # Blue for keywords

            # Decorators
            self.highlight_pattern(r"@\w+", QColor("#dcdcaa"))  # Yellow for decorators

            # Function calls
            self.highlight_pattern(r"\b\w+(?=\()", QColor("#dcdcaa"))  # Yellow for function calls

            # Class names
            self.highlight_pattern(r"(?<=class\s)\w+", QColor("#4ec9b0"))  # Teal for class names

            # Self parameter
            self.highlight_pattern(r"\bself\b", QColor("#569cd6"))  # Blue for self

            # Highlight built-ins
            builtins = ["print", "len", "str", "int", "float", "bool", "list", "dict", "set", "tuple"]
            self.highlight_keywords(builtins, QColor("#4ec9b0"))  # Teal for built-ins

            # Highlight strings
            self.highlight_pattern(r'"[^"\\]*(\\.[^"\\]*)*"', QColor("#ce9178"))  # Orange for strings
            self.highlight_pattern(r"'[^'\\]*(\\.[^'\\]*)*'", QColor("#ce9178"))

            # Highlight comments
            self.highlight_pattern(r"#.*$", QColor("#6a9955"), multiline=False)  # Green for comments

            # Highlight numbers
            self.highlight_pattern(r"\b\d+\b", QColor("#b5cea8"))  # Light green for numbers

        elif language in ["javascript", "js", "typescript", "ts"]:
            # JavaScript/TypeScript syntax highlighting
            keywords = ["function", "const", "let", "var", "if", "else", "for", "while",
                       "return", "try", "catch", "finally", "class", "import", "export", "from"]
            self.highlight_keywords(keywords, QColor("#569cd6"))

            # Highlight built-ins
            builtins = ["console", "document", "window", "Math", "Array", "Object", "String"]
            self.highlight_keywords(builtins, QColor("#4ec9b0"))

            # Highlight strings
            self.highlight_pattern(r'"[^"\\]*(\\.[^"\\]*)*"', QColor("#ce9178"))
            self.highlight_pattern(r"'[^'\\]*(\\.[^'\\]*)*'", QColor("#ce9178"))
            self.highlight_pattern(r"`[^`\\]*(\\.[^`\\]*)*`", QColor("#ce9178"))

            # Highlight comments
            self.highlight_pattern(r"//.*$", QColor("#6a9955"), multiline=False)

            # Highlight numbers
            self.highlight_pattern(r"\b\d+\b", QColor("#b5cea8"))

        elif language in ["jsx", "react"]:
            # JSX/React syntax highlighting
            # Keywords
            keywords = ["function", "const", "let", "var", "if", "else", "for", "while",
                       "return", "try", "catch", "finally", "class", "import", "export", "from",
                       "extends", "default", "async", "await", "static", "get", "set"]
            self.highlight_keywords(keywords, QColor("#569cd6"))  # Blue for keywords

            # React specific
            react_keywords = ["useState", "useEffect", "useContext", "useReducer", "useCallback",
                             "useMemo", "useRef", "useImperativeHandle", "useLayoutEffect",
                             "useDebugValue", "Fragment", "Suspense", "lazy", "memo", "forwardRef"]
            self.highlight_keywords(react_keywords, QColor("#c586c0"))  # Purple for React hooks

            # JSX tags and attributes
            self.highlight_pattern(r"</?[a-zA-Z][a-zA-Z0-9]*", QColor("#4ec9b0"))  # Teal for JSX tags
            self.highlight_pattern(r"<[a-zA-Z][a-zA-Z0-9]*\s+[a-zA-Z][a-zA-Z0-9]*=", QColor("#9cdcfe"))  # Light blue for attributes

            # JSX brackets
            self.highlight_pattern(r"[{}]", QColor("#d7ba7d"))  # Gold for curly braces
            self.highlight_pattern(r"[<>]", QColor("#808080"))  # Gray for angle brackets

            # Strings
            self.highlight_pattern(r'"[^"\\]*(\\.[^"\\]*)*"', QColor("#ce9178"))  # Orange for strings
            self.highlight_pattern(r"'[^'\\]*(\\.[^'\\]*)*'", QColor("#ce9178"))
            self.highlight_pattern(r"`[^`\\]*(\\.[^`\\]*)*`", QColor("#ce9178"))

            # Comments
            self.highlight_pattern(r"//.*$", QColor("#6a9955"), multiline=False)  # Green for comments

            # Function calls
            self.highlight_pattern(r"\b[a-zA-Z_][a-zA-Z0-9_]*(?=\()", QColor("#dcdcaa"))  # Yellow for function calls

            # Props in JSX
            self.highlight_pattern(r"(?<==\{)[^{}]+(?=\})", QColor("#9cdcfe"))  # Light blue for props

            # Numbers
            self.highlight_pattern(r"\b\d+\b", QColor("#b5cea8"))  # Light green for numbers

        elif language in ["html", "xml"]:
            # HTML/XML syntax highlighting
            # Highlight tags
            self.highlight_pattern(r"</?[a-zA-Z0-9]+", QColor("#569cd6"))
            self.highlight_pattern(r">", QColor("#569cd6"))

            # Highlight attributes
            self.highlight_pattern(r'\s([a-zA-Z-]+)="', QColor("#9cdcfe"))

            # Highlight strings
            self.highlight_pattern(r'"[^"]*"', QColor("#ce9178"))

        elif language in ["css", "scss"]:
            # CSS syntax highlighting
            # Highlight selectors
            self.highlight_pattern(r"[.#]?[a-zA-Z0-9_-]+\s*{", QColor("#d7ba7d"))

            # Highlight properties
            self.highlight_pattern(r"[a-zA-Z-]+:", QColor("#9cdcfe"))

            # Highlight values
            self.highlight_pattern(r":\s*[^;]+;", QColor("#ce9178"))

            # Highlight numbers
            self.highlight_pattern(r"\b\d+[a-zA-Z%]*\b", QColor("#b5cea8"))

        elif language in ["latex", "tex"]:
            # LaTeX syntax highlighting
            # Highlight commands
            self.highlight_pattern(r"\\[a-zA-Z]+", QColor("#569cd6"))  # Blue for commands

            # Highlight environments
            self.highlight_pattern(r"\\begin{[^}]+}", QColor("#4ec9b0"))  # Teal for begin
            self.highlight_pattern(r"\\end{[^}]+}", QColor("#4ec9b0"))  # Teal for end

            # Highlight math delimiters
            self.highlight_pattern(r"\$[^$]+\$", QColor("#dcdcaa"))  # Yellow for inline math
            self.highlight_pattern(r"\\\[[^\]]+\]", QColor("#dcdcaa"))  # Yellow for display math
            self.highlight_pattern(r"\\\([^)]+\)", QColor("#dcdcaa"))  # Yellow for inline math

            # Highlight comments
            self.highlight_pattern(r"%.*$", QColor("#6a9955"), multiline=False)  # Green for comments

            # Highlight special characters
            self.highlight_pattern(r"[{}]", QColor("#ce9178"))  # Orange for braces

    def highlight_keywords(self, keywords, color):
        for keyword in keywords:
            pattern = r'\b' + keyword + r'\b'
            self.highlight_pattern(pattern, color)

    def highlight_pattern(self, pattern, color, multiline=True):
        try:
            cursor = self.code_text_edit.textCursor()
            format = QTextCharFormat()
            format.setForeground(color)

            text = self.code_text_edit.toPlainText()
            for match in re.finditer(pattern, text, re.MULTILINE if multiline else 0):
                start, end = match.span()
                cursor.setPosition(start)
                # Use the correct enum from QTextCursor
                cursor.setPosition(end, QTextCursor.KeepAnchor)
                cursor.setCharFormat(format)
                cursor.clearSelection()
        except Exception as e:
            print(f"Error in highlight_pattern: {e}")

    def copy_code_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.code_text_edit.toPlainText())

        # Show a temporary "Copied!" message
        original_text = self.copy_button.text()
        self.copy_button.setText("✓")
        QTimer.singleShot(1500, lambda: self.copy_button.setText(original_text))


def parse_text_for_code_blocks(text):
    if not text:
        return "", []

    # Improved regex pattern to better handle code blocks with language specifiers
    # This pattern handles both cases: with or without newline after language specifier
    pattern = r'```([\w+-]*)?(?:\s*\n)?([\s\S]*?)```'

    try:
        matches = re.findall(pattern, text)

        # Replace each code block with a placeholder
        result = text
        placeholders = []

        for i, match in enumerate(matches):
            language, code = match
            placeholder = f"__CODE_BLOCK_{i}__"
            placeholders.append((placeholder, language.strip(), code.strip()))

            # Replace the code block with the placeholder
            # Use a more precise replacement to avoid partial matches
            # Reconstruct the original code block format for accurate replacement
            original_block = text[text.find(f"```{language}"):text.find("```", text.find(f"```{language}")) + 3]
            result = result.replace(original_block, placeholder, 1)

        return result, placeholders
    except Exception as e:
        print(f"Error in parse_text_for_code_blocks: {e}")
        return text, []


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nexlify Settings")
        self.setFixedSize(380, 210)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.main_frame = QFrame(self)
        self.main_frame.setObjectName("SettingsFrame")
        self.main_frame.setStyleSheet(f"""
            QFrame#SettingsFrame {{
                background-color: {BG_COLOR};
                border-radius: 10px;
                border: 1px solid {BORDER_COLOR};
            }}
        """)

        # Create main layout for the dialog
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.main_frame)

        # Create layout for the main frame
        layout = QVBoxLayout(self.main_frame)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

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

        form_layout = QFormLayout()
        form_layout.setSpacing(8)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form_layout.setLabelAlignment(Qt.AlignRight)

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

        layout.addStretch()

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

        self.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_COLOR_SECONDARY};
                font-size: 12px;
            }}
        """)

        self.setGraphicsEffect(self.create_shadow_effect())

    def create_shadow_effect(self):
        shadow = QGraphicsOpacityEffect()
        shadow.setOpacity(0.99)
        return shadow

    def save_settings(self):
        env_path = find_dotenv()
        if not env_path:
            env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
            open(env_path, 'a').close()

        global GOOGLE_API_KEY, GROQ_API_KEY, OPENROUTER_API_KEY
        GOOGLE_API_KEY = self.google_api_key.text()
        GROQ_API_KEY = self.groq_api_key.text()
        OPENROUTER_API_KEY = self.openrouter_api_key.text()

        try:
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

class ChatBubble(QFrame):
    def __init__(self, text, role="user", parent=None):
        super().__init__(parent)
        self.text = text
        self.role = role
        self.parts = []

        try:
            # Process the text to identify code blocks
            processed_text, placeholders = parse_text_for_code_blocks(text)

            # Initialize parts list before trying to iterate through it
            if placeholders:  # If we found code blocks
                current_text = processed_text

                # Replace placeholders with None to split the text
                for placeholder, language, code in placeholders:
                    parts = current_text.split(placeholder, 1)

                    if parts[0]:  # Add text before placeholder
                        self.parts.append((False, parts[0], None))

                    # Add the code block
                    self.parts.append((True, code, language))

                    # Update current_text for next iteration
                    current_text = parts[1] if len(parts) > 1 else ""

                # Add any remaining text
                if current_text:
                    self.parts.append((False, current_text, None))
            else:
                # If no code blocks were found, just add the entire text
                self.parts.append((False, text, None))
        except Exception as e:
            print(f"Error processing text in ChatBubble: {e}")
            # Fallback: just add the entire text
            self.parts = [(False, text, None)]

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        for is_code, text, language in self.parts:
            if is_code:
                code_widget = CodeBlockWidget(text, language)
                layout.addWidget(code_widget)
            else:
                label = QLabel(text)
                label.setWordWrap(True)
                label.setStyleSheet(f"color: {TEXT_COLOR_PRIMARY}; font-size: 14px;")
                layout.addWidget(label)

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {BUBBLE_USER_COLOR if self.role == "user" else BUBBLE_AI_COLOR};
                border-radius: 10px;
                padding: 10px;
            }}
        """)

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

class CodeBlockWidget(QFrame):
    def __init__(self, code_text, language="", parent=None):
        super().__init__(parent)
        self.code_text = code_text
        self.language = language
        self.setup_ui()

    def setup_ui(self):
        # Create a more visually appealing code block with better styling
        self.setObjectName("codeBlock")
        self.setStyleSheet("""
            #codeBlock {
                background-color: #1e1e1e;
                border-radius: 4px;
                border: 0.5px solid #3e3e3e;
                margin: 5px 0;
            }
            QLabel#languageLabel {
                color: #9cdcfe;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                padding: 2px 8px;
                background-color: #252526;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                border-bottom: 0.5px solid #3e3e3e;
            }
            QTextEdit#codeTextEdit {
                background-color: transparent;
                color: #d4d4d4;
                border: none;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 13px;
                selection-background-color: #264f78;
            }
            QPushButton#copyButton {
                background-color: #252526;
                color: #9cdcfe;
                border: none;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 12px;
            }
            QPushButton#copyButton:hover {
                background-color: #2d2d2d;
            }
            QPushButton#copyButton:pressed {
                background-color: #3e3e3e;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header with language label and copy button
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 5, 0)

        self.language_label = QLabel(self.language if self.language else "Code")
        self.language_label.setObjectName("languageLabel")
        header_layout.addWidget(self.language_label)

        header_layout.addStretch()

        self.copy_button = QPushButton("Copy")
        self.copy_button.setObjectName("copyButton")
        self.copy_button.setCursor(Qt.PointingHandCursor)
        self.copy_button.clicked.connect(self.copy_code_to_clipboard)
        header_layout.addWidget(self.copy_button)

        header_widget = QWidget()
        header_widget.setLayout(header_layout)
        layout.addWidget(header_widget)

        # Code text area
        self.code_text_edit = QTextEdit()
        self.code_text_edit.setObjectName("codeTextEdit")
        self.code_text_edit.setReadOnly(True)
        self.code_text_edit.setPlainText(self.code_text)
        self.code_text_edit.setLineWrapMode(QTextEdit.NoWrap)

        # Set a reasonable minimum and maximum height based on content
        doc_height = self.code_text_edit.document().size().height()
        min_height = min(doc_height + 20, 400)  # Cap at 400px
        self.code_text_edit.setMinimumHeight(min_height)
        self.code_text_edit.setMaximumHeight(min_height)

        layout.addWidget(self.code_text_edit)

        # Apply syntax highlighting if language is specified
        if self.language:
            self.apply_syntax_highlighting(self.language)

    def apply_syntax_highlighting(self, language):
        # Basic syntax highlighting for common languages
        # This is a simplified version - you could expand this with more comprehensive highlighting
        if language.lower() in ["python", "py"]:
            # Python keywords
            keywords = ["def", "class", "import", "from", "if", "elif", "else", "for", "while",
                       "return", "try", "except", "finally", "with", "as", "and", "or", "not", "in", "is", "None", "True", "False"]
            self.highlight_keywords(keywords, QColor("#569cd6"))  # Blue for keywords

            # Decorators
            self.highlight_pattern(r"@\w+", QColor("#dcdcaa"))  # Yellow for decorators

            # Function calls
            self.highlight_pattern(r"\b\w+(?=\()", QColor("#dcdcaa"))  # Yellow for function calls

            # Class names
            self.highlight_pattern(r"(?<=class\s)\w+", QColor("#4ec9b0"))  # Teal for class names

            # Self parameter
            self.highlight_pattern(r"\bself\b", QColor("#569cd6"))  # Blue for self

            # Strings
            self.highlight_pattern(r'"[^"\\]*(\\.[^"\\]*)*"', QColor("#ce9178"))  # Orange for strings
            self.highlight_pattern(r"'[^'\\]*(\\.[^'\\]*)*'", QColor("#ce9178"))

            # Comments
            self.highlight_pattern(r"#.*$", QColor("#6a9955"), multiline=False)  # Green for comments

            # Numbers
            self.highlight_pattern(r"\b\d+\b", QColor("#b5cea8"))  # Light green for numbers

        elif language.lower() in ["javascript", "js", "typescript", "ts"]:
            keywords = ["function", "const", "let", "var", "if", "else", "for", "while",
                       "return", "try", "catch", "finally", "class", "import", "export", "from"]
            self.highlight_keywords(keywords, QColor("#569cd6"))

            # Highlight strings
            self.highlight_pattern(r'"[^"\\]*(\\.[^"\\]*)*"', QColor("#ce9178"))
            self.highlight_pattern(r"'[^'\\]*(\\.[^'\\]*)*'", QColor("#ce9178"))
            self.highlight_pattern(r"`[^`\\]*(\\.[^`\\]*)*`", QColor("#ce9178"))

            # Highlight comments
            self.highlight_pattern(r"//.*$", QColor("#6a9955"), multiline=False)

        elif language.lower() in ["jsx", "react"]:
            # JSX/React syntax highlighting
            # Keywords
            keywords = ["function", "const", "let", "var", "if", "else", "for", "while",
                       "return", "try", "catch", "finally", "class", "import", "export", "from",
                       "extends", "default", "async", "await", "static", "get", "set"]
            self.highlight_keywords(keywords, QColor("#569cd6"))  # Blue for keywords

            # React specific
            react_keywords = ["useState", "useEffect", "useContext", "useReducer", "useCallback",
                             "useMemo", "useRef", "useImperativeHandle", "useLayoutEffect",
                             "useDebugValue", "Fragment", "Suspense", "lazy", "memo", "forwardRef"]
            self.highlight_keywords(react_keywords, QColor("#c586c0"))  # Purple for React hooks

            # JSX tags and attributes
            self.highlight_pattern(r"</?[a-zA-Z][a-zA-Z0-9]*", QColor("#4ec9b0"))  # Teal for JSX tags
            self.highlight_pattern(r"<[a-zA-Z][a-zA-Z0-9]*\s+[a-zA-Z][a-zA-Z0-9]*=", QColor("#9cdcfe"))  # Light blue for attributes

            # JSX brackets
            self.highlight_pattern(r"[{}]", QColor("#d7ba7d"))  # Gold for curly braces
            self.highlight_pattern(r"[<>]", QColor("#808080"))  # Gray for angle brackets

            # Strings
            self.highlight_pattern(r'"[^"\\]*(\\.[^"\\]*)*"', QColor("#ce9178"))  # Orange for strings
            self.highlight_pattern(r"'[^'\\]*(\\.[^'\\]*)*'", QColor("#ce9178"))
            self.highlight_pattern(r"`[^`\\]*(\\.[^`\\]*)*`", QColor("#ce9178"))

            # Comments
            self.highlight_pattern(r"//.*$", QColor("#6a9955"), multiline=False)  # Green for comments

            # Function calls
            self.highlight_pattern(r"\b[a-zA-Z_][a-zA-Z0-9_]*(?=\()", QColor("#dcdcaa"))  # Yellow for function calls

            # Props in JSX
            self.highlight_pattern(r"(?<==\{)[^{}]+(?=\})", QColor("#9cdcfe"))  # Light blue for props

            # Numbers
            self.highlight_pattern(r"\b\d+\b", QColor("#b5cea8"))  # Light green for numbers

        elif language in ["html", "xml"]:
            # HTML/XML syntax highlighting
            # Highlight tags
            self.highlight_pattern(r"</?[a-zA-Z0-9]+", QColor("#569cd6"))
            self.highlight_pattern(r">", QColor("#569cd6"))

            # Highlight attributes
            self.highlight_pattern(r'\s([a-zA-Z-]+)="', QColor("#9cdcfe"))

            # Highlight strings
            self.highlight_pattern(r'"[^"]*"', QColor("#ce9178"))

        elif language in ["css", "scss"]:
            # CSS syntax highlighting
            # Highlight selectors
            self.highlight_pattern(r"[.#]?[a-zA-Z0-9_-]+\s*{", QColor("#d7ba7d"))

            # Highlight properties
            self.highlight_pattern(r"[a-zA-Z-]+:", QColor("#9cdcfe"))

            # Highlight values
            self.highlight_pattern(r":\s*[^;]+;", QColor("#ce9178"))

            # Highlight numbers
            self.highlight_pattern(r"\b\d+[a-zA-Z%]*\b", QColor("#b5cea8"))

        elif language in ["latex", "tex"]:
            # LaTeX syntax highlighting
            # Highlight commands
            self.highlight_pattern(r"\\[a-zA-Z]+", QColor("#569cd6"))  # Blue for commands

            # Highlight environments
            self.highlight_pattern(r"\\begin{[^}]+}", QColor("#4ec9b0"))  # Teal for begin
            self.highlight_pattern(r"\\end{[^}]+}", QColor("#4ec9b0"))  # Teal for end

            # Highlight math delimiters
            self.highlight_pattern(r"\$[^$]+\$", QColor("#dcdcaa"))  # Yellow for inline math
            self.highlight_pattern(r"\\\[[^\]]+\]", QColor("#dcdcaa"))  # Yellow for display math
            self.highlight_pattern(r"\\\([^)]+\)", QColor("#dcdcaa"))  # Yellow for inline math

            # Highlight comments
            self.highlight_pattern(r"%.*$", QColor("#6a9955"), multiline=False)  # Green for comments

            # Highlight special characters
            self.highlight_pattern(r"[{}]", QColor("#ce9178"))  # Orange for braces

    def highlight_keywords(self, keywords, color):
        for keyword in keywords:
            pattern = r'\b' + keyword + r'\b'
            self.highlight_pattern(pattern, color)

    def highlight_pattern(self, pattern, color, multiline=True):
        cursor = self.code_text_edit.textCursor()
        format = QTextCharFormat()
        format.setForeground(color)

        text = self.code_text_edit.toPlainText()
        for match in re.finditer(pattern, text, re.MULTILINE if multiline else 0):
            start, end = match.span()
            cursor.setPosition(start)
            # Fix: Use QTextCursor.KeepAnchor instead of Qt.KeepAnchor
            from PySide6.QtGui import QTextCursor
            cursor.setPosition(end, QTextCursor.KeepAnchor)
            cursor.setCharFormat(format)
            cursor.clearSelection()

    def copy_code_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.code_text_edit.toPlainText())

        # Show a temporary "Copied!" message
        original_text = self.copy_button.text()
        self.copy_button.setText("✓")
        QTimer.singleShot(1500, lambda: self.copy_button.setText(original_text))


def parse_text_for_code_blocks(text):
    if not text:
        return "", []

    # Improved regex pattern to better handle code blocks with language specifiers
    # This pattern handles both cases: with or without newline after language specifier
    pattern = r'```([\w+-]*)?(?:\s*\n)?([\s\S]*?)```'

    try:
        matches = re.findall(pattern, text)

        # Replace each code block with a placeholder
        result = text
        placeholders = []

        for i, match in enumerate(matches):
            language, code = match
            placeholder = f"__CODE_BLOCK_{i}__"
            placeholders.append((placeholder, language.strip(), code.strip()))

            # Replace the code block with the placeholder
            # Use a more precise replacement to avoid partial matches
            # Reconstruct the original code block format for accurate replacement
            original_block = text[text.find(f"```{language}"):text.find("```", text.find(f"```{language}")) + 3]
            result = result.replace(original_block, placeholder, 1)

        return result, placeholders
    except Exception as e:
        print(f"Error in parse_text_for_code_blocks: {e}")
        return text, []


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nexlify Settings")
        self.setFixedSize(380, 210)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.main_frame = QFrame(self)
        self.main_frame.setObjectName("SettingsFrame")
        self.main_frame.setStyleSheet(f"""
            QFrame#SettingsFrame {{
                background-color: {BG_COLOR};
                border-radius: 10px;
                border: 1px solid {BORDER_COLOR};
            }}
        """)

        # Create main layout for the dialog
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.main_frame)

        # Create layout for the main frame
        layout = QVBoxLayout(self.main_frame)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

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

        form_layout = QFormLayout()
        form_layout.setSpacing(8)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form_layout.setLabelAlignment(Qt.AlignRight)

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

        layout.addStretch()

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

        self.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_COLOR_SECONDARY};
                font-size: 12px;
            }}
        """)

        self.setGraphicsEffect(self.create_shadow_effect())

    def create_shadow_effect(self):
        shadow = QGraphicsOpacityEffect()
        shadow.setOpacity(0.99)
        return shadow

    def save_settings(self):
        env_path = find_dotenv()
        if not env_path:
            env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
            open(env_path, 'a').close()

        global GOOGLE_API_KEY, GROQ_API_KEY, OPENROUTER_API_KEY
        GOOGLE_API_KEY = self.google_api_key.text()
        GROQ_API_KEY = self.groq_api_key.text()
        OPENROUTER_API_KEY = self.openrouter_api_key.text()

        try:
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

class ChatBubble(QFrame):
    def __init__(self, text, role="user", parent=None):
        super().__init__(parent)
        self.text = text
        self.role = role
        self.parts = []

        try:
            # Process the text to identify code blocks
            processed_text, placeholders = parse_text_for_code_blocks(text)

            # Initialize parts list before trying to iterate through it
            if placeholders:  # If we found code blocks
                current_text = processed_text

                # Replace placeholders with None to split the text
                for placeholder, language, code in placeholders:
                    parts = current_text.split(placeholder, 1)

                    if parts[0]:  # Add text before placeholder
                        self.parts.append((False, parts[0], None))

                    # Add the code block
                    self.parts.append((True, code, language))

                    # Update current_text for next iteration
                    current_text = parts[1] if len(parts) > 1 else ""

                # Add any remaining text
                if current_text:
                    self.parts.append((False, current_text, None))
            else:
                # If no code blocks were found, just add the entire text
                self.parts.append((False, text, None))
        except Exception as e:
            print(f"Error processing text in ChatBubble: {e}")
            # Fallback: just add the entire text
            self.parts = [(False, text, None)]

        self.setup_ui()

    def setup_ui(self):
        # Create a more visually appealing code block with better styling
        self.setObjectName("ChatBubble")
        self.setStyleSheet(f"""
            QFrame#ChatBubble {{
                background-color: {BUBBLE_AI_COLOR if self.role == "assistant" else BUBBLE_USER_COLOR};
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

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        for is_code, content, language in self.parts:
            if is_code:
                code_block = CodeBlockWidget(content, language, self)
                layout.addWidget(code_block)
            else:
                html_content = markdown.markdown(content)
                text_label = QLabel(self)
                text_label.setText(html_content)
                text_label.setWordWrap(True)
                text_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
                text_label.setTextFormat(Qt.RichText)
                text_label.setOpenExternalLinks(True)
                layout.addWidget(text_label)

class LoadingBubble(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("LoadingBubble")
        self.setMinimumWidth(36)
        self.setStyleSheet(f"""
            QFrame#LoadingBubble {{
                background-color: {BUBBLE_AI_COLOR};
                border-radius: 8px;
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
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(15, 15, 15, 15)

    def add_message(self, text, role="user", engine=None):
        bubble = ChatBubble(text, role=role, parent=self)
        available_width = (self.width() - 120) if self.width() > 120 else 380
        bubble.setMaximumWidth(available_width)

        bubble.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        bubble.adjustSize()

        extra_padding = 0
        bubble.setMinimumHeight(bubble.sizeHint().height() + extra_padding)
        bubble.updateGeometry()

        if role == "assistant":
            header_text = engine if engine else "Nexlify"
            header_alignment = Qt.AlignLeft
        else:
            header_text = "You"
            header_alignment = Qt.AlignRight

        header_label = QLabel(header_text)
        header_label.setStyleSheet(f"color: {TEXT_COLOR_SECONDARY}; font-size: 11px;")
        header_label.setAlignment(header_alignment)

        hbox = QHBoxLayout()
        if role == "assistant":
            hbox.setContentsMargins(0, 0, 80, 0)
            hbox.setAlignment(Qt.AlignLeft)
        else:
            hbox.setContentsMargins(80, 0, 0, 0)
            hbox.setAlignment(Qt.AlignRight)
        hbox.addWidget(bubble)

        bubble_container = QWidget()
        bubble_container.setLayout(hbox)

        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(2)
        vbox.addWidget(header_label)
        vbox.addWidget(bubble_container)

        index = self.layout.count()
        self.layout.insertWidget(index, container)

    def add_loading_bubble(self):
        lb = LoadingBubble(parent=self)
        available_width = (self.width() - 120) if self.width() > 120 else 380
        lb.setMaximumWidth(available_width)
        header_label = QLabel(CURRENT_MODEL)
        header_label.setStyleSheet(f"color: {TEXT_COLOR_SECONDARY}; font-size: 11px;")
        header_label.setAlignment(Qt.AlignLeft)
        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 80, 0)
        hbox.setAlignment(Qt.AlignLeft)
        hbox.addWidget(lb)
        bubble_container = QWidget()
        bubble_container.setLayout(hbox)
        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(2)
        vbox.addWidget(header_label)
        vbox.addWidget(bubble_container)
        index = self.layout.count()
        self.layout.insertWidget(index, container)
        return container, lb

    def resizeEvent(self, event):
        super().resizeEvent(event)
        new_max = (self.width() - 120) if self.width() > 120 else 380
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

        # Store conversation messages for saving history
        self.conversation_messages = []

        # Track current conversation's saved file
        self.current_history_file = None
        self.conversation_modified = False

        self.main_frame = QFrame()
        self.main_frame.setObjectName("ChatDialogFrame")
        self.main_frame.setStyleSheet(f"""
            QFrame#ChatDialogFrame {{
                background-color: {FRAME_BG_COLOR};
                border-radius: 12px;
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
                width: 6px;
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
                padding: 10px 15px;
            }}
            QLineEdit {{
                background-color: {INPUT_BG_COLOR};
                color: {INPUT_TEXT_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
            }}
            QToolButton {{
                background-color: transparent;
                border: none;
                color: {TEXT_COLOR_PRIMARY};
                padding: 6px 10px;
                border-radius: 6px;
                font-size: 16px;
            }}
            QToolButton:hover {{ background-color: {BUTTON_HOVER_COLOR}; border-radius: 6px; }}
        """)
        reply_layout = QHBoxLayout(self.reply_frame)
        reply_layout.setContentsMargins(0, 0, 0, 0)
        reply_layout.setSpacing(10)
        self.reply_line = QLineEdit()
        self.reply_line.setPlaceholderText("Type your message...")
        reply_layout.addWidget(self.reply_line, stretch=1)
        self.reply_send_button = QToolButton()
        self.reply_send_button.setText("↑")
        self.reply_send_button.setToolTip("Send Message")
        reply_layout.addWidget(self.reply_send_button)

        # Add padding spacer to prevent overlap with size grip
        self.corner_spacer = QSpacerItem(15, 15, QSizePolicy.Fixed, QSizePolicy.Fixed)
        reply_layout.addItem(self.corner_spacer)

        self.reply_send_button.clicked.connect(self.handle_reply_send)
        self.reply_line.returnPressed.connect(self.handle_reply_send)

        main_layout.addWidget(self.scroll)
        main_layout.addWidget(self.reply_frame)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(self.main_frame)

        self.setMinimumHeight(300)
        self.setMinimumWidth(350)
        self.resize(450, 350)
        self.size_grip = QSizeGrip(self)

        app_font = QFont("Roboto", 10)
        app_font.setWeight(QFont.Weight.Light)
        self.setFont(app_font)
        self.chat_area.setFont(app_font)
        self.reply_line.setFont(app_font)
        self.reply_send_button.setFont(app_font)

        conversation_messages = [{"role": "system", "content": "You are a helpful assistant."}]

        # Create slash command popup
        self.slash_popup = SlashCommandPopup(self)
        self.slash_popup.set_commands(SLASH_COMMANDS)
        self.slash_popup.hide()

        # Connect to the text changed signal
        self.reply_line.textChanged.connect(self.check_for_slash)

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
        # Position the size grip in the bottom right corner
        self.size_grip.move(self.width() - self.size_grip.width(),
                            self.height() - self.size_grip.height())
        # Make the size grip more visible with custom styling
        self.size_grip.setStyleSheet("""
            QSizeGrip {
                background-color: transparent;
                width: 16px;
                height: 16px;
            }
        """)
        last_chat_geometry = self.geometry()

    def scroll_to_bottom(self):
        QTimer.singleShot(50, lambda: self.scroll.verticalScrollBar().setValue(
            self.scroll.verticalScrollBar().maximum() + 50
        ))

    def add_message(self, text, role="user", engine=None):
        self.chat_area.add_message(text, role=role, engine=engine)
        self.scroll_to_bottom()

        # Add message to conversation history
        self.conversation_messages.append({
            "role": role,
            "content": text
        })

        # Mark conversation as modified
        self.conversation_modified = True

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
        target_y = host_geom.y() + host_geom.height() + 5

        animation = QPropertyAnimation(self, b"pos")
        animation.setDuration(250)
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

        # Reset conversation tracking
        self.conversation_messages = []
        self.current_history_file = None
        self.conversation_modified = False

    def handle_reply_send(self):
        # Close popup if it's open
        if self.slash_popup.isVisible():
            self.slash_popup.hide()

        text = self.reply_line.text().strip()
        if text:
            # Check for special commands
            if text.startswith('/'):
                self.process_command(text)
                self.reply_line.clear()
                # Reset the slash popup to show all commands for next time
                self.slash_popup.reset_to_commands()
            else:
                # Regular message processing
                global CURRENT_MODEL
                self.add_message(text, role="user")
                self.reply_line.clear()
                container, lb = self.add_loading_bubble()
                def do_ai_work():
                    try:
                        ai_reply = self.get_ai_response(text)
                        self.host_window.response_ready.emit(ai_reply, container, lb)
                    except Exception as e:
                        error_msg = f"Error: {str(e)}"
                        self.host_window.response_ready.emit(error_msg, container, lb)

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
        elif selected_model == "QwQ":
            return self.get_qwq_response(prompt)
        else:
            return "Invalid model selected."

    def get_gemini_response(self, prompt):
        global GOOGLE_API_KEY
        genai.configure(api_key=GOOGLE_API_KEY)
        gemini_model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')
        try:
            # Create chat history
            chat = gemini_model.start_chat(history=[])
            for msg in self.conversation_messages:
                if msg["role"] == "user":
                    chat.send_message(msg["content"])
                elif msg["role"] == "assistant":
                    chat.history.append({"role": "model", "parts": [msg["content"]]})
            response = chat.send_message(prompt)
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
            # Create chat history
            chat = gemini_lite_model.start_chat(history=[])
            for msg in self.conversation_messages:
                if msg["role"] == "user":
                    chat.send_message(msg["content"])
                elif msg["role"] == "assistant":
                    chat.history.append({"role": "model", "parts": [msg["content"]]})
            response = chat.send_message(prompt)
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
            # Include conversation history
            messages = []
            for msg in self.conversation_messages:
                messages.append({"role": msg["role"], "content": msg["content"]})
            messages.append({"role": "user", "content": prompt})

            data = {
                "model": "Deepseek-R1-Distill-Qwen-32b",
                "messages": messages
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
        global OPENROUTER_API_KEY, ENABLE_SEARCH, ENABLE_UPTIME_OPTIMIZER
        if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your-api-key-here":
            error_message = "Please set a valid OPENROUTER_API_KEY in your environment variables or settings."
            print(f"{RED}{error_message}{RESET}")
            return error_message
        try:
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/ken",  # Required by OpenRouter
                "X-Title": "Nexlify Chat"  # Required by OpenRouter
            }
            # Include conversation history
            messages = []
            for msg in self.conversation_messages:
                messages.append({"role": msg["role"], "content": msg["content"]})
            messages.append({"role": "user", "content": prompt})

            # Append :online to model name if ENABLE_SEARCH is True
            model_name = "cognitivecomputations/dolphin3.0-r1-mistral-24b:free"
            if ENABLE_SEARCH:
                model_name += ":online"

            data = {
                "model": model_name,
                "messages": messages
            }

            # Add route parameter for uptime optimization if enabled
            if ENABLE_UPTIME_OPTIMIZER:
                data["route"] = "fallback"

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
        global OPENROUTER_API_KEY, ENABLE_SEARCH, ENABLE_UPTIME_OPTIMIZER
        if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your-api-key-here":
            error_message = "Please set a valid OPENROUTER_API_KEY in your environment variables or settings."
            print(f"{RED}{error_message}{RESET}")
            return error_message
        try:
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/ken",  # Required by OpenRouter
                "X-Title": "Nexlify Chat"  # Required by OpenRouter
            }
            # Include conversation history
            messages = []
            for msg in self.conversation_messages:
                messages.append({"role": msg["role"], "content": msg["content"]})
            messages.append({"role": "user", "content": prompt})

            # Append :online to model name if ENABLE_SEARCH is True
            model_name = "meta-llama/llama-3.3-70b-instruct:free"
            if ENABLE_SEARCH:
                model_name += ":online"

            data = {
                "model": model_name,
                "messages": messages
            }

            # Add route parameter for uptime optimization if enabled
            if ENABLE_UPTIME_OPTIMIZER:
                data["route"] = "fallback"

            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
            response.raise_for_status()
            ai_response_data = response.json()
            ai_response = response.json()['choices'][0]['message']['content']
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
        global OPENROUTER_API_KEY, ENABLE_SEARCH, ENABLE_UPTIME_OPTIMIZER
        if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your-api-key-here":
            error_message = "Please set a valid OPENROUTER_API_KEY in your environment variables or settings."
            print(f"{RED}{error_message}{RESET}")
            return error_message
        try:
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/ken",  # Required by OpenRouter
                "X-Title": "Nexlify Chat"  # Required by OpenRouter
            }
            # Include conversation history
            messages = []
            for msg in self.conversation_messages:
                messages.append({"role": msg["role"], "content": msg["content"]})
            messages.append({"role": "user", "content": prompt})

            # Append :online to model name if ENABLE_SEARCH is True
            model_name = "deepseek/deepseek-r1:free"
            if ENABLE_SEARCH:
                model_name += ":online"

            data = {
                "model": model_name,
                "messages": messages
            }

            # Add route parameter for uptime optimization if enabled
            if ENABLE_UPTIME_OPTIMIZER:
                data["route"] = "fallback"

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
        global OPENROUTER_API_KEY, ENABLE_SEARCH, ENABLE_UPTIME_OPTIMIZER
        if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your-api-key-here":
            error_message = "Please set a valid OPENROUTER_API_KEY in your environment variables or settings."
            print(f"{RED}{error_message}{RESET}")
            return error_message
        try:
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/ken",  # Required by OpenRouter
                "X-Title": "Nexlify Chat"  # Required by OpenRouter
            }
            # Include conversation history
            messages = []
            for msg in self.conversation_messages:
                messages.append({"role": msg["role"], "content": msg["content"]})
            messages.append({"role": "user", "content": prompt})

            # Append :online to model name if ENABLE_SEARCH is True
            model_name = "deepseek/deepseek-chat:free"
            if ENABLE_SEARCH:
                model_name += ":online"

            data = {
                "model": model_name,
                "messages": messages
            }

            # Add route parameter for uptime optimization if enabled
            if ENABLE_UPTIME_OPTIMIZER:
                data["route"] = "fallback"

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

    def get_qwq_response(self, prompt):
        global OPENROUTER_API_KEY, ENABLE_SEARCH, ENABLE_UPTIME_OPTIMIZER
        if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your-api-key-here":
            error_message = "Please set a valid OPENROUTER_API_KEY in your environment variables or settings."
            print(f"{RED}{error_message}{RESET}")
            return error_message
        try:
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/ken",  # Required by OpenRouter
                "X-Title": "Nexlify Chat"  # Required by OpenRouter
            }
            # Include conversation history
            messages = []
            for msg in self.conversation_messages:
                messages.append({"role": msg["role"], "content": msg["content"]})
            messages.append({"role": "user", "content": prompt})

            # Append :online to model name if ENABLE_SEARCH is True
            model_name = "qwen/qwq-32b:free"
            if ENABLE_SEARCH:
                model_name += ":online"

            data = {
                "model": model_name,
                "messages": messages
            }

            # Add route parameter for uptime optimization if enabled
            if ENABLE_UPTIME_OPTIMIZER:
                data["route"] = "fallback"

            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
            response.raise_for_status()
            ai_response_data = response.json()
            ai_response = ai_response_data['choices'][0]['message']['content']
            return ai_response
        except requests.exceptions.RequestException as e:
            error_message = f"Error from OpenRouter API (QwQ): {e}"
            print(f"{RED}{error_message}{RESET}")
            return error_message
        except KeyError as e:
            error_message = f"Error parsing OpenRouter response (QwQ - KeyError): {e}"
            print(f"{RED}{error_message}{RESET}")
            return error_message
        except Exception as e:
            error_message = f"Unexpected error with OpenRouter API (QwQ): {e}"
            print(f"{RED}{error_message}{RESET}")
            return error_message

    def update_existing_history(self):
        """Update the existing history file with the current conversation."""
        if not self.current_history_file:
            return

        file_path = os.path.join(HISTORY_FOLDER, self.current_history_file)

        # Check if file still exists
        if not os.path.exists(file_path):
            self.current_history_file = None
            # Create new history file
            self.current_history_file = save_new_chat_history(
                self.conversation_messages,
                CURRENT_MODEL
            )
            return

        try:
            # Load existing data
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Update data with current conversation
            message_count = sum(1 for msg in self.conversation_messages if msg.get("role") == "user")
            data["message_count"] = message_count
            data["messages"] = self.conversation_messages
            data["timestamp"] = datetime.now().strftime("%Y%m%d_%H%M%S")
            data["date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Save back to the same file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            self.conversation_modified = False
            print(f"{GREEN}Updated chat history in {file_path}{RESET}")
        except Exception as e:
            print(f"{RED}Error updating chat history: {str(e)}{RESET}")
            # If update fails, try creating a new file
            self.current_history_file = save_new_chat_history(
                self.conversation_messages,
                CURRENT_MODEL
            )

    def process_command(self, command):
        """Process special commands starting with /"""
        parts = command.split(' ', 1)
        cmd = parts[0].lower()

        if cmd == '/help':
            help_text = (
                "**Nexlify Commands:**\n\n"
                "- **/prompts** - List or use saved prompt templates\n"
                "- **/save [name]** - Save current prompt as template\n"
                "- **/bookmark** - View saved bookmarks\n"
                "- **/mark** - Bookmark last AI response\n"
                "- **/online** - Toggle online search capability\n"
                "- **/uptime** - Toggle uptime optimization\n"
                "- **/help** - Show this help message"
            )
            self.show_system_message(help_text)

        elif cmd == '/prompts':
            self.show_prompts_dialog()

        elif cmd == '/save' and len(parts) > 1:
            self.save_current_prompt(parts[1])

        elif cmd == '/bookmark':
            self.show_bookmarks_dialog()

        elif cmd == '/mark':
            self.bookmark_last_response()

        elif cmd == '/online':
            global ENABLE_SEARCH
            ENABLE_SEARCH = not ENABLE_SEARCH
            status = "enabled" if ENABLE_SEARCH else "disabled"
            self.show_system_message(f"Online search is now **{status}**")
            save_config()

        elif cmd == '/uptime':
            global ENABLE_UPTIME_OPTIMIZER
            ENABLE_UPTIME_OPTIMIZER = not ENABLE_UPTIME_OPTIMIZER
            status = "enabled" if ENABLE_UPTIME_OPTIMIZER else "disabled"
            self.show_system_message(f"Uptime optimization is now **{status}**")
            save_config()

        else:
            self.show_system_message(f"Unknown command: {cmd}. Type /help for available commands.")

    def show_system_message(self, text):
        """Show a system message in the chat area without adding to history"""
        self.chat_area.add_message(text, role="system", engine="Nexlify")
        self.scroll_to_bottom()

    def save_current_prompt(self, name):
        """Save the current input as a prompt template"""
        global SAVED_PROMPTS

        # Get the last user message
        last_user_msg = None
        for msg in reversed(self.conversation_messages):
            if msg.get('role') == 'user':
                last_user_msg = msg.get('content')
                break

        if not last_user_msg:
            self.show_system_message("No user message to save as template.")
            return

        SAVED_PROMPTS[name] = last_user_msg
        save_prompts()
        self.show_system_message(f"Saved prompt template: **{name}**")

    def show_prompts_dialog(self):
        """Show dialog to pick from saved prompts"""
        global SAVED_PROMPTS

        if not SAVED_PROMPTS:
            self.show_system_message("No saved prompts. Use /save [name] to save a prompt.")
            return

        dialog = TemplatePickerDialog("Saved Prompts", SAVED_PROMPTS, self)
        dialog_pos = self.host_window.mapToGlobal(QPoint(
            (self.host_window.width() - dialog.width()) // 2,
            (self.host_window.height() - dialog.height()) // 2 - 100
        ))
        dialog.move(dialog_pos)

        if dialog.exec() == QDialog.Accepted:
            if dialog.delete_mode:
                # Delete the prompt
                if dialog.selected_item in SAVED_PROMPTS:
                    del SAVED_PROMPTS[dialog.selected_item]
                    save_prompts()
                    self.show_system_message(f"Deleted prompt: **{dialog.selected_item}**")
            elif dialog.selected_text:
                # Use the prompt - actually set it in the input field
                self.reply_line.setText(dialog.selected_text)
                self.reply_line.setFocus()
                # Position cursor at end of text
                self.reply_line.setCursorPosition(len(dialog.selected_text))

    def bookmark_last_response(self):
        """Bookmark the last AI response"""
        global BOOKMARKS, CURRENT_MODEL

        # Find the last AI response
        last_ai_msg = None
        for msg in reversed(self.conversation_messages):
            if msg.get('role') == 'assistant':
                last_ai_msg = msg.get('content')
                break

        if not last_ai_msg:
            self.show_system_message("No AI response to bookmark.")
            return

        # Create a bookmark
        bookmark = {
            'id': str(uuid.uuid4()),
            'role': 'assistant',
            'content': last_ai_msg,
            'model': CURRENT_MODEL,
            'timestamp': datetime.now().timestamp()
        }

        BOOKMARKS.append(bookmark)
        save_bookmarks()
        self.show_system_message("Bookmarked last AI response.")

    def show_bookmarks_dialog(self):
        """Show dialog to pick from saved bookmarks"""
        global BOOKMARKS

        if not BOOKMARKS:
            self.show_system_message("No bookmarks. Use /mark to bookmark an AI response.")
            return

        dialog = TemplatePickerDialog("Bookmarks", BOOKMARKS, self)
        dialog_pos = self.host_window.mapToGlobal(QPoint(
            (self.host_window.width() - dialog.width()) // 2,
            (self.host_window.height() - dialog.height()) // 2 - 100
        ))
        dialog.move(dialog_pos)

        if dialog.exec() == QDialog.Accepted:
            if dialog.delete_mode:
                # Delete the bookmark
                idx = dialog.selected_item
                if 0 <= idx < len(BOOKMARKS):
                    del BOOKMARKS[idx]
                    save_bookmarks()
                    self.show_system_message("Deleted bookmark.")
            elif dialog.selected_text:
                # Show the bookmark content
                self.add_message(dialog.selected_text, role="assistant", engine="Bookmark")
                self.scroll_to_bottom()

    def show_libraries_dialog(self):
        """Show dialog to pick from prompt libraries"""
        global PROMPT_LIBRARIES

        if not PROMPT_LIBRARIES:
            self.show_system_message("No prompt libraries. Use /newlib [name] to create one.")
            return

        dialog = TemplatePickerDialog("Prompt Libraries", PROMPT_LIBRARIES, self)
        dialog_pos = self.host_window.mapToGlobal(QPoint(
            (self.host_window.width() - dialog.width()) // 2,
            (self.host_window.height() - dialog.height()) // 2 - 100
        ))
        dialog.move(dialog_pos)

        if dialog.exec() == QDialog.Accepted:
            if dialog.delete_mode:
                # Delete the library
                if dialog.selected_item in PROMPT_LIBRARIES:
                    del PROMPT_LIBRARIES[dialog.selected_item]
                    save_libraries()
                    self.show_system_message(f"Deleted library: **{dialog.selected_item}**")
            elif dialog.selected_item:
                # Show prompts in this library
                lib_name = dialog.selected_item
                self.show_library_prompts(lib_name)

    def show_library_prompts(self, lib_name):
        """Show prompts in a specific library"""
        global PROMPT_LIBRARIES

        if lib_name not in PROMPT_LIBRARIES:
            self.show_system_message(f"Library not found: {lib_name}")
            return

        library = PROMPT_LIBRARIES[lib_name]
        if not library:
            self.show_system_message(f"Library '{lib_name}' is empty. Add prompts with /addto {lib_name} [name]")
            return

        dialog = TemplatePickerDialog(f"Prompts in {lib_name}", library, self)
        dialog_pos = self.host_window.mapToGlobal(QPoint(
            (self.host_window.width() - dialog.width()) // 2,
            (self.host_window.height() - dialog.height()) // 2 - 100
        ))
        dialog.move(dialog_pos)

        if dialog.exec() == QDialog.Accepted:
            if dialog.delete_mode:
                # Delete the prompt from library
                if dialog.selected_item in library:
                    del library[dialog.selected_item]
                    save_libraries()
                    self.show_system_message(f"Deleted prompt '{dialog.selected_item}' from library '{lib_name}'")
            elif dialog.selected_text:
                # Use the prompt - actually put it in the input field
                self.reply_line.setText(dialog.selected_text)
                self.reply_line.setFocus()
                # Position cursor at end of text
                self.reply_line.setCursorPosition(len(dialog.selected_text))

    def create_prompt_library(self, lib_name):
        """Create a new prompt library"""
        global PROMPT_LIBRARIES

        if lib_name in PROMPT_LIBRARIES:
            self.show_system_message(f"Library '{lib_name}' already exists.")
            return

        PROMPT_LIBRARIES[lib_name] = {}
        save_libraries()
        self.show_system_message(f"Created new prompt library: **{lib_name}**")

    def add_to_library(self, lib_name, prompt_name):
        """Add current prompt to a library"""
        global PROMPT_LIBRARIES

        if lib_name not in PROMPT_LIBRARIES:
            self.show_system_message(f"Library '{lib_name}' not found. Create it with /newlib {lib_name}")
            return

        # Get the last user message
        last_user_msg = None
        for msg in reversed(self.conversation_messages):
            if msg.get('role') == 'user':
                last_user_msg = msg.get('content')
                break

        if not last_user_msg:
            self.show_system_message("No user message to add to library.")
            return

        PROMPT_LIBRARIES[lib_name][prompt_name] = last_user_msg
        save_libraries()
        self.show_system_message(f"Added prompt '{prompt_name}' to library '{lib_name}'")

    def check_for_slash(self, text):
        """Show command suggestions when user types /"""
        if text == '/':
            # Reset to show all commands if the user types / again
            self.slash_popup.reset_to_commands()

            # Position the popup below the input line
            pos = self.reply_line.mapToGlobal(QPoint(0, self.reply_line.height()))
            popup_width = min(400, self.width() - 40)
            self.slash_popup.setFixedWidth(popup_width)
            self.slash_popup.move(pos)
            self.slash_popup.show()

        elif text.startswith('/'):
            # Filter commands that match what's being typed
            filtered_commands = [cmd for cmd in SLASH_COMMANDS if cmd.startswith(text)]
            if filtered_commands:
                # Include the clear option with filtered commands
                filtered_with_clear = ["❌ Clear Command"] + filtered_commands
                self.slash_popup.model.setStringList(filtered_with_clear)
                if not self.slash_popup.isVisible():
                    pos = self.reply_line.mapToGlobal(QPoint(0, self.reply_line.height()))
                    self.slash_popup.move(pos)
                    self.slash_popup.show()
            else:
                self.slash_popup.hide()
        else:
            # Hide the popup if not using slash commands
            self.slash_popup.hide()

class BottomBubble(QFrame):
    send_message = Signal(str)
    open_settings = Signal()
    open_history = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("BottomBubble")
        self.setFixedHeight(50)

        self.setStyleSheet(f"""
            QFrame#BottomBubble {{
                background-color: {BG_COLOR};
                border-radius: 10px;
                padding: 5px;
            }}
            QLineEdit {{
                background-color: {INPUT_BG_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 5px;
                color: {INPUT_TEXT_COLOR};
                padding: 6px 8px;
                font-size: 14px;
            }}
            QLineEdit:focus {{ border: 1px solid {TEXT_COLOR_SECONDARY}; }}
            QToolButton#ModelButton {{
                background-color: transparent;
                border: none;
                color: {TEXT_COLOR_SECONDARY};
                font-size: 13px;
                padding: 2px 6px;
                border-radius: 5px;
            }}
            QToolButton#ModelButton:hover {{
                background-color: {MODEL_BUTTON_HOVER};
                border-radius: 5px;
            }}
            QToolButton#SendButton, QToolButton#SettingsButton, QToolButton#HistoryButton {{
                background-color: transparent;
                border: none;
                color: {TEXT_COLOR_PRIMARY};
                font-size: 16px;
                padding: 2px 6px;
                border-radius: 5px;
            }}
            QToolButton#SendButton:hover, QToolButton#SettingsButton:hover, QToolButton#HistoryButton:hover {{
                background-color: {BUTTON_HOVER_COLOR};
                border-radius: 5px;
            }}
            QLabel#LogoLabel {{
                padding: 2px;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(8)

        # New history button
        self.history_button = QToolButton()
        self.history_button.setObjectName("HistoryButton")
        self.history_button.setText("🕒")
        self.history_button.setToolTip("Chat History")
        self.history_button.clicked.connect(self.on_history_clicked)
        layout.addWidget(self.history_button)

        self.logo_label = QLabel()
        self.logo_label.setObjectName("LogoLabel")
        icon = self.load_app_logo()
        if (icon):
            pixmap = icon.pixmap(24, 24)
            self.logo_label.setPixmap(pixmap)
        else:
            self.logo_label.setText("Nexlify")
            self.logo_label.setStyleSheet(f"color: {TEXT_COLOR_PRIMARY}; font-weight: bold;")

        self.logo_label.setToolTip("Nexlify by sufyxxn")
        layout.addWidget(self.logo_label)

        self.settings_button = QToolButton()
        self.settings_button.setObjectName("SettingsButton")
        self.settings_button.setText("⚙")
        self.settings_button.setToolTip("Settings")
        self.settings_button.clicked.connect(self.on_settings_clicked)
        layout.addWidget(self.settings_button)

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
        self.send_button.setText("↑")
        self.send_button.setToolTip("Send")
        self.send_button.clicked.connect(self.handle_send)
        layout.addWidget(self.send_button)

        self.input_line.returnPressed.connect(self.handle_send)

    def on_history_clicked(self):
        self.open_history.emit()

    def load_app_logo(self):
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            logo_path = os.path.join(script_dir, "logo.png")
            if os.path.exists(logo_path):
                return QIcon(logo_path)
        except Exception as e:
            print(f"{YELLOW}Could not load logo from file: {e}{RESET}")

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
        self.resize(450, 80)
        self._dragPos = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addStretch()

        self.bottom_bubble = BottomBubble(self)
        layout.addWidget(self.bottom_bubble)
        self.bottom_bubble.update_model_display()

        self.bottom_bubble.open_settings.connect(self.show_settings_dialog)
        self.bottom_bubble.open_history.connect(self.show_history_dialog)

        self.close_button = QPushButton("✕", self)
        self.close_button.setToolTip("Close")
        self.close_button.setFixedSize(20, 20)
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

    def show_history_dialog(self):
        dialog = HistoryDialog(self)
        dialog_pos = self.mapToGlobal(QPoint(
            (self.width() - dialog.width()) // 2,
            (self.height() - dialog.height()) // 2 - 100
        ))
        dialog.move(dialog_pos)

        if dialog.exec() == QDialog.Accepted:
            if dialog.selected_history_file:
                self.load_conversation_history(dialog.selected_history_file)

    def load_conversation_history(self, file_name):
        messages, model = load_chat_history(file_name)
        if not messages:
            return

        # Clear existing conversation
        self.chat_dialog.clear_chat()
        self.chat_dialog.conversation_messages = []

        # Set the current history file
        self.chat_dialog.current_history_file = file_name
        self.chat_dialog.conversation_modified = False

        # Show chat dialog if not already visible
        if not self.chat_dialog.isVisible():
            self.chat_dialog.show()
            self.chat_dialog.reposition()

        # Add messages to chat
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")

            if content:
                self.chat_dialog.add_message(content, role=role, engine=model if role == "assistant" else None)

        # Reset the modified flag since we just loaded the conversation
        self.chat_dialog.conversation_modified = False

    def show_settings_dialog(self):
        dialog = SettingsDialog(self)
        dialog_pos = self.mapToGlobal(QPoint(
            (self.width() - dialog.width()) // 2,
            (self.height() - dialog.height()) // 2 - 50
        ))
        dialog.move(dialog_pos)
        dialog.exec()
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
        self.close_button.move(self.width() - self.close_button.width() - 3, 3)
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
        self.chat_dialog.conversation_messages = []
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

        self.chat_dialog.add_message(ai_reply, role="assistant", engine=CURRENT_MODEL)

        # Save chat history after AI response
        if len(self.chat_dialog.conversation_messages) >= 2:  # At least one user message and one AI response
            if self.chat_dialog.current_history_file:
                # Update existing history file
                self.chat_dialog.update_existing_history()
            else:
                # Create new history file and save its name
                self.chat_dialog.current_history_file = save_new_chat_history(
                    self.chat_dialog.conversation_messages,
                    CURRENT_MODEL
                )

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
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            toggle_window()

class HistoryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Chat History")
        self.setFixedSize(450, 350)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.selected_history_file = None

        self.main_frame = QFrame(self)
        self.main_frame.setObjectName("HistoryFrame")
        self.main_frame.setStyleSheet(f"""
            QFrame#HistoryFrame {{
                background-color: {BG_COLOR};
                border-radius: 10px;
                border: 1px solid {BORDER_COLOR};
            }}
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.main_frame)

        layout = QVBoxLayout(self.main_frame)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Title and Close button
        title_layout = QHBoxLayout()
        title_label = QLabel("Chat History")
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

        # History list
        self.history_list = QListWidget()
        self.history_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {INPUT_BG_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 5px;
                color: {TEXT_COLOR_PRIMARY};
                padding: 5px;
            }}
            QListWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {BORDER_COLOR};
            }}
            QListWidget::item:selected {{
                background-color: {BUBBLE_USER_COLOR};
                color: {TEXT_COLOR_PRIMARY};
            }}
            QListWidget::item:hover {{
                background-color: {BUTTON_HOVER_COLOR};
            }}
        """)
        self.history_list.itemDoubleClicked.connect(self.accept)
        layout.addWidget(self.history_list)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)

        self.open_button = QPushButton("Open")
        self.open_button.setFixedSize(80, 28)
        self.open_button.setStyleSheet(f"""
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
        self.open_button.clicked.connect(self.accept)

        self.delete_button = QPushButton("Delete")
        self.delete_button.setFixedSize(80, 28)
        self.delete_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {CLOSE_BUTTON_BG};
                color: {TEXT_COLOR_PRIMARY};
                border: none;
                border-radius: 5px;
                padding: 5px;
                font-size: 12px;
            }}
            QPushButton:hover {{ background-color: {CLOSE_BUTTON_HOVER}; }}
        """)
        self.delete_button.clicked.connect(self.delete_history)

        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()
        button_layout.addWidget(self.open_button)
        layout.addLayout(button_layout)

        self.load_history_files()
        self.setGraphicsEffect(self.create_shadow_effect())

    def create_shadow_effect(self):
        shadow = QGraphicsOpacityEffect()
        shadow.setOpacity(0.99)
        return shadow

    def load_history_files(self):
        self.history_list.clear()
        if not os.path.exists(HISTORY_FOLDER):
            return

        history_files = [f for f in os.listdir(HISTORY_FOLDER) if f.endswith('.json')]
        history_files.sort(key=lambda x: os.path.getmtime(os.path.join(HISTORY_FOLDER, x)), reverse=True)

        for file in history_files:
            try:
                with open(os.path.join(HISTORY_FOLDER, file), 'r', encoding='utf-8') as f:
                    data = json.load(f)

                timestamp = datetime.fromtimestamp(os.path.getmtime(os.path.join(HISTORY_FOLDER, file)))
                date_str = timestamp.strftime("%Y-%m-%d %H:%M")

                model = data.get("model", "Unknown")
                messages = data.get("messages", [])
                preview = ""

                for msg in messages:
                    if msg.get("role") == "user":
                        preview = msg.get("content", "")[:50]
                        break

                display_text = f"{date_str} | {model}\n{preview}..."
                item = QListWidgetItem(display_text)
                item.setData(Qt.UserRole, file)
                self.history_list.addItem(item)
            except Exception as e:
                print(f"{RED}Error loading history file {file}: {e}{RESET}")

    def delete_history(self):
        current_item = self.history_list.currentItem()
        if current_item:
            file_name = current_item.data(Qt.UserRole)
            file_path = os.path.join(HISTORY_FOLDER, file_name)

            try:
                os.remove(file_path)
                self.history_list.takeItem(self.history_list.row(current_item))
                print(f"{GREEN}Deleted history file: {file_name}{RESET}")
            except Exception as e:
                print(f"{RED}Error deleting history file: {e}{RESET}")

    def accept(self):
        current_item = self.history_list.currentItem()
        if current_item:
            self.selected_history_file = current_item.data(Qt.UserRole)
            super().accept()
        else:
            print(f"{YELLOW}No history selected{RESET}")

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

def save_chat_history(messages, model):
    if not messages:
        return

    if not os.path.exists(HISTORY_FOLDER):
        os.makedirs(HISTORY_FOLDER)

    # Create a more structured filename with model, count and date
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Count user messages to add to filename
    message_count = sum(1 for msg in messages if msg.get("role") == "user")

    # Generate a unique conversation ID based on first user message
    first_user_message = ""
    for msg in messages:
        if msg.get("role") == "user":
            first_user_message = msg.get("content", "")[:20].strip()
            break

    # Format: ModelName-MessageCount-FirstMessage-Date.json
    safe_message = re.sub(r'[^\w]', '', first_user_message).lower()
    filename = f"{model}-{message_count}msgs-{safe_message}-{timestamp}.json"
    file_path = os.path.join(HISTORY_FOLDER, filename)

    # Create structured data object
    data = {
        "model": model,
        "message_count": message_count,
        "timestamp": timestamp,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "messages": messages
    }

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"{GREEN}Chat history saved to {file_path}{RESET}")
    except Exception as e:
        print(f"{RED}Error saving chat history: {str(e)}{RESET}")
        try:
            # Try an alternative approach if the first one fails
            with open(file_path, 'w', encoding='utf-8') as f:
                # Use a simpler structure if the full one fails
                simple_data = {
                    "model": model,
                    "messages": messages
                }
                json.dump(simple_data, f, ensure_ascii=False)
            print(f"{YELLOW}Chat history saved with simplified format{RESET}")
        except Exception as e2:
            print(f"{RED}All attempts to save history failed: {str(e2)}{RESET}")

def save_new_chat_history(messages, model):
    """Save a new chat history file and return the filename."""
    if not messages:
        return None

    if not os.path.exists(HISTORY_FOLDER):
        os.makedirs(HISTORY_FOLDER)

    # Create a more structured filename with model, count and date
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Count user messages to add to filename
    message_count = sum(1 for msg in messages if msg.get("role") == "user")

    # Generate a unique conversation ID based on first user message
    first_user_message = ""
    for msg in messages:
        if msg.get("role") == "user":
            first_user_message = msg.get("content", "")[:20].strip()
            break

    # Format: ModelName-MessageCount-FirstMessage-Date.json
    safe_message = re.sub(r'[^\w]', '', first_user_message).lower()
    filename = f"{model}-{message_count}msgs-{safe_message}-{timestamp}.json"
    file_path = os.path.join(HISTORY_FOLDER, filename)

    # Create structured data object
    data = {
        "model": model,
        "message_count": message_count,
        "timestamp": timestamp,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "messages": messages
    }

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"{GREEN}New chat history saved to {file_path}{RESET}")
        return filename
    except Exception as e:
        print(f"{RED}Error saving chat history: {str(e)}{RESET}")
        return None

def load_chat_history(file_name):
    file_path = os.path.join(HISTORY_FOLDER, file_name)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get("messages", []), data.get("model", "Unknown")
    except Exception as e:
        print(f"{RED}Error loading chat history: {e}{RESET}")
        return [], "Unknown"

current_window = None
def toggle_window():
    global current_window, last_main_geometry, last_chat_geometry
    try:
        if (current_window is None) or (not current_window):
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

# Add these global variables with the other globals
PROMPTS_FILE = "prompts.pkl"
BOOKMARKS_FILE = "bookmarks.pkl"
PROMPT_LIBRARIES_FILE = "libraries.pkl"

# Add data structures to store our features
SAVED_PROMPTS = {}  # {name: text}
BOOKMARKS = []  # [{id, role, content, model, timestamp}]
PROMPT_LIBRARIES = {}  # {library_name: {prompt_name: prompt_text}}

# After the other load functions, add this function to load the template data
def load_templates_data():
    global SAVED_PROMPTS, BOOKMARKS, PROMPT_LIBRARIES

    try:
        if os.path.exists(PROMPTS_FILE):
            with open(PROMPTS_FILE, 'rb') as f:
                SAVED_PROMPTS = pickle.load(f)
            print(f"{GREEN}Loaded {len(SAVED_PROMPTS)} saved prompts{RESET}")
    except Exception as e:
        print(f"{RED}Error loading saved prompts: {e}{RESET}")
        SAVED_PROMPTS = {}

    try:
        if os.path.exists(BOOKMARKS_FILE):
            with open(BOOKMARKS_FILE, 'rb') as f:
                BOOKMARKS = pickle.load(f)
            print(f"{GREEN}Loaded {len(BOOKMARKS)} bookmarks{RESET}")
    except Exception as e:
        print(f"{RED}Error loading bookmarks: {e}{RESET}")
        BOOKMARKS = []

    try:
        if os.path.exists(PROMPT_LIBRARIES_FILE):
            with open(PROMPT_LIBRARIES_FILE, 'rb') as f:
                PROMPT_LIBRARIES = pickle.load(f)
            print(f"{GREEN}Loaded {len(PROMPT_LIBRARIES)} prompt libraries{RESET}")
    except Exception as e:
        print(f"{RED}Error loading prompt libraries: {e}{RESET}")
        PROMPT_LIBRARIES = {}

# Save functions for each feature
def save_prompts():
    try:
        with open(PROMPTS_FILE, 'wb') as f:
            pickle.dump(SAVED_PROMPTS, f)
        print(f"{GREEN}Saved {len(SAVED_PROMPTS)} prompts{RESET}")
    except Exception as e:
        print(f"{RED}Error saving prompts: {e}{RESET}")

def save_bookmarks():
    try:
        with open(BOOKMARKS_FILE, 'wb') as f:
            pickle.dump(BOOKMARKS, f)
        print(f"{GREEN}Saved {len(BOOKMARKS)} bookmarks{RESET}")
    except Exception as e:
        print(f"{RED}Error saving bookmarks: {e}{RESET}")

def save_libraries():
    try:
        with open(PROMPT_LIBRARIES_FILE, 'wb') as f:
            pickle.dump(PROMPT_LIBRARIES, f)
        print(f"{GREEN}Saved {len(PROMPT_LIBRARIES)} prompt libraries{RESET}")
    except Exception as e:
        print(f"{RED}Error saving prompt libraries: {e}{RESET}")

# Create the template dialog class
class TemplatePickerDialog(QDialog):
    def __init__(self, title, items, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(450, 350)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.selected_item = None
        self.selected_text = None
        self.delete_mode = False

        self.main_frame = QFrame(self)
        self.main_frame.setObjectName("TemplateFrame")
        self.main_frame.setStyleSheet(f"""
            QFrame#TemplateFrame {{
                background-color: {BG_COLOR};
                border-radius: 10px;
                border: 1px solid {BORDER_COLOR};
            }}
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.main_frame)

        layout = QVBoxLayout(self.main_frame)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Title and Close button
        title_layout = QHBoxLayout()
        title_label = QLabel(title)
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

        # Items list
        self.item_list = QListWidget()
        self.item_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {INPUT_BG_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 5px;
                color: {TEXT_COLOR_PRIMARY};
                padding: 5px;
            }}
            QListWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {BORDER_COLOR};
            }}
            QListWidget::item:selected {{
                background-color: {BUBBLE_USER_COLOR};
                color: {TEXT_COLOR_PRIMARY};
            }}
            QListWidget::item:hover {{
                background-color: {BUTTON_HOVER_COLOR};
            }}
        """)
        self.item_list.itemDoubleClicked.connect(self.accept)
        layout.addWidget(self.item_list)

        # Fill the list
        self.items = items
        self.fill_list()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)

        self.use_button = QPushButton("Use")
        self.use_button.setFixedSize(80, 28)
        self.use_button.setStyleSheet(f"""
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
        self.use_button.clicked.connect(self.accept)

        self.delete_button = QPushButton("Delete")
        self.delete_button.setFixedSize(80, 28)
        self.delete_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {CLOSE_BUTTON_BG};
                color: {TEXT_COLOR_PRIMARY};
                border: none;
                border-radius: 5px;
                padding: 5px;
                font-size: 12px;
            }}
            QPushButton:hover {{ background-color: {CLOSE_BUTTON_HOVER}; }}
        """)
        self.delete_button.clicked.connect(self.delete_item)

        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()
        button_layout.addWidget(self.use_button)
        layout.addLayout(button_layout)

        self.setGraphicsEffect(self.create_shadow_effect())

    def create_shadow_effect(self):
        shadow = QGraphicsOpacityEffect()
        shadow.setOpacity(0.99)
        return shadow

    def fill_list(self):
        self.item_list.clear()

        if isinstance(self.items, dict):
            # For dictionaries (prompts, libraries)
            for name, content in self.items.items():
                if isinstance(content, dict):
                    # For libraries that contain multiple prompts
                    item_text = f"{name} ({len(content)} prompts)"
                else:
                    # Normal prompt with preview
                    preview = content[:50] + "..." if len(content) > 50 else content
                    item_text = f"{name}\n{preview}"

                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, name)
                self.item_list.addItem(item)

            # Select the first item by default for better UX
            if self.item_list.count() > 0:
                self.item_list.setCurrentRow(0)

        elif isinstance(self.items, list):
            # For bookmarks
            for idx, bookmark in enumerate(self.items):
                preview = bookmark['content'][:50] + "..." if len(bookmark['content']) > 50 else bookmark['content']
                timestamp = datetime.fromtimestamp(bookmark.get('timestamp', 0))
                date_str = timestamp.strftime("%Y-%m-%d %H:%M")

                role_icon = "🤖" if bookmark['role'] == "assistant" else "👤"
                item_text = f"{role_icon} {date_str} | {bookmark['model']}\n{preview}"

                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, idx)  # Store index for bookmarks
                self.item_list.addItem(item)

            # Select the first item by default
            if self.item_list.count() > 0:
                self.item_list.setCurrentRow(0)

    def delete_item(self):
        self.delete_mode = True
        current_item = self.item_list.currentItem()
        if current_item:
            self.selected_item = current_item.data(Qt.UserRole)
            self.accept()

    def accept(self):
        current_item = self.item_list.currentItem()
        if current_item:
            self.selected_item = current_item.data(Qt.UserRole)
            # For bookmarks, we need to get the actual content
            if isinstance(self.items, list) and not self.delete_mode:
                idx = self.selected_item
                if 0 <= idx < len(self.items):
                    self.selected_text = self.items[idx]['content']
            # For prompts and libraries, get the text
            elif isinstance(self.items, dict) and not self.delete_mode:
                key = self.selected_item
                if key in self.items:
                    if isinstance(self.items[key], dict):
                        # This is a library, so we don't want text yet
                        self.selected_text = None
                    else:
                        self.selected_text = self.items[key]
            super().accept()
        else:
            print(f"{YELLOW}No item selected{RESET}")

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

class SlashCommandPopup(QListView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setEditTriggers(QListView.NoEditTriggers)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet(f"""
            QListView {{
                background-color: {INPUT_BG_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 5px;
                color: {TEXT_COLOR_PRIMARY};
                padding: 5px;
                selection-background-color: {BUBBLE_USER_COLOR};
                selection-color: {TEXT_COLOR_PRIMARY};
            }}
            QListView::item {{
                padding: 5px;
            }}
            QListView::item:hover {{
                background-color: {BUTTON_HOVER_COLOR};
            }}
        """)

        self.model = QStringListModel()
        self.setModel(self.model)
        self.activated.connect(self.item_activated)

        # Track current view state
        self.current_view = "commands"  # Can be "commands", "prompts", "bookmarks", "libraries"
        self.current_library = None

        # Store commands for returning to main menu
        self.commands = []

    def set_commands(self, commands):
        self.commands = commands
        # Add Clear option at the top of the command list
        commands_with_clear = ["❌ Clear Command"] + commands
        self.model.setStringList(commands_with_clear)
        self.current_view = "commands"

    def reset_to_commands(self):
        """Reset to main commands view when user types / again"""
        commands_with_clear = ["❌ Clear Command"] + self.commands
        self.model.setStringList(commands_with_clear)
        self.current_view = "commands"
        self.current_library = None

    def show_prompts(self):
        """Show saved prompts in the popup."""
        global SAVED_PROMPTS
        if not SAVED_PROMPTS:
            self.parent().reply_line.setText("/save ")
            self.parent().reply_line.setFocus()
            self.hide()
            return

        # Create list items from prompts with preview
        items = [f"{name} - {text[:30]}..." if len(text) > 30 else f"{name} - {text}"
                for name, text in SAVED_PROMPTS.items()]
        self.model.setStringList(["❌ Clear Command", "↩️ Back to Commands"] + items)
        self.current_view = "prompts"

    def show_bookmarks(self):
        """Show bookmarks in the popup."""
        global BOOKMARKS
        if not BOOKMARKS:
            self.parent().reply_line.setText("/mark")
            self.parent().reply_line.setFocus()
            self.hide()
            return

        # Create list items from bookmarks with model and preview
        items = []
        for idx, bookmark in enumerate(BOOKMARKS):
            preview = bookmark['content'][:30] + "..." if len(bookmark['content']) > 30 else bookmark['content']
            date_str = datetime.fromtimestamp(bookmark.get('timestamp', 0)).strftime("%m/%d")
            items.append(f"[{date_str}] {bookmark['model']} - {preview}")

        self.model.setStringList(["❌ Clear Command", "↩️ Back to Commands"] + items)
        self.current_view = "bookmarks"

    def show_libraries(self):
        """Show prompt libraries in the popup."""
        global PROMPT_LIBRARIES
        if not PROMPT_LIBRARIES:
            self.parent().reply_line.setText("/newlib ")
            self.parent().reply_line.setFocus()
            self.hide()
            return

        # Create list items from libraries
        items = [f"{name} ({len(library)} prompts)" for name, library in PROMPT_LIBRARIES.items()]
        self.model.setStringList(["❌ Clear Command", "↩️ Back to Commands"] + items)
        self.current_view = "libraries"

    def show_library_prompts(self, lib_name):
        """Show prompts in a specific library."""
        global PROMPT_LIBRARIES
        if lib_name not in PROMPT_LIBRARIES or not PROMPT_LIBRARIES[lib_name]:
            self.parent().reply_line.setText(f"/addto {lib_name} ")
            self.parent().reply_line.setFocus()
            self.hide()
            return

        # Create list items from library prompts
        library = PROMPT_LIBRARIES[lib_name]
        items = [f"{name} - {text[:30]}..." if len(text) > 30 else f"{name} - {text}"
                for name, text in library.items()]

        self.model.setStringList(["❌ Clear Command", "↩️ Back to Libraries"] + items)
        self.current_view = "library_prompts"
        self.current_library = lib_name

    def back_to_commands(self):
        """Return to main commands view."""
        commands_with_clear = ["❌ Clear Command"] + self.commands
        self.model.setStringList(commands_with_clear)
        self.current_view = "commands"
        self.current_library = None

    def item_activated(self, index):
        text = self.model.data(index, Qt.DisplayRole)

        # Handle clear command - hide popup and clear the text input
        if text.startswith("❌ Clear"):
            self.parent().reply_line.clear()
            self.hide()
            return

        # Handle back button
        if text.startswith("↩️ Back"):
            if self.current_view == "prompts" or self.current_view == "bookmarks" or self.current_view == "libraries":
                self.back_to_commands()
            elif self.current_view == "library_prompts":
                self.show_libraries()
            return

        # Handle different views
        if self.current_view == "commands":
            if "prompts" in text.lower():
                self.show_prompts()
            elif "bookmark" in text.lower() and "mark" not in text.lower():
                self.show_bookmarks()
            elif "lib" in text.lower() and "newlib" not in text.lower() and "addto" not in text.lower():
                self.show_libraries()
            else:
                # Extract just the command part before space or dash
                parts = text.split(' ', 1)
                cmd = parts[0]
                self.parent().reply_line.setText(cmd + " ")
                self.parent().reply_line.setFocus()
                self.hide()

        # Handle prompt selection
        elif self.current_view == "prompts":
            try:
                name = text.split(" - ")[0]
                if name in SAVED_PROMPTS:
                    self.parent().reply_line.setText(SAVED_PROMPTS[name])
                    self.parent().reply_line.setFocus()
                    # Position cursor at end of text
                    self.parent().reply_line.setCursorPosition(len(SAVED_PROMPTS[name]))
                    self.hide()
            except Exception as e:
                print(f"{RED}Error selecting prompt: {e}{RESET}")

        # Handle bookmark selection
        elif self.current_view == "bookmarks":
            try:
                # Adjust index for Clear and Back buttons
                idx = self.currentIndex().row() - 2  # Subtract 2 for "Clear" and "Back" buttons
                if 0 <= idx < len(BOOKMARKS):
                    content = BOOKMARKS[idx]['content']
                    # For bookmarks, emit signal to add message directly
                    self.parent().add_message(content, role="assistant", engine=f"Bookmark ({BOOKMARKS[idx]['model']})")
                    self.hide()
            except Exception as e:
                print(f"{RED}Error selecting bookmark: {e}{RESET}")

        # Handle library selection
        elif self.current_view == "libraries":
            try:
                name = text.split(" (")[0]
                if name in PROMPT_LIBRARIES:
                    self.show_library_prompts(name)
            except Exception as e:
                print(f"{RED}Error selecting library: {e}{RESET}")

        # Handle library prompt selection
        elif self.current_view == "library_prompts" and self.current_library:
            try:
                name = text.split(" - ")[0]
                library = PROMPT_LIBRARIES[self.current_library]
                if name in library:
                    self.parent().reply_line.setText(library[name])
                    self.parent().reply_line.setFocus()
                    # Position cursor at end of text
                    self.parent().reply_line.setCursorPosition(len(library[name]))
                    self.hide()
            except Exception as e:
                print(f"{RED}Error selecting library prompt: {e}{RESET}")

# Command definitions
SLASH_COMMANDS = [
    "/help - Show available commands",
    "/prompts - List or use saved prompt templates",
    "/save [name] - Save current prompt as template",
    "/bookmark - View saved bookmarks",
    "/mark - Bookmark last AI response",
    "/online - Toggle online search capability",
    "/uptime - Toggle uptime optimization"
]

def main():
    load_config()
    load_templates_data()  # Load saved prompts, bookmarks, and libraries
    app = QApplication(sys.argv)

    app.setApplicationName("Nexlify")
    app.setApplicationDisplayName("Nexlify AI Assistant")
    app.setOrganizationName("sufyxxn")
    app.setOrganizationDomain("nexlify.ai")

    # Create history folder if it doesn't exist
    if not os.path.exists(HISTORY_FOLDER):
        os.makedirs(HISTORY_FOLDER)
        print(f"{GREEN}Created history folder: {HISTORY_FOLDER}{RESET}")

    icon = None

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

    if icon is None or icon.isNull():
        print(f"{YELLOW}Using embedded icon{RESET}")
        icon = get_embedded_icon()

    if icon is None or icon.isNull():
        print(f"{RED}Creating basic fallback icon{RESET}")
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor("#2A2A2A"))
        icon = QIcon(pixmap)

    app.setWindowIcon(icon)

    tray_icon = SystemTrayIcon(icon)

    if not tray_icon.icon().isNull():
        tray_icon.show()
    else:
        print(f"{RED}Warning: System tray icon appears to be null{RESET}")
        emergency_pixmap = QPixmap(32, 32)
        emergency_pixmap.fill(QColor("#1E1E1E"))
        tray_icon.setIcon(QIcon(emergency_pixmap))
        tray_icon.show()

    app.setQuitOnLastWindowClosed(False)
    print(f"{GREEN}Nexlify is running! Click the system tray icon to access the app.{RESET}")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()