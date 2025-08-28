# Router Port Forwarding Configuration for Port 8080

## Step 1: Access Your Router
1. Open browser and go to: http://192.168.0.1
2. Login with admin credentials

## Step 2: Find Port Forwarding Section
Look for one of these menu options:
- "Port Forwarding"
- "Virtual Server" 
- "NAT Forwarding"
- "Application & Gaming"
- "Advanced" → "Port Forwarding"

## Step 3: Add New Port Forwarding Rule

**Rule Configuration:**
- **Rule Name:** HK_Savor_Spoon_Port_8080
- **External Port:** 8080
- **Internal IP:** 192.168.0.184
- **Internal Port:** 8080  
- **Protocol:** TCP (or Both TCP/UDP)
- **Status:** Enable/Active

## Step 4: Save Configuration
1. Click "Save" or "Apply"
2. Wait for router to restart (1-2 minutes)
3. Some routers require a reboot

## Step 5: Test External Access
After router configuration, test:
```
curl http://58.153.166.26:8080/status
```

## Troubleshooting Tips

### If External Access Still Fails:
1. **Check Windows Firewall:**
   ```powershell
   netsh advfirewall firewall add rule name="HK Savor Spoon Port 8080" dir=in action=allow protocol=TCP localport=8080
   ```

2. **Check ISP Blocking:**
   - Some ISPs block common ports
   - Try port 8000, 9000, or 3000 if 8080 is blocked

3. **Router-Specific Instructions:**
   - **TP-Link:** Advanced → NAT Forwarding → Port Forwarding
   - **Netgear:** Dynamic DNS → Port Forwarding
   - **ASUS:** Adaptive QoS → Traditional QoS → Port Forwarding
   - **Linksys:** Smart Wi-Fi Tools → Port Range Forwarding

4. **Alternative Ports if 8080 Blocked:**
   - Port 3000 (commonly allowed)
   - Port 9000 (less likely to be blocked)
   - Port 8000 (alternative web port)

## Current Server Status
- Local Server: http://192.168.0.184:8080
- External Server: http://58.153.166.26:8080 (after config)
- Website Update: Change WINDOWS_PRINT_SERVER_URL to http://58.153.166.26:8080

## Success Test
If successful, you should see:
```json
{
  "status": "online",
  "server": "HK Savor Spoon Windows Print Server", 
  "version": "1.0",
  "computer": "DELL-PC",
  "local_ip": "192.168.0.184",
  "default_printer": "Star TSP100 Cutter (TSP143)",
  "timestamp": "2025-08-27T23:48:25"
}
```
