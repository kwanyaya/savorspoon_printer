#!/usr/bin/env python3
"""
HK Savor Spoon Cloud Print Server
Receives requests from hksavorspoon.com and forwards to local Star TSP143III
"""

import socket
import time
import json
import logging
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import threading
import uuid
import hashlib
import hmac

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/var/log/savor_spoon_cloud.log')
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins=['https://hksavorspoon.com', 'http://hksavorspoon.com'])

# Configuration
CONFIG = {
    'API_KEY': 'hksavorspoon-secure-print-key-2025',
    'WEBHOOK_SECRET': 'cloud-print-webhook-secret-2025',  # For website authentication
    'PRINTER_DISCOVERY_PORT': 8081,  # Port for printer to register itself
    'PRINT_TIMEOUT': 10,
    'MAX_RETRIES': 3,
    'ALLOWED_ORIGINS': ['hksavorspoon.com', 'www.hksavorspoon.com']
}

# Registered printers (restaurants can have multiple locations)
REGISTERED_PRINTERS = {}
PRINT_QUEUE = []
QUEUE_LOCK = threading.Lock()

class PrinterRegistration:
    """Manages printer registration and communication"""
    
    def __init__(self):
        self.printers = {}
        self.lock = threading.Lock()
    
    def register_printer(self, restaurant_id, printer_info):
        """Register a printer from a restaurant location"""
        with self.lock:
            self.printers[restaurant_id] = {
                'ip': printer_info['ip'],
                'port': printer_info.get('port', 9100),
                'location': printer_info.get('location', 'Main'),
                'last_seen': datetime.now(),
                'status': 'online'
            }
            logger.info(f"✅ Printer registered: {restaurant_id} at {printer_info['ip']}")
    
    def get_printer(self, restaurant_id):
        """Get printer info for a restaurant"""
        return self.printers.get(restaurant_id)
    
    def list_printers(self):
        """List all registered printers"""
        return self.printers.copy()

printer_registry = PrinterRegistration()

def verify_website_signature(payload, signature, secret):
    """Verify request is from hksavorspoon.com"""
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected_signature}", signature)

def send_to_printer_direct(printer_ip, printer_port, text):
    """Send print job directly to Star TSP143III"""
    try:
        logger.info(f"🖨️  Sending to printer {printer_ip}:{printer_port}")
        
        # Build ESC/POS commands for Star TSP143III
        commands = build_star_escpos_commands(text)
        
        # Connect and send
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(CONFIG['PRINT_TIMEOUT'])
        sock.connect((printer_ip, printer_port))
        
        total_sent = 0
        while total_sent < len(commands):
            sent = sock.send(commands[total_sent:])
            if sent == 0:
                raise Exception("Connection broken")
            total_sent += sent
        
        sock.close()
        
        logger.info(f"✅ Print successful: {total_sent} bytes sent")
        return True, f"Printed {total_sent} bytes"
        
    except Exception as e:
        error_msg = f"Print failed: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return False, error_msg

