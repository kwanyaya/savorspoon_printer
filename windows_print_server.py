
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HK Savor Spoon - Windows Print Server
Receives print jobs from Laravel web application and prints to local USB printer
"""

import os
import sys
import json
import logging
import socket
import platform
import tempfile
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import win32print
import win32api

# Configuration
API_KEY = "hksavorspoon-secure-print-key-2025"  # Change this to a secure key
PORT = 8080
DEBUG = False

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('print_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Flask app setup
app = Flask(__name__)
CORS(app)

def get_system_info():
    """Get system information including default printer and network details"""
    try:
        computer_name = platform.node()
        
        # Get local IP address
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        
        # Get default printer
        try:
            default_printer = win32print.GetDefaultPrinter()
        except Exception:
            default_printer = None
        
        # Get DDNS info if available
        ddns_info = get_ddns_info()
            
        return computer_name, local_ip, default_printer, ddns_info
        
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        return "Unknown", "Unknown", None, None

def get_ddns_info():
    """Get DDNS configuration info"""
    try:
        import json
        with open('ddns_config.json', 'r', encoding='utf-8-sig') as f:
            config = json.load(f)
            if config.get('enabled'):
                return {
                    'domain': config.get('domain_name', ''),
                    'provider': config.get('service_provider', ''),
                    'last_update': config.get('last_update', ''),
                    'enabled': True
                }
    except FileNotFoundError:
        pass
    except Exception as e:
        logger.warning(f"Error reading DDNS config: {e}")
    
    return None

def validate_api_key(request):
    """Validate API key from request headers"""
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        api_key = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    if api_key != API_KEY:
        logger.warning(f"Invalid API key attempt from {request.remote_addr}")
        return False
    return True

def _contains_traditional_chinese(text):
    """Detect if text contains Traditional Chinese characters"""
    # Common Traditional Chinese characters that differ from Simplified
    traditional_chars = {
        '繁', '體', '學', '國', '華', '語', '電', '話', '時', '間', '開', '關',
        '東', '西', '南', '北', '長', '車', '門', '風', '雞', '魚', '豬', '牛',
        '個', '這', '那', '說', '話', '來', '買', '賣', '錢', '銀', '金', '鐵',
        '書', '讀', '寫', '聽', '聲', '見', '視', '覺', '愛', '親', '朋', '友',
        '謝', '謝', '對', '錯', '議', '題', '問', '答', '會', '員', '務', '業',
        '總', '計', '單', '據', '訂', '購', '歡', '迎', '光', '臨', '顧', '客'
    }
    
    return any(char in traditional_chars for char in text)

def _contains_simplified_chinese(text):
    """Detect if text contains Simplified Chinese characters"""
    # Common Simplified Chinese characters
    simplified_chars = {
        '简', '体', '学', '国', '华', '语', '电', '话', '时', '间', '开', '关',
        '东', '西', '南', '北', '长', '车', '门', '风', '鸡', '鱼', '猪', '牛',
        '个', '这', '那', '说', '话', '来', '买', '卖', '钱', '银', '金', '铁',
        '书', '读', '写', '听', '声', '见', '视', '觉', '爱', '亲', '朋', '友',
        '谢', '谢', '对', '错', '议', '题', '问', '答', '会', '员', '务', '业',
        '总', '计', '单', '据', '订', '购', '欢', '迎', '光', '临', '顾', '客'
    }
    
    return any(char in simplified_chars for char in text)

def print_text_to_printer(text, job_name="HK Savor Spoon Print Job"):
    """
    Print text to default printer with optimized Chinese character support
    
    Args:
        text: Text to print (supports Chinese and English)
        job_name: Name for the print job
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        _, _, default_printer, _ = get_system_info()
        if not default_printer:
            raise Exception("No default printer found")
        
        # Check if this is a Star TSP100 printer (common thermal printer)
        is_star_printer = "star" in default_printer.lower() and "tsp" in default_printer.lower()
        
        if is_star_printer:
            return _print_to_star_printer(text, job_name, default_printer)
        else:
            return _print_to_standard_printer(text, job_name, default_printer)
            
    except Exception as e:
        error_msg = f"Print error: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

