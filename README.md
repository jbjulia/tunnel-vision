# Guardians of the Gateway - Tunnel Vision

## Introduction

This project facilitates the configuration, setup, and management of OpenVPN tunnels. It provides a streamlined
interface to clone repositories, generate certificates, and configure servers and clients for secure communication. The
project is intended to be run on a Linux-based system and requires superuser privileges.

## Table of Contents

1. [Dependencies](#dependencies)
2. [Installation](#installation)
3. [Directions for Use](#directions-for-use)
4. [Structure and Components](#structure-and-components)
5. [Server Information](#server-information)
6. [Contributing](#contributing)
7. [License](#license)

## Dependencies

- **Python 3**: The project is written in Python 3.
- **OpenVPN**: Required for creating and managing VPN tunnels.
- **Git**: Required for cloning the easy-rsa repository.

## Installation

1. **Clone the Repository**: Clone the project repository to your local machine.
2. **Set Up Environment**: Ensure that Python 3, OpenVPN, and Git are installed.
3. **Grant Permissions**: Run the script with superuser privileges using `sudo`.

## Directions for Use

### Installation

1. **Clone the Repository**: Clone the project repository to your local machine.
2. **Navigate to the Directory**: Navigate to the project directory in your terminal.
3. **Install Dependencies**: Ensure that Python 3, OpenVPN, and Git are installed on your system.
4. **Grant Permissions**: Make the `tv.py` script executable by running `chmod +x tv.py`.
5. **Run as Superuser**: Execute the script with superuser privileges using `sudo ./tv.py`.

### Setting Up an OpenVPN Tunnel

1. **Launch the Application**: Run the `tv.py` script.
2. **Select "Create Tunnel"**: Follow the prompts and choose the option to create a new tunnel.
3. **Enter Tunnel Information**: Provide a name for the tunnel and select the connection type, IP addresses, interface
   name, and port number as prompted.
4. **Confirm Settings**: Review the configuration and confirm to proceed.

### Managing Existing Tunnels

1. **Launch the Application**: Run the `tv.py` script.
2. **Select "Manage Tunnels"**: Choose the option to manage existing tunnels.
3. **Modify or Delete Tunnels**: Follow the prompts to modify or delete existing tunnels as needed.

### Connecting to Servers

1. **Select "Connect to Server"**: From the main menu, choose the option to connect to a server.
2. **Choose a Server**: Select a server from the `servers.json` file.
3. **Enter Credentials**: If required, enter the necessary credentials to establish the connection.

## Structure and Components

- `functions.py`: Contains utility functions for checking OS, privileges, and more.
- `keys.py`: Manages the cloning of the easy-rsa repository and key generation.
- `ovpn.py`: Contains the `OpenVPN` class for configuring and managing tunnels.
- `tv.py`: Main entry point for the application.
- `constants.py`: Holds constants like paths and ANSI color codes.
- `servers.json`: JSON file mapping server locations to public and private IPs.

## Server Information

- The server information is stored in `servers.json`.
- Contains public and private IP addresses for various locations.

## Contributing

- Fork the repository.
- Create a branch for the specific part you're working on.
- Make your changes and create a pull request.

## License

Please refer to the project's license file.