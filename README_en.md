# LEfSe Web - A Modern Web Interface for LEfSe Analysis

LEfSe Web is a modernized web-based interface for performing LEfSe (Linear discriminant analysis Effect Size) analysis. This project wraps the classic LEfSe pipeline into a modular Python + Streamlit application, allowing users to upload data, run statistical tests, and visualize results via a user-friendly web app.

## 📁 Project Structure

```
.
├── lefse/                    # Core LEfSe pipeline (refactored)
│   ├── lefse_format_input.py     # Format input table for LEfSe analysis
│   ├── lefse_plot_cladogram.py  # Draw cladogram visualization
│   ├── lefse_plot_features.py   # Optional features plot
│   ├── lefse_plot_res.py        # Draw LDA barplot
│   ├── lefse_run.py             # Run LEfSe main analysis logic
│   └── lefse.py                 # Legacy interface or utility functions
│
├── lefsebiom/                # BIOM file support (if applicable)
│   ├── AbundanceTable.py
│   ├── CClade.py
│   ├── ConstantsBreadCrumbs.py
│   └── ValidateData.py
│
├── streamlit_lefse_app.py   # Streamlit web app entry point
├── extract_significant_features.py  # Utility: export significant features by class
├── requirements.txt         # Required Python packages
├── README.md                # Documentation (this file)
├── license.txt              # License file
├── output/                  # Exported results (customizable)
└── tmp_lefse_run/           # Temporary working directory
    ├── input.tsv
    ├── result.res
    ├── features.csv
    ├── barplot.png
    ├── cladogram.png
    └── significant_features_by_class.csv
```

## 🧪 Input Format

Input should be a tab-delimited `.tsv` file with the first two rows indicating class and subclass labels, and subsequent rows showing feature abundances.

Example:
```
class     A     A     B     B
subclass  a     b     a     b
asv1      0.1   0.2   0.5   0.4
asv2      0.0   0.1   0.6   0.3
...
```

## 🚀 How to Run

### A. Web Mode (Recommended)
```bash
streamlit run streamlit_lefse_app.py
```
- Upload your input `.tsv` file via UI
- Select LDA threshold (e.g., 2.0)
- Run and visualize results: barplot + cladogram
- Download result files from sidebar

### B. Command Line (Advanced)
```bash
# 1. Format input
python -m lefse.lefse_format_input input.tsv tmp_lefse_run/input.in

# 2. Run LEfSe
python -m lefse.lefse_run tmp_lefse_run/input.in tmp_lefse_run/result.res

# 3. Draw barplot
python -m lefse.lefse_plot_res tmp_lefse_run/result.res tmp_lefse_run/barplot.png   --dpi 300 --format png --title "" --feature_font_size 8 --class_legend_font_size 10

# 4. Draw cladogram
python -m lefse.lefse_plot_cladogram tmp_lefse_run/result.res tmp_lefse_run/cladogram.png
```

### C. Extract significant features (optional)
```bash
python extract_significant_features.py tmp_lefse_run/result.res tmp_lefse_run/significant_features_by_class.csv
```

## 📦 Requirements

Install required packages with:
```bash
pip install -r requirements.txt
```

## 🛠️ Features

- ✅ Web-based LEfSe runner (Streamlit)
- ✅ Modular Python wrappers for LEfSe pipeline
- ✅ Auto-generated barplot & cladogram with publication-ready style
- ✅ Per-class significant feature extraction (CSV)
- ✅ Support for custom class colors, DPI, and LDA threshold

## 🧩 Future Plans

- [ ] Upload support for BIOM + metadata
- [ ] Export cladogram as interactive SVG/HTML
- [ ] Feature filtering by subclass or taxonomy
- [ ] Dockerized deployment

---

This is an enhanced and modernized interface for microbiome researchers and bioinformatics practitioners who wish to run LEfSe analysis in an intuitive, visual, and modular way.