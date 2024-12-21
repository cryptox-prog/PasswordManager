import mysql.connector
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QEvent
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QSpacerItem, QSizePolicy, QMessageBox
from password_manager import PasswordManagerWindow
from utils import resource_path

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(0, 0, 500, 200)
        self.setWindowTitle("Login")
        self.setWindowIcon(QIcon(resource_path("images/app_icon.png")))

        self.host = "localhost"
        self.database = "passwordsdb"

        self.screen_style = ""
        self.button_style = ""
        self.view_password_style = ""
        self.line_edit_style = ""

        self.get_style()
        self.password_manager_window = None

        self.setStyleSheet(self.screen_style)

        layout = QVBoxLayout(self)
        spacer_top = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer_top)

        self.username_line_edit = QLineEdit(self)
        self.username_line_edit.setStyleSheet(self.line_edit_style)
        self.username_line_edit.setPlaceholderText("Username")
        layout.addWidget(self.username_line_edit)

        password_layout = QHBoxLayout()
        self.password_line_edit = QLineEdit(self)
        self.password_line_edit.setStyleSheet(self.line_edit_style)
        self.password_line_edit.setPlaceholderText("Password")
        self.password_line_edit.setEchoMode(QLineEdit.Password)

        password_layout.addWidget(self.password_line_edit)

        self.view_password_button = QPushButton(self)
        self.view_password_button.setStyleSheet(self.view_password_style)
        self.view_password_button.setIcon(QIcon(resource_path("images/eye_icon.png")))
        self.view_password_button.setCursor(Qt.PointingHandCursor)
        self.view_password_button.installEventFilter(self)
        password_layout.addWidget(self.view_password_button)
        layout.addLayout(password_layout)

        login_button = QPushButton("Login", self)
        login_button.setStyleSheet(self.button_style)
        login_button.setCursor(Qt.PointingHandCursor)
        login_button.clicked.connect(self.login)
        layout.addWidget(login_button)

        spacer_bottom = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer_bottom)

    def eventFilter(self, obj, event):
        if obj == self.view_password_button:
            if event.type() == QEvent.Enter:
                self.password_line_edit.setEchoMode(QLineEdit.Normal)
                return True
            elif event.type() == QEvent.Leave:
                self.password_line_edit.setEchoMode(QLineEdit.Password)
                return True

        return super().eventFilter(obj, event)

    def login(self):
        try:
            _username = self.username_line_edit.text()
            _password = self.password_line_edit.text()
            connection = mysql.connector.connect(
                host=self.host,
                user=_username,
                password=_password,
                database=self.database
            )
            connection.close()
            self.password_manager_window = PasswordManagerWindow(_username, _password)
            self.password_manager_window.show()
            self.close()
        except mysql.connector.Error:
            msg_box = QMessageBox()
            msg_box.setWindowIcon(QIcon(resource_path("images/app_icon.png")))
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setWindowTitle("Connection Error")
            msg_box.setText("Unable to establish a connection.")
            msg_box.setStandardButtons(QMessageBox.Retry)

            result = msg_box.exec()

    def get_style(self):
        try:
            with open(resource_path("css/view_password_button.css"), 'r') as file:
                self.view_password_style = file.read()
            with open(resource_path("css/button.css"), 'r') as file:
                self.button_style = file.read()
            with open(resource_path("css/line_edit.css"), 'r') as file:
                self.line_edit_style = file.read()
            with open(resource_path("css/screen_background.css"), 'r') as file:
                self.screen_style = file.read()
        except FileNotFoundError:
            pass
