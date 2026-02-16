
# Automation Alchemy – Deployment Documentation

## Overview

This document records all steps completed to fully automate the creation and configuration of a multi-VM environment using **Vagrant**, **Ansible**, and a **Flask application** behind an **Nginx load balancer**.  
All actions are performed automatically through provisioning scripts — with no manual setup required.

---

## Step 1 – Environment Setup

1. All virtual machines are defined and provisioned via **Vagrant**.
2. Each VM receives a static IP and descriptive hostname.
3. The total environment consists of 5 machines:
   - `lb-server-auto` (Load Balancer + Ansible control node) – 192.168.56.20  
   - `web1-server-auto` – 192.168.56.21  
   - `web2-server-auto` – 192.168.56.22  
   - `app-server-auto` (Flask app) – 192.168.56.23  
   - `backup-server-auto` – 192.168.56.24

After running `vagrant up`, all machines are provisioned automatically and reachable within the private network.

---

## Step 2 – Ansible Configuration

Ansible is used for configuring all VMs.  
`lb-server-auto` acts as the control node and contains all Ansible playbooks and roles under `/vagrant/ansible/`.

### Inventory File
The inventory (`inventory.ini`) defines all groups and IP addresses for each host.

### Connection Test
To verify SSH access and configuration, the following command was executed on the load balancer VM:
```bash
ansible all -m ping -i /vagrant/ansible/inventory.ini
```
**Result:** All hosts returned `"ping": "pong"`, confirming passwordless SSH access and full connectivity.

---

## Step 3 – Base Role

All VMs share a **common** role that:
- Updates APT repositories
- Installs basic packages (`curl`, `vim`, `git`)
- Ensures consistent environment setup

This guarantees idempotency and baseline configuration for each machine.

---

## Step 4 – Load Balancer Configuration (Nginx)

Nginx is installed and configured automatically on `lb-server-auto` via the **nginx_lb** role.

### Configuration Summary
- Installs Nginx package
- Copies a proxy configuration that forwards requests to the application server (`192.168.56.23:5000`)
- Restarts the service

**Nginx config snippet:**
```nginx
upstream flask_app {
    server 192.168.56.23:5000;
}

server {
    listen 80;
    location / {
        proxy_pass http://flask_app;
    }
}
```

**Verification:**
Accessing `http://192.168.56.20` from the host machine displays:
```
Hello from Flask app server! Automated deployment successful.
```

---

## Step 5 – Flask Application Deployment

The Flask backend is deployed on the `app-server-auto` VM via the **app_deploy** role.

### Automated Tasks:
1. Installs Python 3 and pip.
2. Installs Flask using pip.
3. Creates the directory `/home/vagrant/flask_app/`.
4. Copies application files from the role to the target directory.
5. Defines a `systemd` service called `flask_app.service` to keep the Flask app running persistently.
6. Starts and enables the service.

### Flask App Code
```python
from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "Hello from Flask app server! Automated deployment successful."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### Verification Steps
**Service Status:**
```bash
sudo systemctl status flask_app
```
✅ Status shows: `active (running)`

**Local Curl Test:**
```bash
curl http://localhost:5000
```
✅ Output: `"Hello from Flask app server! Automated deployment successful."`

**Remote Curl Test:**
```bash
curl http://192.168.56.23:5000
```
✅ Output matches the same message.

---

## Step 6 – Backup Server Configuration

The `backup-server-auto` was provisioned with rsync to handle file synchronization or backup operations if needed.  
The role ensures rsync is installed and ready for future automation tasks.

---

## Step 7 – Idempotency Verification

After successful provisioning, idempotency was tested by re-running:
```bash
vagrant provision
```
✅ Result: All tasks completed without error; most reported as `"ok"`, indicating no redundant changes.

---

## Step 8 – End-to-End Validation

### Verification Table

| Test | Command | Result |
|------|----------|--------|
| Flask app running | `curl http://192.168.56.23:5000` | ✅ Hello message shown |
| Nginx forwarding | Visit `http://192.168.56.20` | ✅ Displays same Flask output |
| Persistent service | `sudo systemctl status flask_app` | ✅ Active (running) |
| SSH access | `ansible all -m ping -i /vagrant/ansible/inventory.ini` | ✅ All pong |
| Idempotency | `vagrant provision` | ✅ No changes detected |

