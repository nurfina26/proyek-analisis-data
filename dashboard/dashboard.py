import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Dashboard Kualitas Udara Beijing", layout="wide")
st.title("Dashboard Kualitas Udara Beijing (2013-2017)")
st.markdown("Analisis PM2.5 berdasarkan data dari 12 stasiun pemantau di Beijing. Data sudah dibersihkan.")

@st.cache_data
def load_data():
    df = pd.read_csv("dashboard/main_data.csv")
    if "datetime" not in df.columns:
        df["datetime"] = pd.to_datetime(df[["year", "month", "day", "hour"]])
    if "season" not in df.columns:
        def get_season(m):
            if m in [12, 1, 2]:
                return "Dingin"
            elif m in [3, 4, 5]:
                return "Semi"
            elif m in [6, 7, 8]:
                return "Panas"
            else:
                return "Gugur"
        df["season"] = df["month"].apply(get_season)
    return df

df = load_data()

st.sidebar.header("Filter")
stations = sorted(df["station"].unique())
selected_stations = st.sidebar.multiselect("Pilih Stasiun", stations, default=stations)
selected_season = st.sidebar.multiselect("Pilih Musim", ["Dingin", "Semi", "Panas", "Gugur"], default=["Dingin", "Semi", "Panas", "Gugur"])
year_min, year_max = int(df["year"].min()), int(df["year"].max())
selected_years = st.sidebar.slider("Rentang Tahun", year_min, year_max, (year_min, year_max))

filtered = df[
    (df["station"].isin(selected_stations)) &
    (df["season"].isin(selected_season)) &
    (df["year"] >= selected_years[0]) &
    (df["year"] <= selected_years[1])
]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Rata-rata PM2.5", f"{filtered['PM2.5'].mean():.1f} ug/m3")
col2.metric("Rata-rata PM10", f"{filtered['PM10'].mean():.1f} ug/m3")
col3.metric("Stasiun Terburuk", filtered.groupby("station")["PM2.5"].mean().idxmax())
col4.metric("Total Data", f"{len(filtered):,}")

st.divider()

st.subheader("1. Bagaimana tren PM2.5 dan PM10 dari 2013-2017?")
yearly = filtered.groupby("year")[["PM2.5", "PM10"]].mean()
fig1, ax1 = plt.subplots(figsize=(10, 5))
ax1.plot(yearly.index, yearly["PM2.5"], marker="o", label="PM2.5")
ax1.plot(yearly.index, yearly["PM10"], marker="s", label="PM10")
ax1.set_title("Tren Rata-rata PM2.5 dan PM10 di Beijing (2013-2017)")
ax1.set_xlabel("Tahun")
ax1.set_ylabel("Konsentrasi")
ax1.legend()
ax1.grid(True)
st.pyplot(fig1)
st.markdown("**Insight:** PM2.5 dan PM10 sempat turun sampai terendah di 2016, lalu naik lagi di 2017. PM10 selalu lebih tinggi dari PM2.5.")

st.subheader("2. Faktor cuaca apa yang paling berpengaruh ke PM2.5?")
cols = ["PM2.5", "TEMP", "DEWP", "PRES", "WSPM", "RAIN"]
corr = filtered[cols].corr()
fig2, ax2 = plt.subplots(figsize=(8, 5))
sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", ax=ax2)
ax2.set_title("Korelasi PM2.5 dengan Faktor Cuaca")
st.pyplot(fig2)
st.markdown("**Insight:** Kecepatan angin (WSPM) paling berpengaruh dengan korelasi -0.27. Angin kencang membantu menurunkan polusi.")

st.subheader("3. Stasiun mana yang paling buruk dan musim apa yang paling parah?")
fig3, ax3 = plt.subplots(figsize=(12, 6))
sns.barplot(data=filtered, x="station", y="PM2.5", hue="season", errorbar=None, ax=ax3)
ax3.set_title("Rata-rata PM2.5 per Stasiun dan Musim")
ax3.set_xlabel("Stasiun")
ax3.set_ylabel("Rata-rata PM2.5")
ax3.tick_params(axis="x", rotation=30)
st.pyplot(fig3)
st.markdown("**Insight:** Polusi PM2.5 paling parah di musim Dingin, paling tinggi di Wanshouxigong. Stasiun paling bersih adalah Dingling.")

st.divider()
st.markdown("### Conclusion & Recommendation")
st.markdown("""
- Kurangi pembakaran batu bara untuk pemanasan ruangan di musim dingin.
- Perketat kontrol emisi kendaraan dan industri, terutama di Wanshouxigong, Dongsi, dan Nongzhanguan.
- Perbanyak penghijauan dan imbau masyarakat memakai masker saat musim dingin
""")