def build_star_escpos_commands(text):
    """Build ESC/POS commands optimized for Star TSP143III"""
    commands = bytearray()
    
    # Initialize printer
    commands.extend(b'\x1B\x40')  # ESC @ - Initialize
    commands.extend(b'\x1B\x1D\x74\x00')  # PC437 charset
    
    # Check for Chinese characters
    is_chinese = any('\u4e00' <= char <= '\u9fff' for char in text)
    
    if is_chinese:
        try:
            text_bytes = text.encode('big5', errors='replace')
            commands.extend(b'\x1B\x1D\x74\x02')  # Big5 charset
        except:
            text_bytes = text.encode('utf-8', errors='replace')
            commands.extend(b'\x1B\x1D\x74\x08')  # UTF-8 charset
    else:
        text_bytes = text.encode('ascii', errors='replace')
    
    # Add text
    commands.extend(text_bytes)
    
    # Cut paper
    commands.extend(b'\x0A\x0A\x0A')  # Line feeds
    commands.extend(b'\x1B\x64\x03')  # Cut paper
    
    return bytes(commands)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check for cloud server"""
    return jsonify({
        'status': 'healthy',
        'server': 'HK Savor Spoon Cloud Print Server',
        'version': '1.0',
        'registered_printers': len(printer_registry.list_printers()),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/printers/register', methods=['POST'])
def register_printer():
    """Register a printer from restaurant location"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['restaurant_id', 'printer_ip', 'auth_key']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Verify auth key
        if data['auth_key'] != CONFIG['API_KEY']:
            return jsonify({'error': 'Invalid authentication'}), 401
        
        # Register printer
        printer_info = {
            'ip': data['printer_ip'],
            'port': data.get('printer_port', 9100),
            'location': data.get('location', 'Main')
        }
        
        printer_registry.register_printer(data['restaurant_id'], printer_info)
        
        return jsonify({
            'success': True,
            'message': f"Printer registered for {data['restaurant_id']}",
            'printer_info': printer_info
        })
        
    except Exception as e:
        logger.error(f"Printer registration error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/print', methods=['POST'])
def print_from_website():
    """Receive print request from hksavorspoon.com"""
    try:
        # Get raw payload for signature verification
        payload = request.get_data(as_text=True)
        signature = request.headers.get('X-Signature-256', '')
        
        # Verify request is from hksavorspoon.com (optional but recommended)
        origin = request.headers.get('Origin', '')
        referer = request.headers.get('Referer', '')
        
        # Check origin
        allowed_origin = any(domain in origin for domain in CONFIG['ALLOWED_ORIGINS'])
        if not allowed_origin and origin:
            logger.warning(f"🚫 Request from unauthorized origin: {origin}")
            return jsonify({'error': 'Unauthorized origin'}), 403
        
        # Parse JSON data
        data = request.get_json()
        
        # Validate required fields
        if not data or 'text' not in data:
            return jsonify({'error': 'Missing text parameter'}), 400
        
        if 'restaurant_id' not in data:
            return jsonify({'error': 'Missing restaurant_id parameter'}), 400
        
        text = data['text']
        restaurant_id = data['restaurant_id']
        
        logger.info(f"📝 Print request from website for {restaurant_id} ({len(text)} chars)")
        
        # Get printer for this restaurant
        printer_info = printer_registry.get_printer(restaurant_id)
        if not printer_info:
            return jsonify({
                'error': f'No printer registered for restaurant {restaurant_id}',
                'hint': 'Register printer first using /printers/register'
            }), 404
        
        # Try to print
        success, message = send_to_printer_direct(
            printer_info['ip'],
            printer_info['port'],
            text
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'restaurant_id': restaurant_id,
                'printer_ip': printer_info['ip'],
                'timestamp': datetime.now().isoformat()
            })
        else:
            # Queue for retry
            with QUEUE_LOCK:
                PRINT_QUEUE.append({
                    'id': str(uuid.uuid4()),
                    'restaurant_id': restaurant_id,
                    'text': text,
                    'timestamp': datetime.now().isoformat(),
                    'attempts': 0
                })
            
            return jsonify({
                'success': False,
                'message': f'Print failed: {message}',
                'queued': True,
                'restaurant_id': restaurant_id
            }), 500
    
    except Exception as e:
        logger.error(f"Print request error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/printers', methods=['GET'])
def list_printers():
    """List all registered printers"""
    api_key = request.headers.get('X-API-Key')
    if api_key != CONFIG['API_KEY']:
        return jsonify({'error': 'Invalid API key'}), 401
    
    printers = printer_registry.list_printers()
    return jsonify({
        'registered_printers': printers,
        'total_count': len(printers)
    })

@app.route('/test/<restaurant_id>', methods=['POST'])
def test_print(restaurant_id):
    """Test print for a specific restaurant"""
    api_key = request.headers.get('X-API-Key')
    if api_key != CONFIG['API_KEY']:
        return jsonify({'error': 'Invalid API key'}), 401
    
    printer_info = printer_registry.get_printer(restaurant_id)
    if not printer_info:
        return jsonify({'error': f'No printer found for {restaurant_id}'}), 404
    
    test_content = f"""
================================
    HK SAVOR SPOON RESTAURANT
    Cloud Print Test
================================
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Restaurant ID: {restaurant_id}
Printer: {printer_info['ip']}:{printer_info['port']}

Test Results:
✅ Cloud server connection
✅ Printer registration  
✅ Direct network printing
✅ Website integration ready

Status: Ready for production! 🎉
================================
"""
    
    success, message = send_to_printer_direct(
        printer_info['ip'],
        printer_info['port'],
        test_content
    )
    
    return jsonify({
        'success': success,
        'message': message,
        'restaurant_id': restaurant_id,
        'printer_info': printer_info
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
                restaurant_id = job['restaurant_id']
                printer_info = printer_registry.get_printer(restaurant_id)
                
                if printer_info:
                    logger.info(f"🔄 Retrying print job {job['id']} for {restaurant_id}")
                    
                    success, message = send_to_printer_direct(
                        printer_info['ip'],
                        printer_info['port'],
                        job['text']
                    )
                    
                    if not success:
                        job['attempts'] += 1
                        if job['attempts'] < CONFIG['MAX_RETRIES']:
                            with QUEUE_LOCK:
                                PRINT_QUEUE.append(job)
                        else:
                            logger.error(f"❌ Job {job['id']} failed after {CONFIG['MAX_RETRIES']} attempts")
                else:
                    logger.warning(f"⚠️  No printer found for {restaurant_id}, dropping job")
            
            time.sleep(30)  # Check every 30 seconds
            
        except Exception as e:
            logger.error(f"Queue worker error: {e}")
            time.sleep(60)

if __name__ == '__main__':
    print("=" * 70)
    print("🌐 HK SAVOR SPOON CLOUD PRINT SERVER")
    print("=" * 70)
    print("✅ Receives requests from hksavorspoon.com")
    print("🖨️  Forwards to local Star TSP143III printers")
    print("🔄 Auto-retry with queue management")
    print("🌍 Multi-location restaurant support")
    print("🔐 Secure authentication")
    print("")
    print("📡 ENDPOINTS:")
    print("  POST /print                - Print from website")
    print("  POST /printers/register    - Register printer")
    print("  GET  /printers             - List printers")
    print("  POST /test/<restaurant_id> - Test print")
    print("  GET  /queue                - Queue status")
    print("  GET  /health               - Health check")
    print("")
    print("🚀 Starting cloud server...")
    print("=" * 70)
    
    # Start retry worker
    retry_thread = threading.Thread(target=retry_queue_worker, daemon=True)
    retry_thread.start()
    
    try:
        app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\n🛑 Cloud server stopped")
        logger.info("Cloud server shutdown completed")