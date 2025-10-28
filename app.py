import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import seaborn as sns
from io import StringIO

# =============================
# 1. Dataset langsung di file
# =============================
DATA = """
Provinsi,Bahasa_Asing,Komputer,Menjahit,Kecantikan,Total_Lembaga,Persentase_Desa_Dengan_Lembaga,Latitude,Longitude
Aceh,122,215,78,44,459,37.2,4.6951,96.7494
Sumatera Utara,235,312,122,81,750,41.5,2.1154,99.5451
Sumatera Barat,198,289,134,75,696,39.3,-0.7399,100.8000
Riau,176,254,99,58,587,35.1,0.5333,101.4500
Jambi,142,201,77,49,469,33.6,-1.4852,102.4381
Sumatera Selatan,223,315,145,92,775,43.8,-3.3194,104.9143
Bengkulu,121,184,67,41,413,36.0,-3.8006,102.2655
Lampung,210,302,121,83,716,42.5,-5.4500,105.2667
DKI Jakarta,312,401,255,210,1178,68.2,-6.2000,106.8167
Jawa Barat,620,785,423,312,2140,59.3,-6.9147,107.6098
Jawa Tengah,541,699,358,285,1883,57.1,-7.1500,110.1400
DI Yogyakarta,244,312,175,133,864,64.8,-7.7956,110.3695
Jawa Timur,588,755,401,310,2054,58.7,-7.2504,112.7688
Banten,276,366,189,142,973,56.2,-6.4058,106.0640
Bali,180,225,119,88,612,61.4,-8.3405,115.0920
Nusa Tenggara Barat,164,209,88,57,518,39.7,-8.6500,117.3660
Nusa Tenggara Timur,138,184,65,48,435,36.9,-10.1833,123.5833
Kalimantan Barat,176,249,101,62,588,37.5,-0.0227,109.3414
Kalimantan Tengah,142,198,76,51,467,35.9,-1.6815,113.3824
Kalimantan Selatan,169,229,93,61,552,38.2,-3.3194,114.5901
Kalimantan Timur,191,265,102,68,626,40.4,0.5004,117.1450
Sulawesi Utara,139,197,73,48,457,37.6,1.4931,124.8413
Sulawesi Tengah,155,211,83,55,504,35.2,-1.4300,121.4456
Sulawesi Selatan,288,366,165,111,930,44.1,-5.1477,119.4327
Gorontalo,102,144,54,35,335,33.7,0.6997,122.4467
Sulawesi Barat,111,152,61,39,363,34.8,-2.667,118.888
Maluku,98,133,53,36,320,31.2,-3.2385,130.1453
Maluku Utara,87,122,46,32,287,30.5,0.7893,127.3960
Papua Barat,76,109,39,27,251,29.8,-1.3361,133.1747
Papua,88,125,48,31,292,28.7,-4.2699,138.0800
"""

df = pd.read_csv(StringIO(DATA))

# =============================
# Pengaturan awal aplikasi
# =============================
st.set_page_config(page_title="Dashboard Potensi Desa", layout="wide", page_icon="🌾")
st.title("🌾 Dashboard Potensi Desa di Indonesia")
st.markdown("Analisis dan visualisasi potensi desa berdasarkan **lembaga keterampilan** di setiap provinsi.")

# =============================
# Sidebar
# =============================
st.sidebar.header("🔍 Filter Data")
jenis_lembaga = ['Bahasa_Asing', 'Komputer', 'Menjahit', 'Kecantikan']
pilihan_jenis = st.sidebar.selectbox("Pilih Jenis Lembaga:", jenis_lembaga)
wilayah_opsi = st.sidebar.multiselect("Pilih Provinsi (opsional):", df['Provinsi'].tolist(), default=[])

if wilayah_opsi:
    df_filtered = df[df['Provinsi'].isin(wilayah_opsi)]
else:
    df_filtered = df

# =============================
# Ringkasan Data
# =============================
col1, col2, col3 = st.columns(3)
col1.metric("Total Provinsi", df['Provinsi'].nunique())
col2.metric("Total Lembaga Pelatihan", int(df['Total_Lembaga'].sum()))
col3.metric("Rata-rata Persentase Desa", f"{df['Persentase_Desa_Dengan_Lembaga'].mean():.2f}%")

st.divider()

# =============================
# Bar Chart
# =============================
st.subheader(f"🏫 5 Provinsi dengan {pilihan_jenis.replace('_', ' ')} Terbanyak")
top5 = df.sort_values(pilihan_jenis, ascending=False).head(5)

plt.figure(figsize=(8, 4))
sns.barplot(x='Provinsi', y=pilihan_jenis, data=top5, palette='viridis')
plt.xticks(rotation=45, ha='right')
plt.title(f"5 Provinsi dengan {pilihan_jenis.replace('_', ' ')} Terbanyak")
st.pyplot(plt.gcf())
plt.close()

# =============================
# Peta Interaktif
# =============================
st.subheader("🗺️ Peta Sebaran Lembaga Pelatihan per Provinsi")

gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df['Longitude'], df['Latitude']), crs="EPSG:4326")
m = folium.Map(location=[-2.5, 117], zoom_start=5)

for _, row in gdf.iterrows():
    tooltip_text = (
        f"<b>{row['Provinsi']}</b><br>"
        f"Total Lembaga: {row['Total_Lembaga']}<br>"
        f"{pilihan_jenis.replace('_',' ')}: {row[pilihan_jenis]}<br>"
        f"Persentase Desa: {row['Persentase_Desa_Dengan_Lembaga']:.1f}%"
    )
    folium.CircleMarker(
        location=[row['Latitude'], row['Longitude']],
        radius=7 + (row[pilihan_jenis] / df[pilihan_jenis].max()) * 8,
        color='blue',
        fill=True,
        fill_opacity=0.6,
        tooltip=tooltip_text
    ).add_to(m)

st_data = st_folium(m, width=1200, height=600)

# =============================
# Heatmap Korelasi
# =============================
st.subheader("🔗 Korelasi antar Jenis Lembaga")
corr = df[jenis_lembaga].corr()
plt.figure(figsize=(8, 6))
sns.heatmap(corr, annot=True, cmap='coolwarm')
st.pyplot(plt.gcf())
plt.close()

# =============================
# Tabel Data
# =============================
st.subheader("📋 Data Lengkap Provinsi")
st.dataframe(df_filtered)

st.markdown("---")
st.markdown("© 2025 Dashboard Potensi Desa Indonesia | Dibuat oleh Fridha Megantara Putra")
