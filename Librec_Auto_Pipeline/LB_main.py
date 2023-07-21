"""LB_code_experiment!!"""

import pandas as pd
from tqdm import tqdm
import os
from pathlib import Path
import shutil
import random
import subprocess
from itertools import cycle
import numpy as np

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
       return 0
   else:
       return 1

def boot(path,v):
    r_1 = pd.read_csv('train-1.txt', names=['userid', 'itemid', 'score'], sep='\t')
    r_2 = pd.read_csv('test-1.txt', names=['userid', 'itemid', 'score'], sep='\t')
    users = list(set(r_1.userid) & set(r_2.userid))
    items = list(set(r_1.itemid) & set(r_2.itemid))
    dict = {}
    for i in range(len(users)):
        rec_items = random.sample(items, v)
        dict[users[i]] = rec_items
    r = pd.DataFrame.from_dict(dict, orient='index')
    new_df = r.stack().reset_index(level=1, drop=True).to_frame(name='itemid')
    new_df['rating'] = 1
    new_df['userid'] = new_df.index
    first_column = new_df.pop('userid')
    new_df.insert(0, 'userid', first_column)
    Path(path).mkdir(parents=True, exist_ok=True)
    new_df.to_csv(path + 'out-1.txt', header=None, index=None, sep=',', mode='w')

def librec_auto(t,l):
    df = pd.read_csv('scoredDataSets/ML1M/t_' + str(t) + '/out-1.txt', names=['userid', 'itemid', 'rate'], sep=',')
    popularity_data = compute_popularity(df, 'itemid')
    head, mid, tail = get_head_mid_tail(popularity_data, 0.4, 0.8)
    df['label'] = df.apply(lambda row: label_items(row, head), axis=1)
    users = list(df['userid'].sample(n=l).unique())
    for user in tqdm(users):
        user_recs = df[df['userid'] == user]
        seq = cycle([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        user_recs['seq'] = [next(seq) for count in range(user_recs.shape[0])]
        user_recs['expo_score'] = user_recs['seq'].apply(lambda k: expo_score(k))
        user_recs['label'] = user_recs['label'].astype(bool)
        user_recs = user_recs[['userid', 'itemid', 'expo_score', 'label']].reset_index(drop=True)
        user_recs.to_csv('scoredDataSets/ML1M/t_' + str(t) + '/' + 'out-1_rec.txt', header=None, index=False, sep='\t',mode='a')


def user_feedback(t , u):
    train_prev, train_next = 'scoredDataSets/ML1M/t_' + str(t) + '/' + 'train-1.txt', 'scoredDataSets/ML1M/t_' + str(t+1) + '/' + 'train-1.txt'
    shutil.copy(train_prev, train_next)
    Path('scoredDataSets/ML1M/t_' + str(t+1)).mkdir(parents=True, exist_ok=True)
    df = pd.read_csv('scoredDataSets/ML1M/t_' + str(t) + '/' + 'out-1_rec.txt', names=['userid', 'itemid', 'score', 'label'], sep ='\t')
    df = df.iloc[:, 0:2]
    df['rate'] = 1
    for i in df['userid'].unique():
        df_2 = df[df.userid == i].head(u)
        df_2.to_csv('scoredDataSets/ML1M/t_' + str(t+1) + '/train-1.txt', header=None, index=None, sep='\t', mode='a')



def expo_score(k):
    return (11-k)/(10+1)



def first_iter(path, u):
    pd_1 = pd.read_csv(path, names=['userid', 'itemid', 'rate'], sep=',')
    for i in pd_1['userid'].unique():
        pd_2 = pd_1[pd_1.userid == i].head(u)
        pd_2.to_csv('scoredDataSets/ML1M/t_2/train-1.txt', header=None, index=None, sep='\t', mode='a')


#if __name__ == '__main__':
n = 10  #Length of Librec auto produced List
k = 10 #Length of LB produced list (where is it used though)
T = 301 #Number of Pipeline iterations
U = 1 #Number of items clicked per user as feedback and used as input_data()
L = 100 #Number of users picked from out-1.txt file (6040 in total).
V = 10 #Number of items recommended to user @Bootstrap phase.


if os.path.exists('data/train-1.txt'):
    os.remove('data/train-1.txt')
boot('scoredDataSets/ML1M/t_1/', V)

Path('scoredDataSets/ML1M/t_2/').mkdir(parents=True, exist_ok=True)
first_iter('scoredDataSets/ML1M/t_1/out-1.txt', U)


for t in tqdm(range(2, T)):
    train_path, test_path, lb_path = 'scoredDataSets/ML1M/t_' + str(t) + '/train-1.txt', 'data/test-1.txt', 'data/train-1.txt'
    shutil.copy(train_path, lb_path)
    subprocess.run('python3 -m librec_auto run -t demo -nj -nc', shell=True, text=True, input="y")
    Path('scoredDataSets/ML1M/t_' + str(t)).mkdir(parents=True, exist_ok=True)
    Path('scoredDataSets/ML1M/t_' + str(t+1)).mkdir(parents=True, exist_ok=True)
    src,  long_rec = 'demo/exp00000/result/out-1.txt', 'scoredDataSets/ML1M/t_' + str(t) + '/out-1.txt'
    shutil.copy(src, long_rec)
    librec_auto(t, L)
    user_feedback(t, U)
