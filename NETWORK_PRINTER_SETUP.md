# Network Printer Setup Guide for HK Savor Spoon Print Server

## 🌐 Network Printer Connection Options

### Option 1: Direct Network Printer (Recommended)
**Printer → LAN Cable → Router**

**Requirements:**
- Star TSP100/TSP143 with Ethernet port
- LAN cable 
- Router with available port

**Steps:**
1. Connect printer to router via LAN cable
2. Printer will auto-assign IP (check router admin page)
3. Note the printer's IP address
4. Server will auto-detect on startup

### Option 2: USB-to-Ethernet Adapter
**Printer → USB Cable → USB-to-Ethernet Adapter → LAN Cable → Router**

**Requirements:**
- USB-to-Ethernet adapter
- Print server adapter that supports raw TCP printing
- LAN cable

**Note:** This is more complex and may require specific adapter configuration.

## 🔧 Server Configuration

The auto-recovery print server now supports:

### Automatic Network Detection
```
🔍 Scanning for network printers...
✅ Found potential network printer at 192.168.1.100:9100
🌐 Network printer configured: 192.168.1.100:9100
✅ Network printer 192.168.1.100:9100 is reachable
🌐 Network printer preferred (auto-detected as working)
```

### Hybrid Mode (USB + Network)
- **Primary Method:** Network or USB (auto-selected)
- **Backup Method:** Automatic failover
- **Benefits:** Maximum reliability

### Manual Configuration
If auto-detection fails, you can manually set:

```python
CONFIG = {
    'NETWORK_PRINTER_IP': '192.168.1.100',    # Your printer's IP
    'NETWORK_PRINTER_PORT': 9100,             # Raw printing port
    'PREFER_NETWORK': True                    # Use network first
}
```

## 🖨️ Printer IP Discovery

### Method 1: Router Admin Panel
1. Access router admin (usually http://192.168.1.1)
2. Look for "Connected Devices" or "DHCP Clients"
3. Find device with name containing "Star" or "TSP"

### Method 2: Automatic Scan
The server automatically scans these IPs:
- `192.168.1.100` - Common printer IP
- `192.168.1.101`
- `192.168.1.200` 
- `192.168.1.201`

### Method 3: Manual Network Scan
```bash
# Windows Command Prompt
nmap -p 9100 192.168.1.0/24

# Or use ping to test specific IPs
ping 192.168.1.100
```

## 📡 Network Printing Advantages

### Speed & Reliability
- **Faster Setup:** No USB driver issues
- **Distance:** Printer can be anywhere on network
- **Reliability:** Less prone to connection drops
- **Multiple Access:** Multiple servers can access same printer

### Troubleshooting Benefits
- **Remote Monitoring:** Check printer status over network
- **Easy Replacement:** Swap printers without changing USB connections
- **Centralized Management:** One printer serves multiple POS stations

## 🔄 Failover Modes

### Network-First Mode (Preferred)
```
1. Try Network Printer → ✅ Success
2. If Network Fails → Try USB Backup
```

### USB-First Mode (Fallback)
```
1. Try USB Printer → ✅ Success  
2. If USB Fails → Try Network Backup
```

## 🛠️ Setup Instructions

### Step 1: Physical Connection
1. **Connect printer to router via LAN cable**
2. **Power on printer and wait for network initialization**
3. **Print network configuration page** (usually hold feed button on startup)

### Step 2: Find Printer IP
Check one of these:
- **Router admin page** → Connected devices
- **Printer LCD display** (if available)
- **Network config printout**

### Step 3: Test Connection
```bash
# Test if printer responds on port 9100
telnet 192.168.1.100 9100
```

### Step 4: Run Print Server
```bash
python auto_recovery_print_server.py
```

Server will display:
```
🔍 Scanning for network printers...
✅ Found potential network printer at 192.168.1.100:9100
🌐 Network printer configured: 192.168.1.100:9100
🖨️  Hybrid setup: USB=Star TSP100 Cutter, Network=192.168.1.100:9100
🌐 Network printer preferred (auto-detected as working)
```

## 📊 Performance Comparison

| Connection Type | Speed | Reliability | Setup Complexity |
|----------------|-------|-------------|------------------|
| **USB Only** | Good | Good | Simple |
| **Network Only** | Excellent | Excellent | Medium |
| **Hybrid Mode** | Excellent | Outstanding | Medium |

## 🚨 Troubleshooting

### Network Printer Not Found
1. **Check physical connection:** LAN cable plugged in
2. **Check printer power:** Ensure printer is on
3. **Check network settings:** Printer has valid IP
4. **Check firewall:** Windows firewall may block port 9100

### Print Jobs Not Processing
1. **Test connectivity:** `telnet <printer_ip> 9100`
2. **Check printer status:** Paper, power, errors
3. **Restart network:** Unplug/replug LAN cable
4. **Check router:** Other devices working?

### Hybrid Mode Issues
- **USB takes priority:** Set `PREFER_NETWORK = True`
- **Network unreliable:** Set `PREFER_NETWORK = False`
- **Both failing:** Check `/status` endpoint for details

## 📝 Configuration Examples

### Restaurant with Network Printer Only
```python
CONFIG = {
    'NETWORK_PRINTER_IP': '192.168.1.100',
    'NETWORK_PRINTER_PORT': 9100,
    'PREFER_NETWORK': True,
    'DEFAULT_PRINTER': None  # No USB fallback
}
```

### Restaurant with Hybrid Setup
```python
CONFIG = {
    'NETWORK_PRINTER_IP': '192.168.1.100',
    'NETWORK_PRINTER_PORT': 9100,
    'PREFER_NETWORK': True,
    'DEFAULT_PRINTER': 'Star TSP100 Cutter'  # USB backup
}
```

### Multiple Print Servers
Each server can use the same network printer:
```python
# Server 1 (Main POS)
CONFIG = {'NETWORK_PRINTER_IP': '192.168.1.100', 'PREFER_NETWORK': True}

# Server 2 (Kitchen Display)  
CONFIG = {'NETWORK_PRINTER_IP': '192.168.1.100', 'PREFER_NETWORK': True}

# Server 3 (Backup)
CONFIG = {'NETWORK_PRINTER_IP': '192.168.1.100', 'PREFER_NETWORK': False}  # USB primary
```

## ✅ Benefits for Your Restaurant

1. **Flexibility:** Place printer anywhere on network
2. **Reliability:** Automatic USB/Network failover  
3. **Speed:** Network printing often faster than USB
4. **Scalability:** Easy to add more POS stations
5. **Maintenance:** Remote printer monitoring
6. **Future-Proof:** Easy to upgrade or replace printers

The network-ready auto-recovery print server gives you the best of both worlds - the reliability of USB with the flexibility and speed of network printing! 🚀