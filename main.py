import random
import matplotlib
from datetime import datetime
from scipy import stats
import pandas as pd
import numpy as np
from math import exp, sqrt, log
import matplotlib.pyplot as plt
from pandas_market_calendars import get_calendar
from collections import Counter


class SnowBall:

    def __init__(self, s0, s_val, rf, bp, vol, discount_rate, 
                start, end, val_date,
                knock_in,
                knock_out, knock_out_step,
                ob: list,
                out, in_range, in_not_out,
                deposit, knocked_in,
                trigger): #out:敲出  in_range: 未敲入未敲出  in_not_out: 敲入但未敲出
        self.s0 = s0
        self.s_val = s_val
        self.rf = rf
        self.bp = bp
        self.vol = vol
        self.discount_rate = discount_rate
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
        self.deposit = deposit
        self.knocked_in = knocked_in
        self.trigger = trigger


    def get_bd(self):

        sse = get_calendar('SSE')
        schedule = sse.schedule(start_date=self.val_date, end_date=self.end)
        bd_list = [str(i) for i in list(schedule.index)]
        bd_lens = len(bd_list)

        return bd_list, bd_lens


    def get_ob_days(self):
        ob_days = [str(datetime.strptime(date, "%Y-%m-%d")) for date in self.ob]
        return ob_days
    
    def get_flags(flag_result : list):
        if flag_result == [0, 1]:
            result = 1 #not in but out
        elif flag_result == [1, 1]:
            result = 2 # in and out
        elif flag_result == [1, 0]:
            result = 3 # in not out
        else:
            result = 4 # not in not out
        
        return result


    def simulation(self, bd_list, bd_lens, ob_days):

        s = np.zeros(bd_lens+1)
        t = [0]
        s[0] = self.s_val
        start = datetime.strptime(self.start, "%Y-%m-%d")
        val_date = datetime.strptime(self.val_date, "%Y-%m-%d")
        htm_delta = datetime.strptime(self.end, "%Y-%m-%d") - start
        htm_delta_discount = datetime.strptime(self.end, "%Y-%m-%d") - val_date
        flag_in = self.knocked_in
        flag_out = 0

        for i in range(0, bd_lens):
            s[i+1] = s[i]*exp((self.rf - self.bp - 0.5 * self.vol ** 2) * 1/252 + self.vol * sqrt(1/252) * np.random.randn())

        for bd_day in bd_list[1:]:
            price = s[bd_list.index(bd_day)]
            if bd_day in ob_days:
                ob_day_index = ob_days.index(bd_day)  #判断第几个观察日
                knock_out = self.s0 * (self.knock_out - self.knock_out_step * ob_day_index)
                if price > knock_out:
                    delta = datetime.strptime(bd_day, "%Y-%m-%d %H:%M:%S") - start
                    discount = datetime.strptime(bd_day, "%Y-%m-%d %H:%M:%S") - val_date
                    flag_out = 1
                    flag_in = 1 if ((np.min(s[1:bd_list.index(bd_day)]) < self.knock_in * self.s0) + self.knocked_in) > 0 else 0
                    if self.trigger:
                        payoff = 1 + (self.out[ob_day_index] * (delta.days + 1) / 365) *  exp(-self.discount_rate * (discount.days + 1)/ 365) #收益率
                    else:
                        payoff = 1 + self.deposit * (exp(-self.discount_rate * (discount.days + 1)/ 365) - 1) + self.out[ob_day_index] * (delta.days + 1) / 365 *  exp(-self.discount_rate * (discount.days + 1)/ 365) #收益率
                break

            if flag_out == 0:
                if np.min(s[1:]) < self.knock_in * self.s0 or flag_in == 1:
                    flag_in = 1
                    if self.trigger:
                        payoff = 1 + (eval(self.in_not_out)) *  exp(-self.discount_rate * (htm_delta_discount.days + 1)/ 365)
                    else:
                        payoff = 1 + self.deposit * (exp(-self.discount_rate * (htm_delta_discount.days + 1)/ 365) - 1) + eval(self.in_not_out) *  exp(-self.discount_rate * (htm_delta_discount.days + 1)/ 365)
                    break

                else:
                    flag_in == 0
                    if self.trigger:
                        payoff = 1+ (self.in_range * (htm_delta.days+1) / 365) * exp(-self.discount_rate * (htm_delta_discount.days + 1)/ 365)
                    else:
                        payoff = 1 + self.deposit * (exp(-self.discount_rate * (htm_delta_discount.days + 1)/ 365) -1 ) + self.in_range * (htm_delta.days+1) / 365 * exp(-self.discount_rate * (htm_delta_discount.days + 1)/ 365)

        return payoff, [flag_in, flag_out]
