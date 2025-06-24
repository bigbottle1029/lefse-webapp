# LEfSe Web

> Modernized Web-Based Interface for LEfSe Microbial Biomarker Discovery Tool

---

## 🧬 Overview

LEfSe Web 是將經典 LEfSe (Linear Discriminant Analysis Effect Size) 微生物標記發現流程模組化，並搭配 Streamlit Web App 建立使用者友善界面。支援輸入處理、三階段統計分析（Kruskal-Wallis → Wilcoxon → LDA）、barplot 與 cladogram 可視化，並相容原始命令列操作。

---

## 📁 Project Structure

```
LEFSE/
├── lefse/                         # 核心模組（模組化後的原始 LEfSe 腳本）
│   ├── lefse_format_input.py     # 格式轉換
│   ├── lefse_plot_cladogram.py   # 畫 cladogram
│   ├── lefse_plot_features.py    # 萃取特徵
│   ├── lefse_plot_res.py         # 畫 barplot（新版 seaborn 美化）
│   ├── lefse_run.py              # 分析主程式（呼叫 R 做統計 + Python 做 LDA）
│   └── lefse.py                  # CLI 接口（保留）
│
├── lefsebiom/                    # 輔助類別（原始 LEfSe 的解析與驗證模組）
│   ├── AbundanceTable.py
│   ├── ConstantsBreadCrumbs.py
│   ├── ValidateData.py
│   └── CClade.py
│
├── example/                      # 範例數據（建議自行新增）
│
├── tmp_lefse_run/               # 預設暫存執行資料夾（含中間結果與圖片）
│   ├── barplot.png
│   ├── cladogram.png
│   ├── features.csv             # 符合 LDA 門檻的特徵清單
│   ├── input.tsv                # 處理後輸入
│   ├── result.res               # 分析結果主檔
│
├── output/                      # 使用者指定輸出資料夾（可自訂）
│
├── streamlit_lefse_app.py      # Streamlit Web App 主程式
├── extract_significant_features.py # CLI 方式萃取重要特徵
├── README.md                    # 本文件
├── requirements.txt             # Python 套件需求
├── license.txt
├── setup.py                     # 安裝模組（未必需要）
```

---

## 📥 Input Format

輸入檔案為 tab-delimited `.tsv`，符合 LEfSe 標準格式：

```
#Example:
class	A	A	B	B
subclass	a	b	a	b
asv1	0.1	0.2	0.3	0.1
asv2	0.5	0.1	0.2	0.9
```

- 第 1 行：分類變項（如 class）
- 第 2 行（可選）：次分類（如 subclass）
- 第 3 行起：feature（如 ASV、蛋白、代謝物），行名為特徵 ID

---

## 🚀 Web App 使用方式

```bash
# 啟動 web server
streamlit run streamlit_lefse_app.py
```

1. 上傳格式化 `.tsv` 檔
2. 設定 LDA 閾值、背景色、顯示設定
3. 點擊「執行分析」
4. 自動產生 cladogram 與 barplot
5. 可下載圖片與結果檔

---

## 🔧 CLI 使用方式

你也可完全以命令列操作模組：

```bash
# Step 1: 格式化輸入
python -m lefse.lefse_format_input input.tsv tmp_lefse_run/input.in

# Step 2: 執行分析（不再依賴 rpy2，改為呼叫 Rscript）
python -m lefse.lefse_run tmp_lefse_run/input.in tmp_lefse_run/result.res

# Step 3: barplot
python -m lefse.lefse_plot_res tmp_lefse_run/result.res tmp_lefse_run/barplot.png --dpi 300 --format png

# Step 4: cladogram
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
（詳細請見 `requirements.txt`）

R 套件：
- `optparse`
- `MASS`
- `coin`

---

## 📌 注意事項

- 原始 `lefse.py` 仍保留命令列相容性，但建議改用模組化接口（可讀性高）
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

如需協助格式轉換與功能擴充，歡迎 issue 或聯絡作者。