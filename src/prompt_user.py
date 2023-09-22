from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import (
    QMessageBox,
)


def message(icon_type, title, text, buttons=None):
    window = QMessageBox()
    window.setFixedSize(QSize(400, 200))

    icon_mapping = {
        "info": QMessageBox.Icon.Information,
        "warning": QMessageBox.Icon.Warning,
        "critical": QMessageBox.Icon.Critical,
        "question": QMessageBox.Icon.Question,
    }

    window.setIcon(icon_mapping.get(icon_type, QMessageBox.Icon.NoIcon))
    window.setWindowTitle(title)
    window.setText(text)

    clicked_button = None
    if buttons:
        button_flags = 0
        for button in buttons:
            button_flags |= getattr(QMessageBox.StandardButton, button)
        window.setStandardButtons(button_flags)

        if window.exec():
            for button in buttons:
                if window.standardButton(window.clickedButton()) == getattr(
                    QMessageBox.StandardButton, button
                ):
                    clicked_button = button
                    break
    else:
        window.exec()

    return clicked_button
