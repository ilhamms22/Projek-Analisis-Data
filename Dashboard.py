import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Konfigurasi Streamlit
st.set_page_config(page_title="Dashboard Penyewaan Sepeda", layout="wide")

# Load dataset
@st.cache_data
def load_data():
    day_df = pd.read_csv("day.csv")
    hour_df = pd.read_csv("hour.csv")

    # Konversi tipe data
    day_df["dteday"] = pd.to_datetime(day_df["dteday"])
    hour_df["dteday"] = pd.to_datetime(hour_df["dteday"])

    categorical_columns = ["season", "weathersit", "workingday", "holiday"]
    for col in categorical_columns:
        if col in day_df.columns:
            day_df[col] = day_df[col].astype("category")
        if col in hour_df.columns:
            hour_df[col] = hour_df[col].astype("category")

    # Mapping kategori
    season_dict = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
    weather_dict = {
        1: "Clear",
        2: "Mist",
        3: "Light Snow/Rain",
        4: "Heavy Rain/Snow",
    }

    day_df["season"] = day_df["season"].map(season_dict)
    day_df["weathersit"] = day_df["weathersit"].map(weather_dict)
    hour_df["season"] = hour_df["season"].map(season_dict)
    hour_df["weathersit"] = hour_df["weathersit"].map(weather_dict)

    return day_df, hour_df


# Load data
day_df, hour_df = load_data()

# Sidebar
st.sidebar.header("Filter Data")
min_date = day_df["dteday"].min()
max_date = day_df["dteday"].max()

# Widget filter tanggal
date_range = st.sidebar.date_input("Pilih Rentang Tanggal", [min_date, max_date], min_value=min_date, max_value=max_date)

# Konversi tanggal agar sesuai dengan dataframe
start_date = pd.to_datetime(date_range[0])
if len(date_range) == 1:
    start_date = pd.to_datetime(date_range[0])
    end_date = start_date  # Set end_date sama dengan start_date
elif len(date_range) > 1:
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])
else:
    start_date = end_date = None

# Filter data
day_df_filtered = day_df[(day_df["dteday"] >= start_date) & (day_df["dteday"] <= end_date)]
hour_df_filtered = hour_df[(hour_df["dteday"] >= start_date) & (hour_df["dteday"] <= end_date)]

# Header
st.title("Dashboard Penyewaan Sepeda")
st.write(f"Menampilkan data dari **{start_date.date()}** hingga **{end_date.date()}**")

# ---- Statistik ----
st.subheader("Statistik Penyewaan Sepeda")
col1, col2, col3 = st.columns(3)

col1.metric("Total Penyewaan", f"{day_df_filtered['cnt'].sum():,}")
col2.metric("Rata-rata Penyewaan Harian", f"{day_df_filtered['cnt'].mean():.2f}")
col3.metric("Hari Tertinggi", f"{day_df_filtered['cnt'].max():,}")

# ---- Visualisasi ----
st.subheader("Analisis Penyewaan Sepeda")

# Plot Distribusi Penyewaan Harian
fig, ax = plt.subplots(figsize=(10, 5))
sns.histplot(data=day_df_filtered, x="cnt", bins=30, kde=True, ax=ax)
ax.set_title("Distribusi Penyewaan Sepeda Harian")
ax.set_xlabel("Jumlah Penyewaan")
ax.set_ylabel("Frekuensi")
st.pyplot(fig)

# ---- Analisis Musim ----
st.subheader("Pola Penyewaan Berdasarkan Musim dan Cuaca")

# Rata-rata penyewaan berdasarkan musim
fig, ax = plt.subplots(figsize=(8, 5))
sns.barplot(data=day_df_filtered, x="season", y="cnt", ax=ax)
ax.set_title("Rata-rata Penyewaan Sepeda Berdasarkan Musim")
ax.set_xlabel("Musim")
ax.set_ylabel("Rata-rata Penyewaan")
st.pyplot(fig)

