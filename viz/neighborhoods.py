import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def plot_neighborhood_case_bubbles(neighborhood_counts: pd.DataFrame) -> go.Figure:
    figure = px.scatter_mapbox(
        neighborhood_counts,
        lat="latitude",
        lon="longitude",
        size="case_count",
        color="case_count",
        hover_name="neighborhood",
        hover_data={
            "community": True,
            "case_count": True,
            "latitude": False,
            "longitude": False,
        },
        size_max=52,
        zoom=10.6,
        center={"lat": 44.97, "lon": -93.27},
        mapbox_style="open-street-map",
        color_continuous_scale="YlOrRd",
        title="Minneapolis unique case numbers by neighborhood",
    )
    figure.update_layout(
        margin={"l": 0, "r": 0, "t": 48, "b": 0},
        coloraxis_colorbar_title="Cases",
        mapbox_accesstoken=None,
    )
    return figure
