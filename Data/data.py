import pandas as pd

comp_list = ["蘇州盃", "青聲說"] + ['...輸入其他']
tags_list = ["攻防", "第一塊"] 

grid_columns = ["標題", "持方", "標籤", "簡述"]

test_database = pd.DataFrame(
    [[1, 2, 3, 3], [4, 5, 6, 6], [7, 8, 9, 0], [10, 11, 12, 9]],
    columns=grid_columns,
)