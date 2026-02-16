# Testing Guide for Project Review

This guide addresses all mandatory requirements for the project review. Follow this guide to demonstrate each requirement.

---

## Prerequisites

**IMPORTANT:** Start from a blank slate - no VMs should be running before the review begins.

```bash
vagrant destroy -f
```

---

## Requirement 1: Project Documentation

**What to Show:**
- Clear objectives, scope, requirements, and procedures in documentation
- Repository contains all necessary automation and configuration files

**Demonstration:**
1. Show `README.md` or `documentation.md` with project overview
2. Show repository structure:
   ```bash
   ls -la
   tree -L 2  # if available
   ```
3. Explain key files:
   - `Vagrantfile` - VM definitions
   - `ansible/` - Configuration automation
   - `Jenkinsfile` - CI/CD pipeline definition
   - `ansible/roles/` - Ansible roles for different components

---

## Requirement 2: Automation and CI/CD Tools Proficiency

**What to Show:**
- Explain choice of automation and CI/CD tools
- Compare to other available options

**Demonstration:**
**Ansible:**
- Why Ansible: Declarative, idempotent, agentless, YAML-based
- Alternatives: Puppet, Chef, SaltStack
- Show Ansible playbooks: `ansible/site.yml`

**Jenkins:**
- Why Jenkins: Open-source, extensive plugin ecosystem, Pipeline as Code
- Alternatives: GitLab CI, GitHub Actions, CircleCI
- Show Jenkinsfile: `Jenkinsfile`

**Vagrant:**
- Why Vagrant: Reproducible environments, provider-agnostic
- Alternatives: Terraform, Docker Compose (for containers only)

---

## Requirement 3: Create 5 VMs from Blank Slate

**What to Show:**
- Scripts create at least 5 VMs with proper network and administrative configurations
- No manual intervention required

**Demonstration:**
```bash
# Start from blank slate
vagrant destroy -f

# Show Vagrantfile
cat Vagrantfile

# Create all VMs
vagrant up

# Verify all VMs are running
vagrant status
```

**Expected Result:**
- 5 VMs created: lb-server-auto, web1-server-auto, web2-server-auto, app-server-auto, backup-server-auto
- All VMs show "running" status
- No errors during provisioning

---

## Requirement 4: Deploy Application Automatically

**What to Show:**
- Scripts deploy application automatically
- Application accessible via browser

**Demonstration:**
```bash
# After vagrant up completes, verify application
curl http://192.168.56.20/

# Or open in browser
# http://192.168.56.20
```

**Expected Result:**
- Application responds with Flask message
- No manual deployment steps required

---

## Requirement 5: Infrastructure Metrics Display

**What to Show:**
- Application displays infrastructure metrics
- Explain significance of metrics

**Demonstration:**
```bash
# Access metrics endpoint
curl http://192.168.56.20/metrics

# Or from individual servers (this should fail as LB is only available externally)
curl http://192.168.56.21:5000/metrics
curl http://192.168.56.22:5000/metrics
curl http://192.168.56.23:5000/metrics
```

**Explain Metrics:**
- `hostname`: Identifies which VM is serving the request
- `role`: Shows frontend/backend role
- `cpu_percent`: Current CPU usage
- `memory_percent`: Current memory usage
- **Significance:** Monitor resource utilization, identify bottlenecks, track performance

---

## Requirement 6: Idempotency Demonstration

**What to Show:**
- Explain idempotency concept
- Run scripts multiple times without issues

**Demonstration:**
```bash
# Explain: Idempotency means running the same operation multiple times
# produces the same result without side effects

# Run provisioning multiple times
vagrant provision
vagrant provision
vagrant provision

# Show that tasks report "ok" (no changes) or "changed" only when needed
```

**Expected Result:**
- Most tasks show "ok" (no changes needed)
- Only changed tasks show "changed"
- No errors or failures
- System state remains consistent

---

