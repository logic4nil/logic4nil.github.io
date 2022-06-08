from functools import partial

import paddle
from paddlenlp.data import Stack, Tuple, Pad
from paddlenlp.layers import LinearChainCrfLoss
from paddlenlp.metrics import ChunkEvaluator

from model import *
from utils import *

def do_train():
    train_ds, dev_ds = load_dataset(datafiles=("data/train.txt", "data/test.txt"))

    # dev_ds = load_dataset("data/test.txt")

    tag_vocab = load_dict("data/tag.dic")
    word_vocab = load_dict("data/word.dic")

    convert = partial(convert_example, word_vocab=word_vocab, tag_vocab=tag_vocab)

    train_ds.map(convert)
    dev_ds.map(convert)


    batchify_fn = lambda examples, fn = Tuple(
        Pad(axis=0, pad_val=word_vocab.get('OOV')),  # token_ids
        Stack(),  # seq_len
        Pad(axis=0, pad_val=tag_vocab.get('O'))  # label_ids
    ): fn(examples)
    

    train_ds_loader = paddle.io.DataLoader(
        dataset = train_ds,
        batch_size = 32,
        shuffle = True,
        drop_last = True,
        return_list = True,
        collate_fn=batchify_fn
    )

    dev_ds_loader = paddle.io.DataLoader(
        dataset = dev_ds,
        batch_size = 32,
        shuffle = True,
        drop_last = True,
        return_list = True,
        collate_fn=batchify_fn
    )

    use_w2v_emb = True

    network = BiGRUWithCRF(300, 300, len(word_vocab), len(tag_vocab), use_w2v_emb)

    model = paddle.Model(network)

    optimizer = paddle.optimizer.Adam(learning_rate=0.001, parameters=model.parameters())
    crf_loss = LinearChainCrfLoss(network.crf)
    
    chunk_evaluator = ChunkEvaluator(label_list=tag_vocab.keys(), suffix=True)

    model.prepare(optimizer, crf_loss, chunk_evaluator)

    model.fit(train_data=train_ds_loader,
              eval_data=dev_ds_loader,
              epochs=5,
              save_dir='./results',
              log_freq=10)


if __name__ == "__main__":
    do_train()

