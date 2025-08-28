# 🌐 HK Savor Spoon Print Server - External Access Summary

## ✅ Current Status
- **Local IP**: 192.168.0.184
- **Public IP**: 58.153.166.26
- **Router IP**: 192.168.0.1
- **Print Server**: Running on port 5000 ✅
- **Local Access**: http://192.168.0.184:5000 ✅

## 🔧 Router Port Forwarding Configuration

### Access Your Router:
1. Open browser and go to: **http://192.168.0.1**
2. Login with your router credentials
3. Look for "Port Forwarding", "Virtual Server", or "NAT"

### Add This Rule:
```
Service Name: HK Savor Spoon Print Server
External Port: 5000
Internal IP: 192.168.0.184
Internal Port: 5000
Protocol: TCP
Status: Enabled
```

## 🧪 Test External Access

### After configuring port forwarding, test with:
```powershell
# Test external access
curl http://58.153.166.26:5000/status

# If it works, you'll see JSON response with server status
```

### Expected Response:
```json
{
  "computer": "DESKTOP-9LNMIOL",
  "default_printer": "Star TSP100 Cutter (TSP143)",
  "local_ip": "192.168.0.184",
  "server": "HK Savor Spoon Windows Print Server",
  "status": "online"
}
```

## 🌐 For Your HK Savor Spoon Website

### Use These URLs:
- **Print Endpoint**: `http://58.153.166.26:5000/print`
- **Status Check**: `http://58.153.166.26:5000/status`
- **API Key**: `hksavorspoon-secure-print-key-2025`

### Example API Call:
```javascript
fetch('http://58.153.166.26:5000/print', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'hksavorspoon-secure-print-key-2025'
  },
  body: JSON.stringify({
    text: "Your receipt text here",
    font_size: "large",
    job_name: "HK Savor Spoon Order"
  })
})
```

## 🛡️ Security Notes

### Windows Firewall:
Run as Administrator:
```powershell
netsh advfirewall firewall add rule name="HK Savor Spoon Print Server" dir=in action=allow protocol=TCP localport=5000
```

### Router Security:
- Only forward port 5000
- Consider changing the API key for production
- Monitor access logs in print_server.log

## 📋 Quick Checklist

- [ ] Configure router port forwarding (192.168.0.184:5000 → 58.153.166.26:5000)
- [ ] Add Windows Firewall rule for port 5000
- [ ] Test external access: curl http://58.153.166.26:5000/status
- [ ] Update HK Savor Spoon website to use: http://58.153.166.26:5000
- [ ] Test printing from your website

## 🆘 Troubleshooting

### If external access doesn't work:
1. **Double-check router port forwarding**: Internal IP must be 192.168.0.184
2. **Check Windows Firewall**: Ensure port 5000 is allowed
3. **Restart router**: Sometimes needed after configuration changes
4. **Test local access first**: Ensure http://192.168.0.184:5000 works

### Common Router Interfaces:
- **TP-Link**: Advanced → NAT Forwarding → Virtual Servers
- **ASUS**: WAN → Virtual Server/Port Forwarding
- **Netgear**: Dynamic DNS → Port Forwarding/Port Triggering
- **Linksys**: Smart Wi-Fi Tools → Port Range Forwarding

Your print server is ready for external access once port forwarding is configured! 🚀
