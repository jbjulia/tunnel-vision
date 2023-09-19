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

from resources import constants as c
from src import prompt_user


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
            prompt_user.message(
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
                prompt_user.message(
                    icon_type="warning",
                    title="Invalid Port",
                    text="Please enter a value in the unprivileged range (1024-49151).",
                )
        except ValueError:
            prompt_user.message(
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
        prompt_user.message(
            title="Error",
            text="There was an address related error.",
            icon_type="critical",
        )
        private_ip = "127.0.0.1"
    except socket.timeout:
        prompt_user.message(
            title="Error",
            text="Connection timed out.",
            icon_type="critical",
        )
        private_ip = "127.0.0.1"
    except OSError:
        prompt_user.message(
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


def find_active_tunnels():
    active_tunnels = subprocess.run(["pgrep", "openvpn"], stdout=subprocess.PIPE)

    if active_tunnels.stdout:
        return True
    else:
        return False


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

        return True

    except subprocess.CalledProcessError as e:
        prompt_user.message(
            title="Error",
            text=f"The following error occurred when copying files to the server:\n\n{e}",
            icon_type="critical",
        )

        return False


def connect_vpn(server_ip=None, tunnel_name=None):
    def execute_connection():
        try:
            ssh_cmd = f"sshpass -p {c.PASS} ssh root@{server_ip} 'sudo systemctl start openvpn@{tunnel_name}-server'"
            subprocess.run(ssh_cmd, shell=True, check=True)

            local_client_conf_path = f"{c.TESTS}{tunnel_name}/{tunnel_name}-client.conf"
            destination_path = f"/etc/openvpn/{tunnel_name}-client.conf"
            copy_cmd = f"sudo cp {local_client_conf_path} {destination_path}"
            subprocess.run(copy_cmd, shell=True, check=True)

            client_cmd = f"sudo systemctl start openvpn@{tunnel_name}-client"
            subprocess.run(client_cmd, shell=True, check=True)

            prompt_user.message(
                title="Success",
                text="Successfully connected to the VPN.",
                icon_type="info",
            )
            return True

        except Exception as e:
            prompt_user.message(
                title="Error",
                text=f"Error while connecting to VPN: {str(e)}",
                icon_type="critical",
            )
            return False

    if not (server_ip and tunnel_name):
        selected_tunnel = prompt_user.dialog("Select Tunnel to Connect")

        if selected_tunnel:
            tunnels = load_json(c.TUNNELS)
            server_ip = tunnels[selected_tunnel]["server_public_ip"]
            tunnel_name = selected_tunnel

    if server_ip and tunnel_name:
        return execute_connection()
    else:
        return False


def disconnect_vpn(tunnel_name=None):
    if not tunnel_name:
        tunnel_name = prompt_user.dialog("Select Tunnel to Disconnect")
        if not tunnel_name:
            return

    # Load tunnel information
    tunnels = load_json(c.TUNNELS)
    if tunnel_name in tunnels:
        server_ip = tunnels[tunnel_name]["server_public_ip"]
    else:
        prompt_user.message(
            icon_type="critical", title="Error", text="Tunnel not found."
        )
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

        prompt_user.message(
            icon_type="info", title="Success", text="Tunnel closed successfully."
        )
    except subprocess.CalledProcessError as e:
        prompt_user.message(
            icon_type="critical",
            title="Error",
            text=f"An error occurred while closing the tunnel. {e}",
        )


def delete_tunnel():
    selected_tunnel = prompt_user.dialog("Select Tunnel to Delete")
    if not selected_tunnel:
        return

    tunnels = load_json(c.TUNNELS)
    server_ip = tunnels[selected_tunnel]["server_public_ip"]

    try:
        disconnect_vpn(selected_tunnel)
    except subprocess.CalledProcessError as e:
        prompt_user.message(
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
        prompt_user.message(
            icon_type="critical",
            title="Error",
            text=f"Failed to delete the tunnel: {e}",
        )
