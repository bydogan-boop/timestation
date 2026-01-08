import streamlit as st
import requests
import datetime
import pandas as pd
from supabase import create_client
from fpdf import FPDF

# --- AYARLAR VE BAĞLANTI ---
st.set_page_config(page_title="Timestation Watch Tracker", page_icon="⌚", layout="wide")

# Supabase bağlantısı
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)
except Exception as e:
    st.error("Secrets dosyası veya Supabase bağlantı bilgileri hatalı!")
    st.stop()

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

def generate_french_pdf(saat, hareketler, toplam_maliyet):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, "FICHE DE SUIVI ET DOUANE", ln=True, align="C")
    pdf.ln(10)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, "Details de la Montre", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(95, 8, f"Marque & Modele: {saat['brand_model']}")
    pdf.cell(95, 8, f"Numero de serie: {saat['seri_no']}", ln=True)
    pdf.cell(95, 8, f"Code Stock: {saat['stok_kodu']}")
    pdf.cell(95, 8, f"Etat: {saat['condition']}", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 10, "Historique des Frais", ln=True)
    for h in hareketler:
        pdf.set_font("Arial", "", 9)
        pdf.cell(190, 7, f"- {h['date']} | {h['cost_type']}: {h['description']} ({h['amount_eur']} EUR)", ln=True)
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, f"COUT TOTAL DE REVIENT: {toplam_maliyet:.2f} EUR", ln=True, align="R")
    
    return pdf.output(dest='S').encode('latin-1')

# --- ARAYÜZ ---
st.title("⌚ Timestation Takip Sistemi")

import streamlit as st
import requests
import datetime
import pandas as pd
from supabase import create_client
from fpdf import FPDF

# --- AYARLAR VE BAĞLANTI ---
st.set_page_config(page_title="Timestation Watch Tracker", page_icon="⌚", layout="wide")

# Supabase bağlantısı
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)
except Exception as e:
    st.error("Secrets dosyası veya Supabase bağlantı bilgileri hatalı!")
    st.stop()

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

def generate_french_pdf(saat, hareketler, toplam_maliyet):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, "FICHE DE SUIVI ET DOUANE", ln=True, align="C")
    pdf.ln(10)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, "Details de la Montre", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(95, 8, f"Marque & Modele: {saat['brand_model']}")
    pdf.cell(95, 8, f"Numero de serie: {saat['seri_no']}", ln=True)
    pdf.cell(95, 8, f"Code Stock: {saat['stok_kodu']}")
    pdf.cell(95, 8, f"Etat: {saat['condition']}", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 10, "Historique des Frais", ln=True)
    for h in hareketler:
        pdf.set_font("Arial", "", 9)
        pdf.cell(190, 7, f"- {h['date']} | {h['cost_type']}: {h['description']} ({h['amount_eur']} EUR)", ln=True)
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, f"COUT TOTAL DE REVIENT: {toplam_maliyet:.2f} EUR", ln=True, align="R")
    
    return pdf.output(dest='S').encode('latin-1')

# --- ARAYÜZ ---
st.title("⌚ Timestation Takip Sistemi")

