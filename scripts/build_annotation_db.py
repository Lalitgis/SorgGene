"""
SorghumPost - Build Annotation Database
=========================================
Parses Sorghumbase GFF3 annotation file(s) into a SQLite database of genes.

Each entry in GFF3_FILES is one sorghum genotype/assembly. Run this again
after adding more genotypes to GFF3_FILES to extend the database (used by
the Cross-Genotype Comparison tab).

Usage:
    python scripts/build_annotation_db.py

Input:
    data/<genotype>.gff3(.gz)   -- see GFF3_FILES below

Output:
    database/annotation.db
"""

import sqlite3
import os
import re
import gzip

# ── Source files ──────────────────────────────────────────────
# key   = short genotype label used throughout the app
# value = (path to gff3 or gff3.gz, human-readable assembly name)
GFF3_FILES = {
    "BTx623": (
        os.path.join("data", "Sorghum_bicolor.Sorghum_bicolor_NCBIv3.gff3.gz"),
        "Sorghum_bicolor_NCBIv3",
    ),
    "Tx2783": (
        os.path.join("data", "Sorghum_tx2783.gff3.gz"),
        "Sorghum_bicolor-Tx2783-Reference-CSHL-USDA-1.0",
    ),
    "Rio": (
        os.path.join("data", "Sorghum_rio.gff3.gz"),
        "JGI-v2.0",
    ),
}

DB_PATH = os.path.join("database", "annotation.db")


def open_maybe_gz(path):
    if path.endswith(".gz"):
        return gzip.open(path, "rt", encoding="utf-8")
    return open(path, "r", encoding="utf-8")


def parse_attributes(attr_string):
    """Extract ID and biotype from a GFF3 attributes column."""
    gene_id = ""
    biotype = ""

    id_match = re.search(r"ID=([^;]+)", attr_string)
    if id_match:
        gene_id = id_match.group(1).strip()

    biotype_match = re.search(r"biotype=([^;]+)", attr_string)
    if biotype_match:
        biotype = biotype_match.group(1).strip()

    return gene_id, biotype


def create_database(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS genes (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            gene_id     TEXT,
            genotype    TEXT,
            assembly    TEXT,
            chrom       TEXT,
            start       INTEGER,
            end         INTEGER,
            strand      TEXT,
            biotype     TEXT
        )
    """)
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_genotype_chrom_start_end "
        "ON genes (genotype, chrom, start, end)"
    )
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_gene_id ON genes (gene_id)")
    conn.commit()
    print("Database and table ready.")


def parse_gff3(filepath, genotype, assembly, conn):
    cursor = conn.cursor()
    count = 0
    batch = []
    batch_size = 2000

    print(f"\nProcessing {genotype} ({assembly}) -- {filepath}")

    with open_maybe_gz(filepath) as f:
        for line in f:
            if line.startswith("#"):
                continue

            parts = line.rstrip("\n").split("\t")
            if len(parts) < 9:
                continue

            chrom, source, feature, start, end, score, strand, phase, attributes = parts

            if feature != "gene":
                continue

            gene_id, biotype = parse_attributes(attributes)
            if not gene_id:
                continue

            batch.append((
                gene_id,
                genotype,
                assembly,
                chrom,
                int(start),
                int(end),
                strand,
                biotype,
            ))
            count += 1

            if len(batch) >= batch_size:
                cursor.executemany("""
                    INSERT INTO genes
                    (gene_id, genotype, assembly, chrom, start, end, strand, biotype)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, batch)
                conn.commit()
                batch = []
                print(f"  {count} genes processed...", end="\r")

    if batch:
        cursor.executemany("""
            INSERT INTO genes
            (gene_id, genotype, assembly, chrom, start, end, strand, biotype)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, batch)
        conn.commit()

    print(f"  Done -- {genotype}: {count} genes inserted.")
    return count


def main():
    print("=" * 55)
    print("SorghumPost -- Building Annotation Database")
    print("=" * 55)

    for genotype, (path, assembly) in GFF3_FILES.items():
        if not os.path.exists(path):
            print(f"File not found for {genotype}: {path}")
            print("  Please add it under data/ and update GFF3_FILES.")
            return

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Removed old database: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    create_database(conn)

    total = 0
    for genotype, (path, assembly) in GFF3_FILES.items():
        total += parse_gff3(path, genotype, assembly, conn)

    conn.close()

    size_mb = os.path.getsize(DB_PATH) / (1024 * 1024)
    print("\n" + "=" * 55)
    print(f"Done. Total genes: {total:,}")
    print(f"Database size: {size_mb:.1f} MB")
    print(f"Saved to: {DB_PATH}")
    print("=" * 55)


if __name__ == "__main__":
    main()
