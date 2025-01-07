#!/usr/bin/env bash

SERVER=""
SERVER_PASSWORD=""
GNS3_PATH="\$HOME/.local/bin/gns3server"
ZEROTIER_NETWORK=""
INSTALL=0
UPDATE=0
CONFIGURE=0
PASSWORDLESS=1
KEY_FILE=""

# Formatting
GREEN=$(tput setaf 2)
YELLOW=$(tput setaf 3)
RED=$(tput setaf 1)
BOLD=$(tput bold)
RESET=$(tput sgr0)

usage() {
  cat <<EOF
    Usage:
      $0 [flags]

    Remotely install and setup everything needed for CloudSurge.

    Flags:
      -s, --server     server address (something like user@127.0.0.1)
      -k, --keyfile    key file to use for ssh
      -i, --install    install GNS3 Server on a server 
      -u, --update     update everything on the server 
      -c, --configure  configure the remote server
      -z, --zerotier   the zerotier network to join
      -p, --password   ask for a password
      -h, --help       display this help
EOF
}

success() {
  echo "${GREEN}${BOLD}$1${RESET}"
}

warning() {
  echo "${YELLOW}${BOLD}$1${RESET}" >&2
}

fail() {
  echo "${RED}${BOLD}$1${RESET}" >&2
  exit 1
}

run() {
  if [[ -z $KEY_FILE ]]; then
    ssh -q "$SERVER" "$1"
  else
    ssh -q -i "$KEY_FILE" "$SERVER" "$1"
  fi
}

runs() {
  run "echo $SERVER_PASSWORD | sudo -S $1"
  ECODE=$?
  echo
  return $ECODE
}

run_cs() {
  runs "su cloudsurge -c '$1'"
}

apt() {
  runs "DEBIAN_FRONTEND=noninteractive apt $1 -y"
}

install_tool() {
  if ! run "command -v $1 &> /dev/null"; then
    warning "$1 was not found"
    success "Installing $1..."
    sleep 1
    apt "install $1" ||
      fail "Installing $1 failed!"
  fi
}

install_gns3() {
  success "Installing dependencies for GNS3..."
  sleep 1
  apt "install python3 python3-pip pipx qemu-kvm qemu-utils libvirt-clients libvirt-daemon-system virtinst software-properties-common ca-certificates curl gnupg2" ||
    fail "Installing dependencies for GNS3 failed!"
  if command -v gns3 &>/dev/null; then
    GNS3_VERSION=$(gns3 --version)
  fi

  if run "[[ -x $GNS3_PATH ]]"; then
    GNS3_SERVER_VERSION=$(run "$GNS3_PATH --version")
  fi

  success "Installing dependencies for vpcs..."
  install_tool "git"
  install_tool "make"
  install_tool "gcc"
  run "rm -rf ./CloudSurge/vpcs"
  success "Cloning vpcs repository..."
  sleep 1
  run "git clone https://github.com/GNS3/vpcs ./CloudSurge/vpcs" ||
    fail "Cloning vpcs failed!"
  success "Building vpcs..."
  sleep 1
  run "cd ./CloudSurge/vpcs/src && bash mk.sh" ||
    fail "Building vpcs failed!"
  success "Installing vpcs..."
  sleep 1
  runs "mv ./CloudSurge/vpcs/src/vpcs /usr/local/bin/vpcs" ||
    fail "Installing vpcs failed!"

  success "Installing dependencies for ubridge..."
  apt "install libcap-dev"
  apt "install libpcap0.8-dev"
  success "Successfully installed dependencies for ubridge"
  run "rm -rf ./CloudSurge/ubridge"
  success "Cloning ubridge repository..."
  sleep 1
  run "git clone https://github.com/GNS3/ubridge ./CloudSurge/ubridge" ||
    fail "Cloning ubridge failed!"
  success "Building ubridge..."
  sleep 1
  run "cd ./CloudSurge/ubridge && make" ||
    fail "Building ubridge failed!"
  success "Installing ubridge..."
  sleep 1
  run "cd ./CloudSurge/ubridge && echo $SERVER_PASSWORD | sudo -S make install" ||
    fail "Installing ubridge failed!"

  success "Installing dependencies for dynamips..."
  install_tool "cmake"
  apt "install libelf-dev"
  success "Successfully installed dependencies for dynamips"
  run "rm -rf ./CloudSurge/dynamips"
  success "Cloning dynamips repository..."
  sleep 1
  run "git clone https://github.com/GNS3/dynamips ./CloudSurge/dynamips" ||
    fail "Cloning dynamips failed!"
  run "mkdir ./CloudSurge/dynamips/build"
  success "Building dynamips..."
  sleep 1
  run "cd ./CloudSurge/dynamips/build && cmake .." ||
    fail "Building dynamips failed!"
  success "Installing dynamips..."
  sleep 1
  run "cd ./CloudSurge/dynamips/build && echo $SERVER_PASSWORD | sudo -S make install" ||
    fail "Installing dynamips failed!"

  success "Adding kvm group to cloudsurge user"
  sleep 1
  runs "usermod -aG kvm cloudsurge" ||
    fail "Successfully added kvm group to cloudsurge failed!"

  if [[ -n $GNS3_VERSION && -n $GNS3_SERVER_VERSION ]]; then
    if [[ "$GNS3_VERSION" == "$GNS3_SERVER_VERSION" ]]; then
      return 0
    else
      warning "Version mismatch between Client and Server! Installing the right version..."
      sleep 1
      run_cs "pipx install gns3-server==$GNS3_VERSION --force" ||
        fail "Installing gns3server failed!"
    fi
  elif [[ -n $GNS3_VERSION && -z $GNS3_SERVER_VERSION ]]; then
    success "Installing gns3server matching your local gns3 installation..."
    sleep 1
    run_cs "pipx install gns3-server==$GNS3_VERSION --force" ||
      fail "Installing gns3server failed!"
  else
    success "Installing gns3server..."
    sleep 1
    run_cs "pipx install gns3-server --force" ||
      fail "Installing gns3server failed!"
  fi
}

