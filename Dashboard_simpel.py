import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io

# reportlab
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

st.set_page_config(page_title="Dashboard apa ini", layout="wide")
st.title("📊 Untuk Catet Uang kopi dari member :))")

# ========================
# Styling tombol kecil
# ========================
st.markdown(
    """
    <style>
    div.stButton > button.small-btn {
        padding: 0.2rem 0.4rem;
        font-size: 0.8rem;
        border-radius: 6px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ========================
# Fungsi format angka
# ========================
format_rupiah = lambda x: f"Rp {x:,.0f}".replace(",", ".")

# ========================
# Inisialisasi DataFrame kosong
# ========================
if "df_payments" not in st.session_state:
    st.session_state.df_payments = pd.DataFrame(columns=["id", "user", "nominal", "paid_at"])

if "df_free" not in st.session_state:
    st.session_state.df_free = pd.DataFrame(columns=["id", "user", "trial_type", "start_date", "end_date"])

df_payments = st.session_state.df_payments
df_free = st.session_state.df_free

# ========================
# Pilihan tanggal input (untuk record data baru)
# ========================
st.sidebar.header("📅 Input Data")
input_date = st.sidebar.date_input("Tanggal Input", datetime.now().date())

# ========================
# Form input pembayaran baru
# ========================
st.subheader("➕ Catetnya disini cuk")
with st.form("form_payment", clear_on_submit=True):
    user_name = st.text_input("Nama yang ngasi uang kopi/kalo lupa kasi nomor hape nya aja ahahahah", key="user_payment")
    amount = st.number_input("Jumlah nya", min_value=0, step=1000, key="amount_payment")
    submit_payment = st.form_submit_button("Simpan Pembayaran")

    if submit_payment and user_name and amount > 0:
        new_payment = {
            "id": int(datetime.now().timestamp()),  # unik
            "user": user_name,
            "amount": amount,
            "paid_at": input_date.strftime("%Y-%m-%d")
        }
        st.session_state.df_payments = pd.concat(
            [st.session_state.df_payments, pd.DataFrame([new_payment])],
            ignore_index=True
        )
        st.success(f"Pembayaran dari {user_name} sebesar {format_rupiah(amount)} berhasil disimpan!")
        st.rerun()

# ========================
# Form input free trial
# ========================
st.subheader("🎁 Ini yang dapet Free Trial")
with st.form("form_trial", clear_on_submit=True):
    trial_user = st.text_input("Nama yang dapet Trial", key="trial_user")
    trial_type = st.selectbox("Jumlah hari Trial", ["1 Hari", "2 Hari"], key="trial_type")
    submit_trial = st.form_submit_button("Simpan Free Trial")

    if submit_trial and trial_user:
        days = 1 if trial_type == "1 Hari" else 2
        start_date = input_date
        end_date = start_date + timedelta(days=days)

        new_trial = {
            "id": int(datetime.now().timestamp()),  # unik
            "user": trial_user,
            "trial_type": trial_type,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
        }
        st.session_state.df_free = pd.concat(
            [st.session_state.df_free, pd.DataFrame([new_trial])],
            ignore_index=True
        )
        st.success(f"Free trial {trial_type} untuk {trial_user} berhasil disimpan! (sampai {end_date})")
        st.rerun()

# ========================
# Pilihan rentang tanggal filter
# ========================
st.sidebar.header("📂 Lihat Data")
date_range = st.sidebar.date_input(
    "Pilih Rentang Tanggal Data",
    [datetime.now().date() - timedelta(days=6), datetime.now().date()]
)

if isinstance(date_range, list) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = end_date = datetime.now().date()

# Filter data berdasarkan rentang tanggal
filtered_payments = df_payments[
    (df_payments["paid_at"] >= start_date.strftime("%Y-%m-%d")) &
    (df_payments["paid_at"] <= end_date.strftime("%Y-%m-%d"))
]

filtered_free = df_free[
    (df_free["start_date"] >= start_date.strftime("%Y-%m-%d")) &
    (df_free["start_date"] <= end_date.strftime("%Y-%m-%d"))
]

# ========================
# Fungsi generate PDF
# ========================
def generate_pdf(payments_df, free_df, start_date, end_date):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    story = []

    # Judul
    story.append(Paragraph(f"Laporan - {start_date} s/d {end_date}", styles["Title"]))
    story.append(Spacer(1, 20))

    # Bagian Pembayaran
    story.append(Paragraph("Pembayaran", styles["Heading2"]))
    if not payments_df.empty:
        df_show = payments_df.copy()
        df_show["amount"] = df_show["amount"].apply(lambda x: format_rupiah(int(x)))
        data = [df_show.columns.tolist()] + df_show.values.tolist()
        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.grey),
            ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
            ("ALIGN", (0,0), (-1,-1), "CENTER"),
            ("GRID", (0,0), (-1,-1), 0.5, colors.black),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ]))
        story.append(table)
    else:
        story.append(Paragraph("Tidak ada pembayaran.", styles["Normal"]))
    story.append(Spacer(1, 20))

    # Bagian Free Trial
    story.append(Paragraph("Free Trials", styles["Heading2"]))
    if not free_df.empty:
        data = [free_df.columns.tolist()] + free_df.values.tolist()
        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.grey),
            ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
            ("ALIGN", (0,0), (-1,-1), "CENTER"),
            ("GRID", (0,0), (-1,-1), 0.5, colors.black),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ]))
        story.append(table)
    else:
        story.append(Paragraph("Tidak ada free trial.", styles["Normal"]))

    doc.build(story)
    buffer.seek(0)
    return buffer

# ========================
# Tombol Download PDF
# ========================
pdf_buffer = generate_pdf(filtered_payments, filtered_free, start_date, end_date)
st.download_button(
    label="📥 Download Laporan (PDF)",
    data=pdf_buffer,
    file_name=f"laporan_{start_date}_sd_{end_date}.pdf",
    mime="application/pdf"
)

# ========================
# Layout 2 kolom dengan header + tombol hapus
# ========================
col1, col2 = st.columns(2)

with col1:
    st.subheader("💰 Uang kopi yang udah masuk")
    if not filtered_payments.empty:
        # Header
        header = st.columns([3, 3, 3, 1])
        header[0].markdown("**Nama**")
        header[1].markdown("**Jumlah**")
        header[2].markdown("**Tanggal**")
        header[3].markdown("**Aksi**")

        for idx, row in filtered_payments.iterrows():
            cols = st.columns([3, 3, 3, 1])
            cols[0].write(row["user"])
            cols[1].write(format_rupiah(int(row["amount"])))
            cols[2].write(row["paid_at"])
            if cols[3].button("🗑️", key=f"del_pay_{row['id']}", help="Hapus data", type="secondary"):
                st.session_state.df_payments = st.session_state.df_payments[
                    st.session_state.df_payments["id"] != row["id"]
                ]
                st.rerun()

        # 👉 Tambahkan total di bawah tabel
        total_amount = filtered_payments["amount"].astype(int).sum()
        st.markdown(f"### 🔢 Total: {format_rupiah(total_amount)}")

    else:
        st.info("Tidak ada pembayaran di rentang tanggal ini.")

with col2:
    st.subheader("🎁 Daftar yang dapet free trial :P")
    if not filtered_free.empty:
        # Header
        header = st.columns([3, 2, 3, 3, 1])
        header[0].markdown("**Nama**")
        header[1].markdown("**Jenis**")
        header[2].markdown("**Tgl_Mulai**")
        header[3].markdown("**Tgl_Habis**")
        header[4].markdown("**Aksi**")

        for idx, row in filtered_free.iterrows():
            cols = st.columns([3, 2, 3, 3, 1])
            cols[0].write(row["user"])
            cols[1].write(row["trial_type"])
            cols[2].write(row["start_date"])
            cols[3].write(row["end_date"])
            if cols[4].button("🗑️", key=f"del_free_{row['id']}", help="Hapus data", type="secondary"):
                st.session_state.df_free = st.session_state.df_free[
                    st.session_state.df_free["id"] != row["id"]
                ]
                st.rerun()
    else:
        st.info("Tidak ada free trial di rentang tanggal ini.")
