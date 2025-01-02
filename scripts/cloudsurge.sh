#!/usr/bin/env bash

SERVER=""
SERVER_PASSWORD=""
GNS3_PATH="\$HOME/.local/bin/gns3server"
ZEROTIER_NETWORK=""
INSTALL=0
UPDATE=0
CONFIGURE=0
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

      -h, --help     display this help
EOF
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
    echo "${BOLD}${YELLOW}$1 was not found${RESET}"
    echo "${BOLD}${YELLOW}Installing $1...${RESET}"
    sleep 1
    apt "install $1" &&
      echo "${BOLD}${GREEN}$1 installed successfully${RESET}"
  fi
}

install_gns3() {
  echo "${BOLD}${GREEN}Installing dependencies for GNS3${RESET}"
  apt "install python3 python3-pip pipx qemu-kvm qemu-utils libvirt-clients libvirt-daemon-system virtinst software-properties-common ca-certificates curl gnupg2"
  if command -v gns3 &>/dev/null; then
    GNS3_VERSION=$(gns3 --version)
  fi

  if run "[[ -x $GNS3_PATH ]]"; then
    GNS3_SERVER_VERSION=$(run "$GNS3_PATH --version")
  fi

  install_tool "git"
  install_tool "make"
  install_tool "gcc"
  run "rm -rf ./CloudSurge/vpcs"
  run "git clone https://github.com/GNS3/vpcs ./CloudSurge/vpcs"
  run "cd ./CloudSurge/vpcs/src && bash mk.sh"
  runs "mv ./CloudSurge/vpcs/src/vpcs /usr/local/bin/vpcs"

  apt "install libcap-dev"
  apt "install libpcap0.8-dev"
  run "rm -rf ./CloudSurge/ubridge"
  run "git clone https://github.com/GNS3/ubridge ./CloudSurge/ubridge"
  run "cd ./CloudSurge/ubridge && make"
  run "cd ./CloudSurge/ubridge && echo $SERVER_PASSWORD | sudo -S make install"

  install_tool "cmake"
  apt "install libelf-dev"
  run "git clone https://github.com/GNS3/dynamips ./CloudSurge/dynamips"
  run "mkdir ./CloudSurge/dynamips/build"
  run "cd ./CloudSurge/dynamips/build && cmake .."
  run "cd ./CloudSurge/dynamips/build && echo $SERVER_PASSWORD | sudo -S make install"

  runs "usermod -aG kvm cloudsurge"

  if [[ -n $GNS3_VERSION && -n $GNS3_SERVER_VERSION ]]; then
    if [[ "$GNS3_VERSION" == "$GNS3_SERVER_VERSION" ]]; then
      return 0
    else
      echo "${BOLD}${RED}Version mismatch between Client and Server! Installing the right version...${RESET}"
      run_cs "pipx install gns3-server==$GNS3_VERSION --force" &&
        echo "${BOLD}${GREEN}Installed gns3server${RESET}"
    fi
  elif [[ -n $GNS3_VERSION && -z $GNS3_SERVER_VERSION ]]; then
    echo "${BOLD}${GREEN}Installing gns3server matching your local gns3 installation...${RESET}"
    run_cs "pipx install gns3-server==$GNS3_VERSION --force" &&
      echo "${BOLD}${GREEN}Installed gns3server $GNS3_SERVER_VERSION${RESET}"
  else
    echo "${BOLD}${GREEN}Installing gns3server...${RESET}"
    run_cs "pipx install gns3-server --force" &&
      echo "${BOLD}${GREEN}Installed gns3server${RESET}"
  fi
}

update() {
  echo "${BOLD}${GREEN}Updating system packages...${RESET}"
  sleep 1
  apt "update"

  echo "${BOLD}${GREEN}Upgrading system packages...${RESET}"
  sleep 1
  apt "upgrade"
}

if [[ -z "$@" ]]; then
  usage
  exit 1
fi

TEMP=$(getopt -o s:k:iucz:h --long server:,keyfile:,install,update,configure,zerotier:,help -n "$0" -- "$@")

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
  echo "${RED}${BOLD}Please set a server with -s/--server${RESET}" >&2
  exit 1
