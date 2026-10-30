#!/usr/bin/env python3
"""
Enterprise Semantic RAG Knowledge Base - CLI Query & Inspection Tool
Database: ./data/knowledge_base.db

Usage Examples:
  python search_kb.py --stats
  python search_kb.py --themes
  python search_kb.py --clients
  python search_kb.py --client ACME
  python search_kb.py --query "Veeam retention"
  python search_kb.py --query "Acronis" --theme "Backup & Disaster Recovery (BCDR)"
  python search_kb.py --query "BitLocker" --type document
  python search_kb.py --sops
  python search_kb.py --scripts
"""

import os
import sys
import json
import sqlite3
import pathlib
import argparse

APP_ROOT = pathlib.Path(__file__).resolve().parent
DB_PATH = pathlib.Path(os.environ.get('KB_DB_PATH', str(APP_ROOT / 'data' / 'knowledge_base.db')))


def get_conn():
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Knowledge base database not found at {DB_PATH}.\n"
            f"Run `python init_db.py` first to initialize a clean database (or `python init_db.py --seed-examples`)."
        )
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    existing_client_cols = [r[1] for r in cur.execute("PRAGMA table_info(clients)").fetchall()]
    if existing_client_cols and ('doc_id' not in existing_client_cols):
        mig_dir = APP_ROOT / 'cloudflare-worker' / 'migrations'
        for mig_name in ('0001_schema.sql', '0002_clients_01.sql', '0003_files_01.sql', '0004_emails_01.sql', '0005_cmdb_01.sql', '0006_fts_populate.sql'):
            mig_path = mig_dir / mig_name
            if mig_path.exists():
                cur.executescript(mig_path.read_text(encoding='utf-8'))
        conn.commit()
    return conn


def print_stats(conn):
    cur = conn.cursor()
    print("=" * 78)
    print(" SEMANTIC RAG KNOWLEDGE BASE - SUMMARY")
    print("=" * 78)
    for row in cur.execute("SELECT status, COUNT(*) as cnt, ROUND(COALESCE(SUM(size_bytes), 0)/1048576.0, 2) as mb FROM files GROUP BY status ORDER BY cnt DESC"):
        print(f"  File Status [{row['status']:15s}] : {row['cnt']:6d} files ({row['mb']:8.2f} MB)")

    total_emails = cur.execute("SELECT COUNT(*) FROM emails").fetchone()[0]
    total_clients = cur.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
    total_cmdb = cur.execute("SELECT COUNT(*) FROM cmdb_records").fetchone()[0]
    total_fts = cur.execute("SELECT COUNT(*) FROM kb_fts").fetchone()[0]
    print(f"  Total Indexed Emails          : {total_emails:6d}")
    print(f"  Total Client Organizations    : {total_clients:6d}")
    print(f"  Total CMDB Records            : {total_cmdb:6d}")
    print(f"  Total Full-Text Search Docs   : {total_fts:6d}")

    print("\n--- Primary Thematic Distribution ---")
    for row in cur.execute("""
        SELECT primary_theme, COUNT(*) as cnt
        FROM files
        WHERE status IN ('primary', 'archive_entry')
        GROUP BY primary_theme
        ORDER BY cnt DESC
    """):
        print(f"  {row['primary_theme']:50s} : {row['cnt']:5d} items")


def print_themes(conn):
    cur = conn.cursor()
    print("=" * 78)
    print(" THEMATIC TAXONOMY & SUB-THEMES BREAKDOWN")
    print("=" * 78)
    theme_map = {}
    for row in cur.execute("SELECT primary_theme, sub_themes FROM files WHERE status IN ('primary', 'archive_entry')"):
        pt = row['primary_theme']
        theme_map.setdefault(pt, {'count': 0, 'sub': {}})
        theme_map[pt]['count'] += 1
        try:
            subs = json.loads(row['sub_themes'] or '[]')
        except Exception:
            subs = []
        for s in subs:
            theme_map[pt]['sub'][s] = theme_map[pt]['sub'].get(s, 0) + 1

    for pt, data in sorted(theme_map.items(), key=lambda x: x[1]['count'], reverse=True):
        print(f"\n[{pt}] ({data['count']} total items)")
        for s, cnt in sorted(data['sub'].items(), key=lambda x: x[1], reverse=True):
            print(f"    - {s:52s}: {cnt:4d}")


def print_clients(conn, limit=100):
    cur = conn.cursor()
    print("=" * 95)
    print(f" {'CODE':12s} | {'ORGANIZATION NAME':42s} | {'FILES':5s} | {'CFGS':5s} | {'BKPS':5s} | {'SVRS':4s}")
    print("=" * 95)
    for row in cur.execute("""
        SELECT client_code, organization_name, file_count, cmdb_config_count, cmdb_backup_count, cmdb_server_count
        FROM clients
        WHERE file_count > 0 OR cmdb_config_count > 0
        ORDER BY file_count DESC, cmdb_config_count DESC
        LIMIT ?
    """, (limit,)):
        print(f" {row['client_code']:12s} | {row['organization_name'][:42]:42s} | {row['file_count']:5d} | {row['cmdb_config_count']:5d} | {row['cmdb_backup_count']:5d} | {row['cmdb_server_count']:4d}")


