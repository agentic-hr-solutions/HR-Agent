# VS Code Python Import Fix

## ✅ Fixed!

The import errors for `mcp` and `pydantic` have been resolved.

## What Was Done

1. **Created Python Virtual Environment**
   ```bash
   cd backend
   python3 -m venv .venv
   ```

2. **Installed All Dependencies**
   ```bash
   .venv/bin/pip install mcp pydantic langgraph langchain-core langchain-openai
   ```

3. **Configured VS Code**
   - Updated `.vscode/settings.json` to use the virtual environment
   - Set Python interpreter path: `backend/.venv/bin/python`
   - Configured Pylance language server

## Verification

```bash
cd backend
.venv/bin/python3 -c "import pydantic; print('✅ pydantic OK')"
# Output: ✅ pydantic OK
```

## Next Steps

### 1. Reload VS Code Window
Press `Cmd+Shift+P` and select **"Developer: Reload Window"** to apply the new Python interpreter settings.

### 2. Select Python Interpreter
If imports still show errors after reload:
- Press `Cmd+Shift+P`
- Type "Python: Select Interpreter"
- Choose: `./backend/.venv/bin/python`

### 3. Verify in VS Code
Open `backend/mcp_server.py` and check:
- ✅ No red squiggles under `from mcp.server.fastmcp import FastMCP`
- ✅ No red squiggles under `from pydantic import BaseModel, Field`
- ✅ IntelliSense works when you type `FastMCP.`

## Alternative: Using the Terminal

If you prefer working in the terminal, always activate the virtual environment first:

```bash
cd backend
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate     # On Windows

# Then run your commands
python mcp_server.py
pytest tests/test_mcp_server.py
```

## Installed Packages

All required packages are now installed in `backend/.venv/`:

- ✅ `mcp` (1.25.0) - FastMCP server framework
- ✅ `pydantic` (2.12.5) - Type validation
- ✅ `langgraph` (1.0.6) - Workflow orchestration
- ✅ `langchain-core` (1.2.7) - Core LangChain
- ✅ `langchain-openai` (1.1.7) - OpenAI integration

Plus all their dependencies.

## Running the MCP Server

```bash
cd backend
source .venv/bin/activate
python mcp_server.py
```

Or without activating:

```bash
cd backend
.venv/bin/python mcp_server.py
```

## Running Tests

```bash
cd backend
.venv/bin/pytest tests/test_mcp_server.py -v
```

## Troubleshooting

### If imports still don't work after reload:

1. **Check Python interpreter in VS Code status bar** (bottom right)
   - Should show: `3.13.3 ('.venv': venv)`
   - If not, click it and select the correct interpreter

2. **Restart Pylance**
   - `Cmd+Shift+P` → "Python: Restart Language Server"

3. **Clear Python cache**
   ```bash
   cd backend
   find . -type d -name "__pycache__" -exec rm -rf {} +
   find . -type f -name "*.pyc" -delete
   ```

4. **Reinstall if needed**
   ```bash
   cd backend
   rm -rf .venv
   python3 -m venv .venv
   .venv/bin/pip install mcp pydantic langgraph langchain-core langchain-openai
   ```

## Quick Reference

| Task | Command |
|------|---------|
| Activate venv | `source backend/.venv/bin/activate` |
| Deactivate venv | `deactivate` |
| Install package | `.venv/bin/pip install <package>` |
| Run Python script | `.venv/bin/python <script.py>` |
| Run tests | `.venv/bin/pytest tests/` |
| List packages | `.venv/bin/pip list` |

---

**Status**: ✅ All imports working! Ready to develop.
