# -*- coding: utf-8 -*-
"""
SECURE PRINT SERVER v5.0 - Enhanced Security + Rate Limiting
============================================================
Addresses security issues and malicious traffic
"""

import win32print
import win32api
import win32gui
import json
import threading
import time
import signal
import sys
import uuid
import pathlib
import _json as json_module
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from datetime import datetime, timedelta
import os
from contextlib import contextmanager
from collections import defaultdict
import ipaddress

# Configure logging with more detail and Unicode support
import io
logging.basicConfig(
    level=logging.INFO,  # Changed to INFO to reduce noise
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')),
        logging.FileHandler('print_server_secure.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global configuration
CONFIG = {
    'API_KEY': 'hksavorspoon-secure-print-key-2025',
    'DEFAULT_PRINTER': None,
    'PRINT_TIMEOUT': 3,
    'LOCAL_IP': None,
    'DDNS_CONFIG': None
}

# Security configuration
SECURITY_CONFIG = {
    'RATE_LIMIT_REQUESTS': 10,  # Max requests per minute
    'RATE_LIMIT_WINDOW': 60,    # Time window in seconds
    'MAX_REQUEST_SIZE': 1024 * 1024,  # 1MB max request
    'BLOCK_DURATION': 300,      # Block suspicious IPs for 5 minutes
    'SUSPICIOUS_THRESHOLD': 5,   # Requests to trigger block
}

# IP tracking for rate limiting and security
ip_requests = defaultdict(list)
blocked_ips = {}
suspicious_patterns = [
    'ssh-', 'connect ', 'git', '.env', 'login', 'admin', 'boaform',
    'manager/', 'cgi-bin', 'favicon.ico', 'robots.txt', '.well-known'
]

# Allowed IP ranges (Hong Kong restaurant network)
ALLOWED_IP_RANGES = [
    '192.168.0.0/16',    # Local network
    '10.0.0.0/8',        # Private network
    '172.16.0.0/12',     # Private network
    '127.0.0.0/8',       # Localhost
    '151.106.117.246',   # Your website IP (from logs)
]

def is_ip_allowed(ip_str):
    """Check if IP is in allowed ranges"""
    try:
        ip = ipaddress.ip_address(ip_str)
        for allowed_range in ALLOWED_IP_RANGES:
            if '/' in allowed_range:
                if ip in ipaddress.ip_network(allowed_range, strict=False):
                    return True
            else:
                if str(ip) == allowed_range:
                    return True
        return False
    except:
        return False

def is_suspicious_request(request):
    """Detect suspicious requests"""
    path = request.path.lower()
    user_agent = request.headers.get('User-Agent', '').lower()
    
    # Check for suspicious patterns
    for pattern in suspicious_patterns:
        if pattern in path or pattern in user_agent:
            return True
    
    # Check for non-standard HTTP methods
    if request.method not in ['GET', 'POST', 'OPTIONS']:
        return True
        
    # Check for unusual paths
    if len(request.path) > 100:  # Extremely long paths
        return True
        
    return False

def cleanup_old_records():
    """Clean up old IP tracking records"""
    current_time = time.time()
    cutoff_time = current_time - SECURITY_CONFIG['RATE_LIMIT_WINDOW']
    
    # Clean up rate limiting records
    for ip in list(ip_requests.keys()):
        ip_requests[ip] = [req_time for req_time in ip_requests[ip] if req_time > cutoff_time]
        if not ip_requests[ip]:
            del ip_requests[ip]
    
    # Clean up blocked IPs
    for ip in list(blocked_ips.keys()):
        if blocked_ips[ip] < current_time:
            del blocked_ips[ip]
            logger.info(f"🔓 Unblocked IP: {ip}")

@app.before_request
def security_check():
    """Security middleware - runs before every request"""
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    if client_ip and ',' in client_ip:
        client_ip = client_ip.split(',')[0].strip()
    
    current_time = time.time()
    
    # Clean up old records periodically
    if current_time % 30 < 1:  # Every ~30 seconds
        cleanup_old_records()
    
    # Check if IP is blocked
    if client_ip in blocked_ips:
        if blocked_ips[client_ip] > current_time:
            logger.warning(f"🚫 Blocked IP attempted access: {client_ip}")
            return jsonify({'error': 'Access denied'}), 403
        else:
            # Block expired, remove it
            del blocked_ips[client_ip]
    
    # For non-allowed IPs, apply strict security
    if not is_ip_allowed(client_ip):
        # Check for suspicious requests
        if is_suspicious_request(request):
            logger.warning(f"🔍 Suspicious request from {client_ip}: {request.method} {request.path}")
            
            # Count suspicious requests
            if 'suspicious_count' not in ip_requests[client_ip + '_sus']:
                ip_requests[client_ip + '_sus'] = []
            
            ip_requests[client_ip + '_sus'].append(current_time)
            
            # Block if too many suspicious requests
            recent_suspicious = len([t for t in ip_requests[client_ip + '_sus'] 
                                   if t > current_time - SECURITY_CONFIG['RATE_LIMIT_WINDOW']])
            
            if recent_suspicious >= SECURITY_CONFIG['SUSPICIOUS_THRESHOLD']:
                blocked_ips[client_ip] = current_time + SECURITY_CONFIG['BLOCK_DURATION']
                logger.error(f"🚨 BLOCKED suspicious IP: {client_ip} for {SECURITY_CONFIG['BLOCK_DURATION']}s")
                return jsonify({'error': 'Too many suspicious requests'}), 429
            
            # Return 404 for suspicious requests to avoid revealing endpoints
            return jsonify({'error': 'Not found'}), 404
        
        # Rate limiting for non-allowed IPs
        ip_requests[client_ip].append(current_time)
        recent_requests = [t for t in ip_requests[client_ip] 
                          if t > current_time - SECURITY_CONFIG['RATE_LIMIT_WINDOW']]
        
        if len(recent_requests) > SECURITY_CONFIG['RATE_LIMIT_REQUESTS']:
            logger.warning(f"⚡ Rate limit exceeded for {client_ip}")
            return jsonify({'error': 'Rate limit exceeded'}), 429
    
    # Check request size
    if request.content_length and request.content_length > SECURITY_CONFIG['MAX_REQUEST_SIZE']:
        logger.warning(f"📦 Large request from {client_ip}: {request.content_length} bytes")
        return jsonify({'error': 'Request too large'}), 413

# Circuit breaker state
CIRCUIT_BREAKER = {
    'failures': 0,
    'last_failure': None,
    'state': 'CLOSED',
    'failure_threshold': 3,
    'recovery_timeout': 60,
    'success_count': 0,
    'min_successes': 2
}

# Persistent print retry queue
QUEUE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'print_queue.jsonl')
QUEUE_LOCK = threading.Lock()

def enqueue_print_job(job):
    """Append a job to the persistent queue as a JSON line."""
    pathlib.Path(QUEUE_FILE).parent.mkdir(parents=True, exist_ok=True)
    with QUEUE_LOCK:
        with open(QUEUE_FILE, 'a', encoding='utf-8') as f:
            f.write(json_module.dumps(job, ensure_ascii=False) + '\n')
            logger.info(f"Enqueued job {job.get('id')} for retry")

def read_queue():
    """Read all jobs from queue file and return as list of dicts."""
    if not os.path.exists(QUEUE_FILE):
        return []
    with QUEUE_LOCK:
        with open(QUEUE_FILE, 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
    jobs = []
    for line in lines:
        try:
            jobs.append(json_module.loads(line))
        except Exception as e:
            logger.error(f"Failed to parse queue line: {e}")
    return jobs

def overwrite_queue(jobs):
    """Overwrite the queue file with new list of jobs."""
    pathlib.Path(QUEUE_FILE).parent.mkdir(parents=True, exist_ok=True)
    with QUEUE_LOCK:
        with open(QUEUE_FILE, 'w', encoding='utf-8') as f:
            for job in jobs:
                f.write(json_module.dumps(job, ensure_ascii=False) + '\n')

class AggressiveTimeoutPrinter:
    """Enhanced printer with aggressive timeout and circuit breaker integration"""

    def __init__(self, printer_name, timeout_seconds=3):
        self.printer_name = printer_name
        self.timeout = timeout_seconds
        self.print_result = None
        self.print_error = None
        self.worker_thread = None
        self.force_stop = False

    def _is_chinese_text(self, text):
        """Check if text contains Chinese characters"""
        return any('\u4e00' <= c <= '\u9fff' for c in text)

    def _print_worker_aggressive(self, text):
        """Aggressive print worker with multiple timeout strategies"""
        printer_handle = None
        job_id = None

        try:
            logger.debug(f"Opening printer: {self.printer_name}")
            printer_handle = win32print.OpenPrinter(self.printer_name)

            # Quick status check
            printer_info = win32print.GetPrinter(printer_handle, 2)
            status = printer_info.get('Status', 0)
            logger.debug(f"Printer status: {status}")

            if status not in [0, 0x00000400]:  # Ready or Printing
                raise Exception(f"Printer not ready, status: {status}")

            # Determine encoding
            is_chinese = self._is_chinese_text(text)
            if is_chinese:
                try:
                    text_bytes = text.encode('big5', errors='replace')
                    encoding = "Big5"
                except:
                    text_bytes = text.encode('utf-8', errors='replace')
                    encoding = "UTF-8"
            else:
                text_bytes = text.encode('utf-8', errors='replace')
                encoding = "UTF-8"

            logger.debug(f"Using encoding: {encoding}, {len(text_bytes)} bytes")

            # Start document with timeout
            doc_info = ("HK Savor Spoon Print", None, "RAW")
            job_id = win32print.StartDocPrinter(printer_handle, 1, doc_info)
            logger.debug(f"Document started, job ID: {job_id}")

            # Start page
            win32print.StartPagePrinter(printer_handle)

            # Build minimal command set
            commands = bytearray()
            commands.extend(b'\x1B\x40')  # Reset

            if is_chinese and encoding == "Big5":
                commands.extend(b'\x1B\x74\x0E')  # Big5 charset

            commands.extend(text_bytes)
            commands.extend(b'\x0A\x0A')      # Line feeds
            commands.extend(b'\x1B\x64\x02')  # Cut

            # Write in very small chunks with micro-delays
            total_written = 0
            chunk_size = 128  # Smaller chunks

            for i in range(0, len(commands), chunk_size):
                if self.force_stop:
                    raise Exception("Print operation cancelled by timeout")

                chunk = commands[i:i + chunk_size]
                written = win32print.WritePrinter(printer_handle, bytes(chunk))
                total_written += written

                # Micro delay between chunks
                time.sleep(0.001)  # 1ms

            logger.debug(f"Written {total_written} bytes")

            # Complete job
            win32print.EndPagePrinter(printer_handle)
            win32print.EndDocPrinter(printer_handle)
            win32print.ClosePrinter(printer_handle)

            self.print_result = {
                'success': True,
                'bytes_written': total_written,
                'encoding': encoding,
                'message': f'Print completed successfully ({total_written} bytes)'
            }

        except Exception as e:
            error_msg = f"Print error: {str(e)}"
            logger.error(error_msg)
            self.print_error = error_msg

            # Emergency cleanup
            try:
                if job_id and printer_handle:
                    win32print.EndPagePrinter(printer_handle)
                    win32print.EndDocPrinter(printer_handle)
            except:
                pass
            try:
                if printer_handle:
                    win32print.ClosePrinter(printer_handle)
            except:
                pass

    def print_with_aggressive_timeout(self, text):
        """Print with aggressive timeout and force termination"""
        self.print_result = None
        self.print_error = None
        self.force_stop = False

        # Create worker thread
        self.worker_thread = threading.Thread(
            target=self._print_worker_aggressive,
            args=(text,),
            daemon=True
        )

        logger.info(f"Starting aggressive print (timeout: {self.timeout}s)")
        start_time = time.time()
        self.worker_thread.start()

        # Wait with timeout
        self.worker_thread.join(timeout=self.timeout)
        elapsed = time.time() - start_time

        if self.worker_thread.is_alive():
            # Thread still running - force stop
            logger.warning(f"Print operation hung after {elapsed:.1f}s - forcing stop")
            self.force_stop = True

            # Give it one more second to cleanup
            self.worker_thread.join(timeout=1.0)

            if self.worker_thread.is_alive():
                logger.error("💀 Print thread did not respond to stop signal")

            return False, f"Print operation hung after {elapsed:.1f}s - TIMEOUT!"

        # Check results
        if self.print_error:
            return False, self.print_error

        if self.print_result and self.print_result['success']:
            logger.info(f"Print completed in {elapsed:.1f}s")
            return True, self.print_result['message']

        return False, "Print operation failed with no result"

def is_circuit_breaker_open():
    """Check if circuit breaker is open."""
    if CIRCUIT_BREAKER['state'] == 'OPEN':
        # Check if enough time has passed to try again
        if CIRCUIT_BREAKER['last_failure'] and \
           time.time() - CIRCUIT_BREAKER['last_failure'] > CIRCUIT_BREAKER['recovery_timeout']:
            CIRCUIT_BREAKER['state'] = 'HALF_OPEN'
            CIRCUIT_BREAKER['success_count'] = 0
            logger.info("🔄 Circuit breaker moving to HALF_OPEN state")
            return False
        return True
    return False

def record_print_success():
    """Record successful print for circuit breaker."""
    if CIRCUIT_BREAKER['state'] == 'HALF_OPEN':
        CIRCUIT_BREAKER['success_count'] += 1
        if CIRCUIT_BREAKER['success_count'] >= CIRCUIT_BREAKER['min_successes']:
            CIRCUIT_BREAKER['state'] = 'CLOSED'
            CIRCUIT_BREAKER['failures'] = 0
            logger.info("✅ Circuit breaker CLOSED - service restored")
    elif CIRCUIT_BREAKER['state'] == 'CLOSED':
        CIRCUIT_BREAKER['failures'] = max(0, CIRCUIT_BREAKER['failures'] - 1)

def record_print_failure():
    """Record failed print for circuit breaker."""
    CIRCUIT_BREAKER['failures'] += 1
    CIRCUIT_BREAKER['last_failure'] = time.time()
    CIRCUIT_BREAKER['success_count'] = 0

    if CIRCUIT_BREAKER['failures'] >= CIRCUIT_BREAKER['failure_threshold']:
        CIRCUIT_BREAKER['state'] = 'OPEN'
        logger.warning(f"🚫 Circuit breaker OPEN after {CIRCUIT_BREAKER['failures']} failures")

def queue_worker_loop(poll_interval=10):
    """Background worker that retries queued print jobs."""
    logger.info('Print queue worker started (enhanced)')
    while True:
        try:
            jobs = read_queue()
            if not jobs:
                time.sleep(poll_interval)
                continue

            remaining = []
            for job in jobs:
                job_id = job.get('id')
                attempts = job.get('attempts', 0)
                logger.info(f"🔁 Retrying queued job {job_id} (attempt {attempts + 1})")

                success, msg = process_print_job(job)
                if success:
                    logger.info(f"Queued job {job_id} printed: {msg}")
                else:
                    logger.warning(f"Queued job {job_id} failed: {msg}")
                    job['attempts'] = attempts + 1
                    # Give up after 5 attempts
                    if job['attempts'] < 5:
                        remaining.append(job)
                    else:
                        logger.error(f"🚫 Job {job_id} reached max attempts, dropping")

            overwrite_queue(remaining)
            time.sleep(poll_interval)
        except Exception as e:
            logger.error(f"Queue worker error: {e}")
            time.sleep(poll_interval)

def process_print_job(job):
    """Process a single print job."""
    try:
        text = job.get('text', '')
        printer_name = CONFIG['DEFAULT_PRINTER']

        if not printer_name:
            return False, "No printer configured"

        if is_circuit_breaker_open():
            return False, "Circuit breaker open"

        printer = AggressiveTimeoutPrinter(printer_name, CONFIG['PRINT_TIMEOUT'])
        success, message = printer.print_with_aggressive_timeout(text)

        if success:
            record_print_success()
        else:
            record_print_failure()

        return success, message

    except Exception as e:
        record_print_failure()
        return False, str(e)

# API Routes with enhanced security

@app.route('/status', methods=['GET'])
def status():
    """Server status endpoint - public access with limited info"""
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    
    # Limited info for non-allowed IPs
    if not is_ip_allowed(client_ip):
        return jsonify({
            'status': 'online',
            'server': 'HK Savor Spoon Print Server',
            'version': '5.0-secure'
        })
    
    # Full info for allowed IPs
    return jsonify({
        'status': 'online',
        'server': 'HK Savor Spoon Print Server',
        'version': '5.0-secure',
        'printer': CONFIG['DEFAULT_PRINTER'],
        'circuit_breaker': {
            'state': CIRCUIT_BREAKER['state'],
            'failures': CIRCUIT_BREAKER['failures']
        },
        'queue_size': len(read_queue()),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/print', methods=['POST'])
def print_text():
    """Print with circuit breaker and aggressive retry - SECURE"""
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    
    # Check API key
    api_key = request.headers.get('X-API-Key')
    if api_key != CONFIG['API_KEY']:
        logger.warning(f"🔑 Invalid API key from {client_ip}")
        return jsonify({'error': 'Invalid API key'}), 401

    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'Missing text parameter'}), 400

        text = data['text']
        printer_name = CONFIG['DEFAULT_PRINTER']

        if not printer_name:
            return jsonify({'error': 'No default printer configured'}), 500

        logger.info(f"📝 Print request from {client_ip} ({len(text)} chars)")

        # Check circuit breaker
        if is_circuit_breaker_open():
            logger.warning("🚫 Circuit breaker OPEN - queuing request")
            job = {
                'id': str(uuid.uuid4()),
                'text': text,
                'attempts': 0,
                'timestamp': datetime.now().isoformat(),
                'source': client_ip
            }
            enqueue_print_job(job)
            return jsonify({
                'success': True,
                'message': 'Print job queued (circuit breaker active)',
                'queued': True,
                'job_id': job['id']
            })

        # Try immediate print
        printer = AggressiveTimeoutPrinter(printer_name, CONFIG['PRINT_TIMEOUT'])
        success, message = printer.print_with_aggressive_timeout(text)

        if success:
            record_print_success()
            logger.info(f"✅ Print successful for {client_ip}: {message}")
            return jsonify({
                'success': True,
                'message': message,
                'timestamp': datetime.now().isoformat()
            })
        else:
            record_print_failure()
            logger.warning(f"❌ Print failed for {client_ip}: {message}")

            # Queue for retry
            job = {
                'id': str(uuid.uuid4()),
                'text': text,
                'attempts': 0,
                'timestamp': datetime.now().isoformat(),
                'source': client_ip
            }
            enqueue_print_job(job)

            return jsonify({
                'success': True,
                'message': 'Print job queued for retry',
                'queued': True,
                'job_id': job['id'],
                'retry_reason': message
            })

    except Exception as e:
        logger.error(f"Print endpoint error from {client_ip}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/queue', methods=['GET'])
def get_queue_status():
    """Get print queue status - requires API key"""
    api_key = request.headers.get('X-API-Key')
    if api_key != CONFIG['API_KEY']:
        return jsonify({'error': 'Invalid API key'}), 401

    jobs = read_queue()
    return jsonify({
        'queue_size': len(jobs),
        'jobs': jobs,
        'circuit_breaker': {
            'state': CIRCUIT_BREAKER['state'],
            'failures': CIRCUIT_BREAKER['failures'],
            'last_failure': CIRCUIT_BREAKER['last_failure']
        }
    })

@app.route('/emergency-clear', methods=['POST'])
def emergency_clear():
    """Emergency endpoint to clear print queue and reset circuit breaker"""
    api_key = request.headers.get('X-API-Key')
    if api_key != CONFIG['API_KEY']:
        return jsonify({'error': 'Invalid API key'}), 401

    try:
        logger.info("🚨 Emergency clear requested")

        # Reset circuit breaker
        CIRCUIT_BREAKER['failures'] = 0
        CIRCUIT_BREAKER['state'] = 'CLOSED'
        CIRCUIT_BREAKER['success_count'] = 0
        CIRCUIT_BREAKER['last_failure'] = None

        # Clear queue
        overwrite_queue([])
        logger.info("Queue cleared and circuit breaker reset")

        return jsonify({
            'success': True,
            'message': 'Queue cleared and circuit breaker reset',
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Emergency clear error: {e}")
        return jsonify({'error': str(e)}), 500

# Security monitoring endpoint
@app.route('/security-status', methods=['GET'])
def security_status():
    """Security status - requires API key"""
    api_key = request.headers.get('X-API-Key')
    if api_key != CONFIG['API_KEY']:
        return jsonify({'error': 'Invalid API key'}), 401

    return jsonify({
        'blocked_ips': len(blocked_ips),
        'blocked_list': list(blocked_ips.keys()),
        'rate_limited_ips': len(ip_requests),
        'security_config': SECURITY_CONFIG
    })

# Enhanced error handlers
@app.errorhandler(404)
def not_found(error):
    # Don't log 404s for suspicious requests to reduce noise
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(413)
def request_too_large(error):
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    logger.warning(f"📦 Request too large from {client_ip}")
    return jsonify({'error': 'Request too large'}), 413

@app.errorhandler(429)
def rate_limit_exceeded(error):
    return jsonify({'error': 'Rate limit exceeded'}), 429

def init_system():
    """Initialize the system and start background workers."""
    try:
        # Detect default printer
        printers = win32print.EnumPrinters(2)
        default_printer = None
        
        for printer in printers:
            printer_name = printer[2]
            if 'Star TSP100' in printer_name or 'TSP143' in printer_name:
                default_printer = printer_name
                break
        
        if not default_printer and printers:
            default_printer = printers[0][2]
        
        CONFIG['DEFAULT_PRINTER'] = default_printer
        
        # Start queue worker
        queue_thread = threading.Thread(target=queue_worker_loop, daemon=True)
        queue_thread.start()
        
        return True
        
    except Exception as e:
        logger.error(f"System initialization failed: {e}")
        return False

if __name__ == '__main__':
    print("=" * 70)
    print("HK SAVOR SPOON SECURE PRINT SERVER v5.0")
    print("=" * 70)
    print(f"Security Features:")
    print(f"  🛡️  IP Whitelisting & Rate Limiting")
    print(f"  🚫 Suspicious Request Blocking") 
    print(f"  📊 Security Monitoring")
    print(f"  🔐 Enhanced Authentication")
    print("")
    print(f"Printer: {CONFIG.get('DEFAULT_PRINTER', 'Not detected')}")
    print(f"API Key: {CONFIG['API_KEY'][:10]}...")
    print("")
    print("Available Endpoints:")
    print("  GET  /status          - Server status")
    print("  POST /print           - Print text (requires API key)")
    print("  GET  /queue           - Queue status (requires API key)")
    print("  POST /emergency-clear - Clear queue (requires API key)")
    print("  GET  /security-status - Security info (requires API key)")
    print("")
    print("🛡️  ENHANCED SECURITY ACTIVE")
    print("🔄 CIRCUIT BREAKER PROTECTION ACTIVE")
    print("📦 BACKGROUND RETRY QUEUE ACTIVE")
    print("Press Ctrl+C to stop the server")
    print("=" * 70)

    if not init_system():
        print("❌ System initialization failed!")
        sys.exit(1)

    try:
        app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        sys.exit(0)
