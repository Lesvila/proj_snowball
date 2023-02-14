import streamlit as st
import pandas as pd
import numpy as np
from main import *
import plotly.express as px
import matplotlib.pyplot as plt


st.set_page_config(
    page_title="Project Snowball",
    page_icon="☃️",
    layout="wide",
    initial_sidebar_state="auto",
)

padding = 1
st.markdown(f""" <style>
    .reportview-container .main .block-container{{
        padding-top: {padding}rem;
        padding-right: {padding}rem;
        padding-left: {padding}rem;
        padding-bottom: {padding}rem;
    }} </style> """, unsafe_allow_html=True)
hide_menu_style = '''
    <style>
    #MainMenu {visibility: hidden; }
    footer {visibility: hidden;}
    </style>
'''
st.markdown(hide_menu_style, unsafe_allow_html=True)

st.title("Project Snowball")
st.sidebar.image('snowball.jpeg', width=300)
st.sidebar.title('上传要素模板')
file = st.sidebar.file_uploader(' ', type='xlsx', key=None)

with st.form(key='parameters input'):
    with st.sidebar:
        rf = st.number_input('无风险利率', step = 0.1, format='%.2f')
        bp = st.number_input('基差', step = 0.1, format='%.2f')
        vol = st.number_input('年化波动率', step = 0.1, format='%.2f')
        trials = st.number_input('模拟次数', step=1000)

        submit_button = st.form_submit_button(label='开始模拟')

st.sidebar.title("About")
st.sidebar.info(
    "Project Snowball is a tool to perform\n"
    "Monte Carlo simulation on snowball like option.\n"

    "\nSend your comments to cloud.lee12@gmail.com"
)


@st.cache_data
def get_data(file):
    if file is None:
        return pd.DataFrame([])
    if file is not None:
        data_main = pd.DataFrame(pd.read_excel(file, parse_dates=None, sheet_name='MAIN', index_col='序列'))
        data_obdays = pd.DataFrame(pd.read_excel(file, parse_dates=None, sheet_name='OBDAYS'))
        return data_main, data_obdays

try:
    data_main = get_data(file)[0]
    data_obdays = get_data(file)[1]

    basic_info, price_info, return_info, obdays_info = st.columns(4)
    with basic_info:
        st.header('基本信息')

        contract = data_main.loc[1]['数值']
        target_security = data_main.loc[2]['数值']
        target_ticker = data_main.loc[3]['数值']
        principal = data_main.loc[4]['数值']
        start_date = str(data_main.loc[5]['数值']).split(' ')[0]
        end_date = str(data_main.loc[6]['数值']).split(' ')[0]
        val_date = str(data_main.loc[7]['数值']).split(' ')[0]

        st.markdown('合同编号: <span style="color:blue;"> {} </span>'.format(contract),unsafe_allow_html=True)
        st.markdown('标的证券: <span style="color:blue;"> {} </span>'.format(target_security),unsafe_allow_html=True)
        st.markdown('标的代码: <span style="color:blue;"> {} </span>'.format(target_ticker),unsafe_allow_html=True)
        st.markdown('名义本金: <span style="color:blue;"> {:,} </span>'.format(principal),unsafe_allow_html=True)
        st.markdown('起始日期: <span style="color:blue;"> {} </span>'.format(start_date),unsafe_allow_html=True)
        st.markdown('到期日期: <span style="color:blue;"> {} </span>'.format(end_date),unsafe_allow_html=True)
        st.markdown('估值日期: <span style="color:blue;"> {} </span>'.format(val_date),unsafe_allow_html=True)

    with price_info:
        st.header('价格参数')
        
        s0 = data_main.loc[8]['数值']
        s_val = data_main.loc[9]['数值']
        knock_in = data_main.loc[10]['数值']
        knock_out = data_main.loc[11]['数值']
        knock_out_step = data_main.loc[12]['数值']

        st.markdown('起始日价格: <span style="color:red;"> {:,} </span>'.format(s0),unsafe_allow_html=True)
        st.markdown('估值日价格: <span style="color:red;"> {:,} </span>'.format(s_val),unsafe_allow_html=True)
        st.markdown('敲入价格%: <span style="color:red;"> {:.2%} </span>'.format(knock_in),unsafe_allow_html=True)
        st.markdown('敲出价格%: <span style="color:red;"> {:.2%} </span>'.format(knock_out),unsafe_allow_html=True)
        st.markdown('敲出价调整: <span style="color:red;"> {:.2%} </span>'.format(knock_out_step),unsafe_allow_html=True)
    
    with return_info:
        st.header('收益参数')

        return_out = data_main.loc[13]['数值']
        return_range = data_main.loc[14]['数值']
        return_innoout = data_main.loc[15]['数值']
        participate = data_main.loc[16]['数值']

        st.markdown('年化敲出收益率: <span style="color:green;"> {:.2%} </span>'.format(return_out),unsafe_allow_html=True)
        st.markdown('到期收益率: <span style="color:green;"> {:.2%} </span>'.format(return_range),unsafe_allow_html=True)
        st.markdown('敲入未敲出收益率: <span style="color:green;"> {} </span>'.format(return_innoout),unsafe_allow_html=True)
        st.markdown('参与率: <span style="color:green;"> {:.2%} </span>'.format(participate),unsafe_allow_html=True)

    with obdays_info:
        st.header('剩余观察日')
        obdays = pd.DataFrame(data_obdays, dtype='str')
        ob_list = [i[0] for i in obdays.values]
        st.table(obdays)
except:
    st.write('要素列表待上传')


if submit_button:

    sample = SnowBall(s0=s0, s_val=s_val, rf = rf/100, bp = bp/100, vol = vol/100, 
    start=start_date, end=end_date, val_date=val_date, 
    knock_in=knock_in,
    knock_out=knock_out, knock_out_step=knock_out_step,
    ob = ob_list,
    out = return_out, in_range = return_range, in_not_out= return_innoout)

    bd_list = SnowBall.get_bd(sample)[0]
    bd_lens = SnowBall.get_bd(sample)[1]   
    print(bd_list)
    ob_days = SnowBall.get_ob_days(sample)

    def generate_result(trials, sample, bd_list, bd_lens, ob_days):    
        result = [] 
        for i in range(0, trials):
            result.append(SnowBall.simulation(sample, bd_list, bd_lens, ob_days))
        return result

    st.session_state.result = generate_result(trials, sample, bd_list, bd_lens, ob_days)


    result_plot, result_stats = st.columns(2)

    with result_plot:

        if 'result' not in st.session_state:
            st.session_state['result'] = []
        print(f'average result: {np.mean(st.session_state.result)}')
        
        n, bins, patches = plt.hist(st.session_state.result, bins=100)

        fig = px.histogram(data_frame = np.array(st.session_state.result), nbins=100, opacity=0.75, 
        title='{} - {} \n 整体估值: {:,}'.format(contract, target_ticker, round( participate * principal * np.mean(st.session_state.result))), labels=None,
        range_y=(0, n))
        mean = np.mean(st.session_state.result)
        median = np.median(st.session_state.result)

        fig.add_annotation(dict(font=dict(color='red',size=14),
                                            x=mean,
                                            y=max(n),
                                            showarrow=False,
                                            text="单位平均数: {:.4f}".format(mean),
                                            textangle=0,
                                            xanchor='right'))
        fig.add_vline(x=np.mean(st.session_state.result))


        st.plotly_chart(fig)
