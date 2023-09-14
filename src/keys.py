import os
import subprocess

import pexpect

from resources import constants as c


def clone_easy_rsa(tunnel_name):
    """
    Clone the easy-rsa repository from GitHub.

    :param tunnel_name: Name of the tunnel
    :return: True if successful, False otherwise
    """
    print("Cloning the easy-rsa repository...")
    target_dir = f"{c.TESTS}{tunnel_name}/easy-rsa"

    try:
        subprocess.check_call(
            f"git clone https://github.com/OpenVPN/easy-rsa.git {target_dir}",
            shell=True,
        )
        print("Repository cloned successfully.")
    except subprocess.CalledProcessError:
        print(
            "Failed to clone the repository. Ensure git is installed and you have internet access."
        )
        return False

    return True


def init_pki(tunnel_name):
    """
    Initialize the PKI (Public Key Infrastructure).

    :param tunnel_name: Name of the tunnel
    :return: True if successful, False otherwise
    """
    target_dir = f"{c.TESTS}{tunnel_name}/easy-rsa/easyrsa3"

    try:
        os.chdir(target_dir)
    except OSError as e:
        print(f"Failed to change directory. Error: {e}")
        return False

    try:
        subprocess.run(["./easyrsa", "init-pki"], check=True)
        child = pexpect.spawn("./easyrsa build-ca nopass")
        child.expect("Common Name .*:")
        child.sendline(f"{tunnel_name}")
        child.expect(pexpect.EOF)
    except Exception as e:
        print(f"Failed to initialize PKI. Error: {e}")
        return False

    return True


def generate_certificates(tunnel_name):
    """
    Generate server and client certificates.

    :param tunnel_name: Name of the tunnel
    :return: True if successful, False otherwise
    """
    target_dir = f"{c.TESTS}{tunnel_name}/easy-rsa/easyrsa3"

    try:
        os.chdir(target_dir)
    except OSError as e:
        print(f"Failed to change directory. Error: {e}")
        return False

    try:
        server_child = pexpect.spawn(
            f"./easyrsa build-server-full {tunnel_name}-server nopass"
        )
        server_child.expect(r"Confirm request details[:]?")
        server_child.sendline("yes")
        server_child.expect(pexpect.EOF)

        client_child = pexpect.spawn(
            f"./easyrsa build-client-full {tunnel_name}-client nopass"
        )
        client_child.expect(r"Confirm request details[:]?")
        client_child.sendline("yes")
        client_child.expect(pexpect.EOF)
    except Exception as e:
        print(f"Failed to generate certificates. Error: {e}")
        return False

    return True


def generate_ta_key(tunnel_name):
    """
    Generate the ta.key (TLS Authentication Key).

    :param tunnel_name: Name of the tunnel
    :return: True if successful, False otherwise
    """
    print("Generating ta.key for TLS encryption...")
    target_dir = f"{c.TESTS}{tunnel_name}/easy-rsa/easyrsa3"

    try:
        os.chdir(target_dir)
    except OSError as e:
        print(f"Failed to change directory. Error: {e}")
        return False

    try:
        subprocess.run(["openvpn", "--genkey", "secret", "ta.key"], check=True)
        print("Key generated successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to generate ta.key. Error: {e}")
        return False

    return True