---

## Step 9 – System Hardening Verification

This step focused on verifying the automated security configuration applied by the **common role** during provisioning. The main goals were to ensure that only necessary services are accessible, SSH access is secured, and all VMs follow consistent hardening policies.

### Firewall Configuration
All VMs were automatically configured with UFW (Uncomplicated Firewall). The rules allow only essential traffic:
- **22/tcp** – for SSH  
- **80/tcp** – for HTTP web traffic  
- **5000/tcp** – for the backend application  

All other incoming connections are denied by default.  
Verification was performed using:
```bash
sudo ufw status verbose
```

Status: active
Logging: on (low)
Default: deny (incoming), allow (outgoing), disabled (routed)
To                         Action      From
--                         ------      ----
22/tcp                     ALLOW       Anywhere
80/tcp                     ALLOW       Anywhere
5000/tcp                   ALLOW       Anywhere


### SSH Access Hardening

Root login is disabled (PermitRootLogin no).

Password authentication is disabled (PasswordAuthentication no).

Only the devops user can log in via SSH using public key authentication.

The devops user is part of the sudo group with password-protected sudo access.

Verification commands:

grep devops /etc/passwd
groups devops
sudo -l

### Secure Defaults

umask value set to 027 for all users, enforcing stricter file permissions.

All systems updated and upgraded automatically during provisioning.

Command used for validation:

sudo apt update && sudo apt list --upgradable


All systems returned 0 upgradable packages, confirming the update step executed successfully.

### Result
All five VMs (load balancer, two web servers, application server, and backup server) are hardened consistently through the automated provisioning process.
This verifies compliance with project requirements for:

Secure SSH configuration

Restricted external access

Consistent firewall and update enforcement

## Conclusion

The infrastructure is now fully automated and self-configuring:
- All VMs provision automatically via Vagrant.
- Ansible configures each system according to its role.
- Flask app deploys automatically and runs persistently.
- Nginx load balances and proxies traffic correctly.
- End-to-end connectivity verified successfully.

This environment can be recreated from scratch using a **single command**:
```bash
vagrant up
```
which handles the entire provisioning and deployment pipeline automatically.

## Step 10 – Extended Automation and Load Balancing

After confirming base functionality, new enhancements were implemented and verified:

### Multi-WebServer Load Balancing

Updated NGINX Configuration

- upstream flask_cluster {
    server 192.168.56.21:5000;
    server 192.168.56.22:5000;
}

server {
    listen 80;
    location / {
        proxy_pass http://flask_cluster;
    }
}


Now the load balancer forwards requests alternately between web1 and web2.

Verification:
Visiting http://192.168.56.20 multiple times returns alternating outputs:

Hello from web1! Automated deployment successful.
Hello from web2! Automated deployment successful.

Flask Application Service on Web Servers

Each web server hosts a Flask instance with a unique identifier message.
Both services are managed by systemd using the same configuration template.

Service Verification:

sudo systemctl status flask_app


✅ Shows active (running) on both web1 and web2.

Restarting the Service:

- sudo systemctl restart flask_app
- sudo systemctl status flask_app


✅ Service restarts cleanly without errors.

Idempotency Re-Test After Enhancements

Re-running:

vagrant provision


✅ No reconfiguration occurred.
All servers remained consistent, confirming full idempotency after extending to two web servers.

# Step 11 – Backup Automation and Jenkins Setup

