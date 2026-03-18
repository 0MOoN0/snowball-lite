from xalpha.indicator import indicator


class EvaluateObject(indicator):
    """
    用于传入Evaluate进行比较的类
    """

    def __init__(self, name, code, price):
        """

        :param name:  名称
        :param code:  代码
        :param price:  用于比较的数据，接收一个DataFrame，必须包含[date,netvalue,totvalue]三列
        """
        self.name = name
        self.code = code
        self.price = price
