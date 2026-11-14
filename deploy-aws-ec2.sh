#!/bin/bash
# ==============================================================================
# One-Click AWS EC2 Deployment Script for Budget Intelligence Platform
# Run this on a fresh Ubuntu 22.04 / 24.04 EC2 instance
# ==============================================================================

set -e

echo "=========================================================="
echo "  Deploying Budget Intelligence Platform on AWS EC2"
echo "=========================================================="

# 1. Update system
echo "[1/5] Updating system packages..."
sudo apt-get update -y && sudo apt-get upgrade -y
sudo apt-get install -y git curl ca-certificates gnupg

# 2. Install Docker & Docker Compose plugin
echo "[2/5] Installing Docker..."
if ! command -v docker &> /dev/null; then
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg

    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    sudo apt-get update -y
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    sudo usermod -aG docker $USER
fi

# 3. Setup Project Directory
echo "[3/5] Setting up project..."
cd ~
if [ ! -d "Budget_Analysis_Rohit_Aman" ]; then
    git clone https://github.com/Amanarun2907/Budget_Analysis_Rohit_Aman.git
fi
cd Budget_Analysis_Rohit_Aman

# 4. Prompt for GROQ_API_KEY if not already set
if [ ! -f ".env" ]; then
    echo ""
    read -p "Enter your GROQ_API_KEY: " user_key
    if [ -z "$user_key" ]; then
        echo "Error: GROQ_API_KEY is required to run the AI engine."
        exit 1
    fi
    echo "GROQ_API_KEY=$user_key" > .env
    echo "LLM_MODEL=qwen/qwen3.8-27b" >> .env
fi

# 5. Build and launch container
echo "[4/5] Building and launching application on Port 80..."
sudo docker compose down || true
sudo docker compose up -d --build

echo "=========================================================="
echo "  Deployment Complete! "
echo "  Your application is now running live on Port 80."
echo "  Open http://<YOUR_EC2_PUBLIC_IP> in your browser!"
echo "=========================================================="
