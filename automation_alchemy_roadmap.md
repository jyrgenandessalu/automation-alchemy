# ⚙️ Automation Alchemy Roadmap

## 🧭 Part 1: Overview & Objectives
Automation Alchemy builds on the foundations of **Server Sorcery 101** and **Infrastructure Insight**. The goal is to transform a manually configured multi-server environment into a **fully automated infrastructure** using Infrastructure as Code (IaC) and Continuous Integration/Continuous Deployment (CI/CD) practices.

### 🎯 Project Goals
- Automate VM creation, configuration, and application deployment.
- Ensure idempotent infrastructure: every run produces the same result.
- Enable one-click provisioning using a single command.
- Integrate Jenkins for automated testing and deployment pipelines.
- Maintain readability and reproducibility for reviewers.

### 🔄 System Flow
**Windows Host → Vagrant → VirtualBox → Linux VMs → Ansible → Jenkins → App Deployment**

- Windows: your main workstation where you trigger automation.
- Vagrant: handles VM creation and provisioning.
- VirtualBox: runs your virtual machines.
- Ansible: configures the servers, installs software, deploys containers.
- Jenkins: builds, tests, and deploys automatically.

---

## 🛠️ Part 2: Tools & Their Roles

### 🧰 Core Tools
- **Vagrant:** automates the creation of VirtualBox VMs from code.
- **VirtualBox:** virtualization layer hosting your Linux servers.
- **Ansible:** configuration management and orchestration tool.
- **Docker:** containerization for consistent app deployment.
- **Jenkins:** automates testing, building, and deployment (CI/CD).

### 🪄 Why These Tools
- **Vagrant + VirtualBox**: portable and easy to replicate for reviewers.
- **Ansible**: agentless, simple YAML-based syntax.
- **Docker**: ensures application consistency.
- **Jenkins**: industry-standard CI/CD automation.

### 🧩 Reviewer Requirements
To run your automation, reviewers only need to install:
1. **VirtualBox**
2. **Vagrant**
3. **Git**
4. **Ansible** (via WSL or native Linux)

---

## 💻 Part 3: Environment Setup

