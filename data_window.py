import mysql.connector
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QPlainTextEdit, QMessageBox
from utils import resource_path

class DataWindow(QWidget):
    def __init__(self, mode, username, password, data_id=1):
        super().__init__()
        self.setWindowTitle("Data")
        self.setGeometry(0, 0, 700, 400)
        self.setWindowIcon(QIcon(resource_path("images/app_icon.png")))

        self.mode = mode
        self.username = username
        self.password = password
        self.data_id = data_id

        self.host = "localhost"
        self.database = "passwordsdb"
        self.data_table = "Passwords"

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.website_line_edit = self.create_form_row(form_layout, "Website:")
        self.username_line_edit = self.create_form_row(form_layout, "Username:")
        self.password_line_edit = self.create_form_row(form_layout, "Password:")
        self.notes_text_edit = QPlainTextEdit()
        form_layout.addRow("Notes:", self.notes_text_edit)

        layout.addLayout(form_layout)
        button_layout = QHBoxLayout()

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_entry)
        button_layout.addWidget(self.save_button)

        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_entry)
        button_layout.addWidget(self.delete_button)

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

        if mode == 'v':
            self.populate_fields()

    def create_form_row(self, layout, label_text):
        label = QLabel(label_text)
        line_edit = QLineEdit()
        layout.addRow(label, line_edit)
        return line_edit

    def populate_fields(self):
        try:
            connection = mysql.connector.connect(
                host=self.host,
                user=self.username,
                password=self.password,
                database=self.database
            )
            cursor = connection.cursor()
            cursor.execute(f"SELECT Website, Username, Password, Notes FROM {self.data_table} WHERE ID = %s", (self.data_id,))
            record = cursor.fetchone()
            if record:
                self.website_line_edit.setText(record[0])
                self.username_line_edit.setText(record[1])
                self.password_line_edit.setText(record[2])
                self.notes_text_edit.setPlainText(record[3])
            connection.close()
        except mysql.connector.Error:
            QMessageBox.critical(self, "Error", "Unable to fetch record.")

    def save_entry(self):
        website = self.website_line_edit.text()
        username = self.username_line_edit.text()
        password = self.password_line_edit.text()
        notes = self.notes_text_edit.toPlainText()

        query = f"INSERT INTO {self.data_table}(Website, Username, Password, Notes) VALUES (%s, %s, %s, %s)"
        params = (website, username, password, notes)

        try:
            connection = mysql.connector.connect(
                host=self.host,
                user=self.username,
                password=self.password,
                database=self.database
            )
            cursor = connection.cursor()
            cursor.execute(query, params)
            connection.commit()
            connection.close()
            QMessageBox.information(self, "Success", "Entry saved successfully.")
            self.close()
        except mysql.connector.Error:
            QMessageBox.critical(self, "Error", "Failed to save entry.")

    def delete_entry(self):
        query = f"DELETE FROM {self.data_table} WHERE ID = %s"
        params = (self.data_id,)

        try:
            connection = mysql.connector.connect(
                host=self.host,
                user=self.username,
                password=self.password,
                database=self.database
            )
            cursor = connection.cursor()
            cursor.execute(query, params)
            connection.commit()
            connection.close()
            QMessageBox.information(self, "Success", "Entry deleted successfully.")
            self.close()
        except mysql.connector.Error:
            QMessageBox.critical(self, "Error", "Failed to delete entry.")
