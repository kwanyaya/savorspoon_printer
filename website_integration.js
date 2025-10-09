/**
 * HK Savor Spoon Cloud Print Integration
 * JavaScript code for hksavorspoon.com to send print requests to cloud server
 */

class SavorSpoonCloudPrint {
    constructor(config) {
        this.cloudServerUrl = config.cloudServerUrl || 'http://YOUR_CLOUD_SERVER_IP:8080';
        this.restaurantId = config.restaurantId || 'hk-savor-spoon-main';
        this.apiKey = config.apiKey || 'hksavorspoon-secure-print-key-2025';
        this.retryAttempts = config.retryAttempts || 3;
        this.retryDelay = config.retryDelay || 2000; // 2 seconds
    }

    /**
     * Print receipt through cloud server
     * @param {string} receiptText - The receipt content to print
     * @param {Object} options - Additional options
     * @returns {Promise} - Print result
     */
    async printReceipt(receiptText, options = {}) {
        const printData = {
            restaurant_id: options.restaurantId || this.restaurantId,
            text: receiptText,
            timestamp: new Date().toISOString(),
            order_id: options.orderId || null,
            table: options.table || null
        };

        try {
            console.log('🖨️ Sending print request to cloud server...');
            
            const response = await fetch(`${this.cloudServerUrl}/print`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Origin': window.location.origin,
                    'X-API-Key': this.apiKey
                },
                body: JSON.stringify(printData)
            });

            const result = await response.json();

            if (response.ok && result.success) {
                console.log('✅ Print successful:', result.message);
                return {
                    success: true,
                    message: result.message,
                    restaurantId: result.restaurant_id,
                    printerIp: result.printer_ip,
                    timestamp: result.timestamp
                };
            } else {
                console.warn('⚠️ Print failed:', result.message);
                
                // If queued, that's still considered a success
                if (result.queued) {
                    return {
                        success: true,
                        message: 'Print queued for retry',
                        queued: true
                    };
                }
                
                throw new Error(result.message || 'Print failed');
            }

        } catch (error) {
            console.error('❌ Print error:', error);
            throw error;
        }
    }

    /**
     * Print with automatic retry
     * @param {string} receiptText - The receipt content
     * @param {Object} options - Additional options
     * @returns {Promise} - Print result with retry logic
     */
    async printWithRetry(receiptText, options = {}) {
        let lastError;
        
        for (let attempt = 1; attempt <= this.retryAttempts; attempt++) {
            try {
                console.log(`🔄 Print attempt ${attempt}/${this.retryAttempts}`);
                
                const result = await this.printReceipt(receiptText, options);
                
                // Success!
                if (result.success) {
                    if (attempt > 1) {
                        console.log(`✅ Print succeeded on attempt ${attempt}`);
                    }
                    return result;
                }
                
            } catch (error) {
                lastError = error;
                console.warn(`❌ Attempt ${attempt} failed:`, error.message);
                
                // Don't retry on the last attempt
                if (attempt < this.retryAttempts) {
                    console.log(`⏳ Waiting ${this.retryDelay}ms before retry...`);
                    await this.delay(this.retryDelay);
                }
            }
        }
        
        // All attempts failed
        throw new Error(`Print failed after ${this.retryAttempts} attempts: ${lastError.message}`);
    }

    /**
     * Check cloud server status
     * @returns {Promise} - Server health status
     */
    async checkServerStatus() {
        try {
            const response = await fetch(`${this.cloudServerUrl}/health`, {
                method: 'GET',
                headers: {
                    'X-API-Key': this.apiKey
                }
            });

            if (response.ok) {
                const status = await response.json();
                console.log('✅ Cloud server online:', status);
                return status;
            } else {
                throw new Error(`Server returned ${response.status}`);
            }

        } catch (error) {
            console.error('❌ Server status check failed:', error);
            throw error;
        }
    }

    /**
     * Get list of registered printers
     * @returns {Promise} - List of printers
     */
    async getRegisteredPrinters() {
        try {
            const response = await fetch(`${this.cloudServerUrl}/printers`, {
                method: 'GET',
                headers: {
                    'X-API-Key': this.apiKey
                }
            });

            if (response.ok) {
                const data = await response.json();
                return data.registered_printers;
            } else {
                throw new Error(`Failed to get printers: ${response.status}`);
            }

        } catch (error) {
            console.error('❌ Failed to get printers:', error);
            throw error;
        }
    }

    /**
     * Test print to verify connection
     * @param {string} restaurantId - Restaurant to test (optional)
     * @returns {Promise} - Test result
     */
    async testPrint(restaurantId = null) {
        const testRestaurantId = restaurantId || this.restaurantId;
        
        try {
            console.log(`🧪 Sending test print to ${testRestaurantId}...`);
            
            const response = await fetch(`${this.cloudServerUrl}/test/${testRestaurantId}`, {
                method: 'POST',
                headers: {
                    'X-API-Key': this.apiKey
                }
            });

            const result = await response.json();

            if (response.ok && result.success) {
                console.log('✅ Test print successful');
                return result;
            } else {
                throw new Error(result.message || 'Test print failed');
            }

        } catch (error) {
            console.error('❌ Test print failed:', error);
            throw error;
        }
    }

    /**
     * Helper function for delays
     * @param {number} ms - Milliseconds to delay
     * @returns {Promise} - Delay promise
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Format receipt for printing
     * @param {Object} orderData - Order information
     * @returns {string} - Formatted receipt text
     */
    formatReceipt(orderData) {
        const now = new Date();
        const dateStr = now.toLocaleDateString('en-GB');
        const timeStr = now.toLocaleTimeString('en-GB');
        
        let receipt = `
================================
    HK SAVOR SPOON RESTAURANT
    香港美味勺子餐廳
================================
Date: ${dateStr}
Time: ${timeStr}
Order #: ${orderData.orderId || 'N/A'}
Table: ${orderData.table || 'N/A'}

Items:
`;

        // Add items
        if (orderData.items && orderData.items.length > 0) {
            orderData.items.forEach(item => {
                const price = parseFloat(item.price || 0).toFixed(2);
                const qty = item.quantity || 1;
                const total = (qty * parseFloat(item.price || 0)).toFixed(2);
                
                receipt += `- ${item.name}`;
                if (qty > 1) {
                    receipt += ` x${qty}`;
                }
                receipt += `    $${total}\n`;
            });
        }

        // Add totals
        const subtotal = parseFloat(orderData.subtotal || 0).toFixed(2);
        const tax = parseFloat(orderData.tax || 0).toFixed(2);
        const total = parseFloat(orderData.total || 0).toFixed(2);

        receipt += `
--------------------------------
Subtotal:            $${subtotal}`;
        
        if (parseFloat(tax) > 0) {
            receipt += `
Tax:                 $${tax}`;
        }
        
        receipt += `
Total:               $${total}

Payment: ${orderData.paymentMethod || 'Cash'}

Thank you for dining with us!
謝謝光臨！
================================
`;

        return receipt;
    }
}

