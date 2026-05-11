from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget, QLineEdit, QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QLabel, QSizePolicy, QScrollArea
from PyQt6.QtGui import QIcon, QPainter, QMovie, QColor, QTextCharFormat, QFont, QPixmap, QTextBlockFormat
from PyQt6.QtCore import Qt, QSize, QTimer
from dotenv import dotenv_values
import sys
import os

env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname")
current_dir = os.getcwd()
old_chat_message = ""
TempDirPath = os.path.join(current_dir, "Frontend", "Files")
GraphicsDirPath = os.path.join(current_dir, "Frontend", "Graphics")

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

def QueryModifier(Query):

    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's", "can you"]

    if any(word + "" in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"

    else:
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."
    
    return new_query.capitalize()

def SetMicroPhoneStatus(Command):
    with open(os.path.join(TempDirPath, "Mic.data"), "w", encoding='utf-8') as file:
        file.write(Command)

def GetMicroPhoneStatus():
    with open(os.path.join(TempDirPath, "Mic.data"), "r", encoding='utf-8') as file:
        Status = file.read()
    return Status

def SetAssistantStatus(Status):
    with open(os.path.join(TempDirPath, "Status.data"), "w", encoding='utf-8') as file:
        file.write(Status)

def GetAssistantStatus():
    with open(os.path.join(TempDirPath, "Mic.data"), "r", encoding='utf-8') as file:
        Status = file.read()
    return Status

def MicButtonInitialed():
    SetMicroPhoneStatus("False")

def MicButtonClosed():
    SetMicroPhoneStatus("True")

def get_graphics_path(Filename):
    return os.path.join(GraphicsDirPath, Filename)

def get_temp_path(Filename):
    return os.path.join(TempDirPath, Filename)

def ShowTextToScreen(Text):
    with open(os.path.join(TempDirPath, "Responses.data"), "w", encoding='utf-8') as file:
        file.write(Text)

class ChatSection(QWidget):

    def __init__(self):
        super(ChatSection, self).__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 40, 40, 100)
        layout.setSpacing(0)
        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.chat_text_edit.setFrameStyle(QFrame.Shape.NoFrame)
        self.chat_text_edit.setStyleSheet("""
            QTextEdit {
                background-color: black;
                color: white;
                border: none;
                padding: 10px;
            }
        """)
        layout.addWidget(self.chat_text_edit)
        self.setStyleSheet("background-color: black;")
        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none;")
        movie = QMovie(get_graphics_path('Jarvis.gif'))
        max_gif_size_W = 480
        max_gif_size_H = 270
        movie.setScaledSize(QSize(max_gif_size_W, max_gif_size_H))
        self.gif_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        self.gif_label.setMovie(movie)
        movie.start()
        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size: 16px; margin-right: 195px; border: none; margin-top: -30px;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.gif_label)
        layout.addWidget(self.label)
        font = QFont()
        font.setPointSize(13)
        font.setFamily("Helvetica")
        self.chat_text_edit.setFont(font)
        
        # Load initial chat history
        try:
            with open(get_temp_path('Database.data'), 'r', encoding='utf-8') as file:
                initial_chat = file.read()
                if initial_chat:
                    self.addMessage(initial_chat, 'white')
        except Exception as e:
            print(f"Error loading initial chat: {e}")
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(100)
        self.chat_text_edit.viewport().installEventFilter(self)
        self.setStyleSheet("""
            QScrollBar:vertical {
                border: none;
                background: #333;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #666;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                border: none;
                background: none;
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

    def loadMessages(self):
        global old_chat_message
        try:
            with open(get_temp_path('Responses.data'), "r", encoding='utf-8') as file:
                messages = file.read()
                
                if messages and messages != old_chat_message:
                    self.addMessage(message=messages, color='white')
                    old_chat_message = messages
                    self.chat_text_edit.verticalScrollBar().setValue(
                        self.chat_text_edit.verticalScrollBar().maximum()
                    )
        except Exception as e:
            print(f"Error loading messages: {e}")

    def SpeechRecogText(self):
        try:
            with open(get_temp_path('Status.data'), "r", encoding='utf-8') as file:
                messages = file.read()
                self.label.setText(messages)
        except Exception as e:
            print(f"Error loading status: {e}")

    def load_icon(self, path, width=60, height=60):
        pixmap = QPixmap(path)
        new_pixmap = pixmap.scaled(width, height)
        self.icon_label.setPixmap(new_pixmap)

    def toggle_icon(self, event=None):

        if self.toggled:
                self.load_icon(get_graphics_path('voice.png'), 60, 60)
                MicButtonInitialed()

        else:
                self.load_icon(get_graphics_path('mic.png'), 60, 60)
                MicButtonClosed()

        self.toggled = not self.toggled

    def addMessage(self, message, color):
        cursor = self.chat_text_edit.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        
        format = QTextCharFormat()
        format.setForeground(QColor(color))
        format.setFontPointSize(13)
        
        block_format = QTextBlockFormat()
        block_format.setTopMargin(10)
        block_format.setLeftMargin(10)
        
        cursor.setCharFormat(format)
        cursor.setBlockFormat(block_format)
        cursor.insertText(message + "\n")
        self.chat_text_edit.setTextCursor(cursor)

class InitialScreen(QWidget):

    def __init__(self, parent = None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        
        # Setup layout
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Setup GIF
        gif_label = QLabel()
        movie = QMovie(get_graphics_path('Jarvis.gif'))
        gif_label.setMovie(movie)
        max_gif_size_H = int(screen_width / 16 * 9)
        movie.setScaledSize(QSize(screen_width, max_gif_size_H))
        gif_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        movie.start()
        gif_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Setup microphone icon
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(150, 150)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Initialize with mic on
        self.toggled = False  # Start with False so first toggle turns it True
        self.toggle_icon()  # This will set it to True and show Mic_on.png
        
        # Setup status label
        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size:16px; margin-bottom:0;")
        
        # Add widgets to layout
        content_layout.addWidget(gif_label, alignment=Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(self.icon_label, alignment=Qt.AlignmentFlag.AlignCenter)
        content_layout.setContentsMargins(0, 0, 0, 150)
        
        # Set layout and window properties
        self.setLayout(content_layout)
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)
        self.setStyleSheet("background-color: black;")
        
        # Setup timer for status updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(100)  # Update every 100ms instead of 5ms
        
        # Enable click handling
        self.icon_label.mousePressEvent = self.toggle_icon

    def SpeechRecogText(self):
        try:
            with open(get_temp_path('Status.data'), "r", encoding="utf-8") as file:
                messages = file.read()
                self.label.setText(messages)
        except Exception as e:
            print(f"Error updating status: {e}")

    def load_icon(self, path, width=60, height=60):
        pixmap = QPixmap(path)
        new_pixmap = pixmap.scaled(width, height)
        self.icon_label.setPixmap(new_pixmap)

    def toggle_icon(self, event=None):
        if self.toggled:
            self.load_icon(get_graphics_path('Mic_off.png'), 60, 60)
            MicButtonInitialed()
        else:
            self.load_icon(get_graphics_path('Mic_on.png'), 60, 60)
            MicButtonClosed()
        
        self.toggled = not self.toggled

class MessageScreen(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        layout = QVBoxLayout()
        label = QLabel("")
        layout.addWidget(label)
        Chat_Section = ChatSection()
        layout.addWidget(Chat_Section)
        self.setLayout(layout)
        self.setStyleSheet("background-color: black;")
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)

class CustomTopBar(QWidget):

    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.initUI()
        self.current_screen = None
        self.stacked_widget = stacked_widget

    def initUI(self):
        self.setFixedHeight(50)
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        home_button = QPushButton()
        home_icon = QIcon(get_graphics_path("Home.png"))
        home_button.setIcon(home_icon)
        home_button.setText(" Home")
        home_button.setStyleSheet("height:40px; line-height:40px ; background-color:white ; color: black")
        message_button = QPushButton()
        message_icon = QIcon(get_graphics_path("Chats.png"))
        message_button.setIcon(message_icon)
        message_button.setText(" Chat")
        message_button.setStyleSheet("height:40px; line-height:40px ; background-color:white ; color: black")
        minimize_button = QPushButton()
        minimize_icon = QIcon(get_graphics_path("Minimize2.png"))
        minimize_button.setIcon(minimize_icon)
        minimize_button.setStyleSheet("background-color:white")
        minimize_button.clicked.connect(self.minimizeWindow)
        self.maximize_button = QPushButton()
        self.maximize_icon = QIcon(get_graphics_path('Maximize.png'))
        self.restore_icon = QIcon(get_graphics_path('Maximize.png'))
        self.maximize_button.setIcon(self.maximize_icon)
        self.maximize_button.setFlat(True)
        self.maximize_button.setStyleSheet("background-color:white")
        self.maximize_button.clicked.connect(self.maximizeWindow)
        close_button = QPushButton()
        close_icon = QIcon(get_graphics_path('Close.png'))
        close_button.setIcon(close_icon)
        close_button.setStyleSheet("background-color:white")
        close_button.clicked.connect(self.closeWindow)
        line_frame = QFrame()
        line_frame.setFixedHeight(1)
        line_frame.setFrameShape(QFrame.Shape.HLine)
        line_frame.setFrameShadow(QFrame.Shadow.Sunken)
        line_frame.setStyleSheet("border-color: black;")
        title_label = QLabel(f"{str(Assistantname).capitalize()} AI      ")
        title_label.setStyleSheet("color:black; font-size: 18px;; background-color:white")
        home_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        message_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        layout.addWidget(title_label)
        layout.addStretch(1)
        layout.addWidget(home_button)
        layout.addWidget(message_button)
        layout.addStretch(1)
        layout.addWidget(minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(close_button)
        layout.addWidget(line_frame)
        self.draggable = True
        self.offset = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.GlobalColor.white)
        super().paintEvent(event)

    def minimizeWindow(self):
        self.parent().showMinimized()

    def maximizeWindow(self):
        if self.parent().showMaximized():
                self.parent().showNormal()
                self.maximize_button.setIcon(self.maximize_icon)
        else:
                self.parent().showMaximized()
                self.maximize_button.setIcon(self.restore_icon)

    def closeWindow(self):
        self.parent().close()

def mousePressEvent(self, event):
    if self.draggable:
        self.offset = event.pos()

def mouseMoveEvent(self, event):
    if self.draggable and self.offset:
        new_pos = event.globalPos() - self.offset
        self.parent().move(new_pos)

def showMessageScreen(self):
    if self.current_screen is not None:
        self.current_screen.hide()

    message_screen = MessageScreen(self)
    layout = self.parent().layout()
    if layout is not None:
        layout.addWidget(message_screen)
    self.current_screen = message_screen

def showInitialScreen(self):
    if self.current_screen is not None:
        self.current_screen.hide()
        
    initial_screen = InitialScreen(self)
    layout = self.parent().layout()
    if layout is not None:
           layout.addWidget(initial_screen)
    self.current_screen = initial_screen

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.init_ui()

    def init_ui(self):
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        
        # Create stacked widget
        stacked_widget = QStackedWidget(self)
        initial_screen = InitialScreen()
        message_screen = MessageScreen()
        stacked_widget.addWidget(initial_screen)
        stacked_widget.addWidget(message_screen)
        
        # Set window geometry and style
        self.setGeometry(0, 0, screen_width, screen_height)
        self.setStyleSheet("background-color: black;")
        
        # Create top bar
        top_bar = CustomTopBar(self, stacked_widget)
        
        self.setMenuWidget(top_bar)
        self.setCentralWidget(stacked_widget)

def GraphicalUserInterface():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    GraphicalUserInterface()