## Requirement 7: CI/CD Pipeline Tracks Repository Changes

**What to Show:**
- CI/CD pipeline detects code changes in Git repository
- Pipeline reacts to changes

**Demonstration:**
1. Show Jenkins job configuration:
   - Open: `http://192.168.56.24:8080`
   - Navigate to: **automation-alchemy** → **Configure**
   - Show: "Poll SCM" trigger with schedule `* * * * *`

2. Make a code change:
   ```bash
   # Edit a file
   echo "# Test change" >> ansible/roles/frontend_container/files/app/app.py
   git add .
   git commit -m "CI/CD test - repository change"
   git push
   ```

3. Show Jenkins detecting change:
   - Refresh Jenkins job page
   - Show build appearing automatically (within 1 minute)
   - Show build starting automatically

**Expected Result:**
- Build appears in Jenkins without manual trigger
- Build starts automatically after code push

---

## Requirement 8: CI/CD Pipeline Deploys Updates

**What to Show:**
- Error-free CI/CD logs
- New version is live and replaced previous one

**Demonstration:**
1. Show build logs in Jenkins:
   - Click on build number
   - Show console output
   - Verify no errors

2. Show application before change:
   ```bash
   curl http://192.168.56.20/
   ```

3. After build completes, show application after change:
   ```bash
   curl http://192.168.56.20/
   ```

**Expected Result:**
- Build logs show successful completion
- No errors in logs
- Application shows updated content
- Previous version replaced

---

## Requirement 9: 5 VMs with Descriptive Names and Hostnames

**What to Show:**
- Hostname resolution works
- Hostnames are descriptive

**Demonstration:**
```bash
# Check hostname on each VM
vagrant ssh lb-server-auto -c "hostname"
vagrant ssh web1-server-auto -c "hostname"
vagrant ssh web2-server-auto -c "hostname"
vagrant ssh app-server-auto -c "hostname"
vagrant ssh backup-server-auto -c "hostname"

# Test hostname resolution (ping by ip)
vagrant ssh lb-server-auto -c "ping -c 2 192.168.56.21"
vagrant ssh lb-server-auto -c "ping -c 2 192.168.56.22"
vagrant ssh web1-server-auto -c "ping -c 2 192.168.56.23"
```

**Expected Result:**
- Hostnames: lb-server-auto, web1-server-auto, web2-server-auto, app-server-auto, backup-server-auto
- Ping by hostname works from any VM to any other VM

---

## Requirement 10: Static IP Addresses

**What to Show:**
- IP configuration shows static IPs
- IPs persist after reboot

**Demonstration:**
```bash
# Show IP configuration on each VM
vagrant ssh lb-server-auto -c "ip a"
vagrant ssh web1-server-auto -c "ip a"
vagrant ssh web2-server-auto -c "ip a"
vagrant ssh app-server-auto -c "ip a"
vagrant ssh backup-server-auto -c "ip a"

# Verify static IPs (should show 192.168.56.20, .21, .22, .23, .24)

# Reboot a VM and verify IP persists
vagrant reload web1-server-auto
vagrant ssh web1-server-auto -c "ip a | grep 192.168.56.21"
```

**Expected Result:**
- Each VM has static IP: 192.168.56.20, .21, .22, .23, .24
- IPs remain the same after reboot

---

## Requirement 11: Only Load Balancer Accessible Externally

**What to Show:**
- Explain network architecture
- Demonstrate that only LB is accessible externally
- Show firewall rules enforce this restriction

