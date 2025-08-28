# HK Savor Spoon Print Server Configuration
# Copy this file to config.py and modify as needed

# Server Configuration
API_KEY = "hksavorspoon-secure-print-key-2025"  # Change this to a secure, unique key
PORT = 5000                                      # Server port
DEBUG = True                                     # Set to False in production

# Printer Configuration
AUTO_CUT = True                                  # Auto-cut paper after printing (if supported)
PAPER_WIDTH = 58                                 # Paper width in mm (58mm for most thermal printers)
PRINT_DENSITY = "medium"                         # Print density: light, medium, dark

# Receipt Configuration
RESTAURANT_NAME = "HK SAVOR SPOON"
RESTAURANT_ADDRESS = "123 Main Street, Hong Kong"
RESTAURANT_PHONE = "+852 1234 5678"
RESTAURANT_EMAIL = "orders@hksavorspoon.com"
WEBSITE = "hksavorspoon.com"

# Network Configuration
ALLOWED_IPS = []                                 # Empty list allows all IPs, or specify: ["192.168.1.0/24"]
CORS_ORIGINS = ["https://hksavorspoon.com"]      # Allowed CORS origins

# Logging Configuration
LOG_LEVEL = "INFO"                               # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "print_server.log"
MAX_LOG_SIZE = 10 * 1024 * 1024                 # 10MB
LOG_BACKUP_COUNT = 5

# Security Configuration
RATE_LIMIT = 100                                 # Max requests per minute per IP
API_KEY_HEADER = "X-API-Key"                     # Header name for API key
REQUIRE_HTTPS = False                            # Set to True in production with SSL

# Print Job Configuration
MAX_PRINT_QUEUE = 50                             # Maximum queued print jobs
PRINT_TIMEOUT = 30                               # Print timeout in seconds
RETRY_ATTEMPTS = 3                               # Number of retry attempts for failed prints
