---
sidebar_position: 2
---

# Tunnel configuration

<!--This documentation is worded for a GUI, not console based application.-->

This topic covers Tunnel configuration with the Tunnel Vision project. It
assumes that you have installed the project as described on the [Get
started](./installation.html) page.

If you have not yet read the `Get started` page, go there now.

Now that you have Tunnel Vision up and running, it is time to configure your
first tunnel.

## Setting up a tunnel

The following steps guide you through setting up a tunnel.

1. Launch **Tunnel Vision**.
2. Run `tv.py`.
3. Select **Create a tunnel**.
4. From the drop-down menu, **choose your desired connection type**. For example,
   `p2p` or `subnet`.

If you do not choose a connection type, it will default to `p2p`.

5. Enter the name of your tunnel to be created. For example, `happy-tunnel`
6. From the drop-down menu, **choose your desired server**. For example, `New
   York (nyc1), London (lon1), or Frankfurt (fra1)`.
7. From the drop-down menu, choose the **private IP** you would like to use.

If you do not choose a private IP address for the client, then it will default
to your current IP.

8. Enter the port number. The default port is `1194`. It will now generate
   certificates and clone the `easy-rsa` repository.
9. Follow the prompts instructed by the repository.
10. Review the configuration and click **confirm configuration** to proceed.

## Manage existing tunnels

1. Launch the Application.
2. Run the `tv.py` script.
3. Click **Manage Tunnels**.
4. **Modify or Delete Tunnels**.

### Connect to a server

1. Click **Connect to Server**.
2. From the list of servers in the `servers.json`, **choose a server you want
   use**.
3. Enter information.
4. **Connect to server**.


<!-- Managing Existing Tunnels

    Launch the Application: Run the tv.py script.
    Select "Manage Tunnels": Choose the option to manage existing tunnels.
    Modify or Delete Tunnels: Follow the prompts to modify or delete existing tunnels as needed.

Connecting to Servers

    Select "Connect to Server": From the main menu, choose the option to connect to a server.
    Choose a Server: Select a server from the servers.json file.
    Enter Credentials: If required, enter the necessary credentials to establish the connection. -->
