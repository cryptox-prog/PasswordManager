from PyQt5.QtWidgets import QApplication
from login_window import LoginWindow
import sys

def main():
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
