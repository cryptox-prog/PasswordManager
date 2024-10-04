import sys
import os
import mysql.connector
from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtGui import QIcon, QClipboard
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QTableWidget, \
    QTableWidgetItem, QHeaderView, QScrollBar, QSpacerItem, QSizePolicy, QMessageBox, QLabel, QPlainTextEdit, \
    QFormLayout

"""
CREATE TABLE Passwords (
ID INT AUTO_INCREMENT PRIMARY KEY,
Website VARCHAR(255) NOT NULL,
Username VARCHAR(255) NOT NULL,
Password VARCHAR(255) NOT NULL,
Notes VARCHAR(255),
UNIQUE (Website, Username)
);
pyinstaller --noconsole --add-data "css;css" --add-data "images;images" --icon="app_icon.ico" main.py
"""

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class QueryWindow(QWidget):
    change_pas_templ_query = "ALTER USER '<u>'@'localhost' IDENTIFIED BY '<p>'; FLUSH PRIVILEGES;"

    def __init__(self, mode, username, password, data=change_pas_templ_query):
        super().__init__()
        self.setGeometry(0, 0, 600, 350)
        self.setWindowIcon(QIcon(resource_path("images/app_icon.png")))
        self.setWindowTitle("Query")

        data = data.replace('<u>', username)

        self.password_manager_window = None

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

        password_line_edit = QLineEdit()
        password_line_edit.setPlaceholderText("Password")
        password_line_edit.setStyleSheet(self.line_edit_style)

        horizontal_layout = QHBoxLayout()
        label = QLabel("Query")
        label.setStyleSheet(self.label_style)

        horizontal_spacer = QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)

        copy_query_button = QPushButton()
        copy_query_button.setIcon(QIcon(resource_path("images/copy_icon.png")))
        copy_query_button.setToolTip("Copy Query")
        copy_query_button.setStyleSheet(self.copy_button_style)
        copy_query_button.setCursor(Qt.PointingHandCursor)

        horizontal_layout.addWidget(label)
        horizontal_layout.addItem(horizontal_spacer)
        horizontal_layout.addWidget(copy_query_button)

        plain_text_edit = QPlainTextEdit()
        plain_text_edit.setPlaceholderText("Query")
        plain_text_edit.setStyleSheet(self.plain_text_edit_style)
        plain_text_edit.setPlainText(data)

        scroll = QScrollBar()
        scroll.setStyleSheet(self.scroll_style)
        plain_text_edit.setVerticalScrollBar(scroll)

        copy_query_button.clicked.connect(lambda: self.copy_text(plain_text_edit))

        close_window_button = QPushButton()
        close_window_button.setText("Close")
        close_window_button.setStyleSheet(self.button_style)
        close_window_button.setCursor(Qt.PointingHandCursor)
        close_window_button.clicked.connect(lambda: self.close_wind(username, password))

        vertical_spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        password_line_edit.textChanged.connect(lambda: self.set_data(data, password_line_edit.text(), plain_text_edit))

        vertical_layout.addItem(vertical_spacer)
        vertical_layout.addWidget(password_line_edit)
        vertical_layout.addLayout(horizontal_layout)
        vertical_layout.addWidget(plain_text_edit)
        vertical_layout.addWidget(close_window_button)
        vertical_layout.addItem(vertical_spacer)

        if mode == self.transfer_password_mode:
            password_line_edit.hide()

    def get_styles(self):
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

    @staticmethod
    def set_data(temp_query, _text, text_display: QPlainTextEdit):
        text_display.setPlainText(temp_query.replace('<p>', _text))

    @staticmethod
    def copy_text(text_edit: QPlainTextEdit):
        text_to_copy = text_edit.toPlainText()

        if text_to_copy:
            clipboard = QApplication.clipboard()
            clipboard.setText(text_to_copy, mode=QClipboard.Clipboard)

    def close_wind(self, _username, _password):
        self.password_manager_window = PasswordManagerWindow(_username, _password)
        self.password_manager_window.show()
        self.close()


