# Get started

This topic covers the basic architecture of Tunnel Vision and installing the
project. It assumes you are familiar with OpenVPN,Python, Git, and GitHub. After
reading this topic, you should have an understanding of how to begin using
Tunnel Vision.

### Requirements

The project requires that you have the following installed:

* `Python 3` - The project uses Python 3 for its source code.
* `OpenVPN` -  Creates and manages VPN tunnels.
* `Git` - Clone the `easy-rsa` repository from GitHub.
* `Linux`

### Project architecture

This outlines the project `src` or source files and a basic synopsis.

* `functions.py`: Contains utility functions for checking OS, privileges, and
  more.
* `keys.py`: Manages the cloning of the `easy-rsa `repository and key
  generation.
* `ovpn.py`: Contains the `OpenVPN` class for configuring and managing tunnels.
* `tv.py`: Main entry point for the application.
* `constants.py`: Contains constants like paths and ANSI color codes.
* `servers.json`: JSON file mapping server locations to public and private IPs.

## Installation

Once you have a [Linux operating system
(OS)](https://www.linux.org/pages/download/) running and installed the
requirements previously mentioned, you can begin installation of the Tunnel
Vision project.

The following steps guide you through the process of getting
started with Tunnel Vision.

1. **Fork** the repository using the secure shell (SSH) link:
   `git@github.com:jbjulia/tunnel-vision.git`
2. From your fork, **clone the repository** to your local machine.
3. In your terminal, **select the directory** you saved the project in.
4. Make the `tv.py` script executable by running the following command `chmod +x tv.py`.
5. Execute the script with **superuser** privileges using `sudo ./tv.py`.

Read more about [Tunnel configuration and setup]().

## See more:

* [Generating a new SSH
  key](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent)
* [Download Python](https://www.python.org/downloads/)
* [Installing Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
* [Getting started Ubuntu](https://ubuntu.com/tutorials/install-ubuntu-desktop#1-overview)
* [OpenVPN](https://openvpn.net)