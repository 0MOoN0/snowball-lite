import logging

from web.services.category.category_service import CategoryService
from web.services.grid.grid_service import GridService

logging.info('------- loading services module -------')
gridService = GridService()
categoryService = CategoryService()
