from PyQt6.QtCore import QThread, pyqtSignal
from src import prompt_user, utils
from src.ovpn import OpenVPN


class CreateTunnel(QThread):
    signal = pyqtSignal(str)

    def __init__(self, args):
        super().__init__()
        self.args = args

    def run(self):
        try:
            tunnel = self.init_tunnel()
            if not tunnel.successful_init:
                self.handle_init_failure()
                return

            if not self.setup_server():
                self.handle_setup_failure()
                return

            self.signal.emit("Success")

            response = prompt_user.message(
                icon_type="question",
                title="Success",
                text="Your tunnel has been successfully created.\n\nWould you like to attempt to connect?",
                buttons=["Yes", "No"],
            )

            if response == "Yes":
                utils.connect_vpn(prompt=False)

        except Exception as e:
            self.signal.emit(f"Failure: {str(e)}")

    def init_tunnel(self):
        return OpenVPN(
            connection_type=self.args["connection_type"],
            tunnel_name=self.args["tunnel_name"],
            server_public_ip=self.args["server_public_ip"],
            server_private_ip=self.args["server_private_ip"],
            client_private_ip=self.args["client_private_ip"],
            interface_name=self.args["interface_name"],
            port_number=self.args["port_number"],
            protocol=self.args["protocol"],
        )

    def handle_init_failure(self):
        prompt_user.message(
            icon_type="critical",
            title="Error!",
            text="The Tunnel failed to setup correctly!",
        )
        utils.cleanup_failure(self.args["tunnel_name"])

    def setup_server(self):
        return utils.copy_to_server(
            self.args["server_public_ip"], self.args["tunnel_name"]
        ) and utils.write_iptables_to_server(
            self.args["interface_name"],
            self.args["port_number"],
            self.args["protocol"],
            self.args["server_public_ip"],
        )

    def handle_setup_failure(self):
        utils.cleanup_failure(self.args["tunnel_name"])
        raise Exception("Failed to copy files to server!")