update() {
  success "Updating system packages..."
  sleep 1
  apt "update" ||
    fail "Updating system packages failed!"

  success "Upgrading system packages..."
  sleep 1
  apt "upgrade" ||
    fail "upgrading system packages failed!"
}

if [[ -z "$@" ]]; then
  usage
  exit 1
fi

TEMP=$(getopt -o s:k:iucz:ph --long server:,keyfile:,install,update,configure,zerotier:,passwordless,help -n "$0" -- "$@")

if [ $? != 0 ]; then
  echo "Terminating..." >&2
  exit 1
fi

eval set -- "$TEMP"
unset TEMP

while true; do
  case "$1" in
  -s | --server)
    SERVER=$2
    shift 2
    continue
    ;;
  -k | --keyfile)
    KEY_FILE=$2
    shift 2
    continue
    ;;
  -i | --install)
    INSTALL=1
    shift
    continue
    ;;
  -u | --update)
    UPDATE=1
    shift
    continue
    ;;
  -c | --configure)
    CONFIGURE=1
    shift
    continue
    ;;
  -z | --zerotier)
    ZEROTIER_NETWORK=$2
    shift 2
    continue
    ;;
  -p | --passwordless)
    PASSWORDLESS=0
    shift
    continue
    ;;
  -h | --help)
    usage
    exit 0
    ;;
  --)
    shift
    break
    ;;
  *)
    exit 1
    ;;
  esac
done

if [[ -z $SERVER ]]; then
  fail "Please set a server with -s/--server"
fi

if ((INSTALL + UPDATE + CONFIGURE != 1)); then
  fail "Please use only one of these flags: -i, -u, -c"
fi

if [[ $PASSWORDLESS == 0 ]]; then
  read -r -s -p "Enter password for Server: " SERVER_PASSWORD
  echo

  echo "Checking password..."
  if ! runs "echo" &>/dev/null; then
    fail "Connection failed! Is the password correct?"
  fi
fi

if ! run "command -v apt &> /dev/null"; then
  fail "Linux distribution is not Debian!"
fi

if [[ $INSTALL -eq 1 ]]; then
  if ! run "LC_ALL=C.UTF-8 lscpu | grep Virtualization &> /dev/null"; then
    fail "This machine does not support KVM! Please use a machine that supports KVM or enable it."
  fi

  update

  success "Adding user and group cloudsurge..."
  sleep 1
  runs "groupadd cloudsurge"
  runs "useradd -c 'CloudSurge' -d /home/cloudsurge -m -s /bin/bash -g cloudsurge cloudsurge"

  apt "install python3-venv"
  install_tool "pipx"
  run_cs "pipx ensurepath" ||
    fail "Adding paths failed!"

  install_gns3

  if ! runs "command -v zerotier-cli &> /dev/null"; then
    install_tool "curl"

    warning "ZeroTier was not found"
    success "Installing ZeroTier..."
    run "curl -s https://install.zerotier.com > /tmp/zerotier.sh"
    sleep 1
    runs "bash /tmp/zerotier.sh" ||
      fail "Installing ZeroTier failed!"

    success "Enabling ZeroTier..."
    sleep 1
    runs "systemctl enable --now zerotier-one.service" ||
      fail "Enabling ZeroTier failed!"
  fi

  success "Downloading CloudSurge SystemdD service..."
  sleep 1
  run "curl -s https://raw.githubusercontent.com/TechTowers/CloudSurge/refs/heads/development/services/cloudsurge.service > cloudsurge.service" ||
    fail "Downloading CloudSurge service failed!"
  success "Moving cloudsurge service to correct place..."
  sleep 1
  runs "mv cloudsurge.service /etc/systemd/system/cloudsurge.service" ||
    fail "Moving cloudsurge service failed!"
  success "Starting CloudSurge SystemdD service..."
  sleep 1
  runs "systemctl enable --now cloudsurge.service" ||
    fail "Starting CloudSurge service failed!"

  run "mkdir ./CloudSurge/ 2> /dev/null"
  run "touch ./CloudSurge/.installed"

elif [[ $UPDATE -eq 1 ]]; then
  if run "[[ -e CloudSurge/.installed ]]"; then
    update
    install_gns3
  else
    fail "Please install with -i first."
  fi

elif [[ $CONFIGURE -eq 1 ]]; then
  if run "[[ -e CloudSurge/.installed ]]"; then
    if [[ -z $ZEROTIER_NETWORK ]]; then
      fail "Please set a ZeroTier Network with -z/--zerotier"
    fi
    success "Configuring ZeroTier Network..."
    for NETWORK in $(runs "zerotier-cli listnetworks | tail +2 | cut -d ' ' -f3"); do
      echo
      warning "Leaving old ZeroTier Network $NETWORK..."
      runs "zerotier-cli leave $NETWORK > /dev/null" ||
        warning "Leaving ZeroTier Network $ZEROTIER_NETWORK failed!"
    done
    success "Joining ZeroTier Network $ZEROTIER_NETWORK..."
    runs "zerotier-cli join $ZEROTIER_NETWORK > /dev/null" ||
      fail "Joining ZeroTier Network $ZEROTIER_NETWORK failed!"
  else
    fail "Please install with -i first."
  fi
fi
