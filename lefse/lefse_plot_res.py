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
    parser.add_argument('--title',                dest="title",                type=str,   default="",  help="Plot title")
    parser.add_argument('--feature_font_size',    dest="feature_font_size",    type=int,   default=7)
    parser.add_argument('--class_legend_font_size',dest="class_legend_font_size",type=int,  default=10)
    parser.add_argument('--format',               dest="format",    choices=["png","svg","pdf"], default='png')
    parser.add_argument('--dpi',                  dest="dpi",       type=int,   default=300)
    parser.add_argument('--width',                dest="width",     type=float, default=7.0)
    parser.add_argument('--height',               dest="height",    type=float, default=4.0)
    parser.add_argument('--left_space',           dest="ls",        type=float, default=0.2)
    parser.add_argument('--right_space',          dest="rs",        type=float, default=0.1)
    parser.add_argument('--orientation',          dest="orientation",choices=["h","v"], default="h")
    parser.add_argument('--autoscale',            dest="autoscale", choices=[0,1], default=1, type=int)
    parser.add_argument('--background_color',     dest="back_color",choices=["k","w"], default="w")
    parser.add_argument('--n_scl',                dest="n_scl",     type=int,   default=1,
                        help="Number of leaf levels to show (1=last level only)")
    parser.add_argument('--max_feature_len',      dest="max_feature_len", type=int, default=60)
    parser.add_argument('--otu_only',             dest="otu_only", action='store_true',
                        help="Plot only OTU-level features (length==8)")
    parser.add_argument('--report_features',      dest="report_features", action='store_true',
                        help="Print feature list (feature, LDA, class) to stdout")
    parser.add_argument('--colors',               dest="colors",    type=str,   default="",
                        help="Comma-separated color list for each class (in sorted order)")
    return vars(parser.parse_args())

def read_data(input_file, otu_only):
    with open(input_file, 'r') as inp:
        lines = [line.strip().split() for line in inp if len(line.strip().split()) > 3]
    if otu_only:
        lines = [ln for ln in lines if len(ln[0].split('.')) == 8]
    classes = sorted({ln[2] for ln in lines})
    return {'rows': lines, 'cls': classes}

def get_color_map(classes, colors_arg):
    # 如果用户传了 --colors，就用它
    if colors_arg:
        cols = [c.strip() for c in colors_arg.split(',')]
        if len(cols) != len(classes):
            raise ValueError(f"--colors 要求 {len(classes)} 个值，您给了 {len(cols)}")
        return dict(zip(classes, cols))
    # 否则用 matplotlib 默认循环
    cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']
    return {cls: cycle[i % len(cycle)] for i, cls in enumerate(classes)}

def plot_hor(path, params, data):
    rows = data['rows']
    classes = data['cls']
    two_class = len(classes) == 2

    # 排序：如果双组，则根据方向画正负，否则统一正向并按 class 排序
    if two_class:
        rows.sort(key=lambda ab: abs(float(ab[3])) * (classes.index(ab[2])*2-1))
    else:
        mmax = max(abs(float(ab[3])) for ab in rows)
        rows.sort(key=lambda ab: abs(float(ab[3]))/mmax + (classes.index(ab[2])+1))

    pos = list(range(len(rows)))
    fig = plt.figure(
        figsize=(params['width'], len(rows)*0.2 + 1.0),
        facecolor=params['back_color'], edgecolor=params['back_color']
    )
    ax = fig.add_subplot(1,1,1, facecolor=params['back_color'])
    plt.subplots_adjust(left=params['ls'], right=1-params['rs'],
                        top=0.9, bottom=0.1)

    color_map = get_color_map(classes, params['colors'])

    # 若要打印 feature 列表
    out_data = defaultdict(list)

    for i, row in enumerate(rows):
        feat, _, grp, lda, *rest = row
        score = abs(float(lda))
        if params['report_features']:
            out_data[feat] = [lda, grp]

        col = color_map[grp]
        val = score * ((-1) if (two_class and classes.index(grp)==1) else 1)
        label = grp if (i==0 or rows[i-1][2] != grp) else ""
        ax.barh(i, val,
                color=col,
                edgecolor=params['fore_color'],
                height=0.8,
                label=label)

    if params['report_features']:
        print("Feature\tLDA_score\tClass")
        for f, v in out_data.items():
            print(f"{f}\t{v[0]}\t{v[1]}")

    # 在条形上写名字
    for i, row in enumerate(rows):
        feat = row[0]
        parts = feat.split('.')
        if params['n_scl'] > 0:
            disp = parts[-params['n_scl']:]
        else:
            disp = parts
        lbl = ".".join(disp)
        if len(lbl) > params['max_feature_len']:
            lbl = lbl[:params['max_feature_len']//2] + "… " + lbl[-params['max_feature_len']//2:]
        align = {'ha': 'left'} if two_class and (classes.index(row[2])==0) else {'ha': 'right'}
        ax.text(0, i, lbl,
                va='center',
                color=params['fore_color'],
                size=params['feature_font_size'],
                **align)

    ax.set_yticks([])
    ax.set_xlabel("LDA SCORE (log10)", color=params['fore_color'])
    ax.xaxis.grid(True, color=params['fore_color'])

    # 图例
    handles, labels = ax.get_legend_handles_labels()
    leg = ax.legend(handles, labels,
                    ncol=len(classes),
                    frameon=False,
                    loc='upper center',
                    bbox_to_anchor=(0.5,1.05),
                    prop={'size': params['class_legend_font_size']})
    for txt in leg.get_texts():
        txt.set_color(params['fore_color'])

    # 标题
    ax.set_title(params['title'], color=params['fore_color'])

    # 保存
    plt.savefig(path,
                dpi=params['dpi'],
                format=params['format'],
                facecolor=params['back_color'],
                edgecolor=params['fore_color'])
    plt.close()

def plot_ver(path, params, data):
    # 简化实现：纵向也调用横向，若需要可以专门重写
    plot_hor(path, params, data)

def plot_res():
    params = read_params(sys.argv)
    # 前景色（文字/边框）取反
    params['fore_color'] = 'w' if params['back_color']=='k' else 'k'

    data = read_data(params['input_file'], params['otu_only'])

    if params['orientation']=='h':
        plot_hor(params['output_file'], params, data)
    else:
        plot_ver(params['output_file'], params, data)

if __name__ == '__main__':
    plot_res()
