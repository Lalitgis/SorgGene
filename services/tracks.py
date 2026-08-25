"""
SorghumPost - Gene Track Visualizations
===========================================
Builds the Plotly "genome track" figure used by the Gene Proximity and
Cross-Genotype Comparison tabs: genes drawn as horizontal bars along a
position axis, with the query position and search window marked.
"""

import plotly.graph_objects as go

from services.theme import LOCATION_COLORS, GRAY_OTHER, apply_plotly_layout, INK_MUTED


def _hover_text(row):
    return (
        f"<b>{row['Gene ID']}</b><br>"
        f"{row['Chromosome']}:{row['Start (bp)']:,}-{row['End (bp)']:,}<br>"
        f"Strand: {row['Strand']} &nbsp; Biotype: {row.get('Biotype', 'n/a')}<br>"
        f"{row['Location']}"
    )


def single_track_figure(genes_df, position: int, window_bp: int, row_label: str = "BTx623"):
    """One-row gene track for a single genotype (Tab 1)."""
    fig = go.Figure()

    fig.add_vrect(
        x0=position - window_bp, x1=position + window_bp,
        fillcolor="#eda100", opacity=0.08, line_width=0,
    )
    fig.add_vline(
        x=position, line_width=2, line_dash="dash", line_color="#eb6834",
        annotation_text="query position", annotation_position="top",
        annotation_font_color="#eb6834", annotation_font_size=11,
    )

    for _, row in genes_df.iterrows():
        color = LOCATION_COLORS.get(row["Location"], GRAY_OTHER)
        fig.add_trace(go.Bar(
            x=[row["End (bp)"] - row["Start (bp)"]],
            y=[row_label],
            base=[row["Start (bp)"]],
            orientation="h",
            marker=dict(color=color, line=dict(color="white", width=1)),
            width=0.5,
            hovertext=_hover_text(row),
            hoverinfo="text",
            showlegend=False,
        ))

    _add_location_legend(fig, ["Overlaps marker", "Near marker"])
    apply_plotly_layout(fig, height=190, showlegend=True)
    fig.update_yaxes(showticklabels=True, title=None)
    fig.update_xaxes(title="Position (bp)", tickformat=",", separatethousands=True)
    fig.update_layout(barmode="overlay", bargap=0.4)
    return fig


def region_track_figure(genes_df, region_start: int, region_end: int, row_label: str = "BTx623"):
    """One-row gene track for an explicit pasted region (Tab 1, region-paste mode).
    Unlike single_track_figure there's no single query point -- just the
    pasted region's boundaries, shaded across the track."""
    fig = go.Figure()

    fig.add_vrect(
        x0=region_start, x1=region_end,
        fillcolor="#eda100", opacity=0.10, line_width=0,
    )

    for _, row in genes_df.iterrows():
        color = LOCATION_COLORS.get(row["Location"], GRAY_OTHER)
        fig.add_trace(go.Bar(
            x=[row["End (bp)"] - row["Start (bp)"]],
            y=[row_label],
            base=[row["Start (bp)"]],
            orientation="h",
            marker=dict(color=color, line=dict(color="white", width=1)),
            width=0.5,
            hovertext=_hover_text(row),
            hoverinfo="text",
            showlegend=False,
        ))

    _add_location_legend(fig, ["Fully within region", "Overlaps region boundary"])
    apply_plotly_layout(fig, height=190, showlegend=True)
    fig.update_yaxes(showticklabels=True, title=None)
    fig.update_xaxes(title="Position (bp)", tickformat=",", separatethousands=True)
    fig.update_layout(barmode="overlay", bargap=0.4)
    return fig


def multi_track_figure(genes_df, position: int, window_bp: int, genotype_order):
    """Multi-row gene track, one row per genotype (Tab 3)."""
    fig = go.Figure()

    fig.add_vrect(
        x0=position - window_bp, x1=position + window_bp,
        fillcolor="#eda100", opacity=0.08, line_width=0,
    )
    fig.add_vline(
        x=position, line_width=2, line_dash="dash", line_color="#eb6834",
        annotation_text="query position", annotation_position="top",
        annotation_font_color="#eb6834", annotation_font_size=11,
    )

    for _, row in genes_df.iterrows():
        color = LOCATION_COLORS.get(row["Location"], GRAY_OTHER)
        fig.add_trace(go.Bar(
            x=[row["End (bp)"] - row["Start (bp)"]],
            y=[row["Genotype"]],
            base=[row["Start (bp)"]],
            orientation="h",
            marker=dict(color=color, line=dict(color="white", width=1)),
            width=0.55,
            hovertext=_hover_text(row),
            hoverinfo="text",
            showlegend=False,
        ))

    _add_location_legend(fig, ["Overlaps marker", "Near marker"])
    apply_plotly_layout(fig, height=110 + 55 * len(genotype_order), showlegend=True)
    fig.update_yaxes(
        categoryorder="array", categoryarray=list(reversed(genotype_order)), title=None
    )
    fig.update_xaxes(title="Position (bp)", tickformat=",", separatethousands=True)
    fig.update_layout(barmode="overlay", bargap=0.35)
    return fig


def _add_location_legend(fig, labels):
    """Invisible-x dummy traces just to populate a clean legend, restricted
    to the labels relevant to the calling chart (LOCATION_COLORS holds
    entries for multiple chart types)."""
    for label in labels:
        color = LOCATION_COLORS.get(label, GRAY_OTHER)
        fig.add_trace(go.Bar(
            x=[None], y=[None], marker=dict(color=color), name=label, showlegend=True,
        ))
