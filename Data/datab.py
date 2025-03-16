import pandas as pd
from .contest_manage import get_contests 

comp_list = get_contests() + ['...輸入其他']
tags_list = ["攻防", "第一塊"] 

grid_columns = ["title", "持方", "標籤"]

'''
test_database = pd.DataFrame(
    [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]] * 4,
    columns=grid_columns,
)
'''