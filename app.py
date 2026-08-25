import streamlit as st
from pathlib import Path

from tabs import (
    tab0_dashboard,
    tab1_gene_proximity,
    tab2_gene_info,
    tab3_cross_genotype,
    tab4_gene_explorer,
)

from services.ui_helpers import inject_css, footer
from services.gene_service import get_summary_stats


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).parent
LOGO_PATH = BASE_DIR / "figures" / "logo.png"


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="SorghumPost",
    page_icon=str(LOGO_PATH),
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM CSS
# ============================================================

inject_css()

st.markdown(
    """
    <style>

    /* Main hero container */
    .sorghumpost-hero {
        padding: 1.5rem 2rem;
        border-radius: 18px;
        margin-bottom: 1.5rem;
        background: linear-gradient(
            135deg,
            rgba(46, 125, 50, 0.10),
            rgba(255, 255, 255, 0.04)
        );
        border: 1px solid rgba(128, 128, 128, 0.20);
    }

    /* Hero content */
    .hero-content {
        display: flex;
        align-items: center;
        gap: 20px;
    }

    /* Logo */
    .hero-logo {
        width: 85px;
        height: 85px;
        object-fit: contain;
        border-radius: 14px;
    }

    /* Title */
    .hero-title {
        font-size: 2.6rem;
        font-weight: 750;
        margin: 0;
        padding: 0;
        line-height: 1.1;
    }

    /* Subtitle */
    .hero-subtitle {
        font-size: 1.05rem;
        margin-top: 7px;
        opacity: 0.75;
    }

    /* Badges */
    .hero-badges {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 18px;
    }

    .hero-badge {
        padding: 5px 11px;
        border-radius: 999px;
        font-size: 0.82rem;
        border: 1px solid rgba(128, 128, 128, 0.25);
        background: rgba(128, 128, 128, 0.08);
    }

    /* Sidebar logo */
    .sidebar-logo {
        display: flex;
        justify-content: center;
        margin-bottom: 5px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HERO SECTION
# ============================================================

badges = [
    "Sorghum bicolor",
    "BTx623 reference",
    "3 genotypes",
    "Runs locally",
]

badge_html = "".join(
    f'<span class="hero-badge">{badge}</span>'
    for badge in badges
)

st.markdown(
    f"""
    <div class="sorghumpost-hero">

        <div class="hero-content">

            <img
                src="data:image/png;base64,{__import__('base64').b64encode(
                    LOGO_PATH.read_bytes()
                ).decode()}"
                class="hero-logo"
            >

            <div>
                <div class="hero-title">
                    SorghumPost
                </div>

                <div class="hero-subtitle">
                    Sorghum genomics toolkit — built on SorghumBase &amp; Phytozome data
                </div>
            </div>

        </div>

        <div class="hero-badges">
            {badge_html}
        </div>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    # Logo
    st.image(str(LOGO_PATH), width=70)

    st.markdown("### SorghumPost")

    st.caption(
        "A genomics lookup toolkit for *Sorghum bicolor*"
    )

    st.divider()

    # --------------------------------------------------------
    # Database statistics
    # --------------------------------------------------------

    stats = get_summary_stats()

    if stats:

        st.markdown("**Database**")

        st.markdown(
            f"- {stats['total_genes']:,} genes indexed"
        )

        st.markdown(
            f"- {stats['total_genotypes']} genotypes loaded"
        )

        st.markdown(
            f"- {stats['total_chroms']} BTx623 chromosomes"
        )

    st.divider()

    # --------------------------------------------------------
    # Data sources
    # --------------------------------------------------------

    st.markdown("**Data sources**")

    st.markdown(
        "- [SorghumBase](https://www.sorghumbase.org)"
    )

    st.markdown(
        "- [Phytozome](https://phytozome-next.jgi.doe.gov)"
    )

    st.divider()

    # --------------------------------------------------------
    # Related project
    # --------------------------------------------------------

    st.caption(
        "Sibling project to "
        "[WheatPost](https://github.com/neupanebpn63/WheatPost)"
    )


# ============================================================
# TABS
# ============================================================

tabs = st.tabs(
    [
        "📊 Dashboard",
        "🔍 Gene Proximity",
        "🧬 Gene Info / ID Lookup",
        "🔎 Gene Explorer",
        "🔀 Cross-Genotype Comparison",
    ]
)


# ============================================================
# TAB 1 — DASHBOARD
# ============================================================

with tabs[0]:
    tab0_dashboard.show()


# ============================================================
# TAB 2 — GENE PROXIMITY
# ============================================================

with tabs[1]:
    tab1_gene_proximity.show()


# ============================================================
# TAB 3 — GENE INFO / ID LOOKUP
# ============================================================

with tabs[2]:
    tab2_gene_info.show()


# ============================================================
# TAB 4 — GENE EXPLORER
# ============================================================

with tabs[3]:
    tab4_gene_explorer.show()


# ============================================================
# TAB 5 — CROSS-GENOTYPE COMPARISON
# ============================================================

with tabs[4]:
    tab3_cross_genotype.show()


# ============================================================
# FOOTER
# ============================================================

footer()
