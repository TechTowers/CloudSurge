#!/usr/bin/env bash

CLOUDSURGE_SERVER=""
CLOUDSURGE_SERVER_PASSWORD=""

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
      -s, --server    server address (something like user@127.0.0.1)
      -p, --password  password for the server

      -h, --help      display this help
EOF
}

if [[ -z "$@" ]]; then
  usage
  exit 1
fi

TEMP=$(getopt -o s:p:h --long server:,password:,help -n "$0" -- "$@")

if [ $? != 0 ]; then
  echo "Terminating..." >&2
  exit 1
fi

eval set -- "$TEMP"
unset TEMP

while true; do
  case "$1" in
  -s | --server)
    CLOUDSURGE_SERVER=$2
    shift 2
    continue
    ;;
  -p | --password)
    CLOUDSURGE_SERVER_PASSWORD=$2
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

if [[ -z $CLOUDSURGE_SERVER ]]; then
  echo "${RED}${BOLD}Please set a server with -s/--server${RESET}" >&2
  exit 1
fi

if [[ -z $CLOUDSURGE_SERVER_PASSWORD ]]; then
  echo "${RED}${BOLD}Please set a server password with -p/--password${RESET}" >&2
  exit 1
fi

if ! command apt &>/dev/null; then
  echo "${BOLD}${RED}Linux distribution is not Debian!${RESET}" >&2
  echo "${BOLD}${RED}Exiting...${RESET}" >&2
  exit 1
fi

echo "${BOLD}${GREEN}Updating system${RESET}"
apt update
apt upgrade -y

if ! command pipx &>/dev/null; then
  echo "${BOLD}${YELLOW}pipx was not found${RESET}"
  echo "${BOLD}${YELLOW}Installing pipx...${RESET}"
  echo apt install pipx -y
  echo "${BOLD}${GREEN}pipx installed successfully${RESET}"
fi

pipx ensurepath
pipx install gns3-server

if command gns3server &>/dev/null; then
  echo "${BOLD}${GREEN}gns3server installed successfully${RESET}"
else
  echo "${BOLD}${RED}gns3server failed to install${RESET}" >&2
  exit 1
fi
