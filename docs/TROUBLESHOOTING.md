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
source /home/dj/miniconda/etc/profile.d/conda.sh
conda activate malawi-rag-sql-chatbot
python -m uvicorn app.main:app --reload --host localhost --port 8000
```

### Restart the server
```bash
# Kill any existing processes
pkill -f "gunicorn app.main:app"

# Start the server again
cd /home/dj/malawi-rag-sql-chatbot
./start_server.sh
```

## Syntax Errors in Code
If you encounter a syntax error like:
```
SyntaxError: invalid syntax
```

1. Identify the file with the error from the logs
2. Fix the syntax error
3. Restart the server using `./start_server.sh`

## Port Already in Use
If you see an error like:
```
[Errno 98] Address already in use
```

```bash
# Find what's using port 5000
sudo lsof -i :5000

# Kill the process
sudo kill <PID>

# Start the server again
./start_server.sh
```

## Connection Reset Errors
```bash
# Check server status:
ps -ef | grep gunicorn | grep -v grep

# Restart server:
pkill -f "gunicorn app.main:app"
cd /home/dj/malawi-rag-sql-chatbot
./start_server.sh
```

## Rate Limiting
```json
{
  "error": "Rate limit exceeded",
  "retry_after": 60
}
```
Wait 60 seconds before making new requests