### 🪟 On Windows Host
1. Install **VirtualBox** (latest version)
2. Install **Vagrant** from [vagrantup.com](https://developer.hashicorp.com/vagrant)
3. Install **Git Bash** or use **WSL2 (Ubuntu)**
4. Create your project folder:
   ```bash
   mkdir automation-alchemy && cd automation-alchemy
   ```

### 🐧 Inside WSL (Ubuntu)
Install dependencies:
```bash
sudo apt update && sudo apt install ansible sshpass -y
```

### 📁 Folder Structure
```
automation-alchemy/
│
├── Vagrantfile
├── ansible/
│   ├── inventory.ini
│   ├── site.yml
│   ├── roles/
│   │   ├── common/
│   │   ├── docker/
│   │   ├── nginx_lb/
│   │   ├── app_deploy/
│   │   └── jenkins/
├── scripts/
│   └── bootstrap.sh
├── Jenkinsfile
└── README.md
```

### ✅ Verification
Run:
```bash
vagrant --version
ansible --version
```
If both return versions, the environment is ready.

---

## 🧱 Part 4: Automation Design (Infrastructure as Code)

### 🖥️ Server Roles
| Server | Role |
|---------|------|
| lb-server | Load balancer (Nginx) |
| web1-server | Frontend container host |
| web2-server | Frontend container host |
| app-server | Backend application host |
| backup-server | Backup + logs |
| ci-server | Jenkins CI/CD host |

### 🧩 Example Vagrantfile
```ruby
Vagrant.configure("2") do |config|
  servers = [
    {name: "lb-server", ip: "192.168.56.20"},
    {name: "web1-server", ip: "192.168.56.21"},
    {name: "web2-server", ip: "192.168.56.22"},
    {name: "app-server", ip: "192.168.56.23"},
    {name: "backup-server", ip: "192.168.56.24"},
    {name: "ci-server", ip: "192.168.56.25"}
  ]

  servers.each do |srv|
    config.vm.define srv[:name] do |node|
      node.vm.box = "ubuntu/jammy64"
      node.vm.hostname = srv[:name]
      node.vm.network "private_network", ip: srv[:ip]
      node.vm.provider "virtualbox" do |vb|
        vb.memory = 1024
        vb.cpus = 1
      end
      node.vm.provision "ansible" do |ansible|
        ansible.playbook = "ansible/site.yml"
        ansible.inventory_path = "ansible/inventory.ini"
      end
    end
  end
end
```

### 🧾 Example Ansible Inventory
```ini
[loadbalancer]
192.168.56.20

[webservers]
192.168.56.21
192.168.56.22

[appserver]
192.168.56.23

[backup]
192.168.56.24

[ci]
192.168.56.25
```

### 🧰 Example Playbook (site.yml)
```yaml
- hosts: all
  become: true
  roles:
    - common

- hosts: webservers
  become: true
  roles:
    - docker
    - app_deploy

- hosts: loadbalancer
  become: true
  roles:
    - nginx_lb

- hosts: ci
  become: true
  roles:
    - jenkins
```

### ⚙️ Common Role Tasks Example
```yaml
# ansible/roles/common/tasks/main.yml
- name: Create devops user
  user:
    name: devops
    state: present
    groups: sudo
    append: yes

- name: Disable root SSH login
  lineinfile:
    path: /etc/ssh/sshd_config
    regexp: '^PermitRootLogin'
    line: 'PermitRootLogin no'
  notify: restart ssh
```

---

## 🚀 Part 5: CI/CD Implementation (Jenkins)

### 📦 Jenkins Setup via Ansible
```yaml
# ansible/roles/jenkins/tasks/main.yml
- name: Install dependencies
  apt:
    name: [openjdk-11-jdk, wget, gnupg]
    state: present

- name: Add Jenkins repository
  shell: |
    wget -q -O - https://pkg.jenkins.io/debian-stable/jenkins.io.key | sudo apt-key add -
    sudo sh -c 'echo deb http://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list'

- name: Install Jenkins
  apt:
    name: jenkins
    state: latest

- name: Start Jenkins
  service:
    name: jenkins
    state: started
    enabled: yes
```

### 🧩 Jenkinsfile
```groovy
pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/yourrepo/app.git'
            }
        }
        stage('Build') {
            steps {
                sh 'docker build -t myapp:latest .'
            }
        }
        stage('Test') {
            steps {
                sh 'docker run myapp:latest pytest'
            }
        }
        stage('Deploy') {
            steps {
                sh 'ansible-playbook -i ansible/inventory.ini ansible/deploy.yml'
            }
        }
    }
}
```

---

## 🪄 Part 6: One-Click Deployment

### ⚡ bootstrap.sh
```bash
#!/bin/bash

set -e

echo "[1/3] Destroying old VMs..."
vagrant destroy -f

echo "[2/3] Bringing up new VMs..."
vagrant up

echo "[3/3] Running Ansible Playbooks..."
ansible-playbook ansible/site.yml

echo "All systems up and running! Access the app via http://192.168.56.20"
```

### 🧠 What Happens
1. Vagrant creates all VMs in VirtualBox.
2. Ansible installs dependencies and deploys the app.
3. Jenkins comes online and monitors GitHub for changes.
4. The load balancer serves your containerized app.

You can rebuild from scratch at any time with:
```bash
./scripts/bootstrap.sh
```

---

## 🔍 Part 7: Validation & Testing

### ✅ Review Checklist (Key Points)
| Category | Validation Method |
|-----------|-------------------|
| Users & Security | `cat /etc/passwd` → shows `devops` user; `PermitRootLogin no` in sshd_config |
| Firewall | `sudo ufw status` shows active and configured rules |
| Docker | `docker ps` shows running app containers |
| Load Balancer | Access via `http://192.168.56.20` → forwards correctly |
| Jenkins | `http://192.168.56.15:8080` loads Jenkins dashboard |
| Backup | Check `/var/backups` or scheduled cron logs |

### 🧪 Idempotency Check
Run twice:
```bash
ansible-playbook ansible/site.yml
```
Second run should report `changed=0` on all tasks.

### 🧰 Troubleshooting Tips
- **SSH issue:** check `vagrant ssh-config`
- **VM not found:** ensure VirtualBox is open and running
- **Jenkins not starting:** check `sudo systemctl status jenkins`

---

## 📘 Part 8: Documentation Template

### README.md Outline
```
# Automation Alchemy

## Overview
This project automates a multi-server infrastructure using Vagrant, Ansible, Docker, and Jenkins.

## Quickstart
1. Install VirtualBox + Vagrant + Ansible.
2. Clone the repository.
3. Run `./scripts/bootstrap.sh`.

## Servers
- lb-server → Nginx Load Balancer
- web1/web2 → Frontend Containers
- app-server → Backend
- ci-server → Jenkins

## Access
- App: http://192.168.56.20
- Jenkins: http://192.168.56.15:8080

## Author
Your Name – 2025
```

---

### ✅ End State Summary
By the end of Automation Alchemy:
- Your entire infrastructure can be rebuilt with one command.
- All servers are provisioned, configured, and deployed automatically.
- Jenkins builds and redeploys upon Git updates.
- Reviewers can verify functionality in under 15 minutes.



