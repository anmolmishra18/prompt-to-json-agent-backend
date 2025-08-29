#!/usr/bin/env python3
"""Allow running the app as a module: python -m app"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)