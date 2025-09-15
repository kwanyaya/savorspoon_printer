# HK Savor Spoon Print Server v6.0 - Auto-Recovery Edition

� **AUTO-RECOVERY UPDATE**: Automatically handles printer offline issues and Windows spooler problems

Windows thermal printer server for HK Savor Spoon restaurant order system with intelligent printer recovery.

## 🚀 Quick Start

### Prerequisites
- Windows 10/11
- Python 3.7+
- Star TSP100 thermal printer (USB connected)
- Star printer driver installed
- **Administrator privileges** (required for auto-recovery features)

### Option 1: Auto-Recovery Server (Recommended) 🚑

**Best for production use** - automatically handles printer offline issues and spooler problems:

```bash
# Install dependencies
pip install -r requirements.txt

# Run as Administrator (IMPORTANT!)
Right-click -> "Run as Administrator"
start_auto_recovery_server.bat

# Test auto-recovery features
python test_auto_recovery.py
```

### Option 2: Standard Secure Server

For basic functionality without auto-recovery:

```bash
# Install dependencies
pip install -r requirements.txt

# Start secure server
python secure_print_server_v5.py
```

### Alternative Management (PowerShell)
```powershell
# Start secure server (default)
.\server.ps1 start

# Start with specific version
.\server.ps1 start -secure   # v5.0 security enhanced
.\server.ps1 start -v4       # v4.0 robust version
.\server.ps1 start -v2       # v2.0 basic version

# Check status and security
.\server.ps1 status
.\server.ps1 security

# Run security monitor
python security_monitor.py
.\server.ps1 test

# Stop server
.\server.ps1 stop
```

## � Auto-Recovery Features (v6.0)

### What Problems Does Auto-Recovery Solve?

1. **Printer Offline Issues** 🔴
   - Automatically detects when printer goes offline
   - Attempts to bring printer back online
   - Restarts printer connections

2. **Windows Print Spooler Problems** 🔄
   - Monitors Print Spooler service health
   - Automatically restarts spooler when hung
   - Clears stuck print jobs from queue

3. **Connection Timeouts** ⏱️
   - Handles printer connection timeouts
   - Retries with fresh connections
   - Prevents permanent connection loss

4. **Print Job Blockages** 📄
   - Detects stuck print jobs
   - Clears print queue automatically
   - Prevents job accumulation

### How It Works
- **Continuous Monitoring**: Checks printer health every 30 seconds
- **Smart Recovery**: Tries multiple recovery strategies automatically
- **Minimal Downtime**: Most issues resolved in 5-15 seconds
- **Administrator Required**: Needs admin privileges for service management

### New API Endpoints
- `GET /recovery/status` - Detailed recovery statistics
- `POST /recovery/trigger` - Manual recovery trigger
- `POST /recovery/config` - Update recovery settings
- `POST /emergency-clear` - Full system reset & clear

📖 **[Read the full Auto-Recovery Guide →](AUTO_RECOVERY_GUIDE.md)**

## �📋 Project Structure

### Essential Files
- `auto_recovery_print_server.py` - **🚑 AUTO-RECOVERY production server** (v6.0 - Handles printer offline & spooler issues)
- `secure_print_server_v5.py` - **🛡️ SECURE server** (v5.0 - Enhanced Security + Circuit Breaker)
- `robust_print_server_v4.py` - Robust server with circuit breaker protection (v4.0)
- `windows_print_server.py` - Alternative basic server (v2.0)
- `security_monitor.py` - **NEW**: Real-time security monitoring dashboard
- `requirements.txt` - Python dependencies
- `ddns_config.json` - DDNS configuration
- `server.ps1` - Enhanced server management script

### Utilities
- `printer_test_suite.py` - Comprehensive testing and diagnostics
- `cleanup_project.py` - Project cleanup utility

### Configuration & Logs
- `print_queue.jsonl` - Persistent print queue
- `print_server_secure.log` - **NEW**: Security event logging

## 🛡️ SECURITY FEATURES (v5.0)

### Built-in Protection
- **IP Whitelisting**: Only allow trusted networks and specific IPs
- **Rate Limiting**: Max 10 requests/minute for non-whitelisted IPs  
- **Suspicious Request Detection**: Auto-detect and block attack patterns:
  - SSH connection attempts (`ssh-`, `connect`)
  - Admin login probes (`login`, `admin`, `manager/`)
  - Path traversal attacks (`.env`, `cgi-bin`)
  - Malformed requests and unusual HTTP methods

### Security Monitoring
```powershell
# Real-time security dashboard
python security_monitor.py

# Security status via PowerShell
.\server.ps1 security

# View security logs
Get-Content print_server_secure.log -Tail 20
```

