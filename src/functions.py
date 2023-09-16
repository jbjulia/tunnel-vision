import getpass
import ipaddress
import json
import os
import random
import shutil
import socket
import string
import subprocess
import sys

from PyQt6.QtCore import QCoreApplication, QSize
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QComboBox,
    QPushButton,
    QDialogButtonBox,
)
from PyQt6.QtWidgets import QMessageBox

from resources import constants as c


def prompt_user(icon_type, title, text, buttons=None):
    msg = QMessageBox()
    icon_mapping = {
        "info": QMessageBox.Icon.Information,
        "warning": QMessageBox.Icon.Warning,
        "critical": QMessageBox.Icon.Critical,
        "question": QMessageBox.Icon.Question,
    }
    msg.setIcon(icon_mapping.get(icon_type, QMessageBox.Icon.NoIcon))
    msg.setWindowTitle(title)
    msg.setText(text)

    clicked_button = None
    if buttons:
        button_flags = 0
        for button in buttons:
            button_flags |= getattr(QMessageBox.StandardButton, button)
        msg.setStandardButtons(button_flags)

        if msg.exec():
            for button in buttons:
                if msg.standardButton(msg.clickedButton()) == getattr(
                    QMessageBox.StandardButton, button
                ):
                    clicked_button = button
                    break

    else:
        msg.exec()

    return clicked_button


def create_dialog(title, options_list, callback):
    dialog = QDialog()
    dialog.setWindowTitle(title)
    dialog.resize(QSize(400, 200))

    layout = QVBoxLayout()

    combo_box = QComboBox()
    combo_box.addItems(options_list)

    btn_action = QPushButton(title)

    layout.addWidget(combo_box)
    layout.addWidget(btn_action)

    dialog.setLayout(layout)

    def on_button_clicked():
        selected_option = combo_box.currentText()
        if selected_option:
            callback(selected_option)
        dialog.accept()

    btn_action.clicked.connect(on_button_clicked)
    dialog.exec()


def check_os():
    if sys.platform != "linux":
        return False
    return True


def check_privileges():
    if os.geteuid() != 0:
        return False
    return True


