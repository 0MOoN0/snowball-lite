# 近10PE百分位
"""
start = 1
for i in range(2425, len(pe_cv)):
    pe_cv["y10_pe_ew_cvpos"].iloc[i] = (pe_cv["pe_ttm_ew_cv"].iloc[start:i+1].rank(method="max").iloc[-1]-1) * 100.0 / 242500
    start+=1

# PCNT_LIN 指的是当前值在全部数据中的分位数
pe_cv_size = pe_cv["pb_ew_cv"].size-1
pe_cv['PCNT_LIN'] = pe_cv["pb_ew_cv"].rank(method='max').apply(lambda x: 100.0*(x-1)/pe_cv_size)
"""