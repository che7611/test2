import pandas as pd
import datetime as dt
import pymysql
import matplotlib.pyplot as plt
from matplotlib.lines import TICKLEFT, TICKRIGHT, Line2D
from matplotlib.patches import Rectangle
import matplotlib as mpl
import matplotlib.dates as mdate
from datetime import time

class Kline(object):
    def DrawKline(self,aa):
    #     date='2014-01-03'
        # aa=df1[str(date)]
        aa.reset_index(drop=True,inplace=True)
        fig =plt.figure(figsize=(30, 12),facecolor='w')

        #副图是主图的比例
        w1=0.25
        w2=0.8/(1+w1)*w1
        rec1=[0.1,0.1+w2,0.9,w2/w1]
        rec2=[0.1,0.1,0.9,w2]
        ax=fig.add_axes(rec1)
        ax1=fig.add_axes(rec2,sharex=ax)
        plt.setp(ax.get_xticklabels(), visible=False)
        plt.setp(ax1.get_xticklabels(), visible=True)

        #设置时间刻度
        dlist=aa.datetime.apply(lambda x:str(x.time()))
        dd=dlist.values
        d1=[i*100 for i in range(len(dd))]
        ax1.set_xticks(d1[::30])
        ax1.set_xticklabels(dd[::30])

        Kline={}
        Kline['W'] = 80
        Kline['Diff'] = 20
        Kline['WW']=100
        d=0
        rows=len(aa)
        for i in aa.iterrows():
            Row=i[1]
            x1 =(d+1)*Kline['WW']
            x2 = x1-Kline['W']/2
            O = Row['open']
            C = Row['close']
            L = Row['low']
            H = Row['high']
            hh = abs(C - O)

            if C > O:
                a = False
                y = O
                cc = 'R'
                # 上影线 下影线
                line1 = Line2D((x1, x1), (C, H), color=cc)
                line2 = Line2D((x1, x1), (O, L), color=cc)

                ax.add_line(line1)
                ax.add_line(line2)
            else:
                a = True
                y = C
                cc = 'C'
                # 影线
                line = Line2D((x1, x1), (L, H), color=cc)
                ax.add_line(line)
            hh = abs(C - O)

            # K线实体
            rec = Rectangle((x2, y), Kline['W'], hh, fill=a, color=cc)
            ax.add_patch(rec)

            if Row['MACD']>0:
                rec= Rectangle((x2, 0), Kline['W'], Row['MACD'], fill=a, color='R')
            else:
                rec= Rectangle((x2, 0), Kline['W'], Row['MACD'], fill=a, color='C')
            ax1.add_patch(rec)
            d+=1
        if "MA60" in aa.columns:
            ax.plot(aa.index*Kline['WW']+Kline['WW'],aa['MA60'],c='r')
        if "MA30" in aa.columns:
            ax.plot(aa.index*Kline['WW']+Kline['WW'],aa['MA30'],c='b')
        ax1.axhline(0,linestyle="--",linewidth=0.5,color='k')
        if "DIFF" in aa.columns:
            ax1.plot(aa.index*Kline['WW']+Kline['WW'],aa['MACD1'],c='b',linewidth=0.5)
        if "DEA" in aa.columns:
            ax1.plot(aa.index*Kline['WW']+Kline['WW'],aa['MACD2'],c='y',linewidth=0.5)

        ax.grid()
        ax.autoscale(tight=False)
        ax.autoscale_view()

        time1=aa.iloc[0]['datetime']
        time2=aa.iloc[-1]['datetime']
        title="%s--%s" %(time1,time2)
        ax.set_title(title, fontsize=20, color='r')
        # fig.savefig("a.jpg")
        plt.show()
        fig.clear()
        plt.close(fig)

print("OK")