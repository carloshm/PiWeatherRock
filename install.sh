#!/usr/bin/env bash
# Install PiWeatherRock on a Raspberry Pi (or similar Linux system).
# Usage: ./install.sh [timezone]
# Example: ./install.sh Europe/Madrid

set -euo pipefail

TIMEZONE="${1:-UTC}"

echo "==> Setting timezone to ${TIMEZONE}..."
sudo timedatectl set-timezone "${TIMEZONE}"

echo "==> Updating system packages..."
sudo apt update
sudo apt full-upgrade -y
sudo apt install -y python3 python3-pip python3-venv git libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev

echo "==> Creating virtual environment..."
python3 -m venv ~/pwr-env
source ~/pwr-env/bin/activate

echo "==> Installing PiWeatherRock..."
pip install --upgrade pip setuptools wheel
pip install .

echo ""
echo "Installation complete."
echo "Activate the environment with: source ~/pwr-env/bin/activate"
echo ""
echo "Before running, create your config file:"
echo "  cp piweatherrock/config.json-sample piweatherrock/piweatherrock-config.json"
echo "  # Edit piweatherrock-config.json with your coordinates, timezone, etc."
echo ""
echo "Run with: pwr-ui -c ./piweatherrock/piweatherrock-config.json"
