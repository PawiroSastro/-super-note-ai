# ======================================================
# AI SUPER NOTE - CLEAN STABLE VERSION
# ======================================================

import streamlit as st
import os
from openai import OpenAI
import streamlit_mermaid as st_mermaid
from pytubefix import YouTube
from docx import Document
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph

# ---------------- CONFIG ----------------

MY_SECRET_KEY = st.secrets["OPENAI_API_KEY"]

client = OpenAI(api_key=MY_SECRET_KEY)

st.set_page_config(
    page_title="AI Super Note",
    page_icon="🚀",
    layout="wide"
)

st.markdown("""
<style>
.stButton>button{
width:100%;
border-radius:10px;
background:#007BFF;
color:white;
font-weight:bold;
}
.stDownloadButton>button{
width:100%;
border-radius:10px;
background:#28a745;
color:white;
font-weight:bold;
}
</style>
""", unsafe_allow_html=True)

st.title("🚀 AI Super Note")

if "data" not in st.session_state:
    st.session_state.data = {
        "audio":None,
        "transkrip":"",
        "ringkasan":"",
        "mindmap":""
    }

# ---------------- INPUT ----------------

c1,c2,c3=st.columns(3)

with c1:

    st.subheader("🎤 Rekam")

    rec=st.audio_input(
        "Gunakan Mikrofon"
    )

    if rec:
        st.session_state.data["audio"]=rec.read()

with c2:

    st.subheader("📂 Upload")

    up=st.file_uploader(
        "Unggah audio",
        type=["mp3","wav","m4a","ogg"]
    )

    if up:
        st.session_state.data["audio"]=up.read()

with c3:

    st.subheader("🔗 YouTube")

    yt=st.text_input(
        "Tempel Link"
    )


# ---------------- PROCESS ----------------

st.divider()

if st.button(
    "🚀 LUNCURKAN SASARAN KE TARGET",
    use_container_width=True
):

    with st.spinner("Memproses..."):

        try:

            # ---------- youtube ----------
            if yt:

                y=YouTube(yt)

                y.streams.get_audio_only().download(
                    filename="yt.mp3"
                )

                with open(
                    "yt.mp3",
                    "rb"
                ) as f:

                    st.session_state.data["audio"]=f.read()

                os.remove(
                    "yt.mp3"
                )


            if st.session_state.data["audio"]:

                with open(
                    "temp_audio.wav",
                    "wb"
                ) as f:

                    f.write(
                        st.session_state.data["audio"]
                    )

                # ---------- transcribe ----------

                with open(
                    "temp_audio.wav",
                    "rb"
                ) as audio:

                    transcript=client.audio.transcriptions.create(
                        model="gpt-4o-mini-transcribe",
                        file=audio,
                        language="id"
                    )

                teks=transcript.text

                st.session_state.data["transkrip"]=teks

                # ---------- AI ----------

                prompt=f"""
Ringkas materi berikut.
Buat:

1 Ringkasan
2 Poin penting
3 Mermaid mindmap graph TD

Isi:

{teks}
"""

                hasil=client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role":"user",
                            "content":prompt
                        }
                    ]
                )

                isi=hasil.choices[0].message.content

                st.session_state.data["ringkasan"]=isi

                st.session_state.data["mindmap"]="""
graph TD
A[Topik]
-->B[Poin 1]
-->C[Poin 2]
-->D[Poin 3]
"""

                st.rerun()

        except Exception as e:

            st.error(
                f"Error : {e}"
            )


# ---------------- OUTPUT ----------------

d=st.session_state.data

if d["transkrip"]:

    a,b=st.columns([2,1])

    with a:

        st.subheader(
            "🧠 Mindmap"
        )

        st_mermaid.st_mermaid(
            d["mindmap"]
        )

        st.info(
            d["ringkasan"]
        )

        st.text_area(
            "Transkrip",
            d["transkrip"],
            height=250
        )

    with b:

        st.subheader(
            "💾 Simpan"
        )

        st.download_button(
            "Audio",
            d["audio"],
            file_name="audio.wav"
        )

        # WORD

        doc=Document()

        doc.add_heading(
            "Laporan AI Super Note",
            level=1
        )

        doc.add_paragraph(
            d["transkrip"]
        )

        bio=BytesIO()

        doc.save(
            bio
        )

        st.download_button(
            "Unduh Word",
            bio.getvalue(),
            "laporan.docx"
        )

        # PDF

        p=BytesIO()

        pdf=SimpleDocTemplate(
            p,
            pagesize=A4
        )

        style=getSampleStyleSheet()

        pdf.build([
            Paragraph(
                "Laporan",
                style["Title"]
            ),
            Paragraph(
                d["transkrip"],
                style["Normal"]
            )
        ])

        st.download_button(
            "Unduh PDF",
            p.getvalue(),
            "laporan.pdf"
        )
