import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import data_processing

def create_graph_1(title, desc, cpv):
    df, mean_price, median_price = data_processing.search(title, desc, cpv, True)

    if df.empty:
        return None
    
    df["unit_price"] = df["amount"] / df["qty"]

    fig = px.histogram(
        df,
        x="unit_price",
        nbins=20,
        title="Розподіл цін за одиницю товару"
    )

    fig.add_vline(
        x=mean_price,
        line_color="orange",
        line_dash="dash",
        line_width=3
    )

    fig.add_vline(
        x=median_price,
        line_color="red",
        line_width=3
    )

    fig.update_traces(
    marker_color="#6495ED",
    marker_line_color="black",
    marker_line_width=1.2
    )

    fig.update_layout(
        bargap=0.15,
        title="Розподіл цін за одиницю товару",
        title_x=0.5,
        title_xanchor="center"
    )

    return fig






def create_graph_2(title, desc, cpv):
    df, mean_price, median_price = data_processing.search(title, desc, cpv, True)

    if df.empty:
        return None

    df["unit_price"] = df["amount"] / df["qty"]

    df["deviation"] = (
    (df["unit_price"] - median_price) / median_price * 100
    ).clip(lower=0)

    if median_price <= 0:
        return None

    def classify(deviation):
        if deviation <= 10:
            return "Нормальна ціна"
        elif deviation <= 30:
            return "Помірне відхилення"
        else:
            return "Аномальне відхилення"
    df["category"] = df["deviation"].apply(classify)

    categories = [
        "Нормальна ціна",
        "Помірне відхилення",
        "Аномальне відхилення"
    ]

    counts = (
        df["category"].value_counts().reindex(categories, fill_value=0)
    )

    fig = go.Figure(
        go.Pie(
            labels=counts.index,
            values=counts.values,
            hole=0.35,
            sort=False,
            marker=dict(
                colors=[
                    "#22A06B",
                    "#F5A623",
                    "#DC2626"
                ]
            ),
            textinfo="label+percent",
            hovertemplate=(
                "%{label}<br>"
                "Кількість тендерів: %{value}<br>"
                "Частка: %{percent}"
                "<extra></extra>"
            )
        )
    )

    fig.update_layout(
    title="Розподіл тендерів за завищенням цін",
    title_x=0.5,
    title_xanchor="center",
    title_y=0.96,
    title_yanchor="top",
    margin=dict(t=130),
    height=650
)
    fig.update_traces(
    domain=dict(
        x=[0.15, 0.85],
        y=[0.0, 0.85]
    )
)

    return fig





def create_graph_3(cpv):
    with open("tenders.json", "r", encoding="utf-8") as f:
        tenders = json.load(f)

    df = pd.DataFrame(tenders)
    df = df[df["cpv"] == cpv].copy()
    df = df[df["qty"] > 0].copy()

    df["unit_price"] = df["amount"] / df["qty"]

    top_10 = (
        df.nlargest(10, "unit_price")
        .sort_values("unit_price")
        .reset_index(drop=True)
    )

    def shorten(text, limit=35):
            text = str(text)
            return text if len(text) <= limit else text[:limit] + "..."

    top_10["label"] = (
        top_10["title"].apply(lambda x: shorten(x, 35))
        + " — "
        + top_10["buyer_name"].apply(lambda x: shorten(x, 25))
    )

    fig = go.Figure(
        go.Bar(
            x=top_10["unit_price"],
            y=list(range(len(top_10))),
            orientation="h",
            marker=dict(
                color="#6495ED",
                line=dict(color="black", width=1)
            ),
            text=top_10["unit_price"],
            texttemplate="%{text:,.0f} грн",
            textposition="outside",
            cliponaxis=False,
            customdata=top_10[
                ["title", "buyer_name", "id"]
            ].to_numpy(),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Замовник: %{customdata[1]}<br>"
                "ID: %{customdata[2]}<br>"
                "Ціна за одиницю: %{x:,.2f} грн"
                "<extra></extra>"
            )
        )
    )

    fig.update_yaxes(
        tickmode="array",
        tickvals=list(range(len(top_10))),
        ticktext=top_10["label"].tolist(),
        automargin=False,
        tickfont=dict(size=11)
    )

    fig.update_xaxes(
        tickangle=0,
        tickformat="~s",
        range=[0, top_10["unit_price"].max() * 1.2]
    )

    fig.update_layout(
    title="Топ-10 найдорожчих товарів",
    title_x=0.5,
    title_xanchor="center",
    title_y=0.96,
    title_yanchor="top",
    width=1100,
    height=600,
    margin=dict(l=320, r=100, t=100, b=70)
)

    return fig