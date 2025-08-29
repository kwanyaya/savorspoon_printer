# DDNS 設置完整指南 - HK Savor Spoon 打印服務器

## 🎯 什麼是 DDNS？為什麼需要它？

### 問題：動態 IP 地址
- 大多數家庭/辦公網路使用**動態 IP**，IP 地址會不定期變化
- 當 IP 變化時，您的 POS 系統無法找到打印服務器
- 導致打印功能突然失效

### 解決方案：DDNS (動態 DNS)
DDNS 為您的動態 IP 創建一個**固定的域名地址**，就像給您的店鋪一個永久的門牌號碼。

**工作原理：**
```
您的店鋪 IP: 203.0.113.5 (今天)
DDNS 域名: hksavorspoon.ddns.net ──→ 自動指向 → 203.0.113.5

明天 IP 變成: 198.51.100.20
DDNS 域名: hksavorspoon.ddns.net ──→ 自動更新 → 198.51.100.20
```

## 🚀 快速設置步驟

### 第一步：選擇 DDNS 服務商

#### 推薦服務商對比

| 服務商 | 免費方案 | 特色 | 適合對象 |
|-------|---------|------|---------|
| **DuckDNS** | ✅ 無限制 | 完全免費，設置簡單 | 🏆 **首選推薦** |
| **No-IP** | ✅ 最多3個域名 | 老牌穩定，功能豐富 | 商業用戶 |
| **Dynu** | ✅ 最多4個域名 | 功能強大，支持多種記錄 | 技術用戶 |

### 第二步：註冊 DDNS 帳號

#### DuckDNS 註冊 (推薦)
1. 訪問：https://www.duckdns.org
2. 點擊 "Sign in" → 選擇 Google/GitHub 等方式登入
3. 創建您的域名，例如：`hksavorspoon.duckdns.org`
4. 記下您的 **Token**（這是您的密碼）

#### No-IP 註冊
1. 訪問：https://www.noip.com
2. 點擊 "Sign Up" 註冊免費帳號
3. 創建主機名，例如：`hksavorspoon.ddns.net`
4. 記下用戶名和密碼

### 第三步：路由器 DDNS 設置

#### 常見路由器品牌設置

##### 🔧 ASUS 路由器
1. 瀏覽器打開：`192.168.1.1`
2. 登入路由器管理介面
3. **進階設定** → **WAN** → **DDNS**
4. 填寫設置：
   ```
   啟用 DDNS 客戶端: 是
   伺服器: Custom (自定義)
   主機名稱: hksavorspoon.duckdns.org
   使用者名稱: (DuckDNS 留空)
   密碼: [您的 DuckDNS Token]
   ```

##### 🔧 TP-Link 路由器
1. 瀏覽器打開：`192.168.0.1` 或 `192.168.1.1`
2. **進階** → **網路** → **動態 DNS**
3. 填寫設置：
   ```
   服務提供者: No-IP 或自定義
   域名: hksavorspoon.ddns.net
   使用者名稱: [您的帳號]
   密碼: [您的密碼]
   ```

##### 🔧 D-Link 路由器
1. 瀏覽器打開：`192.168.0.1`
2. **工具** → **動態 DNS**
3. 啟用並填寫 DDNS 信息

##### 🔧 Netgear 路由器
1. 瀏覽器打開：`192.168.1.1`
2. **動態 DNS** → **設置**
3. 選擇服務商並填寫信息

### 第四步：端口轉發設置

確保您的路由器已設置端口轉發：
```
外部端口: 5000
內部 IP: [您電腦的 IP，例如 192.168.1.100]
內部端口: 5000
協議: TCP
```

### 第五步：使用 DDNS 工具配置

運行我們的 DDNS 配置工具：
```bash
python ddns_helper.py
```

按照提示完成配置：
1. 選擇 "2. 配置 DDNS 設置"
2. 輸入您的 DDNS 信息
3. 選擇 "4. 測試 DDNS 訪問" 驗證設置

## 🧪 測試您的 DDNS 設置

### 1. 測試域名解析
```bash
# Windows 命令提示符
nslookup hksavorspoon.duckdns.org

# 應該返回您的公網 IP
```

