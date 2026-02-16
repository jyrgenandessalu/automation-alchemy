# Automation Alchemy

Automated infrastructure provisioning and CI/CD pipeline setup using Vagrant, Ansible, Docker, Jenkins, and Gitea.

## Overview

This project automates the complete setup of a multi-server infrastructure with:
- **5 Virtual Machines**: Load Balancer, 2 Web Servers, App Server, Backup Server (Jenkins + Gitea)
- **Flask Application**: Containerized frontend and backend services
- **CI/CD Pipeline**: Automated deployment via Jenkins
- **Load Balancing**: Nginx distributing traffic across web servers
- **Security**: UFW firewall rules, SSH hardening, user management
- **Automated Backups**: Cron job for application backups

**Everything is fully automated - no manual intervention required!**

## Prerequisites

- **Vagrant** (2.2.0 or later)
- **VirtualBox** (6.0 or later)
- **Git** (to clone this repository)
- **8GB+ RAM** recommended (VMs use ~5GB total)
- **20GB+ free disk space**

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd automation-alchemy
   ```

2. **Start the infrastructure:**
   ```bash
   vagrant destroy -f  # Clean slate (optional, removes existing VMs)
   vagrant up          # Creates and provisions all VMs (~10-15 minutes)
   ```

3. **Wait for provisioning to complete** - The process will:
   - Create 5 VMs with proper networking
   - Install and configure all services (Nginx, Docker, Jenkins, Gitea)
   - Deploy the Flask application
   - Configure Jenkins CI/CD pipeline
   - Set up firewall rules and security settings
   - Configure automated backups

## Verify Everything Works

### 1. Test the Application
```bash
curl http://192.168.56.20/
```
Expected: `Hello from frontend on web1-server-auto! (containerized) ✅ Updated via CI/CD!`

### 2. Access Jenkins
- **URL:** http://192.168.56.24:8080
- **Username:** `admin`
- **Password:** `admin`

### 3. Test CI/CD Pipeline
1. Make a code change (e.g., edit `ansible/roles/frontend_container/files/app/app.py`)
2. Commit and push:
   ```bash
   git add .
   git commit -m "Test CI/CD"
   git push
   ```
3. Wait up to 1 minute for Jenkins to detect changes (SCM polling: every minute)
4. Check Jenkins build status at http://192.168.56.24:8080
5. Verify deployment: `curl http://192.168.56.20/`

## Infrastructure Details

### VM Configuration

| Server | IP Address | Role | Services |
|--------|------------|------|----------|
| `lb-server-auto` | 192.168.56.20 | Load Balancer | Nginx, Ansible Control Node |
| `web1-server-auto` | 192.168.56.21 | Web Server 1 | Docker (Flask Frontend) |
| `web2-server-auto` | 192.168.56.22 | Web Server 2 | Docker (Flask Frontend) |
| `app-server-auto` | 192.168.56.23 | App Server | Docker (Flask Backend) |
| `backup-server-auto` | 192.168.56.24 | Backup/CI/CD | Jenkins, Gitea |

### Network Architecture
- **Entry Point:** Load Balancer (192.168.56.20:80)
- **Web Servers:** Behind load balancer, direct access restricted
- **App Server:** Internal only, accessed by web servers
- **Backup Server:** Internal operations (Jenkins, Gitea)

## Documentation

- **`TESTING_GUIDE.md`** - Comprehensive guide for testing all 24 project requirements
- **`documentation.md`** - Detailed technical documentation
- **`manual-part.md`** - Quick reference guide

## Troubleshooting

### VMs won't start
- Ensure VirtualBox is installed and running
- Check that virtualization is enabled in BIOS
- Verify sufficient RAM/disk space available

### Application not accessible
- Wait a few minutes after `vagrant up` completes (services need time to start)
- Check VM status: `vagrant status`
- SSH into LB: `vagrant ssh lb-server-auto` and check Nginx: `sudo systemctl status nginx`

### Jenkins not accessible
- Wait 2-3 minutes after provisioning (Jenkins needs time to start)
- Check if port 8080 is accessible: `curl http://192.168.56.24:8080`
- SSH into backup server: `vagrant ssh backup-server-auto` and check: `sudo systemctl status jenkins`

### CI/CD not triggering
- Verify Jenkins job exists: http://192.168.56.24:8080/job/automation-alchemy/
- Check SCM polling is configured (should poll every minute)
- Ensure code is pushed to the repository
- Check Jenkins logs: `vagrant ssh backup-server-auto -c "sudo journalctl -u jenkins -n 50"`

## Clean Up

To remove all VMs and start fresh:
```bash
vagrant destroy -f
```

## Project Structure

```
automation-alchemy/
├── Vagrantfile              # VM definitions and provisioning
├── ansible/                  # Ansible playbooks and roles
│   ├── site.yml             # Main playbook
│   ├── inventory.ini        # Server inventory
│   └── roles/               # Ansible roles
│       ├── common/          # Common tasks (users, SSH, firewall)
│       ├── docker/          # Docker installation
│       ├── frontend_container/  # Frontend Flask app
│       ├── backend_container/   # Backend Flask app
│       ├── nginx_lb/        # Load balancer configuration
│       ├── jenkins/         # Jenkins setup
│       └── gitea/           # Gitea setup
├── Jenkinsfile              # Jenkins Pipeline as Code
└── TESTING_GUIDE.md         # Comprehensive testing guide
```

## License

[Add your license here]
