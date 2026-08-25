"""
SorghumPost - Tab 3: Cross-Genotype Comparison
==================================================
Sorghumbase hosts a pangenome of independently assembled sorghum genotypes
alongside the BTx623 reference. This tab compares gene annotation in the
same chromosome:window across multiple genotypes side by side.

Note: because each genotype is its own independent genome assembly (not a
coordinate-lifted version of BTx623, unlike Phytozome/Sorghumbase's shared
v3.1.1 gene IDs for BTx623 itself), this is a same-coordinate comparison,
not a base-pair-exact liftover. It's most informative for genes near the
window center and on well-assembled chromosomes.
"""

import streamlit as st
import plotly.graph_objects as go

from services.gene_service import get_nearby_genes_multi_genotype, get_chromosome_list, get_genotype_list
from services.ui_helpers import section_header, stat_cards, download_row, callout
from services.links import sorghumbase_url
from services.theme import GENOTYPE_COLORS, GRAY_OTHER, CATEGORICAL, apply_plotly_layout
from services.tracks import multi_track_figure


def show():
    section_header(
        "🔀", "Cross-Genotype Comparison",
        "Compare gene annotation across sequenced sorghum genotypes"
    )
    st.warning(
        "⚠️ Each genotype below is an **independently assembled genome**, "
        "not a coordinate-lifted version of BTx623 -- so a shared "
        "chromosome:position window is an approximate comparison, not an "
        "exact base-pair correspondence. Use this to see which genes are "
        "annotated in roughly the same region across genotypes, not as a "
        "precise liftover."
    )

    available_genotypes = get_genotype_list()
    if not available_genotypes:
        st.error("No genotype data loaded yet. Run scripts/build_annotation_db.py first.")
        return

    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            anchor_genotype = st.selectbox(
                "Anchor genotype (defines the chromosome/position you enter below)",
                options=available_genotypes,
                index=available_genotypes.index("BTx623") if "BTx623" in available_genotypes else 0
            )
        with col2:
            compare_genotypes = st.multiselect(
                "Genotypes to compare", options=available_genotypes, default=available_genotypes
            )

        col3, col4 = st.columns(2)
        with col3:
            chrom_list = get_chromosome_list(anchor_genotype)
            main_chroms = [c for c in chrom_list if c.isdigit()]
            chrom = st.selectbox("Chromosome", options=main_chroms if main_chroms else chrom_list)
        with col4:
            position = st.number_input("Position (bp)", min_value=1, value=5000000, step=1000)

        window_option = st.radio("Window size", options=["100 kb", "200 kb", "Custom"], horizontal=True)
        if window_option == "100 kb":
            window_bp = 100000
        elif window_option == "200 kb":
            window_bp = 200000
        else:
            custom_kb = st.number_input("Custom window (kb)", min_value=1, max_value=10000, value=500, step=50)
            window_bp = custom_kb * 1000

    st.caption(
        f"Searching ± {window_bp:,} bp around Chr{chrom}:{position:,} in: "
        f"{', '.join(compare_genotypes) if compare_genotypes else '(none selected)'}"
    )

    if st.button("🔀 Compare Genotypes", type="primary"):
        if not compare_genotypes:
            st.warning("Please select at least one genotype to compare.")
            return

        with st.spinner(f"Comparing {len(compare_genotypes)} genotype(s)..."):
            combined = get_nearby_genes_multi_genotype(chrom, position, window_bp, compare_genotypes)

        if combined.empty:
            st.warning("No genes found in this window for any selected genotype. Try a larger window.")
            return

        st.success(f"Found **{len(combined)} gene(s)** across **{combined['Genotype'].nunique()} genotype(s)**")

        section_header("📍", "Gene tracks by genotype")
        fig = multi_track_figure(combined, position, window_bp, compare_genotypes)
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        st.caption("🟢 Overlaps marker &nbsp;&nbsp; 🔵 Near marker")

        section_header("📊", "Genes found per genotype")
        counts = combined.groupby("Genotype").size().reindex(compare_genotypes).fillna(0).astype(int)
        bar_fig = go.Figure(go.Bar(
            x=counts.index, y=counts.values,
            marker_color=[GENOTYPE_COLORS.get(g, GRAY_OTHER) for g in counts.index],
            text=counts.values, textposition="outside",
            cliponaxis=False,
            hovertemplate="<b>%{x}</b><br>%{y} genes<extra></extra>",
        ))
        apply_plotly_layout(bar_fig, height=280, showlegend=False)
        if counts.max() > 0:
            bar_fig.update_yaxes(range=[0, counts.max() * 1.15])
        st.plotly_chart(bar_fig, width="stretch", config={"displayModeBar": False})

        section_header("📋", "Results")
        display_df = combined.sort_values(["Genotype", "Start (bp)"]).copy()
        display_df["SorghumBase"] = display_df.apply(
            lambda r: sorghumbase_url(r["Gene ID"], r["Genotype"]), axis=1
        )
        st.dataframe(
            display_df,
            width="stretch",
            hide_index=True,
            height=min(70 + 35 * len(display_df), 460),
            column_config={
                "SorghumBase": st.column_config.LinkColumn("SorghumBase", display_text="View ↗"),
                "Start (bp)": st.column_config.NumberColumn(format="%d"),
                "End (bp)": st.column_config.NumberColumn(format="%d"),
            },
        )

        st.divider()
        download_row(
            combined, f"SorghumPost_cross_genotype_Chr{chrom}_{position}",
            sheet_name="Cross-Genotype", key_prefix="tab3"
        )

        st.divider()
        section_header("📈", "Summary")
        stat_cards([
            {"label": "Total gene matches", "value": len(combined), "icon": "🧬", "accent": CATEGORICAL["blue"]},
            {"label": "Genotypes compared", "value": combined["Genotype"].nunique(), "icon": "🌱", "accent": CATEGORICAL["aqua"]},
            {"label": "Overlapping the query", "value": len(combined[combined["Location"] == "Overlaps marker"]), "icon": "🎯", "accent": CATEGORICAL["green"]},
        ])

    st.divider()
    st.caption(
        "Genotype assemblies from Sorghumbase (ftp.sorghumbase.org): "
        "BTx623 = Sorghum_bicolor_NCBIv3, Tx2783 = CSHL-USDA-1.0, "
        "Rio = JGI-v2.0. Each genotype keeps its own native gene ID "
        "namespace (SORBI_3..., SbiRTX2783..., SbRio...)."
    )
