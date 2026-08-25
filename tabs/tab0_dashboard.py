"""
SorghumPost - Tab 0: Dashboard
=================================
Landing overview: summary stats and quick charts across the loaded
Sorghumbase genotype annotation, plus an explanation of what each tool
in the app does.
"""

import streamlit as st
import plotly.graph_objects as go

from services.gene_service import (
    get_summary_stats,
    get_genes_per_genotype,
    get_biotype_breakdown,
    get_genes_per_chromosome,
    get_gene_density_along_chrom,
    get_genotype_list,
    get_chromosome_list,
)
from services.ui_helpers import section_header, stat_cards, callout
from services.theme import (
    GENOTYPE_COLORS, BIOTYPE_COLORS, GRAY_OTHER, BIOTYPE_ORDER,
    CATEGORICAL, apply_plotly_layout,
)


def show():
    stats = get_summary_stats()
    if not stats:
        st.error("Database not found. Run scripts/build_annotation_db.py first.")
        return

    section_header("📊", "Overview", "What's loaded in this instance of SorghumPost")

    stat_cards([
        {"label": "Total genes indexed", "value": f"{stats['total_genes']:,}", "icon": "🧬", "accent": CATEGORICAL["blue"]},
        {"label": "Genotypes loaded", "value": stats["total_genotypes"], "icon": "🌱", "accent": CATEGORICAL["aqua"]},
        {"label": "BTx623 chromosomes", "value": stats["total_chroms"], "icon": "🧵", "accent": CATEGORICAL["orange"]},
        {"label": "BTx623 protein-coding genes", "value": f"{stats['protein_coding_btx623']:,}", "icon": "⚙️", "accent": CATEGORICAL["violet"]},
    ])

    st.divider()

    col1, col2 = st.columns(2, gap="large")

    with col1:
        section_header("🌾", "Genes per genotype")
        df = get_genes_per_genotype()
        if not df.empty:
            colors = [GENOTYPE_COLORS.get(g, GRAY_OTHER) for g in df["Genotype"]]
            fig = go.Figure(go.Bar(
                x=df["Genotype"], y=df["Genes"],
                marker_color=colors,
                text=df["Genes"].map(lambda v: f"{v:,}"),
                textposition="outside",
                cliponaxis=False,
                hovertemplate="<b>%{x}</b><br>%{y:,} genes<extra></extra>",
            ))
            apply_plotly_layout(fig, height=320, showlegend=False)
            fig.update_yaxes(range=[0, df["Genes"].max() * 1.15])
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    with col2:
        section_header("🧬", "Biotype breakdown")
        genotypes = get_genotype_list()
        default_idx = genotypes.index("BTx623") if "BTx623" in genotypes else 0
        biotype_genotype = st.selectbox("Genotype", options=genotypes, index=default_idx, key="dash_biotype_genotype")
        bdf = get_biotype_breakdown(biotype_genotype)
        if not bdf.empty:
            # Fold anything past the top 6 canonical biotypes into "Other"
            bdf = bdf.copy()
            bdf["Biotype"] = bdf["Biotype"].apply(lambda b: b if b in BIOTYPE_ORDER else "Other")
            bdf = bdf.groupby("Biotype", as_index=False)["Genes"].sum().sort_values("Genes", ascending=True)
            colors = [BIOTYPE_COLORS.get(b, GRAY_OTHER) for b in bdf["Biotype"]]
            fig = go.Figure(go.Bar(
                x=bdf["Genes"], y=bdf["Biotype"], orientation="h",
                marker_color=colors,
                text=bdf["Genes"].map(lambda v: f"{v:,}"),
                textposition="outside",
                cliponaxis=False,
                hovertemplate="<b>%{y}</b><br>%{x:,} genes<extra></extra>",
            ))
            apply_plotly_layout(fig, height=320, showlegend=False)
            fig.update_xaxes(range=[0, bdf["Genes"].max() * 1.25])
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    st.divider()

    section_header("📍", "Gene density along a chromosome", "Genes per 1 Mb window -- pick a genotype and chromosome")
    col3, col4 = st.columns([1, 1])
    with col3:
        density_genotype = st.selectbox("Genotype", options=get_genotype_list(), key="dash_density_genotype")
    with col4:
        chroms = [c for c in get_chromosome_list(density_genotype) if c.isdigit()]
        density_chrom = st.selectbox("Chromosome", options=chroms, key="dash_density_chrom")

    ddf = get_gene_density_along_chrom(density_genotype, density_chrom)
    if not ddf.empty:
        fig = go.Figure(go.Bar(
            x=ddf["Bin Start (bp)"], y=ddf["Genes"],
            marker_color=CATEGORICAL["blue"],
            hovertemplate="Position %{x:,} bp<br>%{y} genes in this 1 Mb window<extra></extra>",
        ))
        apply_plotly_layout(fig, height=280, showlegend=False)
        fig.update_xaxes(title="Position (bp)")
        fig.update_yaxes(title="Genes / 1 Mb")
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    st.divider()

    section_header("🧭", "What's in this app")
    callout(
        "<b>🔍 Gene Proximity Search</b> -- find genes near a chromosome:position on the BTx623 reference.<br>"
        "<b>🧬 Gene Info &amp; ID Lookup</b> -- cross-reference SorghumBase &harr; Phytozome gene IDs.<br>"
        "<b>🔎 Gene Explorer</b> -- browse and filter the full gene table across every loaded genotype.<br>"
        "<b>🔀 Cross-Genotype Comparison</b> -- see which genes sit in the same region across BTx623, Tx2783, and Rio."
    )
