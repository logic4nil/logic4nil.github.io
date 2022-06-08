from functools import partial
from paddlenlp.data import Stack, Tuple, Pad

import argparse
import numpy as np

# 引用 paddle inference 预测库
import paddle.inference as paddle_infer

from paddlenlp.embeddings import TokenEmbedding

from utils import *


word_emb = TokenEmbedding(
        extended_vocab_path='./data/word.dic', unknown_token='OOV')


def predict(input_text):
    args = parse_args()

    # 创建 config
    config = paddle_infer.Config(args.model_file, args.params_file)

    # 根据 config 创建 predictor
    predictor = paddle_infer.create_predictor(config)


    input_handles = [
            predictor.get_input_handle(name)
            for name in predictor.get_input_names()
        ]

    input1_ids = convert_raw(input_text, word_vocab)
    input1_lens = len(input_text)


    batchify_fn = lambda examples, fn = Tuple(
        Pad(axis=0, pad_val=word_vocab.get('OOV')),  # token_ids
        Stack(),  # seq_len
    ): fn(examples)

    data = batchify_fn([[input1_ids, input1_lens]])

    input_handles = [
        predictor.get_input_handle(name)
        for name in predictor.get_input_names()
        ]

    for input_field, input_handle in zip(data, input_handles):
        input_handle.copy_from_cpu(input_field)    

    predictor.run()

    output_handles = [
                predictor.get_output_handle(name)
                for name in predictor.get_output_names()
            ]
    # 从输出句柄获取预测结果
    _, _, decodes = [output_handle.copy_to_cpu() for output_handle in output_handles]
    # 打印预测结果
    print(parse_decodes(input_text, decodes[0], tag_vocab))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_file", type=str, default="export/inference.pdmodel",  help="model filename")
    parser.add_argument("--params_file", type=str, default="export/inference.pdiparams", help="parameter filename")

    return parser.parse_args()

if __name__ == "__main__":
    raw_input1 = '黑龙江省双鸭山市尖山区八马路与东平行路交叉口北40米韦业涛18600009172'

    raw_input2 = '广西壮族自治区桂林市雁山区雁山镇西龙村老年活动中心17610348888羊卓卫'

    predict(raw_input2)


