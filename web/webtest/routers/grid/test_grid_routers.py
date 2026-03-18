
import pytest
from web.models import db
from web.models.grid.Grid import Grid
from web.models.grid.GridType import GridType
from web.webtest.test_base import TestBaseWithRollback

class TestGridRouters(TestBaseWithRollback):
    """
    测试 GridRouters 相关的接口
    """

    def test_get_grid_relation(self, client, rollback_session):
        """
        测试获取网格及其关联的网格类型列表接口
        GET /api/grid/relation
        """
        # 1. 准备测试数据
        # 创建网格1
        grid1 = Grid(
            asset_id=1,
            grid_name="测试网格1",
            grid_status=0
        )
        rollback_session.add(grid1)
        rollback_session.flush()

        # 创建网格2
        grid2 = Grid(
            asset_id=2,
            grid_name="测试网格2",
            grid_status=1
        )
        rollback_session.add(grid2)
        rollback_session.flush()

        # 创建网格类型 (属于网格1)
        grid_type1_1 = GridType(
            grid_id=grid1.id,
            asset_id=1,
            type_name="网格类型1-1",
            grid_type_status=0
        )
        rollback_session.add(grid_type1_1)

        grid_type1_2 = GridType(
            grid_id=grid1.id,
            asset_id=1,
            type_name="网格类型1-2",
            grid_type_status=1
        )
        rollback_session.add(grid_type1_2)

        # 创建网格类型 (属于网格2)
        grid_type2_1 = GridType(
            grid_id=grid2.id,
            asset_id=2,
            type_name="网格类型2-1",
            grid_type_status=0
        )
        rollback_session.add(grid_type2_1)

        rollback_session.commit()

        # 2. 调用接口
        response = client.get('/api/grid/relation')

        # 3. 验证结果
        assert response.status_code == 200
        json_data = response.get_json()
        
        assert json_data['code'] == 20000
        assert json_data['success'] is True
        
        data = json_data['data']
        # 验证返回的数据数量（可能是之前数据库里已有的数据+新加的，至少包含我们加的）
        # 为了准确验证，我们可以在内存中过滤出我们刚创建的ID
        
        target_grid1 = next((item for item in data if item['id'] == grid1.id), None)
        target_grid2 = next((item for item in data if item['id'] == grid2.id), None)
        
        assert target_grid1 is not None
        assert target_grid1['gridName'] == "测试网格1"
        assert len(target_grid1['gridTypes']) == 2
        
        gt1_names = [gt['typeName'] for gt in target_grid1['gridTypes']]
        assert "网格类型1-1" in gt1_names
        assert "网格类型1-2" in gt1_names
        
        assert target_grid2 is not None
        assert target_grid2['gridName'] == "测试网格2"
        assert len(target_grid2['gridTypes']) == 1
        assert target_grid2['gridTypes'][0]['typeName'] == "网格类型2-1"

