import jqdatasdk as jq
import pandas as pd
from jqdatasdk import finance, query, bond
import xalpha as xa

jq.auth('13118859528', 'Aa1474838768')

# 读取债券基金
bond_fund = pd.read_csv('I:\\DevelopSoftware\\LX\\py\\xalpha_test\\data\\bond_fund.csv', encoding='gbk', index_col=0,
                        header=0)
# 1. 获取基金公司排名信息
cr = pd.read_json('I:\\DevelopSoftware\\LX\\py\\xalpha_test\\data\\company_ranking.json', encoding='utf-8')
cr_top40 = cr[:40]
cr.sort_values('assetScale', ascending=False, inplace=True)
# 设置浮点数显示方式
pd.set_option('display.float_format', lambda x: '%.4f' % x)
# 2. 筛选出特定时间内成立的基金，如果回测从2010年开始，则需要找出2007年的基金，如此类推

# 按成立时间筛选基金
bf_07 = bond_fund[bond_fund['start_date'] <= '2007'].sort_values('end_date')
# 找出纯债基金
pure_bond_f = bf_07[bf_07.loc[:, 'type3'] == '纯债债券型']

# 3. 获取基金的持仓信息，将基金归类为：利率债、信用债、封闭债券
rate_bond_code = pd.read_csv('I:\\DevelopSoftware\\LX\\py\\xalpha_test\\data\\rate_bond_code.csv', encoding='gbk',
                             index_col=0, header=0)
# 对基金的持有债券分析
# 对符合条件的纯债基金进行分类，分为信用债和利率债
for i in pure_bond_f.index:
    # 对基金的持有债券分析
    # 3.1获取某只债券的持仓
    bf_bond_holding = finance.run_query(
        query(finance.FUND_PORTFOLIO_BOND).filter(finance.FUND_PORTFOLIO_BOND.code == i[:6],
                                                  finance.FUND_PORTFOLIO_BOND.period_start >= '2010',
                                                  finance.FUND_PORTFOLIO_BOND.period_end < '2011'))
    symbol_list = bf_bond_holding['symbol']
    bond_detail = []
    for symbol in symbol_list:
        col = []
        col.append(symbol)
        df = bond.run_query(query(bond.BOND_BASIC_INFO).filter(bond.BOND_BASIC_INFO.code == symbol))
        if df['bond_type_id'].values[0] in rate_bond_code.index:
            col.append('利率债')
        else:
            col.append('信用债')
        bond_detail.append(col)
    # 构建DataFrame
    bond_detail = pd.DataFrame(bond_detail, columns=['symbol', 'bond_type'])
    # pd.merge(left=by1, right=by2,how='left',left_on='10年',right_on='10年', sort=True) # 左边全部输出
    bf_bond_holding = pd.merge(left=bf_bond_holding, right=bond_detail, how='left', left_on='symbol', right_on='symbol')
    # 3.2 对债券持仓进行分析，计算利率债占比和信用债占比
    sum = bf_bond_holding.groupby('bond_type')['proportion'].sum()
    pure_bond_f.loc[i, 'type4'] = '信用债' if sum['信用债'] - sum['利率债'] > 0 else '利率债'
    pure_bond_f.loc[i, 'credit_rate_rate'] = sum['信用债'] / sum['利率债']

# 根据信用债。利率债分类的债券基金
for code in pure_bond_f.index:
    df = finance.run_query(query(finance.FUND_FIN_INDICATOR).filter(finance.FUND_FIN_INDICATOR.code == code[:6],
                                                                    finance.FUND_FIN_INDICATOR.period_start > '2007',
                                                                    finance.FUND_FIN_INDICATOR.period_start <= '2010',
                                                                    finance.FUND_FIN_INDICATOR.report_type == '年度'))
# 计算三年收益率，从天天基金获取累计收益信息
fundinfo = xa.fundinfo(code[:6])
# 筛选指定时间段的数据
fundinfo = fundinfo.price[(fundinfo.price['date'] > '2007') & (fundinfo.price['date'] < '2010')]
# 赋值
pure_bond_f.loc[code + '.OF', 'three_year_yield'] = (fundinfo.iloc[-1, -1] - fundinfo.iloc[0, -1]) / \
                                                    fundinfo.iloc[0, -1]

# 1. 去除end_date小于2021的债券基金
bond_fund.drop(bond_fund[bond_fund['end_date'] <= '2021'].index.values, axis=0, inplace=True)
bf_07 = bond_fund[bond_fund['start_date'] <= '2007'].sort_values('end_date')
index = []
for code in bf_07.index:
    index.append(code[:6])
# 2. 去除债券公司排名40以后的公司
# 2.1 查询基金所在公司
funds_main_info = finance.run_query(query(finance.FUND_MAIN_INFO.main_code, finance.FUND_MAIN_INFO.advisor).filter(
    finance.FUND_MAIN_INFO.main_code.in_(index)))
result = pd.merge(left=funds_main_info, right=cr_top40["name"], how='left', left_on='advisor', right_on='name')
result = result[pd.notnull(result["name"])]
# 将索引提取出来
bf_index = bf_07.index
# 将索引转换为数组
bf_index = bf_index.str.replace(".OF", "").values
bf_07.insert(0, 'code', bf_index)
