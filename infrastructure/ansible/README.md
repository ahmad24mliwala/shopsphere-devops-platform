
# ShopSphere - Ansible Configuration Management

## Overview

This directory contains Ansible automation for configuring and auditing the ShopSphere Linux server.

## Architecture

- Control node: AWS EC2 Ubuntu instance
- Managed node: Same EC2 instance (local connection for this learning exercise)
- Automation tool: Ansible Core 2.20.1
- Python interpreter: Python 3.14

## Project Structure

```text
ansible/
├── ansible.cfg
├── inventory/
│   └── hosts.ini
├── playbooks/
│   ├── server_setup.yml
│   └── server_audit.yml
└── README.md
```

## Configuration

The `ansible.cfg` file defines the default inventory, Python interpreter and SSH host-key checking.

The inventory defines the `shopsphere_servers` group and its EC2 host.

## Playbooks

### 1. Server Setup

File: `playbooks/server_setup.yml`

Tasks:
- Update APT package cache.
- Install curl, git and unzip.
- Display setup completion message.

### 2. Server Audit

File: `playbooks/server_audit.yml`

Tasks:
- Display hostname and operating system.
- Display CPU cores and total memory.
- Check root filesystem usage.
- Display server uptime.

## Usage

Run commands from this directory.

Check connectivity:

```bash
ansible shopsphere_servers -m ping
```

Validate playbooks:

```bash
ansible-playbook --syntax-check playbooks/server_setup.yml
ansible-playbook --syntax-check playbooks/server_audit.yml
```

Run server setup:

```bash
ansible-playbook playbooks/server_setup.yml
```

Run server audit:

```bash
ansible-playbook playbooks/server_audit.yml
```

## Concepts Demonstrated

- Ansible inventory and configuration.
- YAML-based automation playbooks.
- Ansible modules.
- Privilege escalation using become.
- Ansible facts and registered variables.
- Idempotency.
- Playbook syntax validation.

## Validation Results

Both playbooks executed successfully.

- Connectivity: SUCCESS
- Server setup: 0 failures
- Server audit: 0 failures
- Repeated server setup: 0 changes

## Notes

This is a portfolio learning environment. The control and managed node are the same EC2 instance, using a local connection. Production environments commonly use a separate control node and remote SSH connections.
