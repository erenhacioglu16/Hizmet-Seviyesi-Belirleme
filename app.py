import streamlit as st
import pandas as pd

# Sayfa Yapılandırması
st.set_page_config(page_title="Ecza Deposu Stok Paneli", layout="wide")

# --- 1. ŞİFRE EKRANI ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        st.title("🔐 Ecza Deposu Stok Yönetimi - Giriş")
        st.markdown("Devam etmek için lütfen giriş şifrenizi giriniz.")
        
        password = st.text_input("Şifre", type="password")
        if st.button("Sisteme Giriş Yap"):
            if password == "Eren12345":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("❌ Hatalı Şifre! Lütfen tekrar deneyiniz.")
        return False
    return True

# --- 2. ANA UYGULAMA ---
if check_password():
    st.title("📊 Stok Seviyesi ve Bütçe Projeksiyon Paneli")
    st.markdown("Excel dosyanızı yükleyerek 6 Milyar TL sınırına göre stok ve hedef analizini anlık yapabilirsiniz.")
    
    # Sol Menü - Bütçe Kontrolleri
    st.sidebar.header("⚙️ Bütçe ve Hedef Parametreleri")
    toplam_butce_siniri = st.sidebar.number_input("Maksimum Bütçe Sınırı (TL)", value=6000000000, step=100000000, format="%d")
    ideal_hedef_butce = st.sidebar.number_input("İdeal Hedef Bütçe (TL)", value=5800000000, step=100000000, format="%d")
    
    # Dosya Yükleme Alanı
    st.markdown("### 📄 Dosya Yükleme")
    uploaded_file = st.file_uploader(" 'Emniyet Seviyesi' Excel dosyasını buraya sürükleyin veya seçin", type=["xlsx", "xls"])
    
    if uploaded_file is not None:
        try:
            # Excel'i okuma (Başlıklar 7. satırda olduğu için skiprows=6)
            df = pd.read_excel(uploaded_file, sheet_name='Stok seviyesi', skiprows=6)
            
            # Gerekli sütunlar
            beklenen_sutunlar = ['Ürün Kodu', 'Ürün', 'Firma', 'Kademe', 'Emniyet Seviyesi', 'Min TL', 'Optimum TL', 'Hedef TL', 'Stok TL', 'Fazla TL', 'Alış Vades']
            mevcut_sutunlar = [col for col in beklenen_sutunlar if col in df.columns]
            df = df[mevcut_sutunlar].dropna(subset=['Ürün Kodu'])
            
            # Toplam Finansal Metrikler
            toplam_stok = df['Stok TL'].sum() if 'Stok TL' in df.columns else 0
            toplam_hedef = df['Hedef TL'].sum() if 'Hedef TL' in df.columns else 0
            toplam_fazla = df['Fazla TL'].sum() if 'Fazla TL' in df.columns else 0
            
            st.success("✅ Excel dosyası başarıyla işlendi ve güncellendi.")
            
            # Özet Göstergeler (KPI Cards)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Mevcut Stok Tutarı", f"{toplam_stok:,.0f} ₺")
            c2.metric("Sistem Hedef Tutarı", f"{toplam_hedef:,.0f} ₺")
            c3.metric("Kalan Bütçe (6 Milyar Sınırı)", f"{toplam_butce_siniri - toplam_stok:,.0f} ₺")
            c4.metric("Toplam Atıl (Fazla) Stok", f"{toplam_fazla:,.0f} ₺")
            
            # Risk ve Bütçe Durumu Uyarı Alanı
            st.markdown("---")
            if toplam_stok > toplam_butce_siniri:
                st.error(f"🔴 **KRİTİK BÜTÇE AŞIMI:** Toplam stok tutarı 6 Milyar TL sınırını **{toplam_stok - toplam_butce_siniri:,.0f} ₺** aşıyor!")
            elif toplam_stok > ideal_hedef_butce:
                st.warning(f"🟡 **EMNİYET BÖLGESİ:** Stok tutarı 5.8 Milyar TL ideal hedefinin üzerinde. 200 Milyon TL'lik emniyet payı kullanılıyor.")
            else:
                st.success("🟢 **BÜTÇE UYGUN:** Stok tutarı ideal 5.8 Milyar TL hedefinin altında güvenli bölgede.")

            # Tablo ve Filtreleme
            st.markdown("### 🔍 Ürün Bazlı Stok Detayları")
            
            if 'Firma' in df.columns:
                firma_listesi = ["Tümü"] + sorted(list(df['Firma'].dropna().unique()))
                secilen_firma = st.selectbox("Tedarikçi Firma Filtresi", firma_listesi)
                
                if secilen_firma != "Tümü":
                    goster_df = df[df['Firma'] == secilen_firma]
                else:
                    goster_df = df
            else:
                goster_df = df

            st.dataframe(goster_df, use_container_width=True)

        except Exception as e:
            st.error(f"Dosya okunurken bir hata oluştu: {e}")
    else:
        st.info("💡 Lütfen işlem yapmak için güncel 'Emniyet Seviyesi' Excel dosyanızı yukarıdaki alana yükleyin.")
