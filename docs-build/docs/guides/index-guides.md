---
sidebar_position: 1
---

# What's inside?

This section of the documentation contain more detailed information about the
project build and testing.

View the following pages for more details about each aspect of the project:

* Test Plan
* Test matrix
* Project classes
    * init.py
    * functions.py
    * keys.py
    * ovpn.py
* [Course information](../course-title-page.html)

## Project architecture

This outlines the project `src` or source files and a basic synopsis.

* `functions.py`: Contains utility functions for checking OS, privileges, and
  more.
* `keys.py`: Manages the cloning of the `easy-rsa `repository and key
  generation.
* `ovpn.py`: Contains the `OpenVPN` class for configuring and managing tunnels.
* `tv.py`: Main entry point for the application.
* `constants.py`: Contains constants like paths and ANSI color codes.
* `servers.json`: JSON file mapping server locations to public and private IPs.