### 2. 測試打印服務器訪問
```bash
# 瀏覽器中訪問
http://hksavorspoon.duckdns.org:5000/status

# 應該看到服務器狀態信息
```

### 3. 使用測試工具
```bash
python ddns_helper.py
# 選擇 "4. 測試 DDNS 訪問"
```

## 🔧 Laravel 整合

### 更新您的 .env 文件
```env
# 舊的設置 (會失效)
# WINDOWS_PRINT_SERVER_URL=http://203.0.113.5:5000

# 新的 DDNS 設置 (永久有效)
WINDOWS_PRINT_SERVER_URL=http://hksavorspoon.duckdns.org:5000
WINDOWS_PRINT_SERVER_API_KEY=hksavorspoon-secure-print-key-2025
```

### PHP 代碼示例
```php
// 測試連接
public function testPrintServer()
{
    $response = Http::timeout(10)->get(env('WINDOWS_PRINT_SERVER_URL') . '/status');
    
    if ($response->successful()) {
        $data = $response->json();
        return "✅ 連接成功！打印機: " . $data['default_printer'];
    } else {
        return "❌ 連接失敗";
    }
}

// 發送打印
public function printReceipt($orderData)
{
    $response = Http::withHeaders([
        'X-API-Key' => env('WINDOWS_PRINT_SERVER_API_KEY'),
        'Content-Type' => 'application/json'
    ])->timeout(30)->post(env('WINDOWS_PRINT_SERVER_URL') . '/print', [
        'receipt_data' => [
            'order_id' => $orderData['id'],
            'customer_name' => $orderData['customer_name'],
            'items' => $orderData['items'],
            'total' => $orderData['total'],
            'payment_method' => $orderData['payment_method']
        ]
    ]);

    return $response->successful();
}
```

## 🔍 故障排除

### 常見問題

#### ❌ 域名無法解析
**原因：** DDNS 更新失敗或路由器配置錯誤
**解決：**
1. 檢查路由器 DDNS 設置
2. 確認帳號密碼正確
3. 手動更新 DDNS：`python ddns_helper.py` → 選項 3

#### ❌ 可以解析但無法訪問打印服務器
**原因：** 端口轉發或防火牆問題
**解決：**
1. 檢查路由器端口轉發設置 (5000 端口)
2. 檢查 Windows 防火牆
3. 確認打印服務器正在運行

#### ❌ 間歇性連接失敗
**原因：** IP 變化但 DDNS 未及時更新
**解決：**
1. 啟用 DDNS 監控：`python ddns_helper.py` → 選項 6
2. 縮短更新間隔時間
3. 檢查路由器 DDNS 客戶端狀態

### 高級故障排除

#### 檢查 DDNS 更新日誌
```bash
# 運行監控工具查看詳細日誌
python ddns_helper.py
# 選擇 "6. 開始 DDNS 監控"
```

#### 手動驗證 IP 變化
```bash
# 檢查當前公網 IP
curl https://api.ipify.org

# 比較域名解析的 IP
nslookup hksavorspoon.duckdns.org
```

## 🎯 最佳實踐

### 1. 定期監控
- 設置 DDNS 自動監控：`python ddns_helper.py` → 選項 6
- 每5分鐘檢查一次 IP 變化

### 2. 備份方案
- 配置多個 DDNS 服務商
- 記錄當前配置以便恢復

### 3. 安全考慮
- 使用強密碼
- 定期更換 API 密鑰
- 監控訪問日誌

### 4. 性能優化
- 選擇響應速度快的 DDNS 服務商
- 適當調整更新間隔
- 定期測試連接穩定性

## 📞 技術支持

如果設置過程中遇到問題：

1. **運行診斷工具**：
   ```bash
   python ddns_helper.py
   # 使用各種測試功能
   ```

2. **檢查日誌**：
   - 路由器系統日誌
   - 打印服務器日誌 (`print_server.log`)

3. **聯繫技術支持**時請提供：
   - 路由器型號
   - DDNS 服務商
   - 錯誤信息截圖
   - 診斷工具輸出

---

通過正確設置 DDNS，您的 HK Savor Spoon 打印系統將實現真正的**穩定遠程訪問**，不再受動態 IP 變化影響！
