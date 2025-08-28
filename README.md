# HK Savor Spoon - Windows Print Server

A Python-based print server that receives print jobs from your Laravel web application and prints to a local USB thermal printer.

## 🚀 Quick Start

1. **Run Setup**: Double-click `setup.bat` (run as Administrator)
2. **Connect Printer**: Connect USB printer and set as default
3. **Configure Firewall**: Allow port 5000 through Windows Firewall
4. **Start Server**: Double-click `start_server.bat`
5. **Test**: Run `python test_server.py`

## 📋 Requirements

- Windows 10/11
- Python 3.8 or newer
- USB thermal printer (Star TSP143, Zebra ZD888, etc.)
- Internet connection
- Router with port forwarding capability

## 🔧 Installation

### Method 1: Automatic Setup (Recommended)
1. Download all files to a folder (e.g., `C:\HKSavorSpoon\`)
2. Right-click `setup.bat` → "Run as administrator"
3. Follow the prompts

### Method 2: Manual Setup
```cmd
# Install Python packages
pip install flask flask-cors pywin32

# Or use requirements file
pip install -r requirements.txt
```

## 🖨️ Printer Setup

1. Connect your thermal printer via USB
2. Install drivers (usually auto-detected)
3. Set as default printer:
   - Settings → Printers & scanners
   - Select printer → Manage → Set as default

## 🔑 Configuration

### API Key
Edit `windows_print_server.py` and change the API key:
```python
API_KEY = "your-secure-api-key-here"
```

### Port Configuration (Optional)
Default port is 5000. To change:
```python
PORT = 5000  # Change to your preferred port
```

## 🌐 Network Setup

### 1. Windows Firewall
Create inbound rule for port 5000:
1. Windows Defender Firewall → Advanced settings
2. Inbound Rules → New Rule
3. Port → TCP → Specific port: 5000
4. Allow the connection → All profiles
5. Name: "HKSavorSpoon Print Server"

### 2. Find Your Local IP
```cmd
ipconfig
```
Look for "IPv4 Address" (e.g., 192.168.1.100)

### 3. Router Port Forwarding
1. Access router admin (usually http://192.168.1.1)
2. Port Forwarding settings
3. Add rule:
   - External Port: 5000
   - Internal IP: Your PC IP
   - Internal Port: 5000
   - Protocol: TCP

### 4. Dynamic DNS (Optional but Recommended)
- Sign up for free DDNS (No-IP, DuckDNS)
- Choose hostname (e.g., hksavorspoon-printer.ddns.net)
- Install DDNS client on Windows

## 🏃‍♂️ Running the Server

### Start Server
```cmd
python windows_print_server.py
```
Or double-click `start_server.bat`

### As Windows Service (Production)
1. Download NSSM from https://nssm.cc/
2. Install service:
```cmd
nssm install HKSavorSpoonPrintServer
```
3. Configure:
   - Path: `C:\Python\python.exe`
   - Startup directory: `C:\HKSavorSpoon`
   - Arguments: `windows_print_server.py`

## 🧪 Testing

### Local Testing
```cmd
# Test server status
curl http://localhost:5000/status

# Run test suite
python test_server.py
```

### Remote Testing
From another device:
```cmd
curl http://YOUR-PUBLIC-IP:5000/status
```

## 📡 API Endpoints

### GET `/status`
Server status and information
```json
{
    "status": "online",
    "server": "HK Savor Spoon Windows Print Server",
    "computer": "PC-NAME",
    "local_ip": "192.168.1.100",
    "default_printer": "Printer Name",
    "timestamp": "2025-08-26T10:30:00"
}
```

### GET `/printers`
List available printers (requires API key)
```bash
curl -H "X-API-Key: your-api-key" http://localhost:5000/printers
```

### POST `/print`
Print text or receipt (requires API key)

**Simple Text:**
```bash
curl -H "X-API-Key: your-api-key" \
     -H "Content-Type: application/json" \
     -d '{"text":"Hello World","job_name":"Test"}' \
     http://localhost:5000/print
```

**Receipt:**
```bash
curl -H "X-API-Key: your-api-key" \
     -H "Content-Type: application/json" \
     -d '{
       "receipt_data": {
         "order_id": "ORDER001",
         "customer_name": "John Doe",
         "items": [
           {"name": "Chicken Rice", "quantity": 2, "price": 15.50}
         ],
         "total": "31.00",
         "payment_method": "Cash"
       }
     }' \
     http://localhost:5000/print
