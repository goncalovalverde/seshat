import plotly.graph_objects as go
import statsmodels.api as sm
import datetime


def add_trendline(df, fig, column):
    # This is needed because we can't use DateTimeIndex as input for OLS
    df["serialtime"] = [(d - datetime.datetime(1970, 1, 1)).days for d in df.index]
    df["bestfit"] = (
        sm.OLS(df[column], sm.add_constant(df["serialtime"])).fit().fittedvalues
    )
    fig = fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["bestfit"],
            name="Trend",
            mode="lines",
            line={"dash": "dash"},
            marker_color="red",
        )
    )
    return fig


def add_percentile(df, fig):
    percentile = df.quantile([0.5, 0.85, 0.95])

    for key in percentile.keys():
        position = percentile[key]
        label = f"{int(key*100)}%"

        fig = fig.add_shape(
            type="line",
            yref="paper",
            x0=position,
            y0=0,
            x1=position,
            y1=0.95,
            line_dash="dash",
        )

        fig = fig.add_annotation(
            x=position, yref="paper", y=1, showarrow=False, text=label
        )
    return fig


def add_range_buttons(fig):
    fig.update_xaxes(
        rangeslider_visible=False,
        rangeselector=dict(
            buttons=list(
                [
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all"),
                ]
            )
        ),
    )
    return fig