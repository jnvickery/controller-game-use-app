import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from pathlib import Path
from plotly.subplots import make_subplots

data_path = Path("data/")

st.set_page_config(
    page_title="Controller and Game Usage",
    layout="wide",
    menu_items={"About": "..."},
)


@st.experimental_singleton
def load_data(csvfile):
    df = pd.read_csv(csvfile)
    if "hour" in df.columns:
        df["time"] = df["hour"].apply(lambda x: format_time(x))
    return df


# function to format integer as 12-hour time
@st.experimental_memo
def format_time(hour):
    if hour == 0:
        return "12AM"
    elif hour == 12:
        return "12PM"
    elif hour > 12:
        return f"{hour - 12}PM"
    else:
        return f"{hour}AM"


@st.experimental_memo
def convert_df(df):
    return df.to_csv(index=False).encode("utf-8")


st.title("CONTROLLER AND GAME USAGE")
st.subheader("August 2019 - March 2023")
st.markdown("**Jump tp section:**")
st.markdown(
    """[Average controller use per hour](#average-controller-use-per-hour)
    &emsp; [Controller checkouts by college](#controller-checkouts-by-college)
    &emsp; [Most circulated games](#most-circulated-games)"""
)
st.write("--------")

# 1. When are game controllers getting checked out
# subplots of use per hour
st.subheader("Average controller use per hour")

controller_use_csv = data_path.joinpath("controller_avg_per_hour_day.csv")
all_controller_use = load_data(controller_use_csv)

row0_0, row0_1, row0_2 = st.columns([0.5, 3, 0.5])
with row0_1:
    # select box for semesters
    semester_list = list(all_controller_use["semester"].unique())
    semester_list.sort()

    semester = st.selectbox(
        label="**Select a semester**",
        options=semester_list,
        index=0,
    )

try:
    use_fig_df = all_controller_use.loc[
        all_controller_use["semester"] == semester
    ].copy()

    use_fig = make_subplots(
        rows=4,
        cols=2,
        shared_yaxes="all",
        subplot_titles=use_fig_df["day_name"].unique(),
    )

    for i, var in enumerate(use_fig_df["day_name"].unique()):
        use_fig.add_trace(
            go.Scatter(
                x=use_fig_df.loc[use_fig_df["day_name"] == var, "time"],
                y=use_fig_df.loc[use_fig_df["day_name"] == var, "hour_avg"],
                name=var,
                showlegend=False,
            ),
            row=(i // 2) + 1,
            col=(i % 2) + 1,
        )

    use_fig.update_layout(
        title=f"Average number of controllers checked out per hour - {semester}",
        height=1000,
        width=1000,
    )
    st.plotly_chart(use_fig, theme="streamlit", use_container_width=True)

except ValueError:
    st.subheader((f"{semester} does not have enough data to show graphs."))

csv = convert_df(all_controller_use)
st.download_button(
    "Download all data as csv",
    csv,
    "average_controller_use_per_hour.csv",
    "text/csv",
    key="download-controller-use-csv",
)
st.dataframe(all_controller_use)

# 2. WHO IS CHECKING OUT CONTROLLERS
st.write("-----------")
st.subheader("Controller checkouts by college")

who_csv = data_path.joinpath("who_controllers_long.csv")
who_controllers = load_data(who_csv)

row1_0, row1_1, row1_2 = st.columns([0.5, 3, 0.5])
with row1_1:

    # select box for years
    year_list = list(who_controllers["year"].unique())
    year_list.sort()

    selected_year = st.selectbox(
        label="**Select a year**", options=year_list, index=0, key="controller-year"
    )

    who_fig_df = who_controllers.loc[who_controllers["year"] == selected_year].copy()
    who_fig_df.sort_values(
        by=["station_library", "num_checkouts"],
        ascending=[True, False],
        inplace=True,
    )

    who_fig = px.bar(
        who_fig_df,
        x="num_checkouts",
        y="college_division_name",
        orientation="h",
        barmode="group",
        color="station_library",
        # title="Who is checking out controllers",
        labels={
            "num_checkouts": "Number of checkouts",
        },
    )
    who_fig.update_layout(
        title=f"Controller checkouts by college - {selected_year}",
        yaxis={"categoryorder": "total descending", "autorange": "reversed"},
    )
    st.plotly_chart(who_fig, theme="streamlit", use_container_width=True)

    who_controllers.sort_values(by="num_checkouts", ascending=False, inplace=True)
    who_controllers.reset_index(inplace=True, drop=True)
    csv = convert_df(who_controllers)
    st.download_button(
        "Download all data as csv",
        csv,
        "controller_checkout_by_college.csv",
        "text/csv",
        key="download-controller-by-college",
    )

    st.dataframe(who_controllers)

# 3. WHAT GAMES CIRCULATE THE MOST
st.write("-----------")
st.subheader("Most circulated games")

games_csv = data_path.joinpath("what_games_long.csv")
what_games = load_data(games_csv)
what_games["short_title"] = what_games["title"].str.split(r"\/", expand=False).str[0]

st.write(
    f"**Total game checkouts for all years ({min(year_list)} to {max(year_list)}):**"
)

for lib in what_games["station_library"].drop_duplicates().sort_values():
    tot = what_games["num_checkouts"].loc[what_games["station_library"] == lib].sum()
    st.write(f"{lib} = {tot:,}")

row1_0, row1_1, row1_2 = st.columns([0.5, 3, 0.5])
with row1_1:

    selected_year = st.selectbox(
        label="**Select a year**", options=year_list, index=0, key="game-year"
    )

    # display_number = st.number_input("Display top", value=20)
    # display_number = display_number - 0.5

    game_fig_df = what_games.loc[what_games["year"] == selected_year].copy()
    game_fig_df.sort_values(
        by=["station_library", "num_checkouts"], ascending=[True, False], inplace=True
    )

    game_fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes="all",
        vertical_spacing=0.10,
        subplot_titles=game_fig_df["station_library"].unique(),
    )

    for i, var in enumerate(game_fig_df["station_library"].unique()):
        game_fig.add_trace(
            go.Bar(
                y=game_fig_df.loc[game_fig_df["station_library"] == var, "short_title"],
                x=game_fig_df.loc[
                    game_fig_df["station_library"] == var, "num_checkouts"
                ],
                name=var,
                showlegend=False,
                orientation="h",
            ),
            row=i + 1,
            col=1,
        )
        # game_fig.update_yaxes(autorange="reversed", row=i + 1, col=1)
        game_fig.update_yaxes(range=[19.5, -0.5], row=i + 1, col=1)
        # game_fig.update_yaxes(range=[display_number, -0.5], row=i + 1, col=1)
        game_fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="lightgrey")

    game_fig.update_layout(
        title=f"Top 20 circulated games - {selected_year}",
        height=1200,
        xaxis_showticklabels=True
        # yaxis=dict(autorange="reversed")
        # width=2000,
    )

    st.plotly_chart(game_fig, theme="streamlit", use_container_width=True)

    csv = convert_df(what_games)
    st.download_button(
        "Download all data as csv",
        csv,
        "game_checkouts.csv",
        "text/csv",
        key="game-download-csv",
    )

    st.dataframe(what_games)
