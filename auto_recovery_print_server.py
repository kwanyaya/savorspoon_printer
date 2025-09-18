# -*- coding: utf-8 -*-
"""
AUTO-RECOVERY PRINT SERVER v6.0 - Enhanced with Printer Recovery
================================================================
Automatically handles printer offline, spooler issues, and connection problems
"""

import win32print
import win32api
import win32gui
import win32service
import win32serviceutil
import json
import threading
import time
import signal
import sys
import uuid
import pathlib
import subprocess
import os
import psutil
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from datetime import datetime, timedelta
from contextlib import contextmanager
from collections import defaultdict
import ipaddress

# Configure logging with more detail and Unicode support
import io
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')),
        logging.FileHandler('print_server_recovery.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global configuration
CONFIG = {
    'API_KEY': 'hksavorspoon-secure-print-key-2025',
    'DEFAULT_PRINTER': None,
    'PRINT_TIMEOUT': 2,
    'FAST_PRINT_TIMEOUT': 1,
    'LOCAL_IP': None,
    'DDNS_CONFIG': None,
    'AUTO_RECOVERY': True,  # Enable automatic recovery
    'RECOVERY_MAX_RETRIES': 3,
    'PRINTER_CHECK_INTERVAL': 30,  # Check printer every 30 seconds
    'SPOOLER_RESTART_COOLDOWN': 60,  # Wait 60s between spooler restarts
    'FONT_SIZE': 'normal',  # Font size: 'small', 'normal', 'large', 'xlarge', 'double'
    'FONT_BOLD': False,  # Enable bold font
}

# Printer recovery state
RECOVERY_STATE = {
    'last_spooler_restart': 0,
    'spooler_restart_count': 0,
    'printer_offline_count': 0,
    'last_printer_check': 0,
    'recovery_in_progress': False,
    'lock': threading.Lock()
}

# Security configuration (same as v5)
SECURITY_CONFIG = {
    'RATE_LIMIT_REQUESTS': 10,
    'RATE_LIMIT_WINDOW': 60,
    'MAX_REQUEST_SIZE': 1024 * 1024,
    'BLOCK_DURATION': 300,
    'SUSPICIOUS_THRESHOLD': 5,
}

# IP tracking for rate limiting and security
ip_requests = defaultdict(list)
blocked_ips = {}
suspicious_patterns = [
    'ssh-', 'connect ', 'git', '.env', 'login', 'admin', 'boaform',
    'manager/', 'cgi-bin', 'favicon.ico', 'robots.txt', '.well-known'
]

# Allowed IP ranges
ALLOWED_IP_RANGES = [
    '192.168.0.0/16',
    '10.0.0.0/8',
    '172.16.0.0/12',
    '127.0.0.0/8',
    '151.106.117.246',
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
    
    for pattern in suspicious_patterns:
        if pattern in path or pattern in user_agent:
            return True
    
    if request.method not in ['GET', 'POST', 'OPTIONS']:
        return True
        
    if len(request.path) > 100:
        return True
        
    return False

def cleanup_old_records():
    """Clean up old IP tracking records"""
    current_time = time.time()
    cutoff_time = current_time - SECURITY_CONFIG['RATE_LIMIT_WINDOW']
    
    for ip in list(ip_requests.keys()):
        ip_requests[ip] = [req_time for req_time in ip_requests[ip] if req_time > cutoff_time]
        if not ip_requests[ip]:
            del ip_requests[ip]
    
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
    
    # Fast path for trusted IPs
    if is_ip_allowed(client_ip):
        return None
    
    current_time = time.time()
    
    if current_time % 30 < 1:
        cleanup_old_records()
    
    # Check if IP is blocked
    if client_ip in blocked_ips:
        if blocked_ips[client_ip] > current_time:
            logger.warning(f"🚫 Blocked IP attempted access: {client_ip}")
            return jsonify({'error': 'Access denied'}), 403
    
    # For non-allowed IPs, apply strict security
    if not is_ip_allowed(client_ip):
        if is_suspicious_request(request):
            logger.warning(f"🔍 Suspicious request from {client_ip}: {request.method} {request.path}")
            return jsonify({'error': 'Not found'}), 404
        
        # Rate limiting
        ip_requests[client_ip].append(current_time)
        recent_requests = [t for t in ip_requests[client_ip] 
                          if t > current_time - SECURITY_CONFIG['RATE_LIMIT_WINDOW']]
        
        if len(recent_requests) > SECURITY_CONFIG['RATE_LIMIT_REQUESTS']:
            logger.warning(f"⚡ Rate limit exceeded for {client_ip}")
            return jsonify({'error': 'Rate limit exceeded'}), 429

# ====================================================================
# PRINTER RECOVERY FUNCTIONS
# ====================================================================

def is_service_running(service_name):
    """Check if a Windows service is running"""
    try:
        service_handle = win32serviceutil.SmartOpenService(None, service_name)
        status = win32service.QueryServiceStatus(service_handle)[1]
        win32service.CloseServiceHandle(service_handle)
        return status == win32service.SERVICE_RUNNING
    except Exception as e:
        logger.error(f"Error checking service {service_name}: {e}")
        return False

def restart_print_spooler():
    """Restart Windows Print Spooler service"""
    with RECOVERY_STATE['lock']:
        current_time = time.time()
        
        # Check cooldown period
        if current_time - RECOVERY_STATE['last_spooler_restart'] < CONFIG['SPOOLER_RESTART_COOLDOWN']:
            logger.warning("🕐 Spooler restart on cooldown")
            return False
        
        try:
            logger.info("🔄 Attempting to restart Print Spooler service...")
            
            # Stop the spooler
            result = subprocess.run(['net', 'stop', 'spooler'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                logger.warning(f"Stop spooler warning: {result.stderr}")
            
            # Wait a moment
            time.sleep(3)
            
            # Start the spooler
            result = subprocess.run(['net', 'start', 'spooler'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                logger.info("✅ Print Spooler restarted successfully")
                RECOVERY_STATE['last_spooler_restart'] = current_time
                RECOVERY_STATE['spooler_restart_count'] += 1
                
                # Wait for spooler to fully initialize
                time.sleep(5)
                return True
            else:
                logger.error(f"❌ Failed to start Print Spooler: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Spooler restart timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Error restarting Print Spooler: {e}")
            return False

def clear_print_queue():
    """Clear all pending print jobs"""
    try:
        logger.info("🗑️  Clearing print queue...")
        
        # Stop spooler to clear queue
        subprocess.run(['net', 'stop', 'spooler'], capture_output=True, text=True)
        time.sleep(2)
        
        # Clear spool directory
        spool_dir = r"C:\Windows\System32\spool\PRINTERS"
        if os.path.exists(spool_dir):
            for filename in os.listdir(spool_dir):
                if filename.endswith(('.spl', '.shd')):
                    try:
                        os.remove(os.path.join(spool_dir, filename))
                        logger.debug(f"Removed spool file: {filename}")
                    except Exception as e:
                        logger.warning(f"Could not remove {filename}: {e}")
        
        # Restart spooler
        subprocess.run(['net', 'start', 'spooler'], capture_output=True, text=True)
        time.sleep(3)
        
        logger.info("✅ Print queue cleared")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error clearing print queue: {e}")
        return False

def get_printer_status(printer_name):
    """Get detailed printer status"""
    try:
        printer_handle = win32print.OpenPrinter(printer_name)
        printer_info = win32print.GetPrinter(printer_handle, 2)
        win32print.ClosePrinter(printer_handle)
        
        status = printer_info['Status']
        attributes = printer_info['Attributes']
        
        status_info = {
            'online': not (status & win32print.PRINTER_STATUS_OFFLINE),
            'error': bool(status & win32print.PRINTER_STATUS_ERROR),
            'paper_jam': bool(status & win32print.PRINTER_STATUS_PAPER_JAM),
            'paper_out': bool(status & win32print.PRINTER_STATUS_PAPER_OUT),
            'paused': bool(status & win32print.PRINTER_STATUS_PAUSED),
            'pending_deletion': bool(status & win32print.PRINTER_STATUS_PENDING_DELETION),
            'busy': bool(status & win32print.PRINTER_STATUS_BUSY),
            'door_open': bool(status & win32print.PRINTER_STATUS_DOOR_OPEN),
            'toner_low': bool(status & win32print.PRINTER_STATUS_TONER_LOW),
            'out_of_memory': bool(status & win32print.PRINTER_STATUS_OUT_OF_MEMORY),
            'raw_status': status,
            'raw_attributes': attributes
        }
        
        logger.debug(f"Printer {printer_name} status: {status_info}")
        return status_info
        
    except Exception as e:
        logger.error(f"Error getting printer status for {printer_name}: {e}")
        return {'online': False, 'error': True, 'error_message': str(e)}

def attempt_printer_recovery(printer_name):
    """Attempt to recover an offline or problematic printer"""
    with RECOVERY_STATE['lock']:
        if RECOVERY_STATE['recovery_in_progress']:
            logger.info("🔄 Recovery already in progress")
            return False
        
        RECOVERY_STATE['recovery_in_progress'] = True
    
    try:
        logger.info(f"🚑 Starting printer recovery for {printer_name}")
        
        # Step 1: Check if spooler is running
        if not is_service_running('Spooler'):
            logger.warning("🚨 Print Spooler is not running!")
            if restart_print_spooler():
                logger.info("✅ Print Spooler restarted")
            else:
                logger.error("❌ Failed to restart Print Spooler")
                return False
        
        # Step 2: Clear print queue if there are stuck jobs
        try:
            jobs = win32print.EnumJobs(win32print.OpenPrinter(printer_name), 0, -1, 1)
            if len(jobs) > 5:  # Too many queued jobs might indicate a problem
                logger.warning(f"📄 Found {len(jobs)} queued jobs, clearing queue")
                clear_print_queue()
        except:
            pass
        
        # Step 3: Check printer status
        status = get_printer_status(printer_name)
        
        # Step 4: Try to fix common issues
        if status.get('paused'):
            logger.info("▶️  Printer is paused, attempting to resume")
            try:
                printer_handle = win32print.OpenPrinter(printer_name)
                win32print.SetPrinter(printer_handle, 0, None, win32print.PRINTER_CONTROL_RESUME)
                win32print.ClosePrinter(printer_handle)
                logger.info("✅ Printer resumed")
                time.sleep(2)
            except Exception as e:
                logger.error(f"❌ Failed to resume printer: {e}")
        
        # Step 5: Test printer connection
        try:
            test_handle = win32print.OpenPrinter(printer_name)
            win32print.GetPrinter(test_handle, 1)
            win32print.ClosePrinter(test_handle)
            logger.info("✅ Printer connection test successful")
            return True
        except Exception as e:
            logger.error(f"❌ Printer connection test failed: {e}")
            
            # Step 6: Last resort - restart spooler
            logger.info("🔄 Last resort: restarting Print Spooler")
            if restart_print_spooler():
                # Wait and test again
                time.sleep(5)
                try:
                    test_handle = win32print.OpenPrinter(printer_name)
                    win32print.ClosePrinter(test_handle)
                    logger.info("✅ Printer recovery successful after spooler restart")
                    return True
                except:
                    logger.error("❌ Printer still not accessible after spooler restart")
                    return False
            else:
                return False
    
    finally:
        with RECOVERY_STATE['lock']:
            RECOVERY_STATE['recovery_in_progress'] = False

def printer_health_monitor():
    """Background thread to monitor printer health"""
    logger.info("🏥 Printer health monitor started")
    
    while True:
        try:
            if CONFIG['DEFAULT_PRINTER'] and CONFIG['AUTO_RECOVERY']:
                current_time = time.time()
                
                # Check printer health every interval
                if current_time - RECOVERY_STATE['last_printer_check'] > CONFIG['PRINTER_CHECK_INTERVAL']:
                    RECOVERY_STATE['last_printer_check'] = current_time
                    
                    try:
                        # Quick printer test
                        printer_handle = win32print.OpenPrinter(CONFIG['DEFAULT_PRINTER'])
                        status_info = win32print.GetPrinter(printer_handle, 2)
                        win32print.ClosePrinter(printer_handle)
                        
                        # Check if printer is offline
                        if status_info['Status'] & win32print.PRINTER_STATUS_OFFLINE:
                            RECOVERY_STATE['printer_offline_count'] += 1
                            logger.warning(f"🔴 Printer offline detected (count: {RECOVERY_STATE['printer_offline_count']})")
                            
                            # Attempt recovery after 2 consecutive offline detections
                            if RECOVERY_STATE['printer_offline_count'] >= 2:
                                logger.info("🚑 Triggering automatic printer recovery")
                                if attempt_printer_recovery(CONFIG['DEFAULT_PRINTER']):
                                    RECOVERY_STATE['printer_offline_count'] = 0
                                    logger.info("✅ Automatic recovery successful")
                                else:
                                    logger.error("❌ Automatic recovery failed")
                        else:
                            # Printer is online, reset counter
                            if RECOVERY_STATE['printer_offline_count'] > 0:
                                logger.info("🟢 Printer back online")
                                RECOVERY_STATE['printer_offline_count'] = 0
                    
                    except Exception as e:
                        RECOVERY_STATE['printer_offline_count'] += 1
                        logger.warning(f"🔴 Printer check failed: {e} (count: {RECOVERY_STATE['printer_offline_count']})")
                        
                        if RECOVERY_STATE['printer_offline_count'] >= 3:
                            logger.info("🚑 Triggering recovery due to repeated failures")
                            if attempt_printer_recovery(CONFIG['DEFAULT_PRINTER']):
                                RECOVERY_STATE['printer_offline_count'] = 0
            
            time.sleep(10)  # Check every 10 seconds, but only do full check per interval
        
        except Exception as e:
            logger.error(f"Printer health monitor error: {e}")
            time.sleep(30)

# Circuit breaker and printer connection pool (same as v5)
CIRCUIT_BREAKER = {
    'failures': 0,
    'last_failure': None,
    'state': 'CLOSED',
    'failure_threshold': 3,
    'recovery_timeout': 60,
    'success_count': 0,
    'min_successes': 2
}

PRINTER_POOL = {
    'handle': None,
    'last_used': None,
    'connection_timeout': 30,
    'lock': threading.Lock()
}

def get_pooled_printer_handle():
    """Get a pooled printer handle with automatic recovery"""
    with PRINTER_POOL['lock']:
        current_time = time.time()
        
        # Check if existing handle is still valid
        if (PRINTER_POOL['handle'] and 
            PRINTER_POOL['last_used'] and 
            current_time - PRINTER_POOL['last_used'] < PRINTER_POOL['connection_timeout']):
            
            try:
                # Quick validation
                win32print.GetPrinter(PRINTER_POOL['handle'], 1)
                PRINTER_POOL['last_used'] = current_time
                return PRINTER_POOL['handle']
            except:
                # Handle is stale, close it
                try:
                    win32print.ClosePrinter(PRINTER_POOL['handle'])
                except:
                    pass
                PRINTER_POOL['handle'] = None
        
        # Create new connection with recovery attempt
        max_attempts = 2
        for attempt in range(max_attempts):
            try:
                PRINTER_POOL['handle'] = win32print.OpenPrinter(CONFIG['DEFAULT_PRINTER'])
                PRINTER_POOL['last_used'] = current_time
                return PRINTER_POOL['handle']
            except Exception as e:
                logger.error(f"Failed to open printer connection (attempt {attempt + 1}): {e}")
                
                # If first attempt fails and auto-recovery is enabled, try recovery
                if attempt == 0 and CONFIG['AUTO_RECOVERY']:
                    logger.info("🚑 Attempting printer recovery before retry")
                    if attempt_printer_recovery(CONFIG['DEFAULT_PRINTER']):
                        logger.info("✅ Recovery successful, retrying connection")
                        time.sleep(2)  # Give printer time to stabilize
                        continue
                
                if attempt == max_attempts - 1:
                    logger.error("❌ All printer connection attempts failed")
                    return None

class AutoRecoveryPrinter:
    """Enhanced printer with automatic recovery capabilities"""

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

    def _get_font_commands(self, font_size=None, bold=None):
        """Generate font control commands for Star TSP100 printer"""
        commands = bytearray()
        
        # Use global config if not specified
        if font_size is None:
            font_size = CONFIG.get('FONT_SIZE', 'normal')
        if bold is None:
            bold = CONFIG.get('FONT_BOLD', False)
        
        # Font size commands for Star TSP100
        font_commands = {
            'small': b'\x1B\x21\x01',      # Small font (12x24 dots)
            'normal': b'\x1B\x21\x00',     # Normal font (12x24 dots) - default
            'large': b'\x1B\x21\x10',      # Large font (24x48 dots) - width doubled
            'xlarge': b'\x1B\x21\x20',     # Extra large font (24x48 dots) - height doubled  
            'double': b'\x1B\x21\x30',     # Double size (24x48 dots) - both width & height doubled
        }
        
        # Set font size
        if font_size in font_commands:
            commands.extend(font_commands[font_size])
        else:
            commands.extend(font_commands['normal'])  # Default to normal
        
        # Bold on/off commands
        if bold:
            commands.extend(b'\x1B\x45\x01')  # Bold ON
        else:
            commands.extend(b'\x1B\x45\x00')  # Bold OFF
        
        return commands

    def _print_worker_with_recovery(self, text):
        """Print worker with automatic recovery on failure"""
        printer_handle = None
        job_id = None
        use_pooled = True
        recovery_attempted = False

        try:
            # Try to get printer handle with recovery
            printer_handle = get_pooled_printer_handle()
            if not printer_handle:
                logger.warning("❌ Could not get printer handle even after recovery attempt")
                self.print_error = "Printer connection failed after recovery attempt"
                return

            # Determine encoding
            is_chinese = self._is_chinese_text(text)
            if is_chinese:
                try:
                    text_bytes = text.encode('big5', errors='replace')
                    encoding = "Big5"
                    charset_cmd = b'\x1B\x74\x0E'
                except:
                    text_bytes = text.encode('utf-8', errors='replace')
                    encoding = "UTF-8"
                    charset_cmd = b''
            else:
                text_bytes = text.encode('utf-8', errors='replace')
                encoding = "UTF-8"
                charset_cmd = b''

            logger.debug(f"Using encoding: {encoding}, {len(text_bytes)} bytes")

            # Start print job
            doc_info = ("HK Savor Spoon Auto-Recovery Print", None, "RAW")
            job_id = win32print.StartDocPrinter(printer_handle, 1, doc_info)
            win32print.StartPagePrinter(printer_handle)

            # Build and send commands
            commands = bytearray()
            commands.extend(b'\x1B\x40')  # Reset printer
            commands.extend(charset_cmd)  # Charset if needed
            commands.extend(self._get_font_commands(self.font_size, self.font_bold))  # Font size and bold settings
            commands.extend(text_bytes)
            commands.extend(b'\x0A\x0A\x1B\x64\x02')  # Line feeds + Cut

            # Write in chunks
            chunk_size = 512
            total_written = 0

            for i in range(0, len(commands), chunk_size):
                if self.force_stop:
                    raise Exception("Print operation cancelled by timeout")

                chunk = commands[i:i + chunk_size]
                written = win32print.WritePrinter(printer_handle, bytes(chunk))
                total_written += written

                if i + chunk_size < len(commands):
                    time.sleep(0.0005)

            logger.debug(f"Written {total_written} bytes")

            # Complete job
            win32print.EndPagePrinter(printer_handle)
            win32print.EndDocPrinter(printer_handle)

            self.print_result = {
                'success': True,
                'bytes_written': total_written,
                'encoding': encoding,
                'message': f'Print completed successfully ({total_written} bytes)',
                'recovery_used': recovery_attempted
            }

        except Exception as e:
            error_msg = f"Print error: {str(e)}"
            logger.error(error_msg)
            
            # If we haven't tried recovery yet and auto-recovery is enabled, try it
            if not recovery_attempted and CONFIG['AUTO_RECOVERY'] and "timed out" not in str(e).lower():
                logger.info("🚑 Print failed, attempting recovery")
                recovery_attempted = True
                
                if attempt_printer_recovery(self.printer_name):
                    logger.info("✅ Recovery successful, retrying print")
                    # Close current handle and retry with new connection
                    try:
                        if job_id and printer_handle:
                            win32print.EndPagePrinter(printer_handle)
                            win32print.EndDocPrinter(printer_handle)
                    except:
                        pass
                    
                    # Reset printer pool to force new connection
                    with PRINTER_POOL['lock']:
                        if PRINTER_POOL['handle']:
                            try:
                                win32print.ClosePrinter(PRINTER_POOL['handle'])
                            except:
                                pass
                            PRINTER_POOL['handle'] = None
                    
                    # Retry the print operation (recursive call, but limited by recovery_attempted flag)
                    time.sleep(2)  # Give printer time to stabilize
                    if not self.force_stop:
                        self._print_worker_with_recovery(text)
                        return
            
            self.print_error = error_msg

            # Emergency cleanup
            try:
                if job_id and printer_handle:
                    win32print.EndPagePrinter(printer_handle)
                    win32print.EndDocPrinter(printer_handle)
            except:
                pass

    def print_with_auto_recovery(self, text, font_size=None, font_bold=None):
        """Print with automatic recovery on failure"""
        self.print_result = None
        self.print_error = None
        self.force_stop = False
        self.font_size = font_size
        self.font_bold = font_bold

        # Create worker thread
        self.worker_thread = threading.Thread(
            target=self._print_worker_with_recovery,
            args=(text,),
            daemon=True
        )

        logger.info(f"Starting auto-recovery print (timeout: {self.timeout}s)")
        start_time = time.time()
        self.worker_thread.start()

        # Wait with timeout
        self.worker_thread.join(timeout=self.timeout)
        elapsed = time.time() - start_time

        if self.worker_thread.is_alive():
            logger.warning(f"Print operation hung after {elapsed:.1f}s - forcing stop")
            self.force_stop = True
            self.worker_thread.join(timeout=1.0)

            if self.worker_thread.is_alive():
                logger.error("💀 Print thread did not respond to stop signal")

            return False, f"Print operation timeout after {elapsed:.1f}s"

        # Check results
        if self.print_error:
            return False, self.print_error

        if self.print_result and self.print_result['success']:
            recovery_msg = " (with recovery)" if self.print_result.get('recovery_used') else ""
            logger.info(f"Print completed in {elapsed:.1f}s{recovery_msg}")
            return True, self.print_result['message']

        return False, "Print operation failed with no result"

# Circuit breaker functions (same as v5)
def is_circuit_breaker_open():
    """Check if circuit breaker is open."""
    if CIRCUIT_BREAKER['state'] == 'OPEN':
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

# Queue management (similar to v5 but using the new printer class)
QUEUE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'print_queue.jsonl')
QUEUE_LOCK = threading.Lock()

def enqueue_print_job(job):
    """Append a job to the persistent queue as a JSON line."""
    pathlib.Path(QUEUE_FILE).parent.mkdir(parents=True, exist_ok=True)
    with QUEUE_LOCK:
        with open(QUEUE_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(job, ensure_ascii=False) + '\n')
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
            jobs.append(json.loads(line))
        except Exception as e:
            logger.error(f"Failed to parse queue line: {e}")
    return jobs

def overwrite_queue(jobs):
    """Overwrite the queue file with new list of jobs."""
    pathlib.Path(QUEUE_FILE).parent.mkdir(parents=True, exist_ok=True)
    with QUEUE_LOCK:
        with open(QUEUE_FILE, 'w', encoding='utf-8') as f:
            for job in jobs:
                f.write(json.dumps(job, ensure_ascii=False) + '\n')

def process_print_job(job):
    """Process a single print job with auto-recovery."""
    try:
        text = job.get('text', '')
        printer_name = CONFIG['DEFAULT_PRINTER']

        if not printer_name:
            return False, "No printer configured"

        if is_circuit_breaker_open():
            return False, "Circuit breaker open"

        printer = AutoRecoveryPrinter(printer_name, CONFIG['PRINT_TIMEOUT'])
        success, message = printer.print_with_auto_recovery(text)

        if success:
            record_print_success()
        else:
            record_print_failure()

        return success, message

    except Exception as e:
        record_print_failure()
        return False, str(e)

def queue_worker_loop(poll_interval=10):
    """Background worker that retries queued print jobs."""
    logger.info('Print queue worker started (with auto-recovery)')
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

# API Routes with auto-recovery
@app.route('/status', methods=['GET'])
def status():
    """Server status endpoint with recovery information"""
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    
    if not is_ip_allowed(client_ip):
        return jsonify({
            'status': 'online',
            'server': 'HK Savor Spoon Auto-Recovery Print Server',
            'version': '6.0-auto-recovery'
        })
    
    # Get printer status
    printer_status = None
    if CONFIG['DEFAULT_PRINTER']:
        printer_status = get_printer_status(CONFIG['DEFAULT_PRINTER'])
    
    return jsonify({
        'status': 'online',
        'server': 'HK Savor Spoon Auto-Recovery Print Server',
        'version': '6.0-auto-recovery',
        'printer': CONFIG['DEFAULT_PRINTER'],
        'printer_status': printer_status,
        'auto_recovery': CONFIG['AUTO_RECOVERY'],
        'font_config': {
            'font_size': CONFIG['FONT_SIZE'],
            'font_bold': CONFIG['FONT_BOLD']
        },
        'recovery_stats': {
            'spooler_restarts': RECOVERY_STATE['spooler_restart_count'],
            'offline_detections': RECOVERY_STATE['printer_offline_count'],
            'recovery_in_progress': RECOVERY_STATE['recovery_in_progress']
        },
        'circuit_breaker': {
            'state': CIRCUIT_BREAKER['state'],
            'failures': CIRCUIT_BREAKER['failures']
        },
        'queue_size': len(read_queue()),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/print', methods=['POST'])
def print_text():
    """Print with auto-recovery capabilities"""
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
        fast_mode = data.get('fast', False)
        font_size = data.get('font_size', CONFIG['FONT_SIZE'])  # Allow per-request font size
        font_bold = data.get('font_bold', CONFIG['FONT_BOLD'])  # Allow per-request bold setting
        printer_name = CONFIG['DEFAULT_PRINTER']

        if not printer_name:
            return jsonify({'error': 'No default printer configured'}), 500

        logger.info(f"📝 Print request from {client_ip} ({len(text)} chars, fast={fast_mode}, recovery=enabled)")

        # Check circuit breaker
        if is_circuit_breaker_open():
            logger.warning("🚫 Circuit breaker OPEN - queuing request")
            job = {
                'id': str(uuid.uuid4()),
                'text': text,
                'attempts': 0,
                'timestamp': datetime.now().isoformat(),
                'source': client_ip,
                'fast': fast_mode
            }
            enqueue_print_job(job)
            return jsonify({
                'success': True,
                'message': 'Print job queued (circuit breaker active)',
                'queued': True,
                'job_id': job['id']
            })

        # Choose timeout based on mode
        timeout = CONFIG['FAST_PRINT_TIMEOUT'] if fast_mode else CONFIG['PRINT_TIMEOUT']
        
        # Try immediate print with auto-recovery
        printer = AutoRecoveryPrinter(printer_name, timeout)
        success, message = printer.print_with_auto_recovery(text, font_size, font_bold)

        if success:
            record_print_success()
            logger.info(f"✅ Print successful for {client_ip}: {message}")
            return jsonify({
                'success': True,
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'fast_mode': fast_mode,
                'auto_recovery': True
            })
        else:
            record_print_failure()
            logger.warning(f"❌ Print failed for {client_ip}: {message}")

            # Queue for retry (only if not in fast mode)
            if not fast_mode:
                job = {
                    'id': str(uuid.uuid4()),
                    'text': text,
                    'attempts': 0,
                    'timestamp': datetime.now().isoformat(),
                    'source': client_ip,
                    'fast': False
                }
                enqueue_print_job(job)

                return jsonify({
                    'success': True,
                    'message': 'Print job queued for retry with auto-recovery',
                    'queued': True,
                    'job_id': job['id'],
                    'retry_reason': message
                })
            else:
                return jsonify({
                    'success': False,
                    'message': f'Fast print failed: {message}',
                    'fast_mode': True
                }), 500

    except Exception as e:
        logger.error(f"Print endpoint error from {client_ip}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/recovery/trigger', methods=['POST'])
def trigger_manual_recovery():
    """Manually trigger printer recovery"""
    api_key = request.headers.get('X-API-Key')
    if api_key != CONFIG['API_KEY']:
        return jsonify({'error': 'Invalid API key'}), 401

    if not CONFIG['DEFAULT_PRINTER']:
        return jsonify({'error': 'No printer configured'}), 500

    logger.info("🚑 Manual recovery triggered")
    success = attempt_printer_recovery(CONFIG['DEFAULT_PRINTER'])
    
    return jsonify({
        'success': success,
        'message': 'Recovery successful' if success else 'Recovery failed',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/recovery/status', methods=['GET'])
def recovery_status():
    """Get recovery status and statistics"""
    api_key = request.headers.get('X-API-Key')
    if api_key != CONFIG['API_KEY']:
        return jsonify({'error': 'Invalid API key'}), 401

    printer_status = None
    if CONFIG['DEFAULT_PRINTER']:
        printer_status = get_printer_status(CONFIG['DEFAULT_PRINTER'])

    return jsonify({
        'auto_recovery_enabled': CONFIG['AUTO_RECOVERY'],
        'printer_status': printer_status,
        'recovery_stats': {
            'spooler_restarts': RECOVERY_STATE['spooler_restart_count'],
            'offline_detections': RECOVERY_STATE['printer_offline_count'],
            'last_spooler_restart': RECOVERY_STATE['last_spooler_restart'],
            'recovery_in_progress': RECOVERY_STATE['recovery_in_progress'],
            'last_printer_check': RECOVERY_STATE['last_printer_check']
        },
        'spooler_running': is_service_running('Spooler'),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/recovery/config', methods=['POST'])
def update_recovery_config():
    """Update recovery configuration"""
    api_key = request.headers.get('X-API-Key')
    if api_key != CONFIG['API_KEY']:
        return jsonify({'error': 'Invalid API key'}), 401

    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No configuration data provided'}), 400

        if 'auto_recovery' in data:
            CONFIG['AUTO_RECOVERY'] = bool(data['auto_recovery'])
            logger.info(f"Auto-recovery {'enabled' if CONFIG['AUTO_RECOVERY'] else 'disabled'}")

        if 'printer_check_interval' in data:
            CONFIG['PRINTER_CHECK_INTERVAL'] = max(10, int(data['printer_check_interval']))
            logger.info(f"Printer check interval set to {CONFIG['PRINTER_CHECK_INTERVAL']}s")

        if 'recovery_max_retries' in data:
            CONFIG['RECOVERY_MAX_RETRIES'] = max(1, int(data['recovery_max_retries']))
            logger.info(f"Recovery max retries set to {CONFIG['RECOVERY_MAX_RETRIES']}")

        return jsonify({
            'success': True,
            'message': 'Recovery configuration updated',
            'config': {
                'auto_recovery': CONFIG['AUTO_RECOVERY'],
                'printer_check_interval': CONFIG['PRINTER_CHECK_INTERVAL'],
                'recovery_max_retries': CONFIG['RECOVERY_MAX_RETRIES']
            }
        })

    except Exception as e:
        logger.error(f"Config update error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/font/config', methods=['POST'])
def update_font_config():
    """Update font configuration"""
    api_key = request.headers.get('X-API-Key')
    if api_key != CONFIG['API_KEY']:
        return jsonify({'error': 'Invalid API key'}), 401

    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No configuration data provided'}), 400

        valid_font_sizes = ['small', 'normal', 'large', 'xlarge', 'double']
        
        if 'font_size' in data:
            font_size = data['font_size'].lower()
            if font_size in valid_font_sizes:
                CONFIG['FONT_SIZE'] = font_size
                logger.info(f"Font size set to: {font_size}")
            else:
                return jsonify({
                    'error': f'Invalid font size. Valid options: {valid_font_sizes}'
                }), 400

        if 'font_bold' in data:
            CONFIG['FONT_BOLD'] = bool(data['font_bold'])
            logger.info(f"Font bold {'enabled' if CONFIG['FONT_BOLD'] else 'disabled'}")

        return jsonify({
            'success': True,
            'message': 'Font configuration updated',
            'config': {
                'font_size': CONFIG['FONT_SIZE'],
                'font_bold': CONFIG['FONT_BOLD'],
                'valid_font_sizes': valid_font_sizes
            }
        })

    except Exception as e:
        logger.error(f"Font config update error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/font/config', methods=['GET'])
def get_font_config():
    """Get current font configuration"""
    api_key = request.headers.get('X-API-Key')
    if api_key != CONFIG['API_KEY']:
        return jsonify({'error': 'Invalid API key'}), 401

    return jsonify({
        'font_size': CONFIG['FONT_SIZE'],
        'font_bold': CONFIG['FONT_BOLD'],
        'valid_font_sizes': ['small', 'normal', 'large', 'xlarge', 'double'],
        'font_descriptions': {
            'small': 'Small font (12x24 dots)',
            'normal': 'Normal font (12x24 dots) - default',
            'large': 'Large font - width doubled',
            'xlarge': 'Extra large font - height doubled',
            'double': 'Double size - both width & height doubled'
        }
    })

# Queue and emergency endpoints (same as v5)
@app.route('/queue', methods=['GET'])
def get_queue_status():
    """Get print queue status"""
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
        },
        'auto_recovery': CONFIG['AUTO_RECOVERY']
    })

@app.route('/emergency-clear', methods=['POST'])
def emergency_clear():
    """Emergency endpoint to clear print queue, reset circuit breaker, and restart spooler"""
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
        
        # Clear system print queue and restart spooler
        clear_print_queue()
        
        # Reset recovery state
        with RECOVERY_STATE['lock']:
            RECOVERY_STATE['printer_offline_count'] = 0
            RECOVERY_STATE['recovery_in_progress'] = False

        logger.info("Emergency clear completed")

        return jsonify({
            'success': True,
            'message': 'Emergency clear completed: queue cleared, circuit breaker reset, spooler restarted',
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Emergency clear error: {e}")
        return jsonify({'error': str(e)}), 500

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
        
        # Start printer health monitor
        if CONFIG['AUTO_RECOVERY']:
            health_thread = threading.Thread(target=printer_health_monitor, daemon=True)
            health_thread.start()
        
        return True
        
    except Exception as e:
        logger.error(f"System initialization failed: {e}")
        return False

if __name__ == '__main__':
    print("=" * 80)
    print("HK SAVOR SPOON AUTO-RECOVERY PRINT SERVER v6.0")
    print("=" * 80)
    print(f"🚑 AUTO-RECOVERY FEATURES:")
    print(f"  🔄 Automatic Print Spooler Management")
    print(f"  🏥 Continuous Printer Health Monitoring")
    print(f"  🔧 Automatic Printer Offline Recovery")
    print(f"  🗑️  Smart Print Queue Clearing")
    print(f"  ⚡ Connection Pool with Recovery")
    print("")
    print(f"🛡️  SECURITY FEATURES:")
    print(f"  🛡️  IP Whitelisting & Rate Limiting")
    print(f"  🚫 Suspicious Request Blocking") 
    print(f"  📊 Security Monitoring")
    print(f"  🔐 Enhanced Authentication")
    print("")
    print(f"⚙️  CONFIGURATION:")
    print(f"  Printer: {CONFIG.get('DEFAULT_PRINTER', 'Not detected')}")
    print(f"  Auto-Recovery: {'✅ ENABLED' if CONFIG['AUTO_RECOVERY'] else '❌ DISABLED'}")
    print(f"  Health Check Interval: {CONFIG['PRINTER_CHECK_INTERVAL']}s")
    print(f"  Print Timeout: {CONFIG['PRINT_TIMEOUT']}s (normal), {CONFIG['FAST_PRINT_TIMEOUT']}s (fast)")
    print(f"  Font Size: {CONFIG['FONT_SIZE'].upper()} {'+ BOLD' if CONFIG['FONT_BOLD'] else ''}")
    print(f"  API Key: {CONFIG['API_KEY'][:10]}...")
    print("")
    print("📡 AVAILABLE ENDPOINTS:")
    print("  GET  /status                - Server & printer status")
    print("  POST /print                 - Print with auto-recovery (supports font_size, font_bold)")
    print("  GET  /queue                 - Queue status")
    print("  POST /emergency-clear       - Emergency reset & clear")
    print("  POST /recovery/trigger      - Manual recovery trigger")
    print("  GET  /recovery/status       - Recovery statistics")
    print("  POST /recovery/config       - Update recovery settings")
    print("  GET  /font/config           - Get font settings")
    print("  POST /font/config           - Update font settings")
    print("")
    print("🚑 AUTO-RECOVERY ACTIVE - Monitoring printer health...")
    print("🔄 CIRCUIT BREAKER PROTECTION ACTIVE")
    print("📦 BACKGROUND RETRY QUEUE ACTIVE")
    print("Press Ctrl+C to stop the server")
    print("=" * 80)

    if not init_system():
        print("❌ System initialization failed!")
        sys.exit(1)

    try:
        app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        # Clean up pooled printer connection
        with PRINTER_POOL['lock']:
            if PRINTER_POOL['handle']:
                try:
                    win32print.ClosePrinter(PRINTER_POOL['handle'])
                except:
                    pass
        sys.exit(0)
