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
with col2:
    lda_th     = st.slider("LDA threshold", 0.0, 10.0, 2.0, 0.1)
    run_wilcox = st.checkbox("Run Wilcoxon test", value=True)




# === 初始化顏色映射 ===
if "class_colors_map" not in st.session_state:
    st.session_state.class_colors_map = {}

# === 讀入資料並抓取 class 名稱 ===
try:
    df_input = pd.read_csv(uploaded, sep="\t", index_col=0, header=None)
    # 🧠 class_row 是 1-based index，因此要 -1
    class_row_name = df_input.index[class_row - 1]
    class_row_vals = df_input.loc[class_row_name]
    class_row_vals.name = class_row_name  # 關鍵！正確標示 column 名
    class_row_vals.index.name = "Sample"  # 樣本 ID 當 index

except Exception as e:
    st.warning(f"⚠️ 無法讀取 class 名稱：{e}")
    class_names = []
    class_row_vals = pd.Series([])






# ✅ 正確取出 class 名稱
class_names = sorted(class_row_vals.dropna().unique().tolist())

# === 顯示 class 顏色選擇器 ===
st.markdown("🎨 選擇各個 class 的顏色：")
for cls in class_names:
    default_color = st.session_state.class_colors_map.get(cls, "#%06x" % (hash(cls) & 0xFFFFFF))
    picked_color = st.color_picker(f"{cls}", default_color, key=f"color_{cls}")
    st.session_state.class_colors_map[cls] = picked_color

# === 整理為 --colors 字串格式 ===
class_colors_str = ",".join(st.session_state.class_colors_map[c] for c in class_names)

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

    # Step 3️⃣: extract features.csv
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
        result_res, bar_png,
        "--dpi", "300",
        "--format", "png",
        "--colors", class_colors_str,
        "--title", "",                  # ✅ 必加
        "--feature_font_size", "8",     # ✅ 依需求調整
        "--class_legend_font_size", "10",
        "--background_color", "w"  # ✅ 這一行是關鍵
    ]


    bar = subprocess.run(cmd_bar, capture_output=True, text=True)
    if bar.returncode != 0:
        st.error("❌ Barplot generation failed")
        st.text(bar.stderr)
        st.stop()
    else:
        st.text("✅ barplot subprocess completed")
        st.text(bar.stdout)
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
        "--colors", class_colors_str
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