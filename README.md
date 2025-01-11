# ☁️⚡ CloudSurge

<!--toc:start-->

- [☁️⚡ CloudSurge](#️-cloudsurge)
  - [🚀 Quick Start](#🚀-quick-start)
    - [💲 CLI](#💲-cli)
    - [🖱️ GUI (WIP)](#🖱️-gui-wip)
  - [💽 Providers](#💽-providers)
    - [DigitalOcean](#digitalocean)

<!--toc:end-->

CloudSurge is a program that you can use to set up GNS3 in the cloud
automagically ✨. There are three main components:

- the `cloudsurge.sh` script
- the front end
- the back end

The `cloudsurge.sh` script can be used on its own to connect to a remote VPS
via ssh to install GNS3 and all the dependencies. It also installs ZeroTier
which then is used to connect to the VPS. The reason for that is pretty easy:
some providers like Azure have a own firewall which blocks the traffic
regardless of if the firewall of the VPS itself allows it. That's why we
decided on using ZeroTier to work around this restriction.

## 🚀 Quick Start

There are two main ways you could use CloudSurge. Either you let us create a VM
for you or you create one yourself and use our CLI to just set up GNS3 and
[ZeroTier](https://www.zerotier.com/) (click for Documentation).

### 💲 CLI

For more info take a look at the [script's README](/scripts/README.md)

1. Create an account on a provider that has KVM support
2. Create a VM
3. Download the SSH key or copy the password
4. Clone the repository:

```bash
git clone https://github.com/TechTowers/CloudSurge
```

5. Make the script executable:

```bash
cd scripts
chmod +x cloudsurge.sh
```

6. Run the script:

```bash
./cloudsurge.sh -h
```

7. After you installed and configured the VM with our script you need to
   [authorize](https://docs.zerotier.com/start#authorize-your-device-on-your-network)
   the VM on the ZeroTier Network

### 🖱️ GUI (WIP)

## 💽 Providers

Currently, we support two Providers:

1. [DigitalOcean](www.digitalocean.com/)
2. [AWS](aws.amazon.com)

If you already have an account you should still read the sections below to do some things you may not have done!

### DigitalOcean

First create a DigitalOcean account. It will ask you for a payment method and verify the payment method by charging you a little bit, but don't worry you'll get it refunded again!

It will ask you some Question to create a Droplet yourself, but if you're here you probably want to let us do that for you, so just skip it.

Open [this](https://cloud.digitalocean.com/account/api/tokens) page and generate a new API Token with **Full Access**.

After that you will need to add an SSH key on [this](https://cloud.digitalocean.com/account/security) page. Click on the `Add SSH Key` button and follow the steps outlined there.

After that you can add a DigitalOcean provider in CloudSurge. You will be asked for the API Token, the SSH fingerprint and the path of your SSH key: just put in the three things, and you're good to go :)
