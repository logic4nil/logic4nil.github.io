# -*- encoding:utf8 -*-
import os

import paddle

from model import *
from utils import *

if __name__ == "__main__":
    tag_vocab = load_dict("data/tag.dic")
    word_vocab = load_dict("data/word.dic")

    m = BiGRUWithCRF(300, 300, len(word_vocab), len(tag_vocab), True)
    
    m.eval()

    m = paddle.jit.to_static(
            m, 
            input_spec=[
                paddle.static.InputSpec(shape=[None, None], dtype="int64", name="x"),  # input_ids: [batch_size, max_seq_len]
                paddle.static.InputSpec( shape=[None], dtype="int64", name="lens")
            ]
        )
            
    save_path = os.path.join("export", "inference")
    paddle.jit.save(m, save_path)

