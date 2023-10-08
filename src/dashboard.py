from PyQt6 import uic, QtGui
from PyQt6.QtCore import (
    QPropertyAnimation,
    QEasingCurve,
    Qt,
    QTimer,
    QCoreApplication,
)
from PyQt6.QtGui import QMouseEvent, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QGraphicsOpacityEffect,
    QMainWindow,
    QProgressBar,
)

from src import prompt_user, utils
from src.update_ip import UpdateIP
from src.create_tunnel import CreateTunnel


class Dashboard(QMainWindow):
    def __init__(self, ui):
        super(Dashboard, self).__init__()
        uic.loadUi(ui, self)

        self.ip_update_thread = None
        self.circular_loading_bar = None
        self.tunnel_creation_thread = None
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

        self.circular_loading_bar = QProgressBar(self)
        self.circular_loading_bar.setStyleSheet(
            """
        
            QProgressBar {
                border: none,
                border-radius: 24%,
                background-color: transparent;
            }
            QProgressBar::chunk {
                background-color: #8F48D5,
                border-radius: 17%;
            }
        """
        )
        self.circular_loading_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.circular_loading_bar.setRange(0, 100)
        self.circular_loading_bar.setMinimum(0)
        self.circular_loading_bar.setMaximum(0)
        self.circular_loading_bar.hide()

    def resizeEvent(self, event):
        bar_width = 90
        bar_height = 55
        x = (self.width() - bar_width) // 2
        y = (self.height() - bar_height) // 2
        self.circular_loading_bar.setGeometry(x, y, bar_width, bar_height)

    def start_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.initiate_ip_update)
        self.timer.start(5000)

    def initiate_ip_update(self):
        self.ip_update_thread = UpdateIP()
        self.ip_update_thread.signal.connect(self.update_ip_label)
        self.ip_update_thread.start()

    def update_ip_label(self, ip_info, active_tunnels):
        self.lblConnectionStatus.setText(ip_info)
        if active_tunnels:
            self.lblConnectionStatus.setStyleSheet("color: #00B894")
        else:
            self.lblConnectionStatus.setStyleSheet("color: #D63031")

    def setup_opacity_animation(self):
        self.opacity_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.opacity_animation.setDuration(3000)
        self.opacity_animation.setStartValue(0)
        self.opacity_animation.setEndValue(1)
        self.opacity_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.opacity_animation.start()

    def setup_icons(self):
        self.lblLogo.setPixmap(QPixmap("resources/ui/logos/tunnel-vision-logo.png"))
        self.btnBuildTunnel.setIcon(QIcon("resources/ui/icons/arrow-right.svg"))
        self.btnConnectVPN.setIcon(QIcon("resources/ui/icons/lock.svg"))
        self.btnDisconnectVPN.setIcon(QIcon("resources/ui/icons/unlock.svg"))
        self.btnDeleteTunnel.setIcon(QIcon("resources/ui/icons/trash.svg"))
        self.btnQuitApplication.setIcon(QIcon("resources/ui/icons/x.svg"))

        self.btnRandomizeName.setIcon(QIcon("resources/ui/icons/refresh-cw.svg"))
        self.btnGetPrivateIP.setIcon(QIcon("resources/ui/icons/refresh-cw.svg"))
        self.btnCancel.setIcon(QIcon("resources/ui/icons/x.svg"))
        self.btnCreateTunnel.setIcon(QIcon("resources/ui/icons/arrow-right.svg"))

    def connect_signals(self):
        self.btnBuildTunnel.clicked.connect(self.build_new_tunnel)
        self.btnConnectVPN.clicked.connect(utils.connect_vpn)
        self.btnDeleteTunnel.clicked.connect(utils.delete_tunnel)
        self.btnDisconnectVPN.clicked.connect(utils.disconnect_vpn)
        self.btnQuitApplication.clicked.connect(self.quit_application)

        self.btnRandomizeName.clicked.connect(self.randomize_name)
        self.btnGetPrivateIP.clicked.connect(self.get_private_ip)
        self.btnCancel.clicked.connect(self.start_over)
        self.btnCreateTunnel.clicked.connect(self.create_tunnel)

    def build_new_tunnel(self):
        self.set_state("CONFIGURATION")

    def randomize_name(self):
        self.txtTunnelName.setText(utils.create_tunnel_name())

    def get_private_ip(self):
        self.txtClientPrivateIP.setText(utils.get_private_ip())

    def start_over(self):
        self.txtTunnelName.clear()
        self.txtClientPrivateIP.clear()
        self.cmbAvailableServers.setCurrentIndex(-1)
        self.radP2P.setChecked(False)
        self.radSubnet.setChecked(False)
        self.rad1194.setChecked(False)
        self.rad443.setChecked(False)

        self.set_state("MENU")

    def create_tunnel(self):
        if self.validate_fields():
            selected_server = self.cmbAvailableServers.currentText()
            ip_dict = utils.get_servers(selected_server)

            self.circular_loading_bar.show()

            port_number, protocol = (
                ("1194", "udp")
                if self.rad1194.isChecked()
                else ("443", "tcp")
                if self.rad443.isChecked()
                else ("1194", "udp")
            )

            args = {
                "connection_type": "p2p" if self.radP2P.isChecked() else "subnet",
                "tunnel_name": self.txtTunnelName.text().strip(),
                "server_public_ip": ip_dict["public_ip"],
                "server_private_ip": ip_dict["private_ip"],
                "client_private_ip": self.txtClientPrivateIP.text().strip(),
                "interface_name": "tun0",
                "port_number": port_number,
                "protocol": protocol,
            }

            self.tunnel_creation_thread = CreateTunnel(args)
            self.tunnel_creation_thread.signal.connect(self.handle_tunnel_creation)
            self.tunnel_creation_thread.start()
            self.set_button_states(False)

    def handle_tunnel_creation(self):
        self.set_button_states(True)
        self.circular_loading_bar.hide()
        self.set_state("MENU")

    def validate_fields(self):
        is_valid = all(
            [
                self.txtTunnelName.text(),
                self.txtClientPrivateIP.text(),
                self.cmbAvailableServers.currentIndex() != -1,
                (self.radP2P.isChecked() or self.radSubnet.isChecked()),
                (self.rad1194.isChecked() or self.rad443.isChecked()),
            ]
        )

        if not is_valid:
            prompt_user.message(
                icon_type="warning",
                title="Missing Fields",
                text="Please fill out the required fields.",
            )
            return False

        return True

    def set_button_states(self, state: bool):
        self.btnBuildTunnel.setEnabled(state)
        self.btnConnectVPN.setEnabled(state)
        self.btnDeleteTunnel.setEnabled(state)
        self.btnDisconnectVPN.setEnabled(state)
        self.btnQuitApplication.setEnabled(state)
        self.btnRandomizeName.setEnabled(state)
        self.btnGetPrivateIP.setEnabled(state)
        self.btnCancel.setEnabled(state)
        self.btnCreateTunnel.setEnabled(state)

    def set_state(self, state):
        state_map = {
            "MENU": {"show": [self.wgtMenu], "hide": [self.wgtConfiguration]},
            "CONFIGURATION": {
                "show": [self.wgtConfiguration],
                "hide": [self.wgtMenu],
            },
        }

        if state in state_map:
            for widget in state_map[state]["show"]:
                widget.setVisible(True)

            for widget in state_map[state]["hide"]:
                widget.setVisible(False)

        self.center_on_screen()

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
                utils.disconnect_vpn(prompt=False)

        self.timer.stop()
        QCoreApplication.quit()
