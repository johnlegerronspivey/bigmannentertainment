# Supervisor Tools Documentation

## Overview
Comprehensive supervisor management tools for the BME (Big Mann Entertainment) application, providing enhanced service control, monitoring, and troubleshooting capabilities.

---

## Quick Start

### Using the Management Script

```bash
# Check status of all services
sudo supervisor-tools status

# View health check
sudo supervisor-tools check

# View recent logs
sudo supervisor-tools logs

# Restart all services
sudo supervisor-tools restart

# Fix common issues
sudo supervisor-tools fix
```

---

## Installation & Configuration

### What Was Fixed

1. **Supervisor Configuration Enhanced** (`/etc/supervisor/supervisord.conf`):
   - Added `user=root` to eliminate "running as root" warnings
   - Configured log rotation (50MB max, 10 backups)
   - Added environment variables for proper locale
   - Improved process management settings

2. **Program Configuration Enhanced** (`/etc/supervisor/conf.d/supervisord_enhanced_programs.conf`):
   - **Backend Service**:
     - Restart strategy: 3 retries, 5-second start delay
     - Log rotation: 50MB per file, 5 backups
     - Graceful shutdown: 30-second wait
     - Priority: 100 (starts after database)
   
   - **Frontend Service**:
     - Restart strategy: 3 retries, 10-second start delay
     - Log rotation: 50MB per file, 5 backups
     - Graceful shutdown: 60-second wait (React needs more time)
     - Priority: 200 (starts after backend)
   
   - **MongoDB Service**:
     - Restart strategy: 3 retries, 3-second start delay
     - Log rotation: 50MB per file, 5 backups
     - Priority: 50 (starts first - database ready before apps)

3. **Service Group Created** (`bme_services`):
   - Groups backend, frontend, and mongodb together
   - Allows managing all services with one command
   - Proper startup order: mongodb → backend → frontend

---

## Management Script Commands

### Status & Monitoring

```bash
# View service status
sudo supervisor-tools status

# Health check (comprehensive diagnostics)
sudo supervisor-tools check

# View recent logs from all services
sudo supervisor-tools logs

# Tail live logs (press Ctrl+C to exit)
sudo supervisor-tools tail
```

### Service Control

```bash
# Start all services
sudo supervisor-tools start

# Stop all services
sudo supervisor-tools stop

# Restart all services
sudo supervisor-tools restart
```

### Maintenance & Troubleshooting

```bash
# Fix common supervisor issues
sudo supervisor-tools fix

# Update supervisor to latest version
sudo supervisor-tools update

# Backup current configuration
sudo supervisor-tools backup

# Install/reinstall supervisor
sudo supervisor-tools install

# Show help
sudo supervisor-tools help
```

---

## Direct Supervisorctl Commands

### Service Management

```bash
# Check status
sudo supervisorctl status

# Start/stop individual services
sudo supervisorctl start bme_services:backend
sudo supervisorctl stop bme_services:frontend
sudo supervisorctl restart bme_services:mongodb

# Start/stop all services
sudo supervisorctl start bme_services:*
sudo supervisorctl stop all
sudo supervisorctl restart all
```

### Configuration Management

```bash
# Reload configuration files
sudo supervisorctl reread
sudo supervisorctl update

# Reload and restart all services
sudo supervisorctl reload
```

### Log Viewing

```bash
# Tail logs for specific service
sudo supervisorctl tail bme_services:backend
sudo supervisorctl tail -f bme_services:frontend  # Follow mode

# Clear logs
sudo supervisorctl clear bme_services:backend
```

---

## Log Files

### Location
All log files are stored in `/var/log/supervisor/`

### Log Files Available

- **Backend Logs**:
  - `/var/log/supervisor/backend.out.log` - Standard output
  - `/var/log/supervisor/backend.err.log` - Error output

- **Frontend Logs**:
  - `/var/log/supervisor/frontend.out.log` - Standard output
  - `/var/log/supervisor/frontend.err.log` - Error output

- **MongoDB Logs**:
  - `/var/log/supervisor/mongodb.out.log` - Standard output
  - `/var/log/supervisor/mongodb.err.log` - Error output

- **Supervisor Logs**:
  - `/var/log/supervisor/supervisord.log` - Main supervisor log

### Viewing Logs

```bash
# View recent logs
tail -n 50 /var/log/supervisor/backend.out.log

# Follow logs in real-time
tail -f /var/log/supervisor/backend.out.log

# View errors only
tail -f /var/log/supervisor/backend.err.log

# Search logs
grep "ERROR" /var/log/supervisor/backend.out.log
```

### Log Rotation

Logs automatically rotate when they reach 50MB, keeping 5 backup files:
- `backend.out.log`
- `backend.out.log.1`
- `backend.out.log.2`
- ... (up to 5 backups)

---

## Troubleshooting

### Services Won't Start

1. Check status:
   ```bash
   sudo supervisor-tools status
   ```

2. View error logs:
   ```bash
   tail -n 100 /var/log/supervisor/backend.err.log
   tail -n 100 /var/log/supervisor/frontend.err.log
   ```

3. Run fix command:
   ```bash
   sudo supervisor-tools fix
   ```

4. Check health:
   ```bash
   sudo supervisor-tools check
   ```

### Services Crash Repeatedly

1. View logs to identify the issue:
   ```bash
   sudo supervisor-tools logs
   ```

