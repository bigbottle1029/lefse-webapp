#!/usr/bin/env python3

import os
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import defaultdict
import argparse

def read_params(args):
    parser = argparse.ArgumentParser(description='Plot LEfSe LDA results')
    parser.add_argument('input_file',  metavar='INPUT_FILE',  type=str, help="tab-delimited LEfSe result file")
    parser.add_argument('output_file', metavar='OUTPUT_FILE', type=str, help="output image path")
    parser.add_argument('--title', type=str, default="", help="Plot title")
    parser.add_argument('--feature_font_size', type=int, default=7)
    parser.add_argument('--class_legend_font_size', type=int, default=10)
    parser.add_argument('--format', choices=["png","svg","pdf"], default='png')
    parser.add_argument('--dpi', type=int, default=300)
    parser.add_argument('--width', type=float, default=7.0)
    parser.add_argument('--height', type=float, default=4.0)
    parser.add_argument('--left_space', dest="ls", type=float, default=0.2)
    parser.add_argument('--right_space', dest="rs", type=float, default=0.1)
    parser.add_argument('--orientation', choices=["h","v"], default="h")
    parser.add_argument('--autoscale', choices=[0,1], default=1, type=int)
    parser.add_argument('--background_color', choices=["k","w"], default="w")
    parser.add_argument('--n_scl', type=int, default=1)
    parser.add_argument('--max_feature_len', type=int, default=60)
    parser.add_argument('--otu_only', action='store_true')
    parser.add_argument('--report_features', action='store_true')
    parser.add_argument('--colors', type=str, default="")
    return vars(parser.parse_args())

def read_data(input_file, otu_only):
    with open(input_file, 'r') as inp:
        lines = [line.strip().split() for line in inp if len(line.strip().split()) > 3]
    if otu_only:
        lines = [ln for ln in lines if len(ln[0].split('.')) == 8]
    classes = sorted({ln[2] for ln in lines})
    return {'rows': lines, 'cls': classes}

def get_color_map(classes, colors_arg):
    if colors_arg:
        cols = [c.strip() for c in colors_arg.split(',')]
        if len(cols) != len(classes):
            raise ValueError(f"--colors 要求 {len(classes)} 个值，您给了 {len(cols)}")
        return dict(zip(classes, cols))
    cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']
    return {cls: cycle[i % len(cycle)] for i, cls in enumerate(classes)}

def plot_hor(path, params, data):
    rows = data['rows']
    classes = data['cls']
    if not rows:
        print("[ERROR] No features to plot.")
        return

    print(f"[INFO] Plotting {len(rows)} features for classes: {classes}")
    two_class = len(classes) == 2

    if two_class:
        rows.sort(key=lambda ab: abs(float(ab[3])) * (classes.index(ab[2])*2-1))
    else:
        mmax = max(abs(float(ab[3])) for ab in rows)
        rows.sort(key=lambda ab: abs(float(ab[3]))/mmax + (classes.index(ab[2])+1))

    fig = plt.figure(figsize=(params['width'], len(rows)*0.2 + 1.0),
                     facecolor=params['background_color'], edgecolor=params['background_color'])
    ax = fig.add_subplot(1,1,1, facecolor=params['background_color'])
    plt.subplots_adjust(left=params['ls'], right=1-params['rs'],
                        top=0.9, bottom=0.1)

    color_map = get_color_map(classes, params['colors'])

    out_data = defaultdict(list)

    for i, row in enumerate(rows):
        feat, _, grp, lda, *rest = row
        score = abs(float(lda))
        if params['report_features']:
            out_data[feat] = [lda, grp]

        try:
            col = color_map[grp]
            val = score * ((-1) if (two_class and classes.index(grp)==1) else 1)
            label = grp if (i==0 or rows[i-1][2] != grp) else ""
            ax.barh(i, val,
                    color=col,
                    edgecolor=params['fore_color'],
                    height=0.8,
                    label=label)
        except Exception as e:
            print(f"[ERROR] Failed to draw bar for {feat}: {e}")

    if params['report_features']:
        print("Feature\tLDA_score\tClass")
        for f, v in out_data.items():
            print(f"{f}\t{v[0]}\t{v[1]}")

    mv = max([abs(float(v[3])) for v in rows])  # 最大的 LDA 值，供定位用

    for i, r in enumerate(rows):
        indcl = classes.index(r[2])
        feat = r[0]
        parts = feat.split('.')
        disp = parts[-params['n_scl']:] if params['n_scl'] > 0 else parts
        lbl = ".".join(disp)
        if len(lbl) > params['max_feature_len']:
            lbl = lbl[:params['max_feature_len']//2 - 2] + " [..]" + lbl[-params['max_feature_len']//2 + 2:]

        try:
            lda_score = float(r[3])
            sign = 1 if (classes.index(r[2]) == 0) else -1
            if sign < 0:
                ax.text(mv/40.0, float(i)-0.3, lbl,
                        ha='left', va='baseline', color=params['fore_color'],
                        size=params['feature_font_size'])
            else:
                ax.text(-mv/40.0, float(i)-0.3, lbl,
                        ha='right', va='baseline', color=params['fore_color'],
                        size=params['feature_font_size'])
        except Exception as e:
            print(f"[WARN] Failed to label {feat}: {e}")


    ax.set_yticks([])
    ax.set_xlabel("LDA SCORE (log10)", color=params['fore_color'])
    ax.xaxis.grid(True, color=params['fore_color'])

    try:
        handles, labels = ax.get_legend_handles_labels()
        if handles and labels:
            leg = ax.legend(handles, labels,
                            ncol=len(classes),
                            frameon=False,
                            loc='upper center',
                            bbox_to_anchor=(0.5,1.05),
                            prop={'size': params['class_legend_font_size']})
            for txt in leg.get_texts():
                txt.set_color(params['fore_color'])
    except Exception as e:
        print(f"[WARN] Failed to create legend: {e}")

    ax.set_title(params['title'], color=params['fore_color'])

    try:
        plt.savefig(path,
                    dpi=params['dpi'],
                    format=params['format'],
                    facecolor=params['background_color'],
                    edgecolor=params['fore_color'])
        print(f"[INFO] Barplot saved to: {path}")
    except Exception as e:
        print(f"[ERROR] Failed to save figure: {e}")
    plt.close()

def plot_ver(path, params, data):
    plot_hor(path, params, data)

def plot_res():
    params = read_params(sys.argv)
    params['fore_color'] = 'w' if params.get('background_color', 'w') == 'k' else 'k'
    data = read_data(params['input_file'], params['otu_only'])

    if params['orientation']=='h':
        plot_hor(params['output_file'], params, data)
    else:
        plot_ver(params['output_file'], params, data)

if __name__ == '__main__':
    plot_res()
