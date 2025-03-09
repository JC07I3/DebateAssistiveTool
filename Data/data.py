import pandas as pd

comp_list = ["蘇州盃", "青聲說"] + ['...輸入其他']
tags_list = ["攻防", "第一塊"] 

grid_columns = ["名稱", "簡述", "標籤"]

test_database = pd.DataFrame(
    [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
    columns=grid_columns
)