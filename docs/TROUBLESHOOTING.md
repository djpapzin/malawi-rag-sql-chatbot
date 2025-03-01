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

If you encounter the following error:
```json
{
  "error": "Rate limit exceeded. Please wait 60 seconds before making new requests."
}
```

This means you have made too many requests in a short period. Wait for 60 seconds before making new requests.

## Worker Timeout Issues

If you encounter worker timeout errors in the server logs like:
```
[2025-03-01 17:27:58 +0200] [4111263] [CRITICAL] WORKER TIMEOUT (pid:4111265)
```

This indicates that a worker process took too long to process a request and was terminated. This can happen with complex queries that require extensive processing.

### Solution:

1. Increase the worker timeout in the `start_server.sh` script:
   ```bash
   # Edit the start_server.sh file
   # Change the timeout parameter
   nohup gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:5000 --timeout 120 --access-logfile server_access.log --error-logfile server_error.log --log-level info > nohup.out 2>&1 &
   ```

2. Increase the client-side timeout in test scripts:
   ```python
   # In test_specific_queries.py or other test files
   # Change the timeout parameter in requests.post calls
   response = requests.post(url, json={"message": query}, timeout=30)
   ```

3. Restart the server after making these changes:
   ```bash
   ./start_server.sh
   ```

## Python Code in Responses

If you see Python code or code blocks in the API responses:

### Solution:

The response cleaning function in `app/database/langchain_sql.py` may need enhancement. Update the `_clean_llm_response` method with more comprehensive regex patterns to remove:

1. Code blocks (```python ... ```)
2. Import statements (import ...)
3. Function definitions (def ...)
4. Print statements (print(...))
5. Return statements (return ...)

After updating the code, restart the server for changes to take effect.
