
import streamlit as st
import pandas as pd
import numpy as np
import joblib
from io import BytesIO
import os
import matplotlib.pyplot as plt

# ============================================================
# KONFIGURASI
# ============================================================

st.set_page_config(
    page_title="Dashboard PDB Sektoral",
    page_icon="📊",
    layout="wide"
)

MODEL_FILE = "model_dashboard.pkl"
HISTORICAL_FILE = "hasil_aktual_prediksi.xlsx"

official_features = [
    "inflasi", "jisdor", "export", "import"
]

gt_features = [
    "Perkebunan", "Peternakan", "Hortikultura", "Perburuan",
    "Perikanan", "Gas alam", "Minyak bumi", "Energi panas bumi",
    "Industri", "Industri makanan", "Industri tekstil", "Industri kimia",
    "Farmasi industri", "Industri pulp dan kertas", "Industri plastik",
    "Listrik", "Perabotan", "Es batu", "Pengelolaan sampah",
    "Pengolahan limbah", "Penyediaan air", "Konstruksi", "Daur ulang",
    "Perkulakan", "Perdagangan", "Transportasi", "Akomodasi",
    "Makanan dan minuman", "Komunikasi", "Informasi", "Telekomunikasi",
    "Penerbitan", "Asuransi", "Jasa keuangan", "Lahan yasan",
    "Konsultan", "Alih daya", "Pengadaan", "Pemerintahan",
    "Kesehatan", "Pendidikan", "Pekerja sosial", "Hiburan", "Kesenian"
]

template_columns = ["Periode"] + official_features + gt_features

nama_sektor = {
    "A": "Pertanian, Kehutanan, dan Perikanan",
    "B": "Pertambangan dan Penggalian",
    "C": "Industri Pengolahan",
    "D": "Pengadaan Listrik dan Gas",
    "E": "Pengadaan Air, Pengelolaan Sampah, Limbah dan Daur Ulang",
    "F": "Konstruksi",
    "G": "Perdagangan Besar dan Eceran",
    "H": "Transportasi dan Pergudangan",
    "I": "Penyediaan Akomodasi dan Makan Minum",
    "J": "Informasi dan Komunikasi",
    "K": "Jasa Keuangan dan Asuransi",
    "L": "Real Estat",
    "MN": "Jasa Perusahaan",
    "O": "Administrasi Pemerintahan",
    "P": "Jasa Pendidikan",
    "Q": "Jasa Kesehatan dan Kegiatan Sosial",
    "RSTU": "Jasa Lainnya"
}

# ============================================================
# LOAD MODEL
# ============================================================

@st.cache_resource
def load_models():
    return joblib.load(MODEL_FILE)

if not os.path.exists(MODEL_FILE):
    st.error(
        f"File `{MODEL_FILE}` tidak ditemukan. "
        "Letakkan model_dashboard.pkl di folder yang sama dengan app.py."
    )
    st.stop()

try:
    model_dashboard = load_models()
except Exception as e:
    st.error(f"Model tidak dapat dimuat: {e}")
    st.stop()

# ============================================================
# FUNGSI PREDIKSI
# ============================================================

def predict_sector(df, info_model):
    skenario = info_model["skenario"]
    fitur_input = info_model["fitur_input"]

    if skenario in ["S1", "S2", "S4"]:
        X_input = df[fitur_input].copy()

    elif skenario in ["S3", "S5"]:
        pca_scaler = info_model.get("pca_scaler")
        pca = info_model.get("pca")
        fitur_pca_input = info_model.get("fitur_pca_input")

        if pca_scaler is None or pca is None:
            raise ValueError("Objek PCA tidak ditemukan pada model.")

        if fitur_pca_input is None:
            if hasattr(pca_scaler, "feature_names_in_"):
                fitur_pca_input = list(pca_scaler.feature_names_in_)
            else:
                raise ValueError("Nama fitur PCA tidak ditemukan.")

        X_gt = df[fitur_pca_input].copy()
        X_gt_scaled = pca_scaler.transform(X_gt)
        X_pca = pca.transform(X_gt_scaled)

        pc_names = [
            f"PC{i}" for i in range(1, X_pca.shape[1] + 1)
        ]

        X_pca_df = pd.DataFrame(
            X_pca,
            columns=pc_names,
            index=df.index
        )

        pc_features = [
            f for f in fitur_input
            if str(f).upper().startswith("PC")
        ]

        official_model_features = [
            f for f in fitur_input
            if f not in pc_features
        ]

        parts = []

        if pc_features:
            parts.append(X_pca_df[pc_features])

        if official_model_features:
            parts.append(df[official_model_features].copy())

        X_input = pd.concat(parts, axis=1)[fitur_input]

    else:
        raise ValueError(f"Skenario {skenario} tidak dikenali.")

    X_scaled = info_model["scaler_model"].transform(X_input)
    return info_model["model"].predict(X_scaled)

