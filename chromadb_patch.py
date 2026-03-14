"""
Patches sqlite3 with pysqlite3 to meet ChromaDB's minimum SQLite version requirement.
This is needed in Docker containers where the system SQLite3 may be too old.
Import this module BEFORE any ChromaDB imports.
"""
try:
    import pysqlite3
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    # pysqlite3 not installed — assume the system sqlite3 is recent enough
    pass