def _print_to_star_printer(text, job_name, printer_name):
    """Print to Star TSP100 with proper Chinese character encoding"""
    
    # Detect text type for better encoding selection
    has_traditional = _contains_traditional_chinese(text)
    has_simplified = _contains_simplified_chinese(text)
    
    logger.info(f"Text analysis - Traditional: {has_traditional}, Simplified: {has_simplified}")
    
    # Define encoding strategies optimized for Star TSP100
    encoding_strategies = []
    
    # If Traditional Chinese detected, prioritize Big5
    if has_traditional:
        encoding_strategies.extend([
            {
                "name": "Big5 Traditional Chinese",
                "encoding": "big5",
                "charset_cmd": b'\x1B\x40\x1B\x74\x0E',  # ESC @ ESC t 14 (Big5)
                "font_cmd": b'\x1C\x43\x01',              # FS C 1 (Chinese mode)
                "priority": 1
            },
            {
                "name": "Big5 with Extended Commands",
                "encoding": "big5", 
                "charset_cmd": b'\x1B\x40\x1B\x52\x0F\x1B\x74\x0E',  # Extended Big5 setup
                "font_cmd": b'\x1C\x43\x01\x1C\x26',                 # Chinese + Extended
                "priority": 2
            }
        ])
    
    # If Simplified Chinese detected, prioritize GBK/GB2312
    if has_simplified:
        encoding_strategies.extend([
            {
                "name": "GBK Simplified Chinese",
                "encoding": "gbk",
                "charset_cmd": b'\x1B\x40\x1B\x74\x0F',  # ESC @ ESC t 15 (GBK)
                "font_cmd": b'\x1C\x43\x02',              # FS C 2 (GB mode)
                "priority": 1 if not has_traditional else 3
            },
            {
                "name": "GB2312 Simplified Chinese",
                "encoding": "gb2312",
                "charset_cmd": b'\x1B\x40\x1B\x52\x08',  # Extended GB2312
                "font_cmd": b'\x1C\x43\x02',              # FS C 2 (GB mode)
                "priority": 2 if not has_traditional else 4
            }
        ])
    
    # Universal fallbacks
    encoding_strategies.extend([
        {
            "name": "UTF-8 with Chinese Support",
            "encoding": "utf-8",
            "charset_cmd": b'\x1B\x40\x1C\x2E',          # Reset + International
            "font_cmd": b'\x1B\x74\x00',                  # Character table 0
            "priority": 5
        },
        {
            "name": "CP950 Traditional (Windows)",
            "encoding": "cp950",
            "charset_cmd": b'\x1B\x40\x1B\x74\x0E',      # Big5 compatible
            "font_cmd": b'\x1C\x43\x01',                  # Chinese mode
            "priority": 6
        }
    ])
    
    # Sort strategies by priority
    encoding_strategies.sort(key=lambda x: x['priority'])
    
    # Try each encoding strategy
    for strategy in encoding_strategies:
        printer_handle = None
        job_id = None
        try:
            logger.info(f"Trying encoding strategy: {strategy['name']}")
            
            # Test if this encoding can handle the text
            try:
                test_encoded = text.encode(strategy['encoding'], errors='strict')
            except UnicodeEncodeError as ue:
                logger.warning(f"Encoding {strategy['encoding']} cannot handle text: {ue}")
                continue
            
            # Open printer with timeout handling
            try:
                printer_handle = win32print.OpenPrinter(printer_name)
                logger.info(f"Printer opened successfully: {printer_name}")
            except Exception as pe:
                logger.error(f"Failed to open printer {printer_name}: {pe}")
                continue
            
            try:
                doc_info = (job_name, None, "RAW")
                job_id = win32print.StartDocPrinter(printer_handle, 1, doc_info)
                logger.info(f"Document started with job ID: {job_id}")
                
                win32print.StartPagePrinter(printer_handle)
                logger.info("Page started successfully")
                
                # Prepare print commands
                commands = bytearray()
                
                # Initialize printer and set character set
                commands.extend(strategy['charset_cmd'])
                
                # Set font mode if available
                if 'font_cmd' in strategy:
                    commands.extend(strategy['font_cmd'])
                
                # Set text formatting
                commands.extend(b'\x1B\x61\x00')         # Left align
                commands.extend(b'\x1D\x21\x11')         # Double width and height
                
                # Add the encoded text
                commands.extend(test_encoded)
                
                # Add formatting and cut
                commands.extend(b'\x0A\x0A\x0A')         # Line feeds
                commands.extend(b'\x1B\x64\x03')         # Cut paper
                
                # Send to printer
                logger.info(f"Sending {len(commands)} bytes to printer...")
                bytes_written = win32print.WritePrinter(printer_handle, bytes(commands))
                logger.info(f"Successfully wrote {bytes_written} bytes to printer")
                
                # Cleanup
                win32print.EndPagePrinter(printer_handle)
                win32print.EndDocPrinter(printer_handle)
                win32print.ClosePrinter(printer_handle)
                
                logger.info(f"Print successful using {strategy['name']} encoding")
                return True, f"Print job sent to {printer_name} ({strategy['name']})"
                
            except Exception as print_error:
                logger.error(f"Print operation failed: {print_error}")
                # Cleanup on error
                try:
                    if job_id:
                        win32print.EndPagePrinter(printer_handle)
                        win32print.EndDocPrinter(printer_handle)
                    if printer_handle:
                        win32print.ClosePrinter(printer_handle)
                except Exception as cleanup_error:
                    logger.error(f"Cleanup failed: {cleanup_error}")
                continue
                
        except Exception as e:
            logger.warning(f"Strategy {strategy['name']} failed: {e}")
            # Cleanup on error
            try:
                if job_id and printer_handle:
                    win32print.EndPagePrinter(printer_handle)
                    win32print.EndDocPrinter(printer_handle)
                if printer_handle:
                    win32print.ClosePrinter(printer_handle)
            except Exception as cleanup_error:
                logger.error(f"Final cleanup failed: {cleanup_error}")
            continue
    
    # If all strategies failed
    raise Exception("All Star printer encoding strategies failed for Traditional Chinese text")