def check_dependencies():
    dependencies = [
        "curl",
        "git",
        "openvpn",
        # "python3-pexpect",
        # "python3-pyqt6",
        "sshpass",
    ]

    missing_packages = []

    for package_name in dependencies:
        result = subprocess.run(
            ["dpkg", "-l", package_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        if result.returncode == 0:
            pass
        else:
            missing_packages.append(package_name)

    return missing_packages


def get_login():
    try:
        return os.getlogin()
    except OSError:
        return getpass.getuser()


def create_tunnel_name():
    random_str = "".join(random.choices(string.ascii_letters + string.digits, k=8))

    return f"{get_login()}_{random_str}"


def curl_ip_info():
    curl_command = ["curl", "https://ipinfo.io"]
    result = subprocess.run(curl_command, stdout=subprocess.PIPE)
    result_str = result.stdout.decode("utf-8")
    result_json = json.loads(result_str)

    ip = result_json.get("ip", "N/A")
    city = result_json.get("city", "N/A")
    region = result_json.get("region", "N/A")
    country = result_json.get("country", "N/A")

    return f"Your current IP Address is {ip} ({city}, {region}, {country})"


def validate_ip(ip_address):
    while True:
        if not ip_address:
            return get_private_ip()

        try:
            return str(ipaddress.ip_address(ip_address))
        except ValueError:
            prompt_user(
                icon_type="warning",
                title="Invalid IP",
                text="Please enter a valid IP.",
            )


def validate_port(port):
    while True:
        try:
            if 1024 <= port <= 49151:
                return port
            else:
                prompt_user(
                    icon_type="warning",
                    title="Invalid Port",
                    text="Please enter a value in the unprivileged range (1024-49151).",
                )
        except ValueError:
            prompt_user(
                icon_type="warning",
                title="Invalid Port",
                text="Please enter a numerical value",
            )


def get_private_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        s.connect(("10.255.255.255", 1))
        private_ip = s.getsockname()[0]
    except socket.gaierror:
        prompt_user(
            title="Error",
            text="There was an address related error.",
            icon_type="critical",
        )
        private_ip = "127.0.0.1"
    except socket.timeout:
        prompt_user(
            title="Error",
            text="Connection timed out.",
            icon_type="critical",
        )
        private_ip = "127.0.0.1"
    except OSError:
        prompt_user(
            title="Error",
            text="OS error, possibly related to permissions or other system-related issues",
            icon_type="critical",
        )
        private_ip = "127.0.0.1"
    finally:
        s.close()

    return private_ip


def load_json(json_file):
    with open(json_file) as in_file:
        data = json.load(in_file)

    return data


def dump_json(data, json_file):
    with open(json_file, "w") as out_file:
        json.dump(data, out_file, indent=4, sort_keys=True)


def get_servers(index):
    servers = load_json(c.SERVERS)
    server_list = list(servers.keys())

    return servers[server_list[index]]


def copy_to_server(server_public_ip, tunnel_name):
    local_server_conf_path = f"{c.TESTS}{tunnel_name}/{tunnel_name}-server.conf"
    local_jail_path = f"{c.TESTS}{tunnel_name}/{tunnel_name}-jail"

    tmp_path = f"root@{server_public_ip}:/tmp/"
    destination_openvpn = "/etc/openvpn/"

    scp_flags = "-P 22 -C"  # -vvv"
    ssh_flags = "-o StrictHostKeyChecking=no"

    local_paths = {
        f"{tunnel_name}-server.conf": (local_server_conf_path, destination_openvpn),
        f"{tunnel_name}-jail": (local_jail_path, destination_openvpn),
    }

    try:
        for item, (local_path, destination) in local_paths.items():
            command = f"sshpass -p {c.PASS} scp {scp_flags} {'-r' if 'jail' in item else ''} {local_path} {tmp_path}"
            subprocess.check_call(command, shell=True)

            command = (
                f"sshpass -p '{c.PASS}' ssh {ssh_flags} root@{server_public_ip} "
                f"'mv /tmp/{item} {destination}'"
            )
            subprocess.check_call(command, shell=True)

        prompt_user(
            title="Success",
            text="Copy to server completed successfully!",
            icon_type="info",
        )

        return True

    except subprocess.CalledProcessError as e:
        prompt_user(
            title="Error",
            text=f"The following error occurred when copying files to the server:\n\n{e}",
            icon_type="critical",
        )

        return False


def dialog_select_tunnel(title):
    dialog = QDialog()
    dialog.setWindowTitle(title)
    dialog.resize(400, 200)

    layout = QVBoxLayout()
    combo_box = QComboBox()

    tunnels = load_json(c.TUNNELS)

    if not tunnels:
        prompt_user(
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

    # Connect the buttons to appropriate slots
    button_box.accepted.connect(dialog.accept)

    button_box.rejected.connect(dialog.reject)

    layout.addWidget(button_box)
    dialog.setLayout(layout)

    result = dialog.exec()

    if result == QDialog.DialogCode.Accepted:
        return combo_box.currentText()
    else:
        return None


def connect_vpn(server_ip=None, tunnel_name=None):
    def execute_connection(server_ip, tunnel_name):
        try:
            ssh_cmd = f"sshpass -p {c.PASS} ssh root@{server_ip} 'sudo systemctl start openvpn@{tunnel_name}-server'"
            subprocess.run(ssh_cmd, shell=True, check=True)

            local_client_conf_path = f"{c.TESTS}{tunnel_name}/{tunnel_name}-client.conf"
            destination_path = f"/etc/openvpn/{tunnel_name}-client.conf"
            copy_cmd = f"sudo cp {local_client_conf_path} {destination_path}"
            subprocess.run(copy_cmd, shell=True, check=True)

            client_cmd = f"sudo systemctl start openvpn@{tunnel_name}-client"
            subprocess.run(client_cmd, shell=True, check=True)

            prompt_user(
                title="Success",
                text="Successfully connected to the VPN.",
                icon_type="info",
            )
            return True
        except Exception as e:
            prompt_user(
                title="Error",
                text=f"Error while connecting to VPN: {str(e)}",
                icon_type="critical",
            )
            return False

    if not (server_ip and tunnel_name):
        selected_tunnel = dialog_select_tunnel("Select Tunnel to Connect")
        if selected_tunnel:
            tunnels = load_json(c.TUNNELS)
            server_ip = tunnels[selected_tunnel]["server_public_ip"]
            tunnel_name = selected_tunnel

    return execute_connection(server_ip, tunnel_name)


def disconnect_vpn(tunnel_name=None):
    if not tunnel_name:
        tunnel_name = dialog_select_tunnel("Select Tunnel to Disconnect")
        if not tunnel_name:
            return

    # Load tunnel information
    tunnels = load_json(c.TUNNELS)
    if tunnel_name in tunnels:
        server_ip = tunnels[tunnel_name]["server_public_ip"]
    else:
        prompt_user(icon_type="critical", title="Error", text="Tunnel not found.")
        return

    try:
        # Stop client side service
        subprocess.run(
            [f"sudo systemctl stop openvpn@{tunnel_name}-client"],
            shell=True,
            check=True,
        )

        # Stop server side service via SSH
        ssh_cmd = f"sshpass -p {c.PASS} ssh root@{server_ip} 'sudo systemctl stop openvpn@{tunnel_name}-server'"
        subprocess.run(ssh_cmd, shell=True, check=True)

        prompt_user(
            icon_type="info", title="Success", text="Tunnel closed successfully."
        )
    except subprocess.CalledProcessError as e:
        prompt_user(
            icon_type="critical",
            title="Error",
            text=f"An error occurred while closing the tunnel. {e}",
        )


def delete_tunnel():
    selected_tunnel = dialog_select_tunnel("Select Tunnel to Delete")
    if not selected_tunnel:
        return

    tunnels = load_json(c.TUNNELS)
    server_ip = tunnels[selected_tunnel]["server_public_ip"]

    try:
        disconnect_vpn(selected_tunnel)
    except subprocess.CalledProcessError as e:
        prompt_user(
            icon_type="critical",
            title="Error",
            text=f"An error occurred while closing the tunnel. {e}",
        )
        return

    try:
        ssh_cmd = f"sshpass -p {c.PASS} ssh root@{server_ip} 'sudo rm -rf /etc/openvpn/{selected_tunnel}*'"
        subprocess.run(ssh_cmd, shell=True, check=True)

        local_client_conf_path = f"/etc/openvpn/{selected_tunnel}*"
        remove_client_conf_cmd = f"sudo rm -f {local_client_conf_path}"
        subprocess.run(remove_client_conf_cmd, shell=True, check=True)

        del tunnels[selected_tunnel]
        dump_json(tunnels, c.TUNNELS)

        tunnel_folder_path = os.path.join(c.TESTS, selected_tunnel)
        shutil.rmtree(tunnel_folder_path)
    except Exception as e:
        prompt_user(
            icon_type="critical",
            title="Error",
            text=f"Failed to delete the tunnel: {e}",
        )


def quit_application():
    active_tunnels = subprocess.run(["pgrep", "openvpn"], stdout=subprocess.PIPE)

    if active_tunnels.stdout:
        user_response = prompt_user(
            icon_type="question",
            title="Active Tunnels",
            text="Active OpenVPN tunnels found. Would you like to close them?",
            buttons=("Yes", "No"),
        )

        if user_response == "Yes":
            disconnect_vpn()

    QCoreApplication.quit()
