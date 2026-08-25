"""
SorghumPost - Tab 1: Gene Proximity Search
=============================================
Find all annotated genes within a defined window around a position on the
Sorghum bicolor (BTx623) reference genome.
Uses Sorghumbase BTx623 annotation via gene_service.py
"""

import streamlit as st
import pandas as pd

from services.gene_service import (
    get_nearby_genes, get_genes_in_region, get_chromosome_list, to_phytozome_id,
)
from services.ui_helpers import section_header, stat_cards, download_row, callout
from services.links import sorghumbase_url, phytozome_url
from services.theme import CATEGORICAL
from services.tracks import single_track_figure, region_track_figure
from services.region_parser import parse_regions


def show():
    section_header(
        "🔍", "Gene Proximity Search",
        "Find genes near a chromosome:position on the BTx623 reference genome"
    )
    callout(
        "Results are based on the <b>BTx623 reference genome</b> "
        "(Sorghumbase / <code>Sorghum_bicolor_NCBIv3</code> annotation -- "
        "the same gene models as Phytozome v3.1.1)."
    )

    mode = st.radio(
        "Input mode", ["Single position", "Paste a region", "Batch upload (CSV)"], horizontal=True
    )

    if mode in ("Single position", "Batch upload (CSV)"):
        st.markdown("**Window size**")
        window_option = st.radio(
            "Select window size around position",
            options=["100 kb", "200 kb", "Custom"],
            horizontal=True,
            label_visibility="collapsed",
        )

        if window_option == "100 kb":
            window_bp = 100000
        elif window_option == "200 kb":
            window_bp = 200000
        else:
            custom_kb = st.number_input("Custom window (kb)", min_value=1, max_value=10000, value=500, step=50)
            window_bp = custom_kb * 1000

    st.divider()

    if mode == "Single position":
        col1, col2 = st.columns(2)

        with col1:
            chrom_list = get_chromosome_list("BTx623")
            main_chroms = [c for c in chrom_list if c.isdigit()]
            chrom = st.selectbox(
                "Chromosome", options=main_chroms if main_chroms else chrom_list,
                help="Select the chromosome your position is on"
            )

        with col2:
            position = st.number_input(
                "Position (bp)", min_value=1, value=5000000, step=1000,
                help="Physical position of your marker/region of interest in base pairs"
            )

        st.caption(f"Searching ± {window_bp:,} bp around Chr{chrom}:{position:,} (BTx623)")

        if st.button("🔍 Search Nearby Genes", type="primary"):
            _run_search([(chrom, position, f"Chr{chrom}:{position:,}")], window_bp, show_track=True)

    elif mode == "Paste a region":
        st.markdown("**Paste one or more genomic regions**")
        st.caption(
            "Paste a region straight out of a GWAS results table or Manhattan plot -- "
            "e.g. `Chr6:34,967,715..35,167,715`. One region per line to search a batch at once."
        )
        region_text = st.text_area(
            "Region(s)",
            placeholder="Chr6:34,967,715..35,167,715\nChr1:1,200,000-1,450,000",
            height=110,
            label_visibility="collapsed",
        )
        flank_kb = st.number_input(
            "Optional flanking padding (kb, added to both sides)",
            min_value=0, max_value=5000, value=0, step=10,
            help="Extend each pasted region by this many kb on both sides. Leave at 0 to search the exact region as pasted.",
        )

        if st.button("🔍 Search Region(s)", type="primary"):
            if not region_text.strip():
                st.warning("Paste at least one region first.")
            else:
                parsed, failed = parse_regions(region_text)
                if failed:
                    bad_lines = "\n".join(f"`{line}`" for line in failed)
                    st.warning(
                        f"Couldn't parse {len(failed)} line(s) -- skipped:\n\n{bad_lines}\n\n"
                        "Expected format: `Chr6:34,967,715..35,167,715` (or `-` / `to` between the numbers)."
                    )
                if parsed:
                    _run_region_search(parsed, flank_kb * 1000, show_track=(len(parsed) == 1))

    else:
        st.markdown("**Upload a CSV file with your positions of interest**")
        st.caption("Required columns: `Marker`, `Chr`, `Position` -- Example: Marker1, 3, 45320000")

        example = "Marker,Chr,Position\nMarker1,3,45320000\nMarker2,1,7123456\nMarker3,7,61234321"
        st.download_button("⬇️ Download Example CSV", data=example, file_name="example_markers.csv", mime="text/csv")

        uploaded = st.file_uploader("Upload your marker CSV", type=["csv"])

        if uploaded is not None:
            try:
                markers_df = pd.read_csv(uploaded)
                required = {"Marker", "Chr", "Position"}
                if not required.issubset(markers_df.columns):
                    st.error(f"CSV must contain columns: {required}. Found: {set(markers_df.columns)}")
                    return

                st.success(f"Loaded {len(markers_df)} positions.")
                st.dataframe(markers_df, width="stretch", hide_index=True)

                markers = [
                    (str(row["Chr"]), int(row["Position"]), row["Marker"])
                    for _, row in markers_df.iterrows()
                ]

                if st.button("🔍 Search All Positions", type="primary"):
                    _run_search(markers, window_bp, show_track=False)

            except Exception as e:
                st.error(f"Error reading CSV: {e}")

    st.divider()
    st.caption(
        "Gene annotation from Sorghumbase (ftp.sorghumbase.org), BTx623 "
        "reference, Sorghum_bicolor_NCBIv3 gene set -- the same annotation "
        "underlying Phytozome Sbicolor v3.1.1."
    )


