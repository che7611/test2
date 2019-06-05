import pymongo as pmg
import pandas as pd
import datetime as dt
import pymysql
import matplotlib.pyplot as plt
from matplotlib.lines import TICKLEFT, TICKRIGHT, Line2D
from matplotlib.patches import Rectangle
import matplotlib as mpl
import matplotlib.dates as mdate
from datetime import time
from KRData.HKData import HKFuture
import talib as tb
import configparser
from kline import Kline

class backtesting():
    
#初始化-----------------------------------------------------------------------
    def __init__(self,hf:HKFuture,index='HSI'):
        self.hf=hf
        self._DateList=hf.get_main_contract_trade_dates(index)
        self.trade_para()
        self.Test_Trade=True
        self.cls()
    
#清理-----------------------------------------------------------------------------
    def cls(self):
        self._para={}
        self._res={}
        self._res['macd']=[]
        self._res['ma60']=[]
        self._res['trade']=[]
        
#当前指数全部品种进行测试---------------------------------------------------------------------
    def prod_all(self):
        self.cls()
        for k in self._DateList.keys():
            # print(k)
            self.prod_test(k)
            
#按单月合约进行测试-----------------------------------------------------------------------------
    def prod_test(self,prod):
        self.prod_init(prod)
        self._para['prod']=prod
        dt1=dt.time(9,15)
        dt2=dt.time(16,30)
        date_list=self._DateList[prod]
        self.dl=date_list
        for dd in date_list:
            self._para['date']=dd
            date1=str(dd.date())
            df=self._para['df_prod'][self._para['df_prod']['trade_date']==date1]
            if len(df)<2:
                break
            day_only=df.datetime.apply(lambda x:x.time()>=dt1 and x.time()<=dt2 )
            self._para['df1']=df[day_only]
            if len(df[day_only])<2:
                break
            self.day_loop()
    
#单月品种测试前的初如化---------------------------------------------------------------------------
    def prod_init(self,prod):
        _fields = ['datetime', 'code', 'open', 'high', 'low', 'close', 'vol','trade_date']
        df1=self.hf.get_bars(prod,_fields)
        df1['macd'],df1['diff'],df1['dea']=tb.MACD(df1.close.values,fastperiod=6,slowperiod=12,signalperiod=9)
        df1['ma30']=tb.EMA(df1.close.values,timeperiod=30)
        df1['ma60']=tb.EMA(df1.close.values,timeperiod=60)
        df1['bias']=(df1['close']-df1['ma60'])/df1['ma60']*100
        df1['chg']=df1['close']-df1['open']
        df1['std60']=tb.STDDEV(df1['chg'].values,timeperiod=60)
        df1['std1']=df1['chg']/df1['std60']
        self._para['df_prod']=df1

#交易日循环部分-----------------------------------------------------------------------------------
    def day_loop(self):
        self.day_init()
        df=self._para['df1']
        self._para['day_no']=0
        if self.Test_Trade:
            self.trade_init()
            for i,row in df.iterrows():
                self._para['row']=row
                self.loop_calc()
                self.trade_main()
                self._para['day_no']+=1
            self.trade_end()
        else:
            for i,row in df.iterrows():
                self._para['row']=row
                self.loop_calc()
                self._para['day_no']+=1
        
#交易日开始前准备----------------------------------------------------------------------------------
    def day_init(self):
        row1=self._para['df1'].iloc[0]

        self._para['ma60']={}
        self._para['ma60_no_over']=0
        self._para['ma60_no_under']=0
        self._para['ma60']['no']=0
        self._para['ma60']['cnt']=1
        self._para['ma60']['begin']=row1['close']
        self._para['ma60']['state']='over' if row1['close']>=row1['ma60'] else 'under'
        
        self._para['macd']={}
        self._para['macd']['begin']=row1['close']
        self._para['macd']['state']='red' if row1['macd']>=0 else 'green'
        self._para['macd']['ma60_state']=self._para['ma60']['state']
        self._para['macd']['ma60_no']=0
        self._para['macd']['no']=0
        self._para['macd']['begin_idx']=0
        self._para['macd_no_red']=0
        self._para['macd_no_green']=0
        self._para['macd']['cnt']=1
        self._para['macd']['std_up']=0
        self._para['macd']['std_dn']=0
           
#计算主体部分----------------------------------------------------------------------------------
    def loop_calc(self):
        self.calc_ma60()
        self.calc_macd()
        
