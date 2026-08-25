"""
SorghumPost - Gene Service
============================
Handles gene proximity queries against annotation.db.
Called by Tab 1 -- Gene Proximity Search.
"""

import sqlite3
import pandas as pd
import os
import re
import streamlit as st

DB_PATH = os.path.join("database", "annotation.db")


def normalize_chrom(chrom: str) -> str:
    """Normalize chromosome input to match database format.
    Sorghum chromosomes are stored as plain strings: '1'..'10', or
    scaffold names like 'super_101'. Strips any 'Chr'/'chr' prefix
    and surrounding whitespace.
    """
    chrom = chrom.strip()
    if chrom.lower().startswith("chr"):
        chrom = chrom[3:]
    return chrom.strip()


def _chrom_sort_key(chrom: str):
    """Sort '1'..'10' numerically first, then everything else alphabetically."""
    if chrom.isdigit():
        return (0, int(chrom), "")
    return (1, 0, chrom)


@st.cache_data
def get_nearby_genes(chrom: str, position: int, window_bp: int, genotype: str = "BTx623") -> pd.DataFrame:
    """
    Find all genes within a window around a marker position.

    Parameters:
        chrom    : Chromosome name e.g. '1' or 'Chr1'
        position : Marker position in base pairs
        window_bp: Window size in base pairs (e.g. 100000 for 100kb)
        genotype : Sorghum genotype/assembly label (e.g. 'BTx623')

    Returns:
        pandas DataFrame with nearby genes sorted by distance from marker
    """

    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(
            f"annotation.db not found at {DB_PATH}. "
            "Please run: python scripts/build_annotation_db.py"
        )

    chrom = normalize_chrom(chrom)
    start = max(0, position - window_bp)
    end = position + window_bp

    query = """
        SELECT
            gene_id,
            chrom,
            start,
            end,
            strand,
            biotype,
            genotype
        FROM genes
        WHERE genotype = ?
          AND chrom = ?
          AND start <= ?
          AND end >= ?
        ORDER BY start
    """

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn, params=(genotype, chrom, end, start))
    conn.close()

    if df.empty:
        return df

    def get_distance_and_status(row):
        if row["start"] <= position <= row["end"]:
            return 0, "Overlaps marker"
        else:
            dist = min(abs(position - row["start"]), abs(position - row["end"]))
            return dist, "Near marker"

    df[["distance_bp", "location"]] = df.apply(
        lambda row: pd.Series(get_distance_and_status(row)),
        axis=1
    )

    df = df.sort_values("distance_bp").reset_index(drop=True)

    df = df.rename(columns={
        "gene_id":     "Gene ID",
        "chrom":       "Chromosome",
        "start":       "Start (bp)",
        "end":         "End (bp)",
        "strand":      "Strand",
        "biotype":     "Biotype",
        "genotype":    "Genotype",
        "distance_bp": "Distance from Marker (bp)",
        "location":    "Location"
    })

    return df


@st.cache_data
def get_genes_in_region(chrom: str, start: int, end: int, genotype: str = "BTx623") -> pd.DataFrame:
    """
    Find all genes overlapping an explicit [start, end] region -- e.g. a
    GWAS significant interval pasted straight in, rather than a single
    point + symmetric window.

    Parameters:
        chrom, start, end : the region (start/end swapped automatically if reversed)
        genotype           : Sorghum genotype/assembly label (e.g. 'BTx623')

    Returns:
        pandas DataFrame with genes overlapping the region, sorted by position.
        'Location' marks each gene as fully contained in the region or only
        overlapping one of its boundaries.
    """

    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(
            f"annotation.db not found at {DB_PATH}. "
            "Please run: python scripts/build_annotation_db.py"
        )

    chrom = normalize_chrom(chrom)
    if start > end:
        start, end = end, start

    query = """
        SELECT
            gene_id,
            chrom,
            start,
            end,
            strand,
            biotype,
            genotype
        FROM genes
        WHERE genotype = ?
          AND chrom = ?
          AND start <= ?
          AND end >= ?
        ORDER BY start
    """

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn, params=(genotype, chrom, end, start))
    conn.close()

    if df.empty:
        return df

    def get_status(row):
        if row["start"] >= start and row["end"] <= end:
            return "Fully within region"
        return "Overlaps region boundary"

    df["location"] = df.apply(get_status, axis=1)
    df = df.sort_values("start").reset_index(drop=True)

    df = df.rename(columns={
        "gene_id":  "Gene ID",
        "chrom":    "Chromosome",
        "start":    "Start (bp)",
        "end":      "End (bp)",
        "strand":   "Strand",
        "biotype":  "Biotype",
        "genotype": "Genotype",
        "location": "Location",
    })

    return df


