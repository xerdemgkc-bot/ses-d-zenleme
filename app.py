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
st.write("Sesi stüdyo kalitesine taşımak için analiz ediliyor...")

yuklenen_dosya = st.file_uploader("Ses Dosyasını Seçin", type=["mp3", "wav", "m4a"])

if yuklenen_dosya is not None:
    # Hatalı olan 'label' kısmını kaldırdık, metin olarak üstüne yazdık
    st.write("### Orijinal Kayıt")
    st.audio(yuklenen_dosya)
    
    if st.button("🪄 SESİ MÜKEMMELLEŞTİR"):
        with st.spinner("Ses frekansları dengeleniyor..."):
            try:
                # 1. Sesi yükle
                data, rate = librosa.load(yuklenen_dosya, sr=44100)
                
                # 2. Gürültü Filtresi
                temiz_data = nr.reduce_noise(y=data, sr=rate, prop_decrease=0.90)
                
                # 3. İşleme için kaydet
                sf.write("islem.wav", temiz_data, rate)
                ses = AudioSegment.from_wav("islem.wav")
                
                # 4. VOKAL PARLATMA (Equalizer mantığı)
                # Sesin 'dolgun' çıkması için compressor ve gain ekliyoruz
                ses = effects.compress_dynamic_range(ses, threshold=-18.0, ratio=3.5)
                ses = ses.apply_gain(4) 
                ses = effects.normalize(ses)
                
                # 5. Çıktı
                cikti = io.BytesIO()
                ses.export(cikti, format="mp3", bitrate="320k")
                
                st.success("✅ İşlem tamamlandı!")
                st.write("### Düzenlenmiş Stüdyo Kaydı")
                st.audio(cikti)
                st.download_button("Dosyayı İndir", cikti.getvalue(), "studio_vocal.mp3")
                
                if os.path.exists("islem.wav"):
                    os.remove("islem.wav")
            except Exception as e:
                st.error(f"Bir sorun oluştu: {e}")
