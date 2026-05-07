import streamlit as st
import pandas as pd
import pickle

# Konfigurasi Halaman agar terlihat profesional
st.set_page_config(
    page_title="Smart Shopping Recommender",
    page_icon="🛍️",
    layout="centered"
)

# 1. Load Data Aturan Asosiasi (Pre-calculated dari Notebook)
@st.cache_data
def load_data():
    # Memuat aturan yang sudah kita simpan sebelumnya
    with open('rules_apriori.pkl', 'rb') as f:
        rules = pickle.load(f)
    # Memuat daftar produk unik
    with open('products.pkl', 'rb') as f:
        products = pickle.load(f)
    return rules, products

# Menghindari error jika file belum ada
try:
    rules, products = load_data()
except FileNotFoundError:
    st.error("File 'rules_apriori.pkl' atau 'products.pkl' tidak ditemukan. Pastikan Anda sudah menjalankan bagian ekspor di Notebook.")
    st.stop()

# 2. Desain Antarmuka (UI)
st.title("🛍️ Smart Shopping Recommender")
st.markdown("""
Sistem ini membantu Anda menemukan produk yang **paling cocok** dibeli bersamaan dengan produk pilihan Anda.
""")

st.divider()

# 3. Input Pengguna (Hanya yang Dipahami Orang Awam)
col1, col2 = st.columns([2, 1])

with col1:
    selected_product = st.selectbox(
        "Apa produk yang sedang dibeli?",
        options=products,
        help="Pilih satu produk dari daftar untuk melihat pasangan produk terbaiknya."
    )

with col2:
    top_n = st.slider(
        "Tampilkan berapa rekomendasi?",
        min_value=1,
        max_value=10,
        value=5
    )

# 4. Logika Rekomendasi di Balik Layar
if st.button("Cari Produk Terkait", type="primary", use_container_width=True):
    
    # Filter rules: Cari produk pilihan di dalam 'antecedents'
    # Secara internal kita tetap menggunakan batasan kualitas (misal lift > 1)
    recommendations = rules[
        (rules['antecedents'].apply(lambda x: selected_product in x)) & 
        (rules['lift'] > 1.0)
    ]
    
    # Urutkan berdasarkan skor 'lift' tertinggi (Kecocokan Paling Kuat)
    recommendations = recommendations.sort_values(by='lift', ascending=False).head(top_n)

    if not recommendations.empty:
        st.success(f"Berdasarkan pola belanja pelanggan lain, berikut adalah {len(recommendations)} pasangan terbaik untuk **{selected_product}**:")
        
        # Merapikan tampilan tabel untuk pengguna
        display_df = recommendations[['consequents', 'lift']].copy()
        
        # Mengubah frozenset menjadi teks biasa agar tidak bingung
        display_df['Produk Rekomendasi'] = display_df['consequents'].apply(lambda x: ', '.join(list(x)))
        
        # Mengubah 'lift' menjadi bahasa yang dimengerti (Score Kecocokan)
        display_df['Level Kecocokan'] = display_df['lift'].apply(lambda x: "Sangat Tinggi" if x > 5 else ("Tinggi" if x > 2 else "Bagus"))
        
        # Tampilkan tabel hasil akhir
        st.dataframe(
            display_df[['Produk Rekomendasi', 'Level Kecocokan']],
            use_container_width=True,
            hide_index=True
        )
        
        st.info("💡 **Tips:** Anda bisa menawarkan produk-produk di atas sebagai paket promo (bundling).")
    else:
        st.warning("Belum ada data pola pembelian yang kuat untuk produk ini. Coba pilih produk lain.")

# Footer
st.divider()
st.caption("Developed with ❤️ for Market Basket Analysis Project")