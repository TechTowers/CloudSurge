#!/usr/bin/env bash

SERVER=""
SERVER_PASSWORD=""
GNS3_PATH="\$HOME/.local/bin/gns3server"
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
      $0 [options]

    Remotely install and setup everything needed for CloudSurge.

    Options:
      -s, --server     server address (something like user@127.0.0.1)
      -k, --keyfile    key file to use for ssh
      -i, --install    install GNS3 Server on a server 
      -u, --update     update everything on the server 
      -c, --configure  configure the remote server

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
  echo
}

apt() {
  runs "DEBIAN_FRONTEND=noninteractive apt $1 -y"
}

install_gns3() {
  if command -v gns3 &>/dev/null; then
    GNS3_VERSION=$(gns3 --version)
  fi

  if run "[[ -x $GNS3_PATH ]]"; then
    GNS3_SERVER_VERSION=$(run "$GNS3_PATH --version")
  fi

  if [[ -n $GNS3_VERSION && -n $GNS3_SERVER_VERSION ]]; then
    if [[ "$GNS3_VERSION" == "$GNS3_SERVER_VERSION" ]]; then
      return 0
    else
      echo "${BOLD}${RED}Version mismatch between Client and Server! Installing the right version...${RESET}"
      run "pipx install gns3-server==$GNS3_VERSION --force" &&
        echo "${BOLD}${GREEN}Installed gns3server${RESET}"
    fi
  elif [[ -n $GNS3_VERSION && -z $GNS3_SERVER_VERSION ]]; then
    echo "${BOLD}${GREEN}Installing gns3server matching your local gns3 installation...${RESET}"
    run "pipx install gns3-server==$GNS3_VERSION --force" &&
      echo "${BOLD}${GREEN}Installed gns3server $GNS3_SERVER_VERSION${RESET}"
  else
    echo "${BOLD}${GREEN}Installing gns3server...${RESET}"
    run "pipx install gns3-server --force" &&
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

get_nftable_config() {
  cat <<EOF
flush ruleset                                                                    
                                                                             
table inet firewall {
                                                                             
    chain inbound_ipv4 {
        icmp type echo-request limit rate 5/second accept      
    }

    chain inbound_ipv6 {                                                         
        icmpv6 type { nd-neighbor-solicit, nd-router-advert, nd-neighbor-advert } accept
        icmpv6 type echo-request limit rate 5/second accept
    }

    chain inbound {                                                              
        type filter hook input priority 0; policy drop;

        ct state vmap { established : accept, related : accept, invalid : drop } 

        iifname lo accept

        meta protocol vmap { ip : jump inbound_ipv4, ip6 : jump inbound_ipv6 }

        tcp dport { 22, 3080 } accept
    }                                                                            
                                                                             
    chain forward {                                                              
        type filter hook forward priority 0; policy drop;                        
    }                                                                            
}
EOF
}

if [[ -z "$@" ]]; then
  usage
  exit 1
fi

TEMP=$(getopt -o s:k:iuch --long server:,keyfile:,install,update,configure,help -n "$0" -- "$@")

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
  update

  if ! run "command -v pipx &> /dev/null"; then
    echo "${BOLD}${YELLOW}pipx was not found${RESET}"
    echo "${BOLD}${YELLOW}Installing pipx...${RESET}"
    sleep 1
    apt "install pipx" &&
      echo "${BOLD}${GREEN}pipx installed successfully${RESET}"
    run "pipx ensurepath" &&
      echo "${BOLD}${GREEN}Added paths...${RESET}"
  fi

  if ! run "[[ -e /usr/sbin/nft ]]"; then
    echo "${BOLD}${YELLOW}nftables was not found${RESET}"
    echo "${BOLD}${YELLOW}Installing nftables...${RESET}"
    apt "install nftables"
  fi

  echo "${BOLD}${GREEN}Enabling nftables${RESET}"
  runs "systemctl enable --now nftables"

  install_gns3

  run "mkdir CloudSurge/ 2> /dev/null"
  run "touch CloudSurge/.installed"

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
    echo "${BOLD}${GREEN}Writing firewall rules${RESET}"
    runs "chmod 777 /etc/nftables.conf"
    get_nftable_config | run "cat > /etc/nftables.conf"
    runs "chmod 755 /etc/nftables.conf"
    echo "${BOLD}${GREEN}Restarting nftables${RESET}"
    runs "systemctl restart nftables"
  else
    echo "${BOLD}${RED}Please install with -i first.${RESET}"
    exit 1
  fi
fi
