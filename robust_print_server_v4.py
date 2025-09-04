# -*- coding: utf-8 -*-
"""
IMPROVED PRINT SERVER v4.0 - Circuit Breaker + Enhanced Timeout
===============================================================
Addresses persistent timeout issues with circuit breaker pattern
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
from datetime import datetime
import os
from contextlib import contextmanager

# Configure logging with more detail and Unicode support
import io
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')),
        logging.FileHandler('print_server_debug.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global configuration
CONFIG = {
    'API_KEY': 'hksavorspoon-secure-print-key-2025',
    'DEFAULT_PRINTER': None,
    'PRINT_TIMEOUT': 3,  # Reduced to 3 seconds for faster failure detection
    'LOCAL_IP': None,
    'DDNS_CONFIG': None
}

# Circuit breaker state
CIRCUIT_BREAKER = {
    'failures': 0,
    'last_failure': None,
    'state': 'CLOSED',  # CLOSED, OPEN, HALF_OPEN
    'failure_threshold': 3,
    'recovery_timeout': 60,  # seconds
    'success_count': 0,
    'min_successes': 2
}

# --- Persistent print retry queue (file-backed)
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
    for ln in lines:
        try:
            jobs.append(json_module.loads(ln))
        except Exception as e:
            logger.warning(f"Failed to parse queue line: {e}")
    return jobs

def overwrite_queue(jobs):
    """Overwrite queue file with provided list of job dicts."""
    with QUEUE_LOCK:
        with open(QUEUE_FILE, 'w', encoding='utf-8') as f:
            for job in jobs:
                f.write(json_module.dumps(job, ensure_ascii=False) + '\n')

def update_circuit_breaker(success):
    """Update circuit breaker state based on operation result."""
    global CIRCUIT_BREAKER

    if success:
        CIRCUIT_BREAKER['success_count'] += 1
        CIRCUIT_BREAKER['failures'] = 0

        if CIRCUIT_BREAKER['state'] == 'HALF_OPEN' and CIRCUIT_BREAKER['success_count'] >= CIRCUIT_BREAKER['min_successes']:
            CIRCUIT_BREAKER['state'] = 'CLOSED'
            CIRCUIT_BREAKER['success_count'] = 0
            logger.info("Circuit breaker CLOSED - printing restored")
        elif CIRCUIT_BREAKER['state'] == 'CLOSED':
            CIRCUIT_BREAKER['success_count'] = 0
    else:
        CIRCUIT_BREAKER['failures'] += 1
        CIRCUIT_BREAKER['last_failure'] = datetime.now()

        if CIRCUIT_BREAKER['state'] == 'CLOSED' and CIRCUIT_BREAKER['failures'] >= CIRCUIT_BREAKER['failure_threshold']:
            CIRCUIT_BREAKER['state'] = 'OPEN'
            logger.warning(f"🚫 Circuit breaker OPEN - {CIRCUIT_BREAKER['failures']} consecutive failures")
        elif CIRCUIT_BREAKER['state'] == 'HALF_OPEN':
            CIRCUIT_BREAKER['state'] = 'OPEN'
            CIRCUIT_BREAKER['success_count'] = 0
            logger.warning("🚫 Circuit breaker re-OPENED - half-open attempt failed")

def is_circuit_breaker_open():
    """Check if circuit breaker should allow requests."""
    if CIRCUIT_BREAKER['state'] == 'CLOSED':
        return False
    elif CIRCUIT_BREAKER['state'] == 'OPEN':
        # Check if recovery timeout has passed
        if CIRCUIT_BREAKER['last_failure']:
            elapsed = (datetime.now() - CIRCUIT_BREAKER['last_failure']).total_seconds()
            if elapsed >= CIRCUIT_BREAKER['recovery_timeout']:
                CIRCUIT_BREAKER['state'] = 'HALF_OPEN'
                CIRCUIT_BREAKER['success_count'] = 0
                logger.info("Circuit breaker HALF-OPEN - testing recovery")
                return False
        return True
    elif CIRCUIT_BREAKER['state'] == 'HALF_OPEN':
        return False
    return False

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

def process_print_job(job):
    """Process a queued print job with circuit breaker awareness"""
    printer_name = CONFIG.get('DEFAULT_PRINTER')
    if not printer_name:
        return False, 'No default printer configured'

    try:
        printer = AggressiveTimeoutPrinter(printer_name, timeout_seconds=CONFIG.get('PRINT_TIMEOUT', 3))
        success, message = printer.print_with_aggressive_timeout(job['text'])
        update_circuit_breaker(success)
        return success, message
    except Exception as e:
        update_circuit_breaker(False)
        return False, str(e)

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

# Initialize configuration
CONFIG['DEFAULT_PRINTER'] = win32print.GetDefaultPrinter() if win32print else None
CONFIG['LOCAL_IP'] = "127.0.0.1"  # Default fallback

# Clear print queue on startup
try:
    printers = win32print.EnumPrinters(2) if win32print else []
    for printer in printers:
        printer_name = printer[2]
        try:
            printer_handle = win32print.OpenPrinter(printer_name)
            jobs = win32print.EnumJobs(printer_handle, 0, -1, 1)
            for job in jobs:
                try:
                    win32print.SetJob(printer_handle, job['JobId'], 0, None, win32print.JOB_CONTROL_DELETE)
                    logger.info(f"Cleared job {job['JobId']} from {printer_name}")
                except:
                    pass
            win32print.ClosePrinter(printer_handle)
        except:
            pass
except:
    pass

# Start background queue worker thread
queue_thread = threading.Thread(target=queue_worker_loop, args=(10,), daemon=True)
queue_thread.start()

@app.route('/status', methods=['GET'])
def status():
    """Get server status with circuit breaker info"""
    try:
        printer_name = CONFIG['DEFAULT_PRINTER']
        printer_status = "Unknown"
        if printer_name and win32print:
            try:
                printer_handle = win32print.OpenPrinter(printer_name)
                printer_info = win32print.GetPrinter(printer_handle, 2)
                status_code = printer_info.get('Status', 0)
                # Map status codes to readable names
                status_map = {0: "Ready", 0x00000001: "Paused", 0x00000002: "Error", 0x00000080: "Offline"}
                printer_status = status_map.get(status_code, f"Status {status_code}")
                win32print.ClosePrinter(printer_handle)
            except:
                printer_status = "Error"

        ddns_info = CONFIG.get('DDNS_CONFIG', {})
        external_url = f"http://{ddns_info.get('domain', 'unknown')}:8080" if ddns_info else "Not configured"

        return jsonify({
            'status': 'online',
            'server': 'HK Savor Spoon Print Server v4.0 (Circuit Breaker)',
            'timestamp': datetime.now().isoformat(),
            'printer': {
                'name': printer_name,
                'status': printer_status
            },
            'network': {
                'local_ip': CONFIG['LOCAL_IP'],
                'external_url': external_url
            },
            'circuit_breaker': {
                'state': CIRCUIT_BREAKER['state'],
                'failures': CIRCUIT_BREAKER['failures'],
                'last_failure': CIRCUIT_BREAKER['last_failure'].isoformat() if CIRCUIT_BREAKER['last_failure'] else None
            },
            'queue': {
                'jobs_pending': len(read_queue())
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/print', methods=['POST'])
def print_text():
    """Print with circuit breaker and aggressive retry"""
    # Check API key
    api_key = request.headers.get('X-API-Key')
    if api_key != CONFIG['API_KEY']:
        return jsonify({'error': 'Invalid API key'}), 401

    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'Missing text parameter'}), 400

        text = data['text']
        printer_name = CONFIG['DEFAULT_PRINTER']

        if not printer_name:
            return jsonify({'error': 'No default printer configured'}), 500

        # Check circuit breaker
        if is_circuit_breaker_open():
            logger.warning("🚫 Circuit breaker OPEN - queuing request")
            job = {
                'id': str(uuid.uuid4()),
                'text': text,
                'attempts': 0,
                'timestamp': datetime.now().isoformat(),
                'reason': 'circuit_breaker_open'
            }
            enqueue_print_job(job)
            return jsonify({
                'success': False,
                'queued': True,
                'queue_id': job['id'],
                'error': 'Printing temporarily disabled due to repeated failures',
                'circuit_breaker': CIRCUIT_BREAKER['state']
            }), 503

        logger.info(f"Print request received ({len(text)} chars)")

        # Use aggressive timeout printer
        printer = AggressiveTimeoutPrinter(printer_name, timeout_seconds=CONFIG['PRINT_TIMEOUT'])
        success, message = printer.print_with_aggressive_timeout(text)

        update_circuit_breaker(success)

        if success:
            return jsonify({
                'success': True,
                'message': message,
                'printer': printer_name,
                'timestamp': datetime.now().isoformat()
            })

        # If print failed, attempt one immediate retry
        logger.warning(f"Initial print attempt failed: {message}. Attempting immediate retry...")
        success2, message2 = printer.print_with_aggressive_timeout(text)

        update_circuit_breaker(success2)

        if success2:
            logger.info(f"Immediate retry succeeded: {message2}")
            return jsonify({
                'success': True,
                'message': message2,
                'printer': printer_name,
                'timestamp': datetime.now().isoformat()
            })

        # If still failing, enqueue for background retry
        job = {
            'id': str(uuid.uuid4()),
            'text': text,
            'attempts': 1,
            'timestamp': datetime.now().isoformat(),
            'last_error': message2
        }
        enqueue_print_job(job)
        logger.error(f"Print job enqueued for background retry: {job['id']} (error: {message2})")

        return jsonify({
            'success': False,
            'queued': True,
            'queue_id': job['id'],
            'error': message2,
            'printer': printer_name,
            'circuit_breaker': CIRCUIT_BREAKER['state']
        }), 202

    except Exception as e:
        error_msg = f"Print endpoint error: {str(e)}"
        logger.error(error_msg)
        update_circuit_breaker(False)
        return jsonify({'error': error_msg}), 500

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

        # Clear Windows print queue
        try:
            printers = win32print.EnumPrinters(2) if win32print else []
            for printer in printers:
                printer_name = printer[2]
                try:
                    printer_handle = win32print.OpenPrinter(printer_name)
                    jobs = win32print.EnumJobs(printer_handle, 0, -1, 1)
                    for job in jobs:
                        try:
                            win32print.SetJob(printer_handle, job['JobId'], 0, None, win32print.JOB_CONTROL_DELETE)
                            logger.info(f"Cleared job {job['JobId']} from {printer_name}")
                        except:
                            pass
                    win32print.ClosePrinter(printer_handle)
                except:
                    pass
        except:
            pass

        return jsonify({
            'success': True,
            'message': 'Print queue cleared and circuit breaker reset',
            'timestamp': datetime.now().isoformat(),
            'circuit_breaker': CIRCUIT_BREAKER['state']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/queue', methods=['GET'])
def get_queue_status():
    """Get queue status and circuit breaker info"""
    api_key = request.headers.get('X-API-Key')
    if api_key != CONFIG['API_KEY']:
        return jsonify({'error': 'Invalid API key'}), 401

    try:
        jobs = read_queue()
        return jsonify({
            'queue': {
                'jobs_count': len(jobs),
                'jobs': [{'id': j.get('id'), 'attempts': j.get('attempts', 0), 'timestamp': j.get('timestamp')} for j in jobs[:10]]  # First 10 jobs
            },
            'circuit_breaker': CIRCUIT_BREAKER
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 70)
    print("HK SAVOR SPOON PRINT SERVER v4.0 - CIRCUIT BREAKER EDITION")
    print("=" * 70)
    print(f"Computer: {os.environ.get('COMPUTERNAME', 'Unknown')}")
    print(f"Local IP: {CONFIG['LOCAL_IP']}")
    print(f"Default Printer: {CONFIG['DEFAULT_PRINTER']}")
    print(f"Print Timeout: {CONFIG['PRINT_TIMEOUT']} seconds")
    print(f"API Key: {CONFIG['API_KEY'][:10]}...")
    print("")
    print("Available Endpoints:")
    print("  GET  /status          - Server status (public)")
    print("  POST /print           - Print text (requires API key)")
    print("  GET  /queue           - Queue status (requires API key)")
    print("  POST /emergency-clear - Clear queue & reset circuit breaker (requires API key)")
    print("")
    print("CIRCUIT BREAKER PROTECTION ACTIVE")
    print("AGGRESSIVE TIMEOUT PROTECTION ACTIVE")
    print("BACKGROUND RETRY QUEUE ACTIVE")
    print("Press Ctrl+C to stop the server")
    print("=" * 70)

    try:
        app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        sys.exit(0)