@st.cache_data
def get_chromosome_list(genotype: str = "BTx623") -> list:
    """Return list of chromosomes/scaffolds available for a given genotype,
    numeric chromosomes ('1'..'10') sorted first."""

    if not os.path.exists(DB_PATH):
        return []

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT DISTINCT chrom FROM genes WHERE genotype = ?",
        (genotype,)
    )
    chroms = [row[0] for row in cursor.fetchall()]
    conn.close()
    return sorted(chroms, key=_chrom_sort_key)


@st.cache_data
def get_nearby_genes_multi_genotype(chrom: str, position: int, window_bp: int, genotypes: list) -> pd.DataFrame:
    """
    Compare gene annotation in the same chromosome:window across several
    sorghum genotype assemblies. Since each genotype is an independently
    assembled genome, this is a same-coordinate comparison, not a true
    liftover -- see the caveat shown in the UI.
    """
    all_results = []
    for genotype in genotypes:
        df = get_nearby_genes(chrom, position, window_bp, genotype)
        if not df.empty:
            all_results.append(df)

    if not all_results:
        return pd.DataFrame()

    return pd.concat(all_results, ignore_index=True)


@st.cache_data
def get_summary_stats() -> dict:
    """High-level counts for the Dashboard tab."""
    if not os.path.exists(DB_PATH):
        return {}

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM genes")
    total_genes = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(DISTINCT genotype) FROM genes")
    total_genotypes = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(DISTINCT chrom) FROM genes WHERE genotype = 'BTx623' AND length(chrom) <= 2")
    total_chroms = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM genes WHERE genotype = 'BTx623' AND biotype = 'protein_coding'")
    protein_coding = cursor.fetchone()[0]
    conn.close()

    return {
        "total_genes": total_genes,
        "total_genotypes": total_genotypes,
        "total_chroms": total_chroms,
        "protein_coding_btx623": protein_coding,
    }


@st.cache_data
def get_genes_per_genotype() -> pd.DataFrame:
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT genotype AS Genotype, COUNT(*) AS Genes FROM genes GROUP BY genotype ORDER BY Genes DESC",
        conn
    )
    conn.close()
    return df


@st.cache_data
def get_biotype_breakdown(genotype: str = "BTx623") -> pd.DataFrame:
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT biotype AS Biotype, COUNT(*) AS Genes FROM genes WHERE genotype = ? GROUP BY biotype ORDER BY Genes DESC",
        conn, params=(genotype,)
    )
    conn.close()
    return df


@st.cache_data
def get_genes_per_chromosome(genotype: str = "BTx623") -> pd.DataFrame:
    """Gene counts for main numbered chromosomes only (scaffolds excluded)."""
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT chrom AS Chromosome, COUNT(*) AS Genes FROM genes "
        "WHERE genotype = ? AND length(chrom) <= 2 GROUP BY chrom",
        conn, params=(genotype,)
    )
    conn.close()
    if df.empty:
        return df
    df["_sort"] = df["Chromosome"].apply(lambda c: int(c) if c.isdigit() else 999)
    return df.sort_values("_sort").drop(columns="_sort").reset_index(drop=True)


