import getpass
import ipaddress
import json
import os
import socket
import subprocess
import sys

from resources import constants as c
from src.ovpn import OpenVPN


def check_os():
    """
    This function checks if the OS is Linux.

    :return: True if the OS is Linux, False otherwise.
    """
    if sys.platform != "linux":
        print(
            "This script must be run on a Linux-based system (e.g., Ubuntu, Pop!_OS, etc.)."
        )
        return False
    return True


def check_privileges():
    """
    This function checks if the script is run with superuser privileges.

    :return: True if the script is run with superuser privileges, False otherwise.
    """
    if os.geteuid() != 0:
        print("This script requires elevated privileges. Please run with sudo.")
        return False
    return True


def clear_console():
    """
    This function clears the console.
    """
    os.system("clear")


def display_menu():
    """
    Displays the main menu for the Guardians of the Gateway - Tunnel Vision application and handles user input.

    This function performs the following actions:
    - Clears the console for fresh display.
    - Defines the menu items for building, copying, connecting, and disconnecting VPN tunnels, and quitting the program.
    - Prints the menu items to the console in a formatted manner.
    - Prompts the user to select an option by entering a corresponding number.
    - Calls the appropriate function based on the user's choice, or prints an error message for an invalid selection.
    """
    clear_console()

    menu = {
        "1": "Build OpenVPN tunnel",
        "2": "Copy files to server",
        "3": "Connect VPN",
        "4": "Disconnect VPN",
        "5": "Delete a tunnel",
        "6": "Quit",
    }

    print("========================================")
    print("Guardians of the Gateway - Tunnel Vision")
    print("========================================\n")

    for key, value in menu.items():
        print(f"{key}: {value}")

    choice = input("\nPlease select an option: ")

    if choice == "1":
        OpenVPN()
    elif choice == "2":
        copy_to_server()
    elif choice == "3":
        connect_vpn()
    elif choice == "4":
        disconnect_vpn()
    elif choice == "5":
        delete_tunnel()
    elif choice == "6":
        quit_program()
    else:
        print("Invalid choice. Please try again.")


