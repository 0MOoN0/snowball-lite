from pyecharts import options as opts
from pyecharts.charts import Line

from xalpha.cons import line_opts, yesterdayobj
from xalpha.evaluate import evaluate


class ExtEvaluate(evaluate):
    def __init__(self, benchmark=[], contrast=[], start=None):
        self.benchmark = benchmark
        self.contrast = contrast
        self.start = start
        self.fundobjs = benchmark + contrast
        super().__init__(*self.fundobjs, start=start)

    def v_totvalue(self, end=yesterdayobj(), vopts=None, rendered=True, netvalue=False, normalization=False):
        """
        不同数据的可视化比较，如果是基金，则可以选择使用累计净值和归一化处理

        :param end:
        :param vopts:
        :param rendered:
        :param netvalue:
        :param normalization:
        :return:
        """
        indicators = "netvalue" if netvalue else "totvalue"  # 比较指标，使用netvalue还是totvalue
        fundobjs = self.fundobjs
        funds = fundobjs[0].price[["date", indicators]].rename(columns={indicators: fundobjs[0].code})
        for fundobj in fundobjs[1:]:
            funds = funds.merge(
                fundobj.price[["date", indicators]].rename(
                    columns={indicators: fundobj.code}
                ),
                on="date",
            )
        funds = funds.reset_index(drop=True)
        if normalization:
            for col in funds:  # 净值归一化处理
                if col != "date":
                    funds[col] = funds[col] / funds[col].iloc[0]
        partprice = funds[funds["date"] <= end]
        ####################
        line_up = Line()  # contrast图像
        if vopts is None:
            vopts = line_opts
        line_up.add_xaxis([d.date() for d in list(partprice.date)])  # 添加x轴
        line_up.extend_axis(
            yaxis=opts.AxisOpts(min_=partprice.iloc[:, 1:len(self.benchmark) + 1].stack().min(),  # 设置benchmark的y轴
                                max_=partprice.iloc[:, 1:len(self.benchmark) + 1].stack().max()))
        line_up.set_global_opts(
            yaxis_opts=opts.AxisOpts(min_=partprice.iloc[:, 1 + len(self.benchmark):].stack().min(),
                                     max_=partprice.iloc[:, 1 + len(self.benchmark):].stack().max()))
        line_up.set_global_opts(**vopts)
        for fund in fundobjs[len(self.benchmark):]:  # 获取contrast图像
            line_up.add_yaxis(  # 添加y轴
                series_name=fund.name,
                y_axis=list(partprice[fund.code]),
                yaxis_index=0,
                label_opts=opts.LabelOpts(is_show=False)  # 不显示坐标点
            )
        # line_up.add_yaxis(fundobjs[0].name, list(partprice.iloc[:, 1]))
        line_down = Line()  # 底层图像，以传入的第一个对象数据为底层
        line_down.add_xaxis([d.date() for d in list(partprice.date)])
        for fund in fundobjs[:len(self.benchmark)]:  # 设置benchmark的y轴数据
            line_down.add_yaxis(
                series_name=fund.name,
                y_axis=list(partprice[fund.code]),
                yaxis_index=1,
                label_opts=opts.LabelOpts(is_show=False)
            )
        line_up.overlap(line_down)
        if rendered:
            return line_up.render_notebook()
        else:
            return line_up, line_down

    def totvalue_correlation_table(self, end=yesterdayobj(), netvalue=False, normalization=False):
        """
        使用累计净值计算基金的相关系数

        :param end: string or object of date, the end date of the line
        :returns: pandas DataFrame, with correlation coefficient as elements
        """
        indicators = "netvalue" if netvalue else "totvalue"  # 比较指标，使用netvalue还是totvalue
        fundobjs = self.fundobjs
        funds = fundobjs[0].price[["date", indicators]].rename(columns={indicators: fundobjs[0].code})
        for fundobj in fundobjs[1:]:
            funds = funds.merge(
                fundobj.price[["date", indicators]].rename(
                    columns={indicators: fundobj.code}
                ),
                on="date",
            )
        funds = funds.reset_index(drop=True)
        if normalization:
            for col in funds:  # 净值归一化处理
                if col != "date":
                    funds[col] = funds[col] / funds[col].iloc[0]
        partprice = funds[funds["date"] <= end]
        covtable = partprice.iloc[:, 1:].corr()
        return covtable
