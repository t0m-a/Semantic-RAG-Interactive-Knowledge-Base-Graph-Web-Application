@echo off
echo ============================================================================
echo  Purging Legacy Private Database (archive_knowledge.db) ^& Model Files...
echo ============================================================================
cd /d "%~dp0"

if exist "archive_knowledge.db" (
    del /f /q "archive_knowledge.db"
    echo  [OK] Deleted legacy archive_knowledge.db
)
if exist "archive_knowledge.db-wal" del /f /q "archive_knowledge.db-wal"
if exist "archive_knowledge.db-shm" del /f /q "archive_knowledge.db-shm"
if exist "semantic_lsa_model.pkl" (
    del /f /q "semantic_lsa_model.pkl"
    echo  [OK] Deleted legacy semantic_lsa_model.pkl
)
if exist "data\knowledge_base.db" (
    del /f /q "data\knowledge_base.db"
    echo  [OK] Reset data\knowledge_base.db for clean schema initialization
)
if exist "data\knowledge_base.db-wal" del /f /q "data\knowledge_base.db-wal"
if exist "data\knowledge_base.db-shm" del /f /q "data\knowledge_base.db-shm"
if exist "data\semantic_lsa_model.pkl" del /f /q "data\semantic_lsa_model.pkl"

echo.
echo ============================================================================
echo  Initializing Clean Database with Fabricated Placeholder Data...
echo ============================================================================
if exist "%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe" (
    "%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe" init_db.py --reset --seed-examples
) else (
    python init_db.py --reset --seed-examples
)

echo.
echo ============================================================================
echo  Done! Legacy private database purged and placeholder data initialized.
echo ============================================================================
pause
