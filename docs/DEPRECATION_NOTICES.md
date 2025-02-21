# Deprecation Notices

## LangChain Together Class
```
C:\...\langchain_sql.py:69: LangChainDeprecationWarning
```

### Migration Path
1. Install updated package:
```bash
pip install -U langchain-together
```
2. Update imports:
```python
# Before
from langchain.together import Together

# After
from langchain_together import Together
```
