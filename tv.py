#!/usr/bin/env python3

import sys

from src import functions as f

if __name__ == "__main__":
    # Check if the OS is Linux and if the script is run with superuser privileges
    if f.check_os() and f.check_privileges():
        f.display_menu()
    else:
        sys.exit()
