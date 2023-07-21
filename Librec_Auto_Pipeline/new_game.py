import pandas as pd
from itertools import cycle
import numpy as np
import matplotlib.pyplot as plt

def compute_popularity(df, col):
    pop = df.groupby([col]).size().reset_index(name='popularity')
    pop['popularity'] = pop['popularity'] / len(df)
    return pop.sort_values('popularity', ascending=False)


def get_head_mid_tail(popularity, head_threshold, mid_threshold):
    p, i = 0, 0
    head_index, mid_index = 0, 0
    head_found, mid_found = False, False
    for index,row in popularity.iterrows():
        p += float(row['popularity'])
        if p > head_threshold and not head_found:
            head_index = i + 1
            head_found = True
        elif p > mid_threshold and not mid_found:
            mid_index = i + 1
            mid_found = True
        i += 1
    return list(popularity[:head_index]['itemid']), list(popularity[head_index:mid_index]['itemid']), list(popularity[mid_index:]['itemid'])


def label_items(row, head):
   if row['itemid'] in head:
       return 'False'
   else:
       return 'True'


def expo_score(k):
    return (11-k)/(10+1)

# """Compute_Score_Labels_for_bootstrap"""
#
#
df = pd.read_csv('T_3/t_1/out-1.txt', names=['userid', 'itemid', 'rating'], sep=',')
#
# seq = cycle([1, 2, 3,4,5,6,7,8,9,10])
# df['seq'] = [next(seq) for count in range(df.shape[0])]
# df['expo_score'] = df['seq'].apply(lambda k: expo_score(k))
# #df = df.drop('seq')
# popular_data = compute_popularity(df, 'itemid')
# head, mid, tail = get_head_mid_tail(popular_data, 0.4, 0.8)
# df['label'] = df.apply(lambda row: label_items(row, head), axis=1)
# #df['count'] = df['itemid'].map(df['itemid'].value_counts())
# print(df)
#
# df.to_csv('T_3/t_1/out-1-new.txt', header=None, index=None, sep=',', mode='w')
#
# """"Count_itemids_test"""
# #
# df_1 = pd.read_csv('T_3/t_1/out-1-new.txt', names=['userid', 'movieid', 'rating', 'seq', 'score', 'label'], sep = ',')
# df_1['count'] = df_1['movieid'].map(df_1['movieid'].value_counts())
# print(df_1)
# df_1.to_csv('T_3/t_1/out-1-new.txt', header=None, index=None, sep=',', mode='w')
# """End"""

# df_4 = pd.read_csv('T_2/t_2/FOEIR-DIC_rec.txt', names=['userid', 'movieid', 'score', 'label'], sep=',')
# df_4= df_4.drop(columns=['userid', 'label'])
# #df_4['count'] = df_4.groupby(['movieid']).size().reset_index(name='count')
# #df_4['count'] = df_4['movieid'].map(df_4['movieid'].value_counts())
# df_4 = df_4.groupby('movieid').sum()
# #df = df.groupby('id').sum()
# #sort_values(by=['score'], ascending=F)
#items_ranked = list(pd_2['itemid'].unique())alse).reset_index(drop=True)
# print(df_4)

"""""Add_Count_to_DIC-rec"""
#
# for t in range(2 ,100):
#     df_1 = pd.read_csv('T_3/t_' + str(t) + '/FOEIR-DIC_rec.txt', names=['userid', 'movieid', 'score', 'label'], sep=',')
#     df_1['count'] = df_1['movieid'].map(df_1['movieid'].value_counts())
#     df_1.to_csv('T_3/t_' + str(t) + '/FOEIR-DIC_rec.txt', header=None, index=False, sep=',', mode='w')



""""Bootstrap_Cumulative_Score(Three of the least recommended items are again, in the total least recommended_items, aswell...But 1 is actually 8th most recommended!"""

fd = pd.read_csv('T_3/t_1/out-1-new.txt', names=['userid', 'movieid','rating', 'seq', 'score', 'label', 'count'], sep=',')

fd = fd.drop(columns=['count','userid','rating', 'seq', 'label'])
#fd['count'] = fd['movieid'].map(fd['movieid'].value_counts())
#print(fd)
fd_1 = fd.groupby('movieid').score.agg(['sum']).reset_index()
#fd_1 = fd_1.groupby('movieid').count.agg(['sum_2']).reset_index()
fd_2 = fd_1.sort_values(by=['sum'], ascending=False).reset_index(drop=True)
print(fd_2)