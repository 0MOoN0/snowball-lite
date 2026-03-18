class Bucket():

    def __init__(self, index_code, strategy=None):
        self.index_code = index_code
        self.strategy = strategy

    # 获取预期仓位
    def forecast_position(self, date, position):
        return self.strategy.operate(date=date, position=position)
