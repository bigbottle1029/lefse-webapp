# LEfSe Web

> Modernized Web-Based Interface for LEfSe Microbial Biomarker Discovery Tool

---

## 🧬 Overview

**LEfSe Web** 是將經典 LEfSe (Linear Discriminant Analysis Effect Size) 微生物標記發現流程模組化，並搭配 Streamlit Web App 建立使用者友善界面。  
支援輸入處理、三階段統計分析（Kruskal-Wallis → Wilcoxon → LDA）、barplot 與 cladogram 可視化，並相容原始命令列操作。

---

## 🔧 Installation (via Conda)

建議使用 Conda 快速建立獨立環境並安裝所有依賴項，確保相容性與可重現性。

### Step 1: 建立 Conda 環境

```bash
conda create -n lefseweb python=3.8 -y
conda activate lefseweb
```

### Step 2: 安裝 Python 套件依賴

```bash
pip install -r requirements.txt
```

或手動安裝：

```bash
pip install streamlit matplotlib pandas seaborn scikit-learn scipy
```

### Step 3: 安裝 R 與必要套件

請先確認你已安裝 R（建議使用 R ≥ 4.0），可使用 RStudio 開啟並執行：

```r
install.packages(c("optparse", "MASS", "coin"))
```

---

## 📁 Project Structure

```
LEFSE/
├── lefse/
│   ├── lefse_format_input.py
│   ├── lefse_plot_cladogram.py
│   ├── lefse_plot_features.py
│   ├── lefse_plot_res.py
│   ├── lefse_run.py
│   └── lefse.py
├── lefsebiom/
│   ├── AbundanceTable.py
│   ├── ConstantsBreadCrumbs.py
│   ├── ValidateData.py
│   └── CClade.py
├── example/
├── tmp_lefse_run/
│   ├── barplot.png
│   ├── cladogram.png
│   ├── features.csv
│   ├── input.tsv
│   ├── result.res
├── output/
├── streamlit_lefse_app.py
├── extract_significant_features.py
├── README.md
├── requirements.txt
├── license.txt
├── setup.py
```

---

## 📥 Input Format

```
# Example:
class	A	A	B	B
subclass	a	b	a	b
asv1	0.1	0.2	0.3	0.1
asv2	0.5	0.1	0.2	0.9
```

- 第 1 行：分類變項（如 class）
- 第 2 行（可選）：次分類（如 subclass）
- 第 3 行起：特徵矩陣（如 ASV、蛋白、代謝物）

---

## 🚀 Web App 使用方式

```bash
streamlit run streamlit_lefse_app.py
```

1. 上傳格式化 `.tsv` 檔  
2. 設定 LDA 閾值、背景色、顯示設定  
3. 點擊「執行分析」  
4. 自動產生 cladogram 與 barplot  
5. 可下載圖片與結果檔  

---

## 🔧 CLI 使用方式

```bash
python -m lefse.lefse_format_input input.tsv tmp_lefse_run/input.in
python -m lefse.lefse_run tmp_lefse_run/input.in tmp_lefse_run/result.res
python -m lefse.lefse_plot_res tmp_lefse_run/result.res tmp_lefse_run/barplot.png --dpi 300 --format png
python -m lefse.lefse_plot_cladogram tmp_lefse_run/result.res tmp_lefse_run/cladogram.png
```

---

## 🛠 Requirements

```txt
Python >= 3.8
streamlit
matplotlib
pandas
seaborn
scikit-learn
scipy
```

R 套件：`optparse`, `MASS`, `coin`

---

## 📌 注意事項

- 原始 `lefse.py` 保留命令列相容性，但建議改用模組化接口（可讀性高）
- cladogram 與 barplot 均支援美化與色彩統一
- 當 feature 超過 ~1000 時 barplot 會自動報錯避免崩潰

---

## 🔮 Future Work

- ✅ WebApp: Streamlit 完整整合
- 📈 自定調色與 barplot clustering（進行中）
- 🧪 單純 Python 版本統計分析（移除對 R 依賴）
- ☁️ 部署版本（Docker / HuggingFace Spaces）

---

## 📜 License

See `license.txt`

---

如需協助格式轉換與功能擴充，歡迎提交 issue 或聯絡作者。

如需協助格式轉換與功能擴充，歡迎 issue 或聯絡作者。
