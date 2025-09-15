#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-Recovery Print Server Test Script
=====================================
Tests the automatic recovery features
"""

import requests
import time
import json
from datetime import datetime

# Configuration
SERVER_URL = "http://localhost:8080"
API_KEY = "hksavorspoon-secure-print-key-2025"

def test_server_status():
    """Test server status and recovery information"""
    print("🔍 Testing server status...")
    try:
        response = requests.get(f"{SERVER_URL}/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server: {data.get('server', 'Unknown')}")
            print(f"✅ Version: {data.get('version', 'Unknown')}")
            print(f"✅ Printer: {data.get('printer', 'Not configured')}")
            
            if 'auto_recovery' in data:
                print(f"✅ Auto-Recovery: {'Enabled' if data['auto_recovery'] else 'Disabled'}")
            
            if 'recovery_stats' in data:
                stats = data['recovery_stats']
                print(f"📊 Recovery Stats:")
                print(f"   - Spooler restarts: {stats.get('spooler_restarts', 0)}")
                print(f"   - Offline detections: {stats.get('offline_detections', 0)}")
                print(f"   - Recovery in progress: {stats.get('recovery_in_progress', False)}")
            
            if 'printer_status' in data and data['printer_status']:
                ps = data['printer_status']
                print(f"🖨️  Printer Status:")
                print(f"   - Online: {ps.get('online', 'Unknown')}")
                print(f"   - Error: {ps.get('error', 'Unknown')}")
                print(f"   - Paper out: {ps.get('paper_out', 'Unknown')}")
                print(f"   - Paper jam: {ps.get('paper_jam', 'Unknown')}")
            
            return True
        else:
            print(f"❌ Server status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking server status: {e}")
        return False

def test_recovery_status():
    """Test detailed recovery status endpoint"""
    print("\n🔍 Testing recovery status...")
    try:
        headers = {'X-API-Key': API_KEY}
        response = requests.get(f"{SERVER_URL}/recovery/status", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Recovery status retrieved successfully")
            print(f"📊 Auto-recovery enabled: {data.get('auto_recovery_enabled', 'Unknown')}")
            print(f"🔧 Spooler running: {data.get('spooler_running', 'Unknown')}")
            
            if 'recovery_stats' in data:
                stats = data['recovery_stats']
                print("📈 Detailed Recovery Statistics:")
                for key, value in stats.items():
                    if 'timestamp' in key.lower() or 'time' in key.lower():
                        if value and value > 0:
                            time_str = datetime.fromtimestamp(value).strftime('%Y-%m-%d %H:%M:%S')
                            print(f"   - {key}: {time_str}")
                        else:
                            print(f"   - {key}: Never")
                    else:
                        print(f"   - {key}: {value}")
            
            return True
        else:
            print(f"❌ Recovery status check failed: {response.status_code}")
            if response.status_code == 401:
                print("   Check your API key")
            return False
    except Exception as e:
        print(f"❌ Error checking recovery status: {e}")
        return False

def test_print_with_recovery():
    """Test printing with auto-recovery"""
    print("\n🖨️  Testing print with auto-recovery...")
    try:
        headers = {
            'X-API-Key': API_KEY,
            'Content-Type': 'application/json'
        }
        
        test_text = f"""
==========================================
AUTO-RECOVERY TEST PRINT
==========================================
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Server: HK Savor Spoon Auto-Recovery v6.0

Recovery Features Test:
✅ Automatic printer offline detection
✅ Print spooler restart capability  
✅ Stuck job clearing
✅ Connection timeout handling
✅ Circuit breaker protection

Traditional Chinese Test:
繁體中文測試 - 香港美味湯品餐廳
自動恢復功能正常運作

==========================================
Test completed successfully!
==========================================

"""
        
        data = {'text': test_text}
        response = requests.post(f"{SERVER_URL}/print", headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Print request successful")
            print(f"📄 Message: {result.get('message', 'No message')}")
            
            if result.get('auto_recovery'):
                print("🚑 Auto-recovery feature confirmed active")
            
            if result.get('queued'):
                print(f"📋 Print job queued: {result.get('job_id', 'Unknown ID')}")
                print(f"🔄 Reason: {result.get('retry_reason', 'Circuit breaker or immediate failure')}")
            
            return True
        else:
            print(f"❌ Print request failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   Raw response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing print: {e}")
        return False

def test_manual_recovery():
    """Test manual recovery trigger"""
    print("\n🚑 Testing manual recovery trigger...")
    try:
        headers = {'X-API-Key': API_KEY}
        response = requests.post(f"{SERVER_URL}/recovery/trigger", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Manual recovery triggered successfully")
            print(f"📄 Result: {data.get('message', 'No message')}")
            print(f"🎯 Success: {data.get('success', 'Unknown')}")
            return True
        else:
            print(f"❌ Manual recovery failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error triggering manual recovery: {e}")
        return False

def test_queue_status():
    """Test print queue status"""
    print("\n📋 Testing queue status...")
    try:
        headers = {'X-API-Key': API_KEY}
        response = requests.get(f"{SERVER_URL}/queue", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Queue status retrieved successfully")
            print(f"📊 Queue size: {data.get('queue_size', 0)} jobs")
            
            if data.get('auto_recovery'):
                print("🚑 Auto-recovery confirmed in queue system")
            
            cb_state = data.get('circuit_breaker', {})
            print(f"🔌 Circuit breaker state: {cb_state.get('state', 'Unknown')}")
            print(f"🔌 Circuit breaker failures: {cb_state.get('failures', 0)}")
            
            return True
        else:
            print(f"❌ Queue status failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking queue status: {e}")
        return False

def main():
    """Run all auto-recovery tests"""
    print("=" * 60)
    print("HK SAVOR SPOON AUTO-RECOVERY PRINT SERVER TEST")
    print("=" * 60)
    print(f"🎯 Testing server at: {SERVER_URL}")
    print(f"🔑 Using API key: {API_KEY[:10]}...")
    print(f"⏰ Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    
    tests = [
        ("Server Status", test_server_status),
        ("Recovery Status", test_recovery_status),
        ("Print with Recovery", test_print_with_recovery),
        ("Manual Recovery", test_manual_recovery),
        ("Queue Status", test_queue_status),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {e}")
            results[test_name] = False
        
        # Small delay between tests
        time.sleep(0.5)
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if success:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! Auto-recovery server is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the server configuration and logs.")
    
    print(f"⏰ Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
