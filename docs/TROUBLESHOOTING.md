# Common Errors & Solutions

## Server Not Responding

### Check if the server is running
```bash
# Check running gunicorn processes
ps -ef | grep gunicorn | grep -v grep

# If no processes are found, the server is not running
```

### Server not starting or crashing
```bash
# Check server error logs
tail -n 100 server_error.log

# Check startup logs
cat nohup.out

# Try starting in debug mode (this will show immediate errors)
cd /home/dj/malawi-rag-sql-chatbot
source ~/miniconda/etc/profile.d/conda.sh
conda activate malawi-rag-sql-chatbot
python -m uvicorn app.main:app --reload --host localhost --port 8000
```

### Restart the server
```bash
# Kill any existing processes
pkill -f "gunicorn app.main:app"

# Start the server again
cd /home/dj/malawi-rag-sql-chatbot
./start_production.sh
```

## Static Files Not Loading

If static files (CSS, JS) are not loading correctly:

1. Check browser console for errors (404, CORS issues)

2. Verify that the files exist in the correct location:
```bash
# Check if the CSS file exists
ls -la frontend/static/css/loading.css

# Check if the JS file exists
ls -la frontend/static/js/main.js
```

3. Verify the files are accessible:
```bash
# Test if CSS file is accessible
curl -s -I https://dziwani.kwantu.support/static/css/loading.css | head

# Test if JS file is accessible
curl -s -I https://dziwani.kwantu.support/static/js/main.js | head
```

4. Check Nginx configuration:
```bash
# Verify that Nginx is properly configured
sudo nginx -t

# Check the configuration
sudo cat /etc/nginx/conf.d/dziwani.kwantu.support.conf
```

5. Ensure FastAPI is correctly serving static files:
```bash
# In app/main.py, the static files should be mounted correctly
# Example:
# app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
```

## API Connection Issues

If the frontend is not connecting to the API:

1. Check the main.js file to ensure it's using relative URLs:
```bash
# View the main.js file
cat frontend/static/js/main.js | grep API_BASE_URL
```

2. Correct value should be:
```javascript
const API_BASE_URL = ''; // Empty string for relative URLs
```

3. Update if needed:
```bash
# Edit the file and replace the API_BASE_URL with ''
# Then restart the server
./start_production.sh
```

## Syntax Errors in Code
If you encounter a syntax error like:
```