def _print_to_standard_printer(text, job_name, printer_name):
    """Print to standard printer with enhanced Chinese character support"""
    
    has_traditional = _contains_traditional_chinese(text)
    has_simplified = _contains_simplified_chinese(text)
    
    logger.info(f"Standard printer - Traditional: {has_traditional}, Simplified: {has_simplified}")
    
    # Try different encoding methods for standard printers
    encoding_methods = []
    
    # For Traditional Chinese, try Big5 and CP950 first
    if has_traditional:
        encoding_methods.extend([
            ("Big5", "big5"),
            ("CP950 (Windows Traditional)", "cp950"),
            ("UTF-16LE with BOM", "utf-16le")
        ])
    
    # For Simplified Chinese, try GBK and GB2312
    if has_simplified:
        encoding_methods.extend([
            ("GBK", "gbk"),
            ("GB2312", "gb2312"),
            ("CP936 (Windows Simplified)", "cp936")
        ])
    
    # Universal fallbacks
    encoding_methods.extend([
        ("UTF-8 with BOM", "utf-8-sig"),
        ("UTF-8", "utf-8"),
        ("UTF-16 with BOM", "utf-16")
    ])
    
    # Method 1: Try direct printing with various encodings
    for encoding_name, encoding in encoding_methods:
        try:
            logger.info(f"Trying direct print with {encoding_name}")
            
            printer_handle = win32print.OpenPrinter(printer_name)
            doc_info = (job_name, None, "RAW")
            job_id = win32print.StartDocPrinter(printer_handle, 1, doc_info)
            win32print.StartPagePrinter(printer_handle)
            
            # Encode text
            if encoding == "utf-16le":
                text_bytes = text.encode('utf-16le')
                # Add BOM for UTF-16LE
                text_bytes = b'\xff\xfe' + text_bytes
            elif encoding == "utf-8-sig":
                text_bytes = text.encode('utf-8-sig')
            else:
                text_bytes = text.encode(encoding, errors='replace')
            
            win32print.WritePrinter(printer_handle, text_bytes)
            
            win32print.EndPagePrinter(printer_handle)
            win32print.EndDocPrinter(printer_handle)
            win32print.ClosePrinter(printer_handle)
            
            logger.info(f"Direct print successful with {encoding_name}")
            return True, f"Print job sent to {printer_name} ({encoding_name})"
            
        except UnicodeEncodeError:
            logger.warning(f"Encoding {encoding} cannot handle the text")
            try:
                win32print.EndPagePrinter(printer_handle)
                win32print.EndDocPrinter(printer_handle)
                win32print.ClosePrinter(printer_handle)
            except:
                pass
            continue
            
        except Exception as direct_error:
            logger.warning(f"Direct printing with {encoding_name} failed: {direct_error}")
            try:
                win32print.EndPagePrinter(printer_handle)
                win32print.EndDocPrinter(printer_handle)
                win32print.ClosePrinter(printer_handle)
            except:
                pass
            continue
    
    # Method 2: File method fallback with multiple encoding attempts
    logger.info("Direct printing failed, trying file method")
    
    file_encodings = [
        ("UTF-8 with BOM", "utf-8-sig"),
        ("UTF-16 with BOM", "utf-16"),
        ("Big5", "big5"),
        ("GBK", "gbk"),
        ("CP950", "cp950")
    ]
    
    for encoding_name, encoding in file_encodings:
        try:
            temp_dir = tempfile.gettempdir()
            temp_file_path = os.path.join(temp_dir, f"hk_print_{job_name.replace(' ', '_')}.txt")
            
            # Try to write file with this encoding
            with open(temp_file_path, 'w', encoding=encoding) as tmp_file:
                tmp_file.write(text)
            
            # Print the file
            win32api.ShellExecute(0, "print", temp_file_path, None, ".", 0)
            
            # Clean up temp file after a delay
            import time
            time.sleep(3)
            try:
                os.unlink(temp_file_path)
            except:
                pass
                
            logger.info(f"File method successful with {encoding_name}")
            return True, f"Print job sent to {printer_name} (File Method - {encoding_name})"
            
        except UnicodeEncodeError:
            logger.warning(f"File method encoding {encoding} failed")
            continue
        except Exception as file_error:
            logger.warning(f"File method with {encoding_name} failed: {file_error}")
            continue
    
    # If everything failed
    raise Exception("Both direct and file printing failed with all encoding methods")

