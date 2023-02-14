import random
import matplotlib
from datetime import datetime
from scipy import stats
import pandas as pd
import numpy as np
from math import exp, sqrt, log
import matplotlib.pyplot as plt
from pandas_market_calendars import get_calendar


class SnowBall:

    def __init__(self, s0, s_val, rf, bp, vol, 
                start, end, val_date,
                knock_in,
                knock_out, knock_out_step,
                ob: list,
                out, in_range, in_not_out,): #out:敲出  in_range: 未敲入未敲出  in_not_out: 敲入但未敲出
        self.s0 = s0
        self.s_val = s_val
        self.rf = rf
        self.bp = bp
        self.vol = vol
        self.start = start
        self.end = end
        self.val_date = val_date
        self.knock_in = knock_in
        self.knock_out = knock_out
        self.knock_out_step = knock_out_step
        self.ob = ob
        self.out = out
        self.in_range = in_range
        self.in_not_out = in_not_out


    def get_bd(self):

        sse = get_calendar('SSE')
        schedule = sse.schedule(start_date=self.val_date, end_date=self.end)
        bd_list = [str(i) for i in list(schedule.index)]
        bd_lens = len(bd_list)

        return bd_list, bd_lens


    def get_ob_days(self):
        ob_days = [str(datetime.strptime(date, "%Y-%m-%d")) for date in self.ob]
        return ob_days


    def simulation(self, bd_list, bd_lens, ob_days):

        s = np.zeros(bd_lens+1)
        t = [0]
        s[0] = self.s_val

        for i in range(0, bd_lens):
            s[i+1] = s[i]*exp((self.rf - self.bp - 0.5 * self.vol ** 2) * 1/252 + self.vol * sqrt(1/252) * np.random.randn())

        for bd_day in bd_list:
            bd_index = bd_list.index(bd_day)

            flag_in = 0
            flag_out = 0
            price = s[bd_index]
            
            start = datetime.strptime(self.start, "%Y-%m-%d")
            val_date = datetime.strptime(self.val_date, "%Y-%m-%d")

            htm_delta = datetime.strptime(self.end, "%Y-%m-%d") - start
            htm_delta_discount = datetime.strptime(self.end, "%Y-%m-%d") - val_date

            if bd_day in ob_days:
                ob_day_index = ob_days.index(bd_day)  #判断第几个观察日
                knock_out = self.s0 * (self.knock_out + self.knock_out_step * ob_day_index)
                if price > knock_out:
                    delta = datetime.strptime(bd_day, "%Y-%m-%d %H:%M:%S") - start
                    discount = datetime.strptime(bd_day, "%Y-%m-%d %H:%M:%S") - val_date
                    payoff = (1 + self.out * (delta.days + 1) / 365) *  exp(-self.rf * (discount.days + 1)/ 365) #收益率
                    break
            
            elif s[bd_index] < self.knock_in * self.s0:
                payoff = (1 + eval(self.in_not_out)) *  exp(-self.rf * (htm_delta_discount.days + 1)/ 365)
                break

            else:
                payoff = (1 + self.in_range * (htm_delta.days+1) / 365) * exp(-self.rf * (htm_delta_discount.days + 1)/ 365)

        return payoff


test1 = SnowBall(6819.43, 5864.47, 0.0214, 0.048, 0.2074, '2022-2-25', '2024-2-26', '2022-12-31', 0.75, 0.96, -0.005, ['2023-1-30','2023-2-27', '2023-3-27','2023-4-25','2023-5-25','2023-6-26','2023-7-25','2023-8-25','2023-9-25','2023-10-25','2023-11-27','2023-12-25','2024-1-25','2024-2-26',], 0.152, 0.152, 'min(0,s[-1]/self.s0 - 1)')
bd_list = SnowBall.get_bd(test1)[0]
bd_lens = SnowBall.get_bd(test1)[1]   
ob_days = SnowBall.get_ob_days(test1)  
result = []        
for i in range(0,1000):
    result.append(SnowBall.simulation(test1, bd_list, bd_lens, ob_days))
    # print(result)

if __name__ == '__main__':
    print(f'average result: {np.mean(result)}')
    n, bins, patches = plt.hist(pd.DataFrame(result), 50, density=True, alpha=0.75)
    plt.vlines(x = np.mean(result), ymin=0, ymax=max(n), colors='r')
    plt.text(x=np.mean(result), y=max(n), s='{0:.2f}'.format(np.mean(result)))
    plt.show()