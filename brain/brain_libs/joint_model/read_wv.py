filename = 'wv/wiki.zh_classical.vec'
def load_ft(filename):
    vocab = []
    embd = []
    #file = open(filename,'r')
    count = 0
    with open(filename,'r') as file:
        for line in file.readlines():
            row = line.strip().split(' ')
            vocab.append(row[0])
            embd.append(row[1:])
            count += 1
            if count == 20:
                break
    print('Loaded FastText!')
    #file.close()
    return vocab,embd

vocab,embd = load_ft(filename)
print(vocab)
#print(embd)
#vocab_size = len(vocab)
#embedding_dim = len(embd[0])
#embedding = np.asarray(embd)
