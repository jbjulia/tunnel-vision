#!/usr/bin/env python3

import sys

from PyQt6.QtWidgets import QApplication

from resources import constants as c
from src import functions as f
from src.dashboard import Dashboard

if __name__ == "__main__":
    # Check if the OS is Linux and if the script is run with superuser privileges
    if f.check_os() and f.check_privileges():
        # f.display_menu()
        pass
    else:
        # sys.exit()
        pass

    app = QApplication(sys.argv)
    window = Dashboard(ui=c.DASHBOARD)
    window.show()
    sys.exit(app.exec())
