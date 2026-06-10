# ==============================
# SERVER CONFIGURATION
# ==============================

# Excel file containing server details
# Columns: server ip | putty username | putty password | mxone root password
SERVERS_FILE = "mxone_system.xlsx"

# Local file to upload
LOCAL_FILE = "fireeye.sh"

# Remote destination
REMOTE_PATH = "/root"

# Execute after upload
RUN_SCRIPT = True



EMAIL_ENABLED=True
SMTP_SERVER=smtp.mitel.com
SMTP_PORT=587
SENDER_EMAIL=mekala.manikanta@mitel.com
SENDER_PASSWORD=Purushotham@2003
RECIPIENTS=mekala.manikanta@mitel.com

# MiXML Configuration
esm_PORT=443
esm_USE_PROXY=False
esm_PROXY_PORT=8080

