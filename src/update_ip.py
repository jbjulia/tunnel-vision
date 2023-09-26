from PyQt6.QtCore import QThread, pyqtSignal
from src import utils


class UpdateIP(QThread):
    signal = pyqtSignal(str, bool)

    def run(self):
        self.curl_ip_info()

    def curl_ip_info(self):
        ip_info = utils.curl_ip_info()
        active_tunnels = utils.find_active_tunnels()
        self.signal.emit(ip_info, active_tunnels)
