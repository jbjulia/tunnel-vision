import json
import os
import random
import string
import subprocess

from PyQt6 import uic, QtGui
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, Qt, QCoreApplication
from PyQt6.QtGui import QPixmap, QMouseEvent, QIcon
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QGraphicsOpacityEffect

from src import functions as f
from src.ovpn import OpenVPN


def toggle_widget(widget, hide=False):
    widget.setVisible(not widget.isVisible() if not hide else False)


def quit_application():
    QCoreApplication.instance().quit()


class Dashboard(QMainWindow):
    def __init__(self, ui):
        super(Dashboard, self).__init__()
        self.offset = None
        self.opacity_animation = None
        self.opacity_effect = None
        uic.loadUi(ui, self)
        self.username = os.getlogin()

        # Connect main menu buttons
        self.btnBuildNewTunnel.clicked.connect(self.build_new_tunnel)
        self.btnQuitApplication.clicked.connect(quit_application)

        # Connect configuration menu buttons
        self.btnRandomizeName.clicked.connect(self.randomize_name)
        self.btnGetPrivateIP.clicked.connect(self.get_private_ip)
        self.btnStartOver.clicked.connect(self.start_over)
        self.btnGenerateConfigurations.clicked.connect(self.generate_configurations)

        # Initialize visibility of widgets
        toggle_widget(self.wgtConfiguration, hide=True)
        toggle_widget(self.wgtMainMenu, hide=False)

        pixmap = QPixmap("resources/ui/logos/tunnel-vision-logo.png")
        self.lblLogo.setPixmap(pixmap)
        self.init_ui()

    def init_ui(self):
        # self.center_on_screen()
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.opacity_effect = QGraphicsOpacityEffect(self.lblLogo)
        self.lblLogo.setGraphicsEffect(self.opacity_effect)

        self.opacity_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.opacity_animation.setDuration(3000)
        self.opacity_animation.setStartValue(0)
        self.opacity_animation.setEndValue(1)
        self.opacity_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.opacity_animation.start()

        self.btnBuildNewTunnel.setIcon(QIcon("resources/ui/icons/arrow-right.svg"))
        self.btnConnectVPN.setIcon(QIcon("resources/ui/icons/lock.svg"))
        self.btnDisconnectVPN.setIcon(QIcon("resources/ui/icons/unlock.svg"))
        self.btnDeleteTunnel.setIcon(QIcon("resources/ui/icons/trash.svg"))
        self.btnQuitApplication.setIcon(QIcon("resources/ui/icons/x.svg"))

        try:
            # Run curl command to get JSON data from ipinfo.io
            curl_command = ["curl", "https://ipinfo.io"]
            result = subprocess.run(curl_command, stdout=subprocess.PIPE)
            result_str = result.stdout.decode("utf-8")

            # Parse JSON data
            result_json = json.loads(result_str)

            # Extract IP, City and Region
            ip = result_json.get("ip", "N/A")
            city = result_json.get("city", "N/A")
            region = result_json.get("region", "N/A")
            country = result_json.get("country", "N/A")

            self.lblConnectionStatus.setText(
                f"Your current IP Address is {ip} ({city}, {region}, {country})"
            )
        except Exception as e:
            print(f"An error occurred: {e}")

    def build_new_tunnel(self):
        toggle_widget(self.wgtMainMenu, hide=True)
        toggle_widget(self.wgtConfiguration)

    def randomize_name(self):
        random_str = "".join(random.choices(string.ascii_letters + string.digits, k=8))
        self.txtTunnelName.setText(f"{self.username}_{random_str}")

    def get_private_ip(self):
        self.txtClientPrivateIP.setText(f.get_private_ip())

    def start_over(self):
        toggle_widget(self.wgtConfiguration, hide=True)
        toggle_widget(self.wgtMainMenu)

    def display_warning(self, title, text):
        QMessageBox.warning(self, title, text, QMessageBox.StandardButton.Ok)

    def generate_configurations(self):
        if not all(
            [
                self.txtTunnelName.text(),
                self.txtClientPrivateIP.text(),
                self.cmbAvailableServers.currentIndex() != -1,
            ]
        ):
            self.display_warning(
                "Missing Fields", "Please fill out the required fields."
            )
        else:
            connection_type = "p2p" if self.radP2P.isChecked() else "subnet"
            tunnel_name = self.txtTunnelName.text().strip()
            ip_dict = f.get_servers(
                display=False, server=self.cmbAvailableServers.currentIndex()
            )
            client_private_ip = self.txtClientPrivateIP.text().strip()
            port_number = "1194"

            OpenVPN(
                connection_type=connection_type,
                tunnel_name=tunnel_name,
                server_public_ip=ip_dict["public_ip"],
                server_private_ip=ip_dict["private_ip"],
                client_private_ip=client_private_ip,
                interface_name="tun0",
                port_number=port_number,
            )

            # Add a MessageBox prompting to return to the main menu
            reply = QMessageBox.question(
                self,
                "Success",
                "Configurations generated successfully.\n\nWould you like to attempt to connect?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                pass
                # f.connect_vpn(tunnel_name, ip_dict["public_ip"])

    def center_on_screen(self):
        qr = self.frameGeometry()
        cp = QtGui.QGuiApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.offset = event.pos()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.offset:
            self.move(self.pos() + event.pos() - self.offset)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.offset = None
            event.accept()
