import streamlit as st
import requests
import datetime
import pandas as pd
from supabase import create_client

# --- AYARLAR VE BAĞLANTI ---
# st.set_page_config sayfanın en üstünde olmalı
st.set_page_config(page_title="A-Gala Watch Tracker", page_icon="⌚", layout="wide")

# Supabase bağlantı bilgileri (Secrets kısmından çekilir)
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# --- FONKSİYONLAR ---
def get_exchange_rate(base_currency):
    if base_currency == "EUR": return 1.0
    try:
        url = f"https://api.frankfurter.app/latest?from={base_currency}&to=EUR"
        response = requests.get(url)
        return response.json()['rates']['EUR']
    except: return None

def is_stok_kodu_unique(code):
    res = supabase.table("watches").select("stok_kodu").eq("stok_kodu", code).execute()
    return len(res.data) == 0

# --- ARAYÜZ BAŞLIĞI ---
st.title("⌚ A-Gala Envanter & Takip Sistemi")

# --- 1. BÖLÜM: YENİ SAAT KAYDI (GİRİŞ) ---
with st.expander("🆕 Yeni Saat Kaydı Oluştur", expanded=False):
    with st.form("watch_entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            stok_kodu = st.text_input("Stok Kodu (Benzersiz)*").upper()
            marka_model = st.text_input("Marka & Model*")
            seri_no = st.text_input("Seri Numarası")
            condition = st.selectbox("Saat Kondisyonu", ["Parfait", "Bon", "Usé", "Épave"])
        with col2:
            alim_birimi = st.selectbox("Alım Döviz Birimi", ["JPY", "USD", "CHF", "EUR"])
            alim_fiyati_original = st.number_input(f"Alış Fiyatı ({alim_birimi})", min_value=0.0)
            tva_regime = st.selectbox("TVA Rejimi", ["Marge", "Standart"])
            drive_id = st.text_input("Google Drive Klasör ID")

        st.write("**Aksesuar ve Belgeler**")
        c1, c2, c3 = st.columns(3)
        has_cert = c1.checkbox("Sertifika")
        has_invoice = c2.checkbox("Alım Faturası")
        has_box = c3.checkbox("Orijinal Kutu")

        submit_button = st.form_submit_button("Saati Kaydet")

        if submit_button:
            if not stok_kodu or not marka_model:
                st.error("Gerekli alanları doldurun!")
            elif not is_stok_kodu_unique(stok_kodu):
                st.error("Bu stok kodu zaten var!")
            else:
                rate = get_exchange_rate(alim_birimi)
                if rate:
                    buying_price_eur = alim_fiyati_original * rate
                    data = {
                        "stok_kodu": stok_kodu, "brand_model": marka_model, "seri_no": seri_no,
                        "condition": condition, "has_certificate": has_cert, "has_invoice": has_invoice,
                        "has_box": has_box, "buying_price_original": alim_fiyati_original,
                        "currency": alim_birimi, "exchange_rate_to_eur": rate,
                        "buying_price_eur": round(buying_price_eur, 2), "tva_regime": tva_regime,
                        "drive_folder_id": drive_id, "status": "Buyee Warehouse"
                    }
                    supabase.table("watches").insert(data).execute()
                    st.success("Saat envantere eklendi!")
                    st.rerun()

# --- 2. BÖLÜM: HAREKET VE TAKİP (TIMELINE) ---
st.divider()
st.header("🚚 Hareket ve Masraf Yönetimi")

saat_listesi = supabase.table("watches").select("id, stok_kodu, brand_model").execute()
if saat_listesi.data:
    options = {f"{s['stok_kodu']} - {s['brand_model']}": s['id'] for s in saat_listesi.data}
    secili_saat_label = st.selectbox("Saat Seçiniz", options.keys())
    secili_saat_id = options[secili_saat_label]

    col_action, col_timeline = st.columns([1, 2])

    with col_action:
        st.subheader("📍 İşlem Ekle")
        with st.form("movement_form"):
            hareket_tipi = st.selectbox("İşlem Tipi", ["Logistique", "Douane", "Réparation", "Autre"])
            tutar = st.number_input("Masraf Tutarı (€)", min_value=0.0)
            aciklama = st.text_input("Açıklama")
            yeni_durum = st.selectbox("Yeni Konum", ["Buyee Warehouse", "En Transit", "Douane France", "Atelier TR", "Atelier FR", "Stock France", "Vendu"])
            
            if st.form_submit_button("Güncelle"):
                move_data = {"watch_id": secili_saat_id, "cost_type": hareket_tipi, "description": aciklama, "amount_eur": tutar, "date": str(datetime.date.today())}
                supabase.table("watch_costs").insert(move_data).execute()
                supabase.table("watches").update({"status": yeni_durum}).eq("id", secili_saat_id).execute()
                st.success("Güncellendi!")
                st.rerun()

    with col_timeline:
        st.subheader("📜 Saat Geçmişi")
        hareketler = supabase.table("watch_costs").select("*").eq("watch_id", secili_saat_id).order("date").execute()
        if hareketler.data:
            for h in hareketler.data:
                st.info(f"**{h['date']}** | **{h['cost_type']}**: {h['description']} - **{h['amount_eur']} €**")
        else:
            st.write("Henüz hareket yok.")
