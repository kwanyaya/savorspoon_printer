# HK Savor Spoon - Windows Print Server

A lightweight, reliable Python-based print server that receives print jobs from your Laravel web application and prints to local USB thermal printers with full Chinese character support.

## 🚀 Quick Start

1. **Download & Setup**: Clone or download this repository
2. **Run Setup**: Double-click `setup.bat` (run as Administrator)
3. **Connect Printer**: Connect USB printer and set as default
4. **Start Server**: Double-click `start_server.bat`
5. **Test**: Run `python test_server.py`

## 📋 System Requirements

- **Operating System**: Windows 10/11
- **Python**: 3.8 or newer
- **Printer**: USB thermal printer (Star TSP143, Zebra ZD888, Epson TM-T20, etc.)
- **Network**: Internet connection for web integration
- **Hardware**: Any modern Windows PC

## 🔧 Installation Guide

### Step 1: Install Python
1. Download Python 3.8+ from [python.org](https://python.org/downloads/)
2. **IMPORTANT**: Check "Add Python to PATH" during installation
3. Verify: Open Command Prompt and run `python --version`

### Step 2: Download Files
1. Download all files to a folder (e.g., `C:\HKSavorSpoon\`)
2. Keep all files in the same directory

### Step 3: Run Setup
**Option A (Recommended)**: 
- Right-click `setup.bat` → "Run as administrator"

**Option B (Manual)**:
```cmd
pip install flask flask-cors pywin32
```

### Step 4: Configure Printer
1. Connect your thermal printer via USB
2. Install printer drivers (usually auto-detected)
3. Set as default printer:
   - Settings → Printers & scanners
   - Select your printer → Manage → Set as default

### Step 5: Configure Security
1. Edit `windows_print_server.py`
2. Change the API key:
   ```python
   API_KEY = "your-secure-unique-key-here"
   ```

### Step 6: Start Server
- Double-click `start_server.bat`, or
- Run: `python windows_print_server.py`

## 🖨️ Printer Compatibility

### Fully Tested Printers
- **Star TSP143III** - Excellent Chinese support
- **Zebra ZD888** - Good compatibility
- **Epson TM-T20II** - Works well

### Character Set Support
- **English**: Full ASCII support
- **Chinese Simplified**: GBK/GB2312 encoding
- **Chinese Traditional**: Big5 encoding
- **Mixed Text**: English + Chinese in same document

## 🌐 Network Configuration

### Local Network Setup

1. **Find Your IP Address**:
   ```cmd
   ipconfig
   ```
   Look for "IPv4 Address" (e.g., 192.168.1.100)

2. **Windows Firewall**:
   - Windows Defender Firewall → Advanced settings
   - Inbound Rules → New Rule → Port → TCP → 5000 → Allow
   - Or let `setup.bat` configure it automatically

### Internet Access (Port Forwarding)

1. **Router Configuration**:
   - Access router admin (usually http://192.168.1.1)
   - Find "Port Forwarding" or "Virtual Server" settings
   - Add rule:
     - External Port: 5000
     - Internal IP: Your PC IP (from ipconfig)
     - Internal Port: 5000
     - Protocol: TCP

2. **Find Your Public IP**:
   - Visit [whatismyip.com](https://whatismyip.com)
   - Note your public IP address

3. **Test External Access**:
   ```bash
   # From any internet connection
   curl http://YOUR-PUBLIC-IP:5000/status
   ```

### Dynamic DNS (Recommended for Production)
- Use services like [No-IP](https://noip.com) or [DuckDNS](https://duckdns.org)
- Creates a permanent domain name for your dynamic IP
- Example: `hksavorspoon-printer.ddns.net`

## 🔗 Laravel Integration

### Environment Configuration

Add to your Laravel `.env` file:
```env
WINDOWS_PRINT_SERVER_URL=http://your-domain-or-ip:5000
WINDOWS_PRINT_SERVER_API_KEY=your-secure-unique-key-here
```

### Service Class Example

```php
<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class PrintService
{
    private $serverUrl;
    private $apiKey;

    public function __construct()
    {
        $this->serverUrl = env('WINDOWS_PRINT_SERVER_URL');
        $this->apiKey = env('WINDOWS_PRINT_SERVER_API_KEY');
    }

    /**
     * Print a receipt for an order
     */
    public function printReceipt($orderData)
    {
        try {
            $response = Http::withHeaders([
                'X-API-Key' => $this->apiKey,
                'Content-Type' => 'application/json'
            ])->timeout(30)->post($this->serverUrl . '/print', [
                'receipt_data' => [
                    'order_id' => $orderData['id'],
                    'customer_name' => $orderData['customer_name'],
                    'items' => $orderData['items'],
                    'total' => $orderData['total'],
                    'payment_method' => $orderData['payment_method'],
                    'order_time' => $orderData['created_at']
                ],
                'job_name' => 'Order #' . $orderData['id']
            ]);

            if ($response->successful()) {
                Log::info('Print job sent successfully', ['order_id' => $orderData['id']]);
                return true;
            } else {
                Log::error('Print job failed', [
                    'order_id' => $orderData['id'],
                    'error' => $response->body()
                ]);
                return false;
            }

        } catch (\Exception $e) {
            Log::error('Print service error', [
                'order_id' => $orderData['id'] ?? 'unknown',
                'error' => $e->getMessage()
            ]);
            return false;
        }
    }

    /**
     * Print simple text
     */
    public function printText($text, $jobName = 'HK Savor Spoon Print')
    {
        try {
            $response = Http::withHeaders([
                'X-API-Key' => $this->apiKey,
                'Content-Type' => 'application/json'
            ])->timeout(30)->post($this->serverUrl . '/print', [
                'text' => $text,
                'job_name' => $jobName
            ]);

            return $response->successful();

        } catch (\Exception $e) {
            Log::error('Print text error', ['error' => $e->getMessage()]);
            return false;
        }
    }

    /**
     * Test server connection
     */
    public function testConnection()
    {
        try {
            $response = Http::timeout(10)->get($this->serverUrl . '/status');
            return $response->successful();
        } catch (\Exception $e) {
            return false;
        }
    }

    /**
     * Send test print
     */
    public function sendTestPrint()
    {
        try {
            $response = Http::withHeaders([
                'X-API-Key' => $this->apiKey
            ])->timeout(30)->post($this->serverUrl . '/test-print');

            return $response->successful();

        } catch (\Exception $e) {
            Log::error('Test print error', ['error' => $e->getMessage()]);
            return false;
        }
    }
}
```

### Controller Example

```php
<?php

namespace App\Http\Controllers;

use App\Services\PrintService;
use Illuminate\Http\Request;

class OrderController extends Controller
{
    private $printService;

    public function __construct(PrintService $printService)
    {
        $this->printService = $printService;
    }

    public function processOrder(Request $request)
    {
        // Process order logic...
        $order = $this->createOrder($request->all());

        // Print receipt
        $printSuccess = $this->printService->printReceipt([
            'id' => $order->id,
            'customer_name' => $order->customer_name,
            'items' => $order->items->map(function($item) {
                return [
                    'name' => $item->name,
                    'quantity' => $item->quantity,
                    'price' => $item->price
                ];
            })->toArray(),
            'total' => $order->total,
            'payment_method' => $order->payment_method,
            'created_at' => $order->created_at->format('Y-m-d H:i:s')
        ]);

        return response()->json([
            'success' => true,
            'order_id' => $order->id,
            'print_status' => $printSuccess ? 'printed' : 'print_failed'
        ]);
    }
}
```

## 📡 API Reference

### Public Endpoints

#### GET `/status`
Get server status and information
```bash
curl http://localhost:5000/status
```

**Response:**
```json
{
    "status": "online",
    "server": "HK Savor Spoon Windows Print Server",
    "version": "2.0",
    "computer": "PC-NAME",
    "local_ip": "192.168.1.100",
    "default_printer": "Star TSP143III",
    "timestamp": "2025-08-28T10:30:00"
}
```

### Protected Endpoints (Require API Key)

#### GET `/printers`
List available printers
```bash
curl -H "X-API-Key: your-api-key" http://localhost:5000/printers
```

#### POST `/print`
Print text or receipt
```bash
# Simple text
curl -H "X-API-Key: your-api-key" \
     -H "Content-Type: application/json" \
     -d '{"text":"Hello World 你好世界","job_name":"Test"}' \
     http://localhost:5000/print

# Receipt
curl -H "X-API-Key: your-api-key" \
     -H "Content-Type: application/json" \
     -d '{
       "receipt_data": {
         "order_id": "ORDER001",
         "customer_name": "张三",
         "items": [
           {"name": "叉烧饭", "quantity": 2, "price": 15.50}
         ],
         "total": "31.00",
         "payment_method": "现金"
       }
     }' \
     http://localhost:5000/print
```

#### POST `/test-print`
Send a test print
```bash
curl -H "X-API-Key: your-api-key" \
     -X POST \
     http://localhost:5000/test-print
```

## 🧪 Testing Your Setup

### Comprehensive Test Suite
Run the built-in test suite:
```cmd
python test_server.py
```

### Test with External URL
```cmd
python test_server.py --external-url http://your-domain:5000
```

### Manual Testing Steps

1. **Local Status Check**:
   ```cmd
   curl http://localhost:5000/status
   ```

2. **Network Status Check** (from another device):
   ```cmd
   curl http://YOUR-PC-IP:5000/status
   ```

3. **External Access Check**:
   ```cmd
   curl http://YOUR-PUBLIC-IP:5000/status
   ```

## 🚨 Troubleshooting

### Common Issues & Solutions

#### "Python not found"
- **Cause**: Python not installed or not in PATH
- **Solution**: Reinstall Python, ensure "Add to PATH" is checked

#### "No default printer found"
- **Cause**: No printer configured as default
- **Solution**: 
  1. Connect printer via USB
  2. Install drivers
  3. Set as default in Windows Settings

#### "Connection refused" / "Can't connect"
- **Cause**: Firewall blocking or server not running
- **Solution**:
  1. Check if server is running
  2. Run `setup.bat` as Administrator to configure firewall
  3. Verify IP address with `ipconfig`

#### "Unauthorized" errors
- **Cause**: API key mismatch
- **Solution**: Verify API keys match in Laravel and Python server

#### Print jobs fail silently
- **Cause**: Printer issues or encoding problems
- **Solution**:
  1. Check printer status (paper, drivers)
  2. Review `print_server.log` for errors
  3. Try test print: `python test_server.py`

#### External access not working
- **Cause**: Port forwarding not configured
- **Solution**:
  1. Configure router port forwarding (port 5000)
  2. Check public IP address
  3. Test with: `python test_server.py --external-url http://YOUR-PUBLIC-IP:5000`

#### Chinese characters not printing correctly
- **Cause**: Encoding or printer compatibility issues
- **Solution**:
  1. Ensure printer supports Chinese character sets
  2. For Star printers, characters are automatically optimized
  3. Try different printers if issues persist

### Debug Mode
Enable detailed logging by editing `windows_print_server.py`:
```python
DEBUG = True
```

### Log Files
- **Print Server**: `print_server.log`
- **Laravel**: Check application logs
- **Windows**: Event Viewer → Application Logs

## 🔒 Security Best Practices

1. **Change Default API Key**: Use a strong, unique key
2. **Network Security**: Consider VPN instead of direct port forwarding
3. **IP Restrictions**: Limit access to known IP ranges
4. **Regular Updates**: Keep Windows and Python packages updated
5. **Monitor Logs**: Check for unauthorized access attempts
6. **Firewall**: Only open necessary ports

## 🔧 Maintenance

### Regular Tasks
- **Weekly**: Restart print server to clear memory
- **Monthly**: Archive old log files
- **Quarterly**: Update Python packages
- **As Needed**: Check if public IP changed

### Log Rotation
```cmd
# Archive old logs
move print_server.log print_server_backup_%date%.log
```

### Package Updates
```cmd
pip install --upgrade flask flask-cors pywin32
```

## 📁 Project Structure

```
savorspoon_printer/
├── windows_print_server.py    # Main server application
├── test_server.py            # Comprehensive test suite
├── requirements.txt          # Python dependencies
├── setup.bat                # Automatic setup script
├── start_server.bat         # Server startup script
├── README.md                # This documentation
├── print_server.log         # Log file (created at runtime)
└── .gitignore              # Git ignore rules
```

## 🆕 Version 2.0 Improvements

- **Cleaner Code**: Reduced complexity, better organization
- **Enhanced Chinese Support**: Improved encoding handling
- **Better Error Handling**: More informative error messages
- **Comprehensive Testing**: Full test suite with Chinese character tests
- **Simplified Configuration**: Fewer files, easier setup
- **Improved Documentation**: Complete guide in single file

## 📞 Support & Contribution

### Getting Help
1. Check this README for common solutions
2. Review `print_server.log` for detailed errors
3. Run `python test_server.py` for diagnostics
4. Test each component individually

### Reporting Issues
When reporting issues, please include:
- Windows version
- Python version (`python --version`)
- Printer model
- Error messages from `print_server.log`
- Steps to reproduce

## 📄 License

This project is for HK Savor Spoon internal use.

---

**HK Savor Spoon Windows Print Server v2.0**  
*Making restaurant operations seamless with reliable, multi-language printing*