def check_dependencies(package_name):
    """
    This function checks for the package and installs if necessary.

    :param package_name: The name of the package to be installed.
    :return: True if successful, False otherwise.
    """
    print(f"Checking for {package_name}...")

    # Check if the package is already installed
    result = subprocess.run(
        ["dpkg", "-l", package_name],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if result.returncode == 0:
        print(f"Package '{package_name}' is already installed.\n")
        return True

    print(f"Installing package '{package_name}'...")

    try:
        subprocess.run(
            f"apt install {package_name} -y",
            shell=True,
            check=True,
        )
        print(f"Package '{package_name}' installed successfully.\n")
        return True
    except subprocess.CalledProcessError:
        print(
            f"Failed to install package '{package_name}'. Check if you have sufficient permissions."
        )
        return False


def make_directory(dir_name, chown=False, chmod=False, sticky_bit=False):
    """
    Creates a directory with specified characteristics and applies optional permissions changes.

    This function performs the following actions:
    - Creates the directory, including any necessary parent directories, with the given name.
    - If the 'chown' is True, changes ownership of the directory to the current user.
    - If the 'chmod' is True, changes the permissions of the directory, optionally setting the sticky bit if requested.
    - Prints success messages for each successful operation, or an error message if something goes wrong.

    :param dir_name: The name of the directory to be created. Path relative to a predefined constant `c.TESTS`.
    :param chown: Optional; Whether to change ownership to the current user. Defaults to False.
    :param chmod: Optional; Whether to change permissions to 777. Defaults to False.
    :param sticky_bit: Optional; Whether to set the sticky bit along with the chmod operation. Defaults to False.
    :return: True if directory creation and any requested changes were successful, or an error message if else.
    """
    try:
        subprocess.run(
            f"mkdir -p {c.TESTS}{dir_name} && chown {os.getlogin()}:{os.getlogin()} {c.TESTS}{dir_name} -R",
            shell=True,
            check=True,
        )
        print(f"Directory '{dir_name}' created successfully.")
        if chown:
            current_user = getpass.getuser()
            subprocess.check_call(
                f"chown {current_user}:{current_user} {c.TESTS}* -R", shell=True
            )
            print(f"Ownership of '{dir_name}' changed successfully.")
        if chmod:
            subprocess.run(
                f"chmod {'1' if sticky_bit else ''}777 {c.TESTS + dir_name}",
                shell=True,
                check=True,
            )
            print(f"Permissions of {dir_name} changed successfully.")
        return True
    except subprocess.CalledProcessError:
        print(f"Failed to create {dir_name}. Check if you have sufficient permissions.")


def validate_ip(prompt):
    """
    Prompt the user for a valid IP address and return it.
    Repeats the prompt until a valid IP address is entered.

    :param prompt: The prompt message to display to the user.
    :return: A valid IP address as a string.
    """
    while True:
        ip = input(prompt)

        if not ip:
            return get_private_ip()

        try:
            return str(ipaddress.ip_address(ip))
        except ValueError:
            print("Invalid IP address. Please enter a valid IP.")


def validate_port(prompt):
    """
    Prompt the user for a valid port number and return it. The valid port range is 1024-49151.
    If the user presses Enter without entering anything, the default port 1194 is returned.

    :param prompt: The prompt message to display to the user.
    :return: A valid port number.
    """
    while True:
        port = input(prompt)

        # If the user presses Enter without entering anything, use the default port
        if not port:
            return 1194

        try:
            port = int(port)

            # Check if the port is in the valid unprivileged range
            if 1024 <= port <= 49151:
                return port
            else:
                print(
                    "Invalid port number. Please enter a value in the unprivileged range (1024-49151)."
                )

        except ValueError:
            print("Invalid port number. Please enter a numerical value.")


def get_private_ip():
    """
    Retrieves the private IP address of the host machine.

    This function performs the following actions:
    - Creates a UDP socket and attempts to connect to an arbitrary IP address (10.255.255.255).
    - Uses the `getsockname` method to fetch the local endpoint address, i.e., the private IP.
    - If any exception occurs, it defaults the private IP to '127.0.0.1'.
    - Closes the socket.
    - Prints the private IP address.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        # Doesn't matter if the destination is unreachable
        s.connect(("10.255.255.255", 1))
        private_ip = s.getsockname()[0]
    except socket.gaierror:
        print("Address-related error")
        private_ip = "127.0.0.1"
    except socket.timeout:
        print("Connection timed out")
        private_ip = "127.0.0.1"
    except OSError:
        print(
            "OS error, possibly related to permissions or other system-related issues"
        )
        private_ip = "127.0.0.1"
    finally:
        s.close()

    return private_ip


def get_servers():
    """
    Retrieves and displays the list of available servers from the servers.json file,
    then prompts the user to select a server by its number.

    This function performs the following actions:
    - Reads the server information from the servers.json file.
    - Enumerates the available servers and prints them to the console with coloring for enhanced visibility.
    - Prompts the user to select a server by entering its number.
    - Returns the details of the selected server as a dictionary.

    :return servers[server_list[choice]]: A dictionary containing the private and public IP addresses of the server.
    """
    # Read server information from servers.json
    servers = load_json(c.SERVERS)

    # Display available servers
    server_list = list(servers.keys())
    print(f"\n{c.BOLD + c.UNDERLINE}Available servers:{c.END}\n")
    for idx, server in enumerate(server_list, start=1):
        print(f"  {c.BOLD}{idx}.  {c.GREEN}{server}{c.END}")

    # Get user's server choice
    choice = (
        int(input(f"\n{c.BLUE}Select a server by entering its number:{c.END} ")) - 1
    )

    return servers[server_list[choice]]


def load_json(json_file):
    """
    Loads data from a specified JSON file.

    This function reads the specified JSON file and returns the data as a dictionary.
    It can be used to load various data structures, including tunnel configurations or other structured information.

    :param json_file: The path to the JSON file to be read.
    :return: The dictionary containing the data from the JSON file. If the file is not found or is incorrectly
    formatted, an error may be raised.
    """
    with open(json_file) as in_file:
        data = json.load(in_file)

    return data


def dump_json(data, json_file):
    """
    Dumps the specified data to a JSON file.

    This function takes a dictionary containing the data and writes it to the specified JSON file.
    The keys of the JSON object are sorted alphabetically, and the resulting JSON is indented for better readability.

    :param data: The dictionary containing the data to be dumped.

    :param json_file: The path to the JSON file where the data will be written. If the file exists, it will be
    overwritten; otherwise, a new file will be created.
    """
    with open(json_file, "w") as out_file:
        json.dump(data, out_file, indent=4, sort_keys=True)


def copy_to_server():
    """
    Copies the OpenVPN server configuration file and jail directory to the server.

    This function performs the following actions:
    - Reads the servers.json file to obtain the available servers and asks the user to select one.
    - Matches the selected server IP with the corresponding tunnel name in tunnels.json.
    - Defines local paths for the server configuration file and jail directory.
    - Defines temporary and final remote paths on the server.
    - Uses `sshpass` with `scp` and specific flags to copy the server configuration file and jail directory to the
      temporary remote path.
    - Uses `sshpass` with `ssh` to move the server configuration file and jail directory from the temporary remote path
      to the final remote path, removing any conflicting files or directories if they exist.
    - Prints a success message upon completion, or an error message if something goes wrong.

    The SSH flags used are:
    - `-o StrictHostKeyChecking=no`: Disables strict host key checking.

    The SCP flags used are:
    - `-P 22`: Specifies the port number (for SCP the flag is uppercase).
    - `-C`: Requests compression of all data.
    - `-v`: Verbose mode to show debugging messages.

    Note: This function requires the 'sshpass' utility to be installed on the system.
    """
    # Display available servers and ask user to select one
    server_ip = get_servers()["public_ip"]

    # Read tunnels.json to find the corresponding tunnel name
    tunnels = load_json(c.TUNNELS)

    tunnel_name = next(
        tunnel_name
        for tunnel_name, tunnel_data in tunnels.items()
        if tunnel_data["server_public_ip"] == server_ip
    )

    local_server_conf_path = f"{c.TESTS}{tunnel_name}/{tunnel_name}-server.conf"
    local_jail_path = f"{c.TESTS}{tunnel_name}/{tunnel_name}-jail"

    # Temporary remote path
    tmp_path = f"root@{server_ip}:/tmp/"

    # Final destination path
    destination = f"/etc/openvpn/"

    # SCP flags
    scp_flags = "-P 22 -C"  # -v

    # SSH flags
    ssh_flags = "-o StrictHostKeyChecking=no"

    # Define local paths
    local_paths = {"server.conf": local_server_conf_path, "jail": local_jail_path}

    print("\nCopying files to server...")

    try:
        # Copy and move files
        for item, local_path in local_paths.items():
            # Copy file to temporary remote path
            command = f"sshpass -p {c.PASS} scp {scp_flags} {'-r' if item == 'jail' else ''} {local_path} {tmp_path}"
            subprocess.check_call(command, shell=True)

            # Remove conflicting directory or file if it exists, then move the new one
            command = (
                f"sshpass -p '{c.PASS}' ssh {ssh_flags} root@{server_ip} "
                f"'rm -rf {destination}{tunnel_name}-{item} && "
                f"mv /tmp/{tunnel_name}-{item} {destination}'"
            )
            subprocess.check_call(command, shell=True)

        print("Configuration file and jail directory copied successfully.")

    except subprocess.CalledProcessError as e:
        print(f"An error occurred while copying the files. {e}")


def connect_vpn():
    """
    Establishes an OpenVPN connection by first starting the server-side tunnel, then the client-side tunnel.

    This function performs the following actions:
    - Prints the available server IPs using 'get_servers()["public_ip"]'.
    - Prompts the user to select the desired server for connection.
    - Initiates an SSH connection to the selected server using sshpass, with the password defined in the script.
    - Looks for the server-side configuration file in /etc/openvpn and starts the OpenVPN tunnel on the server
      using 'systemctl start openvpn@{tunnel_name}'.
    - Copies the client-side configuration file to /etc/openvpn/ and starts the client-side tunnel.
    - Prints status messages to inform the user of the progress of the connection process.
    """
    # Retrieve available servers
    server_ip = get_servers()["public_ip"]

    # Read tunnels.json to find the corresponding tunnel name
    tunnels = load_json(c.TUNNELS)

    tunnel_name = next(
        tunnel_name
        for tunnel_name, tunnel_data in tunnels.items()
        if tunnel_data["server_public_ip"] == server_ip
    )

    # Connect to the selected server and start the OpenVPN tunnel
    print(f"Connecting to server {server_ip}...")
    ssh_cmd = f"sshpass -p {c.PASS} ssh root@{server_ip} 'sudo systemctl start openvpn@{tunnel_name}-server'"
    subprocess.run(ssh_cmd, shell=True)
    print("Server-side tunnel started.")

    # Copy client-side OpenVPN configuration file to /etc/openvpn/
    local_client_conf_path = f"{c.TESTS}{tunnel_name}/{tunnel_name}-client.conf"
    destination_path = f"/etc/openvpn/{tunnel_name}-client.conf"
    copy_cmd = f"sudo cp {local_client_conf_path} {destination_path}"
    subprocess.run(copy_cmd, shell=True)

    # Start the client-side OpenVPN tunnel
    client_cmd = f"sudo systemctl start openvpn@{tunnel_name}-client"
    subprocess.run(client_cmd, shell=True)
    print("Client-side tunnel started.")


def disconnect_vpn():
    """
    Disconnects any active OpenVPN tunnels and exits the program.

    This function performs the following actions:
    - Utilizes the 'pgrep' command to search for any active OpenVPN processes.
    - If active tunnels are detected, it attempts to terminate them using the 'pkill' command.
    - If the termination is successful, a success message is printed to the console.
    - If the termination fails (e.g., due to permissions or other issues), a failure message is printed, instructing the
      user to manually close the tunnels via their console.
    - If no active tunnels are found, an informational message is printed to the console.
    """
    # Find any active OpenVPN processes
    active_tunnels = subprocess.run(["pgrep", "openvpn"], stdout=subprocess.PIPE)

    # If active tunnels are found, attempt to terminate them
    if active_tunnels.stdout:
        try:
            subprocess.run(["pkill", "openvpn"], check=True)
            print("Active tunnels closed.")
        except subprocess.CalledProcessError:
            print(
                "Failed to close active tunnels. Please manually close them via your console."
            )
    else:
        print("No active tunnels found.")


def delete_tunnel():
    """
    Deletes a specified tunnel.

    This function performs the following actions:
    - Reads the tunnels.json file to display available tunnels.
    - Asks the user to type the name of the tunnel to delete.
    - Attempts to close the specified tunnel.
    - Removes the tunnel from the tunnels.json file.
    - Removes the corresponding configuration and log files from the /etc/openvpn directory.

    The tunnel naming convention is: tunnel_name-client.conf, and tunnel_name-client.log.

    Note: Proper permissions may be required to perform some of these operations.
    """
    # Load the tunnels
    tunnels = load_json(c.TUNNELS)

    # Display available tunnels
    print(f"\n{c.BOLD + c.UNDERLINE}Available tunnels:{c.END}\n")
    for tunnel_name in tunnels:
        print(f"  {c.GREEN}{tunnel_name}{c.END}")

    # Ask the user to type the tunnel name
    selected_tunnel = input(
        f"\n{c.BLUE}Please type the name of the tunnel you want to delete:{c.END} "
    )

    if selected_tunnel not in tunnels:
        print("Tunnel not found.")
        return

    # Attempt to close the tunnel
    try:
        command = f"openvpn --rmtun --dev-type tun --dev {selected_tunnel}"
        subprocess.check_call(command, shell=True)
        print(f"Tunnel '{selected_tunnel}' closed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while closing the tunnel. {e}")

    # Remove from tunnels.json
    del tunnels[selected_tunnel]
    dump_json(tunnels, c.TUNNELS)

    # Remove the corresponding configuration and log files
    config_path = f"/etc/openvpn/{selected_tunnel}-client.conf"
    log_path = f"/etc/openvpn/{selected_tunnel}-client.log"

    try:
        os.remove(config_path)
        os.remove(log_path)
        print(
            f"Configuration and log files for '{selected_tunnel}' removed successfully."
        )
    except FileNotFoundError as e:
        print(f"An error occurred while removing the files. {e}")

    print(f"Tunnel '{selected_tunnel}' deleted successfully.")


def quit_program():
    """
    Checks for any active OpenVPN tunnels, prompts the user for whether to disconnect them, and then exits the program.

    This function performs the following actions:
    - Utilizes the 'pgrep' command to search for any active OpenVPN processes.
    - If active tunnels are detected, prompts the user with an option to disconnect them.
    - If the user chooses to disconnect, calls the `disconnect_vpn` function to handle the disconnection process.
    - If the user chooses not to disconnect, active tunnels are left open.
    - If no active tunnels are found, prints an informational message to the console.
    - Exits the program with a farewell message.
    """
    # Check for active OpenVPN tunnels
    active_tunnels = subprocess.run(["pgrep", "openvpn"], stdout=subprocess.PIPE)

    # If active tunnels are found, prompt the user to close them
    if active_tunnels.stdout:
        user_response = (
            input(
                "Active OpenVPN tunnels found. Would you like to close them? (yes/no): "
            )
            .strip()
            .lower()
        )

        if user_response == "yes":
            disconnect_vpn()
        else:
            print("Leaving active tunnels open.")
    else:
        print("No active tunnels found.")

    print("Goodbye.")
    sys.exit()
