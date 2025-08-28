# Network Diagnostic Steps for HK Savor Spoon Print Server

## 1. Check Current External IP
Run these commands to get your actual external IP:

### Method 1: Web Service
```powershell
(Invoke-WebRequest -Uri "https://ifconfig.me/ip" -UseBasicParsing).Content.Trim()
```

### Method 2: DNS Lookup  
```powershell
nslookup myip.opendns.com resolver1.opendns.com
```

### Method 3: Router Admin Panel
1. Go to http://192.168.0.1
2. Look for "WAN Status" or "Internet Status"
3. Find "Public IP" or "External IP"

## 2. Test Basic Connectivity

### Test Router Connection:
```powershell
ping 192.168.0.1
```

### Test Internet Connection:
```powershell
ping 8.8.8.8
```

### Test Local Network:
```powershell
ping 192.168.0.184
```

## 3. Common Issues & Solutions

### Issue 1: Dynamic IP Changed
**Solution:** Get the new IP and update your website configuration

### Issue 2: ISP Blocks Ping (ICMP)
**Solution:** This is normal - ping may fail but HTTP requests can still work
**Test:** Try HTTP instead of ping:
```powershell
curl http://[your-real-external-ip]:8080/status
```

### Issue 3: Router Firewall/DMZ
**Solution:** 
1. Enable DMZ for your computer (192.168.0.184)
2. Or configure proper port forwarding
3. Check router firewall settings

### Issue 4: ISP Port Blocking
**Solution:** Try alternative ports:
- Port 3000 (commonly allowed)
- Port 9000 (less restricted)
- Port 8000 (alternative web port)

## 4. Alternative Solutions

### Option A: Use Dynamic DNS Service
1. Set up free DDNS (like No-IP, DuckDNS)
2. Get a permanent domain name
3. Auto-updates when IP changes

### Option B: Use Ngrok Tunnel
1. Install ngrok: https://ngrok.com/
2. Run: `ngrok http 8080`
3. Get public URL like: https://abc123.ngrok.io
4. Use this URL in your website

### Option C: Use Cloudflare Tunnel
1. Free service from Cloudflare
2. Creates secure tunnel to your local server
3. No port forwarding needed

## 5. Quick Fix Commands

### Get Real External IP:
```powershell
# Try multiple methods
$ip1 = try { (Invoke-WebRequest "https://ifconfig.me/ip" -UseBasicParsing).Content.Trim() } catch { "Failed" }
$ip2 = try { (Invoke-WebRequest "https://ipinfo.io/ip" -UseBasicParsing).Content.Trim() } catch { "Failed" }
$ip3 = try { (Invoke-WebRequest "https://api.ipify.org" -UseBasicParsing).Content.Trim() } catch { "Failed" }
Write-Host "Method 1: $ip1"
Write-Host "Method 2: $ip2" 
Write-Host "Method 3: $ip3"
```

### Test HTTP Access (bypass ping):
```powershell
# Replace [REAL-IP] with your actual external IP
try { 
    $response = Invoke-WebRequest "http://[REAL-IP]:8080/status" -UseBasicParsing -TimeoutSec 10
    Write-Host "SUCCESS: Server accessible"
    $response.Content
} catch { 
    Write-Host "FAILED: $($_.Exception.Message)"
}
```

## 6. Next Steps Based on Results

### If External IP Changed:
1. Update HK Savor Spoon website with new IP
2. Test with new IP address

### If Ping Fails But HTTP Works:
1. This is normal - many routers block ping
2. Continue with HTTP testing

### If Nothing Works:
1. Try ngrok tunnel (easiest solution)
2. Consider cloud hosting for print server
3. Use VPN service

## Current Configuration Reminder:
- Internal IP: 192.168.0.184
- Router IP: 192.168.0.1  
- Previous External IP: 58.153.166.26 (may have changed)
- Print Server Port: 8080
- Local Test: http://localhost:8080/status ✓
