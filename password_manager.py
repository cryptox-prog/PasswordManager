import mysql.connector
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, \
    QHeaderView, QScrollBar, QMessageBox
from data_window import DataWindow
from query_window import QueryWindow
from utils import resource_path

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
        self.data_table = "Passwords"

        self.connect(username, password)

        self.get_main_table_data()

        self.screen_style = ""
        self.menu_button_style = ""
        self.line_edit_style = ""
        self.table_style = ""
        self.scroll_style = ""

        self.get_styles()

        self.setWindowIcon(QIcon(resource_path("images/app_icon.png")))

        self.setStyleSheet(self.screen_style)

        self.layout = QVBoxLayout(self)

        # Create buttons
        button_layout = QHBoxLayout()
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
        self.layout.addWidget(self.website_search_line_edit)

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
            QMessageBox.critical(self, "Connection Error", "Unable to establish a connection.")

    def get_main_table_data(self):
        query = f"SELECT Website, Username FROM {self.data_table} ORDER BY ID"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def populate_table(self, data):
        self.table.setRowCount(len(data))
        self.table.setColumnCount(2)
        for row_index, row in enumerate(data):
            for col_index, value in enumerate(row):
                self.table.setItem(row_index, col_index, QTableWidgetItem(str(value)))

    def create_button(self, layout, text, tooltip, action):
        button = QPushButton(text)
        button.setToolTip(tooltip)
        button.setCursor(Qt.PointingHandCursor)
        button.setStyleSheet(self.menu_button_style)
        button.clicked.connect(action)
        layout.addWidget(button)

    def search(self):
        search_query = self.website_search_line_edit.text()
        query = f"SELECT Website, Username FROM {self.data_table} WHERE Website LIKE '%{search_query}%' ORDER BY ID"
        self.cursor.execute(query)
        self.populate_table(self.cursor.fetchall())

    def cell_clicked(self, row):
        website = self.table.item(row, 0).text()
        username = self.table.item(row, 1).text()
        query = f"SELECT ID FROM {self.data_table} WHERE Website = %s AND Username = %s"
        self.cursor.execute(query, (website, username))
        record_id = self.cursor.fetchone()
        if record_id:
            self.data_window = DataWindow('v', self.restr_user, self.restr_pass, record_id[0])
            self.data_window.show()
            self.close()

    def add_new_entry(self):
        self.data_window = DataWindow('a', self.restr_user, self.restr_pass)
        self.data_window.show()
        self.close()

    def change_password(self, username, password):
        self.query_window = QueryWindow('c', username, password)
        self.query_window.show()
        self.close()

    def transfer_passwords(self, username, password):
        query = "SELECT Website, Username, Password, Notes FROM Passwords ORDER BY ID"
        self.cursor.execute(query)
        data = self.cursor.fetchall()
        transfer_query = self.create_transfer_query(data)
        self.query_window = QueryWindow('t', username, password, transfer_query)
        self.query_window.show()
        self.close()

    @staticmethod
    def create_transfer_query(data):
        create_table_query = "CREATE TABLE Passwords (ID INT AUTO_INCREMENT PRIMARY KEY, Website VARCHAR(255), Username VARCHAR(255), Password VARCHAR(255), Notes VARCHAR(255));"
        insert_queries = "INSERT INTO Passwords (Website, Username, Password, Notes) VALUES "
        for entry in data:
            insert_queries += f"('{entry[0]}', '{entry[1]}', '{entry[2]}', '{entry[3]}'),"
        return create_table_query + insert_queries.rstrip(',') + ";"

    def get_styles(self):
        try:
            with open(resource_path("css/menu_button.css"), 'r') as file:
                self.menu_button_style = file.read()
            with open(resource_path("css/line_edit.css"), 'r') as file:
                self.line_edit_style = file.read()
            with open(resource_path("css/table.css"), 'r') as file:
                self.table_style = file.read()
            with open(resource_path("css/scrollbar.css"), 'r') as file:
                self.scroll_style = file.read()
        except FileNotFoundError:
            pass