def print_client_profile(conn, code):
    cur = conn.cursor()
    c = cur.execute("SELECT * FROM clients WHERE UPPER(client_code) = UPPER(?) OR organization_name LIKE ?", (code, f"%{code}%")).fetchone()
    if not c:
        print(f"No client found matching '{code}'.")
        return
    cc = c['client_code']
    print("=" * 80)
    print(f" CLIENT PROFILE: [{cc}] {c['organization_name']}")
    print(f" Status: {c['org_status']} | Type: {c['org_type']} | Documentation ID: {c['doc_id']}")
    print(f" Files: {c['file_count']} | CMDB Configs: {c['cmdb_config_count']} | Contacts: {c['cmdb_contact_count']} | Backups: {c['cmdb_backup_count']} | Servers: {c['cmdb_server_count']}")
    print("=" * 80)

    print("\n--- Key Files & Documentation ---")
    for f in cur.execute("""
        SELECT rel_path, primary_theme, title_or_subject, summary_preview
        FROM files
        WHERE client_code = ? AND status = 'primary'
        ORDER BY extension, filename
        LIMIT 40
    """, (cc,)):
        print(f"  * [{f['primary_theme']}] {f['rel_path']}")
        if f['title_or_subject'] and f['title_or_subject'] not in f['rel_path']:
            print(f"      Subject: {f['title_or_subject']}")

    print("\n--- Key CMDB Records (Servers, Firewalls, AD, Backups) ---")
    for r in cur.execute("""
        SELECT source_table, item_name, item_type, status_or_location
        FROM cmdb_records
        WHERE client_code = ?
        LIMIT 30
    """, (cc,)):
        print(f"  * [{r['source_table']:18s}] {r['item_name']:35s} ({r['item_type']}) {r['status_or_location']}")


def search_fts(conn, query, theme=None, source_type=None, client=None, limit=25):
    cur = conn.cursor()
    sql = """
        SELECT source_type, ref_id, rel_path, title, primary_theme, sub_themes, client_code, organization_name,
               snippet(kb_fts, 8, '«', '»', ' ... ', 24) as snip
        FROM kb_fts
        WHERE kb_fts MATCH ?
    """
    params = [query]
    if theme:
        sql += " AND primary_theme LIKE ?"
        params.append(f"%{theme}%")
    if source_type:
        sql += " AND source_type = ?"
        params.append(source_type)
    if client:
        sql += " AND (UPPER(client_code) = UPPER(?) OR organization_name LIKE ?)"
        params.extend([client, f"%{client}%"])
    sql += " ORDER BY rank LIMIT ?"
    params.append(limit)

    rows = cur.execute(sql, params).fetchall()
    print(f"Found {len(rows)} results for '{query}':")
    print("-" * 80)
    for i, r in enumerate(rows, 1):
        client_tag = f" [{r['client_code']} - {r['organization_name']}]" if r['client_code'] else ""
        print(f"{i:2d}. [{r['source_type'].upper()}] {r['title']}{client_tag}")
        print(f"    Path : {r['rel_path']}")
        print(f"    Theme: {r['primary_theme']} -> {r['sub_themes']}")
        print(f"    Match: {r['snip']}\n")


def main():
    parser = argparse.ArgumentParser(description="Search the Semantic RAG Knowledge Base")
    parser.add_argument("--stats", action="store_true", help="Show overall knowledge base statistics")
    parser.add_argument("--themes", action="store_true", help="Show thematic taxonomy and sub-theme counts")
    parser.add_argument("--clients", action="store_true", help="List client organizations and counts")
    parser.add_argument("--client", type=str, help="Show detailed profile for a client code or name")
    parser.add_argument("--query", "-q", type=str, help="Full-text search query (FTS5 syntax supported)")
    parser.add_argument("--theme", type=str, help="Filter search by thematic domain")
    parser.add_argument("--type", type=str, choices=['document', 'email', 'script', 'spreadsheet', 'cmdb', 'archive_note'], help="Filter search by source type")
    parser.add_argument("--sops", action="store_true", help="List all SOPs, tutorials, and guides")
    parser.add_argument("--scripts", action="store_true", help="List all technical scripts and automation tools")
    parser.add_argument("--limit", type=int, default=25, help="Max results to display")

    args = parser.parse_args()
    conn = get_conn()

    if args.stats:
        print_stats(conn)
    elif args.themes:
        print_themes(conn)
    elif args.clients:
        print_clients(conn, args.limit)
    elif args.client:
        print_client_profile(conn, args.client)
    elif args.sops:
        cur = conn.cursor()
        rows = cur.execute("""
            SELECT rel_path, filename, extension, primary_theme, sub_themes, summary_preview
            FROM files
            WHERE status IN ('primary', 'archive_entry')
              AND (sub_themes LIKE '%SOP%' OR rel_path LIKE '%SOP%' OR rel_path LIKE '%Runbook%' OR rel_path LIKE '%Onboarding%')
            ORDER BY rel_path
        """).fetchall()
        print(f"=== SOPs, Tutorials & Operational Guides ({len(rows)}) ===")
        for r in rows:
            print(f"  * {r['rel_path']} ({r['primary_theme']})")
    elif args.scripts:
        cur = conn.cursor()
        rows = cur.execute("""
            SELECT rel_path, filename, extension, primary_theme, sub_themes, summary_preview
            FROM files
            WHERE status IN ('primary', 'archive_entry')
              AND extension IN ('.ps1', '.sh', '.bat', '.cmd', '.py')
            ORDER BY extension, filename
        """).fetchall()
        print(f"=== Technical Scripts & Automation Tools ({len(rows)}) ===")
        for r in rows:
            print(f"  * [{r['extension']:4s}] {r['rel_path']:65s} | {r['summary_preview'][:70]}")
    elif args.query:
        search_fts(conn, args.query, theme=args.theme, source_type=args.type, client=args.client, limit=args.limit)
    else:
        print_stats(conn)


if __name__ == '__main__':
    main()