### Allowed IP Ranges (Configurable)
- `192.168.0.0/16` - Local restaurant network
- `10.0.0.0/8` - Private networks
- `172.16.0.0/12` - Private networks  
- `127.0.0.0/8` - Localhost
- Specific external IPs (e.g., your website server)

### Security Actions
- **Rate Limiting**: Slow down non-whitelisted IPs
- **Automatic Blocking**: Block IPs after 5 suspicious requests for 5 minutes
- **Request Filtering**: Return 404 for suspicious paths (hide real endpoints)
- **Request Size Limits**: Reject requests larger than 1MB
- `print_server.log` - Server logs
- `print_server_debug.log` - Debug logs

## 🔧 API Endpoints

### Public Endpoints
- `GET /status` - Server and printer status

### Authenticated Endpoints (requires API key)
- `POST /print` - Print text or receipt data
- `POST /test-print` - Send test print
- `GET /printers` - List available printers
- `GET /queue` - View print queue status
- `POST /emergency-clear` - Clear queue and reset circuit breaker

### API Key
```
X-API-Key: hksavorspoon-secure-print-key-2025
```

## 🖨️ Printer Setup

### Star TSP100 Configuration
1. Install Star TSP100 driver from [Star Micronics website](https://www.star-m.jp/products/s_print/sdk/windows.html)
2. Set as default printer in Windows
3. Configure printer properties:
   - **Paper Size**: Roll Paper 80mm
   - **Print Quality**: High
   - **Advanced**: Enable "Print directly to printer"
   - **Ports**: Disable "Enable bidirectional support"

### Troubleshooting Printer Issues
```bash
# Run comprehensive diagnostics
python printer_test_suite.py

# Check printer hardware (if software tests fail):
# 1. Turn OFF printer
# 2. Hold FEED button + turn ON
# 3. Hold FEED for 3 seconds
# 4. Should print configuration page
```

## 🌐 Network Access

### Local Network
- Server runs on port 8080
- Local: `http://localhost:8080`
- Network: `http://[YOUR_IP]:8080`

### External Access (Optional)
- Configure DDNS (NoIP recommended)
- Update `ddns_config.json`
- Set up port forwarding on router (port 8080)

## ⚡ Features

### v4.0 Server Features
- **Circuit Breaker Pattern** - Prevents cascading failures
- **Aggressive Timeout Protection** - 3-second timeouts with force termination
- **Background Retry Queue** - Automatic retry of failed jobs
- **File-based Persistence** - Queue survives server restarts
- **Enhanced Chinese Support** - Traditional Chinese character printing
- **Zero Order Loss** - Guaranteed delivery with retry mechanism

### Reliability Features
- Print job queuing and retry
- Automatic failure recovery
- Server health monitoring
- Comprehensive error logging
- Graceful degradation

## 🧪 Testing

### Quick Test
```bash
# Test server status
curl http://localhost:8080/status

# Test print (with API key)
curl -X POST http://localhost:8080/print \
  -H "Content-Type: application/json" \
  -H "X-API-Key: hksavorspoon-secure-print-key-2025" \
  -d '{"text": "Hello World Test"}'
```

### Comprehensive Testing
```bash
python printer_test_suite.py
```

## 🔧 Maintenance

### Cleanup Project
```bash
python cleanup_project.py
```

### View Logs
```bash
# Server logs
type print_server.log

# Debug logs  
type print_server_debug.log
```

### Server Management
```powershell
# PowerShell management
.\server.ps1 status    # Check status
.\server.ps1 restart   # Restart server
.\server.ps1 test      # Run tests
```

## 📞 Support

### Common Issues
1. **Jobs complete but printer doesn't print**
   - Check printer power and paper
   - Try printer self-test (FEED button + power on)
   - Reinstall Star driver

2. **Server timeout errors**
   - v4.0 server has 3-second timeouts with retry
   - Check printer USB connection
   - Verify printer isn't paused in Windows

3. **Chinese characters not printing**
   - Server automatically detects Traditional Chinese
   - Uses Big5 encoding for Star TSP100
   - Check printer firmware supports Chinese

### Getting Help
- Check logs in `print_server.log`
- Run `python printer_test_suite.py` for diagnostics
- Verify printer works with Windows test page

## 📝 Version History

- **v4.0** - Circuit breaker + retry queue + aggressive timeouts
- **v2.0** - Enhanced Chinese support + DDNS integration  
- **v1.0** - Basic print server functionality

---

**HK Savor Spoon Restaurant Print System**  
Reliable thermal receipt printing for order management
