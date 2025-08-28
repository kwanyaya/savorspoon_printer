# HK Savor Spoon - Router Configuration for Public IP 154.88.89.9

## Current Network Setup
- **Public IP:** 154.88.89.9 ✅
- **Internal IP:** 192.168.0.184 (assuming unchanged)
- **Router IP:** 192.168.0.1
- **Print Server Port:** 5000

## Step 1: Configure Router Port Forwarding

### Access Router Admin Panel:
1. Open browser: http://192.168.0.1
2. Login with admin credentials

### Add Port Forwarding Rules:

**Rule 1: Main Print Server (Port 5000)**
- **Service Name:** HK_Savor_Spoon_Main
- **External Port:** 5000
- **Internal IP:** 192.168.0.184
- **Internal Port:** 5000
- **Protocol:** TCP
- **Status:** Enable

**Rule 2: Backup Print Server (Port 8080)**
- **Service Name:** HK_Savor_Spoon_Backup
- **External Port:** 8080
- **Internal IP:** 192.168.0.184
- **Internal Port:** 8080
- **Protocol:** TCP
- **Status:** Enable

## Step 2: Update Website Configuration

### Change in your HK Savor Spoon website:
**From (old IP):**
```
WINDOWS_PRINT_SERVER_URL=http://58.153.166.26:5000
```

**To (new IP):**
```
WINDOWS_PRINT_SERVER_URL=http://154.88.89.9:5000
```

### Alternative URLs for testing:
- Main: `http://154.88.89.9:5000`
- Backup: `http://154.88.89.9:8080`

## Step 3: Test External Access

### Test Commands (run these after router config):
```powershell
# Test main server
curl http://154.88.89.9:5000/status

# Test backup server
curl http://154.88.89.9:8080/status

# Test local (should work)
curl http://localhost:5000/status
```

### Expected Response:
```json
{
  "status": "online",
  "server": "HK Savor Spoon Windows Print Server",
  "version": "1.0",
  "computer": "DELL-PC",
  "local_ip": "192.168.0.184",
  "default_printer": "Star TSP100 Cutter (TSP143)",
  "timestamp": "2025-08-28T..."
}
```

## Step 4: Common Router Locations for Port Forwarding

### TP-Link:
- Advanced → NAT Forwarding → Port Forwarding

### Netgear:
- Dynamic DNS → Port Forwarding/Port Triggering

### ASUS:
- Adaptive QoS → Traditional QoS → Port Forwarding

### D-Link:
- Advanced → Port Forwarding

### Linksys:
- Smart Wi-Fi Tools → Port Range Forwarding

## Step 5: Troubleshooting

### If External Access Fails:

**Check 1: Verify Internal IP**
```powershell
ipconfig | findstr "IPv4"
```
Update router rules if your internal IP changed.

**Check 2: Test Router Access**
```powershell
ping 192.168.0.1
```

**Check 3: Check Windows Firewall**
```powershell
netsh advfirewall firewall show rule name="HK Savor Spoon Port 5000"
```

**Check 4: Add Firewall Rules (if needed)**
```powershell
netsh advfirewall firewall add rule name="HK Savor Spoon Port 5000" dir=in action=allow protocol=TCP localport=5000
netsh advfirewall firewall add rule name="HK Savor Spoon Port 8080" dir=in action=allow protocol=TCP localport=8080
```

## Step 6: Prevent Future IP Changes

### Option A: Contact ISP for Static IP
- Call your ISP
- Request static IP service
- Cost: ~$10-30/month
- Permanent solution

### Option B: Dynamic DNS (Recommended)
1. Go to https://www.noip.com/
2. Create free account
3. Create hostname: `hksavorspoon.ddns.net`
4. Download No-IP DUC
5. Use domain in website instead of IP

### Option C: Ngrok (Easiest)
1. Download: https://ngrok.com/
2. Run: `ngrok http 5000`
3. Use provided URL in website

## Quick Summary of Changes Needed:

✅ **Router:** Add port forwarding 5000 → 192.168.0.184:5000
✅ **Website:** Change URL to http://154.88.89.9:5000
✅ **Test:** curl http://154.88.89.9:5000/status

## Immediate Action Required:
1. **Configure router port forwarding** (most important)
2. **Update website URL** from 58.153.166.26 to 154.88.89.9
3. **Test external access** after router config
