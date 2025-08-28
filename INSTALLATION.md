# HK Savor Spoon Print Server - Installation Guide

## 📋 Current Setup Status

Your print server files have been created successfully! Here's what you have:

### ✅ Files Created:
- `windows_print_server.py` - Main print server application
- `requirements.txt` - Python package dependencies  
- `setup.bat` - Automated setup script
- `setup.ps1` - PowerShell setup script (advanced)
- `start_server.bat` - Server startup script
- `test_server.py` - Test suite for verification
- `test_interface.html` - Web-based test interface
- `config_template.py` - Configuration template
- `README.md` - Complete documentation

## 🚀 Next Steps

### 1. Install Python (If Not Already Installed)
1. Download Python 3.8+ from: https://python.org/downloads/
2. **IMPORTANT:** During installation, check "Add Python to PATH"
3. Verify installation by opening Command Prompt and typing: `python --version`

### 2. Run the Setup
Option A (Easy): Double-click `setup.bat` (Run as Administrator)
Option B (Advanced): Run `setup.ps1` in PowerShell (Run as Administrator)

### 3. Connect Your Printer
1. Connect USB thermal printer to your PC
2. Install printer drivers (usually auto-detected)
3. Set printer as **Default Printer**:
   - Settings → Printers & scanners
   - Select your printer → Manage → Set as default

### 4. Configure Security
1. Edit `windows_print_server.py`
2. Change the API key: 
   ```python
   API_KEY = "your-secure-unique-key-here"
   ```

### 5. Start the Server
Double-click `start_server.bat` or run:
```cmd
python windows_print_server.py
```

### 6. Test the Server
Option A: Run `python test_server.py`
Option B: Open `test_interface.html` in your browser

## 🌐 Network Configuration

### Firewall Setup
The setup script will configure Windows Firewall automatically, or manually:
1. Windows Defender Firewall → Advanced settings
2. Inbound Rules → New Rule → Port → TCP → 5000 → Allow

### Router Port Forwarding
1. Access router admin panel (usually http://192.168.1.1)
2. Find "Port Forwarding" settings
3. Forward external port 5000 to your PC's internal IP port 5000

### Get Your IP Address
Run in Command Prompt: `ipconfig`
Look for "IPv4 Address" (e.g., 192.168.1.100)

## 🔧 Laravel Integration

Add to your Laravel `.env` file:
```env
WINDOWS_PRINT_SERVER_URL=http://your-ip-or-domain:5000
WINDOWS_PRINT_SERVER_API_KEY=your-secure-unique-key-here
```

### Example Laravel Code
```php
use Illuminate\Support\Facades\Http;

class PrintService 
{
    public function printReceipt($orderData) 
    {
        $response = Http::withHeaders([
            'X-API-Key' => env('WINDOWS_PRINT_SERVER_API_KEY'),
            'Content-Type' => 'application/json'
        ])->post(env('WINDOWS_PRINT_SERVER_URL') . '/print', [
            'receipt_data' => [
                'order_id' => $orderData['id'],
                'customer_name' => $orderData['customer_name'],
                'items' => $orderData['items'],
                'total' => $orderData['total'],
                'payment_method' => $orderData['payment_method'],
            ]
        ]);

        return $response->successful();
    }
}
```

## 🔍 Testing Your Setup

### 1. Local Test
Visit: http://localhost:5000/status

### 2. Network Test  
From another device: http://[your-pc-ip]:5000/status

### 3. Print Test
Use the web interface (`test_interface.html`) or run:
```bash
curl -H "X-API-Key: your-api-key" -X POST http://localhost:5000/test-print
```

## 🚨 Troubleshooting

### "Python not found"
- Install Python from python.org
- Make sure "Add to PATH" was checked during installation
- Restart Command Prompt after installation

### "No default printer found"
- Connect printer via USB
- Install drivers
- Set as default in Windows Settings

### "Connection refused"
- Check Windows Firewall
- Verify server is running
- Check IP address and port

### "Permission denied"
- Run setup scripts as Administrator
- Check User Account Control settings

## 📞 Support

If you need help:
1. Check the `README.md` for detailed troubleshooting
2. Review the `print_server.log` file for errors
3. Test each component step by step
4. Use the web test interface for debugging

## 🎉 Success Indicators

When everything is working, you should see:
- ✅ Server running on http://localhost:5000
- ✅ Default printer detected
- ✅ Test prints working
- ✅ Remote access from other devices
- ✅ Laravel integration successful

---

**HK Savor Spoon Print Server v1.0**
*Making restaurant operations seamless*