@st.cache_data
def get_gene_density_along_chrom(genotype: str, chrom: str, bin_size: int = 1_000_000) -> pd.DataFrame:
    """Gene counts binned along one chromosome, for a density track chart."""
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT start FROM genes WHERE genotype = ? AND chrom = ?",
        conn, params=(genotype, normalize_chrom(chrom))
    )
    conn.close()
    if df.empty:
        return df
    df["bin"] = (df["start"] // bin_size) * bin_size
    counts = df.groupby("bin").size().reset_index(name="Genes")
    counts = counts.rename(columns={"bin": "Bin Start (bp)"})
    return counts.sort_values("Bin Start (bp)").reset_index(drop=True)


@st.cache_data
def get_all_genes(genotypes=None, chroms=None, biotypes=None, keyword=None) -> pd.DataFrame:
    """Filtered view over the full gene table, for the Gene Explorer tab."""
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()

    query = "SELECT gene_id, genotype, chrom, start, end, strand, biotype FROM genes WHERE 1=1"
    params = []

    if genotypes:
        query += f" AND genotype IN ({','.join('?' * len(genotypes))})"
        params.extend(genotypes)
    if chroms:
        query += f" AND chrom IN ({','.join('?' * len(chroms))})"
        params.extend(chroms)
    if biotypes:
        query += f" AND biotype IN ({','.join('?' * len(biotypes))})"
        params.extend(biotypes)
    if keyword:
        query += " AND gene_id LIKE ?"
        params.append(f"%{keyword}%")

    query += " ORDER BY genotype, chrom, start"

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    df = df.rename(columns={
        "gene_id": "Gene ID",
        "genotype": "Genotype",
        "chrom": "Chromosome",
        "start": "Start (bp)",
        "end": "End (bp)",
        "strand": "Strand",
        "biotype": "Biotype",
    })
    return df


@st.cache_data
def get_genotype_list() -> list:
    """Return list of genotypes/assemblies currently loaded in the database."""

    if not os.path.exists(DB_PATH):
        return []

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT genotype FROM genes ORDER BY genotype")
    genotypes = [row[0] for row in cursor.fetchall()]
    conn.close()
    return genotypes


def to_phytozome_id(gene_id: str) -> str:
    """Convert a Sorghumbase/Ensembl BTx623 gene ID (SORBI_3...) to its
    Phytozome-style ID (Sobic....). Only valid for protein-coding genes
    on the BTx623 reference -- other gene IDs (e.g. ENSRNA... ncRNAs) have
    no Phytozome equivalent and are returned unchanged.
    """
    match = re.match(r"^SORBI_3(.+)$", gene_id)
    if match:
        return f"Sobic.{match.group(1)}"
    return gene_id


def to_sorghumbase_id(gene_id: str) -> str:
    """Convert a Phytozome-style gene ID (Sobic....) to its Sorghumbase/
    Ensembl BTx623 gene ID (SORBI_3...). Non-Sobic IDs are returned
    unchanged (assumed to already be a Sorghumbase-style ID)."""
    match = re.match(r"^Sobic\.(.+)$", gene_id, re.IGNORECASE)
    if match:
        return f"SORBI_3{match.group(1)}"
    return gene_id


@st.cache_data
def lookup_gene_info(gene_id_input: str, genotype: str = "BTx623") -> dict:
    """
    Look up a single gene by either its Sorghumbase ID (SORBI_3...) or its
    Phytozome ID (Sobic....) and return its annotation plus both ID forms.

    Returns None if the gene is not found in the database.
    """

    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(
            f"annotation.db not found at {DB_PATH}. "
            "Please run: python scripts/build_annotation_db.py"
        )

    gene_id_input = gene_id_input.strip()
    sorghumbase_id = to_sorghumbase_id(gene_id_input)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT gene_id, chrom, start, end, strand, biotype, genotype
        FROM genes
        WHERE genotype = ? AND gene_id = ?
        """,
        (genotype, sorghumbase_id)
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    gene_id, chrom, start, end, strand, biotype, genotype = row
    phytozome_id = to_phytozome_id(gene_id)

    return {
        "sorghumbase_id": gene_id,
        "phytozome_id": phytozome_id if phytozome_id != gene_id else "Not available (Ensembl-only feature)",
        "chrom": chrom,
        "start": start,
        "end": end,
        "strand": strand,
        "biotype": biotype,
        "genotype": genotype,
    }


@st.cache_data
def batch_lookup_gene_info(gene_ids: list, genotype: str = "BTx623") -> pd.DataFrame:
    """Look up multiple gene IDs at once. Returns a DataFrame with one row
    per input ID, marking IDs that weren't found."""

    results = []
    for gene_id in gene_ids:
        gene_id = gene_id.strip()
        if not gene_id:
            continue
        info = lookup_gene_info(gene_id, genotype)
        if info:
            results.append({
                "Input ID": gene_id,
                "SorghumBase ID": info["sorghumbase_id"],
                "Phytozome ID": info["phytozome_id"],
                "Chromosome": info["chrom"],
                "Start (bp)": info["start"],
                "End (bp)": info["end"],
                "Strand": info["strand"],
                "Biotype": info["biotype"],
            })
        else:
            results.append({
                "Input ID": gene_id,
                "SorghumBase ID": "Not found",
                "Phytozome ID": "Not found",
                "Chromosome": "",
                "Start (bp)": pd.NA,
                "End (bp)": pd.NA,
                "Strand": "",
                "Biotype": "",
            })

    df = pd.DataFrame(results)
    for col in ("Start (bp)", "End (bp)"):
        if col in df.columns:
            df[col] = df[col].astype("Int64")
    return df
