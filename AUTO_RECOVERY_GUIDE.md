# AUTO-RECOVERY PRINT SERVER v6.0 - User Guide

## 🚑 What's New: Automatic Printer Recovery

The Auto-Recovery Print Server automatically handles common printer problems that cause print failures:

### Common Problems This Solves:
- **Printer Offline**: Automatically detects and brings printer back online
- **Print Spooler Hang**: Restarts Windows Print Spooler service when stuck
- **Stuck Print Jobs**: Clears print queue when jobs are blocking
- **Connection Timeouts**: Automatically reconnects to printer
- **Service Not Running**: Ensures Print Spooler service is always running

## 🔧 How It Works

### 1. Continuous Health Monitoring
- Checks printer status every 30 seconds
- Monitors Windows Print Spooler service
- Detects offline/error conditions automatically

### 2. Automatic Recovery Actions
When problems are detected, the server automatically:
1. **Checks Print Spooler Service** - Restarts if not running
2. **Clears Stuck Print Jobs** - Removes blocking jobs from queue
3. **Tests Printer Connection** - Validates printer accessibility
4. **Resumes Paused Printer** - Brings printer out of pause state
5. **Restarts Spooler (Last Resort)** - Full service restart if needed

### 3. Smart Retry Logic
- Failed prints are automatically retried with recovery
- Circuit breaker prevents system overload
- Progressive backoff for persistent issues

## 🚀 Getting Started

### 1. Install Requirements
```bash
pip install -r requirements.txt
```

**Note**: You need `psutil` for process monitoring (already added to requirements.txt)

### 2. Run as Administrator
**IMPORTANT**: For full recovery functionality, run as Administrator:
```cmd
Right-click -> "Run as Administrator"
start_auto_recovery_server.bat
```

### 3. Check Server Status
Open browser to: `http://localhost:8080/status`

You'll see recovery information:
```json
{
  "status": "online",
  "server": "HK Savor Spoon Auto-Recovery Print Server",
  "version": "6.0-auto-recovery",
  "printer": "Star TSP100 Printer",
  "printer_status": {
    "online": true,
    "error": false,
    "paper_jam": false,
    "paper_out": false
  },
  "auto_recovery": true,
  "recovery_stats": {
    "spooler_restarts": 2,
    "offline_detections": 0,
    "recovery_in_progress": false
  }
}
```

## 📡 New API Endpoints

### Recovery Management
- `POST /recovery/trigger` - Manually trigger recovery
- `GET /recovery/status` - Get detailed recovery statistics
- `POST /recovery/config` - Update recovery settings

### Enhanced Print Endpoint
- `POST /print` - Now includes automatic recovery
- Response includes recovery information:
```json
{
  "success": true,
  "message": "Print completed successfully (256 bytes)",
  "auto_recovery": true,
  "timestamp": "2025-09-16T14:30:00"
}
```

## ⚙️ Configuration Options

### Update Recovery Settings
```bash
curl -X POST http://localhost:8080/recovery/config \
  -H "X-API-Key: hksavorspoon-secure-print-key-2025" \
  -H "Content-Type: application/json" \
  -d '{
    "auto_recovery": true,
    "printer_check_interval": 30,
    "recovery_max_retries": 3
  }'
```

### Configuration Parameters
- **auto_recovery**: Enable/disable automatic recovery (default: true)
- **printer_check_interval**: How often to check printer health in seconds (default: 30)
- **recovery_max_retries**: Maximum recovery attempts per issue (default: 3)
- **spooler_restart_cooldown**: Minimum time between spooler restarts in seconds (default: 60)

## 🚨 Emergency Features

### Emergency Clear
Clears everything and resets the system:
```bash
curl -X POST http://localhost:8080/emergency-clear \
  -H "X-API-Key: hksavorspoon-secure-print-key-2025"
```

This will:
- Clear all print queues (system and application)
- Reset circuit breaker
- Restart Print Spooler
- Reset recovery counters

