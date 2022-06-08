from paddlenlp.datasets import MapDataset

def load_dataset(datafiles):
    def read(data_path):
        with open(data_path, 'r', encoding='utf-8') as fd:
            next(fd)

            for line in fd.readlines():
                words, lables = line.strip('\n').split('\t')
                words = words.split('\002')
                lables = lables.split('\002')

                yield words, lables

    if isinstance(datafiles, str):
        return MapDataset(list(read(datafiles)))
    elif isinstance(datafiles, list) or isinstance(datafiles, tuple):
        return [MapDataset(list(read(datafile))) for datafile in datafiles]


def load_dict(dictfile):
    dicts = {}
    i = 0
    with open(dictfile, 'r', encoding='utf-8') as fd:
        for line in fd.readlines():
            dicts[line.strip('\n')] = i
            i += 1

    return dicts


def convert_tokens_to_ids(tokens, vocab, oov_token=None):
    token_ids = []

    oov_id = vocab.get(oov_token) if oov_token else None

    for token in tokens:
        token_id = vocab.get(token, oov_id)
        token_ids.append(token_id)

    return token_ids


# 训练数据转换
def convert_example(example, word_vocab, tag_vocab):
    words, labels = example

    word_ids = convert_tokens_to_ids(words, word_vocab, 'OOV')
    label_ids = convert_tokens_to_ids(labels, tag_vocab, 'O')

    return word_ids, len(word_ids), label_ids

# 预测数据转换
def convert_raw(raw_input, word_vocab):
    return convert_tokens_to_ids(raw_input, word_vocab)

def load_embedding(embedding_file):
    emb = paddle.nn.Embedding(word_num, emb_size)

    para_state_dict = paddle.load(embedding_file)
    emb.set_state_dict(para_state_dict)

    return emb

def save_embedding(emb, embedding_file):
    state_dict = emb.state_dict()
    paddle.save(state_dict, embedding_file)

def parse_decodes(data, decodes, label_vocab):
    id_label = dict(zip(label_vocab.values(), label_vocab.keys()))

    tags = [id_label[x] for x in decodes]

    sent_out = []
    tags_out = []
    words = ""
    for s, t in zip(data, tags):
        if t.endswith('-B') or t == 'O':
            if len(words):
                sent_out.append(words)
            tags_out.append(t.split('-')[0])
            words = s
        else:
            words += s
    if len(sent_out) < len(tags_out):
        sent_out.append(words)

    return sent_out, tags_out

tag_vocab = load_dict("data/tag.dic")

word_vocab = load_dict("data/word.dic")

