#!/usr/bin/env python3
"""
Direct Star TSP143III LAN Printer Integration
No PC required! Direct network printing to Star TSP143III
"""

import socket
import time
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration for Star TSP143III LAN
CONFIG = {
    'API_KEY': 'hksavorspoon-secure-print-key-2025',
    'PRINTER_IP': '192.168.1.100',  # Your Star TSP143III IP
    'PRINTER_PORT': 9100,           # Raw printing port
    'PRINT_TIMEOUT': 5,
    'MAX_RETRIES': 3
}

# Print queue for reliability
PRINT_QUEUE = []
QUEUE_LOCK = threading.Lock()

def build_star_tsp_commands(text):
    """Build ESC/POS commands optimized for Star TSP143III"""
    commands = bytearray()
    
    # Initialize printer
    commands.extend(b'\x1B\x40')  # ESC @ - Initialize
    
    # Set character code table (important for Star printers)
    commands.extend(b'\x1B\x1D\x74\x00')  # PC437 (standard)
    
    # Check for Chinese characters
    is_chinese = any('\u4e00' <= char <= '\u9fff' for char in text)
    
    if is_chinese:
        # For Chinese text, use UTF-8 and inform printer
        try:
            # Try Big5 first (better for traditional Chinese)
            text_bytes = text.encode('big5', errors='replace')
            commands.extend(b'\x1B\x1D\x74\x02')  # Set to Big5
            logger.debug("Using Big5 encoding for Chinese text")
        except:
            # Fallback to UTF-8
            text_bytes = text.encode('utf-8', errors='replace')
            commands.extend(b'\x1B\x1D\x74\x08')  # Set to UTF-8
            logger.debug("Using UTF-8 encoding for Chinese text")
    else:
        # English text
        text_bytes = text.encode('ascii', errors='replace')
    
    # Star TSP143III specific settings
    commands.extend(b'\x1B\x47\x01')  # Enable double-strike (bold)
    
    # Add the text
    commands.extend(text_bytes)
    
    # End formatting
    commands.extend(b'\x1B\x47\x00')  # Disable double-strike
    
    # Line feeds and cut
    commands.extend(b'\x0A\x0A\x0A')  # 3 line feeds
    commands.extend(b'\x1B\x64\x03')  # ESC d 3 - Cut paper (Star specific)
    
    return bytes(commands)

def print_to_star_tsp143(text, ip, port=9100):
    """Print directly to Star TSP143III LAN"""
    try:
        start_time = time.time()
        logger.info(f"🖨️  Printing to Star TSP143III at {ip}:{port}")
        
        # Build Star-specific commands
        commands = build_star_tsp_commands(text)
        
        # Connect to printer
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(CONFIG['PRINT_TIMEOUT'])
        
        # Connect
        sock.connect((ip, port))
        
        # Send data in chunks for reliability
        chunk_size = 1024
        total_sent = 0
        
        for i in range(0, len(commands), chunk_size):
            chunk = commands[i:i + chunk_size]
            sent = sock.send(chunk)
            total_sent += sent
            
            # Small delay between chunks for Star printers
            if i + chunk_size < len(commands):
                time.sleep(0.01)  # 10ms delay
        
        sock.close()
        
        print_time = time.time() - start_time
        logger.info(f"✅ Print successful: {total_sent} bytes in {print_time:.2f}s")
        
        return True, f"Printed {total_sent} bytes to Star TSP143III"
        
    except socket.timeout:
        error_msg = f"Printer timeout - check if Star TSP143III at {ip} is online"
        logger.error(f"❌ {error_msg}")
        return False, error_msg
        
    except ConnectionRefusedError:
        error_msg = f"Connection refused - Star TSP143III at {ip} not responding"
        logger.error(f"❌ {error_msg}")
        return False, error_msg
        
    except Exception as e:
        error_msg = f"Print error: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return False, error_msg

