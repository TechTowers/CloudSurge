# ☁️⚡ CloudSurge

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
