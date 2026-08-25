"""
SorgGene Setup Checker
==========================
Run this before starting the app to verify the database is present.
    python setup_data.py
"""

import os
import sqlite3

DB_PATH = os.path.join("database", "annotation.db")
EXPECTED_GENOTYPES = ["BTx623", "Tx2783", "Rio"]


def check():
    print("\n" + "=" * 50)
    print("SorgGene - Setup Check")
    print("=" * 50)

    if not os.path.exists(DB_PATH):
        print(f"❌ annotation.db not found at {DB_PATH}")
        print("   Run: python scripts/build_annotation_db.py")
        print("   (See README for how to get the source GFF3 files.)")
        print("=" * 50 + "\n")
        return

    size_mb = os.path.getsize(DB_PATH) / (1024 * 1024)
    print(f"✅ annotation.db found ({size_mb:.1f} MB)")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT genotype, COUNT(*) FROM genes GROUP BY genotype ORDER BY genotype")
    rows = cursor.fetchall()
    conn.close()

    found_genotypes = {g for g, _ in rows}
    for genotype, count in rows:
        print(f"   - {genotype}: {count:,} genes")

    missing = [g for g in EXPECTED_GENOTYPES if g not in found_genotypes]
    print("=" * 50)
    if not missing:
        print("✅ All expected genotypes present. Run: streamlit run app.py")
    else:
        print(f"⚠️  Missing genotype(s): {missing}")
        print("   Cross-Genotype Comparison tab will only show loaded genotypes.")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    check()
