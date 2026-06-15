import pandas as pd
import streamlit as st
import plotly.express as px

# Title
st.title("Atlantic France ")

# Loading Dataset
data=pd.read_csv("Atlantic_France_Processed.csv")

# Convert Date column to datetime
data["date"]=pd.to_datetime(data["date"],errors="coerce")

# # Display the first 5 rows of the dataset
st.write(data.head())

# Sidebar
st.sidebar.header("Dashboard Filters")

# Date Range Selector
start_date,end_date=st.sidebar.date_input(
    "Select Date Range",
    (
        data["date"].min(),
        data["date"].max()
     )
)

# Rank type filter
Rank_filter=st.sidebar.multiselect(
    "Rank Tier",
    options=data["rank_tier"].unique(),
    default=data["rank_tier"].unique()
)

# Album type filter
Album_filter=st.sidebar.multiselect(
    "Album Type",
    options=data["album_type"].unique(),
    default=data["album_type"].unique()
)

# Explicit content toggle
Explicit_filter=st.sidebar.radio(
    "Explicit content",
    ["ALL","Explicit","Clean"]
)

# Applying Filters
filtered=data.copy()

# Date Filter
filtered=filtered[
    (filtered["date"]>=pd.to_datetime(start_date))
    &
    (filtered["date"]<=pd.to_datetime(end_date))

]

# Rank Filter
filtered=filtered[
    filtered["rank_tier"].isin(Rank_filter)
]

# Album Filter
filtered=filtered[
    filtered["album_type"].isin(Album_filter)
]

# Explicit Toggle
if Explicit_filter=="Explicit":
    filtered=filtered[
        filtered["is_explicit"]==True
        ]
elif Explicit_filter=="Clean":
    filtered=filtered[
        filtered["is_explicit"]==False
    ]

# KPI Cards
col1,col2,col3,col4=st.columns(4)

with col1:
    st.metric(
        "Songs",
        filtered["song"].nunique()
    )

with col2:
    st.metric(
        "Artists",
        filtered["artist"].nunique()
    )

with col3:
    st.metric(
        "Avg Popularity",
        round(
            filtered["popularity"].mean(),
            1
        )
    )

with col4:
    st.metric(
        "Explicit %",
        round(
            filtered["is_explicit"].mean()*100,
            1
        )
    )


# CONTENT COMPLIANCE SUMMARY PANEL
st.subheader("Content Compliance Summary")

total_songs=len(filtered)
explicit_songs=filtered["is_explicit"].sum()
clean_songs=total_songs - explicit_songs

if total_songs >0:
    compliance_score =(
        clean_songs/total_songs
    )*100
else:
    compliance_score=0

c1,c2,c3=st.columns(3)
with c1:
    st.metric(
        "Clean Songs",
        clean_songs
    )
with c2:
    st.metric(
        "Explicit Songs",
        explicit_songs
    )
with c3:
    st.metric(
        "Compliance %",
        f"{compliance_score:.1f}%"
    )

# Tab Section
tab1,tab2,tab3,tab4,tab5=st.tabs([
    "Overview Analysis", 
    "Content Analysis",
    "Album Analysis",
    "Duration Analysis",
    "Data Explorer"
])

# TAB 1 - OVERVIEW
with tab1:
    st.subheader("Dataset Overview")
    st.dataframe(filtered.head())

# TAB 2 - CONTENT ANALYSIS
with tab2:
    st.subheader("Explicit VS Clean Content Analysis")

    content_counts=(
        filtered["is_explicit"].value_counts().reset_index()
    )
    content_counts.columns=[
        "Content Type",
        "Count"
    ]

    content_counts["Content Type"]=(
        content_counts["Content Type"].map({
            True:"Explicit",
            False:"Clean"
        })
    )

    fig=px.pie(
        content_counts,
        names="Content Type",
        values="Count",
        title="Explicit vs Clean Songs"
    )
    st.plotly_chart(
        fig,
        use_container_width =True
    )
 # Rank Tier Content Comparison
st.subheader("Rank Tier Content Comparison")

rank_explicit = (
        filtered.groupby("rank_tier")["is_explicit"]
        .mean()
        .reset_index()
    )

rank_explicit["is_explicit"] = (
        rank_explicit["is_explicit"] * 100
    )

fig2 = px.bar(
        rank_explicit,
        x="rank_tier",
        y="is_explicit",
        title="Explicit Content % by Rank Tier",
        labels={
            "rank_tier": "Rank Tier",
            "is_explicit": "Explicit %"
        }
    )

st.plotly_chart(
        fig2,
        use_container_width=True
    )
# TAB 3 - ALBUM ANALYSIS
with tab3:
    st.subheader("Album Format Distribution")

    album_counts=(
        filtered["album_type"].value_counts().reset_index()
    )

    album_counts.columns=[
        "Album Type",
        "Count"
    ]

    fig=px.bar(
        album_counts,
        x="Album Type",
        y="Count",
        title="Album Type Distribution"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# TAB 4 - DURATION ANALYSIS
with tab4:
    st.subheader("Song Duration Distribution")

    fig=px.histogram(
        filtered,
        x="duration_min",
        nbins=20,
        title="Song Duration Histogram"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# TAB 5 - DATA EXPLORER
with tab5:
    st.subheader("Full Dataset")
    st.dataframe(
        filtered,
        use_container_width=True
    )

    st.download_button(
        "Download Filtered Data",
        filtered.to_csv(index=False),
        "filtered_data.csv",
        "text/csv"
    )