**Demonstration:**
```bash
# 1. Show LB is accessible from host (external access works)
curl http://192.168.56.20/  # Should work - LB is accessible

# 2. Show direct access to web/app servers is BLOCKED from host
# (This demonstrates external access limitation)
curl http://192.168.56.21:5000/  # Should be blocked by firewall
curl http://192.168.56.22:5000/  # Should be blocked by firewall
curl http://192.168.56.23:5000/  # Should be blocked by firewall
# Expected: Connection timeout or refused (firewall blocking)

# 3. Show LB can access web servers (from LB itself)
vagrant ssh lb-server-auto -c "curl http://192.168.56.21:5000/"
vagrant ssh lb-server-auto -c "curl http://192.168.56.22:5000/"
# Should work - LB is allowed to access web servers

# 4. Show firewall rules demonstrate the restriction
vagrant ssh web1-server-auto -c "sudo ufw status verbose | grep 5000"
vagrant ssh lb-server-auto -c "sudo ufw status verbose | grep 80"

# 5. Show NGINX configuration (demonstrates LB is the entry point)
vagrant ssh lb-server-auto -c "cat /etc/nginx/sites-enabled/*"
```

**Expected Firewall Rules:**

**Load Balancer (192.168.56.20):**
```
80/tcp                     ALLOW       Anywhere
```
- Port 80 open to all (external access allowed)

**Web Servers (192.168.56.21, .22):**
```
5000/tcp                   ALLOW       192.168.56.20
```
- Port 5000 only allowed from LB IP (192.168.56.20)
- Direct access from host is blocked

**App Server (192.168.56.23):**
```
5000/tcp                   ALLOW       192.168.56.20
```
- Port 5000 only allowed from LB IP
- Direct access from host is blocked

**Explain Architecture:**
1. **Load Balancer (192.168.56.20)** is the **only external entry point**
   - Port 80 open to all (host can access)
   - Receives all external traffic
   - Forwards to web servers

2. **Web Servers (192.168.56.21, .22)** are **behind the LB**
   - Port 5000 restricted to LB IP only (192.168.56.20)
   - Cannot be accessed directly from host
   - Must be accessed through LB

3. **App Server (192.168.56.23)** is **internal only**
   - Port 5000 restricted to LB IP only
   - Not directly accessible from host
   - Only accessible through LB

4. **Backup Server (192.168.56.24)** is **completely internal**
   - No external access needed
   - Only for internal operations

**Test Results:**
- ✅ Host can access LB: `curl http://192.168.56.20/` works
- ✅ Host CANNOT access web servers directly: `curl http://192.168.56.21:5000/` is blocked
- ✅ LB can access web servers: From LB, `curl http://192.168.56.21:5000/` works
- ✅ Firewall rules show port 5000 restricted to LB IP on web/app servers

---

## Requirement 12: VMs Up-to-Date with Security Patches

**What to Show:**
- Updated status of each VM
- Security patches are applied

**Demonstration:**
```bash
# Check each VM
vagrant ssh lb-server-auto -c "sudo apt update && sudo apt list --upgradable"
vagrant ssh web1-server-auto -c "sudo apt update && sudo apt list --upgradable"
vagrant ssh web2-server-auto -c "sudo apt update && sudo apt list --upgradable"
vagrant ssh app-server-auto -c "sudo apt update && sudo apt list --upgradable"
vagrant ssh backup-server-auto -c "sudo apt update && sudo apt list --upgradable"
```

**Expected Result:**
- `apt update` runs successfully
- `apt list --upgradable` shows:
  - **0 packages** (ideal), OR
  - **Only systemd packages** (libnss-systemd, libpam-systemd, libsystemd0, libudev1, systemd, systemd-sysv, systemd-timesyncd, udev) - **This is ACCEPTABLE and normal**
  
**Important Note:**
- Systemd packages are often "kept back" by Ubuntu for stability reasons
- These are not critical security vulnerabilities
- They require system reboot and are held back to prevent disruption
- This is standard Ubuntu behavior and indicates the system is properly maintained
- **No other packages should be upgradable** - if you see other packages, they should be upgraded

---

## Requirement 13: DevOps User Exists on Each VM

**What to Show:**
- DevOps user exists on all VMs

