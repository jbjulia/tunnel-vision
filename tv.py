#!/usr/bin/env python3

import sys

from PyQt6.QtWidgets import QApplication

from resources import constants as c
from src import prompt_user, utils
from src.dashboard import Dashboard

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Check if the OS is Linux and if the script is run with superuser privileges
    if utils.check_os() and utils.check_privileges():
        # Check for missing dependencies
        missing_packages = utils.check_dependencies()
        if missing_packages:
            missing_str = "\n".join(missing_packages)
            prompt_user.message(
                title="Missing Dependencies",
                text=f"The following packages are missing:\n\n{missing_str}\n\nPlease install them and restart the "
                f"application.",
                icon_type="critical",
            )
            sys.exit(1)

        # Initialize and show the dashboard
        window = Dashboard(ui=c.DASHBOARD)
        window.show()
        sys.exit(app.exec())

    else:
        prompt_user.message(
            title="Error",
            text="This application is intended to be run on Linux (e.g. Ubuntu, Pop!_OS) with superuser "
            "privileges.\n\nPlease ensure you are using the correct operating system and that you are running this "
            "application with superuser privileges.",
            icon_type="critical",
        )
        sys.exit(1)