# 1. BÖLÜM: KAYIT FORMU (Aynı kalıyor, hata yakalama eklendi)
with st.expander("🆕 Yeni Saat Kaydı Oluştur"):
    with st.form("watch_entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            stok_kodu = st.text_input("Stok Kodu*").upper()
            marka_model = st.text_input("Marka & Model*")
            seri_no = st.text_input("Seri No")
            condition = st.selectbox("Etat", ["Parfait", "Bon", "Usé", "Épave"])
        with col2:
            alim_birimi = st.selectbox("Devise", ["JPY", "USD", "CHF", "EUR"])
            fiyat = st.number_input("Prix", min_value=0.0)
            tva = st.selectbox("TVA", ["Marge", "Standart"])
            drive = st.text_input("Google Drive ID")

        if st.form_submit_button("Saati Kaydet"):
            rate = get_exchange_rate(alim_birimi)
            if rate and is_stok_kodu_unique(stok_kodu):
                data = {
                    "stok_kodu": stok_kodu, "brand_model": marka_model, "seri_no": seri_no,
                    "condition": condition, "buying_price_original": fiyat, "currency": alim_birimi,
                    "exchange_rate_to_eur": rate, "buying_price_eur": round(fiyat * rate, 2),
                    "tva_regime": tva, "drive_folder_id": drive
                }
                try:
                    supabase.table("watches").insert(data).execute()
                    st.success("Kaydedildi!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Veritabanı Hatası (RLS kontrol edin): {e}")

# 2. BÖLÜM: DETAYLAR VE HAREKETLER
st.divider()
res = supabase.table("watches").select("*").execute()
if res.data:
    df = pd.DataFrame(res.data)
    options = {f"{row['stok_kodu']} - {row['brand_model']}": row['id'] for _, row in df.iterrows()}
    sel_label = st.selectbox("İncelemek istediğiniz saati seçin", options.keys())
    sel_id = options[sel_label]
    saat = next(item for item in res.data if item["id"] == sel_id)

    # Maliyet Hesaplama
    h_res = supabase.table("watch_costs").select("*").eq("watch_id", sel_id).execute()
    ek_masraf = sum(float(h['amount_eur']) for h in h_res.data)
    toplam_maliyet = float(saat['buying_price_eur']) + ek_masraf

    c_det, c_form = st.columns([2, 1])
    
    with c_det:
        st.subheader("📊 Finansal Özet")
        st.metric("Toplam Maliyet (EUR)", f"{toplam_maliyet:.2f} €")
        
        # Fransızca PDF Butonu
        pdf_data = generate_french_pdf(saat, h_res.data, toplam_maliyet)
        st.download_button(f"📥 PDF Raporu Al (Fransızca)", data=pdf_data, file_name=f"Rapport_{saat['stok_kodu']}.pdf")
        
        # Zaman Çizelgesi
        st.write("**İşlem Geçmişi:**")
        for h in h_res.data:
            st.caption(f"{h['date']} | {h['cost_type']}: {h['amount_eur']} € - {h['description']}")

    with c_form:
        st.subheader("📍 Yeni İşlem")
        with st.form("move"):
            tip = st.selectbox("Tip", ["Logistique", "Douane", "Réparation", "Autre"])
            tutar = st.number_input("Tutar (€)", min_value=0.0)
            desc = st.text_input("Açıklama")
            durum = st.selectbox("Konum", ["En Transit", "Douane France", "Stock France", "Vendu"])
            if st.form_submit_button("Ekle"):
                supabase.table("watch_costs").insert({"watch_id": sel_id, "cost_type": tip, "amount_eur": tutar, "description": desc, "date": str(datetime.date.today())}).execute()
                supabase.table("watches").update({"status": durum}).eq("id", sel_id).execute()
                st.rerun()

# 2. BÖLÜM: DETAYLAR VE HAREKETLER
st.divider()
res = supabase.table("watches").select("*").execute()
if res.data:
    df = pd.DataFrame(res.data)
    options = {f"{row['stok_kodu']} - {row['brand_model']}": row['id'] for _, row in df.iterrows()}
    sel_label = st.selectbox("İncelemek istediğiniz saati seçin", options.keys())
    sel_id = options[sel_label]
    saat = next(item for item in res.data if item["id"] == sel_id)

    # Maliyet Hesaplama
    h_res = supabase.table("watch_costs").select("*").eq("watch_id", sel_id).execute()
    ek_masraf = sum(float(h['amount_eur']) for h in h_res.data)
    toplam_maliyet = float(saat['buying_price_eur']) + ek_masraf

    c_det, c_form = st.columns([2, 1])
    
    with c_det:
        st.subheader("📊 Finansal Özet")
        st.metric("Toplam Maliyet (EUR)", f"{toplam_maliyet:.2f} €")
        
        # Fransızca PDF Butonu
        pdf_data = generate_french_pdf(saat, h_res.data, toplam_maliyet)
        st.download_button(f"📥 PDF Raporu Al (Fransızca)", data=pdf_data, file_name=f"Rapport_{saat['stok_kodu']}.pdf")
        
        # Zaman Çizelgesi
        st.write("**İşlem Geçmişi:**")
        for h in h_res.data:
            st.caption(f"{h['date']} | {h['cost_type']}: {h['amount_eur']} € - {h['description']}")

    with c_form:
        st.subheader("📍 Yeni İşlem")
        with st.form("move"):
            tip = st.selectbox("Tip", ["Logistique", "Douane", "Réparation", "Autre"])
            tutar = st.number_input("Tutar (€)", min_value=0.0)
            desc = st.text_input("Açıklama")
            durum = st.selectbox("Konum", ["En Transit", "Douane France", "Stock France", "Vendu"])
            if st.form_submit_button("Ekle"):
                supabase.table("watch_costs").insert({"watch_id": sel_id, "cost_type": tip, "amount_eur": tutar, "description": desc, "date": str(datetime.date.today())}).execute()
                supabase.table("watches").update({"status": durum}).eq("id", sel_id).execute()
                st.rerun()
