from email.mime import application
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QClipboard
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QPlainTextEdit, QLabel, \
    QSpacerItem, QSizePolicy, QMessageBox, QScrollBar
from utils import resource_path

class QueryWindow(QWidget):
    change_pas_templ_query = "ALTER USER '<u>'@'localhost' IDENTIFIED BY '<p>'; FLUSH PRIVILEGES;"

    def __init__(self, mode, username, password, data=change_pas_templ_query):
        super().__init__()
        self.setGeometry(0, 0, 600, 350)
        self.setWindowIcon(QIcon(resource_path("images/app_icon.png")))
        self.setWindowTitle("Query")

        self.username = username
        self.password = password
        self.data = data.replace('<u>', username)

        self.change_password_mode = 'c'
        self.transfer_password_mode = 't'

        self.screen_style = ""
        self.copy_button_style = ""
        self.plain_text_edit_style = ""
        self.button_style = ""
        self.label_style = ""
        self.line_edit_style = ""
        self.scroll_style = ""

        self.get_styles()
        self.setStyleSheet(self.screen_style)

        vertical_layout = QVBoxLayout(self)

        self.password_line_edit = QLineEdit()
        self.password_line_edit.setPlaceholderText("Password")
        self.password_line_edit.setStyleSheet(self.line_edit_style)
        self.password_line_edit.textChanged.connect(self.update_query)

        horizontal_layout = QHBoxLayout()
        label = QLabel("Query")
        label.setStyleSheet(self.label_style)

        horizontal_spacer = QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)

        copy_query_button = QPushButton()
        copy_query_button.setIcon(QIcon(resource_path("images/copy_icon.png")))
        copy_query_button.setToolTip("Copy Query")
        copy_query_button.setStyleSheet(self.copy_button_style)
        copy_query_button.setCursor(Qt.PointingHandCursor)
        copy_query_button.clicked.connect(self.copy_text)

        horizontal_layout.addWidget(label)
        horizontal_layout.addItem(horizontal_spacer)
        horizontal_layout.addWidget(copy_query_button)

        self.plain_text_edit = QPlainTextEdit()
        self.plain_text_edit.setPlaceholderText("Query")
        self.plain_text_edit.setStyleSheet(self.plain_text_edit_style)
        self.plain_text_edit.setPlainText(self.data)

        scroll = QScrollBar()
        scroll.setStyleSheet(self.scroll_style)
        self.plain_text_edit.setVerticalScrollBar(scroll)

        close_window_button = QPushButton("Close")
        close_window_button.setStyleSheet(self.button_style)
        close_window_button.setCursor(Qt.PointingHandCursor)
        close_window_button.clicked.connect(self.close)

        vertical_layout.addWidget(self.password_line_edit)
        vertical_layout.addLayout(horizontal_layout)
        vertical_layout.addWidget(self.plain_text_edit)
        vertical_layout.addWidget(close_window_button)

        if mode == self.transfer_password_mode:
            self.password_line_edit.hide()

    def get_styles(self):
        try:
            with open(resource_path("css/screen_background.css"), 'r') as file:
                self.screen_style = file.read()
            with open(resource_path("css/view_password_button.css"), 'r') as file:
                self.copy_button_style = file.read()
            with open(resource_path("css/plain_text_edit.css"), 'r') as file:
                self.plain_text_edit_style = file.read()
            with open(resource_path("css/button.css"), 'r') as file:
                self.button_style = file.read()
            with open(resource_path("css/label.css"), 'r') as file:
                self.label_style = file.read()
            with open(resource_path("css/line_edit.css"), 'r') as file:
                self.line_edit_style = file.read()
            with open(resource_path("css/scrollbar.css"), 'r') as file:
                self.scroll_style = file.read()
        except FileNotFoundError:
            pass

    def update_query(self):
        text = self.password_line_edit.text()
        self.plain_text_edit.setPlainText(self.data.replace('<p>', text))

    def copy_text(self):
        text_to_copy = self.plain_text_edit.toPlainText()
        if text_to_copy:
            clipboard = application.clipboard()
            clipboard.setText(text_to_copy, mode=QClipboard.Clipboard)
