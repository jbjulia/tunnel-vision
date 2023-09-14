---
sidebar_position: 3
---

# Build the Docs

Tunnel vision's documentation uses Docusaurus, which is a
**static-site-generator** (also called **[Jamstack](https://jamstack.org/)**).

It builds your site as simple **static HTML, JavaScript and CSS files**.


## What you need

There are some requirements in order to build the docs locally. This next
section assumes you do not have Node.js installed on your machine. Follow these
steps to **install**. If already installed skip these steps:


1. Update your Advanced Package Tool `apt`:

```bash
sudo apt update
```

2. Install Node.js and the package manager:

```bash
sudo apt install nodejs npm
```

This will install various packages, including the tools needed to compile native
addons from npm.

3. Once the install is complete check version. Note, the version must be 16 or
   higher.

```bash
node -v
```

If the installed version is below 16, update to a higher version by running the
following commands:

```bash
sudo npm install -g n
sudo n lts
```

LTS means long term support and is recommended. However, you can update to the
latest version by using `current` in place of `lts`.

## Start the build

Navigate to the `docs-build` dir:

```bash
cd docs-build
```

If you want to con

Build your site **locally**:

```bash
npm run start
```

The `docs-build` folder is now locally hosted at
[http://localhost:3000/](http://localhost:3000/).

Build and view the **production** site.

```bash
cd build
npm run build
npm run serve
```

The static HTML files are generated in the `build` folder.

The `build` folder is now served at
[http://localhost:3000/](http://localhost:3000/).

Currently, the docs are not being served on a web host.

Read more details on
[Docusaurus](https://docusaurus.io/docs/category/getting-started).
