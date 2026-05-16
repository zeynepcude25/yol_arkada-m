import streamlit as st
import streamlit.components.v1 as components
from gtts import gTTS
import base64
import io
import re

# ==========================================
# 1. SAYFA VE TAM EKRAN MOBİL DOKUNMATİK CSS AYARLARI
# ==========================================
st.set_page_config(page_title="EBB Yol Arkadaşım", page_icon="🚌", layout="centered")

# Telefon ekranını dikeyde tamamen kaplayan ve tarayıcı barlarını gizleyen CSS
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding-top: 1rem;}
    
    /* Ortadaki büyük kırmızı yazı */
    .karsilama-text {
        color: #8B1E10; 
        text-align: center; 
        font-size: 28px; 
        font-weight: bold;
        margin-top: 15px;
        margin-bottom: 15px;
    }
    
    /* TELEFON İÇİN DEVAŞA BUTON: Telefon ekranının dikeyde %70'ini kaplar */
    .stButton > button {
        width: 100% !important;
        height: 70vh !important; /* vh (viewport height) telefon ekranına göre kendini ayarlar */
        font-size: 28px !important;
        font-weight: bold !important;
        background: radial-gradient(circle, #ff6600 0%, #8b1e10 100%) !important;
        color: white !important;
        border-radius: 30px !important;
        border: none !important;
        box-shadow: 0px 8px 15px rgba(0, 0, 0, 0.3) !important;
    }
    </style>
""", unsafe_allow_html=True)

# Hafıza yönetim değişkenleri (State)
if "kvkk_onay" not in st.session_state:
    st.session_state["kvkk_onay"] = False

# Ses Üretme Fonksiyonu (Yazışma modu ve ilk açılış için)
def ses_uret(metin, dil_kodu):
    try:
        tts = gTTS(text=metin, lang=dil_kodu, slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        b64 = base64.b64encode(fp.read()).decode()
        html_audio = f'<audio autoplay src="data:audio/mp3;base64,{b64}">'
        components.html(html_audio, height=0, width=0)
    except Exception:
        pass

# ==========================================
# AŞAMA 1: FOTOĞRAFTAKİ KUTUCUKLU ONAY EKRANI
# ==========================================
if not st.session_state["kvkk_onay"]:
    st.markdown("<h3 style='text-align: center;'>🗻 EBB YOL ARKADAŞIM</h3>", unsafe_allow_html=True)
    
    col_bos, col_lang = st.columns([4, 1])
    with col_lang:
        dil = st.selectbox("Dil / Language", ["TR", "EN"], key="ilk_ekran_dil")
    
    st.markdown("<p style='text-align: center; color: gray;'>Engelsiz Ulaşım Asistanı</p>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center;'>KVKK ve Veri Güvenliği Aydınlatma Metni</h4>", unsafe_allow_html=True)
    
    kvkk_metni = """
    Yol Arkadaşım çalışırken anlık konum koşullarınız (GPS) sadece yolculuk güvenliğinizi sağlamak 
    amacıyla anlık olarak işlenir. Bu veriler hiçbir uzak sunucuya kaydedilmez ve yolculuğunuz bittiği an silinir.
    """
    st.info(kvkk_metni)
    
    # Okudum onaylıyorum kısmı tıklanabilir kutucuk (Checkbox)
    onay_kutucuku = st.checkbox("Okudum, onaylıyorum / I have read and approve")
    
    # Buton sadece kutucuk işaretliyse basılabilir olur
    if st.button("DEVAM ET / CONTINUE", disabled=not onay_kutucuku):
        st.session_state["kvkk_onay"] = True
        st.rerun()

# ==========================================
# AŞAMA 2: ASIL SORGULAMA EKRANI (TELEFON UYUMLU DEV BUTONLU)
# ==========================================
else:
    st.markdown("<h3 style='text-align: center;'>🗻 EBB YOL ARKADAŞIM</h3>", unsafe_allow_html=True)
    
    col_bos, col_lang = st.columns([4, 1])
    with col_lang:
        dil = st.selectbox("Dil / Language", ["TR", "EN"], key="ana_ekran_dil")
        
    st.markdown("<p style='text-align: center; color: gray;'>Engelsiz Ulaşım Asistanı</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Uygulama doğrudan Sesli Mod ile başlar
    mod = st.radio(
        "Modlar / Select Mode",
        ["🔊 Sesli Mod", "🔴 🤫 Sessiz Mod (Yazışma)"],
        horizontal=True
    )
    
    if dil == "TR":
        karsilama = "Nasıl yardımcı olabilirim?"
        placeholder_text = "Yazışarak durak sorun... (Örn: K4 otobüsü ne zaman gelir?)"
        chat_label = "💬 Yolculuk Chat Ekranı (Sessiz Mod)"
        speech_lang = "tr-TR"
    else:
        karsilama = "How can I help you?"
        placeholder_text = "Type to ask station... (e.g., When does bus K4 arrive?)"
        chat_label = "💬 Journey Chat Screen (Silent Mode)"
        speech_lang = "en-US"

    st.markdown(f"<div class='karsilama-text'>{karsilama}</div>", unsafe_allow_html=True)
    
    # SESSİZ MOD (YAZIŞMA) SÜRECİ
    if mod == "🔴 🤫 Sessiz Mod (Yazışma)":
        st.write(f"*{chat_label}*")
        kullanici_girdisi = st.text_input("", placeholder=placeholder_text, label_visibility="collapsed", key="yazisma_kutusu")
        
        if kullanici_girdisi:
            hat_bulucu = re.findall(r'\b[A-Z-a-z]?\d+[A-Z-a-z]?\b', kullanici_girdisi)
            if hat_bulucu:
                hat_adi = hat_bulucu[0].upper()
                cevap = f"{hat_adi} nolu Erzurum otobüsünün durağa gelmesine 6 dakika kalmıştır." if dil == "TR" else f"Bus {hat_adi} will arrive in 6 minutes."
            else:
                cevap = "Hat bilgisi Erzurum Ulaşım sisteminde sorgulanıyor..." if dil == "TR" else "Searching in Erzurum Transit database..."
            st.success(cevap)
            ses_uret(cevap, dil.lower())

    # SİRİ GİBİ ÇALIŞAN SESLİ MOD (TELEFONDA TAM EKRAN DOKUNMATİK)
    elif mod == "🔊 Sesli Mod":
        # Sesli modda alt yazışma kutusu tamamen kaldırıldı!
        st.write("🎯 **Görme Engelli Dostu Arayüz:** Ekranda küçük butonları aramanıza gerek yoktur. Ekranın herhangi bir yerine dokunarak konuşmaya başlayabilirsiniz.")
        
        # Tarayıcıda pürüzsüz çalışan Siri JS motoru
        siri_mobil_js = f"""
        <script>
        function siriTetikle() {{
            var recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = '{speech_lang}';
            recognition.interimResults = false;
            
            document.getElementById("SiriDurum").innerHTML = "🔴 Dinleniyor... Konuşun...";
            recognition.start();
            
            recognition.onresult = function(event) {{
                var ses_metni = event.results[0][0].transcript;
                document.getElementById("SiriDurum").innerHTML = "🤖 Algılanan: '" + ses_metni + "'";
                
                var hat_bul = ses_metni.match(/\\b[A-Za-z]?\\d+[A-Za-z]?\\b/);
                var cevap_metni = "";
                
                if(hat_bul) {{
                    var hat = hat_bul[0].toUpperCase();
                    cevap_metni = "{'TR' if dil=='TR' else 'EN'}" == "TR" ? 
                        hat + " nolu Erzurum Büyükşehir Belediyesi otobüsünün gelmesine altı dakika kalmıştır." : 
                        "Bus " + hat + " will arrive in six minutes.";
                }} else {{
                    cevap_metni = "{'TR' if dil=='TR' else 'EN'}" == "TR" ? 
                        "Söylediğinizi anlayamadım. Lütfen ekrana tekrar dokunup hat numarasını söyleyin." : 
                        "I couldn't understand. Please tap the screen again and state the line.";
                }}
                
                var msg = new SpeechSynthesisUtterance();
                msg.text = cevap_metni;
                msg.lang = '{speech_lang}';
                window.speechSynthesis.speak(msg);
                
                document.getElementById("SiriCevap").innerHTML = "💬 " + cevap_metni;
            }};
            
            recognition.onerror = function() {{
                document.getElementById("SiriDurum").innerHTML = "❌ Ses algılanamadı, lütfen tekrar dokunun.";
            }};
        }}
        </script>
        
        <div style="text-align: center; margin-top: 5px;">
            <h4 id="SiriDurum" style="color: #8B1E10;">👇 Konuşmak İçin Aşağıdaki Büyük Alana Dokunun 👇</h4>
            <div id="SiriCevap" style="background-color: #f0f2f6; padding: 10px; border-radius: 10px; font-weight: bold; font-size: 16px; margin-top: 5px;"></div>
        </div>
        """
        
        # Ekranın %70'ini kaplayan devasa mobil dokunmatik buton
        if st.button("🔴 EKRANA DOKUNUN / TAP TO SPEAK", use_container_width=True):
            components.html(siri_mobil_js + "<script>siriTetikle();</script>", height=140)