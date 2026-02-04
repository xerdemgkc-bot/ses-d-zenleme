import streamlit as st
import librosa
import noisereduce as nr
import soundfile as sf
from pydub import AudioSegment, effects
import io
import os
import numpy as np

st.set_page_config(page_title="MasterStudio AI", page_icon="🚀")

st.title("🚀 MasterStudio AI")
st.write("Sıradan bir kaydı profesyonel bir stüdyo kaydına dönüştürür.")

yuklenen_dosya = st.file_uploader("Ses Dosyasını Seçin", type=["mp3", "wav", "m4a"])

if yuklenen_dosya is not None:
    st.audio(yuklenen_dosya, label="Orijinal Kayıt")
    
    if st.button("🪄 SESİ MÜKEMMELLEŞTİR"):
        with st.spinner("Vokal analizi ve derin temizlik yapılıyor..."):
            try:
                # 1. Yüksek Kalite Yükleme
                data, rate = librosa.load(yuklenen_dosya, sr=44100)
                
                # 2. İki Aşamalı Temizlik
                # Önce vokal dışındaki frekansları traşlıyoruz
                temiz_data = nr.reduce_noise(y=data, sr=rate, prop_decrease=0.95, stationary=True)
                
                # 3. Dosyayı işlemek için kaydet
                sf.write("islem.wav", temiz_data, rate)
                ses = AudioSegment.from_wav("islem.wav")
                
                # 4. PROFESYONEL DOKUNUŞLAR
                # - Compressor: Sesi dolgunlaştırır
                # - Gain: Sesi net duyulur seviyeye çıkarır
                # - Normalize: Patlamaları engeller
                ses = effects.compress_dynamic_range(ses, threshold=-20.0, ratio=4.0)
                ses = ses.apply_gain(5) # Sesi 5 desibel yükselt (Daha canlı duyulsun)
                ses = effects.normalize(ses)
                
                # 5. Çıktı Hazırlama
                cikti = io.BytesIO()
                ses.export(cikti, format="mp3", bitrate="320k")
                
                st.success("✅ İşlem tamamlandı! Sesiniz artık daha tok ve net.")
                st.audio(cikti, label="Stüdyo Kalitesi")
                st.download_button("Dosyayı İndir", cikti.getvalue(), "studio_master.mp3")
                
                if os.path.exists("islem.wav"):
                    os.remove("islem.wav")
            except Exception as e:
                st.error(f"Teknik bir hata oluştu: {e}")
