import sys
import os
import time
import queue
import json
import csv
import re
import webbrowser
import threading
import keyboard
import requests
import google.generativeai as genai
from datetime import timedelta, datetime
from PySide6.QtCore import (
    Qt, QTimer, QRect, QObject, QThread, QPropertyAnimation, QEasingCurve,
    QSequentialAnimationGroup, QParallelAnimationGroup, QSize, Signal, Slot, QMetaObject, QPoint, QEvent, QAbstractAnimation
)
from PySide6.QtGui import QAction, QFontMetrics, QPainter, QPixmap, QIcon, QFont
from PySide6.QtWidgets import (
    QApplication, QWidget, QFrame, QVBoxLayout, QHBoxLayout,
    QComboBox, QLineEdit, QToolButton, QPushButton, QScrollArea,
    QSizePolicy, QLabel, QSpacerItem, QSizeGrip, QMenu, QGroupBox,
    QFormLayout, QSpinBox, QCheckBox, QWidgetAction, QStackedWidget, QStyle, QStyledItemDelegate, QToolTip, QTextEdit, QGraphicsOpacityEffect
)
from dotenv import load_dotenv

load_dotenv()

# ==================== GLOBALS & DEFAULTS  ====================
use_conversation_history = True
days_back_to_load = 15
HOTKEY_LAUNCH = "ctrl+k"
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY") # Add OpenRouter API Key

launch_hotkey_id = None
current_conversation_id = None
current_conversation_file_path = None
conversation_messages = []
MODEL_OPTIONS = ["Gemini", "R1 Groq", "Mistral", "Llama", "R1", "DS-V3"] # Updated MODEL_OPTIONS
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


# =============== FUNCTIONALITY: CONFIG & HISTORY (Simplified) ===============

def load_config():
    """Loads basic config (history settings) from .voiceconfig."""
    config_file = ".voiceconfig"
    if not os.path.exists(config_file):
        return
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
        global use_conversation_history, days_back_to_load, HOTKEY_LAUNCH, CURRENT_MODEL_INDEX, CURRENT_MODEL
        use_conversation_history = config.get("use_conversation_history", use_conversation_history)
        days_back_to_load = config.get("days_back_to_load", days_back_to_load)
        HOTKEY_LAUNCH = config.get("HOTKEY_LAUNCH", HOTKEY_LAUNCH)
        CURRENT_MODEL_INDEX = config.get("CURRENT_MODEL_INDEX", CURRENT_MODEL_INDEX)
        CURRENT_MODEL = MODEL_OPTIONS[CURRENT_MODEL_INDEX]
    except Exception as e:
        print(f"{RED}Error loading config: {e}{RESET}")

def save_config():
    """Saves basic config (history settings) to .voiceconfig."""
    config_file = ".voiceconfig"
    try:
        config = {
            "use_conversation_history": use_conversation_history,
            "days_back_to_load": days_back_to_load,
            "HOTKEY_LAUNCH": HOTKEY_LAUNCH,
            "CURRENT_MODEL_INDEX": CURRENT_MODEL_INDEX
        }
        with open(config_file, "w", newline="", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"{RED}Error saving config: {e}{RESET}")

