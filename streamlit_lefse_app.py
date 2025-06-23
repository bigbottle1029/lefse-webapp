import streamlit as st
import subprocess, os, sys
import pandas as pd
from extract_significant_features import extract_significant_features

st.set_page_config(page_title="LEfSe WebApp", layout="wide")
st.title("🔬 LEfSe Analysis Web")

# === 上傳資料 ===
uploaded = st.file_uploader("Upload feature table (.tsv)", type="tsv")
if not uploaded:
    st.stop()

# === 分組參數 ===
col1, col2 = st.columns(2)
with col1:
    class_row    = st.number_input("Class row index (1-based)", min_value=1, value=1)
    subclass_row = st.number_input("Subclass row index (0 to skip)", min_value=0, value=2)
    subject_row  = st.number_input("Subject row index (0 to skip)", min_value=0, value=0)
    class_colors = st.text_input("Class colors (comma-separated)", value="coral,mediumturquoise")
with col2:
    lda_th     = st.slider("LDA threshold", 0.0, 10.0, 2.0, 0.1)
    run_wilcox = st.checkbox("Run Wilcoxon test", value=True)

# === 點選分析 ===
if st.button("Run LEfSe"):
    workdir = "tmp_lefse_run"
    os.makedirs(workdir, exist_ok=True)
    in_tsv = os.path.join(workdir, "input.tsv")
    with open(in_tsv, "wb") as f:
        f.write(uploaded.getbuffer())

    # Step 1️⃣: format input
    in_for_lefse = os.path.join(workdir, "input.in.for_lefse")
    cmd_fmt = [
        sys.executable, "-m", "lefse.lefse_format_input",
        in_tsv, in_for_lefse, "-c", str(class_row), "-o", "1000000"
    ]
    if subclass_row: cmd_fmt += ["-s", str(subclass_row)]
    if subject_row:  cmd_fmt += ["-u", str(subject_row)]
    fmt = subprocess.run(cmd_fmt, capture_output=True, text=True)
    if fmt.returncode != 0:
        st.error(f"❌ Format input failed:\n{fmt.stderr}")
        st.stop()

    # Step 2️⃣: run LEfSe
    result_res = os.path.join(workdir, "result.res")
    cmd_lefse = [
        sys.executable, "-m", "lefse.lefse_run",
        in_for_lefse, result_res, "-l", str(lda_th)
    ]
    if not run_wilcox:
        cmd_lefse += ["--wilc", "0"]
    lef = subprocess.run(cmd_lefse, capture_output=True, text=True)
    if lef.returncode != 0:
        st.error(f"❌ LEfSe failed:\n{lef.stderr}")
        st.stop()

    # Step 3️⃣: extract features.csv (raw from result.res)
    df = pd.read_csv(result_res, sep="\t", header=None)
    if df.shape[1] == 5:
        df.columns = ["feature", "LDA", "_", "class", "pvalue"]
    else:
        df.columns = ["feature", "LDA", "pvalue"]
    df_feat = df[df["LDA"].abs() >= lda_th][["feature", "LDA", "pvalue"]]
    features_csv = os.path.join(workdir, "features.csv")
    df_feat.to_csv(features_csv, index=False)

    # Step 4️⃣: barplot
    bar_png = os.path.join(workdir, "barplot.png")
    cmd_bar = [
        sys.executable, "-m", "lefse.lefse_plot_res",
        result_res, bar_png, "--dpi", "300", "--format", "png",
        "--colors", class_colors
    ]
    subprocess.run(cmd_bar, capture_output=True, text=True)
    if os.path.exists(bar_png):
        st.image(bar_png, caption="LDA Barplot", use_container_width=True)
        with open(bar_png, "rb") as f:
            st.download_button("📥 Download barplot.png", f, "barplot.png", key="dl_bar")

    # Step 5️⃣: cladogram
    clad_png = os.path.join(workdir, "cladogram.png")
    cmd_clad = [
        sys.executable,
        "lefse/lefse_plot_cladogram.py",
        result_res,
        clad_png,
        "--dpi", "300",
        "--format", "png",
        "--colors", class_colors
    ]
    clad = subprocess.run(cmd_clad, capture_output=True, text=True)
    if os.path.exists(clad_png):
        st.image(clad_png, caption="Cladogram", use_container_width=True)
        with open(clad_png, "rb") as f:
            st.download_button("📥 Download cladogram.png", f, "cladogram.png", key="dl_clad")
    else:
        st.warning("⚠️ Cladogram image not found")

    # Step 6️⃣: extract significant features by class
    sigfeat_csv = os.path.join(workdir, "significant_features_by_class.csv")
    extract_significant_features(result_res, sigfeat_csv)
    if os.path.exists(sigfeat_csv):
        with open(sigfeat_csv, "rb") as f:
            st.download_button("📥 Download significant features", f, "significant_features_by_class.csv", key="dl_sig")

    st.success("✅ LEfSe Analysis Complete!")




