import os
import subprocess

import pexpect

from resources import constants as c
from src import functions as f


def clone_easy_rsa(tunnel_name):
    target_dir = f"{c.TESTS}{tunnel_name}/easy-rsa"

    try:
        subprocess.check_call(
            f"git clone https://github.com/OpenVPN/easy-rsa.git {target_dir}",
            shell=True,
        )
    except subprocess.CalledProcessError as e:
        f.prompt_user(icon_type="critical", title="Operation Failed", text=str(e))
        return False

    return True


def init_pki(tunnel_name):
    target_dir = f"{c.TESTS}{tunnel_name}/easy-rsa/easyrsa3"

    try:
        os.chdir(target_dir)
    except OSError as e:
        f.prompt_user(icon_type="critical", title="Operation Failed", text=str(e))
        return False

    try:
        subprocess.run(["./easyrsa", "init-pki"], check=True)
        child = pexpect.spawn("./easyrsa build-ca nopass")
        child.expect("Common Name .*:")
        child.sendline(f"{tunnel_name}")
        child.expect(pexpect.EOF)
    except Exception as e:
        f.prompt_user(icon_type="critical", title="Operation Failed", text=str(e))
        return False

    return True


def generate_certificates(tunnel_name):
    target_dir = f"{c.TESTS}{tunnel_name}/easy-rsa/easyrsa3"

    try:
        os.chdir(target_dir)
    except OSError as e:
        f.prompt_user(icon_type="critical", title="Operation Failed", text=str(e))
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
        f.prompt_user(icon_type="critical", title="Operation Failed", text=str(e))
        return False

    return True


def generate_ta_key(tunnel_name):
    target_dir = f"{c.TESTS}{tunnel_name}/easy-rsa/easyrsa3"

    try:
        os.chdir(target_dir)
    except OSError as e:
        f.prompt_user(icon_type="critical", title="Operation Failed", text=str(e))
        return False

    try:
        subprocess.run(["openvpn", "--genkey", "secret", "ta.key"], check=True)
    except subprocess.CalledProcessError as e:
        f.prompt_user(icon_type="critical", title="Operation Failed", text=str(e))
        return False

    return True
