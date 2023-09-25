def build_server_directives(
    tunnel_name,
    interface_name,
    connection_type,
    server_private_ip,
    client_private_ip,
    port_number,
    protocol,
):
    """
    Generate OpenVPN server configuration directives.

    Parameters:
        tunnel_name (str): Name of the tunnel.
        interface_name (str): Name of the network interface.
        connection_type (str): Type of network topology.
        server_private_ip (str): Private IP address of the server.
        client_private_ip (str): Private IP address of the client.
        port_number (int): Port to be used for the connection.
        protocol (str): Protocol to be used for the connection.

    Returns:
        str: OpenVPN server configuration directives as a single string.

    The function compiles various server directives such as logging configurations,
    encryption settings, network configurations, and security policies. It then
    joins these directives into a single string for easier handling and returns it.
    """
    server_directives = [
        f"log {tunnel_name}-server.log",
        "tls-server",
        f"dev-type tun",
        f"dev {interface_name}",
        f"topology {connection_type}",
        f"ifconfig {server_private_ip} {client_private_ip}",
        f"port {port_number}",
        f"proto {protocol}",
        "ncp-ciphers AES-128-GCM:AES-128-CBC",
        "cipher AES-128-GCM",
        "auth SHA256",
        "tls-cipher TLS-ECDHE-RSA-WITH-AES-256-GCM-SHA384",
        "dh none",
        f"verify-x509-name {tunnel_name}-client name",
        "remote-cert-tls client",
        "tls-version-min 1.3 or-highest",
        f"chroot {tunnel_name}-jail",
        "user nobody",
        "group nogroup",
        "persist-key",
        "persist-tun",
        "verb 4",
        "keepalive 10 60",
        "fast-io",
        'push "redirect-gateway def1"',
        'push "dhcp-option DNS 1.1.1.1"',
        'push "dhcp-option DNS 8.8.8.8"',
    ]

    return "\n".join(server_directives)


def build_client_directives(
    tunnel_name,
    interface_name,
    connection_type,
    server_private_ip,
    client_private_ip,
    server_public_ip,
    port_number,
    protocol,
):
    """
    Generate OpenVPN client configuration directives.

    Parameters:
        tunnel_name (str): Name of the tunnel.
        interface_name (str): Name of the network interface.
        connection_type (str): Type of network topology.
        server_private_ip (str): Private IP address of the server.
        client_private_ip (str): Private IP address of the client.
        server_public_ip (str): Public IP address of the server.
        port_number (int): Port to be used for the connection.
        protocol (str): Protocol to be used for the connection.

    Returns:
        str: OpenVPN client configuration directives as a single string.

    This function compiles client directives essential for setting up the OpenVPN
    client. This includes settings like logging configurations, encryption parameters,
    and network settings. These directives are then joined into a single string and returned.
    """
    client_directives = [
        f"log {tunnel_name}-client.log",
        "client",
        "nobind",
        "pull",
        "dev-type tun",
        f"dev {interface_name}",
        f"topology {connection_type}",
        f"ifconfig {client_private_ip} {server_private_ip}",
        f"remote {server_public_ip}",
        f"port {port_number}",
        f"proto {protocol}",
        "redirect-gateway def1",
        "cipher AES-128-GCM",
        "auth SHA256",
        f"verify-x509-name {tunnel_name}-server name",
        "remote-cert-tls server",
        "user nobody",
        "group nogroup",
        "persist-key",
        "persist-tun",
        "verb 4",
        "keepalive 10 60",
        "fast-io",
        "up /etc/openvpn/update-resolv-conf",
        "down /etc/openvpn/update-resolv-conf",
    ]

    return "\n".join(client_directives)