def format_receipt(receipt_data):
    """Format receipt data into printable text"""
    
    # Extract receipt information with defaults
    order_id = receipt_data.get('order_id', 'N/A')
    customer_name = receipt_data.get('customer_name', 'N/A')
    items = receipt_data.get('items', [])
    total = receipt_data.get('total', '0.00')
    payment_method = receipt_data.get('payment_method', 'N/A')
    order_time = receipt_data.get('order_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    # Build receipt text
    receipt_lines = [
        "================================",
        "       HK SAVOR SPOON",
        "================================",
        f"Order ID: {order_id}",
        f"Customer: {customer_name}",
        f"Date/Time: {order_time}",
        "--------------------------------",
        "",
        "ITEMS:"
    ]
    
    # Add items
    subtotal = 0
    for item in items:
        name = item.get('name', 'Unknown Item')
        quantity = item.get('quantity', 1)
        price = float(item.get('price', 0))
        item_total = quantity * price
        subtotal += item_total
        
        receipt_lines.extend([
            f"{name:<20} x{quantity}",
            f"  ${price:.2f} each = ${item_total:.2f}"
        ])
    
    # Add totals and footer
    receipt_lines.extend([
        "",
        "--------------------------------",
        f"Subtotal: ${subtotal:.2f}",
        f"Total: ${total}",
        f"Payment: {payment_method}",
        "--------------------------------",
        "",
        "Thank you for your order!",
        "Visit us at hksavorspoon.com",
        "",
        "================================"
    ])
    
    return "\n".join(receipt_lines)

# API Routes

@app.route('/status', methods=['GET'])
def status():
    """Server status endpoint - public access"""
    computer_name, local_ip, default_printer, ddns_info = get_system_info()
    
    status_data = {
        'status': 'online',
        'server': 'HK Savor Spoon Windows Print Server',
        'version': '2.0',
        'computer': computer_name,
        'local_ip': local_ip,
        'default_printer': default_printer,
        'timestamp': datetime.now().isoformat()
    }
    
    # Add DDNS info if available
    if ddns_info:
        status_data['ddns'] = ddns_info
        status_data['external_access'] = f"http://{ddns_info['domain']}:5000"
    
    return jsonify(status_data)

@app.route('/printers', methods=['GET'])
def list_printers():
    """List available printers - requires API key"""
    if not validate_api_key(request):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        printers = []
        printer_enum = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)
        _, _, default_printer, _ = get_system_info()
        
        for printer in printer_enum:
            printer_name = printer[2]
            printers.append({
                'name': printer_name,
                'is_default': printer_name == default_printer
            })
        
        return jsonify({
            'printers': printers,
            'default_printer': default_printer,
            'count': len(printers)
        })
        
    except Exception as e:
        logger.error(f"Error listing printers: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/print', methods=['POST'])
def print_endpoint():
    """Print text or receipt - requires API key"""
    if not validate_api_key(request):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        job_name = data.get('job_name', 'HK Savor Spoon Print Job')
        
        # Handle receipt data
        if 'receipt_data' in data:
            try:
                text_to_print = format_receipt(data['receipt_data'])
                job_name = f"Receipt #{data['receipt_data'].get('order_id', 'N/A')}"
            except Exception as e:
                return jsonify({'error': f'Receipt formatting error: {str(e)}'}), 400
                
        # Handle plain text
        elif 'text' in data:
            text_to_print = data['text']
        else:
            return jsonify({'error': 'No text or receipt_data provided'}), 400
        
        # Print the text
        success, message = print_text_to_printer(text_to_print, job_name)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'job_name': job_name,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({'error': message}), 500
            
    except Exception as e:
        logger.error(f"Print endpoint error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/test-print', methods=['POST'])
def test_print():
    """Send a test print - requires API key"""
    if not validate_api_key(request):
        return jsonify({'error': 'Unauthorized'}), 401
    
    computer_name, local_ip, default_printer, ddns_info = get_system_info()
    
    test_text = f"""
================================
    HK SAVOR SPOON TEST PRINT
================================
Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Server: {computer_name}
Local IP: {local_ip}
Printer: {default_printer}

This is a test print to verify
your printer is working correctly.

English text: Hello World!
Chinese text: 你好世界！
Traditional: 繁體中文測試

If you can read this, your
Windows Print Server is 
configured properly!

================================
"""
    
    success, message = print_text_to_printer(test_text, "Test Print")
    
    if success:
        return jsonify({
            'success': True,
            'message': 'Test print sent successfully',
            'timestamp': datetime.now().isoformat()
        })
    else:
        return jsonify({'error': message}), 500

# Error handlers

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

def display_startup_info():
    """Display startup information"""
    computer_name, local_ip, default_printer, ddns_info = get_system_info()
    
    print("\n" + "="*60)
    print("HK SAVOR SPOON WINDOWS PRINT SERVER v2.0")
    print("="*60)
    print(f"Computer: {computer_name}")
    print(f"Local IP: {local_ip}")
    print(f"Default Printer: {default_printer or 'NOT FOUND!'}")
    
    # Display DDNS info if available
    if ddns_info:
        print(f"DDNS Domain: {ddns_info['domain']}")
        print(f"DDNS Provider: {ddns_info['provider']}")
        print(f"External Access: http://{ddns_info['domain']}:{PORT}")
        print(f"Last DDNS Update: {ddns_info.get('last_update', 'Never')}")
    else:
        print("DDNS: savorspoon-printer.myddns.me (NoIP)")
        print(f"External Access: http://savorspoon-printer.myddns.me:{PORT}")
        print("DDNS Status: Download NoIP client from noip.com")
    
    print(f"API Key: {API_KEY[:10]}...")
    print(f"Server URL: http://0.0.0.0:{PORT}")
    print(f"Local Access: http://localhost:{PORT}/status")
    print(f"Network Access: http://{local_ip}:{PORT}/status")
    print("\nAvailable Endpoints:")
    print("  GET  /status       - Server status (public)")
    print("  GET  /printers     - List printers (requires API key)")
    print("  POST /print        - Print text/receipt (requires API key)")
    print("  POST /test-print   - Send test print (requires API key)")
    print("\nPress Ctrl+C to stop the server")
    print("="*60)
    
    if not default_printer:
        print("\n⚠️  WARNING: No default printer found!")
        print("Please set up a printer before using this server.")
        print("Go to Settings → Printers & scanners")
        print("Select your printer and set as default.")
    
    print()
 
if __name__ == '__main__':
    try:
        display_startup_info()
        app.run(host='0.0.0.0', port=PORT, debug=DEBUG)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)