def test_printer_connection():
    """Test connection to Star TSP143III"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((CONFIG['PRINTER_IP'], CONFIG['PRINTER_PORT']))
        sock.close()
        return result == 0
    except:
        return False

def discover_star_printer():
    """Auto-discover Star TSP143III on network"""
    logger.info("🔍 Scanning for Star TSP143III LAN printer...")
    
    # Common IP ranges for Star printers
    base_ips = [
        "192.168.1",
        "192.168.0", 
        "10.0.0",
        "172.16.0"
    ]
    
    # Common IPs for Star printers
    common_ips = [100, 101, 110, 111, 200, 201, 210]
    
    for base in base_ips:
        for ip_end in common_ips:
            test_ip = f"{base}.{ip_end}"
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((test_ip, 9100))
                sock.close()
                
                if result == 0:
                    logger.info(f"✅ Found printer at {test_ip}:9100")
                    CONFIG['PRINTER_IP'] = test_ip
                    return test_ip
            except:
                continue
    
    logger.warning("❌ No Star TSP143III found on network scan")
    return None

@app.route('/status', methods=['GET'])
def status():
    """Check server and printer status"""
    printer_online = test_printer_connection()
    
    return jsonify({
        'status': 'online',
        'server': 'HK Savor Spoon Direct Star TSP143III Server',
        'version': '1.0-star-direct',
        'printer': {
            'model': 'Star TSP143III LAN',
            'ip': CONFIG['PRINTER_IP'],
            'port': CONFIG['PRINTER_PORT'],
            'online': printer_online,
            'status': 'Ready' if printer_online else 'Offline'
        },
        'queue_size': len(PRINT_QUEUE),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/print', methods=['POST'])
def print_receipt():
    """Print directly to Star TSP143III"""
    # Check API key
    api_key = request.headers.get('X-API-Key')
    if api_key != CONFIG['API_KEY']:
        logger.warning(f"🔑 Invalid API key from {request.remote_addr}")
        return jsonify({'error': 'Invalid API key'}), 401
    
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'Missing text parameter'}), 400
        
        text = data['text']
        client_ip = request.remote_addr
        
        logger.info(f"📝 Print request from {client_ip} ({len(text)} chars)")
        
        # Try to print
        success, message = print_to_star_tsp143(
            text, 
            CONFIG['PRINTER_IP'], 
            CONFIG['PRINTER_PORT']
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'printer': 'Star TSP143III LAN',
                'method': 'direct_network',
                'timestamp': datetime.now().isoformat()
            })
        else:
            # Queue for retry
            with QUEUE_LOCK:
                PRINT_QUEUE.append({
                    'id': str(uuid.uuid4()),
                    'text': text,
                    'timestamp': datetime.now().isoformat(),
                    'attempts': 0,
                    'client_ip': client_ip
                })
            
            return jsonify({
                'success': False,
                'message': f'Print failed: {message}',
                'queued': True,
                'retry': 'Job queued for automatic retry'
            }), 500
    
    except Exception as e:
        logger.error(f"Print endpoint error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/test-print', methods=['POST'])
def test_print():
    """Send a test print to verify printer functionality"""
    api_key = request.headers.get('X-API-Key')
    if api_key != CONFIG['API_KEY']:
        return jsonify({'error': 'Invalid API key'}), 401
    
    test_content = f"""
================================
    HK SAVOR SPOON RESTAURANT
    Star TSP143III Test Print
================================
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Printer: Star TSP143III LAN
IP: {CONFIG['PRINTER_IP']}

Test Items:
- English text printing     ✓
- 中文打印测试               ✓
- Network connectivity      ✓

Connection: Direct Network
Method: ESC/POS Raw TCP

