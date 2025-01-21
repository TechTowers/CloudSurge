#!/usr/bin/env bash

GREEN=$(tput setaf 2)
RED=$(tput setaf 1)
BOLD=$(tput bold)
RESET=$(tput sgr0)

info() {
  echo "${GREEN}${BOLD}$1${RESET}"
}

error() {
  echo "${RED}${BOLD}$1${RESET}"
}

if [[ "$(id -u)" -eq 0 ]]; then
  error "Do not run this script with sudo!"
  exit 1
fi

CLOUDSURGE_FLATPAK="https://github.com/TechTowers/CloudSurge/releases/latest/download/cloudsurge.flatpak"
JOB_SCRIPT="https://raw.githubusercontent.com/TechTowers/CloudSurge/refs/heads/main/scripts/cloudsurge-job.sh"
JOB_TIMER="https://raw.githubusercontent.com/TechTowers/CloudSurge/refs/heads/main/services/cloudsurge-job.timer"
JOB_SERVICE="https://raw.githubusercontent.com/TechTowers/CloudSurge/refs/heads/main/services/cloudsurge-job.service"

SERVICE_DIR="$HOME/.config/systemd/user"

info "Downloading latest CloudSurge version"
curl -fsSL $CLOUDSURGE_FLATPAK >cloudsurge.flatpak

info "Installing the latest CloudSurge version"
flatpak install cloudsurge.flatpak ||
  error "You already have the newest version!"

info "Downloading SystemD service and timer"
mkdir -p "$SERVICE_DIR"
curl -fsSL $JOB_SCRIPT >"$HOME"/.local/bin/cloudsurge-job.sh
chmod +x "$HOME"/.local/bin/cloudsurge-job.sh
curl -fsSL $JOB_TIMER >"$SERVICE_DIR"/cloudsurge-job.timer
curl -fsSL $JOB_SERVICE >"$SERVICE_DIR"/cloudsurge-job.service

info "Enabling service and timer"
systemctl enable --user --now cloudsurge-job.timer

info "Successfully installed CloudSurge and it's services :)"
