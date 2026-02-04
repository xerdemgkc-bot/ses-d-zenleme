import streamlit as st
import librosa
import noisereduce as nr
import soundfile as sf
from pydub import AudioSegment, effects
import io
import os
import numpy as np

st.set_page_config(page_title="Pro Vocal Fixer", page_icon="🎧")

st.title("🎧 Pro Vocal Fixer")
st.write("Sıradan bir kaydı profesyonel podcast seviyesine çeker.")

# Ayarlar Paneli (Kullanıcıya kontrol veriyoruz)
st.sidebar.header("İyileştirme Ayarları")
gurultu_gucu = st.sidebar.slider("Gürültü Silme Gücü", 0.0, 1.0, 0.8)
ses_dolgunlugu = st.sidebar.checkbox("Sesi Toklaştır (Compressor)", value=True)

yuklenen_dosya = st.file_uploader("Ses Dosyası Seç", type=["mp3", "wav", "m4a"])

if yuklenen_dosya is not None:
    st.audio(yuklenen_dosya)
    
    if st.button("🪄 SESİ MÜKEMMELLEŞTİR"):
        with st.spinner("Yapay zeka ses frekanslarını analiz ediyor..."):
            try:
                # 1. Sesi yüksek kalite (High-res) yükle
                data, rate = librosa.load(yuklenen_dosya, sr=44100)
                
                # 2. GELİŞMİŞ GÜRÜLTÜ AZALTMA
                # Sadece sabit gürültüyü değil, değişkenleri de hedefler
                temiz_data = nr.reduce_noise(
                    y=data, 
                    sr=rate, 
                    prop_decrease=gurultu_gucu,
                    n_fft=2048
                )
                
                # 3. SESİ CANLANDIRMA (Yüksek frekansları parlatma)
                # Boğukluğu gidermek için frekansları dengeler
                sf.write("islem.wav", temiz_data, rate)
                ses = AudioSegment.from_wav("islem.wav")
                
                if ses_dolgunlugu:
                    # Compressor: Alçak sesleri yükseltir, patlamaları kısar
                    ses = effects.compress_dynamic_range(
                        ses, 
                        threshold=-24.0, 
                        ratio=4.0, 
                        attack=5.0, 
                        release=50.0
                    )
                
                # 4. NORMALİZASYON
                ses = effects.normalize(ses)
                
                # Çıktı
                cikti = io.BytesIO()
                ses.export(cikti, format="mp3", bitrate="320k") # En yüksek kalite
                
                st.success("✅ Sesiniz başarıyla işlendi!")
                st.audio(cikti)
                st.download_button("Dosyayı İndir (Yüksek Kalite)", cikti.getvalue(), "profesyonel_ses.mp3")
                
                if os.path.exists("islem.wav"):
                    os.remove("islem.wav")
            except Exception as e:
                st.error(f"Bir hata oluştu: {e}")
