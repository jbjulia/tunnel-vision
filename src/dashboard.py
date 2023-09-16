from PyQt6 import uic, QtGui
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, Qt, QTimer, QSize
from PyQt6.QtGui import QMouseEvent, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QGraphicsOpacityEffect,
    QMainWindow,
    QMessageBox,
    QApplication,
)

from src import functions as f
from src.ovpn import OpenVPN


class Dashboard(QMainWindow):
    def __init__(self, ui):
        super(Dashboard, self).__init__()
        uic.loadUi(ui, self)

        self.opacity_animation = None
        self.opacity_effect = None
        self.timer = None
        self.offset = None

        self.init_ui()
        self.start_timer()
        self.connect_signals()

    def init_ui(self):
        self.set_state("MENU")
        self.setWindowTitle("Dashboard")
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.opacity_effect = QGraphicsOpacityEffect(self.lblLogo)
        self.lblLogo.setGraphicsEffect(self.opacity_effect)
        self.setup_opacity_animation()
        self.setup_icons()
        self.lblConnectionStatus.setText(f.curl_ip_info())

    def start_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_ip_label)
        self.timer.start(5000)  # 1000 milliseconds = 1 second

    def update_ip_label(self):
        self.lblConnectionStatus.setText(f.curl_ip_info())

    def setup_opacity_animation(self):
        self.opacity_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.opacity_animation.setDuration(3000)
        self.opacity_animation.setStartValue(0)
        self.opacity_animation.setEndValue(1)
        self.opacity_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.opacity_animation.start()

    def setup_icons(self):
        self.lblLogo.setPixmap(QPixmap("resources/ui/logos/tunnel-vision-logo.png"))
        self.btnBuildNewTunnel.setIcon(QIcon("resources/ui/icons/arrow-right.svg"))
        self.btnConnectVPN.setIcon(QIcon("resources/ui/icons/lock.svg"))
        self.btnDisconnectVPN.setIcon(QIcon("resources/ui/icons/unlock.svg"))
        self.btnDeleteTunnel.setIcon(QIcon("resources/ui/icons/trash.svg"))
        self.btnQuitApplication.setIcon(QIcon("resources/ui/icons/x.svg"))

    def connect_signals(self):
        self.btnBuildNewTunnel.clicked.connect(self.build_new_tunnel)
        self.btnConnectVPN.clicked.connect(f.connect_vpn)
        self.btnDeleteTunnel.clicked.connect(f.delete_tunnel)
        self.btnDisconnectVPN.clicked.connect(f.disconnect_vpn)
        self.btnQuitApplication.clicked.connect(f.quit_application)

        self.btnRandomizeName.clicked.connect(self.randomize_name)
        self.btnGetPrivateIP.clicked.connect(self.get_private_ip)
        self.btnStartOver.clicked.connect(self.start_over)
        self.btnGenerateConfigurations.clicked.connect(self.generate_configurations)

    def build_new_tunnel(self):
        self.set_state("CONFIGURATION")

    def randomize_name(self):
        self.txtTunnelName.setText(f.create_tunnel_name())

    def get_private_ip(self):
        self.txtClientPrivateIP.setText(f.get_private_ip())

    def start_over(self):
        self.txtTunnelName.setText("")
        self.txtClientPrivateIP.setText("")
        self.cmbAvailableServers.setCurrentIndex(-1)
        self.radP2P.setChecked(True)
        self.rad1194UDP.setChecked(True)

        self.set_state("MENU")

    def display_warning(self, title, text):
        QMessageBox.warning(self, title, text, QMessageBox.StandardButton.Ok)

    def generate_configurations(self):
        if self.validate_fields():
            tunnel_name = self.txtTunnelName.text().strip()
            ip_dict = f.get_servers(self.cmbAvailableServers.currentIndex())

            if self.rad1194UDP.isChecked():
                port_number = "1194"
                protocol = "udp"
            elif self.rad443TCP.isChecked():
                port_number = "443"
                protocol = "tcp"
            elif self.rad53UDP.isChecked():
                port_number = "53"
                protocol = "udp"
            else:
                port_number = "1194"
                protocol = "udp"

            OpenVPN(
                connection_type="p2p" if self.radP2P.isChecked() else "subnet",
                tunnel_name=tunnel_name,
                server_public_ip=ip_dict["public_ip"],
                server_private_ip=ip_dict["private_ip"],
                client_private_ip=self.txtClientPrivateIP.text().strip(),
                interface_name="tun0",
                port_number=port_number,
                protocol=protocol,
            )

            ip_dict = f.get_servers(self.cmbAvailableServers.currentIndex())

            f.copy_to_server(ip_dict["public_ip"], tunnel_name)

            reply = QMessageBox.question(
                self,
                "Success",
                "Tunnel configured successfully.\n\nWould you like to attempt to connect?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if reply == QMessageBox.StandardButton.Yes:
                f.connect_vpn(server_ip=ip_dict["public_ip"], tunnel_name=tunnel_name)

            self.set_state("MENU")

    def validate_fields(self):
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
            return False
        return True

    def set_state(self, state):
        state_map = {
            "MENU": {"show": [self.wgtMainMenu], "hide": [self.wgtConfiguration]},
            "CONFIGURATION": {
                "show": [self.wgtConfiguration],
                "hide": [self.wgtMainMenu],
            },
        }

        if state in state_map:
            for widget in state_map[state]["show"]:
                widget.setVisible(True)
            for widget in state_map[state]["hide"]:
                widget.setVisible(False)

        self.smart_resize()
        self.center_on_screen()

    def smart_resize(self, width_percentage=0.5, height_percentage=0.7):
        screen_geometry = QApplication.primaryScreen().geometry()
        width = int(screen_geometry.width() * width_percentage)
        height = int(screen_geometry.height() * height_percentage)
        self.resize(QSize(width, height))

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
