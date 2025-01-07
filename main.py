import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np



st.title('NBA Player Stats')

st.markdown("""
Application web scrapes NBA player stats
* **Data Source:** [Basketball-reference.com](https://www.basketball-reference.com/)
""")

st.sidebar.header("User Input")
selected_year = st.sidebar.selectbox("Year", list(reversed(range(1950, 2025))))


# Web Scraping of NBA player stats
# cache improves efficiency and scrapes the website less
@st.cache_data
def data(year):
    url = "https://www.basketball-reference.com/leagues/NBA_" + str(year) + "_per_game.html"
    html = pd.read_html(url, header=0)
    df = html[0]
    raw = df.drop(df[df.Age == 'Age'].index)  # Data Cleaning - Deletes repeating headers in content
    raw = raw.fillna(0)
    playerstats = raw.drop(['Rk'], axis=1)
    return playerstats


playerstats = data(selected_year)

# Sidebar: Team Selection
sorted_unique_team = sorted(playerstats.Team.unique(), key=str)
selected_team = st.sidebar.multiselect('Team', sorted_unique_team, sorted_unique_team)

# Sidebar: Position
unique_pos = ["C", "PF", "SF", "PG", "SG"]
selected_pos = st.sidebar.multiselect("Position", unique_pos, unique_pos)

# Sidebar: Player
sorted_unique_name = sorted(playerstats.Player.unique(), key=str)
selected_player = st.sidebar.multiselect('Player', sorted_unique_name, sorted_unique_name[:0])

# Filtering Data
pos = (playerstats.Pos.isin(selected_pos))
team = (playerstats.Team.isin(selected_team))
player = (playerstats.Player.isin(selected_player))

df_selected_team = playerstats[(team & pos) | player]

st.header("Display Player Stats of the Selected Team(s)")
st.write("Data Dimension: " + str(df_selected_team.shape[0]) + " rows and " + str(df_selected_team.shape[1])+ " columns.")

st.dataframe(df_selected_team)


# Download NBA player stats data
# https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="playerstats.csv">Download CSV File</a>'
    return href

st.markdown(filedownload(df_selected_team), unsafe_allow_html=True)

df_selected_team.to_csv("output.csv", index=False)
df_PER = pd.read_csv("output.csv")
df = df_PER.replace(' ', ',')

plr = df["Player"]
pts = df["PTS"]
trb = df["TRB"]
ast = df["AST"]
stl = df["STL"]
blk = df["BLK"]
fga = df["FGA"]
fg = df["FG"]
fta = df["FTA"]
ft = df["FT"]
tov = df["TOV"]

# Heatmap
if st.button('Intercorrelation Heatmap'):
    st.header('Intercorrelation Matrix Heatmap')

    corr = df.corr()
    mask = np.zeros_like(corr)
    mask[np.triu_indices_from(mask)] = True
    with sns.axes_style("white"):
        f, ax = plt.subplots(figsize=(7, 5))
        ax = sns.heatmap(corr, mask=mask, vmax=1, vmin=0, square=True)
    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.pyplot()

# Efficiency ratings

if st.button("Efficiency Rating - Have 1 player in the Dataframe"):
    per = (pts + trb + ast + stl + blk) - (fga - fg) - (fta - ft) - tov
    st.header(f"Approximate Efficiency of {plr[0]}: {per[0]}")
    st.write("NBA Efficiency Formula = Points + Rebounds + Steals + Assists + Blocks - Turnovers - Missed Shots")

# Bar Plot
if st.button("Bar Plot"):
    st.header("Bar Plot")

    barWidth = 0.1
    fig = plt.subplots(figsize=(12, 8))

    plr1 = [pts[0], ast[0], trb[0], stl[0], blk[0]]
    plr2 = [pts[1], ast[1], trb[1], stl[1], blk[1]]
    plr3 = [pts[2], ast[2], trb[2], stl[2], blk[2]]
    plr4 = [pts[3], ast[3], trb[3], stl[3], blk[3]]
    plr5 = [pts[4], ast[4], trb[4], stl[4], blk[4]]

    br1 = np.arange(len(plr1))
    br2 = [x + barWidth for x in br1]
    br3 = [x + barWidth for x in br2]
    br4 = [x + barWidth for x in br3]
    br5 = [x + barWidth for x in br4]

    plt.bar(br1, plr1, color='r', width=barWidth,
            edgecolor='grey', label=f'{plr[0]}')
    plt.bar(br2, plr2, color='g', width=barWidth,
            edgecolor='grey', label=f'{plr[1]}')
    plt.bar(br3, plr3, color='b', width=barWidth,
            edgecolor='grey', label=f'{plr[2]}')
    plt.bar(br4, plr4, color='y', width=barWidth,
            edgecolor='grey', label=f'{plr[3]}')
    plt.bar(br5, plr5, color='m', width=barWidth,
            edgecolor='grey', label=f'{plr[4]}')

    plt.xlabel('Branch', fontweight='bold', fontsize=15)
    plt.ylabel('Students passed', fontweight='bold', fontsize=15)
    plt.xticks([r + barWidth for r in range(len(plr1))],
               ['PTS', 'AST', 'REB', 'STL', 'BLK'])

    plt.legend()
    st.pyplot()