class DataWindow(QWidget):
    def __init__(self, mode, username, password, data_id=1):
        super().__init__()
        self.setWindowTitle("Data")
        self.setGeometry(0, 0, 700, 400)
        self.setWindowIcon(QIcon(resource_path("images/app_icon.png")))

        self.rest_usr = username
        self.rest_pas = password
        self.rest_id = data_id

        self.host = "localhost"
        self.database = "passwordsdb"
        self.data_table = "Passwords"
        self.connection = None
        self.cursor = None

        self.password_manager_window = None

        self.view_data_mode = 'v'
        self.add_data_mode = 'a'

        self.screen_style = ""
        self.button_style = ""
        self.copy_button_style = ""
        self.line_edit_style = ""
        self.plain_text_edit_style = ""
        self.label_style = ""

        self.get_styles()

        self.setStyleSheet(self.screen_style)

        layout = QVBoxLayout(self)

        form_layout = QFormLayout()

        website_layout = QHBoxLayout()
        website_label = QLabel("Website:")
        website_label.setStyleSheet(self.label_style)

        self.website_line_edit = QLineEdit()
        self.website_line_edit.setStyleSheet(self.line_edit_style)
        self.website_line_edit.setPlaceholderText("Website")

        self.website_copy_button = QPushButton()
        self.website_copy_button.setToolTip("Copy Website")
        self.website_copy_button.setIcon(QIcon(resource_path("images/copy_icon.png")))
        self.website_copy_button.setCursor(Qt.PointingHandCursor)
        self.website_copy_button.clicked.connect(lambda: self.copy_text(self.website_line_edit))
        self.website_copy_button.setStyleSheet(self.copy_button_style)
        website_layout.addWidget(self.website_line_edit)
        website_layout.addWidget(self.website_copy_button)
        form_layout.addRow(website_label, website_layout)

        username_layout = QHBoxLayout()
        username_label = QLabel("Username:")
        username_label.setStyleSheet(self.label_style)
        self.username_line_edit = QLineEdit()
        self.username_line_edit.setStyleSheet(self.line_edit_style)
        self.username_line_edit.setPlaceholderText("Username")
        self.username_copy_button = QPushButton()
        self.username_copy_button.setToolTip("Copy Username")
        self.username_copy_button.setCursor(Qt.PointingHandCursor)
        self.username_copy_button.setIcon(QIcon(resource_path("images/copy_icon.png")))
        self.username_copy_button.clicked.connect(lambda: self.copy_text(self.username_line_edit))
        self.username_copy_button.setStyleSheet(self.copy_button_style)

        username_layout.addWidget(self.username_line_edit)
        username_layout.addWidget(self.username_copy_button)

        form_layout.addRow(username_label, username_layout)

        password_layout = QHBoxLayout()
        password_label = QLabel("Password:")
        password_label.setStyleSheet(self.label_style)
        self.password_line_edit = QLineEdit()
        self.password_line_edit.setStyleSheet(self.line_edit_style)
        self.password_line_edit.setPlaceholderText("Password")
        self.password_copy_button = QPushButton()
        self.password_copy_button.setToolTip("Copy Password")
        self.password_copy_button.setCursor(Qt.PointingHandCursor)
        self.password_copy_button.setIcon(QIcon(resource_path("images/copy_icon.png")))
        self.password_copy_button.clicked.connect(lambda: self.copy_text(self.password_line_edit))
        self.password_copy_button.setStyleSheet(self.copy_button_style)

        password_layout.addWidget(self.password_line_edit)
        password_layout.addWidget(self.password_copy_button)

        form_layout.addRow(password_label, password_layout)

        notes_label = QLabel("Notes:")
        notes_label.setStyleSheet(self.label_style)
        self.notes_text_edit = QPlainTextEdit()
        self.notes_text_edit.setStyleSheet(self.plain_text_edit_style)
        self.notes_text_edit.setPlaceholderText("Notes")

        form_layout.addRow(notes_label, self.notes_text_edit)

        buttons_layout = QHBoxLayout()
        self.edit_entry_button = QPushButton("Edit Entry")
        self.edit_entry_button.setStyleSheet(self.button_style)
        self.edit_entry_button.setCursor(Qt.PointingHandCursor)
        self.edit_entry_button.clicked.connect(self.set_editable)
        self.delete_entry_button = QPushButton("Delete Entry")
        self.delete_entry_button.setStyleSheet(self.button_style)
        self.delete_entry_button.setCursor(Qt.PointingHandCursor)
        self.delete_entry_button.clicked.connect(lambda: self.delete_entry(data_id, username, password))
        self.close_entry_button = QPushButton("Close Entry")
        self.close_entry_button.setCursor(Qt.PointingHandCursor)
        self.close_entry_button.setStyleSheet(self.button_style)
        self.close_entry_button.clicked.connect(lambda: self.close_wind(username, password))
        buttons_layout.addWidget(self.edit_entry_button)
        buttons_layout.addWidget(self.close_entry_button)
        buttons_layout.addWidget(self.delete_entry_button)

        layout.addLayout(form_layout)
        layout.addLayout(buttons_layout)

        if mode == self.view_data_mode:
            self.set_read_only()
            self.get_and_set_data(data_id, username, password)
        elif mode == self.add_data_mode:
            self.set_editable()
            self.edit_entry_button.disconnect()
            self.edit_entry_button.clicked.connect(lambda: self.save_entry(username, password))

    @staticmethod
    def copy_text(text_edit: QLineEdit):
        text_to_copy = text_edit.text()

        if text_to_copy:
            clipboard = QApplication.clipboard()
            clipboard.setText(text_to_copy, mode=QClipboard.Clipboard)

    def get_and_set_data(self, _id, _username, _password):
        try:
            self.connect(_username, _password)
            self.cursor.execute(f"SELECT Website, Username, Password, Notes FROM {self.data_table} WHERE ID = {_id}")
            result = self.cursor.fetchone()
            if result:
                web, user, pas, note = result
                self.website_line_edit.setText(web)
                self.username_line_edit.setText(user)
                self.password_line_edit.setText(pas)
                self.notes_text_edit.setPlainText(note)
            self.connection.close()
        except mysql.connector.Error:
            msg_box = QMessageBox()
            msg_box.setWindowIcon(QIcon(resource_path("images/app_icon.png")))
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setWindowTitle("Connection Error")
            msg_box.setText("Unable to establish a connection.")
            msg_box.setStandardButtons(QMessageBox.Retry | QMessageBox.Cancel)

            result = msg_box.exec()

            if result == QMessageBox.Retry:
                self.connection.close()
                self.get_and_set_data(_id, _username, _password)
            elif result == QMessageBox.Cancel:
                self.connection.close()
                self.password_manager_window = PasswordManagerWindow(_username, _password)
                self.password_manager_window.show()
                self.close()

    def set_read_only(self):
        self.website_line_edit.setReadOnly(True)
        self.username_line_edit.setReadOnly(True)
        self.password_line_edit.setReadOnly(True)
        self.notes_text_edit.setReadOnly(True)

        self.delete_entry_button.setDisabled(False)
        # self.close_entry_button.setDisabled(False)

        self.website_copy_button.setDisabled(False)
        self.username_copy_button.setDisabled(False)
        self.password_copy_button.setDisabled(False)

        self.edit_entry_button.setText("Edit Entry")

    def set_editable(self):
        self.website_line_edit.setReadOnly(False)
        self.username_line_edit.setReadOnly(False)
        self.password_line_edit.setReadOnly(False)
        self.notes_text_edit.setReadOnly(False)

        self.delete_entry_button.setDisabled(True)
        # self.close_entry_button.setDisabled(True)

        self.website_copy_button.setDisabled(True)
        self.username_copy_button.setDisabled(True)
        self.password_copy_button.setDisabled(True)

        self.edit_entry_button.setText("Save Changes")
        self.edit_entry_button.disconnect()
        self.edit_entry_button.clicked.connect(lambda: self.update_entry(self.rest_usr, self.rest_pas))

    def close_wind(self, _username, _password):
        self.password_manager_window = PasswordManagerWindow(_username, _password)
        self.password_manager_window.show()
        self.close()

    def connect(self, _username, _password):
        self.connection = mysql.connector.connect(
            host=self.host,
            user=_username,
            password=_password,
            database=self.database
        )
        self.cursor = self.connection.cursor()

    def delete_entry(self, _id, _username, _password):
        try:
            self.connect(_username, _password)
            self.cursor.execute(f"DELETE FROM {self.data_table} WHERE ID = {_id}")
            self.connection.commit()
            self.connection.close()

            msg_box = QMessageBox()
            msg_box.setWindowIcon(QIcon(resource_path("images/app_icon.png")))
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setWindowTitle("Success")
            msg_box.setText("Deleted Entry From Database.")
            msg_box.setStandardButtons(QMessageBox.Ok)

            result = msg_box.exec()

            if result == QMessageBox.Ok:
                self.password_manager_window = PasswordManagerWindow(_username, _password)
                self.password_manager_window.show()
                self.close()
            else:
                exit()
        except mysql.connector.Error:
            msg_box = QMessageBox()
            msg_box.setWindowIcon(QIcon(resource_path("images/app_icon.png")))
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setWindowTitle("Error")
            msg_box.setText("Unable to delete entry.")
            msg_box.setStandardButtons(QMessageBox.Retry | QMessageBox.Cancel)

            result = msg_box.exec()

            if result == QMessageBox.Retry:
                self.connection.close()
                self.get_and_set_data(_id, _username, _password)
            elif result == QMessageBox.Cancel:
                self.connection.close()
                self.password_manager_window = PasswordManagerWindow(_username, _password)
                self.password_manager_window.show()
                self.close()

    def update_entry(self, _username, _password):
        web_dat = self.website_line_edit.text()
        usr_dat = self.username_line_edit.text()
        pas_dat = self.password_line_edit.text()
        not_dat = self.notes_text_edit.toPlainText()

        query = f"UPDATE {self.data_table} SET Website='{web_dat}', Username='{usr_dat}', Password='{pas_dat}'," \
                f" Notes='{not_dat}' WHERE ID={self.rest_id}"

        try:
            self.connect(_username, _password)
            self.cursor.execute(query)
            self.connection.commit()
            self.connection.close()

            msg_box = QMessageBox()
            msg_box.setWindowIcon(QIcon(resource_path("images/app_icon.png")))
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setWindowTitle("Success")
            msg_box.setText("Updated Entry.")
            msg_box.setStandardButtons(QMessageBox.Ok)

            result = msg_box.exec()

            if result == QMessageBox.Ok:
                self.password_manager_window = PasswordManagerWindow(_username, _password)
                self.password_manager_window.show()
                self.close()
            else:
                exit()
        except mysql.connector.Error as e:
            print(query)
            print(e)
            msg_box = QMessageBox()
            msg_box.setWindowIcon(QIcon(resource_path("images/app_icon.png")))
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setWindowTitle("Error")
            msg_box.setText("Unable to Update entry.")
            msg_box.setStandardButtons(QMessageBox.Retry | QMessageBox.Cancel)

            result = msg_box.exec()

            if result == QMessageBox.Retry:
                self.connection.close()
                self.get_and_set_data(self.rest_id, _username, _password)
            elif result == QMessageBox.Cancel:
                self.connection.close()
                self.password_manager_window = PasswordManagerWindow(_username, _password)
                self.password_manager_window.show()
                self.close()

    def save_entry(self, _username, _password):
        web_dat = self.website_line_edit.text()
        usr_dat = self.username_line_edit.text()
        pas_dat = self.password_line_edit.text()
        not_dat = self.notes_text_edit.toPlainText()

        query = f"INSERT INTO {self.data_table}(Website, Username, Password, Notes)" \
                f"VALUES('{web_dat}', '{usr_dat}', '{pas_dat}', '{not_dat}')"
        try:
            self.connect(_username, _password)
            self.cursor.execute(query)
            self.connection.commit()
            self.connection.close()

            msg_box = QMessageBox()
            msg_box.setWindowIcon(QIcon(resource_path("images/app_icon.png")))
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setWindowTitle("Success")
            msg_box.setText("Added new Entry to Database.")
            msg_box.setStandardButtons(QMessageBox.Ok)

            result = msg_box.exec()

            if result == QMessageBox.Ok:
                self.password_manager_window = PasswordManagerWindow(_username, _password)
                self.password_manager_window.show()
                self.close()
            else:
                exit()
        except mysql.connector.Error:
            msg_box = QMessageBox()
            msg_box.setWindowIcon(QIcon(resource_path("images/app_icon.png")))
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setWindowTitle("Error")
            msg_box.setText("Unable to Add entry.")
            msg_box.setStandardButtons(QMessageBox.Retry | QMessageBox.Cancel)

            result = msg_box.exec()

            if result == QMessageBox.Retry:
                self.connection.close()
                self.save_entry(_username, _password)
            elif result == QMessageBox.Cancel:
                self.connection.close()
                self.password_manager_window = PasswordManagerWindow(_username, _password)
                self.password_manager_window.show()
                self.close()

    def get_styles(self):
        try:
            with open(resource_path("css/screen_background.css"), 'r') as file:
                self.screen_style = file.read()
            with open(resource_path("css/button.css"), 'r') as file:
                self.button_style = file.read()
            with open(resource_path("css/view_password_button.css"), 'r') as file:
                self.copy_button_style = file.read()
            with open(resource_path("css/line_edit.css"), 'r') as file:
                self.line_edit_style = file.read()
            with open(resource_path("css/plain_text_edit.css"), 'r') as file:
                self.plain_text_edit_style = file.read()
            with open(resource_path("css/label.css"), 'r') as file:
                self.label_style = file.read()
        except FileNotFoundError:
            pass


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
        self.view_password_button.setIconSize(self.view_password_button.size())
        self.view_password_button.setIcon(QIcon(resource_path("images/eye_icon.png")))
        self.view_password_button.setCursor(Qt.PointingHandCursor)
        self.view_password_button.installEventFilter(self)
        password_layout.addWidget(self.view_password_button)
        layout.addLayout(password_layout)

        login_button = QPushButton("Login", self)
        login_button.setStyleSheet(self.button_style)
        login_button.setShortcut("Return")
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

            if result == QMessageBox.Retry:
                # self.username_line_edit.clear()
                # self.password_line_edit.clear()
                pass

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


