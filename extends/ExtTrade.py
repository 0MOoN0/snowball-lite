from xalpha import trade
from xalpha.cons import yesterdayobj
from pyecharts import options as opts
from pyecharts.charts import Line
from extends.ExtEvaluate import ExtEvaluate


def vtradestatus(self, *evaluateobj, cftable, unitcost=False, start=None, end=yesterdayobj(), rendered=True):
    """
    visualization giving the average cost line together with netvalue line as well as buy and sell points

    :returns: pyecharts.line
    """
    funddata = []
    pprice = self.price[self.price["date"] <= end]
    pcftable = cftable
    if start is not None:
        pprice = pprice[pprice["date"] >= start]
        pcftable = pcftable[pcftable["date"] >= start]

    coords = []  # 现金流量表变化时的买入点与卖出点的基金净值，用于计算标记点的大小
    # pcftable = pcftable[abs(pcftable["cash"]) > threhold]
    for i, r in pcftable.iterrows():
        coords.append([r.date, pprice[pprice["date"] <= r.date].iloc[-1]["netvalue"]])

    upper = pcftable.cash.abs().max()
    lower = pcftable.cash.abs().min()
    if upper == lower:
        upper = 2 * lower + 1  # avoid zero in denominator

    def marker_factory(x, y):
        buy = pcftable[pcftable["date"] <= x].iloc[-1]["cash"]
        if buy < 0:
            color = "#ffff00"
        elif buy == 0:
            color = "#ff0000"
        else:
            color = "#3366ff"
        size = (abs(buy) - lower) / (upper - lower) * 5 + 5
        return opts.MarkPointItem(
            coord=[x.date(), y],
            itemstyle_opts=opts.ItemStyleOpts(color=color),
            # this nested itemstyle_opts within MarkPointItem is only supported for pyechart>1.7.1
            symbol="circle",
            symbol_size=size,
        )

    if len(evaluateobj) > 0:
        ext_eva = ExtEvaluate(benchmark=[self.aim], contrast=[*evaluateobj])
        line_up, line_down = ext_eva.v_totvalue(rendered=False, netvalue=True)
        line_down.set_series_opts(markpoint_opts=opts.MarkPointOpts(data=[marker_factory(*c) for c in coords],
                                                               ))
        if rendered:
            return line_up.render_notebook()
        else:
            return line_up

    costdata = []
    for _, row in pprice.iterrows():  # 计算每次现金流量表变化后的成本价
        date = row["date"]
        funddata.append(row["netvalue"])
        if unitcost:
            cost = 0
            if (date - self.cftable.iloc[0].date).days >= 0:
                cost = self.unitcost(date)
            costdata.append(cost)

    line = Line()

    line.add_xaxis([d.date() for d in pprice.date])

    if unitcost:
        line.add_yaxis(
            series_name="持仓成本",
            y_axis=costdata,
            is_symbol_show=False,
        )
    line.add_yaxis(
        series_name="基金净值",
        y_axis=funddata,
        is_symbol_show=False,
        markpoint_opts=opts.MarkPointOpts(
            data=[marker_factory(*c) for c in coords],
        ),
    )
    line.set_global_opts(
        datazoom_opts=[
            opts.DataZoomOpts(
                is_show=True, type_="slider", range_start=50, range_end=100
            ),
            opts.DataZoomOpts(
                is_show=True,
                type_="slider",
                orient="vertical",
                range_start=50,
                range_end=100,
            ),
        ],
        tooltip_opts=opts.TooltipOpts(
            is_show=True,
            trigger="axis",
            trigger_on="mousemove",
            axis_pointer_type="cross",
        ),
    )
    if rendered:
        return line.render_notebook()
    else:
        return line


class ExtTrade(trade):
    """
    trade的拓展类，主要是修改了部分可视化方法
    """

    def __init__(self, infoobj, status, cftable=None, remtable=None):
        super().__init__(infoobj, status, cftable=cftable, remtable=remtable)

    def v_tradestatus(self, *evaluate, start=None, end=yesterdayobj(), rendered=True):
        return vtradestatus(self, *evaluate, cftable=self.cftable, unitcost=True, start=start, end=end,
                            rendered=rendered)
