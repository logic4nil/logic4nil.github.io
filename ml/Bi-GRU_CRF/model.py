# -*- encoding:utf8 -*-

import paddle.nn as nn

from paddlenlp.layers import LinearChainCrf, ViterbiDecoder
from paddlenlp.embeddings import TokenEmbedding

class BiGRUWithCRF(nn.Layer):
    def __init__(self, 
                 emb_size, 
                 hidden_size,
                 word_num, # 需要编码的字数
                 label_num,
                 use_w2v_emb=False):
        super(BiGRUWithCRF, self).__init__()


        # 使用预训练模型
        if use_w2v_emb:
            self.word_emb = TokenEmbedding(
                    extended_vocab_path='./data/word.dic', unknown_token='OOV')
        else:
            self.word_emb = nn.Embedding(word_num, emb_size)

        self.emb_size = emb_size
        self.hidden_size = hidden_size

        self.gru = nn.GRU(emb_size, 
                          hidden_size, 
                          num_layers=2, 
                          direction='bidirectional')

        self.fc = nn.Linear(hidden_size * 2, label_num + 2)
        self.crf = LinearChainCrf(label_num)
        self.decoder = ViterbiDecoder(self.crf.transitions)


    def forward(self, x, lens):
        embs = self.word_emb(x)
        output, _ = self.gru(embs)
        output = self.fc(output)

        _, pred = self.decoder(output, lens)

        return output, lens, pred

