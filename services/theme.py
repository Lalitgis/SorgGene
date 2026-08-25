"""
SorghumPost - Theme & Color System
=====================================
Central palette for the whole app. Colors follow the validated categorical
order from the design system's reference palette: fixed hue slots, assigned
by role and never re-cycled per filter, so the same entity always renders
the same color everywhere in the app.
"""

# ── Brand ─────────────────────────────────────────────────────
BRAND_PRIMARY = "#eb6834"     # harvest orange -- matches .streamlit/config.toml
BRAND_PRIMARY_DARK = "#d95926"
BRAND_GREEN = "#008300"       # sorghum leaf green, for secondary accents

# ── Categorical palette (fixed slot order -- do not reorder) ───
CATEGORICAL = {
    "blue":    "#2a78d6",
    "orange":  "#eb6834",
    "aqua":    "#1baf7a",
    "yellow":  "#eda100",
    "magenta": "#e87ba4",
    "green":   "#008300",
    "violet":  "#4a3aa7",
    "red":     "#e34948",
}
CATEGORICAL_ORDER = ["blue", "orange", "aqua", "yellow", "magenta", "green", "violet", "red"]
CATEGORICAL_SEQUENCE = [CATEGORICAL[k] for k in CATEGORICAL_ORDER]
GRAY_OTHER = "#898781"        # "Other" bucket -- never a categorical slot

# ── Entity -> fixed slot assignments (never reassigned by filters) ──
GENOTYPE_COLORS = {
    "BTx623": CATEGORICAL["blue"],
    "Tx2783": CATEGORICAL["orange"],
    "Rio":    CATEGORICAL["aqua"],
}

BIOTYPE_ORDER = [
    "protein_coding", "rRNA", "tRNA", "snoRNA", "pre_miRNA", "snRNA",
]
BIOTYPE_COLORS = {b: CATEGORICAL[CATEGORICAL_ORDER[i]] for i, b in enumerate(BIOTYPE_ORDER)}
BIOTYPE_OTHER_LABEL = "Other"
BIOTYPE_COLORS[BIOTYPE_OTHER_LABEL] = GRAY_OTHER

LOCATION_COLORS = {
    "Overlaps marker": CATEGORICAL["green"],
    "Near marker": CATEGORICAL["blue"],
    "Fully within region": CATEGORICAL["green"],
    "Overlaps region boundary": CATEGORICAL["blue"],
}

# ── Sequential ramp (single hue, light -> dark) for magnitude/density ──
SEQUENTIAL_BLUE = [
    "#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b",
]

# ── Status palette (fixed -- never themed, never reused as series color) ──
STATUS = {
    "good":     "#0ca30c",
    "warning":  "#fab219",
    "serious":  "#ec835a",
    "critical": "#d03b3b",
}

# ── Chart chrome & ink ───────────────────────────────────────────
INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRIDLINE = "#e1e0d9"
CHART_SURFACE = "#fcfcfb"

PLOTLY_FONT = dict(family="system-ui, -apple-system, 'Segoe UI', sans-serif", color=INK_PRIMARY)


def apply_plotly_layout(fig, height=None, showlegend=True):
    """Apply consistent, theme-aware chrome to a Plotly figure so it blends
    into the Streamlit surface in both light and dark mode."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=PLOTLY_FONT,
        margin=dict(l=10, r=10, t=40, b=10),
        showlegend=showlegend,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    fig.update_xaxes(gridcolor=GRIDLINE, zerolinecolor=GRIDLINE, linecolor=GRIDLINE)
    fig.update_yaxes(gridcolor=GRIDLINE, zerolinecolor=GRIDLINE, linecolor=GRIDLINE)
    if height:
        fig.update_layout(height=height)
    return fig


def biotype_color_map(biotypes):
    """Return a {biotype: color} map for the given biotypes, folding anything
    outside the canonical order into the shared 'Other' gray slot."""
    result = {}
    for b in biotypes:
        result[b] = BIOTYPE_COLORS.get(b, GRAY_OTHER)
    return result
