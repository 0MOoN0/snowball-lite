#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List, Dict

from web.databox.models.dto.convertible_bond_issuance import ConvertibleBondIssuanceData


def make_cb_subscribe_content(items: List[ConvertibleBondIssuanceData], title: str, tag: str) -> Dict:
    """
    将可转债申购 DTO 列表构造成通知内容。

    输出同时包含两套结构以兼容现有模板与测试：
    - items：供 CB_SUBSCRIBE 渲染模板使用（bot/html）
    - grid_info：供历史模板/测试使用（仅含必要标签与资产名）

    Args:
        items (List[ConvertibleBondIssuanceData]): 发行数据DTO列表
        title (str): 通知标题
        tag (str): grid_type_name 标签（如“今日申购”/“明日申购”）

    Returns:
        Dict: 通知内容字典
    """
    items_list = []
    grid_info_list = []

    for dto in items:
        bond_name = dto.bond_name or "未知名称"
        bond_code = dto.bond_code or ""
        subscribe_date = (
            dto.online_subscribe_date.strftime('%Y-%m-%d')
            if getattr(dto, 'online_subscribe_date', None)
            else ''
        )
        apply_code = getattr(dto, 'online_subscribe_code', None) or ''

        items_list.append({
            "bond_name": bond_name,
            "bond_code": bond_code,
            "subscribe_date": subscribe_date,
            "apply_code": apply_code,
            "market": dto.market or ''
        })

        grid_info_list.append({
            "asset_name": f"{bond_name}({bond_code})",
            "grid_type_name": tag,
            # 以下字段为模板兼容的占位/默认值
            "buy_count": 0,
            "sell_count": 0,
            "current_change": []
        })

    return {
        "title": title,
        "items": items_list,
        "grid_info": grid_info_list,
    }