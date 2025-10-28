import streamlit as st
import json
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import os

# =========================
# Konfigurasi Streamlit
# =========================
st.set_page_config(page_title="Potensi Desa Indonesia", layout="wide")
st.title("📊 Analisis Potensi Desa di Indonesia")
st.markdown("Sumber data: **BPS - Potensi Desa (PODES)** | Visualisasi oleh Fridha Megantara Putra")

# =========================
# 1️⃣ Baca file GeoJSON langsung dari root
# =========================
geojson_path = "map.geojson"

if not os.path.exists(geojson_path):
    st.error("❌ File `map.geojson` tidak ditemukan di direktori root! Pastikan file berada di folder yang sama dengan `app.py`.")
else:
    with open(geojson_path, "r", encoding="utf-8") as f:
        geojson_data = json.load(f)

    # =========================
    # 2️⃣ Konversi GeoJSON ke DataFrame
    # =========================
    data = []
    for feature in geojson_data["features"]:
        props = feature["properties"]
        geom = feature["geometry"]
        if geom["type"] == "Point":
            lon, lat = geom["coordinates"]
            props["longitude"] = lon
            props["latitude"] = lat
        data.append(props)

    df = pd.DataFrame(data)

    # =========================
    # 3️⃣ Tabel Data
    # =========================
    st.subheader("📋 Data Potensi Desa per Provinsi")
    st.dataframe(df)

    # =========================
    # 4️⃣ Peta Sebaran Folium
    # =========================
    st.subheader("🗺️ Peta Sebaran Lembaga Keterampilan")

    m = folium.Map(location=[-2.5, 118], zoom_start=5, tiles="CartoDB positron")

    for _, row in df.iterrows():
        if "latitude" in row and "longitude" in row:
            popup_text = f"""
            <b>{row.get('provinsi', 'Tidak diketahui')}</b><br>
            Total Lembaga: {row.get('total_lembaga', '-'):,}<br>
            Bahasa Asing: {row.get('bahasa_asing', '-'):,}<br>
            Komputer: {row.get('komputer', '-'):,}<br>
            Menjahit: {row.get('menjahit', '-'):,}<br>
            Kecantikan: {row.get('kecantikan', '-'):,}<br>
            Montir: {row.get('montir', '-'):,}<br>
            Elektronika: {row.get('elektronika', '-'):,}<br>
            Lainnya: {row.get('lainnya', '-'):,}<br>
            Tidak Ada: {row.get('tidak_ada', '-'):,}
            """
            folium.CircleMarker(
                location=[row["latitude"], row["longitude"]],
                radius=7,
                color="blue",
                fill=True,
                fill_color="blue",
                fill_opacity=0.7,
                popup=popup_text
            ).add_to(m)

    st_folium(m, width=1100, height=550)

    # =========================
    # 5️⃣ Visualisasi EDA
    # =========================
    st.subheader("📈 Analisis EDA Potensi Desa")

    col1, col2 = st.columns(2)

    with col1:
        fig1 = px.bar(
            df.sort_values("total_lembaga", ascending=False),
            x="provinsi", y="total_lembaga",
            title="Jumlah Total Lembaga Keterampilan per Provinsi",
            labels={"provinsi": "Provinsi", "total_lembaga": "Jumlah Lembaga"},
            color="total_lembaga",
            color_continuous_scale="Viridis"
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = px.pie(
            df,
            names="provinsi",
            values="tidak_ada",
            title="Distribusi Provinsi Tanpa Lembaga Keterampilan",
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("✅ Analisis ini menampilkan persebaran lembaga keterampilan di seluruh provinsi Indonesia, lengkap dengan peta interaktif dan visualisasi perbandingan.")
