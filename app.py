import streamlit as st
import librosa
import noisereduce as nr
import soundfile as sf
from pydub import AudioSegment, effects
import io
import os
import numpy as np

st.set_page_config(page_title="Adobe Style Enhancer", page_icon="🎙️")

st.title("🎙️ AI Speech Enhancer")
st.write("Adobe Podcast mantığıyla vokal restorasyonu ve dolgunlaştırma.")

yuklenen_dosya = st.file_uploader("Ses Dosyası (MP3/WAV)", type=["mp3", "wav", "m4a"])

if yuklenen_dosya is not None:
    st.write("### Orijinal Ses")
    st.audio(yuklenen_dosya)
    
    if st.button("🪄 ADOBE TARZI İYİLEŞTİR"):
        with st.spinner("Yapay zeka vokalini yeniden inşa ediyor..."):
            try:
                # 1. Sesi yüksek çözünürlükte yükle
                data, rate = librosa.load(yuklenen_dosya, sr=44100)
                
                # 2. ADOBE MANTIĞI: Spektral Kapılama (Deep Noise Suppression)
                # Gürültüyü sadece kısmıyoruz, vokal olmayan frekansları tamamen izole ediyoruz
                temiz_data = nr.reduce_noise(
                    y=data, 
                    sr=rate, 
                    prop_decrease=1.0, # Gürültüyü %100 hedefle
                    stationary=False,  # Değişken gürültüleri de yakala
                    n_std_thresh_stationary=1.5,
                    n_fft=2048
                )
                
                # 3. VOKAL RESTORASYONU (Dolgunlaştırma)
                sf.write("temp.wav", temiz_data, rate)
                ses = AudioSegment.from_wav("temp.wav")
                
                # Compressor (Adobe'nin o 'tok' sesini veren ana ayar)
                # Eşiği düşük tutarak fısıltıları bile stüdyo seviyesine çekeriz
                ses = effects.compress_dynamic_range(
                    ses, 
                    threshold=-22.0, 
                    ratio=5.0, 
                    attack=2.0, 
                    release=100.0
                )
                
                # 4. PARLATMA (Limiter & Gain)
                ses = ses.apply_gain(6) # Sesi güçlendir
                ses = effects.normalize(ses) # Patlamaları önle
                
                # 5. Çıktı
                cikti = io.BytesIO()
                ses.export(cikti, format="mp3", bitrate="320k")
                
                st.success("✨ Sesiniz stüdyo kalitesine getirildi!")
                st.write("### İşlenmiş Ses")
                st.audio(cikti)
                st.download_button("Dosyayı İndir", cikti.getvalue(), "enhanced_speech.mp3")
                
                if os.path.exists("temp.wav"):
                    os.remove("temp.wav")
            except Exception as e:
                st.error(f"Hata: {e}")
