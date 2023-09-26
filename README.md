<p align="center">
    <img alt="Tunnel vision logo" src="./resources/ui/logos/tunnel-vision-logo.png"/>
</p>

## Overview

Tunnel Vision is an innovative OpenVPN client management application designed to make VPN tunnel creation and management accessible to users of all technical backgrounds. With its intuitive and user-friendly graphical interface, Tunnel Vision eliminates the complexity typically associated with VPN setup.

Users can easily configure VPN connections, choose server locations, and customize tunnel parameters such as tunnel name, private IP addresses, and connection protocols. This software automates the generation of SSL certificates and keys required for secure VPN connections by using the [easy-rsa CA utility](https://github.com/OpenVPN/easy-rsa), ensuring users can establish their VPN tunnels quickly and securely.

The application also provides real-time updates on the user's public IP address, making it easy to monitor the status of the VPN connection. Whether for personal privacy, remote access, or bypassing geo-restrictions, Tunnel Vision empowers individuals and businesses to take control of their online security and access needs. Its user-friendly features, robust error handling, and visual feedback mechanisms make it an invaluable tool in the realm of VPN management, simplifying the process of securing online activities.

Tunnel Vision is built and run on a Linux-based system and requires superuser
privileges.

## Build requirements

* `Python 3` - The project uses Python 3 for its source code.
* `OpenVPN` - Creates and manages VPN tunnels.
* `Git` - Clone the `easy-rsa` repository from GitHub.
* `Linux`

Learn more about project structure and getting started on the [Get
Started](./docs/get-started.md) page.

## Installation

Tunnel Vision is a Python project built on Linux follow these steps to set up
the project on your machine:

1. Create a **Fork** of the `tunnel-vision` repository.
2. Navigate to your personal fork and **clone** the repository the repository using the secure shell (SSH) link:

```
git@github.com:<username>/tunnel-vision.git
```

4. Open terminal.
5. Navigate to the `tunnel-vision` directory.
6. Install the project requirements using the following commands:

```
sudo pip3 install -r requirements.txt
sudo apt install sshpass
```

_This should install the project dependencies._

7. Once the project requirements are met run the Tunnel Vision application using superuser privileges:

```
sudo python3 ./tv.py
```

_At this point, the application should open._

## Configure a tunnel

1. Launch the application.
2. Run the script `tv.py`.
3. Click **Build Tunnel**.
4. Enter **Tunnel Information** such as a name and Internet Protocol (IP)
   address for the tunnel.
5. Review the configuration and click `Create Tunnel` to proceed.

### Manage existing tunnels

1. Launch the application.
2. Run the script `tv.py`.
3. Click **Delete Tunnel**.
4. If any preexisting tunnels, choose from the drop-down menu, the tunnel you would like to delete.

### Connect to a server

1. Select **Connect VPN**.
2. From the drop-down menu, **choose a server you want use**.
3. The IP should update to the chosen server in the main menu.

Read more detailed setup and configuration information on the [Tunnel
configuration](./docs/tunnel-config.md) page.

## Styling and contributing

> **Note:** Do not clone directly on the Tunnel Vision master branch. You
> **MUST** create your own fork then clone that fork.

Read additional information about styling and the conventions in the `docs-build`
module `README` file.

## License

Tunnel Vision is open-source software licensed under the [MIT License](LICENSE).
