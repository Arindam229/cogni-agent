# Cognizance AI Agent Deployment Guide

This guide explains how to deploy the Python Agent and configure Nginx on your Ubuntu server.

## 1. Accessing the Server

Connect to your server via SSH:
```bash
ssh ubuntu@your-server-ip
```

## 2. Deploying the Agent

Navigate to your project directory and use the deployment script:

```bash
cd ~/cogni/Agent
chmod +x deploy.sh
./deploy.sh
```

This will pull the latest code, update dependencies, and restart the Agent process using PM2.

## 3. Configuring Nginx

To expose the Agent securely, you need to configure Nginx as a reverse proxy.

### Step 3.1: Open Nginx Configuration

The main configuration file is usually located at `/etc/nginx/sites-available/default`.
Open it with `nano` (or your preferred editor):

```bash
sudo nano /etc/nginx/sites-available/default
```

### Step 3.2: Add Location Block

Find the `server` block that handles HTTPS traffic (port 443).
Inside that block, add the following `location` directive to forward `/api/ai` requests to the Agent:

```nginx
    # -----------------------------------------------------
    # AI Agent Reverse Proxy
    # -----------------------------------------------------
    location /api/ai/ {
        # Rewrite the URL path: /api/ai/chat -> /api/v1/chat
        rewrite ^/api/ai/(.*) /api/v1/$1 break;

        # Forward usage to localhost:8000
        proxy_pass http://localhost:8000;

        # Standard headers for proxying
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
```

### Step 3.3: Verify and Reload

1.  **Test the configuration** for syntax errors:
    ```bash
    sudo nginx -t
    ```
    *If successful, you will see `syntax is ok` and `test is successful`.*

2.  **Reload Nginx** to apply changes:
    ```bash
    sudo systemctl reload nginx
    ```

## 4. Update Frontend Configuration

Now that Nginx is configured, update your production frontend to use the public URL.

1.  Edit `Hofond/src/Components/js/config.js` on your local machine or server.
2.  Set `CHATBOT_API_DOMAIN`:
    ```javascript
    export const CHATBOT_API_DOMAIN = 'https://cognizance.org.in/api/ai/';
    ```
3.  Rebuild the frontend:
    ```bash
    cd ~/cogni/Hofond
    npm run build
    ```

## Troubleshooting

- **Check Nginx Status**: `sudo systemctl status nginx`
- **View Nginx Error Logs**: `sudo tail -f /var/log/nginx/error.log`
- **Check PM2 Logs**: `pm2 logs cogni-agent`