// Example usage and integration functions
class SavorSpoonPrintIntegration {
    constructor() {
        // Initialize cloud print client
        this.printer = new SavorSpoonCloudPrint({
            cloudServerUrl: 'http://YOUR_CLOUD_SERVER_IP:8080', // Update this!
            restaurantId: 'hk-savor-spoon-main',
            apiKey: 'hksavorspoon-secure-print-key-2025'
        });
        
        // Check server status on load
        this.initializeConnection();
    }

    async initializeConnection() {
        try {
            await this.printer.checkServerStatus();
            console.log('✅ Cloud print service ready');
            
            // Optional: Show status indicator on website
            this.updatePrintStatus('online');
            
        } catch (error) {
            console.error('❌ Cloud print service unavailable:', error);
            this.updatePrintStatus('offline');
        }
    }

    /**
     * Print order receipt
     * @param {Object} orderData - Complete order information
     */
    async printOrder(orderData) {
        try {
            // Show loading indicator
            this.showPrintStatus('printing');
            
            // Format receipt
            const receiptText = this.printer.formatReceipt(orderData);
            
            // Print with retry
            const result = await this.printer.printWithRetry(receiptText, {
                orderId: orderData.orderId,
                table: orderData.table
            });
            
            // Show success
            this.showPrintStatus('success');
            
            // Optional: Show success message to user
            this.showMessage('Receipt printed successfully!', 'success');
            
            return result;
            
        } catch (error) {
            console.error('Print order failed:', error);
            
            // Show error status
            this.showPrintStatus('error');
            
            // Show error message to user
            this.showMessage(`Print failed: ${error.message}`, 'error');
            
            throw error;
        }
    }

    /**
     * Update print status indicator on website
     * @param {string} status - 'online', 'offline', 'printing', 'success', 'error'
     */
    updatePrintStatus(status) {
        const statusElement = document.getElementById('print-status');
        if (statusElement) {
            statusElement.className = `print-status ${status}`;
            
            const messages = {
                online: '🖨️ Printer Ready',
                offline: '❌ Printer Offline',
                printing: '🔄 Printing...',
                success: '✅ Print Success',
                error: '❌ Print Error'
            };
            
            statusElement.textContent = messages[status] || '❓ Unknown';
        }
    }

    showPrintStatus(status) {
        this.updatePrintStatus(status);
        
        // Clear success/error status after 3 seconds
        if (status === 'success' || status === 'error') {
            setTimeout(() => {
                this.updatePrintStatus('online');
            }, 3000);
        }
    }

    /**
     * Show message to user
     * @param {string} message - Message text
     * @param {string} type - 'success', 'error', 'info'
     */
    showMessage(message, type = 'info') {
        // Create or update message element
        let messageElement = document.getElementById('print-message');
        if (!messageElement) {
            messageElement = document.createElement('div');
            messageElement.id = 'print-message';
            messageElement.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 15px;
                border-radius: 5px;
                color: white;
                font-weight: bold;
                z-index: 1000;
                max-width: 300px;
            `;
            document.body.appendChild(messageElement);
        }
        
        // Set message and style
        messageElement.textContent = message;
        messageElement.className = `print-message ${type}`;
        
        const colors = {
            success: '#4CAF50',
            error: '#f44336',
            info: '#2196F3'
        };
        
        messageElement.style.backgroundColor = colors[type] || colors.info;
        messageElement.style.display = 'block';
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            messageElement.style.display = 'none';
        }, 5000);
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Create global print integration instance
    window.savorSpoonPrint = new SavorSpoonPrintIntegration();
    
    console.log('🚀 HK Savor Spoon cloud print integration loaded');
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { SavorSpoonCloudPrint, SavorSpoonPrintIntegration };
}