# ============================================================
# HEADER
# ============================================================

st.title("📊 Dashboard PDB Sektoral Indonesia")
st.caption(
    "Visualisasi hasil penelitian dan prediksi PDB menggunakan "
    "model terbaik pada masing-masing sektor."
)

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("Menu")

menu = st.sidebar.radio(
    "Pilih menu:",
    [
        "📈 Visualisasi Hasil",
        "🔮 Prediksi PDB"
    ]
)

# ============================================================
# MENU 1: VISUALISASI HASIL PENELITIAN
# ============================================================

if menu == "📈 Visualisasi Hasil":

    st.header("Visualisasi Aktual vs Prediksi")

    st.write(
        "Menampilkan perbandingan nilai PDB aktual dan hasil prediksi "
        "model terbaik pada seluruh periode pengamatan."
    )

    if os.path.exists(HISTORICAL_FILE):
        try:
            df_hasil = pd.read_excel(
                HISTORICAL_FILE,
                sheet_name="Aktual_Prediksi"
            )
        except Exception as e:
            st.error(f"Gagal membaca file hasil prediksi: {e}")
            st.stop()
    else:
        uploaded_hasil = st.file_uploader(
            "Upload file hasil_aktual_prediksi.xlsx",
            type=["xlsx"],
            key="historical_upload"
        )

        if uploaded_hasil is None:
            st.info(
                "Letakkan `hasil_aktual_prediksi.xlsx` di folder aplikasi "
                "atau upload file hasil prediksi."
            )
            st.stop()

        df_hasil = pd.read_excel(
            uploaded_hasil,
            sheet_name="Aktual_Prediksi"
            if "Aktual_Prediksi" in pd.ExcelFile(uploaded_hasil).sheet_names
            else 0
        )

    required = ["Periode", "Sektor", "Aktual", "Prediksi"]

    missing = [
        c for c in required
        if c not in df_hasil.columns
    ]

    if missing:
        st.error(
            "Kolom berikut tidak ditemukan: " + ", ".join(missing)
        )
        st.stop()

    sektor_options = sorted(
        df_hasil["Sektor"].dropna().unique().tolist()
    )

    selected_sector = st.selectbox(
        "Pilih sektor:",
        sektor_options
    )

    data = df_hasil[
        df_hasil["Sektor"] == selected_sector
    ].copy()

    data["Periode"] = data["Periode"].astype(str)

    # --------------------------------------------------------
    # Informasi model
    # --------------------------------------------------------

    info_model = model_dashboard.get(selected_sector)

    if info_model is not None:

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Skenario terbaik",
            info_model.get("skenario", "-")
        )

        c2.metric(
            "Model terbaik",
            info_model.get("metode", "-")
        )

        c3.metric(
            "MAPE",
            f'{info_model["mape"]:.2f}%'
            if pd.notna(info_model.get("mape"))
            else "-"
        )

        c4.metric(
            "RMSE",
            f'{info_model["rmse"]:,.2f}'
            if pd.notna(info_model.get("rmse"))
            else "-"
        )

    # --------------------------------------------------------
    # Grafik
    # --------------------------------------------------------

    st.subheader(
        f"PDB Sektor {selected_sector} — "
        f"{nama_sektor.get(selected_sector, selected_sector)}"
    )

    fig, ax = plt.subplots(figsize=(12, 5))

    ax.plot(
        data["Periode"],
        data["Aktual"],
        linewidth=2,
        label="Aktual"
    )

    ax.plot(
        data["Periode"],
        data["Prediksi"],
        linestyle="--",
        linewidth=2,
        label="Prediksi"
    )

    ax.set_xlabel("Periode")
    ax.set_ylabel("PDB ADHK (Miliar Rupiah)")
    ax.grid(alpha=0.3)
    ax.legend()

    plt.xticks(rotation=45, ha="right")
    fig.tight_layout()

    st.pyplot(fig)

    # --------------------------------------------------------
    # Tabel
    # --------------------------------------------------------

    st.subheader("Data Aktual dan Prediksi")

    show_cols = ["Periode", "Aktual", "Prediksi"]

    if "Model" in data.columns:
        show_cols.append("Model")

    if "Skenario" in data.columns:
        show_cols.append("Skenario")

    st.dataframe(
        data[show_cols].reset_index(drop=True),
        use_container_width=True,
        hide_index=True
    )

