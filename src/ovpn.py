import os
import shutil

from resources import constants as c
from src import keys, prompt_user, directives as d, utils


class OpenVPN:
    def __init__(
        self,
        tunnel_name=None,
        connection_type=None,
        server_public_ip=None,
        server_private_ip=None,
        client_private_ip=None,
        interface_name=None,
        port_number=None,
        protocol=None,
    ):
        super(OpenVPN, self).__init__()

        self.tunnel_name = tunnel_name
        self.connection_type = connection_type
        self.server_public_ip = server_public_ip
        self.server_private_ip = server_private_ip
        self.client_private_ip = client_private_ip
        self.interface_name = interface_name
        self.port_number = port_number
        self.protocol = protocol
        self.successful_init = False

        if not self.generate_certificates():
            return
        if not self.generate_server_config():
            return
        if not self.generate_client_config():
            return
        if not self.build_jail():
            return
        if not self.move_files():
            return
        if not self.remove_directories():
            return
        if not self.save_tunnel_config():
            return

        self.successful_init = True

    def generate_certificates(self):
        try:
            os.makedirs(f"{c.TESTS}{self.tunnel_name}", exist_ok=True)
            os.chown(f"{c.TESTS}{self.tunnel_name}", os.getuid(), os.getgid())
            chown_success = True
        except PermissionError:
            prompt_user.message(
                icon_type="critical",
                title="Permission Error",
                text=f"Failed to set ownership for {self.tunnel_name}.\n\nCheck if you have sufficient permissions.",
            )
            chown_success = False

        if (
            chown_success
            and keys.clone_easy_rsa(self.tunnel_name)
            and keys.init_pki(self.tunnel_name)
            and keys.generate_certificates(self.tunnel_name)
            and keys.generate_ta_key(self.tunnel_name)
        ):
            return True
        else:
            prompt_user.message(
                icon_type="critical",
                title="Operation Failed",
                text="One or more operations failed.",
            )
            return False

    def generate_server_config(self):
        server_directives = d.build_server_directives(
            self.tunnel_name,
            self.interface_name,
            self.connection_type,
            self.server_private_ip,
            self.client_private_ip,
            self.port_number,
            self.protocol,
        )

        return self.validate_and_update_configuration("server", server_directives)

    def generate_client_config(self):
        client_directives = d.build_client_directives(
            self.tunnel_name,
            self.interface_name,
            self.connection_type,
            self.server_private_ip,
            self.client_private_ip,
            self.server_public_ip,
            self.port_number,
            self.protocol,
        )

        return self.validate_and_update_configuration("client", client_directives)

    def validate_and_update_configuration(self, config_type, directives):
        base_path = f"{c.TESTS}{self.tunnel_name}/easy-rsa/easyrsa3/pki/inline/{self.tunnel_name}-{config_type}"
        conf_path = f"{base_path}.inline"
        ta_key_path = f"{c.TESTS}{self.tunnel_name}/easy-rsa/easyrsa3/ta.key"

        for file_path in [conf_path, ta_key_path]:
            if not os.path.isfile(file_path):
                prompt_user.message(
                    icon_type="critical",
                    title="File Not Found",
                    text=f"The file '{file_path}' does not exist.\n\nPlease try again.",
                )
                return False

        with open(conf_path, "r") as original_file:
            contents = original_file.readlines()

        contents.insert(2, directives + "\n\n")

        with open(ta_key_path, "r") as ta_key_file:
            ta_key_content = f"<tls-crypt>\n{ta_key_file.read()}</tls-crypt>\n"
            contents.append(ta_key_content)

        with open(conf_path, "w") as modified_file:
            modified_file.writelines(contents)

        os.rename(conf_path, f"{base_path}.conf")

        return True

    def build_jail(self):
        tunnel_dir = f"{c.TESTS}{self.tunnel_name}"
        jail_dir = f"{tunnel_dir}/{self.tunnel_name}-jail/tmp"

        try:
            os.makedirs(jail_dir, exist_ok=True)
            os.chmod(jail_dir, 0o1777)
        except PermissionError:
            prompt_user.message(
                icon_type="critical",
                title="Permission Error",
                text=f"Failed to create jail for {self.tunnel_name}.\n\nCheck if you have sufficient permissions.",
            )
            return False

        return True

    def move_files(self):
        src_dir = os.path.join(
            c.TESTS, self.tunnel_name, "easy-rsa", "easyrsa3", "pki", "inline"
        )

        dest_dir = os.path.join(c.TESTS, self.tunnel_name)

        if not os.path.exists(src_dir):
            prompt_user.message(
                icon_type="critical",
                title="File Move Error",
                text=f"Source directory {src_dir} does not exist.",
            )
            return False

        for file_name in os.listdir(src_dir):
            if file_name.endswith(".conf"):
                src_file_path = os.path.join(src_dir, file_name)
                dest_file_path = os.path.join(dest_dir, file_name)

                try:
                    shutil.move(src_file_path, dest_file_path)
                except shutil.Error as e:
                    prompt_user.message(
                        icon_type="critical",
                        title="File Move Error",
                        text=f"Failed to move {file_name}. Error: {e}",
                    )
                    return False

        return True

    def remove_directories(self):
        easy_rsa_dir = os.path.join(c.TESTS, self.tunnel_name, "easy-rsa")

        if os.path.exists(easy_rsa_dir):
            try:
                shutil.rmtree(easy_rsa_dir)
            except shutil.Error as e:
                prompt_user.message(
                    icon_type="critical",
                    title="Directory Deletion Error",
                    text=f"Failed to remove easy-rsa directory. Error: {e}",
                )
                return False

        return True

    def save_tunnel_config(self):
        config = {
            self.tunnel_name: {
                "connection_type": self.connection_type,
                "server_public_ip": self.server_public_ip,
                "server_private_ip": self.server_private_ip,
                "client_private_ip": self.client_private_ip,
                "interface_name": self.interface_name,
                "port_number": self.port_number,
                "protocol": self.protocol,
            }
        }

        utils.dump_json(config, c.TUNNELS)

        return True
