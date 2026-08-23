import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def plot_neighborhood_case_bubbles(
    neighborhood_counts: pd.DataFrame,
    neighborhoods: dict | None = None,
) -> go.Figure:
    figure = px.choropleth_map(
        neighborhood_counts,
        geojson=neighborhoods,
        locations="neighborhood",
        featureidkey="properties.BDNAME",
        color="case_count",
        hover_name="neighborhood",
        hover_data={"community": True, "case_count": True},
        labels={"case_count": "Unique cases", "community": "Community"},
        color_continuous_scale=[
            "#fff7ec",
            "#fee8c8",
            "#fdbb84",
            "#fc8d59",
            "#e34a33",
            "#b30000",
        ],
        opacity=0.82,
        zoom=10.9,
        center={"lat": 44.972, "lon": -93.266},
        map_style="carto-positron",
        title="Minneapolis unique cases by neighborhood",
        subtitle="Fill is case volume. Larger dots mark higher-count neighborhoods.",
        height=860,
        width=980,
    )
    dots = px.scatter_map(
        neighborhood_counts,
        lat="latitude",
        lon="longitude",
        size="case_count",
        hover_name="neighborhood",
        hover_data={
            "community": True,
            "case_count": True,
            "latitude": False,
            "longitude": False,
        },
        size_max=22,
        zoom=10.9,
        center={"lat": 44.972, "lon": -93.266},
        map_style="carto-positron",
    )
    dots.update_traces(
        marker={
            "color": "rgba(255,255,255,0.62)",
            "sizemin": 4,
            "sizemode": "area",
        },
        showlegend=False,
    )
    figure.add_traces(dots.data)
    figure.update_layout(
        margin={"l": 0, "r": 0, "t": 72, "b": 0},
        paper_bgcolor="#f6f3ee",
        font={"family": "Georgia, 'Times New Roman', serif", "color": "#2b2118"},
        title={"x": 0.02, "xanchor": "left"},
        coloraxis_colorbar={
            "title": "Unique cases",
            "len": 0.55,
            "y": 0.38,
            "thickness": 12,
            "outlinewidth": 0,
        },
        map_bounds={"west": -93.36, "east": -93.18, "south": 44.88, "north": 45.07},
    )
    figure.update_traces(
        marker_line_width=0.7,
        marker_line_color="#5c4033",
        selector={"type": "choroplethmap"},
    )
    return figure