class PasswordManagerWindow(QWidget):
    def __init__(self, username: str, password: str):
        super().__init__()
        self.setGeometry(0, 0, 950, 600)
        self.setWindowTitle("Password Manager")

        self.restr_user = username
        self.restr_pass = password

        self.data_window = None
        self.query_window = None

        self.connection = None
        self.cursor = None

        self.host = "localhost"
        self.database = "passwordsdb"
        self.data_table = "passwords"

        self.connect(username, password)

        self.data = []

        self.get_main_table_data()

        self.screen_style = ""
        self.menu_button_style = ""
        self.menu_button_alter_style = ""
        self.line_edit_style = ""
        self.line_edit_style = ""
        self.table_style = ""
        self.scroll_style = ""

        self.get_styles()

        self.setWindowIcon(QIcon(resource_path("images/app_icon.png")))

        self.setStyleSheet(self.screen_style)

        self.layout = QVBoxLayout(self)

        # Create buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(0)
        self.create_button(button_layout, "Add New Entry", "Enter a new Password", self.add_new_entry)
        self.create_button(button_layout, "Change Password", "Change the App's Password",
                           lambda: self.change_password(username, password))
        self.create_button(button_layout, "Transfer Passwords", "Create a query for all the Passwords",
                           lambda: self.transfer_passwords(username, password))
        self.layout.addLayout(button_layout)

        self.website_search_line_edit = QLineEdit()
        self.website_search_line_edit.setStyleSheet(self.line_edit_style)
        self.website_search_line_edit.setPlaceholderText("Search by Website")
        self.website_search_line_edit.textChanged.connect(self.search)
        setattr(self, "website_search_line_edit", self.website_search_line_edit)
        self.layout.addWidget(self.website_search_line_edit)

        self.username_search_line_edit = QLineEdit()
        self.username_search_line_edit.setStyleSheet(self.line_edit_style)
        self.username_search_line_edit.setPlaceholderText("Search by Username")
        self.username_search_line_edit.textChanged.connect(self.search)
        setattr(self, "username_search_line_edit", self.username_search_line_edit)
        self.layout.addWidget(self.username_search_line_edit)

        self.password_search_line_edit = QLineEdit()
        self.password_search_line_edit.setStyleSheet(self.line_edit_style)
        self.password_search_line_edit.setPlaceholderText("Search by Password")
        self.password_search_line_edit.textChanged.connect(self.search)
        setattr(self, "password_search_line_edit", self.password_search_line_edit)
        self.layout.addWidget(self.password_search_line_edit)

        self.notes_search_line_edit = QLineEdit()
        self.notes_search_line_edit.setStyleSheet(self.line_edit_style)
        self.notes_search_line_edit.setPlaceholderText("Search by Notes")
        self.notes_search_line_edit.textChanged.connect(self.search)
        setattr(self, "notes_search_line_edit", self.notes_search_line_edit)
        self.layout.addWidget(self.notes_search_line_edit)

        self.table = QTableWidget(self)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)

        self.table.cellClicked.connect(self.cell_clicked)

        self.table.setStyleSheet(self.table_style)

        scroll = QScrollBar()
        scroll.setStyleSheet(self.scroll_style)
        self.table.setVerticalScrollBar(scroll)

        # self.table.verticalHeader().setDefaultSectionSize(30)

        self.populate_table(self.get_main_table_data())

        self.table.setHorizontalHeaderLabels(["Website", "Username"])

        self.website_search_line_edit.setFocus()

        self.layout.addWidget(self.table)

    def connect(self, _username, _password):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=_username,
                password=_password,
                database=self.database
            )
            self.cursor = self.connection.cursor()
        except mysql.connector.Error:
            msg_box = QMessageBox()
            msg_box.setWindowIcon(QIcon(resource_path("images/app_icon.png")))
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setWindowTitle("Connection Error")
            msg_box.setText("Unable to establish a connection.")
            msg_box.setStandardButtons(QMessageBox.Retry | QMessageBox.Cancel)

            result = msg_box.exec()

            if result == QMessageBox.Retry:
                self.connect(_username, _password)
            elif result == QMessageBox.Cancel:
                sys.exit()

    def get_main_table_data(self) -> list:
        query = f"SELECT Website, Username FROM {self.data_table} ORDER BY ID"
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        return results

    def populate_table(self, _data: list):
        self.table.setRowCount(len(_data))
        self.table.setColumnCount(2)

        for row_index, row in enumerate(_data):
            for col_index, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.table.setItem(row_index, col_index, item)

    def get_styles(self):
        try:
            with open(resource_path("css/screen_background.css"), 'r') as file:
                self.screen_style = file.read()
            with open(resource_path("css/menu_button.css"), 'r') as file:
                self.menu_button_style = file.read()
            with open(resource_path("css/menu_button_alter.css"), 'r') as file:
                self.menu_button_alter_style = file.read()
            with open(resource_path("css/line_edit.css"), 'r') as file:
                self.line_edit_style = file.read()
            with open(resource_path("css/table.css"), 'r') as file:
                self.table_style = file.read()
            with open(resource_path("css/scrollbar.css"), 'r') as file:
                self.scroll_style = file.read()
        except FileNotFoundError:
            pass

    def create_button(self, layout, text, tooltip, action):
        button = QPushButton(text)
        # button.setFont(QFont('', 10, QFont.Bold))
        button.setToolTip(tooltip)
        button.setCursor(Qt.PointingHandCursor)

        if text == "Change Password":
            button.setStyleSheet(self.menu_button_alter_style)
        else:
            button.setStyleSheet(self.menu_button_style)

        button.clicked.connect(action)
        layout.addWidget(button)

    def search(self):
        conditions = []
        _website = self.website_search_line_edit.text()
        _username = self.username_search_line_edit.text()
        _password = self.password_search_line_edit.text()
        _notes = self.notes_search_line_edit.text()

        if _website:
            conditions.append(f"Website LIKE '%{_website}%'")
        if _username:
            conditions.append(f"Username LIKE '%{_username}%'")
        if _password:
            conditions.append(f"Password LIKE '%{_password}%'")
        if _notes:
            conditions.append(f"Notes LIKE '%{_notes}%'")

        if not conditions:
            query = f"SELECT Website, Username FROM {self.data_table}"
        else:
            query = f"SELECT Website, Username FROM {self.data_table} WHERE {' AND '.join(conditions)} ORDER BY ID"
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        self.populate_table(results)

    def cell_clicked(self, row):
        # Retrieve data from both cells when a cell is clicked
        item1 = self.table.item(row, 0)
        item2 = self.table.item(row, 1)

        if item1 and item2:
            data1 = item1.text()
            data2 = item2.text()

            sql = f"SELECT ID FROM {self.data_table} WHERE Website = %s AND Username = %s"
            self.cursor.execute(sql, (data1, data2))

            # Fetch the results
            results = self.cursor.fetchall()

            if results:
                for row in results:
                    self.data_window = DataWindow('v', self.restr_user, self.restr_pass, row[0])
                    self.data_window.show()
                    self.close()

            else:
                print("No matching rows found.")

    def add_new_entry(self):
        self.data_window = DataWindow('a', self.restr_user, self.restr_pass)
        self.data_window.show()
        self.close()

    def change_password(self, _username, _password):
        self.query_window = QueryWindow('c', _username, _password)
        self.query_window.show()
        self.close()

    def get_data_for_transfer(self):
        query = f"SELECT Website, Username, Password, Notes FROM {self.data_table} ORDER BY ID"
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        return result

    def create_query(self, entries):
        create_table_query = f"CREATE TABLE {self.data_table} (ID INT AUTO_INCREMENT PRIMARY KEY," \
                             "Website VARCHAR(255) NOT NULL," \
                             "Username VARCHAR(255) NOT NULL," \
                             "Password VARCHAR(255) NOT NULL," \
                             "Notes VARCHAR(255)," \
                             "UNIQUE (Website, Username));"

        insert_into_queries = "INSERT INTO Passwords (Website, Username, Password, Notes) VALUES "
        for entry in entries:
            insert_into_query = f"('{entry[0]}', '{entry[1]}', '{entry[2]}', '{entry[3]}'),"
            insert_into_queries += insert_into_query
        insert_into_queries = insert_into_queries[:-1] + ';'

        return create_table_query + " " + insert_into_queries

    def transfer_passwords(self, _username,  _password):
        data = self.get_data_for_transfer()
        query = self.create_query(data)

        self.query_window = QueryWindow('t', _username, _password, query)
        self.query_window.show()
        self.close()


def main():
    app = QApplication(sys.argv)
    # window = DataWindow('v', "root", "passkey", 1)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