## Objective
To automate backup operations between the backup server and web servers while setting up Jenkins for future CI/CD pipeline integration. This ensures scheduled, passwordless backups of deployed applications and prepares the environment for automated builds and deployments.

## Tools Used
- **Ansible** – for automating setup and configuration
- **rsync** – for incremental backups between servers
- **SSH key authentication** – for secure, passwordless communication
- **cron** – for scheduled backup tasks
- **Jenkins** – for CI/CD automation setup

## Implementation Details

### 1. Dependencies Installation
The playbook installs all required packages for both backup automation and Jenkins operation:
```yaml
apt:
  name:
    - openjdk-17-jdk
    - rsync
    - curl
  state: present
  update_cache: yes
```

### 2. Jenkins Installation
The Jenkins repository is added, GPG key imported, and Jenkins installed with the following tasks:
- Added Jenkins GPG key and repository
- Installed Jenkins package
- Enabled and started the Jenkins service
- Allowed port 8080 via UFW

Verification command:
```bash
sudo systemctl status jenkins
```
Expected output:
```
Active: active (running)
```
Access Jenkins via browser:
```
http://192.168.56.24:8080
```
Unlock using:
```bash
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

### 3. SSH Trust Establishment
The backup server’s `devops` SSH key was distributed to both web servers to allow passwordless rsync:
```bash
ssh-copy-id devops@192.168.56.21
ssh-copy-id devops@192.168.56.22
```
This step ensures automation works without manual password prompts.

### 4. Backup Automation Setup
A custom Ansible playbook creates a local backup directory and installs a reusable backup script:
```bash
/usr/local/bin/backup_web_servers.sh
```
Script content:
```bash
#!/bin/bash
set -euo pipefail
TIMESTAMP=$(date +%F-%H-%M-%S)
mkdir -p /backup/$TIMESTAMP/web1 /backup/$TIMESTAMP/web2
rsync -az --delete devops@192.168.56.21:/home/devops/flask_app/ /backup/$TIMESTAMP/web1/
rsync -az --delete devops@192.168.56.22:/home/devops/flask_app/ /backup/$TIMESTAMP/web2/
```

### 5. Scheduling Daily Backups
A cron job was created to run the backup script daily at 02:00:
```bash
sudo crontab -u devops -l
```
Output:
```
#Ansible: Daily backup of web servers
0 2 * * * /usr/local/bin/backup_web_servers.sh
```

### 6. Verification
Manual backup verification confirmed success:
```bash
sudo ls /backup/$(ls /backup | tail -n 1)/web1
sudo ls /backup/$(ls /backup | tail -n 1)/web2
```
Output:
```
app.py
```
This confirms rsync correctly mirrors each web server’s Flask app into timestamped directories.

## Result
✅ Jenkins successfully installed and running on the backup server
✅ Passwordless SSH access established between backup and web servers
✅ Automated rsync-based backups are functioning and verified
✅ Daily backup schedule set via cron

---

# Step 12 – Containerized Deployment and Environment Variable Integration
## Objective

To containerize both frontend and backend Flask applications using Docker and deploy them automatically with Ansible, ensuring dynamic environment variables (ROLE and HOST_VM) correctly identify each VM within the containerized environment.

## Tools Used

Docker – for containerizing Flask applications

Ansible – for automated image build and container deployment

Flask – for serving frontend and backend apps with metrics endpoints

Implementation Details
### 1. Dockerfiles

Each container role (frontend_container, backend_container) includes a Dockerfile copied by Ansible to build the image:

FROM python:3.9-slim
WORKDIR /app
COPY app/ /app/
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
CMD ["python", "/app/app.py"]

### 2. Flask Application

Both frontend and backend app.py files were updated to prefer HOST_VM for identifying the host machine instead of the container ID:

from flask import Flask, jsonify
import socket, os, psutil

app = Flask(__name__)

@app.route("/")
def home():
    role = os.getenv("ROLE", "unknown")
    host = os.getenv("HOST_VM", socket.gethostname())
    return f"Hello from {role} on {host}! (containerized) ✅"

@app.route("/metrics")
def metrics():
    mem = psutil.virtual_memory()
    cpu = psutil.cpu_percent(interval=0.2)
    return jsonify({
        "hostname": os.getenv("HOST_VM", socket.gethostname()),
        "role": os.getenv("ROLE", "unknown"),
        "cpu_percent": cpu,
        "memory_percent": mem.percent
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

### 3. Ansible Tasks

Each container role performs the following steps automatically:

Installs Docker and Python dependencies

Copies Dockerfile and Flask app files

Builds the Docker image (flask-frontend or flask-backend)

Runs the container with environment variables:

environment:
  ROLE: "frontend"
  HOST_VM: "{{ inventory_hostname }}"
ports:
  - "5000:5000"
restart_policy: always

### 4. Verification

After provisioning (vagrant provision):

vagrant ssh web1-server-auto
```bash
curl http://localhost:5000/
```

✅ Output:

Hello from frontend on web1-server-auto! (containerized) ✅


and metrics endpoint:

{"hostname": "web1-server-auto", "role": "frontend", ...}

### 5. Load Balancer Test

NGINX on lb-server-auto correctly distributes traffic between the two frontend containers:

vagrant ssh lb-server-auto
curl http://localhost/


Repeated requests alternate between:

- Hello from frontend on web1-server-auto! (containerized) ✅
- Hello from frontend on web2-server-auto! (containerized) ✅

### 6. Result

✅ Both frontend and backend applications are fully containerized
✅ Environment variables accurately reflect the VM hostname
✅ Ansible provisioning remains idempotent
✅ Load balancing verified across frontend containers

# Step 13 – CI/CD Pipeline

## Objective

To implement a fully automated CI/CD pipeline using Jenkins that monitors the Git repository for changes, builds Docker images, and deploys updated applications to web and application servers without manual intervention.

## Tools Used

- **Jenkins** – CI/CD automation server running on backup-server-auto
- **Git** – Source code repository (Gitea)
- **Ansible** – Deployment automation
- **Docker** – Container image building
- **Jenkinsfile** – Pipeline as Code definition

## Implementation Details

### 1. Jenkins Installation and Configuration

Jenkins is automatically installed on `backup-server-auto` (192.168.56.24) during provisioning via the **jenkins** Ansible role:

- Installs OpenJDK 17 and Jenkins package
- Enables and starts Jenkins service
- Opens port 8080 in UFW firewall
- Configures SSH key authentication for Jenkins user

**Access Jenkins:**
```
http://192.168.56.24:8080
```
Default credentials: `admin` / `admin` (initial password from `/var/lib/jenkins/secrets/initialAdminPassword`)

### 2. Jenkins Job Configuration

A Jenkins job named `automation-alchemy` is automatically created with:

- **SCM Polling:** Checks Git repository every 2 minutes (`H/2 * * * *`)
- **Source Code Management:** Connects to Gitea repository
- **Pipeline Definition:** Uses `Jenkinsfile` from repository root

**Job Configuration File:**
Located at `ansible/roles/jenkins/files/job_config.xml`, automatically deployed during provisioning.

### 3. Pipeline Stages

The `Jenkinsfile` defines three main stages:

#### Stage 1: Checkout
- Checks out source code from Git repository
- Verifies repository connection

#### Stage 2: Build
- Ensures Ansible is installed on Jenkins server
- Prepares deployment environment

#### Stage 3: Deploy
- Sets up SSH key authentication for Jenkins user
- Ensures correct permissions on SSH keys (600 for private key, 644 for public key)
- Runs Ansible playbook to deploy to web and app servers:
  ```bash
  ansible-playbook -i inventory.ini site.yml --limit web,app
  ```

### 4. SSH Key Setup for Jenkins

The pipeline automatically configures SSH keys for the Jenkins user to enable passwordless deployment:

**Key Setup Process:**
1. Creates `/var/lib/jenkins/.ssh` directory with proper permissions (700)
2. Copies SSH private key from load balancer or generates if missing
3. Sets correct ownership (`jenkins:jenkins`) and permissions (600)
4. Regenerates public key from private key to ensure matching key pair
5. Adds public key to authorized_keys on target servers (web1, web2, app)

**Verification:**
```bash
ls -la /var/lib/jenkins/.ssh/
```
Expected output shows:
- `id_ed25519` (600 permissions, jenkins:jenkins owner)
- `id_ed25519.pub` (644 permissions, jenkins:jenkins owner)

### 5. Docker Image Rebuilding

The deployment process ensures Docker images are rebuilt on every deployment:

- **Force Rebuild:** `force_source: true` parameter in Ansible Docker tasks
- **Image Build:** Docker images are rebuilt from source code on each pipeline run
- **Container Deployment:** Old containers are stopped and new ones started with updated code

### 6. Pipeline Workflow

**Complete CI/CD Flow:**

1. **Code Change:** Developer commits and pushes changes to Git repository
2. **SCM Polling:** Jenkins detects changes within 2 minutes
3. **Pipeline Trigger:** Jenkins automatically starts the build
4. **Checkout:** Latest code is checked out from repository
5. **Build:** Environment is prepared (Ansible, SSH keys verified)
6. **Deploy:** Ansible playbook deploys updated code to:
   - Frontend containers on web1-server-auto and web2-server-auto
   - Backend container on app-server-auto
7. **Verification:** Containers restart with new code

### 7. Testing the CI/CD Pipeline

**Manual Test Procedure:**

1. Make a code change (e.g., edit `ansible/roles/frontend_container/files/app/app.py`)
2. Commit and push:
   ```bash
   git add .
   git commit -m "Test CI/CD deployment"
   git push
   ```
3. Wait up to 2 minutes for Jenkins to detect changes
4. Monitor Jenkins build:
   - Access: `http://192.168.56.24:8080`
   - Navigate to `automation-alchemy` job
   - View build logs in real-time
