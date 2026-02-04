import streamlit as st
import librosa
import noisereduce as nr
import soundfile as sf
from pydub import AudioSegment, effects
import io
import os

# Uygulama Başlığı
st.title("🎙️ StudioEnhance AI")
st.write("Ses dosyanızı yükleyin ve 'Sesi Düzenle' butonuna basın.")

# Dosya Yükleme
yuklenen_dosya = st.file_uploader("Dosya Seçin", type=["mp3", "wav", "m4a"])

if yuklenen_dosya is not None:
    st.audio(yuklenen_dosya)
    
    if st.button("SESİ DÜZENLE"):
        with st.spinner("Ses iyileştiriliyor..."):
            try:
                # Sesi yükle
                data, rate = librosa.load(yuklenen_dosya, sr=None)
                
                # Gürültü temizleme
                temiz_data = nr.reduce_noise(y=data, sr=rate, prop_decrease=0.85)
                
                # Geçici dosyaya yaz (pydub için)
                sf.write("gecici.wav", temiz_data, rate)
                ses = AudioSegment.from_wav("gecici.wav")
                
                # Ses seviyesi dengeleme
                ses = effects.normalize(ses)
                
                # Çıktı hazırlama
                cikti = io.BytesIO()
                ses.export(cikti, format="mp3")
                
                st.success("İşlem Başarılı!")
                st.audio(cikti)
                st.download_button("Düzenlenmiş Sesi İndir", cikti.getvalue(), "temiz_ses.mp3", "audio/mp3")
                
                if os.path.exists("gecici.wav"):
                    os.remove("gecici.wav")
            except Exception as e:
                st.error(f"Bir hata oluştu: {e}")