def _run_search(markers: list, window_bp: int, show_track: bool):
    all_results = []

    with st.spinner(f"Searching {len(markers)} position(s)..."):
        for chrom, position, marker_name in markers:
            try:
                df = get_nearby_genes(chrom, position, window_bp, "BTx623")
                if not df.empty:
                    df.insert(0, "Marker", marker_name)
                    df.insert(1, "Query Position (bp)", position)
                    all_results.append(df)
            except Exception as e:
                st.warning(f"Error processing {marker_name}: {e}")

    if not all_results:
        st.warning("No genes found for any position. Try increasing your window size.")
        return

    combined = pd.concat(all_results, ignore_index=True)

    st.success(f"Found **{len(combined)} gene matches** across **{len(markers)} position(s)**")

    if show_track:
        chrom, position, _ = markers[0]
        section_header("📍", "Gene track")
        fig = single_track_figure(combined, position, window_bp)
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    section_header("📋", "Results")

    display_df = combined.drop(columns=["Genotype"], errors="ignore").copy()
    display_df["SorghumBase"] = display_df["Gene ID"].apply(lambda g: sorghumbase_url(g, "BTx623"))
    display_df["Phytozome"] = display_df["Gene ID"].apply(
        lambda g: phytozome_url(to_phytozome_id(g)) if to_phytozome_id(g) != g else None
    )

    st.dataframe(
        display_df,
        width="stretch",
        hide_index=True,
        height=min(70 + 35 * len(display_df), 460),
        column_config={
            "SorghumBase": st.column_config.LinkColumn("SorghumBase", display_text="View ↗"),
            "Phytozome": st.column_config.LinkColumn("Phytozome", display_text="View ↗"),
            "Start (bp)": st.column_config.NumberColumn(format="%d"),
            "End (bp)": st.column_config.NumberColumn(format="%d"),
            "Distance from Marker (bp)": st.column_config.NumberColumn(format="%d"),
        },
    )
    st.caption("🟢 Overlaps marker &nbsp;&nbsp; 🔵 Near marker")

    st.divider()
    download_row(combined, "SorghumPost_gene_proximity", sheet_name="Gene Proximity", key_prefix="tab1")

    st.divider()
    section_header("📈", "Summary")
    inside = len(combined[combined["Location"] == "Overlaps marker"])
    stat_cards([
        {"label": "Total gene matches", "value": len(combined), "icon": "🧬", "accent": CATEGORICAL["blue"]},
        {"label": "Positions with genes found", "value": combined["Marker"].nunique(), "icon": "📍", "accent": CATEGORICAL["orange"]},
        {"label": "Positions inside a gene", "value": inside, "icon": "🎯", "accent": CATEGORICAL["green"]},
    ])


def _run_region_search(regions: list, flank_bp: int, show_track: bool):
    """Parallel to _run_search, but for explicit pasted [start, end] regions
    (e.g. a GWAS significant interval) rather than a single point + window."""
    all_results = []

    with st.spinner(f"Searching {len(regions)} region(s)..."):
        for chrom, start, end, raw_line in regions:
            search_start = max(1, start - flank_bp)
            search_end = end + flank_bp
            try:
                df = get_genes_in_region(chrom, search_start, search_end, "BTx623")
                if not df.empty:
                    df.insert(0, "Region", raw_line)
                    df.insert(1, "Region Start (bp)", search_start)
                    df.insert(2, "Region End (bp)", search_end)
                    all_results.append(df)
            except Exception as e:
                st.warning(f"Error processing '{raw_line}': {e}")

    if not all_results:
        st.warning("No genes found in any of the pasted region(s). Try adding some flanking padding.")
        return

    combined = pd.concat(all_results, ignore_index=True)

    st.success(f"Found **{len(combined)} gene matches** across **{len(regions)} region(s)**")

    if show_track:
        chrom, start, end, raw_line = regions[0]
        search_start = max(1, start - flank_bp)
        search_end = end + flank_bp
        section_header("📍", "Gene track")
        fig = region_track_figure(combined, search_start, search_end)
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    section_header("📋", "Results")

    display_df = combined.drop(columns=["Genotype"], errors="ignore").copy()
    display_df["SorghumBase"] = display_df["Gene ID"].apply(lambda g: sorghumbase_url(g, "BTx623"))
    display_df["Phytozome"] = display_df["Gene ID"].apply(
        lambda g: phytozome_url(to_phytozome_id(g)) if to_phytozome_id(g) != g else None
    )

    st.dataframe(
        display_df,
        width="stretch",
        hide_index=True,
        height=min(70 + 35 * len(display_df), 460),
        column_config={
            "SorghumBase": st.column_config.LinkColumn("SorghumBase", display_text="View ↗"),
            "Phytozome": st.column_config.LinkColumn("Phytozome", display_text="View ↗"),
            "Region Start (bp)": st.column_config.NumberColumn(format="%d"),
            "Region End (bp)": st.column_config.NumberColumn(format="%d"),
            "Start (bp)": st.column_config.NumberColumn(format="%d"),
            "End (bp)": st.column_config.NumberColumn(format="%d"),
        },
    )
    st.caption("🟢 Fully within region &nbsp;&nbsp; 🔵 Overlaps region boundary")

    st.divider()
    download_row(combined, "SorghumPost_gene_region_search", sheet_name="Gene Region Search", key_prefix="tab1region")

    st.divider()
    section_header("📈", "Summary")
    fully_within = len(combined[combined["Location"] == "Fully within region"])
    stat_cards([
        {"label": "Total gene matches", "value": len(combined), "icon": "🧬", "accent": CATEGORICAL["blue"]},
        {"label": "Regions with genes found", "value": combined["Region"].nunique(), "icon": "📍", "accent": CATEGORICAL["orange"]},
        {"label": "Fully within region", "value": fully_within, "icon": "🎯", "accent": CATEGORICAL["green"]},
    ])
