import streamlit as st
import pandas as pd
import pickle

# Konfigurasi Halaman
st.set_page_config(page_title="Market Basket Recommender", layout="wide")

# 1. Load Data Aturan Asosiasi
@st.cache_data
def load_data():
    with open('rules_apriori.pkl', 'rb') as f:
        rules = pickle.load(f)
    with open('products.pkl', 'rb') as f:
        products = pickle.load(f)
    return rules, products

rules, products = load_data()

# 2. Judul Aplikasi
st.title("🛍️ Sistem Rekomendasi Produk (Apriori)")
st.markdown("""
Aplikasi ini merekomendasikan produk yang sering dibeli bersamaan berdasarkan pola transaksi historis.
""")

# 3. Sidebar untuk Filter
st.sidebar.header("Pengaturan Rekomendasi")
min_lift = st.sidebar.slider("Minimal Skor Lift:", 1.0, 10.0, 1.5, 0.1)
min_conf = st.sidebar.slider("Minimal Confidence:", 0.0, 1.0, 0.4, 0.1)

# 4. Input Pengguna (Pilih Produk)
st.subheader("Cari Rekomendasi Produk")
selected_product = st.selectbox("Pilih produk yang ada di keranjang:", products)

# 5. Logika Rekomendasi
if st.button("Lihat Rekomendasi"):
    # Filter rules berdasarkan produk yang dipilih
    # Logika: cari produk di dalam frozenset 'antecedents'
    recommendations = rules[
        (rules['antecedents'].apply(lambda x: selected_product in x)) &
        (rules['lift'] >= min_lift) &
        (rules['confidence'] >= min_conf)
    ]
    
    # Urutkan berdasarkan Lift tertinggi
    recommendations = recommendations.sort_values(by='lift', ascending=False)

    if not recommendations.empty:
        st.success(f"Ditemukan {len(recommendations)} produk yang sering dibeli bersama '{selected_product}':")
        
        # Bersihkan tampilan frozenset agar enak dibaca (diubah ke string)
        display_df = recommendations[['consequents', 'confidence', 'lift']].copy()
        display_df['consequents'] = display_df['consequents'].apply(lambda x: ', '.join(list(x)))
        
        # Tampilkan Tabel
        st.table(display_df.reset_index(drop=True))
        
        # Tambahan Informasi Analitik
        col1, col2 = st.columns(2)
        with col1:
            best_lift = recommendations.iloc[0]['lift']
            st.metric("Skor Lift Tertinggi", f"{best_lift:.2f}")
        with col2:
            best_conf = recommendations.iloc[0]['confidence']
            st.metric("Confidence Tertinggi", f"{best_conf:.2%}")
    else:
        st.warning("Maaf, tidak ditemukan pola asosiasi yang cukup kuat untuk produk ini dengan filter yang dipilih.")