# Rata-rata penyewaan berdasarkan kondisi cuaca
fig, ax = plt.subplots(figsize=(8, 5))
sns.barplot(data=day_df_filtered, x="weathersit", y="cnt", ax=ax)
ax.set_title("Rata-rata Penyewaan Sepeda Berdasarkan Cuaca")
ax.set_xlabel("Kondisi Cuaca")
ax.set_ylabel("Rata-rata Penyewaan")
st.pyplot(fig)

# ---- Waktu Puncak ----
st.subheader("Waktu Puncak Penyewaan Sepeda")

hourly_avg = hour_df_filtered.groupby("hr")["cnt"].mean()

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(hourly_avg, marker="o", linestyle="-")
ax.set_title("Rata-rata Penyewaan Sepeda berdasarkan Jam")
ax.set_xlabel("Jam")
ax.set_ylabel("Rata-rata Penyewaan")
ax.grid()
st.pyplot(fig)

# Menampilkan jam puncak
peak_hours = hourly_avg.nlargest(3)
st.write("**Jam Puncak Penyewaan:**")
for i, (hour, count) in enumerate(peak_hours.items(), start=1):
    st.write(f"**{i}. Pukul {hour}:00** → {count:.2f} penyewaan/jam")

# ---- Kesimpulan ----
st.subheader("Kesimpulan")
st.markdown("""
### 1. Bagaimana pola penggunaan sepeda berdasarkan musim dan cuaca?
Pola penggunaan sepeda dipengaruhi oleh faktor musim dan kondisi cuaca. Dari hasil analisis, terlihat adanya variasi jumlah penyewaan yang signifikan berdasarkan kedua faktor tersebut.

#### Berdasarkan Musim:
- **Musim Gugur (Fall)** memiliki jumlah penyewaan tertinggi, dengan rata-rata 5.644 penyewaan per hari dan 236 penyewaan per jam.
- **Musim Panas (Summer)** berada di peringkat kedua, dengan rata-rata 4.992 penyewaan per hari dan 208 penyewaan per jam.
- **Musim Dingin (Winter)** memiliki jumlah penyewaan sedikit lebih rendah dibandingkan musim panas, dengan rata-rata 4.728 penyewaan per hari dan 198 penyewaan per jam.
- **Musim Semi (Spring)** memiliki jumlah penyewaan terendah, dengan rata-rata 2.604 penyewaan per hari dan 111 penyewaan per jam.

#### Berdasarkan Kondisi Cuaca:
- **Cuaca cerah (Clear)** menunjukkan penggunaan sepeda tertinggi, dengan rata-rata 4.876 penyewaan per hari dan 204 penyewaan per jam.
- **Cuaca berkabut (Mist)** sedikit mengurangi jumlah penyewaan, dengan rata-rata 4.035 penyewaan per hari dan 175 penyewaan per jam.
- **Cuaca buruk seperti hujan/salju ringan (Light Snow/Rain)** menurunkan jumlah penyewaan secara signifikan, dengan rata-rata 1.803 penyewaan per hari dan 111 penyewaan per jam.
- **Cuaca ekstrem (Heavy Rain/Snow)** memiliki dampak paling besar terhadap penurunan penggunaan sepeda, dengan rata-rata hanya 74 penyewaan per jam.

### 2. Kapan waktu puncak (peak hours) penggunaan sepeda?
- **Pukul 17:00 (5 sore)** memiliki jumlah penyewaan tertinggi, dengan rata-rata 461 penyewaan per jam.
- **Pukul 18:00 (6 sore)** masih menunjukkan angka penyewaan yang tinggi, dengan rata-rata 426 penyewaan per jam.
- **Pukul 08:00 (8 pagi)** juga merupakan salah satu waktu puncak, dengan rata-rata 359 penyewaan per jam.

### Kesimpulan
Dari hasil analisis, dapat disimpulkan bahwa **musim gugur dan cuaca cerah** merupakan kondisi terbaik bagi penggunaan sepeda, sedangkan **musim semi dan cuaca ekstrem** memiliki dampak negatif terbesar terhadap jumlah penyewaan.

Selain itu, pola penggunaan sepeda menunjukkan bahwa **jam sibuk** terjadi pada **pukul 08:00 pagi (jam masuk kerja/sekolah) dan pukul 17:00-18:00 sore (jam pulang kerja/sekolah).**
""")
