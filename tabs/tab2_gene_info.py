"""
SorghumPost - Tab 2: Gene Info & ID Cross-Reference
======================================================
Look up a Sorghum bicolor (BTx623) gene by either its Sorghumbase/Ensembl ID
(SORBI_3...) or its Phytozome ID (Sobic....), and get its coordinates plus
both ID forms with direct links out to each database.
"""

import streamlit as st
import pandas as pd

from services.gene_service import lookup_gene_info, batch_lookup_gene_info
from services.ui_helpers import section_header, stat_cards, download_row, callout
from services.links import sorghumbase_url, phytozome_url
from services.theme import CATEGORICAL


def show():
    section_header(
        "🧬", "Gene Info & ID Cross-Reference",
        "Look up a BTx623 gene by its SorghumBase or Phytozome ID"
    )
    callout(
        "Enter either <b>SORBI_3001G000100</b> (SorghumBase/Ensembl) or "
        "<b>Sobic.001G000100</b> (Phytozome) -- both refer to the same v3.1.1 "
        "gene model, so the cross-reference is exact, not fuzzy. 💡 IDs are "
        "converted automatically in either direction."
    )

    mode = st.radio("Input mode", ["Single gene ID", "Batch lookup"], horizontal=True)
    st.divider()

    if mode == "Single gene ID":
        gene_id = st.text_input(
            "Enter gene ID",
            placeholder="e.g. SORBI_3001G000100 or Sobic.001G000100",
        )

        if st.button("🔍 Look Up", type="primary"):
            if not gene_id.strip():
                st.warning("Please enter a gene ID.")
                return

            with st.spinner("Looking up gene..."):
                try:
                    info = lookup_gene_info(gene_id.strip())

                    if info is None:
                        st.error(
                            f"Gene ID `{gene_id}` was not found in the BTx623 "
                            f"reference annotation. Please check the ID."
                        )
                    else:
                        st.success("Gene found")

                        with st.container(border=True):
                            c1, c2 = st.columns(2)
                            with c1:
                                st.metric("SorghumBase ID", info["sorghumbase_id"])
                                st.markdown(
                                    f'<a href="{sorghumbase_url(info["sorghumbase_id"])}" target="_blank">🔗 View on SorghumBase</a>',
                                    unsafe_allow_html=True
                                )
                            with c2:
                                st.metric("Phytozome ID", info["phytozome_id"])
                                if not info["phytozome_id"].startswith("Not available"):
                                    st.markdown(
                                        f'<a href="{phytozome_url(info["phytozome_id"])}" target="_blank">🔗 View on Phytozome</a>',
                                        unsafe_allow_html=True
                                    )

                        st.write("")
                        stat_cards([
                            {"label": "Chromosome", "value": info["chrom"], "icon": "🧵", "accent": CATEGORICAL["blue"]},
                            {"label": "Start (bp)", "value": f'{info["start"]:,}', "icon": "▶️", "accent": CATEGORICAL["orange"]},
                            {"label": "End (bp)", "value": f'{info["end"]:,}', "icon": "⏹️", "accent": CATEGORICAL["aqua"]},
                            {"label": "Strand / Biotype", "value": f'{info["strand"]} / {info["biotype"]}', "icon": "🧬", "accent": CATEGORICAL["violet"]},
                        ])

                        st.divider()
                        df_single = pd.DataFrame([{
                            "Input ID": gene_id,
                            "SorghumBase ID": info["sorghumbase_id"],
                            "Phytozome ID": info["phytozome_id"],
                            "Chromosome": info["chrom"],
                            "Start (bp)": info["start"],
                            "End (bp)": info["end"],
                            "Strand": info["strand"],
                            "Biotype": info["biotype"],
                        }])
                        download_row(df_single, f"SorghumPost_gene_info_{gene_id}", sheet_name="Gene Info", key_prefix="tab2_single")

                except FileNotFoundError as e:
                    st.error(str(e))
                except Exception as e:
                    st.error(f"Unexpected error: {e}")

    else:
        st.markdown("**Option A -- Paste gene IDs**")
        pasted = st.text_area(
            "Paste gene IDs (one per line, either format)",
            placeholder="SORBI_3001G000100\nSobic.001G000200\nSORBI_3003G000400",
            height=150
        )

        st.markdown("**Option B -- Upload a text file**")
        uploaded = st.file_uploader("Upload a .txt file with one gene ID per line", type=["txt"])

        gene_ids = []
        if pasted.strip():
            gene_ids = [g.strip() for g in pasted.strip().split("\n") if g.strip()]
        elif uploaded is not None:
            content = uploaded.read().decode("utf-8")
            gene_ids = [g.strip() for g in content.split("\n") if g.strip()]

        if gene_ids:
            st.caption(f"{len(gene_ids)} gene ID(s) ready for lookup")

        if st.button("🔍 Look Up All", type="primary"):
            if not gene_ids:
                st.warning("Please paste or upload gene IDs.")
                return

            with st.spinner(f"Looking up {len(gene_ids)} gene ID(s)..."):
                try:
                    df = batch_lookup_gene_info(gene_ids)

                    found = len(df[df["SorghumBase ID"] != "Not found"])
                    not_found = len(df[df["SorghumBase ID"] == "Not found"])

                    st.success(f"**{found}** gene(s) found -- **{not_found}** not found")

                    display_df = df.copy()
                    display_df["SorghumBase Link"] = display_df["SorghumBase ID"].apply(
                        lambda gid: sorghumbase_url(gid) if gid != "Not found" else None
                    )
                    display_df["Phytozome Link"] = display_df["Phytozome ID"].apply(
                        lambda gid: phytozome_url(gid) if gid not in ("Not found", "Not available (Ensembl-only feature)") else None
                    )

                    st.dataframe(
                        display_df,
                        width="stretch",
                        hide_index=True,
                        height=min(70 + 35 * len(display_df), 460),
                        column_config={
                            "SorghumBase Link": st.column_config.LinkColumn("SorghumBase", display_text="View ↗"),
                            "Phytozome Link": st.column_config.LinkColumn("Phytozome", display_text="View ↗"),
                            "Start (bp)": st.column_config.NumberColumn(format="%d"),
                            "End (bp)": st.column_config.NumberColumn(format="%d"),
                        },
                    )

                    st.divider()
                    download_row(df, "SorghumPost_gene_info_batch", sheet_name="Gene Info", key_prefix="tab2_batch")

                except FileNotFoundError as e:
                    st.error(str(e))
                except Exception as e:
                    st.error(f"Unexpected error: {e}")

    st.divider()
    st.caption(
        "Gene annotation from Sorghumbase (BTx623 / Sorghum_bicolor_NCBIv3). "
        "Phytozome ID mapping is a direct format conversion (Sobic.xxxGxxxxxx "
        "&harr; SORBI_3xxxGxxxxxx) since both databases share the same v3.1.1 "
        "gene models for the BTx623 reference."
    )
