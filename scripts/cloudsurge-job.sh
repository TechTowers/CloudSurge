#!/usr/bin/env bash

if pgrep cloudsurge; then
  exit 0
fi

# Lists for costs
PROVIDERS=()
VMS=()
LIMITS=()
EXCEEDS=()

# Fill the lists
while read -r LINE; do
  PROVIDERS+=("$(echo "$LINE" | cut -d ";" -f 1)")
  VMS+=("$(echo "$LINE" | cut -d ";" -f 2)")
  LIMITS+=("$(echo "$LINE" | cut -d ";" -f 3)")
  EXCEEDS+=("$(echo "$LINE" | cut -d ";" -f 4)")
done < <(flatpak run org.techtowers.CloudSurge -c)

# Build the notification
BODY=""

for INDEX in $(seq ${#PROVIDERS[@]}); do
  PROVIDER=${PROVIDERS[((INDEX - 1))]}
  VM=${VMS[((INDEX - 1))]}
  LIMIT=${LIMITS[((INDEX - 1))]}
  EXCEED=${EXCEEDS[((INDEX - 1))]}
  BODY+="$VM ($PROVIDER) exceeds the cost limit of $LIMIT by $EXCEED\n"
done

ACTION=$(
  notify-send -a "CloudSurge" \
    "One or more VMs exceeded the cost limit!" \
    "$BODY" \
    -u critical \
    -A default="Open CloudSurge"
)

if [[ "$ACTION" == default ]]; then
  flatpak run org.techtowers.CloudSurge
fi

if [[ $(flatpak run org.techtowers.CloudSurge -o) != "0" ]] && ! pgrep gns; then
  ACTION=$(
    notify-send -a "CloudSurge" \
      "$VMS_RUNNING VMs are running!" \
      "GNS3 Client does not seem to run locally." \
      -u critical \
      -A default="Open CloudSurge"
  )

  if [[ "$ACTION" == default ]]; then
    flatpak run org.techtowers.CloudSurge
  fi
fi
