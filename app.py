Python

import streamlit as st
import librosa
import noisereduce as nr
import soundfile as sf
from pydub import AudioSegment, effects
import io
import os

# --- SAYFA AYARLARI VE TASARIM (CSS) ---
st.set_page_config(page_title="StudioEnhance AI", page_icon="???", layout="centered")

# Adobe tarzý karanlýk tema ve þýk butonlar için CSS
st.markdown("""
    <style>
    /* Ana Arka Plan */
    .stApp {
        background-color: #121212;
        color: #FFFFFF;
    }
    
    /* Yükleme Alaný Kartý */
    .stFileUploader {
        background-color: #1E1E1E;
        border-radius: 15px;
        padding: 20px;
        border: 1px dashed #3A3A3A;
    }

    /* Baþlýk Stili */
    h1 {
        color: #00E5FF;
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        text-align: center;
    }

    /* Düzenle Butonu Stili */
    div.stButton > button:first-child {
        background-color: #00E5FF;
        color: #000000;
        font-weight: bold;
        border-radius: 30px;
        width: 100%;
        border: none;
        padding: 15px;
        transition: 0.3s;
    }
    
    div.stButton > button:first-child:hover {
        background-color: #00B8D4;
        transform: scale(1.02);
    }

    /* Ses Oynatýcý Paneli */
    audio {
        border-radius: 10px;
        width: 100%;
    }
    </style>
    """, unsafe_allow_stdio=True)

# --- BAÞLIK VE TANITIM ---
st.title("??? StudioEnhance AI")
st.markdown("<p style='text-align: center; color: #BBBBBB;'>Tek týkla stüdyo kalitesinde ses elde edin. Gürültüyü silin, sesi parlatýn.</p>", unsafe_allow_stdio=True)
st.write("---")

# --- ANA UYGULAMA MANTIÐI ---
col1, col2 = st.columns([1, 1])

yuklenen_dosya = st.file_uploader("Ses Dosyasýný Buraya Býrakýn", type=["mp3", "wav", "m4a"])

if yuklenen_dosya is not None:
    st.info("?? Dosya yüklendi. Þimdi sihirli dokunuþu yapabiliriz.")
    
    # Düzenleme Butonu
    if st.button("SESÝ PROFESYONEL HALE GETÝR"):
        with st.status("?? Ses iþleniyor...", expanded=True) as status:
            try:
                st.write("?? Arka plan gürültüleri tespit ediliyor...")
                data, rate = librosa.load(yuklenen_dosya, sr=None)
                
                # AI Gürültü Azaltma
                temiz_data = nr.reduce_noise(y=data, sr=rate, prop_decrease=0.9)
                
                st.write("? Ses netleþtiriliyor ve normalize ediliyor...")
                gecici_yol = "gecici_islem.wav"
                sf.write(gecici_yol, temiz_data, rate)
                ses = AudioSegment.from_wav(gecici_yol)
                
                # Dinamik Aralýk Sýkýþtýrma (Studio Sound efekti)
                ses = effects.normalize(ses)
                ses = effects.compressor_sidechain(ses, target_rms=-18.0)
                
                # Sonuç
                cikti_buffer = io.BytesIO()
                ses.export(cikti_buffer, format="mp3")
                
                status.update(label="? Ýþlem Tamamlandý!", state="complete", expanded=False)

                # BAÞARI EKRANI
                st.balloons()
                st.success("Sesi baþarýyla düzenledik!")
                
                # Karþýlaþtýrma Paneli
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown("**Orijinal Ses**")
                    st.audio(yuklenen_dosya)
                with col_b:
                    st.markdown("**Düzenlenmiþ Ses**")
                    st.audio(cikti_buffer)
                
                # Ýndirme Butonu
                st.download_button(
                    label="?? YÜKSEK KALÝTEDE ÝNDÝR (.MP3)",
                    data=cikti_buffer.getvalue(),
                    file_name="studio_enhance_output.mp3",
                    mime="audio/mp3"
                )

                if os.path.exists(gecici_yol):
                    os.remove(gecici_yol)

            except Exception as e:
                st.error(f"Bir hata oluþtu: {e}")
else:
    # Dosya yokken gösterilecek görsel bir yer tutucu (Adobe tarzý)
    st.markdown("""
        <div style="text-align: center; padding: 50px; color: #555555;">
            <p>Desteklenen formatlar: MP3, WAV, M4A</p>
        </div>
    """, unsafe_allow_stdio=True)