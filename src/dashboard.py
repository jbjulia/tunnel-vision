from PyQt6 import uic, QtGui
from PyQt6.QtCore import (
    QPropertyAnimation,
    QEasingCurve,
    Qt,
    QTimer,
    QSize,
    QCoreApplication,
)
from PyQt6.QtGui import QMouseEvent, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QGraphicsOpacityEffect,
    QMainWindow,
    QApplication,
)

from resources import constants as c
from src import prompt_user, utils
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

    def start_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_ip_label)
        self.timer.start(5000)  # 1000 milliseconds = 1 second

    def update_ip_label(self):
        self.lblConnectionStatus.setText(utils.curl_ip_info())

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
        self.btnConnectVPN.clicked.connect(utils.connect_vpn)
        self.btnDeleteTunnel.clicked.connect(utils.delete_tunnel)
        self.btnDisconnectVPN.clicked.connect(utils.disconnect_vpn)
        self.btnQuitApplication.clicked.connect(self.quit_application)

        self.btnRandomizeName.clicked.connect(self.randomize_name)
        self.btnGetPrivateIP.clicked.connect(self.get_private_ip)
        self.btnStartOver.clicked.connect(self.start_over)
        self.btnCreateTunnel.clicked.connect(self.create_tunnel)

    def build_new_tunnel(self):
        self.set_state("CONFIGURATION")

    def randomize_name(self):
        self.txtTunnelName.setText(utils.create_tunnel_name())

    def get_private_ip(self):
        self.txtClientPrivateIP.setText(utils.get_private_ip())

    def start_over(self):
        self.txtTunnelName.setText("")
        self.txtClientPrivateIP.setText("")
        self.cmbAvailableServers.setCurrentIndex(-1)
        self.radP2P.setChecked(True)
        self.rad1194UDP.setChecked(True)

        self.set_state("MENU")

    def create_tunnel(self):
        if self.validate_fields():
            existing_tunnels = utils.load_json(c.TUNNELS)
            if existing_tunnels:
                response = prompt_user.message(
                    icon_type="question",
                    title="Tunnel Already Exist",
                    text="A tunnel already exists. Would you like to delete it and create a new one?",
                    buttons=["Yes", "No"],
                )
                if response == "No":
                    self.set_state("MENU")
                    return
                else:
                    utils.delete_tunnel(prompt=False)

            tunnel_name = self.txtTunnelName.text().strip()
            selected_server = self.cmbAvailableServers.currentText()
            ip_dict = utils.get_servers(selected_server)

            if self.rad1194UDP.isChecked():
                port_number, protocol = "1194", "udp"
            elif self.rad443TCP.isChecked():
                port_number, protocol = "443", "tcp"
            elif self.rad53UDP.isChecked():
                port_number, protocol = "53", "udp"
            else:
                port_number, protocol = "1194", "udp"

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

            utils.copy_to_server(ip_dict["public_ip"], tunnel_name)

            response = prompt_user.message(
                icon_type="question",
                title="Success",
                text="Your tunnel has been successfully created.\n\nWould you like to attempt to connect?",
                buttons=["Yes", "No"],
            )

            if response == "Yes":
                utils.connect_vpn(prompt=False)

            self.set_state("MENU")

    def validate_fields(self):
        if not all(
            [
                self.txtTunnelName.text(),
                self.txtClientPrivateIP.text(),
                self.cmbAvailableServers.currentIndex() != -1,
            ]
        ):
            prompt_user.message(
                icon_type="warning",
                title="Missing Fields",
                text="Please fill out the required fields.",
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

    def quit_application(self):
        if utils.find_active_tunnels():
            user_response = prompt_user.message(
                icon_type="question",
                title="Active Tunnels",
                text="Active OpenVPN tunnels found. Would you like to close them?",
                buttons=("Yes", "No"),
            )

            if user_response == "Yes":
                utils.disconnect_vpn()

        self.timer.stop()
        QCoreApplication.quit()
