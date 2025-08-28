#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HK Savor Spoon Windows Print Server - Port 8080 Version
Alternative port for ISPs that block 5000
"""

# Import all the same modules from the original server
import os
import sys
import logging
import tempfile
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import win32print
import win32api
import socket
import platform

# Configuration - Changed to port 8080
API_KEY = "hksavorspoon-secure-print-key-2025"
PORT = 8080  # Changed from 5000
DEBUG = True

# Copy all the functions from the original server
# (This is a port 8080 version - router config: External 8080 → Internal 8080)

print(f"""
==================================================
HK Savor Spoon Windows Print Server (Port 8080)
==================================================
This version runs on port 8080 instead of 5000
Configure your router port forwarding:
- External Port: 8080
- Internal IP: [your current IP]
- Internal Port: 8080
- Protocol: TCP

Update your website to use:
http://58.153.166.26:8080/print
==================================================
""")

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('print_server_8080.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_local_ip():
    """Get local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

@app.route('/status', methods=['GET'])
def status():
    """Get server status"""
    return jsonify({
        'status': 'online',
        'server': 'HK Savor Spoon Windows Print Server (Port 8080)',
        'version': '1.1',
        'computer': platform.node(),
        'local_ip': get_local_ip(),
        'port': PORT,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/print', methods=['POST'])
def print_text_simple():
    """Simple print endpoint for testing"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        text = data.get('text', '')
        
        # Simple print to default printer
        try:
            printers = [printer[2] for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)]
            if not printers:
                return jsonify({'error': 'No printers found'}), 500
            
            default_printer = win32print.GetDefaultPrinter()
            
            # Print the text
            printer_handle = win32print.OpenPrinter(default_printer)
            doc_info = ("HK Savor Spoon Order", None, "RAW")
            job_id = win32print.StartDocPrinter(printer_handle, 1, doc_info)
            win32print.StartPagePrinter(printer_handle)
            
            # Send text as UTF-8
            text_bytes = text.encode('utf-8', errors='replace')
            win32print.WritePrinter(printer_handle, text_bytes)
            
            win32print.EndPagePrinter(printer_handle)
            win32print.EndDocPrinter(printer_handle)
            win32print.ClosePrinter(printer_handle)
            
            logger.info(f"Print successful on port 8080")
            
            return jsonify({
                'success': True,
                'message': f'Printed to {default_printer} via port 8080',
                'printer': default_printer,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as print_error:
            logger.error(f"Print error: {print_error}")
            return jsonify({'error': f'Print failed: {str(print_error)}'}), 500
            
    except Exception as e:
        logger.error(f"Request error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print(f"""
🚀 Starting HK Savor Spoon Print Server on Port 8080
Local access: http://localhost:8080/status
Network access: http://{get_local_ip()}:8080/status
Public access: http://58.153.166.26:8080/status (after router config)

Configure router port forwarding:
External Port: 8080 → Internal IP: {get_local_ip()}:8080
""")
    
    app.run(host='0.0.0.0', port=PORT, debug=DEBUG)
