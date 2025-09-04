# HK Savor Spoon Print Server

Windows thermal printer server for HK Savor Spoon restaurant order system.

## 🚀 Quick Start

### Prerequisites
- Windows 10/11
- Python 3.7+
- Star TSP100 thermal printer (USB connected)
- Star printer driver installed

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Start server
python robust_print_server_v4.py
```

### Alternative Management (PowerShell)
```powershell
# Start server
.\server.ps1 start

# Check status
.\server.ps1 status

# Run tests
.\server.ps1 test

# Stop server
.\server.ps1 stop
```

## 📋 Project Structure

### Essential Files
- `robust_print_server_v4.py` - **Main production server** (Circuit Breaker + Retry Queue)
- `windows_print_server.py` - Alternative v2.0 server
- `requirements.txt` - Python dependencies
- `ddns_config.json` - DDNS configuration
- `server.ps1` - Server management script

### Utilities
- `printer_test_suite.py` - Comprehensive testing and diagnostics
- `cleanup_project.py` - Project cleanup utility

### Configuration
- `print_queue.jsonl` - Persistent print queue
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