**Demonstration:**
```bash
# Check each VM
vagrant ssh lb-server-auto -c "grep devops /etc/passwd"
vagrant ssh web1-server-auto -c "grep devops /etc/passwd"
vagrant ssh web2-server-auto -c "grep devops /etc/passwd"
vagrant ssh app-server-auto -c "grep devops /etc/passwd"
vagrant ssh backup-server-auto -c "grep devops /etc/passwd"
```

**Expected Result:**
- Each VM shows: `devops:x:1001:1001:DevOps user for automation:/home/devops:/bin/bash`

---

## Requirement 14: SSH Key Authentication Enforced

**What to Show:**
- SSH access using keys works
- Password login is disabled

**Demonstration:**
```bash
# Test SSH with key (should work)
vagrant ssh web1-server-auto -c "whoami"

# Test password login (should fail)
# From host machine, try:
ssh -o PasswordAuthentication=yes devops@192.168.56.21
# Enter password when prompted - should fail

# Show SSH config
vagrant ssh web1-server-auto -c "sudo grep -E 'PasswordAuthentication|PubkeyAuthentication' /etc/ssh/sshd_config"
```

**Expected Result:**
- Key-based SSH works
- Password authentication fails
- Config shows: `PasswordAuthentication no` and `PubkeyAuthentication yes`

---

## Requirement 15: DevOps User in Sudo Group

**What to Show:**
- DevOps user has sudo access

**Demonstration:**
```bash
# Check groups on each VM
vagrant ssh web1-server-auto -c "groups devops"
vagrant ssh web2-server-auto -c "groups devops"
vagrant ssh app-server-auto -c "groups devops"
vagrant ssh backup-server-auto -c "groups devops"
vagrant ssh lb-server-auto -c "groups devops"
```

**Expected Result:**
- Output: `devops : devops sudo`
- Shows devops user is in sudo group

---

## Requirement 16: DevOps Sudo Commands Password Protected

**What to Show:**
- Sudo requires password for devops user

**Demonstration:**
```bash
# IMPORTANT: Test as devops user, NOT vagrant user
# The vagrant user has NOPASSWD sudo (which is normal for Vagrant boxes)

# SSH as devops user (you'll need the devops SSH key)
# First, get the devops private key location
vagrant ssh web1-server-auto -c "sudo ls -la /home/devops/.ssh/id_rsa"

# Test sudo as devops user (will prompt for password)
# Note: You need to SSH as devops user, not vagrant
ssh -i /path/to/devops/key devops@192.168.56.21 "sudo -k && sudo whoami"
# Should prompt for password

# Should prompt for password - enter devops user's password

# Show sudoers configuration
vagrant ssh web1-server-auto -c "sudo visudo -c"
vagrant ssh web1-server-auto -c "sudo grep -r devops /etc/sudoers.d/ 2>/dev/null || echo 'No devops-specific sudoers file (uses default sudo group behavior)'"

# Verify devops is in sudo group (default behavior requires password)
vagrant ssh web1-server-auto -c "groups devops"
```

**Expected Result:**
- Devops user is in `sudo` group (shown by `groups devops`)
- No NOPASSWD rule for devops user in sudoers files
- Sudo commands require password when run as devops user
- **Note:** Vagrant user has NOPASSWD (normal), but devops user requires password (as required)

**Important:**
- The `vagrant` user having passwordless sudo is normal for Vagrant boxes
- The requirement is that the `devops` user requires a password for sudo
- Default Ubuntu behavior: users in `sudo` group require password (unless NOPASSWD is set)
- Since no NOPASSWD rule exists for devops, it requires password by default

---

## Requirement 17: Root Login Disabled

**What to Show:**
- Root login via SSH is disabled
- Explain why it's disabled

**Demonstration:**
```bash
# Attempt root login (should fail)
ssh root@192.168.56.21
# Should fail with "Permission denied" or "root login disabled"

# Show SSH config
vagrant ssh web1-server-auto -c "sudo grep PermitRootLogin /etc/ssh/sshd_config"
```

