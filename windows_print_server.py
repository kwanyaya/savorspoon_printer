#!/usr/bin/env python3
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
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import win32print
import win32api
import tempfile

# Configuration
API_KEY = "hksavorspoon-secure-print-key-2025"  # Change this to a secure key
PORT = 8080
DEBUG = True

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

def get_default_printer():
    """Get the default printer name"""
    try:
        return win32print.GetDefaultPrinter()
    except Exception as e:
        logger.error(f"Error getting default printer: {e}")
        return None

def get_computer_info():
    """Get computer name and IP address"""
    try:
        computer_name = platform.node()
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        return computer_name, local_ip
    except Exception as e:
        logger.error(f"Error getting computer info: {e}")
        return "Unknown", "Unknown"

def validate_api_key(request):
    """Validate API key from request headers"""
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        api_key = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    if api_key != API_KEY:
        logger.warning(f"Invalid API key attempt from {request.remote_addr}")
        return False
    return True

def print_text(text, job_name="HKSavorSpoon Print Job", font_size="large"):
    """Print text to default printer with Star TSP100 Chinese character set support
    
    Args:
        text: Text to print
        job_name: Name for the print job
        font_size: Size of font - 'normal', 'large', 'double_height', 'double_width'
    """
    try:
        default_printer = get_default_printer()
        if not default_printer:
            raise Exception("No default printer found")
        
        # Check if this is a Star TSP100 printer
        is_star_printer = "star" in default_printer.lower() and "tsp" in default_printer.lower()
        
        if is_star_printer:
            # Detect if text contains Traditional or Simplified Chinese
            has_traditional = any('\u4e00' <= char <= '\u9fff' and 
                                ord(char) in [0x7e41, 0x9ad4, 0x4e2d, 0x6587, 0x6e2c, 0x5f0f, 0x7f8e, 0x5473, 0x6e6f, 0x5319] 
                                for char in text)
            
            # Determine best encoding and charset for the content
            encoding_methods = []
            
            # Method 1: Big5 for Traditional Chinese
            encoding_methods.append({
                "name": "Big5 Traditional",
                "encoding": "big5",
                "charset_cmd": b'\x1B\x40\x1B\x74\x0E\x1B\x52\x0F',  # Init + Big5 + Traditional
                "priority": 1 if has_traditional else 3
            })
            
            # Method 2: GBK for Simplified Chinese
            encoding_methods.append({
                "name": "GBK Simplified", 
                "encoding": "gbk",
                "charset_cmd": b'\x1B\x40\x1B\x74\x0F\x1B\x52\x08',  # Init + GBK + Simplified
                "priority": 3 if has_traditional else 1
            })
            
            # Method 3: GB2312 for Simplified Chinese
            encoding_methods.append({
                "name": "GB2312 Simplified",
                "encoding": "gb2312", 
                "charset_cmd": b'\x1B\x40\x1B\x74\x0F\x1C\x43\x02',  # Init + GB2312 + Chinese mode
                "priority": 4 if has_traditional else 2
            })
            
            # Method 4: Unicode UTF-8 (universal fallback)
            encoding_methods.append({
                "name": "Unicode UTF-8",
                "encoding": "utf-8",
                "charset_cmd": b'\x1B\x40\x1C\x2E\x1B\x74\x00',  # Init + Unicode + Default table
                "priority": 2
            })
            
            # Sort by priority
            encoding_methods.sort(key=lambda x: x['priority'])
            
            # Try each encoding method
            for method in encoding_methods:
                try:
                    # Open printer
                    printer_handle = win32print.OpenPrinter(default_printer)
                    
                    # Start document
                    doc_info = ("HKSavorSpoon Print Job", None, "RAW")
                    job_id = win32print.StartDocPrinter(printer_handle, 1, doc_info)
                    
                    # Start page
                    win32print.StartPagePrinter(printer_handle)
                    
                    # Prepare commands
                    commands = bytearray()
                    commands.extend(method['charset_cmd'])
                    
                    # Set text alignment to left
                    commands.extend(b'\x1B\x61\x00')  # ESC a 0 (Left align)
                    
                    # Set larger font size for better readability
                    commands.extend(b'\x1D\x21\x11')  # GS ! 17 (Double width and height)
                    # Alternative font size options:
                    # commands.extend(b'\x1D\x21\x01')  # Double height only
                    # commands.extend(b'\x1D\x21\x10')  # Double width only
                    # commands.extend(b'\x1D\x21\x00')  # Normal size
                    
                    # Encode text with the method's encoding
                    try:
                        if method['encoding'] == 'utf-8':
                            text_encoded = text.encode('utf-8', errors='replace')
                        elif method['encoding'] == 'big5':
                            text_encoded = text.encode('big5', errors='replace')
                        elif method['encoding'] == 'gbk':
                            text_encoded = text.encode('gbk', errors='replace')
                        elif method['encoding'] == 'gb2312':
                            text_encoded = text.encode('gb2312', errors='replace')
                        else:
                            continue  # Skip unsupported encoding
                        
                        # Add the encoded text
                        commands.extend(text_encoded)
                        
                        # Add line feeds and cut paper
                        commands.extend(b'\x0A\x0A\x0A')  # Line feeds
                        commands.extend(b'\x1B\x64\x03')  # Cut paper
                        
                        # Send to printer
                        win32print.WritePrinter(printer_handle, bytes(commands))
                        
                        # End page and document
                        win32print.EndPagePrinter(printer_handle)
                        win32print.EndDocPrinter(printer_handle)
                        win32print.ClosePrinter(printer_handle)
                        
                        logger.info(f"Print job '{job_name}' sent using {method['name']} encoding")
                        return True, f"Print job sent to {default_printer} (Star {method['name']})"
                        
                    except UnicodeEncodeError:
                        # This encoding can't handle the text, try next method
                        win32print.EndPagePrinter(printer_handle)
                        win32print.EndDocPrinter(printer_handle) 
                        win32print.ClosePrinter(printer_handle)
                        continue
                        
                except Exception as method_error:
                    logger.warning(f"Method {method['name']} failed: {method_error}")
                    try:
                        win32print.EndPagePrinter(printer_handle)
                        win32print.EndDocPrinter(printer_handle)
                        win32print.ClosePrinter(printer_handle)
                    except:
                        pass
                    continue
            
            # If all Star methods failed, raise exception
            raise Exception("All Star TSP100 encoding methods failed")
        
        else:
            # For non-Star printers, use standard method with UTF-8
            try:
                printer_handle = win32print.OpenPrinter(default_printer)
                doc_info = ("HKSavorSpoon Print Job", None, "RAW")
                job_id = win32print.StartDocPrinter(printer_handle, 1, doc_info)
                win32print.StartPagePrinter(printer_handle)
                
                # Standard UTF-8 encoding with BOM for better compatibility
                text_bytes = ('\ufeff' + text).encode('utf-8', errors='replace')
                win32print.WritePrinter(printer_handle, text_bytes)
                
                win32print.EndPagePrinter(printer_handle)
                win32print.EndDocPrinter(printer_handle)
                win32print.ClosePrinter(printer_handle)
                
                logger.info(f"Print job '{job_name}' sent to standard printer '{default_printer}'")
                return True, f"Print job sent to {default_printer} (Standard UTF-8)"
                
            except Exception as std_error:
                logger.warning(f"Standard printing failed: {std_error}, trying file method")
                
                # Final fallback to file method
                temp_dir = tempfile.gettempdir()
                temp_file_path = os.path.join(temp_dir, f"hk_print_{job_name.replace(' ', '_')}.txt")
                
                with open(temp_file_path, 'w', encoding='utf-8-sig') as tmp_file:
                    tmp_file.write(text)
                
                win32api.ShellExecute(0, "print", temp_file_path, None, ".", 0)
                
                import time
                time.sleep(2)
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
                    
                logger.info(f"Print job '{job_name}' sent via file method to '{default_printer}'")
                return True, f"Print job sent to {default_printer} (File Method)"
        
    except Exception as e:
        error_msg = f"Print error: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

