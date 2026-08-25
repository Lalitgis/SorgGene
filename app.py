import streamlit as st

from tabs import (
    tab0_dashboard,
    tab1_gene_proximity,
    tab2_gene_info,
    tab3_cross_genotype,
    tab4_gene_explorer,
)
from services.ui_helpers import inject_css, hero, footer
from services.gene_service import get_summary_stats

st.set_page_config(
    page_title="SorghumPost",
    page_icon="figures/logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

hero(
    "SorghumPost",
    "Sorghum genomics toolkit -- built on Sorghumbase &amp; Phytozome data",
    icon="figure/logo.png",
    badges=["Sorghum bicolor", "BTx623 reference", "3 genotypes", "Runs locally"],
)

with st.sidebar:
    st.image('figure/logo.png')
    st.markdown("### SorghumPost")
    st.caption("A genomics lookup toolkit for *Sorghum bicolor*")
    st.divider()

    stats = get_summary_stats()
    if stats:
        st.markdown("**Database**")
        st.markdown(f"- {stats['total_genes']:,} genes indexed")
        st.markdown(f"- {stats['total_genotypes']} genotypes loaded")
        st.markdown(f"- {stats['total_chroms']} BTx623 chromosomes")

    st.divider()
    st.markdown("**Data sources**")
    st.markdown("- [SorghumBase](https://www.sorghumbase.org)")
    st.markdown("- [Phytozome](https://phytozome-next.jgi.doe.gov)")

    st.divider()
    st.caption("Sibling project to [WheatPost](https://github.com/neupanebpn63/WheatPost)")

tabs = st.tabs([
    "📊 Dashboard",
    "🔍 Gene Proximity",
    "🧬 Gene Info / ID Lookup",
    "🔎 Gene Explorer",
    "🔀 Cross-Genotype Comparison",
])

with tabs[0]:
    tab0_dashboard.show()

with tabs[1]:
    tab1_gene_proximity.show()

with tabs[2]:
    tab2_gene_info.show()

with tabs[3]:
    tab4_gene_explorer.show()

with tabs[4]:
    tab3_cross_genotype.show()

footer()
