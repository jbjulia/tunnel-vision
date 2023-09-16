def generate_iptables_rules(tunnel_name, interface_name="eth0"):
    """
    Generate and save iptables rules to a rules.v4 file for a given OpenVPN tunnel.

    Parameters:
        tunnel_name (str): Name of the OpenVPN tunnel.
        interface_name (str, optional): Name of the network interface (default is 'eth0').

    This function:
    1. Creates a list of iptables rules necessary for the OpenVPN tunnel to operate.
    2. Includes generic iptables settings for incoming, outgoing, and forwarded traffic.
    3. Appends tunnel-specific iptables rules.
    4. Saves the complete list of rules to a `rules.v4` file inside the `tests/{tunnel_name}` directory.
    """
    # Generic rules for traffic management
    generic_rules = [
        "sudo iptables -A INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT",
        "sudo iptables -A INPUT -m conntrack --ctstate INVALID -j DROP",
        "sudo iptables -A INPUT -i lo -j ACCEPT",
        "sudo iptables -A INPUT -p icmp -j ACCEPT",
        "sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT",  # Allow SSH
        "sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT",  # Allow HTTP
        "sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT",  # Allow HTTPS
        "sudo iptables -A OUTPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT",
        "sudo iptables -A OUTPUT -m conntrack --ctstate INVALID -j DROP",
        "sudo iptables -A OUTPUT -o lo -j ACCEPT",
        "sudo iptables -A OUTPUT -p icmp -j ACCEPT",
        "sudo iptables -A FORWARD -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT",
        "sudo iptables -A FORWARD -m conntrack --ctstate INVALID -j DROP",
    ]

    # Tunnel-specific rules
    tunnel_rules = [
        f"sudo iptables -t nat -A POSTROUTING -o {interface_name} -j MASQUERADE",
        f"sudo iptables -A FORWARD -i {tunnel_name} -o {interface_name} -j ACCEPT",
        f"sudo iptables -A FORWARD -i {interface_name} -o {tunnel_name} -j ACCEPT",
    ]

    # Combine generic and tunnel-specific rules
    iptables_rules = generic_rules + tunnel_rules

    return iptables_rules
