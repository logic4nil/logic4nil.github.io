## DGA域名识别

### 实现

#### 实现思路
   
1. word2vec，生成a-z,-,0-9的词向量
2. 采用LSTM模型，sigmoid激活
3. Lost crossentropy
4. 结果  
   训练结果准确率95%左右
5. 部署之后，识别出的异常域名请求[微步](https://x.threatbook.cn/)验证是否为DGA域名。否，则构建白名单，用作下一步的模型增强训练。

#### 实施
1. Load data
``` python
import pandas as pd
import numpy as np

def load_data():
    datas = []
    i = 0
    with open("./train.txt") as fd:
        for line in fd.readlines():
            arr = line.strip().lower().split(" ")
            domain_name = arr[0].strip(".").split(".")[0]
            if len(arr) != 2:
                domain_label = "1"
            else:
                domain_label = arr[1]
            datas.append([domain_name, domain_label])
    return datas

datas = load_data()
pdatas = pd.DataFrame(datas, columns=["domain", "label"])
```
2. word2vec建立字符词向量
``` python
from gensim.models import Word2Vec

def cal_word2vec(domains):
    w2v_list = []
    for domain in domains:
        w2v_list.append(list(domain))
    model = Word2Vec(w2v_list, size=50,min_count=1)
    return model

w2vmodel = cal_word2vec(pdatas["domain"])

```
3. 数据转换
```python
# 获取domain的vect
def get_domain_vect(domain, word2vec_model=None):
    tmp = []
    for k, v in enumerate(domain):
        if k >= 15:
            break
        if v not in word2vec_model:
            tmp.append([0]*50)
        else:
            tmp.append(word2vec_model[v])

    for k in range(len(tmp), 15, 1):
        tmp.append([0]*50)
    return tmp

# 所有域名转换为词向量
def vect_all_datas(domains, word2vec_model):
    result = []
    for domain in domains:
        r = get_domain_vect(domain, word2vec_model)
        result.append(r)
    return np.array(result)

vect_datas = vect_all_datas(pdatas["domain"], w2vmodel)
vect_label = pdatas["label"].astype("float32")
```
4. LSTM模型训练
``` python
from keras.models import Sequential
from keras.layers import Dense,Embedding
from keras.layers import LSTM

size = 15000
x_train = vect_datas[0:size]
y_train = vect_label[0:size]
x_test = vect_datas[size:]
y_test = vect_label[size:]


model = Sequential()
model.add(LSTM(128,dropout = 0.2,recurrent_dropout = 0.2))
model.add(Dense(1,activation='sigmoid'))
model.compile(loss = 'binary_crossentropy',optimizer = 'adam',metrics = ['accuracy'])

history = model.fit(x_train,y_train,epochs = 5,batch_size = 100,validation_data=(x_test, y_test))

```
5. 模型保存
``` python
import os
import tensorflow.io.gfile as gfile

save_dir = "./result"
# 保存模型参数
if gfile.exists(save_dir):
    gfile.rmtree(save_dir)
gfile.mkdir(save_dir)
model_name = 'dga.h5'
model_path = os.path.join(save_dir, model_name)
model.save(model_path)

# 保存word2vec
from gensim.models import Word2Vec

w2vmodel.save("./result/word2vec.model")
```
#### 模型上线
- 模型Load
``` python
# Load LSTM model
from keras.models import load_model
l_model = load_model(model_path)

# Load word2vec
from gensim.models import Word2Vec
w2vmodel = Word2Vec.load("./result/word2vec.model")
```

#### 实施中的问题以及更改点

1. 因语料中，词总共才37个，没必要使用100维度表示，将为20
2. 数据问题
   
    参考代码中的数据比较老，异常数据使用[domain_generation_algorithms](https://github.com/baderj/domain_generation_algorithms)的数据，随机选取1w条。正常域名选用alexa Top 1W+。

    训练之后的结果在实际使用中的误差较高，很多中文拼音的域名都识别为DGA域名， 例如 **bilibi.com**等。解决方案：加入中文拼音样本

    中文首字母类的域名，算作异常样本。
    


### 新思路

    字符标注本没必要用word2vec，word2vec主要的作用是用来降维的。
    one-hot或者直接ord(c)也应该没问题。

    DGA域名有一个明显的特征，及字母排序的随机性，基本不包含英文单词和中文拼音。
    可以考虑，构建英文单词和中文拼音的分词工具，基于word构建word2vec。中文首字母类的域名，算作异常样本.

    @2020-7-21，看jieba分词源码发现这样可以试试
    采用jieba分词中的HMM模型进行分词， 只针对Alexa Top10000的站点进行统计。


#### 新思路结论：
1. 用jieba分词，测试结果不是很好，主要原因还是分词词典不是很好，下面的实施中，词典来自不同的预料，对结果影响很大
2. 训练数据量不是很多

#### 新思路实施
##### 分词词典
1. 数据来源  
    - English Words
      - 数据要包含google等词，最好来自web网页，非英文词典  
      - reference： https://www.english-corpora.org/coca/  
      - github.com 搜索 **COCA frequency**
      - git https://github.com/jjzz/ZZ-WordFreq 
      - wordfreq.zz.dsl获取word frequency
        ``` python
            with open("wordfreq.zz.dsl") as fd:
            predata = ""
            for line in fd.readlines():
                data = line.strip()
                if data[0] != "\\":
                    predata = data
                else:
                    if "COCA" in data:
                        print(predata + " " + data.split(" ")[-1])
        ```
    - Chinese Pinyin
      - git https://github.com/mozillazg/pinyin-data
      - 脚本去除音标，思路：直接替换掉有音标的元音("a", "o"...)
      - 只考虑分词结果，中文拼音词频设置为100
    - 添加部分常用分词
      - 根据训练结果添加 api img cdn等，词频可以设置为1000.
    - 词频结果 [words](./english_words.txt)
2. 分词
   train.txt文件：格式： site  label;
   train.word文件： 域名，不包括后缀 .com等，来自train.txt文件
   ```
   pip install jieba 
   python -m jieba -D words.txt -n  train.word > train.result
   ```
##### word2vec 生成词向量
1. 词向量模型

``` python
from gensim.models import Word2Vec

def cal_word2vec(domains):
    w2v_list = []
    model = Word2Vec(domains, size=50,min_count=1)
    return model

def load_site_segs():
    datas = []
    with open("train.result") as fd:
        for line in fd.readlines():
            arr = line.strip().split(" ")
            datas.append(arr)
    return datas
            
datas = load_site_segs()
w2vmodel = cal_word2vec(datas)
```
2. 词向量模型保存
    ``` python
    from gensim.models import Word2Vec

    w2vmodel.save("./result/word2vec.model")
    ``` 
3. 词向量加载 
   ``` python
   from gensim.models import Word2Vec

   w2vmodel = Word2Vec.load("./result/word2vec.model")
   ```
   
##### LSTM 模型训练
1. 获取域名的词向量
   ``` python
    import jieba
    jieba.load_userdict("words.txt")

    def get_domain_seg(domain):
        return jieba.cut(domain)

    def get_domain_vect(domain, word2vec_model=None):
        
        tmp = []
        for k, v in enumerate(get_domain_seg(domain)):
            if k >= 10:
                break
            if v not in word2vec_model:
                tmp.append([0]*50)
            else:
                tmp.append(word2vec_model[v])

        for k in range(len(tmp), 10, 1):
            tmp.append([0]*50)
        return tmp
    
    # 测试
    print(get_domain_vect("google", w2vmodel))
   ```
2. 模型训练
    - 加载数据
    - 算法计算
    - 测试
    - 模型保存
    - 模型Load



