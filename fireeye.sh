#!/bin/bash
set -euo pipefail

# -----------------------------------------------
# Check if Trellix (xagt) is already installed
# -----------------------------------------------
echo "Checking if Trellix (xagt) is already installed..."

# Check if service is running
if systemctl is-active --quiet xagt; then
    echo "------------------------------"
    echo "Trellix (xagt) is already installed and running."
    echo "Skipping installation."
    echo "------------------------------"
    sudo systemctl status xagt --no-pager
    echo "------------------------------"
    echo "Execution is completed."
    echo "------------------------------"
    exit 0
fi

# Check if package is installed but service not running
if rpm -q xagt > /dev/null 2>&1; then
    echo "------------------------------"
    echo "Trellix (xagt) is already installed but service is not running."
    echo "Attempting to fix and start the service..."
    echo "------------------------------"
    
    # Fix and restart the service
    sudo systemctl daemon-reload
    sudo systemctl restart xagt
    sudo systemctl status xagt --no-pager
    if ! systemctl is-active --quiet xagt; then
        echo "xagt service restart failed; service is not active."
        exit 1
    fi
    
    echo "------------------------------"
    echo "Execution is completed."
    echo "------------------------------"
    exit 0
fi

# If not installed, proceed with installation
echo "Trellix (xagt) is NOT installed. Proceeding with installation..."
echo "------------------------------"

cd /home
mkdir -p /home/Fireeye/
cd /home/Fireeye/ || exit 1

# Replace extracted installer files if they exist.
rm -f xagt-36.30.37-1.sle12.x86_64.rpm
rm -f agent_config.json

if [ -f IMAGE_HX_AGENT_LINUX_36.30.37.tgz ]; then
    echo "Installer package already exists locally. Reusing it."
else
    echo "Copying file from Remote Machine"
    scp -o StrictHostKeyChecking=no root@10.211.27.74:/home/Fireeye/IMAGE_HX_AGENT_LINUX_36.30.37.tgz /home/Fireeye/ || {
        echo "Failed to copy installer package from remote machine."
        exit 1
    }
    echo "File downloaded"
fi

echo "Starting Fire Eye installation"
echo "------------------------------"
echo "Starting untar"
tar -zxf IMAGE_HX_AGENT_LINUX_36.30.37.tgz
echo "Untar is done"
echo "------------------------------"
 
#rpm -ihv --nodigest xagt-36.30.37-1.el7.x86_64.rpm
#only for ubuntu
#dpkg -i xagt_36.30.37-1.ubuntu16_amd64.deb
#for mxone
rpm -ihv --nodigest xagt-36.30.37-1.sle12.x86_64.rpm
echo "Xagent setup is completed"
echo "------------------------------"
sudo /opt/fireeye/bin/xagt -i agent_config.json
echo ".JSON is installed."
echo "------------------------------"
sudo systemctl start xagt
echo "XAGT AGENT is started"
echo "------------------------------"
sudo systemctl status xagt --no-pager
if ! systemctl is-active --quiet xagt; then
    echo "Installation finished but xagt service is not active."
    exit 1
fi
echo "------------------------------"
echo "Execution is completed."
echo "------------------------------"