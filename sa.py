import pymysql
import pandas as pd
import matplotlib.pyplot as plt
import scipy as sp
import numpy as np
import datetime as dt
from matplotlib.lines import TICKLEFT, TICKRIGHT, Line2D
from matplotlib.patches import Rectangle
from corr import Analyse_CORR as sa
import talib as tb

class Analyse_CORR:
    def __init__(self):
        self.Test='Test'
    
    def __init__(self,source,target):
        self.Data=source #数据源
        self.DataT=target
        self.Amount=len(target)  #分析的个数
        self.V1=target['close'].values #分析的数据集
        self.V2=source['close'].values #总数据集
        self.V2_LEN=len(self.V2)
#         self.FIG,self.AX = plt.subplots(figsize=(30,12),dpi=200)
#         self.FIG=plt.figure(figsize=(30,12),dpi=200)
#         self.AX=self.FIG.add_subplot(111)
        
    def corr(self):
        resList=[]
        vv1=self.V1
        vv2=self.V2
        rows=self.V2_LEN
        length=self.Amount
        time1=dt.datetime.now()
        for i in range(0,rows-length):
            vv3=vv2[i:length+i]
            corr=round(np.corrcoef(vv1,vv3)[0][1],3)
            resList.append(corr)
        diff=int(length*0.5)
        res=self.fix_corr(resList,diff)
        time2=dt.datetime.now()
        print("spent time:",time2-time1)
        return res
    
    def fix_corr(self,source,diff=60):
        df_corr=pd.DataFrame(source)
        df_corr.columns=['Corr']
        df_corr.sort_values('Corr',ascending=False,inplace=True)

        newList=[]
        for row in df_corr.iterrows():
            index=row[0]
            insert=True
            for i in newList:
                if i> index-diff and i< index+diff:
                    insert=False
                    break
            if insert:
                newList.append(index)

        df_res=df_corr.loc[newList]
        df_res['datetime']=df_res.apply(lambda x:self.Data.iloc[x.name]['datetime'],axis=1)
        self.DF_CORR=df_res
        return df_res
    
    #draw kline
    def DrawKK(self,aa,add1=0,add2=0,preF='T_',corr=0,isSave=False):
        fig =plt.figure(figsize=(30, 12),facecolor='w')
        ax =fig.add_subplot(111)       
#         ax = AA.Axes(self.FIG, [0, 0, 0.9, 0.9])  #用[left, bottom, weight, height]的方式定义axes，0 <= l,b,w,h <= 1
#         self.FIG.add_axes(ax)
#         ax.clear()
#         ax.clear()
        k_width = 50
        k_diff = 10
        kline = k_width + k_diff
        d=0
        rows=len(aa)
        if add1>0:
            ax.axvline((add1+1)*kline,ymax=1,c='b',ls='dashed')
        if add2>0:
            ax.axvline((add1+self.Amount+1)*kline,ymax=1,c='b',ls='dashed')
        for i in aa.iterrows():
            d=d+1
            x = d * kline
            O = i[1]['open']
            C = i[1]['close']
            L = i[1]['low']
            H = i[1]['high']
            hh = abs(C - O)
            x1 = x + k_width / 2
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
            rec = Rectangle((x, y), k_width, hh, fill=a, color=cc)
            ax.add_patch(rec)
            
        plt.plot(aa.index*kline + k_width / 2,aa['ma60'],c='r')
        plt.plot(aa.index*kline + k_width / 2,aa['ma30'],c='b')
        ax.grid()
        ax.autoscale(tight=False)
        ax.autoscale_view()
        time1=aa.iloc[add1]['datetime']
        if add2==0:
            diff=-1
        else:
            diff=add1+self.Amount          
        if (diff-1)>rows:
            diff=rows-1
               
        time2=aa.iloc[diff]['datetime']
        title="%s--%s,Corr:%.3f" %(time1,time2,corr)
        ax.set_title(title, fontsize=20, color='r')
        if isSave:
            file="res/%s%d_%.7s.jpg"%(preF,self.Amount,time1)
            fig.savefig(file)
            self.FIG=fig
            fig.clear()
            plt.close(fig)
    
    def DrawIndex(self,ind,add1=0,add2=0,isSave=False,preF='T_'):
        if add1>ind:
            add1=ind
        begin=ind-add1
        length=self.Amount
        end=begin+length+add2+add1
        df2=self.Data.iloc[begin:end]
        df2.reset_index(inplace=True)
        self.D2=df2
        v1=self.DF_CORR.loc[ind]['Corr']
        file="res/%s.jpg"%(ind)
        self.DrawKK(df2,add1=add1,add2=add2,corr=v1,isSave=isSave,preF=preF)
        
    def DrawNo(self,no,add1=0,add2=0,isSave=False,preF='T_'):
        index=self.DF_CORR.index[no]
        self.DrawIndex(index,add1,add2,isSave,preF=preF+str(no)+"_")
        
print("OK")
