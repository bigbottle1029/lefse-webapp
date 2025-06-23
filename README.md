# 🧬 LEfSe Web App

A user-friendly **Streamlit-based web interface** for running [LEfSe (Linear Discriminant Analysis Effect Size)](https://huttenhower.sph.harvard.edu/galaxy/) to identify differential features in microbiome or other compositional data.

![LEfSe Barplot and Cladogram](https://user-images.githubusercontent.com/your_screenshot_placeholder.png)

---

## 📦 Features

- 📤 Upload `.tsv` formatted feature table
- 🎛️ Configure LEfSe parameters via intuitive UI
- 📊 Automatically generate:
  - LDA barplot
  - Cladogram
  - Significant features table grouped by class
- ⬇️ Download all result images and CSV outputs

---

## 🛠️ Installation

```bash
git clone https://github.com/bigbottle1029/lefse-webapp.git
cd lefse-webapp

conda create -n lefseweb python=3.9
conda activate lefseweb
pip install -r requirements.txt



## 🚀 Run the App
streamlit run streamlit_lefse_app.py