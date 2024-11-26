#!/usr/bin/env bash

SERVER=""
SERVER_PASSWORD=""
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
      -s, --server   server address (something like user@127.0.0.1)
      -k, --keyfile  key file to use for ssh

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
}

if [[ -z "$@" ]]; then
  usage
  exit 1
fi

TEMP=$(getopt -o s:k:h --long server:,keyfile:,help -n "$0" -- "$@")

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

echo "${BOLD}${GREEN}Updating system...${RESET}"
sleep 1
runs "apt update -y"

echo "${BOLD}${GREEN}Upgrading system...${RESET}"
sleep 1
runs "apt upgrade -y"

if ! run "command -v pipx &> /dev/null"; then
  echo "${BOLD}${YELLOW}pipx was not found${RESET}"
  echo "${BOLD}${YELLOW}Installing pipx...${RESET}"
  sleep 1
  runs "apt install pipx -y" &&
    echo "${BOLD}${GREEN}pipx installed successfully${RESET}"
  run "pipx ensurepath" &&
    echo "${BOLD}${GREEN}Added paths...${RESET}"
fi

if ! run "command -v gns3server"; then
  echo "${BOLD}${GREEN}Installing gns3server...${RESET}"
  run "pipx install gns3-server" &&
    echo "${BOLD}${GREEN}gns3server installed successfully${RESET}"
fi
