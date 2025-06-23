import pandas as pd

def extract_significant_features(res_path, out_csv_path):
    """
    從 LEfSe 的 result.res 中挑出顯著特徵（有 class 的），輸出成 csv。
    """
    with open(res_path) as f:
        lines = [line.strip().split('\t') for line in f if line.strip()]

    records = []
    for line in lines:
        if len(line) == 5 and line[2] not in ['', '-']:
            feature = line[0]
            class_label = line[2]
            lda_score = float(line[3])
            pvalue = float(line[4])
            records.append((class_label, feature, lda_score, pvalue))

    if not records:
        print("⚠ No significant features found in:", res_path)
        return

    df = pd.DataFrame(records, columns=["class", "feature", "LDA_score", "pvalue"])
    df.sort_values(by=["class", "pvalue", "LDA_score"], ascending=[True, True, False], inplace=True)
    df.to_csv(out_csv_path, index=False)
    print(f"✅ Extracted {len(df)} significant features → {out_csv_path}")
