def generate_iptables_rules(protocol, port, interface_name):
    filter_rules = [
        ":INPUT ACCEPT [0:0]",
        ":FORWARD ACCEPT [0:0]",
        ":OUTPUT ACCEPT [0:0]",
        "-A INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT",
        "-A INPUT -m conntrack --ctstate INVALID -j DROP",
        "-A INPUT -i lo -j ACCEPT",
        "-A INPUT -p icmp -j ACCEPT",
        "-A INPUT -p tcp --dport 22 -j ACCEPT",
        "-A OUTPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT",
        "-A OUTPUT -m conntrack --ctstate INVALID -j DROP",
        "-A OUTPUT -o lo -j ACCEPT",
        "-A OUTPUT -p icmp -j ACCEPT",
        "-A FORWARD -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT",
        "-A FORWARD -m conntrack --ctstate INVALID -j DROP",
        f"-A INPUT -p {protocol} --dport {port} -j ACCEPT",
        f"-A FORWARD -i {interface_name} -o eth0 -j ACCEPT",
        f"-A FORWARD -i eth0 -o {interface_name} -j ACCEPT",
    ]

    nat_rules = [
        ":PREROUTING ACCEPT [0:0]",
        ":INPUT ACCEPT [0:0]",
        ":OUTPUT ACCEPT [0:0]",
        ":POSTROUTING ACCEPT [0:0]",
        "-A POSTROUTING -o eth0 -j MASQUERADE",
    ]

    filter_section = "\n".join(["*filter"] + filter_rules + ["COMMIT"])
    nat_section = "\n".join(["*nat"] + nat_rules + ["COMMIT"])

    iptables_rules = f"{filter_section}\n\n{nat_section}"

    return iptables_rules
