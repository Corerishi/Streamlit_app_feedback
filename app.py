import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import requests

st.set_page_config(page_title="GATEWAYS 2025", page_icon="🎓", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("Participants.csv")

df = load_data()

st.sidebar.title("Filters")
events  = st.sidebar.multiselect("Event",      df["Event Name"].unique(), default=df["Event Name"].unique())
states  = st.sidebar.multiselect("State",      df["State"].unique(),      default=df["State"].unique())
ev_type = st.sidebar.multiselect("Event Type", df["Event Type"].unique(), default=df["Event Type"].unique())

fdf = df[
    df["Event Name"].isin(events) &
    df["State"].isin(states) &
    df["Event Type"].isin(ev_type)
]

st.title(" GATEWAYS 2025")
st.caption("National Level Fest — Participation Dashboard | CHRIST (Deemed to be University)")
st.markdown("---")

avg = round(fdf["Rating"].mean(), 2) if not fdf.empty else 0
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Participants", len(fdf))
c2.metric("Colleges", fdf["College"].nunique())
c3.metric("States", fdf["State"].nunique())
c4.metric("Avg Rating", f"{avg} ")

st.markdown("---")

if fdf.empty:
    st.warning("No data for selected filters.")
    st.stop()

tab1, tab2, tab3 = st.tabs(["Geographic Analysis", "Events & Colleges", "Feedback & Ratings"])

with tab1:

    st.subheader("State-wise Participants on India Map")

    state_counts = fdf["State"].value_counts().reset_index()
    state_counts.columns = ["State", "Participants"]

    @st.cache_data
    def get_geojson():
        url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
        return requests.get(url, timeout=10).json()

    try:
        geojson = get_geojson()
        fig_map = px.choropleth(
            state_counts,
            geojson=geojson,
            featureidkey="properties.ST_NM",
            locations="State",
            color="Participants",
            color_continuous_scale="Purples",
            hover_name="State",
            title="Number of Participants by State"
        )
        fig_map.update_geos(fitbounds="locations", visible=False)
        fig_map.update_layout(margin=dict(l=0, r=0, t=40, b=0), height=500)
        st.plotly_chart(fig_map, use_container_width=True)

    except Exception:
        st.warning("Map could not load. Showing bar chart instead.")

    st.subheader("State-wise Participation Count")
    fig_state = px.bar(
        state_counts.sort_values("Participants", ascending=False),
        x="State", y="Participants",
        color="State", text="Participants",
        title="Participants per State"
    )
    fig_state.update_traces(textposition="outside")
    fig_state.update_layout(showlegend=False, height=380)
    st.plotly_chart(fig_state, use_container_width=True)

with tab2:

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Event-wise Participation")
        event_counts = fdf["Event Name"].value_counts().reset_index()
        event_counts.columns = ["Event Name", "Count"]

        fig_event = px.bar(
            event_counts, x="Event Name", y="Count",
            color="Count", color_continuous_scale="Teal",
            text="Count", title="Participants per Event"
        )
        fig_event.update_traces(textposition="outside")
        fig_event.update_layout(showlegend=False, height=380, xaxis_tickangle=-20)
        st.plotly_chart(fig_event, use_container_width=True)

        st.subheader("Individual vs Group Events")
        type_counts = fdf["Event Type"].value_counts().reset_index()
        type_counts.columns = ["Type", "Count"]
        fig_type = px.pie(
            type_counts, names="Type", values="Count",
            color_discrete_sequence=["#667eea", "#764ba2"],
            hole=0.4, title="Event Type Split"
        )
        fig_type.update_traces(textinfo="percent+label")
        st.plotly_chart(fig_type, use_container_width=True)

    with col_b:
        st.subheader("College-wise Participation (Top 10)")
        college_counts = fdf["College"].value_counts().head(10).reset_index()
        college_counts.columns = ["College", "Count"]

        fig_col = px.bar(
            college_counts, x="Count", y="College", orientation="h",
            color="Count", color_continuous_scale="Sunset",
            text="Count", title="Top 10 Colleges"
        )
        fig_col.update_traces(textposition="outside")
        fig_col.update_layout(yaxis={"categoryorder": "total ascending"}, height=420)
        st.plotly_chart(fig_col, use_container_width=True)

        st.subheader("Amount Collected per Event")
        amt = fdf.groupby("Event Name")["Amount Paid"].sum().reset_index()
        amt.columns = ["Event Name", "Total Amount"]
        fig_amt = px.pie(
            amt, names="Event Name", values="Total Amount",
            color_discrete_sequence=px.colors.sequential.Plasma_r,
            title="Revenue Share by Event"
        )
        fig_amt.update_traces(textinfo="percent+label")
        st.plotly_chart(fig_amt, use_container_width=True)

with tab3:

    wc_col, rt_col = st.columns([3, 2])

    with wc_col:
        st.subheader("Feedback Word Cloud")
        text = " ".join(fdf["Feedback on Fest"].dropna().astype(str))
        wc = WordCloud(
            width=800, height=380,
            background_color="white",
            colormap="cool",
            max_words=100
        ).generate(text)

        fig_wc, ax = plt.subplots(figsize=(9, 4))
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig_wc)

    with rt_col:
        st.subheader("Ratings Distribution")
        rating_counts = fdf["Rating"].value_counts().sort_index().reset_index()
        rating_counts.columns = ["Rating", "Count"]

        fig_r = px.bar(
            rating_counts, x="Rating", y="Count",
            color="Count", color_continuous_scale="YlOrRd",
            text="Count", title="How participants rated the fest"
        )
        fig_r.update_traces(textposition="outside")
        fig_r.update_layout(
            xaxis=dict(tickvals=[3, 4, 5], ticktext=["3 ★", "4 ★", "5 ★"]),
            height=300
        )
        st.plotly_chart(fig_r, use_container_width=True)

    st.subheader("Most Common Feedback")
    fb_counts = fdf["Feedback on Fest"].value_counts().reset_index()
    fb_counts.columns = ["Feedback", "Count"]
    fig_fb = px.bar(
        fb_counts, x="Count", y="Feedback", orientation="h",
        color="Count", color_continuous_scale="Blues",
        title="Feedback Frequency"
    )
    fig_fb.update_layout(yaxis={"categoryorder": "total ascending"}, height=380)
    st.plotly_chart(fig_fb, use_container_width=True)

    st.subheader("Average Rating per Event")
    avg_event = fdf.groupby("Event Name")["Rating"].mean().round(2).reset_index()
    avg_event.columns = ["Event Name", "Avg Rating"]
    fig_avg = px.bar(
        avg_event.sort_values("Avg Rating", ascending=False),
        x="Event Name", y="Avg Rating",
        color="Avg Rating", color_continuous_scale="RdYlGn",
        range_color=[1, 5], text="Avg Rating",
        title="Average Rating by Event"
    )
    fig_avg.update_traces(textposition="outside")
    fig_avg.update_layout(yaxis=dict(range=[0, 5.5]), height=360)
    st.plotly_chart(fig_avg, use_container_width=True)

st.markdown("---")
st.caption("Made for GATEWAYS 2025 · CHRIST (Deemed to be University)")
