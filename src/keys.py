import os
import subprocess

from resources import constants as c


def clone_easy_rsa(tunnel_name):
    """
    Creates a directory and clones the easy-rsa repository into it.

    :param tunnel_name: Name of the tunnel.
    :return: True on success, False on failure.

    The method performs the following actions:
    - Clones the easy-rsa repository from GitHub into a directory named according to the tunnel.
    - Ensures that Git is available and the internet connection is active.

    Note: The method relies on Git command-line tool execution.
    """
    print(f"Cloning the easy-rsa repository...")

    target_dir = f"{c.TESTS}{tunnel_name}/easy-rsa"

    try:
        subprocess.check_call(
            f"git clone https://github.com/OpenVPN/easy-rsa.git {target_dir}",
            shell=True,
        )
        print("Repository cloned successfully.")
    except subprocess.CalledProcessError:
        print(
            "Failed to clone the repository. Check if git is installed or if you have an internet connection."
        )
        return False

    return True


def init_pki(tunnel_name):
    """
    Initializes the Public Key Infrastructure (PKI) for the specified tunnel name.

    :param tunnel_name: Name of the tunnel.
    :return: True on success, False on failure.

    The method performs the following actions:
    - Changes the working directory to the easy-rsa directory.
    - Initializes the PKI by running the appropriate easy-rsa scripts.
    - Builds the certificate authority without a password.

    Exceptions handled:
    - OSError: In case of failure to change the working directory.
    - CalledProcessError: In case of failure in running the easy-rsa scripts.
    """
    print(f"Initializing PKI...")

    target_dir = f"{c.TESTS}{tunnel_name}/easy-rsa/easyrsa3"

    try:
        os.chdir(target_dir)
    except OSError as e:
        print(f"Failed to change directory. Error: {e}")
        return False

    try:
        # Build the certificate authority
        subprocess.run(["./easyrsa", "init-pki"], check=True)
        subprocess.run(["./easyrsa", "build-ca", "nopass"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to initialize PKI. Error: {e}")
        return False

    return True


def generate_certificates(tunnel_name):
    """
    Generates server and client certificates for the specified tunnel name.

    :param tunnel_name: Name of the tunnel.
    :return: True on success, False on failure.

    The method performs the following actions:
    - Changes the working directory to the easy-rsa directory.
    - Generates server and client certificates using the easy-rsa scripts without a password.

    Optional:
    - Uncomment the section to generate the Diffie-Hellman key exchange if needed.

    Exceptions handled:
    - OSError: In case of failure to change the working directory.
    - CalledProcessError: In case of failure in running the easy-rsa scripts.
    """
    print(f"Generating certificates for server and client...")

    target_dir = f"{c.TESTS}{tunnel_name}/easy-rsa/easyrsa3"

    try:
        os.chdir(target_dir)
    except OSError as e:
        print(f"Failed to change directory. Error: {e}")
        return False

    try:
        subprocess.run(
            ["./easyrsa", "build-server-full", tunnel_name + "-server", "nopass"],
            check=True,
        )
        subprocess.run(
            ["./easyrsa", "build-client-full", tunnel_name + "-client", "nopass"],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Failed to generate certificates. Error: {e}")
        return False

    # Uncomment below if you want to generate the Diffie-Hellman key exchange
    """
    try:
        subprocess.run(["./easyrsa", "gen-dh"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to generate Diffie-Hellman key exchange. Error: {e}")
        return False
    """

    return True


def generate_ta_key(tunnel_name):
    """
    Generates the ta.key (TLS Authentication Key) for the specified tunnel name.

    :param tunnel_name: Name of the tunnel.
    :return: True on success, False on failure.

    The method performs the following actions:
    - Changes the working directory to the easy-rsa directory.
    - Executes the OpenVPN command to generate the ta.key, which is used for
      additional security in TLS encryption.

    Exceptions handled:
    - OSError: In case of failure to change the working directory.
    - CalledProcessError: In case of failure to run the OpenVPN command.
    """
    print(f"Generating ta.key for TLS encryption...")

    target_dir = f"{c.TESTS}{tunnel_name}/easy-rsa/easyrsa3"

    try:
        os.chdir(target_dir)
    except OSError as e:
        print(f"Failed to change directory. Error: {e}")
        return False

    try:
        # Generate ta.key for TLS encryption
        subprocess.run(["openvpn", "--genkey", "secret", "ta.key"], check=True)
        print("Key generated successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to generate ta.key. Error: {e}")
        return False

    return True
