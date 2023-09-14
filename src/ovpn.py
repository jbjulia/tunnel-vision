import os
import shutil
import sys

from resources import constants as c
from src import keys, functions as f


class OpenVPN:
    """
    The OpenVPN class facilitates the configuration, setup, and management of an OpenVPN tunnel.

    Upon instantiation, the class performs several tasks required to configure an OpenVPN tunnel:
    - Clears the console and checks for OpenVPN dependencies.
    - Prompts user for arguments such as connection type, tunnel name, IP addresses, interface name, and port number.
    - Generates certificates required for secure communication.
    - Generates server and client configuration files with appropriate settings.
    - Creates a jail directory to enhance security by restricting process access to resources.
    - Moves the configuration files to the top of the tunnel directory.
    - Removes the easy-rsa directory (no longer needed).
    - Saves the tunnel configuration to a JSON file.

    Attributes:
        tunnel_name (str): Name of the OpenVPN tunnel.
        connection_type (str): Type of connection, either 'p2p' (point-to-point) or 'subnet'.
        server_public_ip (str): Public IP address of the server.
        server_private_ip (str): Private IP address of the server.
        client_private_ip (str): Private IP address of the client.
        interface_name (str): Name of the network interface to be used.
        port_number (int): Port number for the connection (default is 1194, valid range 1024-49151).
    """

    def __init__(
        self,
        tunnel_name=None,
        connection_type=None,
        server_public_ip=None,
        server_private_ip=None,
        client_private_ip=None,
        interface_name=None,
        port_number=None,
    ):
        super(OpenVPN, self).__init__()

        self.tunnel_name = tunnel_name
        self.connection_type = connection_type
        self.server_public_ip = server_public_ip
        self.server_private_ip = server_private_ip
        self.client_private_ip = client_private_ip
        self.interface_name = interface_name
        self.port_number = port_number

        self.generate_certificates()
        self.generate_server_config()
        self.generate_client_config()
        self.build_jail()
        self.move_files()
        self.remove_directories()
        self.save_tunnel_config()

        print(
            f"\n{c.GREEN}SUCCESS! Your configuration files can be found in tests/{self.tunnel_name}{c.END}\n\n"
        )

    def generate_certificates(self):
        """
        Generates the necessary certificates for the OpenVPN connection.

        This method performs several actions to set up the certificates:
        - Creates a directory for the tunnel.
        - Clones Easy-RSA (a CLI utility for building and managing a PKI CA).
        - Initializes a new PKI and builds a CA.
        - Generates server and client certificates.
        - Generates a TLS Authentication key (ta.key).

        If all the operations are successful, a success message is printed.
        Otherwise, an error message is printed, and the program exits.
        """
        print("\nGenerating certificates...")

        f.make_directory(self.tunnel_name, chown=True)

        if (
            keys.clone_easy_rsa(self.tunnel_name)
            and keys.init_pki(self.tunnel_name)
            and keys.generate_certificates(self.tunnel_name)
            and keys.generate_ta_key(self.tunnel_name)
        ):
            print("Certificates generated successfully.")
        else:
            print("One or more operations failed.")
            sys.exit(1)

    def generate_server_config(self):
        """
        Generates the OpenVPN server configuration file.

        This method compiles a series of server directives that are essential
        for the OpenVPN server configuration. These directives include:
        - Logging configurations
        - Encryption and authentication settings
        - Network and connection settings
        - Security policies, such as chroot and user/group settings

        After compiling these directives, they are concatenated into a string
        and passed to a helper method to validate and update the server
        configuration file.
        """
        print("Generating server configuration...")

        server_directives = [
            f"log {self.tunnel_name}-server.log",
            "tls-server",
            f"dev-type tun",
            f"dev {self.interface_name}",
            f"topology {self.connection_type}",
            f"ifconfig {self.server_private_ip} {self.client_private_ip}",
            f"port {self.port_number}",
            "ncp-ciphers AES-128-GCM:AES-128-CBC",
            "cipher AES-128-GCM",
            "auth SHA256",
            "tls-cipher TLS-ECDHE-RSA-WITH-AES-256-GCM-SHA384",
            "dh none",
            f"verify-x509-name {self.tunnel_name}-client name",
            "remote-cert-tls client",
            "tls-version-min 1.3 or-highest",
            f"chroot {self.tunnel_name}-jail",
            "user nobody",
            "group nogroup",
            "persist-key",
            "persist-tun",
            "verb 4",
            "keepalive 10 60",
            "fast-io",
            'push "redirect-gateway def1"',
            'push "dhcp-option DNS 1.1.1.1"',
        ]

        server_directives = "\n".join(server_directives)

        # Validate and update the client configuration
        self.validate_and_update_configuration("server", server_directives)

    def generate_client_config(self):
        """
        Generates the OpenVPN client configuration file.

        This method compiles a series of client directives that are essential
        for the OpenVPN client configuration. These directives include:
        - Logging configurations
        - Client-specific settings such as "nobind"
        - Network and connection settings, including IPs and port
        - Encryption and authentication settings
        - Security policies, such as chroot and user/group settings

        After compiling these directives, they are concatenated into a string
        and passed to a helper method to validate and update the client
        configuration file.
        """
        print("Generating client configuration...")

        client_directives = [
            f"log {self.tunnel_name}-client.log",
            "client",
            "nobind",
            "dev-type tun",
            f"dev {self.interface_name}",
            f"topology {self.connection_type}",
            f"ifconfig {self.client_private_ip} {self.server_private_ip}",
            f"remote {self.server_public_ip}",
            f"port {self.port_number}",
            "cipher AES-128-GCM",
            "auth SHA256",
            f"verify-x509-name {self.tunnel_name}-server name",
            "remote-cert-tls server",
            "user nobody",
            "group nogroup",
            "persist-key",
            "persist-tun",
            "verb 4",
            "keepalive 10 60",
            "fast-io",
        ]

        client_directives = "\n".join(client_directives)

        # Validate and update the client configuration
        self.validate_and_update_configuration("client", client_directives)

    def validate_and_update_configuration(self, config_type, directives):
        """
        Validates and updates the OpenVPN configuration for the given type (server or client).

        The method performs the following actions:
        - Validates the existence of the configuration file and ta.key file.
        - Inserts the provided directives into the appropriate location within the configuration file.
        - Encloses the content of the ta.key file within <tls-crypt> tags and appends it to the configuration file.
        - Renames the configuration file extension to .conf.

        :param config_type: The type of configuration ("server" or "client").
        :param directives: The directives to be inserted into the configuration file.
        :raises FileNotFoundError: If the configuration file or the ta.key file does not exist.
        """

        print(f"Validating and updating {config_type} configuration...")

        base_path = f"{c.TESTS}{self.tunnel_name}/easy-rsa/easyrsa3/pki/inline/{self.tunnel_name}-{config_type}"
        conf_path = f"{base_path}.inline"
        ta_key_path = f"{c.TESTS}{self.tunnel_name}/easy-rsa/easyrsa3/ta.key"

        # Validate files' existence
        for file_path in [conf_path, ta_key_path]:
            if not os.path.isfile(file_path):
                raise FileNotFoundError(
                    f"The file '{file_path}' does not exist. Please ensure it has been created or generated."
                )

        with open(conf_path, "r") as original_file:
            contents = original_file.readlines()

        contents.insert(2, directives + "\n\n")

        with open(ta_key_path, "r") as ta_key_file:
            ta_key_content = f"<tls-crypt>\n{ta_key_file.read()}</tls-crypt>\n"
            contents.append(ta_key_content)

        with open(conf_path, "w") as modified_file:
            modified_file.writelines(contents)

        print(f"{config_type.capitalize()} configuration updated successfully.")
        print(f"Renaming {config_type} configuration file extension...")

        os.rename(conf_path, f"{base_path}.conf")

        print(f"{config_type.capitalize()} configuration file renamed successfully.")

    def build_jail(self):
        """
        Creates a jail directory for the OpenVPN server under the tunnel directory and sets the appropriate permissions.

        The method performs the following actions:
        - Creates a temporary jail directory structure with specific permissions under the tunnel directory.
        - Archives this directory into a tarball (compressed format).

        The creation of a jail directory helps in restricting the process to a specific set of resources, thereby
        enhancing the security.

        Note: The method relies on shell command execution and proper permissions are required.
        """
        print("Building jail for OpenVPN server...")

        tunnel_dir = f"{c.TESTS}{self.tunnel_name}"
        jail_dir = f"{tunnel_dir}/{self.tunnel_name}-jail/tmp"
        # target_tar = f"{tunnel_dir}/{self.tunnel_name}-jail.tar.gz"

        try:
            # Create the jail directory with tmp subdirectory and appropriate permissions
            os.makedirs(jail_dir, exist_ok=True)
            os.chmod(jail_dir, 0o1777)
            print("Jail for OpenVPN server built successfully.")
        except PermissionError:
            print(
                f"Failed to create jail for {self.tunnel_name}. Check if you have sufficient permissions."
            )
            return

        """
        print("Creating tarball...")

        # Archive the jail directory into a tarball
        with tarfile.open(target_tar, "w:gz") as tar:
            tar.add(jail_dir, arcname=os.path.basename(jail_dir))

        print(f"Tarball created successfully.")
        """

    def move_files(self):
        """
        Move the configuration files from the inline directory to the top of the tunnel directory.

        This function handles the following:
        - Defines the source directory containing the configuration files, which is inside the inline directory.
        - Defines the destination directory, which is the top of the tunnel name directory.
        - Checks the existence of the source directory and iterates through its contents.
        - Filters only the files with the ".conf" extension.
        - Attempts to move each file from the source to the destination directory.
        - Logs a success message for each successful move, and an error message if any move fails.

        :return: False if any move operation fails or the source directory does not exist, otherwise None.
        """
        print("Moving configuration files...")

        # Define the source directory (inside the inline directory)
        src_dir = os.path.join(
            c.TESTS, self.tunnel_name, "easy-rsa", "easyrsa3", "pki", "inline"
        )

        # Define the destination directory (top of the tunnel name directory)
        dest_dir = os.path.join(c.TESTS, self.tunnel_name)

        # Check if source directory exists
        if not os.path.exists(src_dir):
            print(f"Source directory {src_dir} does not exist.")
            return False

        # Iterate through the files in the source directory
        for file_name in os.listdir(src_dir):
            # Check if it's a conf file
            if file_name.endswith(".conf"):
                # Construct full file path
                src_file_path = os.path.join(src_dir, file_name)
                dest_file_path = os.path.join(dest_dir, file_name)

                # Move the file
                try:
                    shutil.move(src_file_path, dest_file_path)
                except shutil.Error as e:
                    print(f"Failed to move {file_name}. Error: {e}")
                    return False

        print("Configuration files moved successfully.")

    def remove_directories(self):
        """
        Removes the easy-rsa directory.

        This function performs the following actions:
        - Identifies the path to the easy-rsa directory under the tunnel directory.
        - Checks the existence of this directory and attempts to remove it using the `shutil.rmtree` method.
        - Logs a success message for successful removal and an error message if the removal fails.

        :return: False if the removal operation fails, otherwise None.
        """
        print("Removing the easy-rsa directory...")

        # Define the easy-rsa directory path
        easy_rsa_dir = os.path.join(c.TESTS, self.tunnel_name, "easy-rsa")

        # Attempt to remove the directory if it exists
        if os.path.exists(easy_rsa_dir):
            try:
                shutil.rmtree(easy_rsa_dir)
                print("easy-rsa directory removed successfully.")
            except shutil.Error as e:
                print(f"Failed to remove easy-rsa directory. Error: {e}")
                return False

    def save_tunnel_config(self):
        """
        Saves the configuration of the tunnel to a JSON file.

        This method is responsible for collecting the details of the OpenVPN tunnel,
        including the name, connection type, public and private IPs, interface name,
        and port number, and saving them to a JSON file. The keys in the JSON object
        are sorted, and the JSON data is indented for better readability.

        The following attributes are saved:
        - tunnel_name: The name of the tunnel.
        - connection_type: The type of connection established.
        - server_public_ip: The public IP address of the server.
        - server_private_ip: The private IP address of the server.
        - client_private_ip: The private IP address of the client.
        - interface_name: The name of the network interface used.
        - port_number: The port number used for the connection.
        """
        print("Saving tunnel configuration...")

        config = {
            self.tunnel_name: {
                "connection_type": self.connection_type,
                "server_public_ip": self.server_public_ip,
                "server_private_ip": self.server_private_ip,
                "client_private_ip": self.client_private_ip,
                "interface_name": self.interface_name,
                "port_number": self.port_number,
            }
        }

        f.dump_json(config, c.TUNNELS)

        print(f"Tunnel configuration saved successfully.")
