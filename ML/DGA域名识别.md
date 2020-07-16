## DGA域名识别

### 实现

#### 代码参考

```
    https://github.com/0FuzzingQ/dga_check
```

#### 实现思路
   
1. word2vec，生成a-z,-,0-9的词向量
2. 采用LSTM模型，sigmoid激活
3. Lost crossentropy
4. 结果
   
   训练结果准确率95%左右
5. 部署之后，识别出的异常域名请求[微步](https://x.threatbook.cn/)验证是否为DGA域名。否，则构建白名单，用作下一步的模型增强训练。

#### 实施中的问题以及更改点

1. 因语料中，词总共才37个，没必要使用100维度表示，将为20
2. 数据问题
   
    参考代码中的数据比较老，异常数据使用[domain_generation_algorithms](https://github.com/baderj/domain_generation_algorithms)的数据，随机选取1w条。正常域名选用alexa Top 1W+。

    训练之后的结果在实际使用中的误差较高，很多中文拼音的域名都识别为DGA域名， 例如 **bilibi.com**等。解决方案：加入中文拼音样本

    中文首字母类的域名，算作异常样本。


### 新思路

    DGA域名有一个明显的特征，及字母排序的随机性，基本不包含英文单词和中文拼音。
    可以考虑，构建英文单词和中文拼音的分词攻击，基于word构建word2vec。中文首字母类的域名，算作异常样本。

    算法可以考虑使用逻辑回归，准确度应该不会太差。




