from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import (
    QMessageBox,
    QDialog,
    QVBoxLayout,
    QComboBox,
    QDialogButtonBox,
    QLabel,
)

from resources import constants as c
from src import utils


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


def dialog(title):
    window = QDialog()
    window.setFixedSize(QSize(400, 200))
    window.setWindowTitle(title)

    layout = QVBoxLayout()
    layout.setSpacing(5)  # Adjust this value as needed

    label = QLabel("Please select a tunnel:")
    layout.addWidget(label)

    combo_box = QComboBox()
    combo_box.setFixedSize(QSize(380, 30))

    tunnels = utils.load_json(c.TUNNELS)

    if not tunnels:
        message(
            icon_type="info",
            title="No Tunnels",
            text="There are no tunnels configured.",
        )
        return None

    combo_box.addItems(list(tunnels.keys()))
    layout.addWidget(combo_box)

    button_box = QDialogButtonBox(
        QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
    )
    button_box.accepted.connect(window.accept)
    button_box.rejected.connect(window.reject)

    layout.addWidget(button_box)
    window.setLayout(layout)

    result = window.exec()

    if result == QDialog.DialogCode.Accepted:
        return combo_box.currentText()
    else:
        return None