#计算MA60------------------------------------------------------------------------------------------
    def calc_ma60(self):
        ma60=self._para['ma60']
        row=self._para['row']
        state=0
        if row['close']>=row['ma60'] and ma60['state'] =='under':
            state=1
            self._para['ma60_no_under']+=1
        elif row['close']<row['ma60'] and ma60['state']=='over':
            self._para['ma60_no_over']+=1
            state=2
        else:
            state=0
            ma60['cnt']+=1
        
        if state>0:
            ma60['prod']=self._para['prod']
            ma60['date']=self._para['date']
            ma60['end']=row['close']
            ma60['diff']=ma60['end']-ma60['begin'] if state==2 else ma60['begin']-ma60['end']
            self._res['ma60'].append(ma60)
#             print(ma60)
            ma60={}
            ma60['no']=self._para['ma60_no_over'] if state==2 else self._para['ma60_no_under']
            ma60['state']='over' if state==1 else 'under'
            ma60['begin']=row['close']
            ma60['cnt']=1
            self._para['macd_no_red']=0
            self._para['macd_no_green']=0
        self._para['ma60']=ma60
        
#计算MACD---------------------------------------------------------------------
    def calc_macd(self):
        macd=self._para['macd']
        row=self._para['row']
        state=0
        if row['macd']>0 and macd['state']=='green':
            state=1
            self._para['macd_no_red']+=1
        elif row['macd']<0 and macd['state']=='red':
            state=2
            self._para['macd_no_green']+=1
        else:
            macd['cnt']+=1
            
        if row['std1']>=1.5:
            macd['std_up']+=1
        elif row['std1']<=-1.5:
            macd['std_dn']+=1
            
        if state>0:
            macd['prod']=self._para['prod']
            macd['date']=self._para['date']
            macd['end']=row['close']
            macd['end_idx']=self._para['day_no']
            macd['diff']=macd['end']-macd['begin'] if state==2 else macd['begin']-macd['end']
            macd['ma60_state_end']=self._para['ma60']['state']
            self._res['macd'].append(macd)
            macd={}
            macd['std_up'],macd['std_dn']=0,0
            macd['ma60_state']=self._para['ma60']['state']
            macd['ma60_no']=self._para['ma60']['no']
            macd['no']=self._para['macd_no_red'] if state==1 else self._para['macd_no_green']
            macd['cnt']=1
            macd['state']='red' if state==1 else 'green'
            macd['begin']=row['close']
            macd['begin_idx']=self._para['day_no']
            
        self._para['macd']=macd
    
#测试参数-----------------------------------------------------------------------
    def trade_para(self):
        self._StopList=['Close','MoveStop','FixStop','MoveStop_HL','FixStop_HL']
        self.StopType=self._StopList[0]
        self.Ma60_Begin=40
        self.StopRatio=0.5
        self.Rec_Begin=7
        self.Rec_Len=60
        self.WinRatio=2
        
#测试交易主体----------------------------------------------------------------
    def trade_main(self):
        if self._para['trade_p']['trade_state']==1:
            self.trade_stop()
        elif self._para['trade_p']['trade_state']==0:
            self.trade_open()
    
#每天交易的初始化-------------------------------------------------------------
    def trade_init(self):
        df1=self._para['df1']
        trade={}
        trade_p={}
        self._para['trade']={}
        self._para['trade_p']={}
        trade_p['rec_begin']=self.Rec_Begin
        trade_p['rec_len']=self.Rec_Len
        trade_p['rec_end']=trade_p['rec_begin']+trade_p['rec_len']-1
        preDF=df1[trade_p['rec_begin']:trade_p['rec_end']]
        IndexList=preDF.index.tolist()
        T_idx=preDF['close'].idxmax()
        B_idx=preDF['close'].idxmin()
        trade['top_idx']=IndexList.index(T_idx)
        trade['bottom_idx']=IndexList.index(B_idx)
        trade['rec_top']=preDF['close'].max()
        trade['rec_bottom']=preDF['close'].min()
        trade['rec_diff']=trade['rec_top']-trade['rec_bottom']
        trade_p['stop_diff']=trade['rec_diff']*self.StopRatio
        trade_p['stop_diff']=40 if trade_p['stop_diff']<40 else trade_p['stop_diff']
        trade_p['stop_diff']=220 if trade_p['stop_diff']>220 else trade_p['stop_diff']
        trade_p['trade_state']=0
        self._para['trade']=trade
        self._para['trade_p']=trade_p
        