```

### POST `/test-print`
Send a test print (requires API key)
```bash
curl -H "X-API-Key: your-api-key" \
     -X POST \
     http://localhost:5000/test-print
```

## 🔗 Laravel Integration

### Environment Variables
Add to your Laravel `.env`:
```env
WINDOWS_PRINT_SERVER_URL=http://your-ddns-hostname:5000
WINDOWS_PRINT_SERVER_API_KEY=your-secure-api-key-here
```

### Example PHP Code
```php
<?php

class WindowsPrintService
{
    private $serverUrl;
    private $apiKey;

    public function __construct()
    {
        $this->serverUrl = env('WINDOWS_PRINT_SERVER_URL');
        $this->apiKey = env('WINDOWS_PRINT_SERVER_API_KEY');
    }

    public function printReceipt($orderData)
    {
        $url = $this->serverUrl . '/print';
        
        $data = [
            'receipt_data' => [
                'order_id' => $orderData['id'],
                'customer_name' => $orderData['customer_name'],
                'items' => $orderData['items'],
                'total' => $orderData['total'],
                'payment_method' => $orderData['payment_method'],
                'order_time' => $orderData['created_at']
            ],
            'job_name' => 'Order #' . $orderData['id']
        ];

        $response = Http::withHeaders([
            'X-API-Key' => $this->apiKey,
            'Content-Type' => 'application/json'
        ])->post($url, $data);

        return $response->successful();
    }

    public function testConnection()
    {
        $response = Http::get($this->serverUrl . '/status');
        return $response->successful();
    }
}
```

## 🐛 Troubleshooting

### Common Issues

**"No default printer found"**
- Connect printer and install drivers
- Set printer as default in Windows settings

**"Connection refused"**
- Check Windows Firewall settings
- Verify port forwarding configuration
- Confirm PC IP address

**"Unauthorized" errors**
- Verify API key matches in Laravel and Python
- Check request headers

**Print jobs fail**
- Check printer status (paper, toner)
- Review `print_server.log` for errors

### Log Files
- Print server: `print_server.log`
- Laravel: Check application logs

### Debug Mode
Enable debug logging by setting `DEBUG = True` in the Python file.

## 🔒 Security

1. **Change Default API Key**: Use a strong, unique key
2. **Network Security**: Consider VPN instead of port forwarding
3. **IP Restrictions**: Limit access to known IP ranges
4. **Regular Updates**: Keep Windows and packages updated
5. **Monitor Logs**: Check for unauthorized access

## 🔧 Maintenance

- **Regular Restarts**: Restart print server weekly
- **Log Rotation**: Archive old logs monthly
- **IP Monitoring**: Check if public IP changed
- **Printer Care**: Clean printer, replace consumables

## 📁 File Structure

```
printer_server/
├── windows_print_server.py    # Main server application
├── requirements.txt           # Python dependencies
├── setup.bat                 # Automatic setup script
├── start_server.bat          # Server startup script
├── test_server.py            # Test suite
├── print_server.log          # Log file (created at runtime)
└── README.md                 # This file
```

## 📞 Support

If you encounter issues:
1. Check troubleshooting section above
2. Review log files for errors
3. Run `python test_server.py` for diagnostics
4. Test each component individually

## 📄 License

This project is for HK Savor Spoon internal use.

---

**HK Savor Spoon** - Making restaurant operations seamless