# ============================================================
# MENU 2: PREDIKSI DATA BARU
# ============================================================

else:

    st.header("Prediksi PDB Data Baru")

    st.write(
        "Upload data prediktor sesuai template. Sistem akan "
        "menggunakan model terbaik yang telah diperoleh untuk "
        "masing-masing sektor."
    )

    # --------------------------------------------------------
    # TEMPLATE
    # --------------------------------------------------------

    st.subheader("1️⃣ Download Template Excel")

    template_df = pd.DataFrame(columns=template_columns)

    petunjuk = [
        {
            "Variabel": "Periode",
            "Jenis": "Identitas",
            "Keterangan": "Periode data. Contoh: 2025Q3."
        }
    ]

    for f in official_features:
        petunjuk.append({
            "Variabel": f,
            "Jenis": "Statistik resmi",
            "Keterangan": f"Nilai {f}."
        })

    for f in gt_features:
        petunjuk.append({
            "Variabel": f,
            "Jenis": "Google Trends",
            "Keterangan": f"Nilai Google Trends untuk topik {f}."
        })

    petunjuk_df = pd.DataFrame(petunjuk)

    template_buffer = BytesIO()

    with pd.ExcelWriter(
        template_buffer,
        engine="openpyxl"
    ) as writer:

        template_df.to_excel(
            writer,
            sheet_name="Data",
            index=False
        )

        petunjuk_df.to_excel(
            writer,
            sheet_name="Petunjuk",
            index=False
        )

    template_buffer.seek(0)

    st.download_button(
        "⬇️ Download Template Excel",
        data=template_buffer,
        file_name="template_prediksi_pdb.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )

    # --------------------------------------------------------
    # UPLOAD
    # --------------------------------------------------------

    st.subheader("2️⃣ Upload Data")

    uploaded_file = st.file_uploader(
        "Upload Excel yang sudah diisi",
        type=["xlsx", "xls"]
    )

    if uploaded_file is None:
        st.info("Silakan upload file Excel untuk melakukan prediksi.")
        st.stop()

    try:
        df_input = pd.read_excel(
            uploaded_file,
            sheet_name="Data"
        )
    except Exception:
        try:
            df_input = pd.read_excel(uploaded_file)
        except Exception as e:
            st.error(f"File Excel tidak dapat dibaca: {e}")
            st.stop()

    if df_input.empty:
        st.error("File tidak memiliki data.")
        st.stop()

    st.success(f"File berhasil dibaca: {len(df_input)} baris.")

    # --------------------------------------------------------
    # VALIDASI
    # --------------------------------------------------------

    missing_columns = [
        c for c in template_columns
        if c not in df_input.columns
    ]

    if missing_columns:
        st.error("Kolom yang belum tersedia:")
        st.write(missing_columns)
        st.stop()

    numeric_columns = official_features + gt_features

    non_numeric = [
        c for c in numeric_columns
        if not pd.api.types.is_numeric_dtype(df_input[c])
    ]

    if non_numeric:
        st.error("Variabel berikut harus berupa angka:")
        st.write(non_numeric)
        st.stop()

    missing_values = (
        df_input[numeric_columns]
        .isna()
        .sum()
    )

    missing_values = missing_values[
        missing_values > 0
    ]

    if len(missing_values) > 0:
        st.error("Terdapat missing value:")
        st.dataframe(
            missing_values.rename("Jumlah Missing"),
            use_container_width=True
        )
        st.stop()

    st.subheader("Preview Data")
    st.dataframe(
        df_input.head(),
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------------
    # PREDIKSI
    # --------------------------------------------------------

    st.subheader("3️⃣ Prediksi")

    if st.button(
        "🔮 Lakukan Prediksi",
        type="primary",
        use_container_width=True
    ):

        hasil = []
        errors = []

        progress = st.progress(0)
        sectors = list(model_dashboard.keys())

        for i, (sektor, info_model) in enumerate(
            model_dashboard.items()
        ):

            try:
                prediksi = predict_sector(
                    df_input,
                    info_model
                )

                for j, value in enumerate(prediksi):

                    periode = (
                        str(df_input.iloc[j]["Periode"])
                        if "Periode" in df_input.columns
                        else f"Baris {j + 1}"
                    )

                    hasil.append({
                        "Periode": periode,
                        "Kode Sektor": sektor,
                        "Sektor": nama_sektor.get(
                            sektor, sektor
                        ),
                        "Skenario": info_model["skenario"],
                        "Model": info_model["metode"],
                        "Prediksi PDB (Miliar Rupiah)": round(
                            float(value), 2
                        )
                    })

            except Exception as e:

                errors.append({
                    "Sektor": sektor,
                    "Masalah": str(e)
                })

            progress.progress(
                (i + 1) / len(sectors)
            )

        if hasil:

            df_hasil_baru = pd.DataFrame(hasil)

            st.success(
                f"Prediksi berhasil untuk "
                f"{df_hasil_baru['Sektor'].nunique()} sektor."
            )

            st.subheader("4️⃣ Hasil Prediksi")

            st.dataframe(
                df_hasil_baru,
                use_container_width=True,
                hide_index=True
            )

            # Download
            output_buffer = BytesIO()

            with pd.ExcelWriter(
                output_buffer,
                engine="openpyxl"
            ) as writer:

                df_hasil_baru.to_excel(
                    writer,
                    sheet_name="Hasil Prediksi",
                    index=False
                )

            output_buffer.seek(0)

            st.download_button(
                "⬇️ Download Hasil Prediksi",
                data=output_buffer,
                file_name="hasil_prediksi_pdb.xlsx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                )
            )

            # ------------------------------------------------
            # Grafik data baru
            # ------------------------------------------------

            st.subheader("5️⃣ Visualisasi Prediksi")

            selected_pred_sector = st.selectbox(
                "Pilih sektor:",
                sorted(
                    df_hasil_baru["Kode Sektor"].unique()
                ),
                format_func=lambda x: (
                    f"{x} — {nama_sektor.get(x, x)}"
                )
            )

            plot_data = df_hasil_baru[
                df_hasil_baru["Kode Sektor"]
                == selected_pred_sector
            ].copy()

            fig2, ax2 = plt.subplots(figsize=(12, 5))

            ax2.plot(
                plot_data["Periode"],
                plot_data[
                    "Prediksi PDB (Miliar Rupiah)"
                ],
                marker="o",
                linewidth=2
            )

            ax2.set_xlabel("Periode")
            ax2.set_ylabel(
                "Prediksi PDB (Miliar Rupiah)"
            )

            ax2.set_title(
                f"Prediksi PDB — Sektor "
                f"{selected_pred_sector}"
            )

            ax2.grid(alpha=0.3)

            plt.xticks(rotation=45, ha="right")
            fig2.tight_layout()

            st.pyplot(fig2)

        if errors:

            st.warning(
                "Beberapa sektor tidak dapat diprediksi."
            )

            st.dataframe(
                pd.DataFrame(errors),
                use_container_width=True,
                hide_index=True
            )

# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Dashboard PDB Sektoral Indonesia | "
    "Model terbaik pada masing-masing sektor."
)
