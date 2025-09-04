#!/usr/bin/env python3
"""
Performance Test Script for HK Savor Spoon Print Server
Tests both normal and fast print endpoints
"""

import requests
import time
import json
import statistics
from datetime import datetime

# Configuration
SERVER_URL = "http://localhost:8080"
API_KEY = "hksavorspoon-secure-print-key-2025"
HEADERS = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

# Test data
SIMPLE_RECEIPT = """
================================
    HK SAVOR SPOON RESTAURANT
================================
Date: 2025-09-04 16:30:00
Order #: 12345

Items:
- Kung Pao Chicken    $12.50
- Fried Rice          $8.00
- Hot Tea             $3.50

Subtotal:            $24.00
Tax:                  $2.40
Total:               $26.40

Thank you for dining with us!
================================
"""

COMPLEX_RECEIPT = """
================================
    HK SAVOR SPOON RESTAURANT
    香港美味勺子餐廳
================================
Date: 2025-09-04 16:30:00
Order #: 12345
Table: 5
Server: Alice

Items:
- 宫保鸡丁 Kung Pao Chicken    $12.50
- 炒饭 Fried Rice              $8.00
- 热茶 Hot Tea                 $3.50
- 甜酸排骨 Sweet & Sour Pork   $15.80
- 蒸饺 Steamed Dumplings       $9.90

Subtotal:            $49.70
Tax (8.5%):          $4.22
Service (15%):       $7.46
Total:               $61.38

Payment: Credit Card
Card: ****1234

Thank you for dining with us!
谢谢光临！
================================
"""

def test_endpoint(endpoint, data, test_name):
    """Test a specific endpoint and return timing results"""
    print(f"\n🧪 Testing {test_name}...")
    
    times = []
    errors = 0
    
    for i in range(10):  # 10 test requests
        try:
            start_time = time.time()
            response = requests.post(f"{SERVER_URL}/{endpoint}", 
                                   headers=HEADERS, 
                                   json=data, 
                                   timeout=10)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            times.append(response_time)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"  ✅ Request {i+1}: {response_time:.1f}ms")
                else:
                    print(f"  ❌ Request {i+1}: {response_time:.1f}ms - {result.get('message', 'Unknown error')}")
                    errors += 1
            else:
                print(f"  ❌ Request {i+1}: {response_time:.1f}ms - HTTP {response.status_code}")
                errors += 1
                
        except Exception as e:
            print(f"  💥 Request {i+1}: Error - {str(e)}")
            errors += 1
        
        # Small delay between requests
        time.sleep(0.1)
    
    if times:
        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        median_time = statistics.median(times)
        
        print(f"\n📊 {test_name} Results:")
        print(f"  Average: {avg_time:.1f}ms")
        print(f"  Median:  {median_time:.1f}ms")
        print(f"  Min:     {min_time:.1f}ms")
        print(f"  Max:     {max_time:.1f}ms")
        print(f"  Errors:  {errors}/10")
        
        return {
            'average': avg_time,
            'median': median_time,
            'min': min_time,
            'max': max_time,
            'errors': errors
        }
    else:
        print(f"❌ All requests failed for {test_name}")
        return None

def main():
    print("🚀 HK Savor Spoon Print Server Performance Test")
    print("=" * 60)
    
    # Check server status first
    try:
        response = requests.get(f"{SERVER_URL}/status", timeout=5)
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Server online: {status.get('server', 'Unknown')}")
            print(f"📄 Version: {status.get('version', 'Unknown')}")
        else:
            print(f"❌ Server returned HTTP {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return
    
    # Test scenarios
    results = {}
    
    # Test 1: Normal print with simple receipt
    results['normal_simple'] = test_endpoint(
        'print', 
        {'text': SIMPLE_RECEIPT}, 
        'Normal Print (Simple Receipt)'
    )
    
    # Test 2: Fast print with simple receipt  
    results['fast_simple'] = test_endpoint(
        'fast-print', 
        {'text': SIMPLE_RECEIPT}, 
        'Fast Print (Simple Receipt)'
    )
    
    # Test 3: Normal print with complex receipt (Chinese)
    results['normal_complex'] = test_endpoint(
        'print', 
        {'text': COMPLEX_RECEIPT}, 
        'Normal Print (Complex Receipt)'
    )
    
    # Test 4: Fast print with complex receipt (Chinese)
    results['fast_complex'] = test_endpoint(
        'fast-print', 
        {'text': COMPLEX_RECEIPT}, 
        'Fast Print (Complex Receipt)'
    )
    
    # Test 5: Normal print with fast mode flag
    results['normal_fast_mode'] = test_endpoint(
        'print', 
        {'text': SIMPLE_RECEIPT, 'fast': True}, 
        'Normal Print (Fast Mode Flag)'
    )
    
    # Summary
    print("\n" + "=" * 60)
    print("📈 PERFORMANCE SUMMARY")
    print("=" * 60)
    
    for test_name, result in results.items():
        if result:
            print(f"{test_name.replace('_', ' ').title():25s}: {result['average']:6.1f}ms avg, {result['errors']:2d} errors")
    
    # Speed comparison
    if results['normal_simple'] and results['fast_simple']:
        normal_avg = results['normal_simple']['average']
        fast_avg = results['fast_simple']['average']
        speedup = normal_avg / fast_avg if fast_avg > 0 else 0
        
        print(f"\n⚡ FAST PRINT SPEEDUP:")
        print(f"   Normal: {normal_avg:.1f}ms")
        print(f"   Fast:   {fast_avg:.1f}ms")
        print(f"   Speedup: {speedup:.1f}x faster")
    
    print("\n✅ Performance test completed!")

if __name__ == "__main__":
    main()