def append_message_to_history(role: str, content: str, model_name: str = ""):
    global current_conversation_id, current_conversation_file_path
    if not current_conversation_id or not current_conversation_file_path:
        return

    history_dir = "history"
    if not os.path.exists(history_dir):
        os.makedirs(history_dir)

    file_existed = os.path.exists(current_conversation_file_path)
    with open(current_conversation_file_path, "a", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["timestamp", "role", "content", "model"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        if not file_existed:
            writer.writeheader()

        writer.writerow({
            "timestamp": datetime.now().strftime('%Y%m%d_%H%M%S'),
            "role": role.lower(),
            "content": content.strip(),
            "model": model_name.strip() if model_name else ""
        })

def start_new_conversation():
    global current_conversation_id, current_conversation_file_path
    if current_conversation_id is None:
        timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        current_conversation_id = timestamp_str
        conversation_dir = "history"
        if not os.path.exists(conversation_dir):
            os.makedirs(conversation_dir)
        current_conversation_file_path = os.path.join(
            conversation_dir, f"conversation_{timestamp_str}.csv"
        )

def end_current_conversation():
    global current_conversation_id, current_conversation_file_path
    current_conversation_id = None
    current_conversation_file_path = None

def load_previous_history(days: int):
    history_dir = "history"
    loaded_messages = []
    allowed_roles = {"system","assistant","user","function","tool","developer"}

    if not os.path.exists(history_dir):
        return loaded_messages

    now = datetime.now()
    threshold = now - timedelta(days=days)
    session_files = []
    for fname in os.listdir(history_dir):
        if not fname.startswith("conversation_") or not fname.endswith(".csv"):
            continue
        base = fname[len("conversation_"):-4]
        try:
            file_dt = datetime.strptime(base, "%Y%m%d_%H%M%S")
            if file_dt >= threshold:
                session_files.append(os.path.join(history_dir, fname))
        except:
            continue

    session_files.sort(key=lambda path: os.path.getmtime(path))

    for path in session_files:
        try:
            with open(path, newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    role = row.get("role","").lower()
                    if role not in allowed_roles:
                        role = "user"
                    msg = {
                        "role": role,
                        "content": row.get("content","").strip(),
                        "model": row.get("model","").strip()
                    }
                    loaded_messages.append(msg)
        except Exception as e:
            print(f"{RED}Error loading {path}: {e}{RESET}")

    print(f"{GREEN}Loaded {len(loaded_messages)} messages from {days} days back{RESET}")
    return loaded_messages


# =============== UI ELEMENTS (Simplified from clickui.py) ===============

class ChatBubble(QFrame):
    def __init__(self, text, role="user", parent=None):
        super().__init__(parent)
        self.text = text
        self.role = role
        self.setObjectName("ChatBubble")
        bg_color = BUBBLE_AI_COLOR if self.role == "assistant" else BUBBLE_USER_COLOR
        self.setStyleSheet(f"""
            QFrame#ChatBubble {{
                background-color: {bg_color};
                border-radius: 8px; /* Less rounded for industrial look */
                padding: 8px 10px; /* Adjusted padding */
                border: 1px solid {BORDER_COLOR}; /* Subtle border */
            }}
            QLabel {{
                color: {TEXT_COLOR_PRIMARY};
                font-size: 14px;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.label = QLabel(text, self)
        self.label.setWordWrap(True)
        self.label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(self.label)

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

        bubble.label.setWordWrap(True)
        bubble.label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        bubble.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        bubble.adjustSize()

        extra_padding = 0
        bubble.setMinimumHeight(bubble.sizeHint().height() + extra_padding)
        bubble.updateGeometry()

        if role == "assistant":
            header_text = engine if engine else "AI" # Minimalist header
            header_alignment = Qt.AlignLeft
        else:
            header_text = "You" # Minimalist header
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


        if not conversation_messages:
            conversation_messages.append({"role": "system", "content": "You are a helpful assistant."})

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
            append_message_to_history("user", text, CURRENT_MODEL)
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
        if selected_model == "Gemini": # Renamed model to just "Gemini"
            return self.get_gemini_response(prompt)
        elif selected_model == "R1 Groq": # Renamed "Groq" to "R1 Groq"
            return self.get_groq_response(prompt)
        elif selected_model == "Mistral":
            return self.get_mistral_response(prompt)
        elif selected_model == "Llama":
            return self.get_llama_response(prompt)
        elif selected_model == "R1":
            return self.get_r1_response(prompt)
        elif selected_model == "DS-V3": # New model "DS-V3"
            return self.get_dsv3_response(prompt)
        else:
            return "Invalid model selected."

    def get_gemini_response(self, prompt):
        global GOOGLE_API_KEY
        genai.configure(api_key=GOOGLE_API_KEY)
        gemini_model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21') # Option 1 model name
        try:
            response = gemini_model.generate_content(prompt)
            ai_response = response.text
            return ai_response
        except Exception as e:
            error_message = f"Error from Gemini API: {e}"
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
                "model": "Deepseek-R1-Distill-Qwen-32b", # Updated Groq model name
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

    def get_dsv3_response(self, prompt): # New function for DS-V3 model
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
             QToolButton#SendButton {{ /* Style for the Send Button */
                background-color: transparent;
                border: none;
                color: {TEXT_COLOR_PRIMARY};
                font-size: 16px;
                padding: 2px 6px;
                border-radius: 5px;
            }}
            QToolButton#SendButton:hover {{
                background-color: {BUTTON_HOVER_COLOR};
                border-radius: 5px;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5) # Reduced margins
        layout.setSpacing(8) # Reduced spacing

        # Add Logo Label
        self.logo_label = QLabel()
        logo_pixmap = QPixmap("logo.png").scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation) # Adjust size as needed
        self.logo_label.setPixmap(logo_pixmap)
        self.logo_label.setToolTip("Made By Sufyaan")
        layout.addWidget(self.logo_label)
        # Add Spacer after logo
        layout.addItem(QSpacerItem(5, 0, QSizePolicy.Fixed, QSizePolicy.Minimum))

        self.model_button = QToolButton()
        self.model_button.setObjectName("ModelButton")
        self.model_button.setText(CURRENT_MODEL)
        self.model_button.setToolTip("Click to switch model")
        self.model_button.clicked.connect(self.cycle_model)
        layout.addWidget(self.model_button)


        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("Enter prompt...") # More concise placeholder
        layout.addWidget(self.input_line, stretch=1)

        self.send_button = QToolButton()
        self.send_button.setObjectName("SendButton")
        self.send_button.setText("↑") # Simple arrow icon
        self.send_button.setToolTip("Send")
        self.send_button.clicked.connect(self.handle_send)
        layout.addWidget(self.send_button)

        self.input_line.returnPressed.connect(self.handle_send)

    def handle_send(self):
        global conversation_messages, CURRENT_MODEL
        text = self.input_line.text().strip()
        if text:
            append_message_to_history("user", text, CURRENT_MODEL)
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
        self.setStyleSheet(f"QWidget {{ background-color: {BG_COLOR}; }}") # Overall background

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

    def close_all(self):
        end_current_conversation()
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
        fresh_mode = not use_conversation_history
        threading.Thread(
            target=self.process_ai_reply,
            args=(text, container, lb, fresh_mode),
            daemon=True
        ).start()

    def process_ai_reply(self, text, container, lb, fresh):
        try:
            ai_reply = self.chat_dialog.get_ai_response(text)
        except Exception as e:
            stop_spinner()
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


# =============== TOGGLE WINDOW / HOTKEY (Simplified) ===============

current_window = None
def toggle_window():
    global current_window, last_main_geometry, last_chat_geometry, conversation_messages
    try:
        if current_window is None:
            current_window = BottomBubbleWindow()
            if use_conversation_history:
                conversation_messages = load_previous_history(days_back_to_load)
            else:
                conversation_messages = []
            if last_main_geometry is not None:
                current_window.setGeometry(last_main_geometry)
            if last_chat_geometry is not None and current_window.chat_dialog.isVisible():
                current_window.chat_dialog.setGeometry(last_chat_geometry)
            start_new_conversation()
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
                end_current_conversation()
            else:
                if use_conversation_history:
                    conversation_messages = load_previous_history(days_back_to_load)
                else:
                    conversation_messages = []
                start_new_conversation()
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
        if use_conversation_history:
            conversation_messages = load_previous_history(days_back_to_load)
        else:
            conversation_messages = []
        start_new_conversation()
        current_window.show()
        current_window.raise_()
        current_window.activateWindow()
        current_window.bottom_bubble.input_line.setFocus()

hotkey_invoker = None
def hotkey_callback():
    QMetaObject.invokeMethod(hotkey_invoker, "toggle", Qt.QueuedConnection)

def exit_callback():
    QApplication.quit()

# =============== MAIN ENTRY POINT (Simplified) ===============

def main():
    load_config()
    app = QApplication(sys.argv)
    # --- Line to add logo ---
    app.setWindowIcon(QIcon("logo.png"))
    # --- Line to add logo ---

    # Set application-wide font to Roboto Light
    app_font = QFont("Roboto", 10)
    app_font.setWeight(QFont.Weight.Light)
    app.setFont(app_font)


    global hotkey_invoker
    hotkey_invoker = HotkeyInvoker()

    global launch_hotkey_id
    launch_hotkey_id = keyboard.add_hotkey(HOTKEY_LAUNCH, hotkey_callback, suppress=True)
    keyboard.add_hotkey("ctrl+d", exit_callback, suppress=True)
    app.setQuitOnLastWindowClosed(False)
    print(f"{GREEN}Ready!\n{YELLOW}{HOTKEY_LAUNCH.title()} to show/hide the UI\n{RED}Ctrl+D to quit{RESET}")
    sys.exit(app.exec())

class HotkeyInvoker(QObject):
    @Slot()
    def toggle(self):
        toggle_window()
if __name__ == "__main__":
    main()