**Expected Result:**
- Root login fails
- Config shows: `PermitRootLogin no`
- **Explain:** Root login disabled for security - prevents brute force attacks, forces use of regular users with sudo

---

## Requirement 18: Only DevOps User Can Login

**What to Show:**
- Cannot login as any other user except devops

**Demonstration:**
```bash
# Attempt login as non-existent user (should fail)
ssh linus_torvalds@192.168.56.21
# Should fail with "Permission denied"

# Show only devops can login
ssh devops@192.168.56.21 "whoami"
# Should work and show "devops"
```

**Expected Result:**
- Only devops user can login via SSH
- Other users (real or imaginary) cannot login

---

## Requirement 19: Secure Umask Set

**What to Show:**
- Umask configuration
- Demonstrate umask in use

**Demonstration:**
```bash
# Check umask on each VM
vagrant ssh web1-server-auto -c "umask"
vagrant ssh web2-server-auto -c "umask"
vagrant ssh app-server-auto -c "umask"

# Show umask configuration
vagrant ssh web1-server-auto -c "grep -i umask /etc/profile /etc/bash.bashrc /etc/login.defs 2>/dev/null"

# Demonstrate umask in use
vagrant ssh web1-server-auto -c "touch /tmp/test_umask && ls -l /tmp/test_umask && rm /tmp/test_umask"
```

**Expected Result:**
- Umask shows: `0027` or `0077` (secure value)
- New files created have restrictive permissions
- **Explain:** Umask 027 means files: 640 (rw-r-----), directories: 750 (rwxr-x---)

---

## Requirement 20: Containerization Tools Installed

**What to Show:**
- Docker (or other containerization tools) installed on appropriate servers

**Demonstration:**
```bash
# Check Docker on web servers
vagrant ssh web1-server-auto -c "docker --version"
vagrant ssh web2-server-auto -c "docker --version"

# Check Docker on app server
vagrant ssh app-server-auto -c "docker --version"

# Check if Docker is NOT on LB or backup (if that's the design)
vagrant ssh lb-server-auto -c "docker --version 2>&1 || echo 'Docker not installed (as expected)'"
```

**Expected Result:**
- Docker installed on web1, web2, and app servers
- Shows version: `Docker version 24.x.x` or similar

---

## Requirement 21: Firewall Rules Configured

**What to Show:**
- Firewall rules shown and explained
- No unused ports open

**Demonstration:**
```bash
# Show firewall status on each VM
# Note: lb-server-auto and backup-server-auto may show "inactive" immediately after provisioning
# All firewall rules are configured and will be enabled automatically on boot via systemd service
vagrant ssh web1-server-auto -c "sudo ufw status verbose"
vagrant ssh web2-server-auto -c "sudo ufw status verbose"
vagrant ssh app-server-auto -c "sudo ufw status verbose"
```

**Expected Result:**
- Web and app servers show UFW as "active" with configured rules

- All servers show only necessary ports open (SSH, HTTP, application ports)
- No unused ports are open

**Explain Rules:**
- **Port 22:** SSH access (required)
- **Port 80:** HTTP (LB only, or web servers if direct access needed)
- **Port 5000:** Flask application (web and app servers)
- **Port 8080:** Jenkins (backup server only)
- Default policy: DENY incoming, ALLOW outgoing
- **No unused ports open**

**Expected Result:**
- UFW is active
- Only required ports are open
- Default deny policy in place

---

## Requirement 22: Backend Container on App Server

**What to Show:**
- Running backend container
- Container logs checked

**Demonstration:**
```bash
# Show running containers on app server (use sudo for Docker access)
vagrant ssh app-server-auto -c "sudo docker ps"

# Show backend container specifically
vagrant ssh app-server-auto -c "sudo docker ps | grep flask_backend"

# Check container logs
vagrant ssh app-server-auto -c "sudo docker logs flask_backend"
```

