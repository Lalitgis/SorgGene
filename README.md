# SorghumPost

**A genomics lookup toolkit for sorghum (*Sorghum bicolor*)**

SorghumPost is an open-source Python web application for sorghum researchers who need fast, local, reference-aware tools for working with gene annotation across the Sorghumbase and Phytozome genome portals. Instead of manually browsing genome browsers or cross-referencing gene ID formats, SorghumPost provides a clean browser-based interface that runs locally on your machine.

Built for *Sorghum bicolor*, anchored on the BTx623 reference genome (Sorghumbase `Sorghum_bicolor_NCBIv3`, the same gene models as Phytozome `Sbicolor_v3.1.1`), with pangenome comparison across additional sequenced genotypes.

It's a sibling project to [WheatPost](https://github.com/neupanebpn63/WheatPost), adapted to what Sorghumbase and Phytozome actually provide for sorghum — see [CREDITS.md](CREDITS.md) for the full data lineage and how the feature set differs from WheatPost's.

---

## Features

### 📊 Dashboard
Landing overview with stat cards (genes indexed, genotypes loaded, chromosomes, protein-coding genes), a genes-per-genotype chart, a biotype breakdown chart, and a per-chromosome gene density track — all interactive (Plotly).

### 🔍 Gene Proximity Search
Find all annotated BTx623 genes within a user-defined window (100 kb, 200 kb, or custom) around a chromosome:position of interest. Single-position lookups render an interactive visual gene track (position axis, query marker, overlap highlighting) in addition to the results table. Supports batch CSV upload for multiple positions at once.

- Powered by Sorghumbase's BTx623 (`Sorghum_bicolor_NCBIv3`) gene annotation — 35,479 genes
- Highlights positions that fall directly inside a gene, in both the track diagram and the table
- Clickable gene IDs link to both SorghumBase and Phytozome
- CSV and formatted Excel (.xlsx) download

**Paste a region directly** — got a significant interval straight out of a GWAS results table or Manhattan plot, like `Chr6:34,967,715..35,167,715`? Switch the input mode to **"Paste a region"** and paste it in as-is — no need to compute a midpoint or window size by hand. Accepted separators: `..`, `-`, `–`, or `to` (commas in the numbers are fine). Paste multiple regions, one per line, to search a batch at once, and optionally add flanking padding (in kb) to widen the search on both sides of each region. Each result row is flagged as "Fully within region" or "Overlaps region boundary."

### 🧬 Gene Info & ID Cross-Reference
Look up a gene by either its SorghumBase/Ensembl ID (`SORBI_3001G000100`) or its Phytozome ID (`Sobic.001G000100`) — both refer to the same v3.1.1 gene model, so the cross-reference is exact rather than approximate. Returns coordinates, strand, biotype, and links to both databases. Supports single lookup and batch conversion from a pasted list or uploaded text file.

### 🔎 Gene Explorer
Browse and filter the full 104,785-gene table across every loaded genotype — by genotype, chromosome, biotype, or a gene ID keyword search — for open-ended exploration rather than a targeted position or ID lookup. Sortable grid with clickable SorghumBase links, CSV/Excel export.

### 🔀 Cross-Genotype Comparison
Sorghumbase hosts a pangenome of independently sequenced sorghum genotypes alongside BTx623. This tab compares which genes are annotated in the same chromosome:position window across multiple genotypes side by side — currently BTx623, Tx2783, and Rio — with a per-genotype visual gene track and a genes-found-per-genotype chart.

- Unlike the other tabs, each genotype here is its own independent genome assembly, not a coordinate-lifted version of BTx623 — the UI flags this so results are read as an approximate regional comparison, not an exact liftover
- CSV and formatted Excel (.xlsx) download

---

## Installation

### Requirements
- Python 3.10 or higher
- Git

### Steps

**1. Clone the repository**
```bash
git clone <your-repo-url>
cd SorghumPost
```

**2. Create and activate a virtual environment**
```bash
# Windows
py -m venv .venv
.venv\Scripts\activate

# Mac/Linux
python -m venv .venv
source .venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Verify setup**
```bash
python setup_data.py
```

**5. Run the app**
```bash
streamlit run app.py
```

The app will open automatically in your browser.

---

## Rebuilding the database from source

`database/annotation.db` is included pre-built, so you don't need to do this to run the app. To rebuild it (e.g. to add another genotype), download the relevant GFF3 file(s) from Sorghumbase's public FTP into `data/`, then run:

```bash
python scripts/build_annotation_db.py
```

Source files used for the included database, all from `https://ftp.sorghumbase.org/release-current/gff3/`:

| Genotype | Source file | Assembly |
|---|---|---|
| BTx623 | `sorghum_bicolor/Sorghum_bicolor.Sorghum_bicolor_NCBIv3.gff3.gz` | Sorghum_bicolor_NCBIv3 (= Phytozome Sbicolor v3.1.1) |
| Tx2783 | `sorghum_tx2783pac/Sorghum_tx2783pac.Sorghum_bicolor-Tx2783-Reference-CSHL-USDA-1.0.gff3.gz` | CSHL-USDA-1.0 |
| Rio | `sorghum_rio/Sorghum_rio.JGI-v2.0.gff3.gz` | JGI-v2.0 |

To add more genotypes, add an entry to `GFF3_FILES` in `scripts/build_annotation_db.py` and re-run it — Sorghumbase's FTP lists 100+ additional sorghum genotypes under `release-current/gff3/`.

---

## Example Input Files

Example input files for Tabs 1 and 2 are provided in the `examples/` folder:

- `examples/example_markers.csv` — for batch position input in Tab 1
- `examples/example_gene_ids.txt` — for batch gene ID input in Tab 2

---

## Project structure

```
app.py                     # page config, hero banner, sidebar, tab wiring
services/
  gene_service.py          # all SQLite queries (cached with @st.cache_data)
  theme.py                 # validated color palette, chart chrome
  ui_helpers.py             # CSS injection, stat cards, CSV/Excel export
  links.py                  # SorghumBase / Phytozome URL builders
  tracks.py                 # Plotly gene-track figure builders
  region_parser.py          # parses pasted "Chr6:34,967,715..35,167,715"-style region strings
tabs/
  tab0_dashboard.py
  tab1_gene_proximity.py
  tab2_gene_info.py
  tab3_cross_genotype.py
  tab4_gene_explorer.py
scripts/build_annotation_db.py
database/annotation.db     # pre-built, checked into the repo
.streamlit/config.toml     # Streamlit theme (colors, font)
```

---

## Database Summary

| Database | Source | Size | Records |
|---|---|---|---|
| `annotation.db` | Sorghumbase (BTx623, Tx2783, Rio) | ~15 MB | 104,785 genes |

---

## Credits

See [CREDITS.md](CREDITS.md) for full data attribution — Sorghumbase, Phytozome/JGI, and the reference genome publications.

---

## License

MIT License — free to use, modify, and distribute with attribution.

---

## Contact

For questions, suggestions, or bug reports, please open an issue on GitHub.
