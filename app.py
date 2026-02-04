import streamlit as st
import librosa
import noisereduce as nr
import soundfile as sf
from pydub import AudioSegment, effects
import io
import os
import numpy as np

st.set_page_config(page_title="Pro Leveler AI", page_icon="🎚️")

st.title("🎚️ Pro Leveler & Studio AI")
st.write("Ses seviyesini sabitler, iniş çıkışları yok eder ve sesi maksimum seviyede toklaştırır.")

uploaded_file = st.file_uploader("Ses Dosyasını Seçin", type=["mp3", "wav", "m4a"])

if uploaded_file is not None:
    st.write("### Orijinal Ses")
    st.audio(uploaded_file)
    
    if st.button("🪄 SESİ SABİTLE VE TOKLAŞTIR"):
        with st.spinner("Ses dalgaları hizalanıyor..."):
            try:
                # 1. Kaydı Yükle
                data, rate = librosa.load(uploaded_file, sr=44100)
                
                # 2. Gürültü Temizliği
                reduced_noise = nr.reduce_noise(y=data, sr=rate, prop_decrease=1.0)
                
                sf.write("stabil_islem.wav", reduced_noise, rate)
                ses = AudioSegment.from_wav("stabil_islem.wav")
                
                # 3. STABİLİZASYON (Leveling)
                # Sesi önce normalize ediyoruz ki tavan noktasını bilelim
                ses = effects.normalize(ses)
                
                # 4. AGRESİF COMPRESSION (Ses Seviyesini Sabitleyen Ana Motor)
                # Threshold'u çok düşürerek (-24dB) en kısık sesleri bile yakalıyoruz
                # Ratio'yu artırarak (10.0) yüksek seslerin 'fırlamasını' engelliyoruz
                ses = effects.compress_dynamic_range(
                    ses, 
                    threshold=-24.0, 
                    ratio=10.0, 
                    attack=5.0, 
                    release=200.0
                )
                
                # 5. TOKLAŞTIRMA (Bas Katmanı)
                bas = ses.low_pass_filter(250).apply_gain(8)
                ses = ses.overlay(bas)
                
                # 6. FİNAL STABİLİZASYON
                # Tekrar normalize ederek tüm dosyayı standart -0.1 dB seviyesine getiriyoruz
                ses = effects.normalize(ses, headroom=0.1)
                
                # Çıktı
                buffer = io.BytesIO()
                ses.export(buffer, format="mp3", bitrate="320k")
                
                st.success("✅ Ses seviyesi sabitlendi ve maksimum tokluğa ulaştı!")
                st.write("### Düzenlenmiş Stabil Ses")
                st.audio(buffer)
                st.download_button("Stabil Sesi İndir", buffer.getvalue(), "stabil_deep_vocal.mp3")
                
                if os.path.exists("stabil_islem.wav"):
                    os.remove("stabil_islem.wav")
            except Exception as e:
                st.error(f"Hata: {e}")