### Manual Recovery Trigger
Force a recovery attempt:
```bash
curl -X POST http://localhost:8080/recovery/trigger \
  -H "X-API-Key: hksavorspoon-secure-print-key-2025"
```

## 📊 Monitoring & Logs

### Check Recovery Status
```bash
curl -X GET http://localhost:8080/recovery/status \
  -H "X-API-Key: hksavorspoon-secure-print-key-2025"
```

### Log Files
- `print_server_recovery.log` - Detailed recovery actions and status
- Console output shows real-time recovery activities

### Recovery Statistics
Monitor these metrics:
- `spooler_restarts` - How many times spooler was restarted
- `offline_detections` - How many times printer went offline
- `recovery_in_progress` - Whether recovery is currently running

## 🛡️ Security Features (Inherited from v5)

All security features from v5 are maintained:
- IP whitelisting and rate limiting
- Suspicious request blocking
- API key authentication
- Circuit breaker protection

## 🔍 Troubleshooting

### Common Issues

#### 1. "Not running as Administrator" Warning
**Solution**: Right-click batch file and select "Run as Administrator"

#### 2. Recovery Not Working
**Check**:
- Windows Print Spooler service exists
- User has administrative privileges
- Printer is physically connected and powered on

#### 3. Frequent Spooler Restarts
**Possible Causes**:
- Hardware issues with printer
- Driver problems
- Windows updates affecting print subsystem

**Check logs** for specific error messages.

### Debug Mode
Enable detailed logging by setting `logging.DEBUG`:
```python
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Performance Impact

### Resource Usage
- CPU: Minimal overhead (~1-2% during health checks)
- Memory: ~50-100MB (similar to v5)
- Network: No additional network usage

### Recovery Timing
- Health check: Every 30 seconds (configurable)
- Recovery attempt: 5-15 seconds
- Spooler restart: 10-20 seconds
- Cooldown period: 60 seconds between major actions

## 🔄 Migration from v5

### Automatic Migration
The v6 server is fully backward compatible with v5 clients.

### New Features Available
- Automatic printer recovery
- Enhanced status reporting
- Recovery management endpoints
- Improved error handling

### Configuration Changes
- All v5 settings are preserved
- New recovery settings added with sensible defaults
- No manual configuration required

## 📞 API Examples

### Check if Recovery is Working
```javascript
fetch('http://localhost:8080/recovery/status', {
  headers: {
    'X-API-Key': 'hksavorspoon-secure-print-key-2025'
  }
})
.then(response => response.json())
.then(data => {
  console.log('Recovery Status:', data.recovery_stats);
  console.log('Printer Online:', data.printer_status.online);
});
```

### Print with Recovery
```javascript
fetch('http://localhost:8080/print', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'hksavorspoon-secure-print-key-2025'
  },
  body: JSON.stringify({
    text: 'Test receipt with auto-recovery\n收據測試\n\n'
  })
})
.then(response => response.json())
.then(data => {
  console.log('Print Result:', data.message);
  console.log('Recovery Used:', data.auto_recovery);
});
```

## 🎯 Best Practices

### 1. Run as Administrator
Always run the server with administrator privileges for full functionality.

### 2. Monitor Recovery Stats
Check `/recovery/status` regularly to identify patterns in printer issues.

### 3. Set Appropriate Check Intervals
- For busy restaurants: 15-30 seconds
- For low-volume usage: 60-120 seconds

### 4. Use Emergency Clear Sparingly
Only use emergency clear when printer is completely unresponsive.

### 5. Keep Logs
Monitor `print_server_recovery.log` for early warning signs of hardware issues.

---

## ⚡ Quick Start Summary

1. **Install**: `pip install -r requirements.txt`
2. **Run**: Right-click `start_auto_recovery_server.bat` → "Run as Administrator"
3. **Test**: Open `http://localhost:8080/status` in browser
4. **Print**: Send POST to `/print` with your API key
5. **Monitor**: Check `/recovery/status` for health information

The server will automatically handle printer offline issues, spooler problems, and connection timeouts without any manual intervention!
