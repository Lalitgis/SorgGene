# SorgGene
<p align="center">
  <img src="figures/logo.png" alt="SorgGene logo" width="180">
</p>

<h1 align="center"> SorgGene</h1>

<p align="center">
  <strong>A fast, reference-aware genomics toolkit for <i>Sorghum bicolor</i></strong>
</p>

<p align="center">
  Sorghum gene annotation lookup · Genomic region analysis · Gene ID cross-reference · Pangenome comparison
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/Database-SQLite-003B57?logo=sqlite&logoColor=white" alt="SQLite">
  <img src="https://img.shields.io/badge/Genes-104%2C785-orange" alt="104,785 genes">
  <img src="https://img.shields.io/badge/Genotypes-3-brightgreen" alt="3 genotypes">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT License">
</p>
<p align="center">
  <strong>Created and maintained by [Lalit BC](https://github.com/Lalitgis)</strong>
</p>


## What is SorgGene?

SorgGene is designed for researchers working with:

* 🌾 *Sorghum bicolor* genomics
* 🧬 Gene annotation and genome annotation
* 📍 GWAS and genomic marker analysis
* 🔎 Candidate-gene discovery
* 🧪 Comparative genomics
* 🌱 Sorghum pangenomics
* 🔗 SorghumBase ↔ Phytozome gene ID conversion
* 📊 Batch genomic-region analysis
* 🧬 Multi-genotype gene annotation comparison

The primary reference is **BTx623**, using the SorghumBase `Sorghum_bicolor_NCBIv3` annotation, corresponding to the **Phytozome Sbicolor v3.1.1** gene models.

Additional genotypes are retained as independent genome assemblies and can be explored through the cross-genotype comparison tools.

---

# ✨ Features

## 📊 1. Genomics Dashboard

Get an immediate overview of the annotation database.

The interactive dashboard provides:

* Total genes indexed
* Number of genotypes
* Chromosome statistics
* Protein-coding gene counts
* Genes-per-genotype visualization
* Biotype distribution
* Per-chromosome gene density
* Interactive Plotly visualizations

This provides a quick quality-control and database overview before starting an analysis.

---

## 🔍 2. Gene Proximity & Region Search

Search for genes surrounding a genomic position or directly analyze a genomic interval.

### Position-based search

Enter:

```text
Chromosome:Position
```

For example:

```text
Chr6:34967715
```

Choose a predefined or custom search window:

* 100 kb
* 200 kb
* Custom window

SorgGene returns annotated BTx623 genes surrounding the query position.

Single-position searches additionally generate an **interactive gene-track visualization** showing:

* Gene coordinates
* Query position
* Overlapping genes
* Strand information
* Genomic position
* Gene boundaries

### Region-based search

Paste a genomic interval directly:

```text
Chr6:34,967,715..35,167,715
```

Supported separators include:

```text
..
-
–
to
```

Multiple regions can be supplied line-by-line for batch analysis.

Optional **flanking padding** allows users to expand each region by a specified number of kilobases.

Each result is classified as:

* **Fully within region**
* **Overlaps region boundary**

### Batch analysis

Upload a CSV containing multiple genomic positions or regions.

Results can be exported as:

* CSV
* Formatted Excel `.xlsx`

### Annotation source

BTx623 annotation:

```text
SorghumBase: Sorghum_bicolor_NCBIv3
Phytozome:   Sbicolor v3.1.1
Genes:       35,479
```

---

# 🧬 3. Gene Information & ID Cross-Reference

SorgGene supports direct lookup using either major sorghum gene identifier format.

### SorghumBase / Ensembl-style ID

```text
SORBI_3001G000100
```

### Phytozome ID

```text
Sobic.001G000100
```

Because these identifiers refer to the same **v3.1.1 gene models**, the conversion is an exact cross-reference rather than a coordinate-based approximation.

For each gene, SorgGene provides:

* Gene ID
* Cross-referenced ID
* Chromosome
* Start position
* End position
* Strand
* Biotype
* SorghumBase link
* Phytozome link

### Batch ID conversion

Users can paste multiple IDs or upload a text file to perform batch cross-referencing.

---

# 🌱 4. Gene Explorer

The **Gene Explorer** provides open-ended access to the complete annotation database.

Filter and search across **104,785 genes** using:

* Genotype
* Chromosome
* Biotype
* Gene ID
* Keyword search

The interactive table supports:

* Sorting
* Filtering
* Clickable database links
* CSV export
* Excel export

This is useful when you don't have a specific genomic position or gene ID and instead want to explore the annotation dataset systematically.

---

# 🔀 5. Cross-Genotype Comparison

SorgGene includes comparative annotation data for:

| Genotype   | Assembly                 |
| ---------- | ------------------------ |
| **BTx623** | `Sorghum_bicolor_NCBIv3` |
| **Tx2783** | `CSHL-USDA-1.0`          |
| **Rio**    | `JGI-v2.0`               |

The tool displays genes found within a comparable chromosome/position window across the loaded genotypes.

Each genotype receives:

* Independent gene-track visualization
* Gene annotation table
* Gene count summary
* CSV export
* Excel export

### ⚠️ Important interpretation

These genomes are **independently assembled references**.

The comparison is therefore a **regional annotation comparison**, not a coordinate liftover.

SorgGene explicitly flags this distinction in the interface to help prevent overinterpretation of coordinate relationships between assemblies.

---

# 🗄️ Database

SorgGene uses a local **SQLite annotation database** for fast querying.

### Current database

| Metric               |       Value |
| -------------------- | ----------: |
| Total genes          | **104,785** |
| Genotypes            |       **3** |
| Database             |      SQLite |
| Database size        |      ~15 MB |
| Reference genotype   |      BTx623 |
| Additional genotypes | Tx2783, Rio |

The pre-built database is included with the repository, allowing the application to run without downloading annotation files.

---

# 🧬 Data Sources

The current database is generated from **SorghumBase GFF3 annotation files**.

| Genotype | Source      | Assembly                 |
| -------- | ----------- | ------------------------ |
| BTx623   | SorghumBase | `Sorghum_bicolor_NCBIv3` |
| Tx2783   | SorghumBase | `CSHL-USDA-1.0`          |
| Rio      | SorghumBase | `JGI-v2.0`               |

BTx623 corresponds to the **Phytozome Sbicolor v3.1.1 gene models**.

For complete attribution, data lineage, and source publications, see [`CREDITS.md`](CREDITS.md).

---

# ⚡ Architecture

SorgGene is intentionally lightweight and designed to run locally.

```text
                    ┌─────────────────────┐
                    │   Streamlit Web UI  │
                    └──────────┬──────────┘
                               │
             ┌─────────────────┼─────────────────┐
             │                 │                 │
       Gene Search       Gene Information   Comparative
       & Regions          & ID Mapping       Genomics
             │                 │                 │
             └─────────────────┼─────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │   Service Layer     │
                    │   Cached Queries    │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │      SQLite DB      │
                    │   104,785 genes     │
                    └─────────────────────┘
```

### Technology stack

* **Python 3.10+**
* **Streamlit**
* **SQLite**
* **Pandas**
* **Plotly**
* **OpenPyXL**
* Custom service and visualization modules

The database layer is separated from the UI so additional annotation datasets and genotypes can be integrated without redesigning the application.

---

# 📁 Project Structure

```text
SorgGene/
│
├── app.py
│
├── database/
│   └── annotation.db
│
├── services/
│   ├── gene_service.py
│   ├── links.py
│   ├── region_parser.py
│   ├── theme.py
│   ├── tracks.py
│   └── ui_helpers.py
│
├── tabs/
│   ├── tab0_dashboard.py
│   ├── tab1_gene_proximity.py
│   ├── tab2_gene_info.py
│   ├── tab3_cross_genotype.py
│   └── tab4_gene_explorer.py
│
├── scripts/
│   └── build_annotation_db.py
│
├── examples/
│   ├── example_markers.csv
│   └── example_gene_ids.txt
│
├── .streamlit/
│   └── config.toml
│
├── setup_data.py
├── requirements.txt
├── CREDITS.md
└── README.md
```

---

# 🚀 Installation

## Requirements

* Python **3.10+**
* Git

### 1. Clone the repository

```bash
git clone <https://github.com/Lalitgis/SorgGene.git>
cd SorgGene
```

### 2. Create a virtual environment

**Windows**

```bash
py -m venv .venv
.venv\Scripts\activate
```

**macOS / Linux**

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Verify the installation

```bash
python setup_data.py
```

### 5. Launch SorgGene

```bash
streamlit run app.py
```

The application will open in your default browser.

---

# 🧪 Example Workflows

## GWAS candidate-gene discovery

```text
GWAS signal
    ↓
Genomic interval
    ↓
SorgGene Region Search
    ↓
Annotated genes
    ↓
Gene IDs + coordinates
    ↓
Candidate-gene prioritization
```

## Gene ID conversion

```text
Sobic.001G000100
        ↓
SorgGene
        ↓
SORBI_3001G000100
        ↓
SorghumBase / Phytozome
```

## Multi-genotype exploration

```text
Genomic region
       ↓
 ┌─────┼─────┐
 ↓     ↓     ↓
BTx623 Tx2783 Rio
 ↓     ↓     ↓
Annotation comparison
       ↓
Candidate regions / genes
```

---

# 🔧 Rebuilding & Extending the Database

The repository contains a pre-built `annotation.db`, so rebuilding is **not required for normal use**.

To add additional genotypes:

### 1. Download the relevant GFF3

Place the annotation file in:

```text
data/
```

### 2. Add the genotype to

```text
scripts/build_annotation_db.py
```

### 3. Rebuild

```bash
python scripts/build_annotation_db.py
```

SorghumBase's current FTP release contains **100+ additional sorghum genotypes**, making the database architecture suitable for future pangenome expansion.

---

# 📦 Example Data

Example inputs are included in:

```text
examples/
```

### Batch marker search

```text
examples/example_markers.csv
```

### Batch gene ID lookup

```text
examples/example_gene_ids.txt
```

These can be used to test the application immediately after installation.

---

# 🔗 Related Project

SorgGene is a sorghum-focused sibling project to **[WheatPost](https://github.com/neupanebpn63/WheatPost)**, adapting the same general philosophy of fast, researcher-friendly genomic lookup tools to the datasets and annotation resources available for *Sorghum bicolor*.

The feature set has been adapted specifically to SorghumBase and Phytozome rather than attempting to reproduce wheat-specific functionality.

---

# 📚 Data Attribution

SorgGene uses publicly available genome annotation resources from:

* **SorghumBase**
* **Phytozome / JGI**
* Published *Sorghum bicolor* reference genome resources

Please see [`CREDITS.md`](CREDITS.md) for complete data attribution, source files, publications, and data lineage.

---

# 🛣️ Roadmap

Potential future development includes:

* [ ] Support for additional SorghumBase genotypes
* [ ] Expanded pangenome comparison
* [ ] Gene-family exploration
* [ ] Protein sequence lookup
* [ ] Functional annotation integration
* [ ] GO enrichment workflows
* [ ] Ortholog/paralog exploration
* [ ] REST/API access
* [ ] Containerized deployment
* [ ] Cloud-hosted version
* [ ] Automated annotation database updates

---

# 🤝 Contributing

Contributions, bug reports, feature requests, and improvements are welcome.

Please open a GitHub issue or submit a pull request.

If you use SorgGene in research, feedback on additional datasets, genotypes, and analysis workflows is especially welcome.

---

# 📄 License

SorgGene is released under the **MIT License**.

See [`LICENSE`](LICENSE) for details.

---

## SorgGene

**Fast. Local. Reference-aware.**

A practical bioinformatics toolkit for *Sorghum bicolor* gene annotation, genomic-region analysis, gene ID conversion, and multi-genotype exploration.

**Keywords:** sorghum genomics · *Sorghum bicolor* · bioinformatics · plant genomics · gene annotation · SorghumBase · Phytozome · BTx623 · sorghum pangenomics · comparative genomics · GWAS · candidate gene discovery · genomic region search · gene ID conversion · genome annotation · Streamlit · Python
