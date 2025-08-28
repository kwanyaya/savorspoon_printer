# 🛜 Router Port Forwarding Guide - HK Savor Spoon Print Server

## 🔧 Universal Steps for Any Router:

### 1️⃣ Access Router (Already Done)
- URL: http://192.168.0.1
- Login with admin credentials

### 2️⃣ Navigate to Port Forwarding
Look for these menu options:

#### TP-Link Routers:
- **Advanced** → **NAT Forwarding** → **Virtual Servers**
- Click **"Add"** button

#### ASUS Routers:
- **WAN** → **Virtual Server/Port Forwarding**
- Click **"+"** to add new rule

#### Netgear Routers:
- **Dynamic DNS** → **Port Forwarding/Port Triggering**
- Click **"Add Custom Service"**

#### Linksys Routers:
- **Smart Wi-Fi Tools** → **Port Range Forwarding**
- Click **"Add New"**

#### D-Link Routers:
- **Advanced** → **Port Forwarding**
- Click **"Add"**

### 3️⃣ Fill in the Port Forwarding Rule

**Copy these EXACT values:**

```
🏷️ Service/Rule Name: HK_Savor_Spoon_Print
🌐 External Port (Start): 5000
🌐 External Port (End): 5000
🏠 Internal IP Address: 192.168.0.184
🏠 Internal Port (Start): 5000
🏠 Internal Port (End): 5000
📡 Protocol: TCP
✅ Enable: YES/Checked
```

### 4️⃣ Alternative Field Names (If Different)

Some routers use different terminology:

```
"Public Port" = External Port = 5000
"Private Port" = Internal Port = 5000
"Server IP" = Internal IP = 192.168.0.184
"Local IP" = Internal IP = 192.168.0.184
"Port Range" = 5000-5000 (same start/end)
```

### 5️⃣ Save and Test

1. **Save**: Click "Save", "Apply", or "OK"
2. **Restart**: Router may restart automatically
3. **Wait**: Allow 2-3 minutes for changes to take effect

## 🧪 Test Port Forwarding

### After Configuration, Test External Access:

**Open PowerShell and run:**
```powershell
# Test if external access works
curl http://58.153.166.26:5000/status
```

**Expected Success Response:**
```json
{
  "computer": "DESKTOP-9LNMIOL",
  "default_printer": "Star TSP100 Cutter (TSP143)", 
  "status": "online"
}
```

**If Failed:**
```
Connection timeout or refused
```

## 🛠️ Common Router Interface Screenshots Guide:

### TP-Link Example:
```
Advanced → NAT Forwarding → Virtual Servers → Add

Service Type: [Custom]
External Port: [5000]
Internal IP: [192.168.0.184]
Internal Port: [5000]
Protocol: [TCP]
Status: [Enabled]
```

### ASUS Example:
```
WAN → Virtual Server/Port Forwarding

Service Name: [HK_Savor_Spoon]
Port Range: [5000]
Local IP: [192.168.0.184]
Local Port: [5000]
Protocol: [TCP]
```

### Netgear Example:
```
Dynamic DNS → Port Forwarding

Service Name: [HK Savor Spoon]
Service Type: [TCP]
External Starting Port: [5000]
External Ending Port: [5000]
Internal Starting Port: [5000]
Internal Ending Port: [5000]
Internal IP Address: [192.168.0.184]
```

## 🆘 Troubleshooting

### ❌ If Port Forwarding Doesn't Work:

1. **Double-check IP**: Ensure 192.168.0.184 is correct
   ```powershell
   ipconfig | findstr "IPv4"
   ```

2. **Check Windows Firewall**: Allow port 5000
   ```powershell
   # Run as Administrator
   netsh advfirewall firewall add rule name="HK Savor Spoon" dir=in action=allow protocol=TCP localport=5000
   ```

3. **Router Restart**: Some routers need full restart
   - Unplug power for 30 seconds
   - Plug back in and wait 2-3 minutes

4. **Alternative Port**: Try port 8080 if 5000 is blocked
   - Update server and router configuration

### ✅ Success Indicators:

- External URL responds: http://58.153.166.26:5000/status
- JSON data returns with server information
- No timeout or connection refused errors

## 🌐 Final Test for HK Savor Spoon Website

Once working, your website can use:
```javascript
// API endpoint for your Laravel app
const PRINT_SERVER_URL = 'http://58.153.166.26:5000/print';
const API_KEY = 'hksavorspoon-secure-print-key-2025';
```

Your print server will be accessible from anywhere on the internet! 🚀
