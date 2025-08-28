# Ngrok Setup for HK Savor Spoon Print Server

## What is Ngrok?
Ngrok creates a secure tunnel from the internet to your local server, bypassing router configuration and ISP blocking.

## Installation Steps:

### 1. Download Ngrok
1. Go to: https://ngrok.com/download
2. Download Windows version
3. Extract to: C:\ngrok\

### 2. Create Account (Free)
1. Sign up at: https://dashboard.ngrok.com/signup
2. Get your auth token from dashboard

### 3. Setup Ngrok
```powershell
# Navigate to ngrok folder
cd C:\ngrok\

# Authenticate (replace YOUR_TOKEN with actual token)
.\ngrok.exe authtoken YOUR_TOKEN

# Start tunnel to your print server
.\ngrok.exe http 8080
```

### 4. Get Public URL
After running ngrok, you'll see output like:
```
Forwarding    https://abc123.ngrok.io -> http://localhost:8080
Forwarding    http://abc123.ngrok.io -> http://localhost:8080
```

### 5. Update Website
Change your HK Savor Spoon website setting:
- From: `http://58.153.166.26:8080`
- To: `https://abc123.ngrok.io` (use your actual ngrok URL)

## Advantages of Ngrok:
✅ No router configuration needed
✅ Works behind any firewall/NAT
✅ Provides HTTPS automatically
✅ Free tier available
✅ Bypasses ISP port blocking

## Usage Commands:
```powershell
# Start tunnel for print server
ngrok http 8080

# Start tunnel with custom subdomain (paid feature)
ngrok http 8080 --subdomain=hksavorspoon

# Start tunnel with basic auth
ngrok http 8080 --basic-auth="username:password"
```

## Alternative: Cloudflare Tunnel
If you prefer not to use ngrok:
1. Install cloudflared
2. Run: `cloudflared tunnel --url http://localhost:8080`
3. Get the public URL provided

## Test Command After Setup:
```powershell
# Test with your ngrok URL
curl https://your-ngrok-url.ngrok.io/status
```
