# 🚀 HK Savor Spoon Website Integration Guide

## ✅ Port Forwarding Complete!
Your router is now configured to forward external requests to your print server.

## 🌐 Your Public Print Server URLs

### **Base URL**: `http://58.153.166.26:5000`
### **Key Endpoints**:
- **Status**: `http://58.153.166.26:5000/status`
- **Print**: `http://58.153.166.26:5000/print`
- **Test Print**: `http://58.153.166.26:5000/test-print`

## 📝 API Integration for Your Website

### **1. Environment Configuration (.env)**
```env
# HK Savor Spoon Print Server
WINDOWS_PRINT_SERVER_URL=http://58.153.166.26:5000
WINDOWS_PRINT_SERVER_API_KEY=hksavorspoon-secure-print-key-2025
WINDOWS_PRINT_SERVER_TIMEOUT=30
```

### **2. Laravel Controller Example**
```php
<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class PrintController extends Controller
{
    private $printServerUrl;
    private $apiKey;
    
    public function __construct()
    {
        $this->printServerUrl = env('WINDOWS_PRINT_SERVER_URL');
        $this->apiKey = env('WINDOWS_PRINT_SERVER_API_KEY');
    }
    
    public function printReceipt(Request $request)
    {
        try {
            // Format receipt text
            $receiptText = $this->formatReceipt($request->all());
            
            // Send to print server
            $response = Http::timeout(30)
                ->withHeaders([
                    'X-API-Key' => $this->apiKey,
                    'Content-Type' => 'application/json'
                ])
                ->post($this->printServerUrl . '/print', [
                    'text' => $receiptText,
                    'font_size' => 'large',
                    'job_name' => 'HK_Savor_Spoon_Order_' . $request->order_id
                ]);
            
            if ($response->successful()) {
                Log::info('Print successful', ['order_id' => $request->order_id]);
                return response()->json([
                    'success' => true,
                    'message' => 'Receipt printed successfully'
                ]);
            } else {
                Log::error('Print failed', ['response' => $response->body()]);
                return response()->json([
                    'success' => false,
                    'message' => 'Print server error'
                ], 500);
            }
            
        } catch (\Exception $e) {
            Log::error('Print exception', ['error' => $e->getMessage()]);
            return response()->json([
                'success' => false,
                'message' => 'Print service unavailable'
            ], 500);
        }
    }
    
    private function formatReceipt($orderData)
    {
        $receipt = "========================================\n";
        $receipt .= "         港式美味湯匙\n";
        $receipt .= "         HK SAVOR SPOON\n";
        $receipt .= "========================================\n\n";
        
        $receipt .= "訂單編號: " . $orderData['order_id'] . "\n";
        $receipt .= "日期: " . date('y-m-d H:i') . "\n\n";
        
        // Add items
        foreach ($orderData['items'] as $item) {
            $receipt .= $item['name'] . "\n";
            $receipt .= str_repeat(' ', 25) . "$" . $item['price'] . "\n\n";
        }
        
        $receipt .= "——————————————————\n";
        $receipt .= "總計:" . str_repeat(' ', 20) . "$" . $orderData['total'] . "\n\n";
        
        $receipt .= "==================\n";
        $receipt .= "  謝謝您的訂購！\n";
        $receipt .= "==================\n";
        
        return $receipt;
    }
    
    public function checkPrintServer()
    {
        try {
            $response = Http::timeout(10)
                ->get($this->printServerUrl . '/status');
            
            return response()->json([
                'available' => $response->successful(),
                'data' => $response->json()
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'available' => false,
                'error' => $e->getMessage()
            ]);
        }
    }
}
```

### **3. JavaScript/AJAX Example**
```javascript
// Print receipt function
async function printReceipt(orderData) {
    try {
        const response = await fetch('http://58.153.166.26:5000/print', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': 'hksavorspoon-secure-print-key-2025'
            },
            body: JSON.stringify({
                text: formatReceiptText(orderData),
                font_size: 'large',
                job_name: `HK_Order_${orderData.order_id}`
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log('Print successful:', result.message);
            return { success: true, message: result.message };
        } else {
            console.error('Print failed:', response.status);
            return { success: false, message: 'Print server error' };
        }
    } catch (error) {
        console.error('Print error:', error);
        return { success: false, message: 'Network error' };
    }
}

// Format receipt text
function formatReceiptText(orderData) {
    let receipt = `========================================
         港式美味湯匙
         HK SAVOR SPOON
========================================

訂單編號: ${orderData.order_id}
日期: ${new Date().toLocaleString('zh-HK')}

`;

    // Add items
    orderData.items.forEach(item => {
        receipt += `${item.name}
${' '.repeat(25)}$${item.price}

`;
    });

    receipt += `——————————————————
總計:${' '.repeat(20)}$${orderData.total}

==================
  謝謝您的訂購！
==================`;

    return receipt;
}

// Check if print server is available
async function checkPrintServer() {
    try {
        const response = await fetch('http://58.153.166.26:5000/status');
        return response.ok;
    } catch (error) {
        return false;
    }
}
```

## 🧪 Testing Commands

### **Test from any computer/server:**
```bash
# Test status
curl http://58.153.166.26:5000/status

# Test printing
curl -X POST http://58.153.166.26:5000/print \
  -H "Content-Type: application/json" \
  -H "X-API-Key: hksavorspoon-secure-print-key-2025" \
  -d '{
    "text": "Test from external server\n港式美味湯匙\nHK Savor Spoon\nExternal test successful!",
    "font_size": "large",
    "job_name": "External_Test"
  }'
```

## 📱 Mobile/Tablet Testing

Your print server is now accessible from any device with internet access:
- **Mobile apps** can print directly
- **Tablets** at your restaurant can print
- **Remote locations** can send print jobs

## 🔒 Security Considerations

### **API Key Protection:**
- Keep your API key (`hksavorspoon-secure-print-key-2025`) secure
- Consider rotating it periodically
- Don't expose it in client-side code

### **Network Security:**
- Only port 5000 is forwarded (secure)
- Print server logs all access attempts
- Monitor `print_server.log` for unusual activity

## 📊 Monitoring & Maintenance

### **Check Print Server Status:**
```powershell
# Local check
curl http://192.168.0.184:5000/status

# External check  
curl http://58.153.166.26:5000/status
```

### **Log Files:**
- **Print Server Log**: `print_server.log`
- **Windows Event Log**: Check for printer-related events

## 🚀 Your Print Server is Now Live!

**Public URL**: `http://58.153.166.26:5000`
**Status**: Ready for HK Savor Spoon integration
**Printer**: Star TSP100 with Chinese character support
**Font**: Large, readable receipts

Your customers' orders can now be printed directly to your restaurant's thermal printer from anywhere in the world! 🌍🖨️
