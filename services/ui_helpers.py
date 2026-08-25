"""
SorghumPost - UI Helpers
===========================
Reusable, styled building blocks shared across every tab: the global CSS
injection, stat card grid, section headers, and CSV+Excel export widgets.
Keeping these in one place is what makes the five tabs look like one
product instead of five separate scripts.
"""
import base64
import os

_IMAGE_EXTS = {".png": "png", ".jpg": "jpeg", ".jpeg": "jpeg", ".gif": "gif", ".webp": "webp", ".svg": "svg+xml"}


def _icon_html(icon: str, height: str = "2.6rem") -> str:
    """Render `icon` for use inside a raw-HTML block. If it looks like a path
    to an image file that exists on disk, embed it as a base64 <img> tag
    (st.markdown can't reference local file paths directly); otherwise treat
    it as emoji/text and pass it through unchanged."""
    ext = os.path.splitext(str(icon))[1].lower()
    if ext in _IMAGE_EXTS and os.path.exists(icon):
        mime = _IMAGE_EXTS[ext]
        with open(icon, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        return f'<img src="data:image/{mime};base64,{b64}" style="height:{height};width:auto;display:block;" />'
    return icon
import io
import streamlit as st
import pandas as pd

from services.theme import BRAND_PRIMARY, BRAND_PRIMARY_DARK, INK_SECONDARY, GRIDLINE


def inject_css():
    st.markdown(f"""
    <style>
        /* ---- page chrome ---- */
        .block-container {{
            padding-top: 1.5rem;
            padding-bottom: 3rem;
            max-width: 1200px;
        }}

        /* ---- hero masthead ---- */
        .sp-hero {{
            background: linear-gradient(120deg, #fff6ea 0%, #fdece0 55%, #fbe3d3 100%);
            border: 1px solid #f0dcc4;
            border-radius: 16px;
            padding: 1.6rem 2rem;
            margin-bottom: 1.6rem;
            display: flex;
            align-items: center;
            gap: 1.2rem;
        }}
        .sp-hero-icon {{
            font-size: 2.6rem;
            line-height: 1;
        }}
        .sp-hero-title {{
            font-size: 1.9rem;
            font-weight: 800;
            color: #1a1a19;
            margin: 0;
            letter-spacing: -0.02em;
        }}
        .sp-hero-subtitle {{
            font-size: 0.98rem;
            color: {INK_SECONDARY};
            margin-top: 0.15rem;
        }}
        .sp-hero-badges {{ margin-top: 0.55rem; }}
        .sp-badge {{
            display: inline-block;
            font-size: 0.72rem;
            font-weight: 600;
            color: {BRAND_PRIMARY_DARK};
            background: #ffffffaa;
            border: 1px solid #f0c9a8;
            border-radius: 999px;
            padding: 0.15rem 0.6rem;
            margin-right: 0.4rem;
        }}

        /* ---- section header ---- */
        .sp-section {{
            display: flex;
            align-items: center;
            gap: 0.7rem;
            margin: 0.2rem 0 0.3rem 0;
        }}
        .sp-section-icon {{
            font-size: 1.5rem;
            width: 2.4rem;
            height: 2.4rem;
            min-width: 2.4rem;
            border-radius: 10px;
            background: #fdece0;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .sp-section-title {{
            font-size: 1.3rem;
            font-weight: 750;
            color: #1a1a19;
            margin: 0;
        }}
        .sp-section-subtitle {{
            font-size: 0.9rem;
            color: {INK_SECONDARY};
            margin: 0.1rem 0 0.9rem 3.1rem;
        }}

        /* ---- stat cards ---- */
        .sp-stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
            gap: 0.9rem;
            margin: 0.8rem 0 1.4rem 0;
        }}
        .sp-stat-card {{
            background: #ffffff;
            border: 1px solid {GRIDLINE};
            border-top: 3px solid var(--accent, {BRAND_PRIMARY});
            border-radius: 12px;
            padding: 0.9rem 1.05rem;
            box-shadow: 0 1px 2px rgba(11,11,11,0.04);
        }}
        .sp-stat-icon {{ font-size: 1.15rem; opacity: 0.85; }}
        .sp-stat-value {{
            font-size: 1.65rem;
            font-weight: 800;
            color: #1a1a19;
            line-height: 1.2;
            margin-top: 0.15rem;
        }}
        .sp-stat-label {{
            font-size: 0.8rem;
            color: {INK_SECONDARY};
            font-weight: 500;
        }}

        /* ---- info banner ---- */
        .sp-callout {{
            background: #fdf7ee;
            border: 1px solid #f0dcc4;
            border-left: 4px solid {BRAND_PRIMARY};
            border-radius: 8px;
            padding: 0.7rem 1rem;
            font-size: 0.88rem;
            color: #4a3f2f;
            margin-bottom: 1rem;
        }}

        /* ---- tabs ---- */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 4px;
        }}
        .stTabs [data-baseweb="tab"] {{
            font-weight: 600;
            padding: 0.5rem 1rem;
        }}

        /* ---- buttons ---- */
        .stButton > button, .stDownloadButton > button {{
            border-radius: 8px;
            font-weight: 600;
        }}

        /* ---- footer ---- */
        .sp-footer {{
            margin-top: 2.5rem;
            padding-top: 1rem;
            border-top: 1px solid {GRIDLINE};
            font-size: 0.78rem;
            color: {INK_SECONDARY};
            text-align: center;
        }}
    </style>
    """, unsafe_allow_html=True)


def hero(title: str, subtitle: str, icon: str = "🌾", badges=None):
    badges_html = ""
    if badges:
        badges_html = '<div class="sp-hero-badges">' + "".join(
            f'<span class="sp-badge">{b}</span>' for b in badges
        ) + "</div>"
    st.markdown(f"""
    <div class="sp-hero">
        <div class="sp-hero-icon">{_icon_html(icon)}</div>
        <div>
            <p class="sp-hero-title">{title}</p>
            <p class="sp-hero-subtitle">{subtitle}</p>
            {badges_html}
        </div>
    </div>
    """, unsafe_allow_html=True)


def section_header(icon: str, title: str, subtitle: str = ""):
    st.markdown(f"""
    <div class="sp-section">
        <div class="sp-section-icon">{icon}</div>
        <p class="sp-section-title">{title}</p>
    </div>
    {f'<p class="sp-section-subtitle">{subtitle}</p>' if subtitle else ""}
    """, unsafe_allow_html=True)


def stat_cards(items):
    """items: list of dicts with keys label, value, icon (optional), accent (optional hex).

    NOTE: every fragment here is built as a single line with no embedded
    newlines. Streamlit's markdown renderer treats a line of only
    whitespace inside an HTML block as a blank line, which ends the block
    early -- multi-line indented f-strings concatenated in a loop trigger
    that and silently drop everything after the first card.
    """
    cards = [
        '<div class="sp-stat-card" style="--accent:{accent}">'
        '<div class="sp-stat-icon">{icon}</div>'
        '<div class="sp-stat-value">{value}</div>'
        '<div class="sp-stat-label">{label}</div>'
        '</div>'.format(
            accent=item.get("accent", BRAND_PRIMARY),
            icon=item.get("icon", ""),
            value=item["value"],
            label=item["label"],
        )
        for item in items
    ]
    st.markdown('<div class="sp-stats-grid">' + "".join(cards) + "</div>", unsafe_allow_html=True)


def callout(text: str):
    st.markdown(f'<div class="sp-callout">{text}</div>', unsafe_allow_html=True)


def footer():
    st.markdown(
        '<div class="sp-footer">SorghumPost -- built on Sorghumbase &amp; Phytozome data '
        '&middot; runs entirely on your machine, no data leaves your computer</div>',
        unsafe_allow_html=True
    )


# ── Export helpers ────────────────────────────────────────────

@st.cache_data
def to_excel_bytes(df: pd.DataFrame, sheet_name: str = "Data") -> bytes:
    """Serialize a DataFrame to a formatted .xlsx file in memory:
    bold header row, frozen header, auto-sized columns."""
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]

        header_fmt = workbook.add_format({
            "bold": True,
            "bg_color": "#fdece0",
            "border": 1,
            "border_color": "#e1e0d9",
        })
        for col_idx, col_name in enumerate(df.columns):
            worksheet.write(0, col_idx, col_name, header_fmt)
            try:
                max_len = max(
                    df[col_name].astype(str).map(len).max() if len(df) else 0,
                    len(str(col_name))
                ) + 2
            except Exception:
                max_len = len(str(col_name)) + 2
            worksheet.set_column(col_idx, col_idx, min(max_len, 45))

        worksheet.freeze_panes(1, 0)

    return buffer.getvalue()


def download_row(df: pd.DataFrame, filename_base: str, sheet_name: str = "Data", key_prefix: str = ""):
    """Render CSV + Excel download buttons side by side for the given DataFrame."""
    col1, col2 = st.columns(2)
    with col1:
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download CSV",
            data=csv,
            file_name=f"{filename_base}.csv",
            mime="text/csv",
            width="stretch",
            key=f"{key_prefix}_csv"
        )
    with col2:
        xlsx = to_excel_bytes(df, sheet_name=sheet_name)
        st.download_button(
            "⬇️ Download Excel",
            data=xlsx,
            file_name=f"{filename_base}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width="stretch",
            key=f"{key_prefix}_xlsx"
        )
