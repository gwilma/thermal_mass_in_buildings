#!/usr/bin/env bash
# Download the open-access PDFs listed in sources.tsv into this folder.
# Skips files already present; reports anything that is not a PDF.
set -u
cd "$(dirname "$0")"
tail -n +2 sources.tsv | while IFS=$'\t' read -r name _ url; do
  [ -s "$name" ] && { echo "have  $name"; continue; }
  if curl -sSL -A "Mozilla/5.0" --max-time 90 -o "$name.part" "$url" && head -c 4 "$name.part" | grep -q '%PDF'; then
    mv "$name.part" "$name"; echo "got   $name"
  else
    rm -f "$name.part"; echo "MISS  $name  ($url)"
  fi
done
