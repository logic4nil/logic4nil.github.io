## HMM 与 CRF的区别与联系

## HMM 

jieba分词工具是使用HMM模型最成功的例子。 

jieba分词中，对词典中没有出现过的词组，通过HMM实现粉刺。

jieba的代码比较简单，可以参考代码学习HMM的应用。

这是我之前学习jieba源码中，重点内容的记录 [jieba](!./jieba.md)

## 从HMM推导CRF

### HMM的两个假设
 - 齐次马尔科夫性假，类比HMM中的转换
    $$ P(i_{t}|i_{t-1},...,i_{1}) = P(i_{t}|i_{t-1}) $$
    即t时刻的状态只能依赖于前一时刻的状态，与其他时刻的状态和观测无关，并且与时刻t无关
 - 观测独立性假设，类比HMM中的状态
    $$ P(o_{t}|i_{t}, o_{t-1}, i_{t-1},...,o_{1},t_{1}) = P(o_{t}|i_{t}) $$

### HMM的联合概率

HMM是生成模型，对P(x,y)联合概率分布进行建模，其中y是状态变量，x是观测变量（输入）

