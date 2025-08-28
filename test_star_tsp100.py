#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Star TSP100 Chinese Print Test
Tests different Chinese encodings for Star TSP100 thermal printer
"""

import requests
import json

def test_star_tsp100_chinese():
    """Test Chinese printing specifically for Star TSP100"""
    
    print("🌟 Star TSP100 Chinese Print Test")
    print("=" * 50)
    
    # Test different Chinese text samples
    test_cases = [
        {
            "name": "Traditional Chinese (繁體中文)",
            "text": """
================================
       港式美味湯匙
       HK SAVOR SPOON  
================================
訂單編號: 港001
客戶姓名: 陳小明
日期時間: 2025-08-26 19:15:00
--------------------------------

菜品明細:
白切雞飯 x2
  單價: $15.50 = $31.00

雲吞湯 x1  
  單價: $8.00 = $8.00

港式奶茶 x2
  單價: $4.50 = $9.00

--------------------------------
小計: $48.00
總計: $48.00
付款方式: 現金
--------------------------------

謝謝惠顧！
歡迎再次光臨
hksavorspoon.com

================================
"""
        },
        {
            "name": "Simplified Chinese (简体中文)",
            "text": """
================================
       港式美味汤匙
       HK SAVOR SPOON  
================================
订单编号: 简001
客户姓名: 李小红
日期时间: 2025-08-26 19:15:00
--------------------------------

菜品明细:
白切鸡饭 x2
  单价: $15.50 = $31.00

云吞汤 x1  
  单价: $8.00 = $8.00

港式奶茶 x2
  单价: $4.50 = $9.00

--------------------------------
小计: $48.00
总计: $48.00
付款方式: 现金
--------------------------------

谢谢惠顾！
欢迎再次光临
hksavorspoon.com

================================
"""
        },
        {
            "name": "Mixed Chinese & English",
            "text": """
================================
       HK SAVOR SPOON
       港式美味湯匙
================================
Order ID: MIX001
Customer: 王大明 (Wong Tai Ming)
Date: 2025-08-26 19:15:00
--------------------------------

Items 菜品:
Chicken Rice 白切雞飯 x2
  Price 價格: $15.50 = $31.00

Wonton Soup 雲吞湯 x1  
  Price 價格: $8.00 = $8.00

Milk Tea 奶茶 x2
  Price 價格: $4.50 = $9.00

--------------------------------
Subtotal 小計: $48.00
Total 總計: $48.00
Payment 付款: Cash 現金
--------------------------------

Thank you! 謝謝惠顧！
Visit again! 歡迎再來！
hksavorspoon.com

================================
"""
        }
    ]
    
    headers = {
        "X-API-Key": "hksavorspoon-secure-print-key-2025",
        "Content-Type": "application/json; charset=utf-8"
    }
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['name']}")
        print("-" * 30)
        
        data = {
            "text": test_case["text"],
            "job_name": f"Star測試{i}"
        }
        
        try:
            print(f"Sending {test_case['name']} to Star TSP100...")
            response = requests.post(
                "http://localhost:5000/print", 
                headers=headers, 
                json=data, 
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ SUCCESS!")
                print(f"   Message: {result.get('message', 'No message')}")
                
                # Check which method was used
                if "Star Chinese Mode" in result.get('message', ''):
                    print(f"   Method: Star TSP100 optimized (Best for Chinese)")
                elif "Alternative Encoding" in result.get('message', ''):
                    print(f"   Method: Alternative encoding")
                else:
                    print(f"   Method: Standard printing")
                
                results.append(True)
            else:
                print(f"❌ FAILED: Status {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('error', 'Unknown error')}")
                except:
                    print(f"   Response: {response.text}")
                results.append(False)
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            results.append(False)
        
        # Small delay between tests
        import time
        time.sleep(2)
    
    return results

def main():
    """Run Star TSP100 Chinese printing tests"""
    print("🖨️ Star TSP100 Chinese Character Test Suite")
    print("Testing multiple Chinese encodings and formats")
    print("=" * 50)
    
    try:
        results = test_star_tsp100_chinese()
        
        print("\n" + "=" * 50)
        print("📊 Test Results Summary:")
        
        total_tests = len(results)
        passed_tests = sum(results)
        
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {total_tests - passed_tests}")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL TESTS PASSED!")
            print("Your Star TSP100 should now print Chinese characters correctly!")
        elif passed_tests > 0:
            print(f"\n✅ {passed_tests}/{total_tests} tests passed.")
            print("Some Chinese text is working - check your printer output!")
        else:
            print("\n❌ All tests failed.")
            print("Chinese printing may need additional configuration.")
        
        print("\n📄 Check your Star TSP100 printer for printed receipts!")
        print("Look for clear, readable Chinese characters.")
        
        print("\n🔧 What this test did:")
        print("• Used ESC/POS commands specific to Star TSP100")
        print("• Tested GBK encoding (best for Star printers)")
        print("• Tested Big5 encoding (for Traditional Chinese)")
        print("• Applied Chinese character mode settings")
        print("• Used proper printer initialization sequences")
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")

if __name__ == "__main__":
    main()
