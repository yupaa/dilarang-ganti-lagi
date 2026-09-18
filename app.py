import streamlit as st
import pandas as pd
import numpy as np
import joblib
from io import BytesIO


# ============================================================
# KONFIGURASI HALAMAN
# ============================================================

st.set_page_config(
    page_title="Prediksi PDB Sektoral",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# JUDUL DASHBOARD
# ============================================================

st.title("📊 Dashboard Prediksi PDB Sektoral Indonesia")

st.markdown(
    """
    Dashboard ini digunakan untuk menghasilkan prediksi
    **PDB triwulanan berdasarkan 17 sektor ekonomi**.

    **Langkah penggunaan:**

    1. Download template Excel.
    2. Isi nilai variabel sesuai dengan nama kolom.
    3. Upload kembali file Excel.
    4. Klik **Lakukan Prediksi**.
    5. Hasil prediksi akan ditampilkan untuk setiap sektor.
    """
)


# ============================================================
# LOAD MODEL
# ============================================================

@st.cache_resource
def load_models():
    return joblib.load("model_dashboard.pkl")


try:
    model_dashboard = load_models()

except Exception as e:

    st.error(
        "❌ Model tidak dapat dimuat."
    )

    st.error(
        f"Detail error: {e}"
    )

    st.stop()


# ============================================================
# NAMA SEKTOR
# ============================================================

nama_sektor = {

    'A':
        'Pertanian, Kehutanan, dan Perikanan',

    'B':
        'Pertambangan dan Penggalian',

    'C':
        'Industri Pengolahan',

    'D':
        'Pengadaan Listrik dan Gas',

    'E':
        'Pengadaan Air, Pengelolaan Sampah, '
        'Limbah dan Daur Ulang',

    'F':
        'Konstruksi',

    'G':
        'Perdagangan Besar dan Eceran',

    'H':
        'Transportasi dan Pergudangan',

    'I':
        'Penyediaan Akomodasi dan Makan Minum',

    'J':
        'Informasi dan Komunikasi',

    'K':
        'Jasa Keuangan dan Asuransi',

    'L':
        'Real Estat',

    'MN':
        'Jasa Perusahaan',

    'O':
        'Administrasi Pemerintahan',

    'P':
        'Jasa Pendidikan',

    'Q':
        'Jasa Kesehatan dan Kegiatan Sosial',

    'RSTU':
        'Jasa Lainnya'
}


# ============================================================
# VARIABEL GOOGLE TRENDS
# ============================================================

gt_features = [

    'Perkebunan',
    'Peternakan',
    'Hortikultura',
    'Perburuan',
    'Perikanan',

    'Gas alam',
    'Minyak bumi',
    'Energi panas bumi',

    'Industri',
    'Industri makanan',
    'Industri tekstil',
    'Industri kimia',
    'Farmasi industri',
    'Industri pulp dan kertas',
    'Industri plastik',

    'Listrik',
    'Perabotan',
    'Es batu',

    'Pengelolaan sampah',
    'Pengolahan limbah',
    'Penyediaan air',

    'Konstruksi',
    'Daur ulang',

    'Perkulakan',
    'Perdagangan',

    'Transportasi',

    'Akomodasi',
    'Makanan dan minuman',

    'Komunikasi',
    'Informasi',
    'Telekomunikasi',
    'Penerbitan',

    'Asuransi',
    'Jasa keuangan',

    'Lahan yasan',

    'Konsultan',
    'Alih daya',

    'Pengadaan',
    'Pemerintahan',

    'Kesehatan',
    'Pendidikan',
    'Pekerja sosial',

    'Hiburan',
    'Kesenian'
]


# ============================================================
# VARIABEL STATISTIK RESMI
# ============================================================

official_features = [

    'inflasi',
    'jisdor',
    'export',
    'import'

]


# ============================================================
# CEK JUMLAH VARIABEL
# ============================================================

if len(gt_features) != 44:

    st.warning(
        f"⚠️ Daftar Google Trends berisi "
        f"{len(gt_features)} variabel, bukan 44."
    )


# ============================================================
# SELURUH KOLOM TEMPLATE
# ============================================================

template_columns = [

    'Periode'

] + official_features + gt_features


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("ℹ️ Informasi Dashboard")

st.sidebar.write(
    f"Jumlah sektor: **{len(model_dashboard)}**"
)

st.sidebar.write(
    f"Google Trends: **{len(gt_features)} variabel**"
)

st.sidebar.write(
    f"Statistik resmi: **{len(official_features)} variabel**"
)

st.sidebar.write(
    f"Total prediktor raw: "
    f"**{len(gt_features) + len(official_features)} variabel**"
)


# ============================================================
# DOWNLOAD TEMPLATE
# ============================================================

st.header("1️⃣ Download Template Excel")

st.write(
    """
    Download template berikut untuk memastikan nama kolom
    sesuai dengan variabel yang digunakan dalam model.
    """
)


# ============================================================
# SHEET DATA
# ============================================================

template_df = pd.DataFrame(
    columns=template_columns
)


# ============================================================
# SHEET PETUNJUK
# ============================================================

petunjuk_data = []


petunjuk_data.append({

    'Variabel':
        'Periode',

    'Jenis':
        'Identitas',

    'Keterangan':
        'Periode data yang akan diprediksi.'
})


for fitur in official_features:

    petunjuk_data.append({

        'Variabel':
            fitur,

        'Jenis':
            'Statistik resmi',

        'Keterangan':
            f'Nilai {fitur}.'
    })


for fitur in gt_features:

    petunjuk_data.append({

        'Variabel':
            fitur,

        'Jenis':
            'Google Trends',

        'Keterangan':
            f'Nilai Google Trends untuk topik {fitur}.'
    })


petunjuk_df = pd.DataFrame(
    petunjuk_data
)


# ============================================================
# BUAT FILE EXCEL
# ============================================================

template_buffer = BytesIO()


with pd.ExcelWriter(
    template_buffer,
    engine='openpyxl'
) as writer:

    template_df.to_excel(
        writer,
        index=False,
        sheet_name='Data'
    )

    petunjuk_df.to_excel(
        writer,
        index=False,
        sheet_name='Petunjuk'
    )


template_buffer.seek(0)


# ============================================================
# BUTTON DOWNLOAD
# ============================================================

st.download_button(

    label="⬇️ Download Template Excel",

    data=template_buffer,

    file_name="template_prediksi_pdb.xlsx",

    mime=(
        "application/vnd.openxmlformats-officedocument."
        "spreadsheetml.sheet"
    )
)


# ============================================================
# UPLOAD DATA
# ============================================================

st.header("2️⃣ Upload Data")

uploaded_file = st.file_uploader(

    "Upload file Excel yang sudah diisi",

    type=['xlsx', 'xls']
)


# ============================================================
# PROSES FILE
# ============================================================

if uploaded_file is not None:

    # ========================================================
    # BACA FILE
    # ========================================================

    try:

        df = pd.read_excel(
            uploaded_file,
            sheet_name='Data'
        )

    except Exception:

        try:

            df = pd.read_excel(
                uploaded_file
            )

        except Exception as e:

            st.error(
                "❌ File Excel tidak dapat dibaca."
            )

            st.error(
                str(e)
            )

            st.stop()


    # ========================================================
    # CEK FILE KOSONG
    # ========================================================

    if df.empty:

        st.error(
            "❌ File tidak memiliki data."
        )

        st.stop()


    st.success(
        "✅ File berhasil dibaca."
    )


    # ========================================================
    # PREVIEW DATA
    # ========================================================

    st.subheader("Preview Data")

    st.dataframe(

        df.head(),

        use_container_width=True,

        hide_index=True
    )


    st.write(
        f"Jumlah baris: **{df.shape[0]}**"
    )

    st.write(
        f"Jumlah kolom: **{df.shape[1]}**"
    )


    # ========================================================
    # VALIDASI KOLOM
    # ========================================================

    kolom_hilang = [

        col

        for col in template_columns

        if col not in df.columns

    ]


    kolom_tambahan = [

        col

        for col in df.columns

        if col not in template_columns

    ]


    # ========================================================
    # KOLOM HILANG
    # ========================================================

    if len(kolom_hilang) > 0:

        st.error(
            "❌ File belum sesuai dengan template."
        )

        st.write(
            "**Kolom yang belum tersedia:**"
        )

        st.write(
            kolom_hilang
        )

        st.stop()


    # ========================================================
    # KOLOM TAMBAHAN
    # ========================================================

    if len(kolom_tambahan) > 0:

        st.warning(
            "⚠️ Terdapat kolom tambahan yang tidak digunakan."
        )

        st.write(
            kolom_tambahan
        )


    # ========================================================
    # VALIDASI TIPE DATA
    # ========================================================

    numeric_columns = (

        gt_features

        + official_features

    )


    kolom_non_numerik = []


    for col in numeric_columns:

        if col in df.columns:

            if not pd.api.types.is_numeric_dtype(
                df[col]
            ):

                kolom_non_numerik.append(col)


    if len(kolom_non_numerik) > 0:

        st.error(
            "❌ Variabel berikut harus berupa angka:"
        )

        st.write(
            kolom_non_numerik
        )

        st.stop()


    # ========================================================
    # VALIDASI MISSING VALUE
    # ========================================================

    missing = (

        df[numeric_columns]

        .isna()

        .sum()

    )


    missing = missing[
        missing > 0
    ]


    if len(missing) > 0:

        st.error(
            "❌ Terdapat nilai kosong."
        )

        st.dataframe(

            missing.rename(
                'Jumlah Missing Value'
            ),

            use_container_width=True
        )

        st.stop()


    # ========================================================
    # TOMBOL PREDIKSI
    # ========================================================

    st.header("3️⃣ Prediksi")


    if st.button(

        "🔮 Lakukan Prediksi",

        type='primary',

        use_container_width=True

    ):


        # ====================================================
        # CONTAINER HASIL
        # ====================================================

        hasil_prediksi = []

        error_list = []


        # ====================================================
        # LOOP 17 SEKTOR
        # ====================================================

        for sektor, info_model in model_dashboard.items():


            # ------------------------------------------------
            # INFORMASI MODEL
            # ------------------------------------------------

            skenario = info_model[
                'skenario'
            ]

            metode = info_model[
                'metode'
            ]

            model = info_model[
                'model'
            ]

            scaler_model = info_model[
                'scaler_model'
            ]


            # ------------------------------------------------
            # INFORMASI FITUR
            # ------------------------------------------------
            # fitur_input:
            # seluruh fitur yang masuk ke model
            #
            # fitur_aktif:
            # fitur yang memiliki koefisien != 0
            # pada Lasso / Elastic Net
            # ------------------------------------------------

            fitur_input = info_model[
                'fitur_input'
            ]

            jumlah_fitur_input = info_model[
                'jumlah_fitur_input'
            ]

            jumlah_fitur_aktif = info_model[
                'jumlah_fitur_aktif'
            ]


            # =================================================
            # SKENARIO S1, S2, S4
            # =================================================

            if skenario in [

                'S1',
                'S2',
                'S4'

            ]:


                # ---------------------------------------------
                # CEK FITUR
                # ---------------------------------------------

                fitur_hilang_model = [

                    fitur

                    for fitur in fitur_input

                    if fitur not in df.columns

                ]


                if len(
                    fitur_hilang_model
                ) > 0:

                    error_list.append({

                        'Sektor':
                            sektor,

                        'Masalah':
                        (
                            'Fitur model tidak ditemukan: '
                            + ', '.join(
                                fitur_hilang_model
                            )
                        )
                    })

                    continue


                # ---------------------------------------------
                # AMBIL FITUR
                # ---------------------------------------------

                X_input = df[
                    fitur_input
                ].copy()


            # =================================================
            # SKENARIO S3, S5
            # =================================================

            elif skenario in [

                'S3',
                'S5'

            ]:


                # ---------------------------------------------
                # AMBIL OBJEK PCA
                # ---------------------------------------------

                pca_scaler = info_model.get(
                    'pca_scaler'
                )

                pca = info_model.get(
                    'pca'
                )


                if (

                    pca_scaler is None

                    or pca is None

                ):

                    error_list.append({

                        'Sektor':
                            sektor,

                        'Masalah':
                            'Objek PCA tidak ditemukan.'
                    })

                    continue


                # ---------------------------------------------
                # NAMA FITUR GT UNTUK PCA
                # ---------------------------------------------

                # Versi baru .pkl menyimpan
                # nama fitur asli yang digunakan PCA.

                fitur_pca_input = info_model.get(
                    'fitur_pca_input'
                )


                # Jika tersedia, gunakan daftar tersebut.
                # Jika tidak tersedia, gunakan feature_names_in_
                # sebagai fallback.

                if fitur_pca_input is not None:

                    gt_pca_features = list(
                        fitur_pca_input
                    )

                elif hasattr(
                    pca_scaler,
                    'feature_names_in_'
                ):

                    gt_pca_features = list(
                        pca_scaler.feature_names_in_
                    )

                else:

                    error_list.append({

                        'Sektor':
                            sektor,

                        'Masalah':
                        (
                            'Nama fitur PCA tidak '
                            'ditemukan.'
                        )
                    })

                    continue


                # ---------------------------------------------
                # CEK FITUR GT
                # ---------------------------------------------

                fitur_gt_hilang = [

                    fitur

                    for fitur in gt_pca_features

                    if fitur not in df.columns

                ]


                if len(
                    fitur_gt_hilang
                ) > 0:

                    error_list.append({

                        'Sektor':
                            sektor,

                        'Masalah':
                        (
                            'Fitur Google Trends untuk '
                            'PCA tidak lengkap: '
                            + ', '.join(
                                fitur_gt_hilang
                            )
                        )
                    })

                    continue


                # ---------------------------------------------
                # AMBIL DATA GT
                # ---------------------------------------------

                X_gt = df[
                    gt_pca_features
                ].copy()


                # ---------------------------------------------
                # STANDARDISASI PCA
                # ---------------------------------------------

                X_gt_scaled = (

                    pca_scaler.transform(
                        X_gt
                    )

                )


                # ---------------------------------------------
                # TRANSFORMASI PCA
                # ---------------------------------------------

                X_pca = (

                    pca.transform(
                        X_gt_scaled
                    )

                )


                # ---------------------------------------------
                # NAMA PC
                # ---------------------------------------------

                pc_names = [

                    f'PC{i}'

                    for i in range(

                        1,

                        X_pca.shape[1] + 1

                    )

                ]


                X_pca_df = pd.DataFrame(

                    X_pca,

                    columns=pc_names,

                    index=df.index

                )


                # ---------------------------------------------
                # IDENTIFIKASI PC YANG DIBUTUHKAN
                # ---------------------------------------------

                pc_features = [

                    fitur

                    for fitur in fitur_input

                    if str(fitur)
                    .upper()
                    .startswith('PC')

                ]


                # ---------------------------------------------
                # STATISTIK RESMI
                # ---------------------------------------------

                official_model_features = [

                    fitur

                    for fitur in fitur_input

                    if fitur not in pc_features

                ]


                # ---------------------------------------------
                # GABUNGKAN INPUT
                # ---------------------------------------------

                input_parts = []


                if len(
                    pc_features
                ) > 0:

                    input_parts.append(

                        X_pca_df[
                            pc_features
                        ]

                    )


                if len(
                    official_model_features
                ) > 0:

                    input_parts.append(

                        df[
                            official_model_features
                        ].copy()

                    )


                X_input = pd.concat(

                    input_parts,

                    axis=1

                )


                # ---------------------------------------------
                # PASTIKAN URUTAN KOLOM SESUAI TRAINING
                # ---------------------------------------------

                X_input = X_input[
                    fitur_input
                ]


            # =================================================
            # MODEL TIDAK DIKENALI
            # =================================================

            else:

                error_list.append({

                    'Sektor':
                        sektor,

                    'Masalah':
                    (
                        f'Skenario {skenario} '
                        'tidak dikenali.'
                    )
                })

                continue


            # =================================================
            # SCALING INPUT MODEL
            # =================================================

            try:

                X_scaled = (

                    scaler_model.transform(
                        X_input
                    )

                )

            except Exception as e:

                error_list.append({

                    'Sektor':
                        sektor,

                    'Masalah':
                    (
                        'Gagal melakukan scaling: '
                        + str(e)
                    )
                })

                continue


            # =================================================
            # PREDIKSI
            # =================================================

            try:

                prediksi = model.predict(
                    X_scaled
                )

            except Exception as e:

                error_list.append({

                    'Sektor':
                        sektor,

                    'Masalah':
                    (
                        'Gagal melakukan prediksi: '
                        + str(e)
                    )
                })

                continue


            # =================================================
            # SIMPAN HASIL
            # =================================================

            hasil_prediksi.append({

                'Kode Sektor':
                    sektor,

                'Sektor':
                    nama_sektor.get(
                        sektor,
                        sektor
                    ),

                'Skenario':
                    skenario,

                'Model':
                    metode,

                'Jumlah Fitur Masuk':
                    jumlah_fitur_input,

                'Jumlah Fitur Aktif':
                    jumlah_fitur_aktif,

                'Prediksi PDB (Miliar Rupiah)':
                    round(
                        float(
                            prediksi[0]
                        ),
                        2
                    )

            })


        # ====================================================
        # HASIL PREDIKSI
        # ====================================================

        if len(
            hasil_prediksi
        ) > 0:


            st.header(
                "4️⃣ Hasil Prediksi"
            )


            df_hasil = pd.DataFrame(
                hasil_prediksi
            )


            st.success(

                "✅ Prediksi berhasil dilakukan "
                f"untuk {len(df_hasil)} sektor."

            )


            st.dataframe(

                df_hasil,

                use_container_width=True,

                hide_index=True

            )


            # =================================================
            # DOWNLOAD HASIL
            # =================================================

            hasil_buffer = BytesIO()


            with pd.ExcelWriter(

                hasil_buffer,

                engine='openpyxl'

            ) as writer:

                df_hasil.to_excel(

                    writer,

                    index=False,

                    sheet_name='Hasil Prediksi'

                )


            hasil_buffer.seek(0)


            st.download_button(

                label=
                    "⬇️ Download Hasil Prediksi",

                data=
                    hasil_buffer,

                file_name=
                    "hasil_prediksi_pdb.xlsx",

                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                )

            )


        # ====================================================
        # ERROR
        # ====================================================

        if len(
            error_list
        ) > 0:


            st.warning(

                "⚠️ Beberapa sektor tidak dapat "
                "diprediksi."

            )


            df_error = pd.DataFrame(
                error_list
            )


            st.dataframe(

                df_error,

                use_container_width=True,

                hide_index=True

            )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Dashboard Prediksi PDB Sektoral Indonesia"
)