Status: All systems working! 🎉
================================
"""
    
    success, message = print_to_star_tsp143(
        test_content,
        CONFIG['PRINTER_IP'],
        CONFIG['PRINTER_PORT']
    )
    
    return jsonify({
        'success': success,
        'message': message,
        'test_type': 'Star TSP143III functionality test'
    })

@app.route('/queue', methods=['GET'])
def queue_status():
    """Get print queue status"""
    api_key = request.headers.get('X-API-Key')
    if api_key != CONFIG['API_KEY']:
        return jsonify({'error': 'Invalid API key'}), 401
    
    with QUEUE_LOCK:
        return jsonify({
            'queue_size': len(PRINT_QUEUE),
            'jobs': PRINT_QUEUE.copy()
        })

@app.route('/queue/clear', methods=['POST'])
def clear_queue():
    """Clear print queue"""
    api_key = request.headers.get('X-API-Key')
    if api_key != CONFIG['API_KEY']:
        return jsonify({'error': 'Invalid API key'}), 401
    
    with QUEUE_LOCK:
        cleared_count = len(PRINT_QUEUE)
        PRINT_QUEUE.clear()
    
    logger.info(f"🗑️  Cleared {cleared_count} jobs from queue")
    return jsonify({
        'success': True,
        'message': f'Cleared {cleared_count} queued jobs'
    })

@app.route('/config', methods=['GET', 'POST'])
def printer_config():
    """Get or update printer configuration"""
    api_key = request.headers.get('X-API-Key')
    if api_key != CONFIG['API_KEY']:
        return jsonify({'error': 'Invalid API key'}), 401
    
    if request.method == 'GET':
        return jsonify({
            'printer_ip': CONFIG['PRINTER_IP'],
            'printer_port': CONFIG['PRINTER_PORT'],
            'print_timeout': CONFIG['PRINT_TIMEOUT'],
            'max_retries': CONFIG['MAX_RETRIES']
        })
    
    elif request.method == 'POST':
        data = request.get_json()
        if 'printer_ip' in data:
            CONFIG['PRINTER_IP'] = data['printer_ip']
        if 'printer_port' in data:
            CONFIG['PRINTER_PORT'] = int(data['printer_port'])
        if 'print_timeout' in data:
            CONFIG['PRINT_TIMEOUT'] = int(data['print_timeout'])
        
        logger.info(f"🔧 Updated config: IP={CONFIG['PRINTER_IP']}, Port={CONFIG['PRINTER_PORT']}")
        
        return jsonify({
            'success': True,
            'message': 'Configuration updated',
            'config': {
                'printer_ip': CONFIG['PRINTER_IP'],
                'printer_port': CONFIG['PRINTER_PORT'],
                'print_timeout': CONFIG['PRINT_TIMEOUT']
            }
        })

def retry_queue_worker():
    """Background worker to retry failed prints"""
    while True:
        try:
            with QUEUE_LOCK:
                if PRINT_QUEUE:
                    job = PRINT_QUEUE.pop(0)
                else:
                    job = None
            
            if job:
                logger.info(f"🔄 Retrying print job {job['id']}")
                
                success, message = print_to_star_tsp143(
                    job['text'],
                    CONFIG['PRINTER_IP'],
                    CONFIG['PRINTER_PORT']
                )
                
                if success:
                    logger.info(f"✅ Retry successful for job {job['id']}")
                else:
                    job['attempts'] += 1
                    if job['attempts'] < CONFIG['MAX_RETRIES']:
                        with QUEUE_LOCK:
                            PRINT_QUEUE.append(job)
                        logger.warning(f"❌ Retry {job['attempts']}/{CONFIG['MAX_RETRIES']} failed for job {job['id']}")
                    else:
                        logger.error(f"❌ Job {job['id']} failed after {CONFIG['MAX_RETRIES']} attempts")
            
            time.sleep(10)  # Check every 10 seconds
            
        except Exception as e:
            logger.error(f"Queue worker error: {e}")
            time.sleep(30)

def init_system():
    """Initialize the direct printing system"""
    logger.info("🚀 Initializing Direct Star TSP143III System...")
    
    # Try to discover printer if not configured
    if not test_printer_connection():
        logger.info("🔍 Configured printer not responding, scanning network...")
        discovered_ip = discover_star_printer()
        if not discovered_ip:
            logger.warning("⚠️  No Star TSP143III found! Please check network connection.")
    
    # Test final configuration
    if test_printer_connection():
        logger.info(f"✅ Star TSP143III ready at {CONFIG['PRINTER_IP']}:{CONFIG['PRINTER_PORT']}")
    else:
        logger.error(f"❌ Cannot connect to Star TSP143III at {CONFIG['PRINTER_IP']}")
    
    # Start retry worker
    retry_thread = threading.Thread(target=retry_queue_worker, daemon=True)
    retry_thread.start()

if __name__ == '__main__':
    print("=" * 70)
    print("🌟 HK SAVOR SPOON DIRECT STAR TSP143III LAN SERVER")
    print("=" * 70)
    print("✅ NO PC REQUIRED - Direct network printing!")
    print("🖨️  Target: Star TSP143III LAN thermal printer")
    print("📡 Method: Direct ESC/POS over TCP/IP")
    print("🔄 Features: Auto-retry, queue management")
    print("🌐 API: RESTful endpoints for POS integration")
    print("")
    
    init_system()
    
    print(f"🖨️  Printer: Star TSP143III at {CONFIG['PRINTER_IP']}:{CONFIG['PRINTER_PORT']}")
    print(f"🔑 API Key: {CONFIG['API_KEY'][:10]}...")
    print("")
    print("📡 ENDPOINTS:")
    print("  GET  /status       - Printer status")
    print("  POST /print        - Print receipt")
    print("  POST /test-print   - Send test print")
    print("  GET  /queue        - Queue status")
    print("  POST /queue/clear  - Clear queue")
    print("  GET  /config       - Get configuration")
    print("  POST /config       - Update configuration")
    print("")
    print("🚀 Server starting on port 8080...")
    print("🌟 Star TSP143III direct printing active!")
    print("=" * 70)
    
    try:
        app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        logger.info("Server shutdown completed")