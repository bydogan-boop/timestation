# ⌚ Timestation: Lüks Saat Takip ve Envanter Sistemi

Timestation; Japonya'dan (Buyee vb.) alınan lüks saatlerin alımından satışına kadar geçen tüm uluslararası süreci (nakliye, gümrük, tamir, bakım) yöneten, maliyet analizi yapan ve Fransız gümrük mevzuatına uygun raporlar üreten profesyonel bir envanter yönetim sistemidir.

## 🏗 Veritabanı Mimarisi (Supabase - PostgreSQL)

Sistem, verilerin birbirine bağlı ve tutarlı olması için üç ana tablo üzerine inşa edilmiştir.

### 1. `persons` (Kişiler ve Firmalar)
Tedarikçilerin, müşterilerin ve tamir atölyelerinin tutulduğu tablodur. Esnek yapısı sayesinde bir kayıt aynı anda hem tedarikçi hem de müşteri rollerini üstlenebilir.

* **id**: Benzersiz sistem kimliği (Primary Key).
* **type**: 'Individual' (Şahıs) veya 'Company' (Şirket).
* **name_surname**: İsim Soyisim veya Yetkili Kişi.
* **company_name**: Firma Adı (Opsiyonel).
* **Roles**: `is_supplier`, `is_customer`, `is_repairer` (Boolean).

### 2. `watches` (Ana Stok)
Her saatin kimlik, alış maliyeti ve kondisyon bilgilerinin tutulduğu merkez tablodur.

* **stok_kodu**: Benzersiz stok kodu (Zorunlu ve Tekil).
* **seri_no**: Saatin orijinal seri numarası.
* **brand_model**: Marka ve Model bilgisi.
* **condition**: Parfait, Bon, Usé, Épave (Kondisyon Durumu).
* **Accessories**: `has_certificate`, `has_invoice`, `has_box` (Boolean).
* **buying_price_eur**: ECB kurundan otomatik çevrilmiş Euro maliyeti.
* **tva_regime**: Marge (Kâr KDV) veya Standart.
* **status**: Güncel konum (Örn: Douane France, Atelier TR).

### 3. `watch_costs` (Hareketler ve Masraflar)
Saate yapılan tüm ek harcamaların (Gümrük, kargo, parça değişimi, işçilik) tutulduğu tablodur. `watches` tablosuna `watch_id` üzerinden bağlıdır.

* **cost_type**: Logistique, Douane, Réparation, Autre.
* **amount_eur**: Harcama tutarı (Euro).
* **description**: İşlemin detayı (Örn: "Révision complète du mouvement").
* **date**: İşlem tarihi.

---

## 🚀 Temel Özellikler

* **Otomatik Döviz Çevrimi:** JPY, USD gibi birimlerle girilen alım fiyatları, Avrupa Merkez Bankası (ECB) verileriyle anlık olarak Euro'ya çevrilir ve kur kayda geçer.
* **Akıllı Stok Kontrolü:** Aynı stok kodunun mükerrer girilmesini veritabanı seviyesinde engeller.
* **Maliyet Akümülasyonu:** Saatin ana alış fiyatına, sonradan eklenen tüm tamir ve gümrük masrafları otomatik toplanarak "Net Maliyet" (Cout de revient) hesaplanır.
* **Resmi Raporlama:** Tek tuşla Fransızca "Fiche de Suivi et Douane" (Takip ve Gümrük Fişi) PDF belgesi oluşturur.
* **Görsel Entegrasyon:** Google Drive ID sistemi ile saatin fotoğraflarına hızlı erişim sağlar.

---

## 🛠 Teknik Kurulum

1.  **Gereksinimler:**
    `pip install streamlit supabase requests fpdf pandas`
2.  **Secrets Yönetimi:**
    `.streamlit/secrets.toml` dosyasına veya Streamlit Cloud Secrets kısmına `SUPABASE_URL` ve `SUPABASE_KEY` bilgilerini ekleyin.
3.  **Çalıştırma:**
    `streamlit run app.py`

---

## 🇫🇷 Fransızca Mevzuat Uyumu
Sistem, Fransa'daki ikinci el lüks saat ticareti kurallarına göre tasarlanmıştır. Özellikle **TVA sur Marge** hesaplamaları ve gümrük denetlemelerinde (Control Fiscal) istenen "ürün yaşam döngüsü belgesi" ihtiyacını karşılar.
