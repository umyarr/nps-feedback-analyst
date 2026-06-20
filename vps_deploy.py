import paramiko
import os
import sys

# Перенастройка кодировки на UTF-8 для корректного вывода в Windows
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

IP = os.environ.get("VPS_IP", "91.229.104.97")
USER = os.environ.get("VPS_USER", "root")
PASSWORD = os.environ.get("VPS_PASSWORD")

if not PASSWORD:
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("VPS_PASSWORD="):
                    PASSWORD = line.strip().split("=", 1)[1].strip().strip('"').strip("'")
LOCAL_DIR = r"C:\Users\user\Desktop\Projects\nps-feedback-analyst"
REMOTE_DIR = "/opt/nps-feedback-analyst"

def execute_cmd(client, cmd):
    print(f"Exec: {cmd}")
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='ignore')
    err = stderr.read().decode('utf-8', errors='ignore')
    if out:
        print(f"STDOUT:\n{out.strip()}")
    if err:
        print(f"STDERR:\n{err.strip()}")
    return stdout.channel.recv_exit_status()

def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    print(f"Connecting to {USER}@{IP}...")
    try:
        client.connect(IP, username=USER, password=PASSWORD, timeout=20, banner_timeout=45)
    except Exception as e:
        print(f"Connection failed: {e}")
        sys.exit(1)
        
    print("\n--- 1. Checking if pip and venv are installed on VPS ---")
    stdin, stdout, stderr = client.exec_command("which pip3 || which pip")
    has_pip = stdout.read().decode().strip()
    
    if not has_pip:
        print("pip is not installed. Installing pip and venv via apt-get (noninteractive)...")
        cmd = "export DEBIAN_FRONTEND=noninteractive && apt-get update && apt-get install -y -o Dpkg::Options::=\"--force-confdef\" -o Dpkg::Options::=\"--force-confold\" python3-pip python3-venv"
        execute_cmd(client, cmd)
    else:
        print("pip is already installed, skipping installation.")
    
    print("\n--- 2. Creating remote directories ---")
    execute_cmd(client, f"mkdir -p {REMOTE_DIR}")
    
    print("\n--- 3. Uploading files via SFTP ---")
    sftp = client.open_sftp()
    
    files_to_upload = [
        "analyze_feedback_secure.py",
        "nps_telegram_bot.py",
        "requirements.txt",
        "index.html",
        ".env"
    ]
    
    for f in files_to_upload:
        local_path = os.path.join(LOCAL_DIR, f)
        remote_path = f"{REMOTE_DIR}/{f}"
        if os.path.exists(local_path):
            print(f"Uploading {f} -> {remote_path}")
            sftp.put(local_path, remote_path)
        else:
            print(f"Warning: local file {local_path} not found, skipping.")
            
    sftp.close()
    
    print("\n--- 4. Creating virtual environment and installing dependencies ---")
    execute_cmd(client, f"python3 -m venv {REMOTE_DIR}/venv")
    execute_cmd(client, f"{REMOTE_DIR}/venv/bin/pip install --upgrade pip")
    execute_cmd(client, f"{REMOTE_DIR}/venv/bin/pip install -r {REMOTE_DIR}/requirements.txt")
    
    print("\n--- 5. Configuring systemd service ---")
    service_content = f"""[Unit]
Description=NPS Feedback Analyst Telegram Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory={REMOTE_DIR}
ExecStart={REMOTE_DIR}/venv/bin/python {REMOTE_DIR}/nps_telegram_bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
"""
    # Write service file on remote VPS
    sftp = client.open_sftp()
    service_file_path = "/etc/systemd/system/npsbot.service"
    print(f"Writing systemd service to {service_file_path}")
    with sftp.open(service_file_path, "w") as sf:
        sf.write(service_content)
    sftp.close()
    
    print("\n--- 6. Reloading systemd and starting service ---")
    execute_cmd(client, "systemctl daemon-reload")
    execute_cmd(client, "systemctl enable npsbot")
    execute_cmd(client, "systemctl restart npsbot")
    
    print("\n--- 7. Verifying service status ---")
    execute_cmd(client, "systemctl status npsbot")
    
    client.close()
    print("\nDeployment finished successfully!")

if __name__ == "__main__":
    main()