#交易开仓条件-------------------------------------------------------------------------------
    def trade_open(self):
        if self._para['day_no']<=self._para['trade_p']['rec_end']:
            return
        
        trade=self._para['trade']
        trade_p=self._para['trade_p']
        row=self._para['row']
        state=0
        if row['close']>trade['rec_top']:
            trade['state']='buy'
            trade['open']=row['close']
            trade['stop_price']=row['open']-trade_p['stop_diff']
            state=1
        elif row['close']<trade['rec_bottom']:
            trade['state']='sell'
            trade['open']=row['close']
            trade['stop_price']=row['open']+trade_p['stop_diff']
            state=2
        
        if state>0:
            trade_p['trade_state']=1
            trade['date']=self._para['date']
            if self._para['ma60']['state']=='over':
                trade['ma60_cnt']=self._para['ma60']['cnt']
            else:
                trade['ma60_cnt']=-self._para['ma60']['cnt']
#             trade['open']=row['close']
            trade['ma60_max']=trade['ma60_cnt']
            trade['bias']=row['bias']
            trade['bias_max']=row['bias']
            trade['open_idx']=self._para['day_no']-trade_p['rec_end']
        
        self._para['trade']=trade
        self._para['trade_p']=trade_p
    
#止损平仓--------------------------------------------------------------------------------------------
    def trade_stop(self):
        trade=self._para['trade']
        trade_p=self._para['trade_p']
        row=self._para['row']
        
        trade['diff']=row['high']-trade['open'] if trade['state']=='buy' \
                                            else trade['open']-row['low']
        if  trade['diff']>=trade_p['stop_diff']*self.WinRatio:
            trade['close']=row['close']
            trade['close_type']='win'
            trade['close_idx']=self._para['day_no']-trade_p['rec_end']
            trade_p['trade_state']=2
            self._para['trade_p']=trade_p
            self._para['trade']=trade
            return
        
        if self.StopType=='MoveStop':
            if (row['close']-trade_p['stop_diff'])>trade['stop_price'] and trade['state']=='buy':
                trade['stop_price']=row['close']-trade_p['stop_diff']
                trade['ma60_max']=self._para['ma60']['cnt']
                trade['bias_max']=row['bias']
            elif (row['close']+trade_p['stop_diff'])<trade['stop_price'] and trade['state']=='sell':
                trade['stop_price']=row['close']+trade_p['stop_diff']
                trade['ma60_max']=-self._para['ma60']['cnt']
                trade['bias_max']=row['bias']
                
        cont1=all([row['close']<trade['stop_price'],trade['state']=='buy'])
        cont2=all([row['close']>trade['stop_price'],trade['state']=='sell'])
        if any([cont1,cont2]):
            trade['close']=row['close']
            trade['close_type']='stop'
            trade['close_idx']=self._para['day_no']-trade_p['rec_end']
            trade_p['trade_state']=2
                
        self._para['trade_p']=trade_p
        self._para['trade']=trade

#ma60平仓-------------------------------------------------------------------------------------------------
    def stop_ma60(self):
        trade=self._para['trade']
        trade_p=self._para['trade_p']
        
        cont3=all([trade['ma60_max']>self.Ma60_Begin,trade['state']=='buy',row['close']<row['ma60']])
        cont4=all([trade['ma60_max']<-self.Ma60_Begin,trade['state']=='sell',row['close']>row['ma60']])
        if cont3 or cont4:
            trade['close']=row['close']
            trade['close_type']='ma60'
            trade['close_idx']=self._para['day_no']-trade_p['rec_end']
            trade_p['trade_state']=2
        self._para['trade_p']=trade_p
        self._para['trade']=trade

        
#每日交易结束----------------------------------------------------------------------------------
    def trade_end(self):
        if self._para['trade_p']['trade_state']==0:
            return
        trade=self._para['trade']
        row=self._para['row']
        if self._para['trade_p']['trade_state']==1:
            trade['close']=row['open']
            trade['close_type']='end'
            trade['close_idx']=self._para['day_no']-self._para['trade_p']['rec_end']-1
            
        trade['diff']=trade['close']-trade['open'] if trade['state']=='buy' \
                                            else trade['open']-trade['close']
        trade['prod']=self._para['prod']
        self._res['trade'].append(trade)
        
print("OK")


