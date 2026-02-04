import streamlit as st
import librosa
import noisereduce as nr
import soundfile as sf
from pydub import AudioSegment, effects
import io
import os
import numpy as np

st.set_page_config(page_title="Adobe Style Speech Enhancer", page_icon="🎙️")

st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #ff4b4b; color: white; }
    </style>
    """, unsafe_allow_stdio=True)

st.title("🎙️ AI Studio Enhancer")
st.write("Adobe Podcast teknolojisine en yakın vokal restorasyon sistemi.")

uploaded_file = st.file_uploader("Ses dosyanızı seçin", type=["mp3", "wav", "m4a"])

if uploaded_file is not None:
    st.info("Orijinal Kayıt Yüklendi")
    st.audio(uploaded_file)
    
    if st.button("🪄 ADOBE TARZI SESİ YENİDEN İNŞA ET"):
        with st.spinner("Derin öğrenme filtreleri uygulanıyor..."):
            try:
                # 1. Yüksek Çözünürlüklü Analiz
                data, rate = librosa.load(uploaded_file, sr=44100)
                
                # 2. Spektral Subtraction (Adobe'nin temel temizlik mantığı)
                # Gürültü profilini çok daha hassas analiz eder
                reduced_noise = nr.reduce_noise(
                    y=data, 
                    sr=rate, 
                    prop_decrease=1.0, 
                    stationary=False,
                    n_fft=4096, # Daha geniş analiz penceresi (Daha net ses)
                    time_constant_s=0.5
                )
                
                # 3. Geçici Dosya Oluşturma
                sf.write("processed.wav", reduced_noise, rate)
                audio = AudioSegment.from_wav("processed.wav")
                
                # 4. ADOBE 'TOK SES' AYARI (Advanced Compression)
                # Sesi stüdyo mikrofonuna yakınmış gibi dolgunlaştırır
                audio = effects.compress_dynamic_range(
                    audio, 
                    threshold=-20.0, 
                    ratio=4.5, 
                    attack=3.0, 
                    release=150.0
                )
                
                # 5. Parlatma (Vokal Boost)
                audio = audio.apply_gain(5) # Ses gövdesini güçlendir
                audio = effects.normalize(audio)
                
                # 6. Sonuç
                buffer = io.BytesIO()
                audio.export(buffer, format="mp3", bitrate="320k")
                
                st.success("✨ Ses restorasyonu tamamlandı!")
                st.write("### İşlenmiş Stüdyo Kaydı")
                st.audio(buffer)
                st.download_button("Sesi İndir", buffer.getvalue(), "adobe_style_enhanced.mp3")
                
                if os.path.exists("processed.wav"):
                    os.remove("processed.wav")
            except Exception as e:
                st.error(f"Hata oluştu: {e}")
