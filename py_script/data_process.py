import pandas as pd
import json
import requests

"""
数据处理的相关脚本

fetch_data: 从网络（理杏仁）获取指定(metrics_list)数据， 并以JSON格式返回

format_data_to_list：对fetch_data返回的数据进行处理，将每一条数据按日期格式化为行

get_data_columns_name：对fetch_data返回的数据进行处理，获取数据列名，如cp等

read_json：调用前三个方法，调用fetch_data从远程获取数据，并保存在本地， 调用format_data_to_list将JSON数据内容转为行，调用get_data_columns_name
           获取数据列名，最终转换为DataFrame数据，并以CSV格式保存在磁盘
"""


# 从网络获取数据
def fetch_data(token=None, stock_code=None):
    token = token
    stock_codes = [*stock_code]
    metrics_list = [
        "cp",
        "mc",
        "cmc",
        "fb",
        "sb",
        "ha_shm",
        "pe_ttm.fs.mcw",
        "pe_ttm.fs.ew",
        "pe_ttm.fs.ewpvo",
        "pe_ttm.fs.avg",
        "pe_ttm.fs.median",
        "pb.fs.mcw",
        "pb.fs.ew",
        "pb.fs.ewpvo",
        "pb.fs.avg",
        "pb.fs.median",
        "ps_ttm.fs.mcw",
        "ps_ttm.fs.ew",
        "ps_ttm.fs.ewpvo",
        "ps_ttm.fs.avg",
        "ps_ttm.fs.median",
        "dyr.mcw",
        "dyr.ew",
        "dyr.ewpvo",
        "dyr.avg",
        "dyr.median"
    ]
    url = "https://open.lixinger.com/api/a/index/fundamental"
    data = json.dumps(
        {"token": token, "startDate": "1980-01-01", "stockCodes": stock_codes, "metricsList": metrics_list})
    headers = {'content-type': 'application/json'}
    response = requests.post(url=url, data=data, headers=headers)
    return response.json()  # 响应结果"


def read_json(*stock_code):
    stock_code = stock_code
    token = "a35b4973-631c-4334-8068-bb129fc755a7"
    for index in stock_code:
        print("正在下载%s指数数据" % index)
        index_data = fetch_data(token=token, stock_code=[index])
        index_data = index_data["data"]
        print("正在将JSON数据写出到磁盘")
        # 将数据写出到磁盘
        with open("I:\\DevelopSoftware\\LX\\py\\xalpha_test\\data\\index_" + index + "_data.json",
                  "w") as dumpfile:
            json.dump(index_data, dumpfile)
        print("正在解析并格式化%sJSON数据" % index)
        table_list = []
        for row in index_data:
            row_dict = {}
            row_to_dict(row, row_dict, "")  # 将每一行的数据转换为层级为1的字典
            table_list.append(row_dict)  # 将每一个字典添加到数组
        df_data = pd.DataFrame(data=table_list)  # 使用字典数组创建DataFrame，效率比一条条数据append高非常多
        df_data["date"] = pd.to_datetime(df_data["date"]).dt.date
        print("正在将格式化数据写出到磁盘")
        df_data.to_csv("I:\\DevelopSoftware\\LX\\py\\xalpha_test\\data\\index_" + index + "_data.csv")
        print("完成操作\n")


def format_data_to_list(data_pieces, row_list):
    for key in data_pieces:
        if type(data_pieces[key]) == dict:
            format_data_to_list(data_pieces[key], row_list)
            continue
        row_list.append(data_pieces[key])


def get_data_columns_name(data_pieces, prefix, columns_name):
    for key in data_pieces:
        if type(data_pieces[key]) == dict:
            get_data_columns_name(data_pieces[key], prefix + key + "_", columns_name)
            continue
        columns_name.append(prefix + key)


def row_to_dict(data_pieces, row_dict, prefix):
    for key in data_pieces:
        if type(data_pieces[key]) == dict:
            row_to_dict(data_pieces[key], row_dict, prefix + key + "_")
            continue
        row_dict[prefix + key] = data_pieces[key]


# 获取十年期分位点
def get_tenyears_quantile(df, columnname="pb_fs_ew_cv"):
    new_columnname = "y10_" + columnname+"pos"
    df[new_columnname] = df[columnname+"pos"]
    start = 1
    for i in range(2425, len(df)):
        df[new_columnname].iloc[i] = (df[columnname].iloc[start:i + 1].rank(method="max").iloc[
                                          -1] - 1) * 100.0 / 242500
        start += 1


# 获取MACD线
def get_indicator_macd(rule='W-FRI', index_data=None):
    index_data = index_data[["date", "cp"]]
    index_data["date"] = pd.to_datetime(index_data["date"])
    index_data.set_index(keys=["date"], inplace=True)
    index_data["cp"] = index_data["cp"].resample(rule).last()
    index_data.dropna(inplace=True)
    index_data.reset_index(inplace=True)
    fast_window, slow_window, signal_window = 12, 26, 9
    EMAfast = pd.Series(index_data["cp"].ewm(span=fast_window).mean())
    EMAslow = pd.Series(index_data["cp"].ewm(span=slow_window).mean())
    MACDDiff = pd.Series(EMAfast - EMAslow)
    MACDDem = pd.Series(MACDDiff.ewm(span=signal_window).mean())
    MACDOsc = pd.Series(MACDDiff - MACDDem)
    # DIFF 离差值
    index_data["MACD_DIFF_" + str(fast_window) + "_" + str(slow_window)] = MACDDiff
    # MACD值
    index_data["MACD_DEM_" + str(fast_window) + "_" + str(slow_window)] = MACDDem
    # 柱状图
    index_data["MACD_OSC_" + str(fast_window) + "_" + str(slow_window)] = MACDOsc
    return index_data


# read_json("000016", "000010", "000300", "000905", "399006", "000922", "399324", "000991", "000978", "399989",
#           "000932", "000990", "399396", "399812", "000993", "399971", "000827", "399975", "000992", "399986")
# read_json("1000004")  # 上证指数
