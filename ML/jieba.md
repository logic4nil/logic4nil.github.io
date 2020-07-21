## 结巴分词 源码学习
### 词典分词
完全依靠词典进行分词
 ``` python
    # 分词
    def get_DAG(self, sentence):
            self.check_initialized()
            DAG = {}
            N = len(sentence)
            for k in xrange(N):
                tmplist = []
                i = k
                frag = sentence[k]
                while i < N and frag in self.FREQ:
                    if self.FREQ[frag]:
                        tmplist.append(i)
                    i += 1
                    frag = sentence[k:i + 1]
                if not tmplist:
                    tmplist.append(k)
                DAG[k] = tmplist
            return DAG
```

``` python
    # 计算各分词，最大概率词组。采用DP算法
    def calc(self, sentence, DAG, route):
        N = len(sentence)
        route[N] = (0, 0)
        logtotal = log(self.total)
        for idx in xrange(N - 1, -1, -1):
            route[idx] = max((log(self.FREQ.get(sentence[idx:x + 1]) or 1) -
                              logtotal + route[x + 1][0], x) for x in DAG[idx])
```

以上代码采用的是后向分词方式，判断最大概率也是后向的方案实现的。   
前线方案理论上也可以实现，分词代码改为以k结尾的分词词组， DP算法从0->N-1计算所有结果。

### HMM模型

用来解决字典中没有记录的词。  
采用HMM模型，把中文词汇分为BEMS四个状态。B(开头)，M(中间)，E(结尾)，S(独立成词) 

``` python
    # start_p
    # trans_P:
    #    {'B': {'E': 0.8518218565181658, 'M': 0.14817814348183422},
    #   'E': {'B': 0.5544853051164425, 'S': 0.44551469488355755},
    #   'M': {'E': 0.7164487459986911, 'M': 0.2835512540013088},
    #   'S': {'B': 0.48617017333894563, 'S': 0.5138298266610544}}
    # emit_P: P("和"|M) 表示M状态，出现“和”概率

    def _cut():
        ...
        prob, pos_list = viterbi(sentence, 'BMES', start_P, trans_P, emit_P)
        ...
    
    PrevStatus = {
        'B': 'ES',
        'M': 'MB',
        'S': 'SE',
        'E': 'BM'
    }

    def viterbi(obs, states, start_p, trans_p, emit_p):
        V = [{}]  # tabular
        path = {}

        # 计算首字符的各状态的概率
        for y in states:  # init
            V[0][y] = start_p[y] + emit_p[y].get(obs[0], MIN_FLOAT)
            path[y] = [y]
        for t in xrange(1, len(obs)):
            V.append({})
            newpath = {}
            # 计算前一字符确定情况下，当前字符state最大概率。
            for y in states:
                em_p = emit_p[y].get(obs[t], MIN_FLOAT)
                (prob, state) = max(
                    [(V[t - 1][y0] + trans_p[y0].get(y, MIN_FLOAT) + em_p, y0) for y0 in PrevStatus[y]])
                V[t][y] = prob
                newpath[y] = path[state] + [y]
            path = newpath

        (prob, state) = max((V[len(obs) - 1][y], y) for y in 'ES')

        return (prob, path[state])
```