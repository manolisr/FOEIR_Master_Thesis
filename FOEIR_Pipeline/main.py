
import pandas as pd
from foeir_ranker import scoreBasedEval
from tqdm import tqdm
import os
from pathlib import Path
import shutil
import random
import subprocess


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



def user_feedback(fair_algo, t, u):

    train_prev, train_next = 'scoredDataSets/ML1M/t_' + str(t) + '/' + 'train-1.txt', 'scoredDataSets/ML1M/t_' + str(t+1) + '/' + 'train-1.txt'
    shutil.copy(train_prev, train_next)
    Path('scoredDataSets/ML1M/t_' + str(t+1)).mkdir(parents=True, exist_ok=True)
    #for fair_algo in algo_name:
    df = pd.read_csv('rankings/' + fair_algo + '/ML1Mranking.csv', names=['userid', 'itemid', 'score', 'label'], sep =',')
    df = df.iloc[:, 0:2]
    df['rate'] = 1
    foeir_ranking, fair_ranking = 'rankings/FOEIR-DIC/ML1Mranking.csv' , 'scoredDataSets/ML1M/t_' + str(t) + '/FOEIR-DIC_rec.txt'
    shutil.copy(foeir_ranking, fair_ranking)
    foeir_ranking_1, fair_ranking_1 = 'rankings/FOEIR-DPC/ML1Mranking.csv', 'scoredDataSets/ML1M/t_' + str(t) + '/FOEIR-DPC_rec.txt'
    shutil.copy(foeir_ranking_1, fair_ranking_1)
    foeir_ranking_2, fair_ranking_2 = 'rankings/FOEIR-DTC/ML1Mranking.csv', 'scoredDataSets/ML1M/t_' + str(t) + '/FOEIR-DTC_rec.txt'
    shutil.copy(foeir_ranking_2, fair_ranking_2)
    for i in df['userid'].unique():
        df_2 = df[df.userid == i].head(u)
        df_2.to_csv('scoredDataSets/ML1M/t_' + str(t+1) + '/train-1.txt', header=None, index=None, sep='\t', mode='a')



def foeir(train_path,test_path, long_rec,t,n,l,k):

    """Remove FOEIR results for previous t"""
    counter = 0
    if os.path.exists('rankings/FOEIR-DIC/ML1Mranking.csv'): os.remove('rankings/FOEIR-DIC/ML1Mranking.csv')
    if os.path.exists('rankings/FOEIR-DPC/ML1Mranking.csv'): os.remove('rankings/FOEIR-DPC/ML1Mranking.csv')
    if os.path.exists('rankings/FOEIR-DTC/ML1Mranking.csv'): os.remove('rankings/FOEIR-DTC/ML1Mranking.csv')

    train_data = pd.read_csv(train_path, names=['userid', 'itemid', 'rate'], sep='\t')
    long_rec_data = pd.read_csv(long_rec, names=['userid', 'itemid', 'score'], sep=',')
    test_data = pd.read_csv(test_path, names=['userid', 'itemid', 'rate'], sep='\t')
    popularity_data = compute_popularity(long_rec_data, 'itemid')
    head, mid, tail = get_head_mid_tail(popularity_data, 0.4, 0.8)#0.4,0.8

    print(len(head))
    if len(head) == 0:
        counter += 1
        long_rec_data['label'] = 1
        update_1 = long_rec_data['label'].sample(frac=0.8).index
        long_rec_data.loc[update_1, 'label'] = 0
        popularity_data['label'] = 1
        update_2 = popularity_data['label'].sample(frac=0.8).index
        popularity_data.loc[update_2, 'label'] = 0
    else:
        long_rec_data['label'] = long_rec_data.apply(lambda row: label_items(row, head), axis=1)
        popularity_data['label'] = popularity_data.apply(lambda row: label_items(row, head), axis=1)
    popularity_data.to_csv("scoredDataSets/ML1M/t_" + str(t) + '/pop_plot.txt', header=None, index=None, sep=',', mode='w')
    a = long_rec_data.query('label == 0').label.count()
    print(f'Number of Popular items  is ... {a}', counter)
    users = list(long_rec_data['userid'].sample(n=l).unique())

    for user in tqdm(users):
        user_recs = long_rec_data[long_rec_data['userid'] == user]
        scoreBasedEval(user_recs, 'ML1M', "scoredDataSets/ML1M/t_" + str(t), n, k)


def first_iter(path, u):
    pd_1 = pd.read_csv(path, names=['userid', 'itemid', 'rate'], sep=',')
    for i in pd_1['userid'].unique():
        pd_2 = pd_1[pd_1.userid == i].head(u)
        pd_2.to_csv('scoredDataSets/ML1M/t_2/train-1.txt', header=None, index=None, sep='\t', mode='a')


#if __name__ == '__main__':
n = 40  #Length of Librec auto produced List
k = 10 #Length of FOEIR produced list (where is it used though)
T = 301 #Number of Pipeline iterations
U = 1 #Number of items clicked per user as feedback and used as input_data()
L = 100 #Number of users running FOEIR code for (6040 in total).
V = 10 #Number of items recommended to user @Bootstrap phase.


if os.path.exists('data/train-1.txt'):
    os.remove('data/train-1.txt')
boot('scoredDataSets/ML1M/t_1/', V) # completing the pipeline for t=1. The pipeline does not need running FOEIR and librec-auto.

''' Collect the User-Feedback 1-5 ranked items for each user and append them to a new train-1.txt file and paste it also in librec-auto folder '''


Path('scoredDataSets/ML1M/t_2/').mkdir(parents=True, exist_ok=True)
first_iter('scoredDataSets/ML1M/t_1/out-1.txt', U)


for t in tqdm(range(2, T)):
    train_path, test_path, lb_path = 'scoredDataSets/ML1M/t_' + str(t) + '/train-1.txt', 'data/test-1.txt', 'data/train-1.txt'
    shutil.copy(train_path, lb_path)
    #os.system("python3 -m librec_auto run -t demo -nj -nc")
    subprocess.run('python3 -m librec_auto run -t demo -nj -nc', shell=True, text=True, input="y")
    #result
    Path('scoredDataSets/ML1M/t_' + str(t)).mkdir(parents=True, exist_ok=True)
    Path('scoredDataSets/ML1M/t_' + str(t+1)).mkdir(parents=True, exist_ok=True)
    src,  long_rec = 'demo/exp00000/result/out-1.txt', 'scoredDataSets/ML1M/t_' + str(t) + '/out-1.txt'
    shutil.copy(src, long_rec)
    foeir(train_path, test_path, long_rec, t, n, L, k)
    user_feedback('FOEIR-DIC', t, U)

