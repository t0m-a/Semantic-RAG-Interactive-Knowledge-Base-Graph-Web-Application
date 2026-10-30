#!/usr/bin/env python3
"""
Database Initialization, Reset & Bulk Import Utility
====================================================
Makes the application 100% independent of any previous folder location, removes legacy
database/model files, and prepares a clean database at `./data/knowledge_base.db` ready
for new data import.

Usage:
  python init_db.py                         # Initialize clean schema & remove legacy files
  python init_db.py --reset                 # Clear all records in ./data/knowledge_base.db
  python init_db.py --seed-examples         # Seed synthetic example data (ACME, GLBX, INIT)
  python init_db.py --import-dir /path/docs # Copy & ingest files from a directory
"""

import os
import sys
import shutil
import pathlib
import argparse

APP_ROOT = pathlib.Path(__file__).resolve().parent
WEBAPP_DIR = APP_ROOT / 'webapp'
sys.path.insert(0, str(WEBAPP_DIR))

import rag_engine  # noqa: E402


def seed_example_data(search_engine: rag_engine.HybridSemanticEngine):
    """Seeds synthetic example organizations, documents, emails, and CMDB items for demo purposes."""
    migrations_dir = APP_ROOT / 'cloudflare-worker' / 'migrations'
    conn = rag_engine.get_db()
    cur = conn.cursor()

    sql_files = [
        '0002_clients_01.sql',
        '0003_files_01.sql',
        '0004_emails_01.sql',
        '0005_cmdb_01.sql',
        '0006_fts_populate.sql',
    ]
    for fname in sql_files:
        fpath = migrations_dir / fname
        if fpath.exists():
            sql_text = fpath.read_text(encoding='utf-8').strip()
            if 'INSERT' in sql_text.upper():
                cur.executescript(sql_text)

    conn.commit()
    conn.close()
    search_engine.build_or_load_embeddings(force_rebuild=True)
    print("[init_db] Seeded synthetic example dataset (ACME, GLBX, INIT, WAYN, STRK) and built embeddings.")


def import_directory(source_dir: pathlib.Path, search_engine: rag_engine.HybridSemanticEngine):
    """Copies files from source_dir into ./data/ingest/ and runs incremental ingestion."""
    if not source_dir.exists() or not source_dir.is_dir():
        raise FileNotFoundError(f"Source directory not found: {source_dir}")

    rag_engine.INGEST_DIR.mkdir(parents=True, exist_ok=True)
    copied = 0
    for p in source_dir.rglob('*'):
        if not p.is_file() or p.name.startswith('.'):
            continue
        rel = p.relative_to(source_dir)
        dest = rag_engine.INGEST_DIR / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dest)
        copied += 1

    print(f"[init_db] Copied {copied} files into {rag_engine.INGEST_DIR}. Scanning & indexing...")
    res = rag_engine.scan_for_new_or_modified_files(search_engine, trigger_type='cli_import')
    search_engine.build_or_load_embeddings(force_rebuild=True)
    print(f"[init_db] Import complete: {res['details']}")


def main():
    parser = argparse.ArgumentParser(description="Initialize, reset, or import data into the Knowledge Base")
    parser.add_argument("--reset", action="store_true", help="Clear all existing records in ./data/knowledge_base.db")
    parser.add_argument("--seed-examples", action="store_true", help="Populate synthetic example data (ACME, GLBX, INIT)")
    parser.add_argument("--import-dir", type=str, help="Import and index all files from the specified folder path")
    args = parser.parse_args()

    # 1. Remove any legacy root-level database/model files and initialize clean schema
    rag_engine.init_webapp_schema()
    engine = rag_engine.HybridSemanticEngine()

    if args.reset:
        rag_engine.clear_all_data(engine)
        print(f"[init_db] Cleared all data in {rag_engine.DB_PATH}. Database is empty and ready for new imports.")

    if args.seed_examples:
        seed_example_data(engine)

    if args.import_dir:
        import_directory(pathlib.Path(args.import_dir).resolve(), engine)

    if not args.reset and not args.seed_examples and not args.import_dir:
        res = rag_engine.scan_for_new_or_modified_files(engine, trigger_type='cli_init')
        engine.build_or_load_embeddings(force_rebuild=False)
        print(f"[init_db] Portable database initialized at: {rag_engine.DB_PATH}")
        print(f"[init_db] Auto-ingest folder ready at     : {rag_engine.INGEST_DIR}")
        print(f"[init_db] Web uploads folder ready at     : {rag_engine.UPLOADS_DIR}")
        print(f"[init_db] Status                          : {res['details']}")


if __name__ == '__main__':
    main()
