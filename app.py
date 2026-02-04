Python

import streamlit as st
import streamlit as st
# Bu satırı en üste, diğer importların hemen altına ekle:
st.cache_data.clear()
import librosa
import noisereduce as nr
import soundfile as sf
from pydub import AudioSegment, effects
import io
import os

# Sayfa başlığı (En sade haliyle)
st.title("🎙️ StudioEnhance AI")
st.write("Ses dosyanızı yükleyin ve 'Düzenle' butonuna basın.")

# Dosya yükleyici
yuklenen_dosya = st.file_uploader("Dosya Seçin", type=["mp3", "wav", "m4a"])

if yuklenen_dosya is not None:
    st.audio(yuklenen_dosya) # Orijinal sesi dinle
    
    if st.button("SESİ DÜZENLE"):
        with st.spinner("İşlem yapılıyor, lütfen bekleyin..."):
            try:
                # 1. Dosyayı oku
                data, rate = librosa.load(yuklenen_dosya, sr=None)
                
                # 2. Gürültü giderme
                temiz_data = nr.reduce_noise(y=data, sr=rate, prop_decrease=0.85)
                
                # 3. Geçici kayıt ve işleme
                sf.write("temp.wav", temiz_data, rate)
                ses = AudioSegment.from_wav("temp.wav")
                
                # 4. Normalizasyon (Ses dengeleme)
                ses = effects.normalize(ses)
                
                # 5. Sonucu hazırla
                cikti = io.BytesIO()
                ses.export(cikti, format="mp3")
                
                st.success("İşlem tamamlandı!")
                st.audio(cikti) # Düzenlenmiş sesi dinle
                
                st.download_button(
                    label="Düzenlenmiş Sesi İndir",
                    data=cikti.getvalue(),
                    file_name="temiz_ses.mp3",
                    mime="audio/mp3"
                )
                
                # Temizlik
                if os.path.exists("temp.wav"):
                    os.remove("temp.wav")
                    
            except Exception as e:
                st.error(f"Bir hata oluştu: {e}")
