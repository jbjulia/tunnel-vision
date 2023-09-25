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
from src import prompt_user, rules


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
                return True
            else:
                prompt_user.message(
                    icon_type="warning",
                    title="Invalid Port",
                    text="Please enter a value in the unprivileged range (1024-49151).",
                )
                return False
        except ValueError:
            prompt_user.message(
                icon_type="warning",
                title="Invalid Port",
                text="Please enter a numerical value",
            )
            return False


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


def get_servers(server_name):
    servers = load_json(c.SERVERS)

    if server_name in servers:
        return servers[server_name]
    else:
        return None


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
        safe_directory = os.path.expanduser("~")
        os.chdir(safe_directory)

        for item, (local_path, destination) in local_paths.items():
            command = f"sshpass -p {c.PASS} scp {scp_flags} {ssh_flags} {'-r' if 'jail' in item else ''} {local_path} {tmp_path}"
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


def write_iptables_to_server(interface_name, port_number, protocol, server_ip):
    ssh_flags = "-o StrictHostKeyChecking=no"

    iptables_rules = rules.generate_iptables_rules(
        protocol, port_number, interface_name
    )

    ssh_cmd = f"""sshpass -p {c.PASS} ssh {ssh_flags} root@{server_ip} "echo '{iptables_rules}' > /etc/iptables/rules.v4" """

    try:
        subprocess.run(ssh_cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        prompt_user.message(
            title="Error",
            text=f"Error while writing iptables rules: {str(e)}",
            icon_type="critical",
        )
        return False


def connect_vpn(prompt=True):
    tunnels = load_json(c.TUNNELS)

    if not tunnels:
        prompt_user.message(
            icon_type="info",
            title="No Tunnels",
            text="No tunnels are currently configured.",
        )
        return False

    ssh_flags = "-o StrictHostKeyChecking=no"

    if prompt:
        confirmed = prompt_user.message(
            icon_type="question",
            title="Confirm Connection",
            text="Are you sure you want to connect?",
            buttons=["Yes", "No"],
        )

        if confirmed != "Yes":
            return False

    for tunnel_name, tunnel_info in tunnels.items():
        server_ip = tunnel_info["server_public_ip"]

        check_tunnel_status_cmd = (
            f"sudo systemctl is-active --quiet openvpn@{tunnel_name}-client"
        )
        tunnel_status = subprocess.run(
            check_tunnel_status_cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        if tunnel_status.returncode == 0:
            prompt_user.message(
                title="Already Connected",
                text="The VPN tunnel is already connected. Disconnecting to reconnect.",
                icon_type="warning",
            )
            disconnect_vpn(prompt=False)

        try:
            ssh_cmd = f"sshpass -p {c.PASS} ssh {ssh_flags} root@{server_ip} 'sudo systemctl start openvpn@{tunnel_name}-server'"
            subprocess.run(ssh_cmd, shell=True, check=True)

            local_client_conf_path = f"{c.TESTS}{tunnel_name}/{tunnel_name}-client.conf"
            destination_path = f"/etc/openvpn/{tunnel_name}-client.conf"
            copy_cmd = f"sudo cp {local_client_conf_path} {destination_path}"
            subprocess.run(copy_cmd, shell=True, check=True)

            client_cmd = f"sudo systemctl start openvpn@{tunnel_name}-client"
            subprocess.run(client_cmd, shell=True, check=True)

            if prompt:
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


def disconnect_vpn(prompt=True):
    tunnels = load_json(c.TUNNELS)

    if not tunnels:
        prompt_user.message(
            icon_type="info",
            title="No Tunnels",
            text="No tunnels are currently configured.",
        )
        return

    ssh_flags = "-o StrictHostKeyChecking=no"

    if prompt:
        confirmed = prompt_user.message(
            icon_type="question",
            title="Confirm Disconnection",
            text="Are you sure you want to disconnect?",
            buttons=["Yes", "No"],
        )

        if confirmed != "Yes":
            return

    for tunnel_name, tunnel_info in tunnels.items():
        server_ip = tunnel_info["server_public_ip"]

        try:
            client_cmd = f"sudo systemctl stop openvpn@{tunnel_name}-client"
            subprocess.run(client_cmd, shell=True, check=True)

            ssh_cmd = f"sshpass -p {c.PASS} ssh {ssh_flags} root@{server_ip} 'sudo systemctl stop openvpn@{tunnel_name}-server'"
            subprocess.run(ssh_cmd, shell=True, check=True)

            if prompt:
                prompt_user.message(
                    title="Success",
                    text="Successfully disconnected from the VPN.",
                    icon_type="info",
                )
        except Exception as e:
            prompt_user.message(
                title="Error",
                text=f"An error occurred while closing the tunnel. {e}",
                icon_type="critical",
            )


def delete_tunnel(prompt=True):
    tunnels = load_json(c.TUNNELS)

    if not tunnels:
        prompt_user.message(
            icon_type="info",
            title="No Tunnels",
            text="No tunnels are currently configured.",
        )
        return

    ssh_flags = "-o StrictHostKeyChecking=no"

    if prompt:
        confirmed = prompt_user.message(
            icon_type="question",
            title="Confirm Deletion",
            text="Are you sure you want to delete all tunnels?",
            buttons=["Yes", "No"],
        )

        if confirmed != "Yes":
            return

    tunnel_names_to_delete = []

    for tunnel_name, tunnel_info in tunnels.items():
        server_ip = tunnel_info["server_public_ip"]

        try:
            disconnect_vpn(prompt=False)
        except subprocess.CalledProcessError as e:
            prompt_user.message(
                icon_type="critical",
                title="Error",
                text=f"An error occurred while closing the tunnel. {e}",
            )

        try:
            ssh_cmd = f"sshpass -p {c.PASS} ssh {ssh_flags} root@{server_ip} 'sudo rm -rf /etc/openvpn/{tunnel_name}*'"
            subprocess.run(ssh_cmd, shell=True, check=True)

            local_client_conf_path = f"/etc/openvpn/{tunnel_name}*"
            remove_client_conf_cmd = f"sudo rm -f {local_client_conf_path}"
            subprocess.run(remove_client_conf_cmd, shell=True, check=True)

            tunnel_names_to_delete.append(tunnel_name)

            tunnel_folder_path = os.path.join(c.TESTS, tunnel_name)
            shutil.rmtree(tunnel_folder_path)

        except Exception as e:
            prompt_user.message(
                icon_type="critical",
                title="Error",
                text=f"Failed to delete a tunnel: {e}",
            )

    for tunnel_name in tunnel_names_to_delete:
        del tunnels[tunnel_name]

    dump_json(tunnels, c.TUNNELS)
