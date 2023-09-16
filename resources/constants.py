import os

# UI
DASHBOARD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui/dashboard.ui")

# Paths
CWD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTS = os.path.join(CWD, "tests/")
SERVERS = os.path.join(CWD, "resources/servers.json")
TUNNELS = os.path.join(CWD, "resources/tunnels.json")

# Password for servers
PASS = "G@rd!ans0fTh3G@t3w@y"