def print_receipt(receipt_data):
    """Format and print receipt data"""
    try:
        # Extract receipt information
        order_id = receipt_data.get('order_id', 'N/A')
        customer_name = receipt_data.get('customer_name', 'N/A')
        items = receipt_data.get('items', [])
        total = receipt_data.get('total', '0.00')
        payment_method = receipt_data.get('payment_method', 'N/A')
        order_time = receipt_data.get('order_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        # Format receipt text
        receipt_text = f"""
================================
       HK SAVOR SPOON
================================
Order ID: {order_id}
Customer: {customer_name}
Date/Time: {order_time}
--------------------------------

ITEMS:
"""
        
        subtotal = 0
        for item in items:
            name = item.get('name', 'Unknown Item')
            quantity = item.get('quantity', 1)
            price = float(item.get('price', 0))
            item_total = quantity * price
            subtotal += item_total
            
            receipt_text += f"{name:<20} x{quantity}\n"
            receipt_text += f"  ${price:.2f} each = ${item_total:.2f}\n"
        
        receipt_text += f"""
--------------------------------
Subtotal: ${subtotal:.2f}
Total: ${total}
Payment: {payment_method}
--------------------------------

Thank you for your order!
Visit us at hksavorspoon.com

================================
"""
        
        return print_text(receipt_text, f"Receipt #{order_id}")
        
    except Exception as e:
        error_msg = f"Receipt formatting error: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

@app.route('/status', methods=['GET'])
def status():
    """Server status endpoint"""
    default_printer = get_default_printer()
    computer_name, local_ip = get_computer_info()
    
    return jsonify({
        'status': 'online',
        'server': 'HK Savor Spoon Windows Print Server',
        'version': '1.0',
        'computer': computer_name,
        'local_ip': local_ip,
        'default_printer': default_printer,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/printers', methods=['GET'])
def list_printers():
    """List available printers"""
    if not validate_api_key(request):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        printers = []
        printer_enum = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)
        
        for printer in printer_enum:
            printer_name = printer[2]
            printers.append({
                'name': printer_name,
                'is_default': printer_name == get_default_printer()
            })
        
        return jsonify({
            'printers': printers,
            'default_printer': get_default_printer()
        })
        
    except Exception as e:
        logger.error(f"Error listing printers: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/print', methods=['POST'])
def print_endpoint():
    """Print text or receipt"""
    if not validate_api_key(request):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        job_name = data.get('job_name', 'HKSavorSpoon Print Job')
        
        # Check if it's a receipt or plain text
        if 'receipt_data' in data:
            success, message = print_receipt(data['receipt_data'])
        elif 'text' in data:
            success, message = print_text(data['text'], job_name)
        else:
            return jsonify({'error': 'No text or receipt_data provided'}), 400
        
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
    """Test print endpoint"""
    if not validate_api_key(request):
        return jsonify({'error': 'Unauthorized'}), 401
    
    test_text = f"""
================================
    HK SAVOR SPOON TEST PRINT
================================
Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Server: {get_computer_info()[0]}
Printer: {get_default_printer()}

This is a test print to verify
your printer is working correctly.

If you can read this, your
Windows Print Server is 
configured properly!

================================
"""
    
    success, message = print_text(test_text, "Test Print")
    
    if success:
        return jsonify({
            'success': True,
            'message': 'Test print sent successfully',
            'timestamp': datetime.now().isoformat()
        })
    else:
        return jsonify({'error': message}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

def startup_info():
    """Display startup information"""
    print("\n" + "="*50)
    print("HK Savor Spoon Windows Print Server Starting")
    print("="*50)
    
    default_printer = get_default_printer()
    computer_name, local_ip = get_computer_info()
    
    print(f"Default Printer: {default_printer or 'NOT FOUND!'}")
    print(f"Server: {computer_name} ({local_ip})")
    print(f"API Key: {API_KEY[:10]}...")
    print(f"Server will run on http://0.0.0.0:{PORT}")
    print(f"Local access: http://localhost:{PORT}/status")
    print(f"Remote access: http://{local_ip}:{PORT}/status")
    print("\nEndpoints:")
    print(f"  GET  /status       - Server status")
    print(f"  GET  /printers     - List printers")
    print(f"  POST /print        - Print text or receipt")
    print(f"  POST /test-print   - Send test print")
    print("\nPress Ctrl+C to stop the server")
    print("="*50)
    
    if not default_printer:
        print("\n⚠️  WARNING: No default printer found!")
        print("Please set up a printer before using this server.")
        print("Go to Settings → Printers & scanners")
        print("Select your printer and set as default.")
    
    print("\n")

if __name__ == '__main__':
    try:
        startup_info()
        app.run(host='0.0.0.0', port=PORT, debug=DEBUG)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)