5. Verify deployment:
   ```bash
   curl http://192.168.56.20/
   ```
   Or open `http://192.168.56.20` in browser to see updated application

**Expected Result:**
- Jenkins build completes successfully
- Application displays updated content (e.g., "Updated via CI/CD!" message)
- Load balancer distributes traffic across updated frontend containers

### 8. Pipeline Logs and Monitoring

**Viewing Build Logs:**
- Jenkins UI: `http://192.168.56.24:8080/job/automation-alchemy/`
- Console Output shows:
  - Git checkout status
  - SSH key setup verification
  - Ansible playbook execution
  - Docker build and deployment steps

**Success Indicators:**
- ✅ All pipeline stages complete without errors
- ✅ Ansible tasks show "changed" or "ok" status
- ✅ Docker containers restart successfully
- ✅ Application responds with updated content

### 9. Idempotency in CI/CD

The pipeline maintains idempotency:
- SSH key setup tasks check existing keys before modification
- Ansible playbooks are idempotent by design
- Docker image builds use `force_source: true` to ensure fresh builds
- Container deployment stops existing containers before starting new ones

### 10. Error Handling

The pipeline includes robust error handling:
- SSH key permission verification with explicit error messages
- Ansible playbook execution with verbose output (`-v` flag)
- Container status verification after deployment
- Build failure notifications in Jenkins UI

## Result

✅ Jenkins CI/CD pipeline fully automated and operational
✅ Automatic code deployment on Git repository changes
✅ SSH key authentication configured for passwordless deployment
✅ Docker images rebuilt and containers redeployed on each change
✅ End-to-end automation from code commit to live deployment
✅ Pipeline logs available for monitoring and troubleshooting

The entire CI/CD process runs automatically without manual intervention, demonstrating full automation from source code changes to production deployment.