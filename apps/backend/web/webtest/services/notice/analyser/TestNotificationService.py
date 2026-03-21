import pytest

from test_base import TestBase
from web.models.notice.Notification import Notification
from web.services.notice.sender.sender_strategy import TelegramBotSenderStrategy, ServerChenSenderStrategy


@pytest.mark.parametrize('app', ['default'], indirect=True)
class TestNotificationService(TestBase):

    # 测试server酱发送通知
    def test_server_chan_send_strategy(self, mocker):
        # 获取第一条通知
        notification = Notification.query.first()
        strategy = ServerChenSenderStrategy()
        # notice.content = "helloworld"
        msg = strategy.send(notification=notification)
        print()

    # 测试异步方法
    # @pytest.mark.asyncio
    def test_bot_send_strategy(self, mocker):
        # 获取第一条通知
        notification = Notification.query.first()
        strategy = TelegramBotSenderStrategy()
        # notice.content = "helloworld"
        msg = strategy.send(notification=notification)
        print()

    def get_text(self):
        data = [
            ["资产名称", "网格类型", "买入数", "卖出数", "当前变化"],
            ["国泰中证全指证券公司ETF", "小网", 0, 0, "down"],
            ["易方达中概互联50ETF", "小网", 0, 0, "down"],
        ]

        # 计算每列的最大宽度
        # col_widths = [max(len(str(item)) for item in col) for col in zip(*data)]
        col_widths = [max(self.get_display_width(str(item)) for item in col) for col in zip(*data)]
        text = ''
        # # 打印表格
        # for row in data:
        #     print(" | ".join(f"{str(item).ljust(width)}" for item, width in zip(row, col_widths)))
        for row in data:
            text += " | ".join(
                f"{str(item).ljust(width - self.get_display_width(str(item)) + len(str(item)))}" for item, width in
                zip(row, col_widths)) + "\n"
        return text

    def get_display_width(self, text):
        width = 0
        for char in text:
            # 判断字符是否为中文字符
            if '\u4e00' <= char <= '\u9fff':
                width += 3
            else:
                width += 2
        return width