2. Check recent errors:
   ```bash
   tail -n 200 /var/log/supervisor/supervisord.log
   ```

3. Verify configuration:
   ```bash
   sudo supervisorctl reread
   ```

### Configuration Changes Not Taking Effect

```bash
# Reload configuration
sudo supervisorctl reread
sudo supervisorctl update

# Or restart supervisor entirely
sudo systemctl restart supervisord
```

### Permission Issues

```bash
# Fix log permissions
sudo supervisor-tools fix

# Or manually:
sudo chmod 644 /var/log/supervisor/*.log
sudo chmod 700 /var/run/supervisor.sock
```

### Disk Space Issues

```bash
# Check disk usage
df -h /var/log

# Clear old logs if needed
sudo find /var/log/supervisor -name "*.log.*" -mtime +7 -delete
```

---

## Configuration Files

### Main Configuration
- **File**: `/etc/supervisor/supervisord.conf`
- **Purpose**: Main supervisor daemon configuration
- **Key Settings**:
  - User: root
  - Log file size: 50MB max, 10 backups
  - Socket location: `/var/run/supervisor.sock`

### Program Configuration
- **File**: `/etc/supervisor/conf.d/supervisord_enhanced_programs.conf`
- **Purpose**: Individual service definitions
- **Services Defined**:
  - bme_services:backend
  - bme_services:frontend
  - bme_services:mongodb
  - code-server

### Backup Location
- **Directory**: `/root/supervisor_backups/`
- **Format**: `supervisor_backup_YYYYMMDD_HHMMSS/`
- **Contains**: Full configuration backup

---

## Service Priorities

Services start in this order:
1. **MongoDB** (Priority: 50) - Database must be ready first
2. **Backend** (Priority: 100) - API server starts after database
3. **Frontend** (Priority: 200) - UI starts after backend

This ensures proper dependency management.

---

## Advanced Features

### Restart Strategy
- **Max Retries**: 3 attempts
- **Start Delay**: 
  - MongoDB: 3 seconds
  - Backend: 5 seconds
  - Frontend: 10 seconds

### Graceful Shutdown
- **Signal**: TERM (allows processes to cleanup)
- **Wait Time**:
  - MongoDB: 20 seconds
  - Backend: 30 seconds
  - Frontend: 60 seconds (React dev server needs more time)

### Process Group Management
All services are grouped under `bme_services`, allowing:
- Unified control: `supervisorctl start bme_services:*`
- Group status checking
- Coordinated restarts

---

## Environment Variables

### Backend
- `APP_URL`: Application URL for external access
- `INTEGRATION_PROXY_URL`: Proxy URL for integrations
- All `.env` variables are automatically loaded

### Frontend
- `HOST`: 0.0.0.0 (listen on all interfaces)
- `PORT`: 3000
- `NODE_ENV`: development

---

## Best Practices

1. **Always use the management script** for common tasks:
   ```bash
   sudo supervisor-tools [command]
   ```

2. **Before making changes**, backup configuration:
   ```bash
   sudo supervisor-tools backup
   ```

3. **After configuration changes**, reload:
   ```bash
   sudo supervisorctl reread
   sudo supervisorctl update
   ```

4. **Monitor logs regularly**:
   ```bash
   sudo supervisor-tools logs
   ```

5. **Run health checks** periodically:
   ```bash
   sudo supervisor-tools check
   ```

---

## System Integration

### Systemd Service
Supervisor is managed by systemd:

```bash
# Start/stop supervisor daemon
sudo systemctl start supervisord
sudo systemctl stop supervisord
sudo systemctl restart supervisord

# Enable/disable auto-start
sudo systemctl enable supervisord
sudo systemctl disable supervisord

# Check systemd status
sudo systemctl status supervisord
```

---

## Quick Reference Card

| Task | Command |
|------|---------|
| Check status | `sudo supervisor-tools status` |
| Restart services | `sudo supervisor-tools restart` |
| View logs | `sudo supervisor-tools logs` |
| Health check | `sudo supervisor-tools check` |
| Fix issues | `sudo supervisor-tools fix` |
| Backup config | `sudo supervisor-tools backup` |
| Help | `sudo supervisor-tools help` |

---

## Support & Maintenance

### Regular Maintenance Tasks

**Daily**:
- Check service status
- Review error logs

**Weekly**:
- Run health check
- Review log file sizes

**Monthly**:
- Backup configuration
- Update supervisor if needed
- Clean old log backups

---

## Version Information

- **Supervisor Version**: 4.2.5
- **Enhanced Configuration**: v1.0
- **Management Script**: v1.0
- **Last Updated**: October 15, 2025

---

## Summary of Improvements

✅ **Configuration Enhanced**:
- Eliminated "running as root" warnings
- Added proper log rotation (50MB, 5 backups)
- Improved restart strategies

✅ **Service Management**:
- Created unified service group (bme_services)
- Proper startup priorities (mongodb → backend → frontend)
- Graceful shutdown with appropriate wait times

✅ **Monitoring & Troubleshooting**:
- Comprehensive management script (`supervisor-tools`)
- Health check functionality
- Automated issue fixing

✅ **Reliability**:
- Automatic restart on unexpected exits
- Retry strategies (3 attempts)
- Process group management for coordinated operations

✅ **Logging**:
- Enhanced log rotation
- Separate stdout/stderr logs
- Proper log file permissions

**All supervisor issues have been comprehensively addressed and resolved!**