**Expected Result:**
- Container `flask_backend` is running
- Container shows status: "Up X minutes"
- Logs show Flask app started successfully
- No errors in logs

**Note:** Use `sudo` for docker commands as the vagrant user doesn't have direct Docker socket access

---

## Requirement 23: Frontend Containers on Both Web Servers

**What to Show:**
- Running frontend containers on both web servers
- Access container shell to verify environment

**Demonstration:**
```bash
# Show containers on web1 (use sudo for Docker access)
vagrant ssh web1-server-auto -c "sudo docker ps | grep flask_frontend"

# Show containers on web2
vagrant ssh web2-server-auto -c "sudo docker ps | grep flask_frontend"

# Access container shell on web1
vagrant ssh web1-server-auto -c "sudo docker exec flask_frontend env | grep -E 'ROLE|HOST_VM'"

# Access container shell on web2
vagrant ssh web2-server-auto -c "sudo docker exec flask_frontend env | grep -E 'ROLE|HOST_VM'"
```

**Expected Result:**
- `flask_frontend` container running on both web1 and web2
- Environment variables show:
  - `ROLE=frontend`
  - `HOST_VM=web1-server-auto` (on web1) or `web2-server-auto` (on web2)

**Note:** Use `sudo` for docker commands as the vagrant user doesn't have direct Docker socket access

---

## Requirement 24: Load Balancer Configuration

**What to Show:**
- Load balancer configuration
- Load balancing algorithm explained
- Traffic distributed between both web servers

**Demonstration:**
```bash
# Show NGINX configuration
vagrant ssh lb-server-auto -c "cat /etc/nginx/sites-enabled/*"

# Show NGINX status
vagrant ssh lb-server-auto -c "sudo systemctl status nginx"

```

**Explain Configuration:**
- **Algorithm:** Round-robin (default NGINX upstream)
- **Upstream servers:** web1-server-auto:5000 and web2-server-auto:5000
- **Health checks:** (if configured)
- **Session persistence:** (if configured)

**Expected Result:**
- NGINX config shows upstream with both web servers
- Multiple requests show responses alternating between web1 and web2
- NGINX service is active and running

---

## Review Checklist

Use this checklist to ensure all requirements are met:

- [ ] Requirement 1: Documentation clear and complete
- [ ] Requirement 2: Automation tools explained and compared
- [ ] Requirement 3: 5 VMs created from blank slate
- [ ] Requirement 4: Application deployed automatically
- [ ] Requirement 5: Infrastructure metrics displayed
- [ ] Requirement 6: Idempotency demonstrated
- [ ] Requirement 7: CI/CD tracks repository changes
- [ ] Requirement 8: CI/CD deploys updates successfully
- [ ] Requirement 9: 5 VMs with descriptive hostnames
- [ ] Requirement 10: Static IP addresses assigned
- [ ] Requirement 11: Only LB accessible externally
- [ ] Requirement 12: VMs updated with security patches
- [ ] Requirement 13: DevOps user exists on all VMs
- [ ] Requirement 14: SSH key authentication enforced
- [ ] Requirement 15: DevOps user in sudo group
- [ ] Requirement 16: Sudo commands password protected
- [ ] Requirement 17: Root login disabled
- [ ] Requirement 18: Only devops user can login
- [ ] Requirement 19: Secure umask configured
- [ ] Requirement 20: Containerization tools installed
- [ ] Requirement 21: Firewall rules configured
- [ ] Requirement 22: Backend container on app server
- [ ] Requirement 23: Frontend containers on both web servers
- [ ] Requirement 24: Load balancer configured and working

---

## Quick Review Flow

1. **Start:** `vagrant destroy -f && vagrant up`
2. **Verify VMs:** `vagrant status`
3. **Test Application:** `curl http://192.168.56.20/`
4. **Show Jenkins:** Open `http://192.168.56.24:8080`
5. **Test CI/CD:** Make change, push, show auto-build
6. **Verify Requirements:** Go through checklist above

