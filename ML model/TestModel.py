import pandas as pd
import numpy as np
import json

from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
#from werkzeug import secure_filename
from werkzeug.utils import secure_filename

import pickle

app = Flask(__name__)
CORS(app)

file = open('MitreData.json')

obj_list = []
dict = {}

for line in file:
    # line=line + '\n'
    obj_list.append(eval(line))

new_list = []
for item in obj_list:
    
    dict = item
    new_list.append(dict)

df = pd.DataFrame(new_list)
#df.head()


fileD=open('DataSources.json')
objD_list = []
for line in fileD:
    objD_list.append(eval(line))
    
df_DS = pd.DataFrame(objD_list)
df_DS.head()


tramp_small=pd.read_json('TrampData.json')

tramp=pd.read_json('TrampDataSmall.json')

df_tramp=tramp['sentences']
df_tramp_small=tramp_small['sentences']

df_tramp.append(df_tramp_small,ignore_index=True)




dict_tr={'id':[],'text':[]}
index=0
for i in df_tramp:
    
    if not i['mappings']:
        continue
    idv=i['mappings'][0]['attack_id']
    
    dict_tr['id'].append(idv)
    dict_tr['text'].append(i['text'])
    
df_tr=pd.DataFrame(dict_tr)

df_comb=df.join(df_tr.set_index('id'),on='id')



df_comb.drop(['subtechniqueof'],axis=1)
df_comb.drop(['subtechniques'],axis=1)

for x in df_comb:
    
    df_comb[x]=df_comb[x].fillna(method='bfill',axis=0)
    df_comb[x]=df_comb[x].fillna(method='ffill',axis=0)
    df_comb[x]=df_comb[x].interpolate(method='linear',limit_direction='forward',axis=0)

# df_comb.isnull().sum()


df_comb['id'].value_counts()
tids = df_comb['id'].unique()

dict_target = {}
dict_tactic= {}
i = 0
for x in tids:
     dict_target[x] = i
     dict_tactic[x]=df_comb.loc[df_comb['id']==x,'tactics'].apply(lambda x: ",".join(x.astype(str)), axis=1)
    #  dict_tactic[x]=df_comb.loc[df_comb['id']==x,'tactics'].append(df_comb.loc[df_comb['id']==x,'techniquename'])
     i = i + 1
#print(dict_target)

df_comb['num_target']=df_comb['id'].map(dict_target)


print("************Data collected***********")

def predict_id(num):
    #print(dict_target)
    for key, value in dict_target.items():
        if num == value:
            return key


with open('model_pickle', 'rb') as f:
    clf = pickle.load(f)

print("************Pickle loaded***********")

from sklearn.metrics import accuracy_score
from sklearn.metrics import balanced_accuracy_score,precision_score,recall_score,f1_score
import matplotlib.pyplot as plt

def predict_values(test_df):
    print("************Predict Values start***********")

    test = test_df

    return_list = []
    dict_scores={'precision':'','recall':'','accuracy':'','f1_score':''}
    y_actual=[]
    result=[]

    for index,row in test.iterrows():
        if row['data input'] :
            dict_result={}
            pred=clf.predict([row['data input']])
            y_actual.append(row['actual id'])
            result.append(predict_id(pred))

            dict_result['sentence']=row['data input']
            dict_result['actual_id']=row['actual id']
            dict_result['predict_id']=predict_id(pred)

            return_list.append(dict_result)

    y_actual=np.array(y_actual)
    result=np.array(result)
    dict_scores['precision']=precision_score(y_actual,result,average='macro',zero_division=1)
    dict_scores['recall']=recall_score(y_actual,result,average='macro',zero_division=1)
    dict_scores['f1_score']=f1_score(y_actual, result, average='macro',zero_division=1)
    dict_scores['accuracy']=balanced_accuracy_score(y_actual,result)

    print("************Predict Values end***********")
    return return_list, dict_scores
    



#filer,scores=predict_values()

# print(scores)
# print(filer)
# fp=open('dictdata1.json','w+')
# fp.write(json.dumps(filer))


@app.route('/', methods = ['GET'])
def default():
    return "hi"

@app.route('/upload', methods = ['POST'])
def upload_file():
    file = request.files['file']
    print(file)
    print(type(file))
    print(file.filename)
    fname = file.filename
    file.save(secure_filename(file.filename))
    test=pd.read_csv(fname)
    lst, scores=predict_values(test)
    #print(scores)
    return jsonify(lst), scores

@app.route('/accuracy', methods = ['POST'])
def get_accuracy():
    file = request.files['file']
    print(file)
    print(type(file))
    print(file.filename)
    fname = file.filename
    file.save(secure_filename(file.filename))
    test=pd.read_csv(fname)
    lst, scores=predict_values(test)
    print(scores)
    return scores


if __name__ == '__main__':
    #app.run(host="0.0.0.0", port=8089)
    app.run(debug = True)