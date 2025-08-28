# Test Traditional Chinese Support
# Run this script to test both Simplified and Traditional Chinese

Write-Host "🖨️  Testing Chinese Character Support for HK Savor Spoon" -ForegroundColor Green
Write-Host "=" * 60

# Check if server is running
try {
    $status = Invoke-RestMethod -Uri "http://localhost:5000/status" -Method GET
    Write-Host "✅ Server is running" -ForegroundColor Green
    Write-Host "📄 Printer: $($status.default_printer)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Server is not running. Please start: python windows_print_server.py" -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "📝 Testing Chinese Characters..." -ForegroundColor Yellow

# Test 1: Traditional Chinese
Write-Host ""
Write-Host "1️⃣  Testing Traditional Chinese (繁體中文)..." -ForegroundColor Blue
$traditionalText = @"
繁體中文測試
港式茶餐廳
謝謝光臨！
歡迎再來
"@

$body = @{
    text = $traditionalText
    api_key = "hk_savor_spoon_2024"
} | ConvertTo-Json -Compress

try {
    $response = Invoke-RestMethod -Uri "http://localhost:5000/print" -Method POST -Body $body -ContentType "application/json"
    Write-Host "✅ Traditional Chinese sent: $($response.message)" -ForegroundColor Green
} catch {
    Write-Host "❌ Traditional Chinese failed: $($_.Exception.Message)" -ForegroundColor Red
}

Start-Sleep -Seconds 2

# Test 2: Simplified Chinese
Write-Host ""
Write-Host "2️⃣  Testing Simplified Chinese (简体中文)..." -ForegroundColor Blue
$simplifiedText = @"
简体中文测试
港式茶餐厅
谢谢光临！
欢迎再来
"@

$body = @{
    text = $simplifiedText
    api_key = "hk_savor_spoon_2024"
} | ConvertTo-Json -Compress

try {
    $response = Invoke-RestMethod -Uri "http://localhost:5000/print" -Method POST -Body $body -ContentType "application/json"
    Write-Host "✅ Simplified Chinese sent: $($response.message)" -ForegroundColor Green
} catch {
    Write-Host "❌ Simplified Chinese failed: $($_.Exception.Message)" -ForegroundColor Red
}

Start-Sleep -Seconds 2

# Test 3: Mixed Chinese + English
Write-Host ""
Write-Host "3️⃣  Testing Mixed Characters..." -ForegroundColor Blue
$mixedText = @"
HK Savor Spoon 港式美味
简体：欢迎光临
繁體：歡迎光臨
Menu 菜单 菜單
Thank you 謝謝 谢谢
"@

$body = @{
    text = $mixedText
    api_key = "hk_savor_spoon_2024"
} | ConvertTo-Json -Compress

try {
    $response = Invoke-RestMethod -Uri "http://localhost:5000/print" -Method POST -Body $body -ContentType "application/json"
    Write-Host "✅ Mixed characters sent: $($response.message)" -ForegroundColor Green
} catch {
    Write-Host "❌ Mixed characters failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎉 Testing completed!" -ForegroundColor Green
Write-Host "📋 Please check your Star TSP100 printer output to verify:" -ForegroundColor Yellow
Write-Host "   ✓ Traditional Chinese (繁體中文) displays correctly" -ForegroundColor White
Write-Host "   ✓ Simplified Chinese (简体中文) displays correctly" -ForegroundColor White
Write-Host "   ✓ Mixed text prints properly" -ForegroundColor White
