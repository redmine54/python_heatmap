# ------------------------------------
# px_size x px_sizeの相関行列を乱数で生成
#（対角要素以外は-0.8, 0.8の乱数）
#
import os
import numpy as np
import pandas as pd
import random
import matplotlib as mpl
import matplotlib.pyplot as plt
import io
import base64

pd.options.display.float_format = '{:.3f}'.format
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
# ----------------------------------
# パラメータ
px_size = 300
color_map = ['r','magenta','w','w','w','w','w','w','w','g','blue']
figsize = (100, 80)
dpi=100
R2Sq_Top = 20
NumbOfDataSource=500
title="ヒートマップ"

# html base
HTML_TMP = '''
<!doctype html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>ヒートマップ</title>
<style>
</style>
</head>
  <body style="margin: 0px; padding:0px">
    <div style="margin: 0px; padding:0px">
    <img src="data:image/png;base64,{image_bin}" style="margin: 0px; padding:0px">
    </div>
  </body>
</html>
'''
# ----------------------------------
# matlab imageをhtmlへ埋め込み
#
def img2html(fig):
    sio = io.BytesIO()
    fig.savefig(sio, format='png')
    image_bin = base64.b64encode(sio.getvalue())
    return HTML_TMP.format(image_bin=str(image_bin)[2:-1])

# ----------------------------------
# 相関係数マトリックスを生成
#
def get_random_image(px_size):
    # テスト用のDataFrameを作る
    df=pd.DataFrame()
    for i in range(px_size):
        col=np.random.rand(NumbOfDataSource)
        df2 = pd.DataFrame(col,columns=[i])
        df=pd.concat([df,df2],axis=1)

    #　相関係数算出
    res=df.corr()   # pandasのDataFrameに格納される

    # 生成した相関係数をヒートマップ用に、−１〜１の範囲に拡大（仮）
    res_max=0
    for i,xary in res.iterrows():
        for j,val in enumerate(xary):
            if j<i:
                if abs(val)>res_max:
                    res_max=abs(val)
    for i,xary in res.iterrows():
        for j,val in enumerate(xary):
            if j!=i:
                val=res.iat[i,j]
                res.iat[i,j]=res.iat[i,j]/res_max

    return res

# -----------------------------------
# ヒートマップのカラーマップ生成
#
def gen_cmap_name(cols):
    nmax = float(len(cols)-1)
    color_list = []
    for n, c in enumerate(cols):
        color_list.append((n/nmax, c))
    return mpl.colors.LinearSegmentedColormap.from_list('cmap', color_list)

# --------------------------------------
# main()
#
def main(ext):
    # ----------------------------------
    # 相関行列を生成しヒートマップ表示
    image=get_random_image(px_size)  # 相関行列を生成

    #image=image.drop(image.index[[1, 3, 5]])

    cmap = gen_cmap_name(color_map)  # ヒートマップのカラーマップ生成
    # ヒートマップ表示
    fig = plt.figure(figsize=figsize, dpi=dpi)
    plt.imshow(image, cmap=cmap, vmin=-1.0, vmax=1.0)
    plt.colorbar()
    plt.title(title)

    html = img2html(fig)
    if ext=='.py':
        plt.close()

    plt.savefig(f"./out/{title}.png")
    with open(f"./out/{title}.html", "w") as w:
        w.write(html)


    print(image.shape)

    image.reset_index(drop=True, inplace=True)

    # ---------------------
    # 相関データからデータと寄与率(R2Squere)をpandasに取り出す
    list = []
    for i,xary in image.iterrows():
        for j,val in enumerate(xary):
            list.append([i,j, val, val*val])
    df=pd.DataFrame(list,columns=['x','y','value','R2Sq'])

    # R2Seqの降順ソート
    sorted_df = df.sort_values("R2Sq",ascending=False) # 降順
    i=0
    for index, row in sorted_df.iterrows():
        if row['y']>row['x']:
            i=i+1
            if i<=R2Sq_Top:
                print('{:4}'.format(int(row['x'])),
                      '{:4}'.format(int(row['y'])),
                      '{:8.3f}'.format(row['value']),
                      '{:8.3f}'.format(row['R2Sq']))

if __name__=='__main__':
    # 本プログラム拡張子（'.py' or '.ipynb'）
    try:
        ext = os.path.splitext(__file__)[1]
    except:
        ext = '.ipynb'
    main(ext)