fi

if ((INSTALL + UPDATE + CONFIGURE != 1)); then
  echo "${BOLD}${RED}Please use only one of these flags: -i, -u, -c" >&2
  exit 1
fi

read -s -p "Enter password for Server: " SERVER_PASSWORD
echo

echo "${BOLD}${YELLOW}Checking password...${RESET}"
if ! runs "echo" &>/dev/null; then
  echo "${RED}${BOLD}Connection failed! Is the password correct?${RESET}" >&2
  exit 1
fi

if ! run "command -v apt &> /dev/null"; then
  echo "${BOLD}${RED}Linux distribution is not Debian!${RESET}" >&2
  echo "${BOLD}${RED}Exiting...${RESET}" >&2
  exit 1
fi

if [[ $INSTALL -eq 1 ]]; then
  if ! run "LC_ALL=C.UTF-8 lscpu | grep Virtualization &> /dev/null"; then
    echo "${BOLD}${RED}This machine does not support KVM! Please use a machine that supports KVM or enable it.${RESET}"
    exit 1
  fi

  update

  runs "groupadd cloudsurge"
  runs "useradd -c 'CloudSurge' -d /home/cloudsurge -m -s /bin/bash -g cloudsurge cloudsurge"

  install_tool "pipx"
  run_cs "pipx ensurepath" &&
    echo "${BOLD}${GREEN}Added paths...${RESET}"

  install_gns3

  if ! runs "command -v zerotier-cli &> /dev/null"; then
    install_tool "curl"

    run "curl -s https://install.zerotier.com > /tmp/zerotier.sh"
    echo "${BOLD}${YELLOW}ZeroTier was not found${RESET}"
    echo "${BOLD}${YELLOW}Installing ZeroTier...${RESET}"
    sleep 1
    runs "bash /tmp/zerotier.sh" &&
      echo "${BOLD}${GREEN}ZeroTier installed successfully${RESET}"
    runs "systemctl enable --now zerotier-one.service"
  fi

  echo "${BOLD}${GREEN}Downloading CloudSurge SystemdD service...${RESET}"
  run "curl -s https://raw.githubusercontent.com/TechTowers/CloudSurge/refs/heads/development/services/cloudsurge.service > cloudsurge.service"
  runs "mv cloudsurge.service /etc/systemd/system/cloudsurge.service"
  echo "${BOLD}${GREEN}Starting CloudSurge SystemdD service...${RESET}"
  runs "systemctl enable --now cloudsurge.service" &&
    echo "${BOLD}${GREEN}Started CloudSurge SystemdD service${RESET}"

  run "mkdir ./CloudSurge/ 2> /dev/null"
  run "touch ./CloudSurge/.installed"

elif [[ $UPDATE -eq 1 ]]; then
  if run "[[ -e CloudSurge/.installed ]]"; then
    update
    install_gns3
  else
    echo "${BOLD}${RED}Please install with -i first.${RESET}"
    exit 1
  fi

elif [[ $CONFIGURE -eq 1 ]]; then
  if run "[[ -e CloudSurge/.installed ]]"; then
    if [[ -z $ZEROTIER_NETWORK ]]; then
      echo "${RED}${BOLD}Please set a ZeroTier Network with -z/--zerotier${RESET}" >&2
      exit 1
    fi
    echo "${BOLD}${GREEN}Configuring ZeroTier Network...${RESET}"
    for NETWORK in $(runs "zerotier-cli listnetworks | tail +2 | cut -d ' ' -f3"); do
      echo
      echo "${BOLD}${GREEN}Leaving old ZeroTier Network $NETWORK...${RESET}"
      runs "zerotier-cli leave $NETWORK > /dev/null"
    done
    echo "${BOLD}${GREEN}Joining ZeroTier Network $ZEROTIER_NETWORK...${RESET}"
    runs "zerotier-cli join $ZEROTIER_NETWORK > /dev/null"
  else
    echo "${BOLD}${RED}Please install with -i first.${RESET}"
    exit 1
  fi
fi
