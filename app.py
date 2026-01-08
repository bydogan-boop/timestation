import streamlit as st
import requests
import datetime
import pandas as pd
from supabase import create_client

# --- KUR ÇEKME FONKSİYONU (ECB Bazlı) ---
def get_exchange_rate(base_currency):
    if base_currency == "EUR":
        return 1.0
    try:
        # Ücretsiz ve güncel kur API'si (Örn: frankfurter.dev - ECB verilerini kullanır)
        url = f"https://api.frankfurter.app/latest?from={base_currency}&to=EUR"
        response = requests.get(url)
        data = response.json()
        return data['rates']['EUR']
    except:
        return None

# --- STOK KODU KONTROLÜ ---
def is_stok_kodu_unique(code):
    res = supabase.table("watches").select("stok_kodu").eq("stok_kodu", code).execute()
    return len(res.data) == 0

# --- FORM ARAYÜZÜ ---
st.header("⌚ Yeni Saat Kaydı")

with st.form("watch_entry_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        stok_kodu = st.text_input("Stok Kodu (Benzersiz)*").upper()
        marka_model = st.text_input("Marka & Model*")
        seri_no = st.text_input("Seri Numarası")
        condition = st.selectbox("Saat Kondisyonu", ["Parfait", "Bon", "Usé", "Épave"])
        
    with col2:
        alim_birimi = st.selectbox("Alım Döviz Birimi", ["JPY", "USD", "CHF", "EUR", "GBP"])
        alim_fiyati_original = st.number_input(f"Alış Fiyatı ({alim_birimi})", min_value=0.0, step=0.01)
        tva_regime = st.selectbox("TVA Rejimi", ["Marge", "Standart"])
        drive_id = st.text_input("Google Drive Klasör ID")

    st.write("---")
    st.write("**Aksesuar ve Belgeler**")
    c1, c2, c3 = st.columns(3)
    has_cert = c1.checkbox("Orijinal Sertifika")
    has_invoice = c2.checkbox("Alım Faturası")
    has_box = c3.checkbox("Orijinal Kutu")

    submit_button = st.form_submit_button("Saati Envantere Kaydet")

    if submit_button:
        # 1. Kontrol: Boş alan var mı?
        if not stok_kodu or not marka_model:
            st.error("Lütfen Stok Kodu ve Marka/Model alanlarını doldurun.")
        
        # 2. Kontrol: Stok kodu benzersiz mi?
        elif not is_stok_kodu_unique(stok_kodu):
            st.error(f"HATA: '{stok_kodu}' stok kodu zaten veritabanında mevcut!")
            
        else:
            # 3. Kur Çevrimi İşlemi
            rate = get_exchange_rate(alim_birimi)
            if rate:
                buying_price_eur = alim_fiyati_original * rate
                
                # Veritabanına Hazırlık
                data = {
                    "stok_kodu": stok_kodu,
                    "brand_model": marka_model,
                    "seri_no": seri_no,
                    "condition": condition,
                    "has_certificate": has_cert,
                    "has_invoice": has_invoice,
                    "has_box": has_box,
                    "buying_price_original": alim_fiyati_original,
                    "currency": alim_birimi,
                    "exchange_rate_to_eur": rate,
                    "buying_price_eur": round(buying_price_eur, 2),
                    "tva_regime": tva_regime,
                    "drive_folder_id": drive_id,
                    "status": "Buyee Warehouse"
                }
                
                try:
                    supabase.table("watches").insert(data).execute()
                    st.success(f"Başarılı! Saat {buying_price_eur:.2f} EUR maliyetle kaydedildi.")
                except Exception as e:
                    st.error(f"Veritabanı hatası: {e}")
            else:
                st.error("Güncel döviz kuru çekilemedi. Lütfen internet bağlantısını kontrol edin.")
