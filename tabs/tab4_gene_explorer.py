"""
SorghumPost - Tab 4: Gene Explorer
=====================================
Browse and filter the full gene table across every loaded genotype --
for open-ended exploration rather than a targeted position or ID lookup.
"""

import streamlit as st

from services.gene_service import get_all_genes, get_genotype_list, get_chromosome_list
from services.ui_helpers import section_header, download_row, callout
from services.links import sorghumbase_url

DISPLAY_CAP = 2000


def show():
    section_header("🔎", "Gene Explorer", "Filter and browse the full annotated gene set")

    genotypes = get_genotype_list()
    if not genotypes:
        st.error("Database not found. Run scripts/build_annotation_db.py first.")
        return

    with st.container(border=True):
        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            selected_genotypes = st.multiselect(
                "Genotype", options=genotypes, default=genotypes
            )

        with col2:
            all_chroms = sorted({
                c for g in (selected_genotypes or genotypes)
                for c in get_chromosome_list(g) if c.isdigit()
            }, key=lambda c: int(c))
            selected_chroms = st.multiselect(
                "Chromosome", options=all_chroms, default=[],
                help="Leave empty to include all chromosomes (main + scaffolds)"
            )

        with col3:
            biotype_options = [
                "protein_coding", "rRNA", "tRNA", "snoRNA", "pre_miRNA",
                "snRNA", "sense_intronic", "SRP_RNA", "antisense_RNA",
                "ncRNA", "RNase_MRP_RNA",
            ]
            selected_biotypes = st.multiselect(
                "Biotype", options=biotype_options, default=[],
                help="Leave empty to include all biotypes"
            )

        keyword = st.text_input(
            "Search gene ID contains",
            placeholder="e.g. SORBI_3001, Sobic, SbRio"
        )

    if not selected_genotypes:
        st.warning("Select at least one genotype to search.")
        return

    df = get_all_genes(
        genotypes=selected_genotypes,
        chroms=selected_chroms or None,
        biotypes=selected_biotypes or None,
        keyword=keyword.strip() or None,
    )

    if df.empty:
        st.info("No genes match these filters. Try broadening your search.")
        return

    st.success(f"**{len(df):,}** gene(s) match your filters")

    display_df = df.copy()
    if len(display_df) > DISPLAY_CAP:
        callout(
            f"Showing the first <b>{DISPLAY_CAP:,}</b> of <b>{len(df):,}</b> matches. "
            f"Narrow your filters to see more on screen, or use the download "
            f"buttons below to get the full filtered result."
        )
        display_df = display_df.head(DISPLAY_CAP)

    display_df["SorghumBase Link"] = display_df.apply(
        lambda r: sorghumbase_url(r["Gene ID"], r["Genotype"]), axis=1
    )

    st.dataframe(
        display_df,
        width="stretch",
        hide_index=True,
        height=460,
        column_config={
            "SorghumBase Link": st.column_config.LinkColumn(
                "SorghumBase", display_text="View ↗"
            ),
            "Start (bp)": st.column_config.NumberColumn(format="%d"),
            "End (bp)": st.column_config.NumberColumn(format="%d"),
        },
    )

    st.divider()
    download_row(df, "SorghumPost_gene_explorer", sheet_name="Genes", key_prefix="explorer")

    st.divider()
    st.caption(
        "Browsing all loaded genotypes' annotation from Sorghumbase. "
        "Use the Gene Info tab for exact SorghumBase &harr; Phytozome ID conversion."
    )
