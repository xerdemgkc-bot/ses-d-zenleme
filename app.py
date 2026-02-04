import streamlit as st
import librosa
import noisereduce as nr
import soundfile as sf
from pydub import AudioSegment, effects
import io
import os
import numpy as np

st.set_page_config(page_title="DeepVoice AI Studio", page_icon="🎧")

st.title("🎧 DeepVoice AI Studio")
st.write("Sesi dolgunlaştırır, basları güçlendirir ve stüdyo tonu kazandırır.")

uploaded_file = st.file_uploader("Ses Dosyası Yükle", type=["mp3", "wav", "m4a"])

if uploaded_file is not None:
    st.write("### Orijinal Ses")
    st.audio(uploaded_file)
    
    if st.button("🪄 SESİ TOKLAŞTIR VE DÜZENLE"):
        with st.spinner("Ses mühendisliği algoritmaları çalışıyor..."):
            try:
                # 1. Yüksek Kalite Analiz
                data, rate = librosa.load(uploaded_file, sr=44100)
                
                # 2. Arka Planı Tamamen Sessizleştir
                # Adobe tarzı keskin gürültü temizliği
                reduced_noise = nr.reduce_noise(
                    y=data, 
                    sr=rate, 
                    prop_decrease=1.0, 
                    n_fft=2048
                )
                
                sf.write("tok_islem.wav", reduced_noise, rate)
                ses = AudioSegment.from_wav("tok_islem.wav")
                
                # 3. RADYOCU ETKİSİ (TOKLUK AYARLARI)
                # Sesi çok sert bir şekilde sıkıştırarak o dolgunluğu yaratıyoruz
                ses = effects.compress_dynamic_range(
                    ses, 
                    threshold=-16.0, # Daha agresif eşik
                    ratio=6.0,       # Daha yüksek sıkıştırma oranı
                    attack=2.0, 
                    release=200.0
                )
                
                # 4. BAS VE GÖVDE GÜÇLENDİRME (Low-End Boost)
                # Sesin 'tok' gelmesi için alt frekansları 6dB artırıyoruz
                ses = ses.low_pass_filter(3000).apply_gain(3).overlay(ses)
                
                # 5. PARLATMA VE SES YÜKSELTME
                ses = ses.apply_gain(8) # Genel ses şiddetini ciddi şekilde artır
                ses = effects.normalize(ses) # Cızırtı/patlama olmasını engelle
                
                # 6. Çıktı
                buffer = io.BytesIO()
                ses.export(buffer, format="mp3", bitrate="320k")
                
                st.success("✨ Sesiniz artık çok daha tok ve profesyonel!")
                st.write("### Düzenlenmiş Yeni Ses")
                st.audio(buffer)
                st.download_button("Tok Sesi İndir", buffer.getvalue(), "deep_studio_vocal.mp3")
                
                if os.path.exists("tok_islem.wav"):
                    os.remove("tok_islem.wav")
            except Exception as e:
                st.error(f"Hata: {e}")
