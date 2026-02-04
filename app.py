import streamlit as st
import librosa
import noisereduce as nr
import soundfile as sf
from pydub import AudioSegment, effects
import io
import os
import numpy as np

# Sayfa ayarları - Hata payını sıfıra indirdik
st.set_page_config(page_title="AI Audio Pro", page_icon="🎙️")

st.title("🎙️ AI Studio Enhancer (Adobe Style)")
st.write("Sesinizi stüdyo mikrofonuyla kaydedilmiş gibi dolgunlaştırır.")

uploaded_file = st.file_uploader("Ses Dosyası Yükle", type=["mp3", "wav", "m4a"])

if uploaded_file is not None:
    st.audio(uploaded_file)
    
    if st.button("🪄 ADOBE TARZI SESİ DÜZENLE"):
        with st.spinner("Vokal analizi yapılıyor..."):
            try:
                # 1. Yüksek Çözünürlüklü Analiz (44.1kHz)
                data, rate = librosa.load(uploaded_file, sr=44100)
                
                # 2. ADOBE MANTIĞI: Derin Gürültü Temizleme
                # n_fft değerini yükselterek vokal netliğini koruyoruz
                reduced_noise = nr.reduce_noise(
                    y=data, 
                    sr=rate, 
                    prop_decrease=1.0, 
                    stationary=False,
                    n_fft=2048
                )
                
                # 3. Geçici İşleme
                sf.write("temp_process.wav", reduced_noise, rate)
                audio = AudioSegment.from_wav("temp_process.wav")
                
                # 4. ADOBE 'TOK SES' (Compressor & Limiter)
                # Sesi sanki ağzının dibinde mikrofon varmış gibi yakınlaştırır
                audio = effects.compress_dynamic_range(
                    audio, 
                    threshold=-18.0, 
                    ratio=4.0, 
                    attack=5.0, 
                    release=100.0
                )
                
                # 5. Parlatma (Vokal Boost)
                audio = audio.apply_gain(5)
                audio = effects.normalize(audio)
                
                # 6. Sonuç Hazırlama
                buffer = io.BytesIO()
                audio.export(buffer, format="mp3", bitrate="320k")
                
                st.success("✨ İşlem Tamamlandı!")
                st.audio(buffer)
                st.download_button("Düzenlenmiş Sesi İndir", buffer.getvalue(), "studio_vocal.mp3")
                
                if os.path.exists("temp_process.wav"):
                    os.remove("temp_process.wav")
            except Exception as e:
                st.error(f"Teknik bir sorun oluştu: {e}")
