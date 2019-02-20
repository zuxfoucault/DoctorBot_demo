import data_helper
import numpy as np
import progressbar
import gc

from metrics.accuracy import conlleval

from keras.models import Sequential
from keras.layers.embeddings import Embedding
from keras.layers.recurrent import SimpleRNN, GRU, LSTM
from keras.layers.core import Dense, Dropout
from keras.layers.wrappers import TimeDistributed
from keras.layers import Convolution1D

sentence_file = "data/training_sentence.txt"
slot_file = "data/training_slot.txt"
sentence_training_file = "data/sentence_training.txt"
sentence_developing_file = "data/sentence_developing.txt"
slot_training_file = "data/slot_training.txt"
slot_developing_file = "data/slot_developing.txt"

filepath_model = 'model/GRU_model30.h5'

class SlotFilling(object):
    def __init__(self):
        pass

    def train(self):
        # Prepare data
        sentence_train, slot_train, sentence_dev, slot_dev, vocab_sentence,\
            vocab_slot = data_helper.prepare_data(
                                    "data",
                                    sentence_training_file,
                                    slot_training_file,
                                    sentence_developing_file,
                                    slot_developing_file,
                                    from_vocabulary_size=2000,
                                    to_vocabulary_size=2000,
                                    tokenizer=None)
        sentence_developing, slot_devloping = data_helper.read_data(
            sentence_dev, slot_dev, max_size=None)
        sentence_training, slot_training = data_helper.read_data(
            sentence_train, slot_train, max_size=None)

        ## TODO:
        #sentence_training, slot_training = sentence_training[:1000],\
        #    slot_training[:1000]

        # Dictionaries
        w2id_sentence, id2w_sentence = data_helper.initialize_vocabulary(vocab_sentence)
        w2id_slot, id2w_slot = data_helper.initialize_vocabulary(vocab_slot)

        # For conlleval script
        words_train = [list(map(lambda x: id2w_sentence[x].decode('utf8'), w)) for w in sentence_training]
        labels_train = [list(map(lambda x: id2w_slot[x].decode('utf8'), y)) for y in slot_training]
        words_val = [list(map(lambda x: id2w_sentence[x].decode('utf8'), w)) for w in sentence_developing]
        labels_val = [list(map(lambda x: id2w_slot[x].decode('utf8'), y)) for y in slot_devloping]

        # Define model
        n_vocab = len(w2id_sentence)
        n_classes = len(w2id_slot)

        #model = Sequential()
        #model.add(Embedding(n_vocab,100))
        #model.add(Convolution1D(128, 5, border_mode='same', activation='relu'))
        #model.add(Dropout(0.25))
        #model.add(GRU(100,return_sequences=True))
        #model.add(TimeDistributed(Dense(n_classes, activation='softmax')))
        #model.compile('rmsprop', 'categorical_crossentropy')

        ## Training
        ##n_epochs = 30
        #n_epochs = 1

        train_f_scores = []
        val_f_scores = []
        best_val_f1 = 0

        #print("Training =>")
        #train_pred_label = []
        #avgLoss = 0

        #for i in range(n_epochs):
        #    print("Training epoch {}".format(i))

        #    bar = progressbar.ProgressBar(max_value=len(sentence_training))
        #    for n_batch, sent in bar(enumerate(sentence_training)):
        #        label = slot_training[n_batch]
        #        # Make labels one hot
        #        label = np.eye(n_classes)[label][np.newaxis, :]
        #        # View each sentence as a batch
        #        sent = sent[np.newaxis, :]

        #        if sent.shape[1] > 1: #ignore 1 word sentences
        #            loss = model.train_on_batch(sent, label)
        #            avgLoss += loss

        #        pred = model.predict_on_batch(sent)
        #        pred = np.argmax(pred, -1)[0]
        #        train_pred_label.append(pred)

        #    avgLoss = avgLoss/n_batch

        #    predword_train = [list(map(lambda x: id2w_slot[x].decode('utf8'), y))
        #                      for y in train_pred_label]
        #    con_dict = conlleval(predword_train, labels_train,
        #                         words_train, 'measure.txt')
        #    train_f_scores.append(con_dict['f1'])
        #    print('Loss = {}, Precision = {}, Recall = {}, F1 = {}'.format(
        #        avgLoss, con_dict['r'], con_dict['p'], con_dict['f1']))
        #    # Save model
        #    model.save(filepath_model)
        #    gc.collect()

        print("Validating =>")
        from keras.models import load_model
        model = load_model(filepath_model)

        labels_pred_val = []
        avgLoss = 0

        bar = progressbar.ProgressBar(max_value=len(sentence_developing))
        for n_batch, sent in bar(enumerate(sentence_developing)):
            label = slot_devloping[n_batch]
            label = np.eye(n_classes)[label][np.newaxis, :]
            sent = sent[np.newaxis, :]

            if sent.shape[1] > 1: #some bug in keras
                loss = model.test_on_batch(sent, label)
                avgLoss += loss

            pred = model.predict_on_batch(sent)
            pred = np.argmax(pred, -1)[0]
            labels_pred_val.append(pred)

        avgLoss = avgLoss/n_batch
        gc.collect()

        predword_val = [list(map(lambda x: id2w_slot[x].decode('utf8'), y))
                        for y in labels_pred_val]
        con_dict = conlleval(predword_val, labels_val,
                             words_val, 'measure.txt')
        val_f_scores.append(con_dict['f1'])
        print('Loss = {}, Precision = {}, Recall = {}, F1 = {}'.format(
            avgLoss, con_dict['r'], con_dict['p'], con_dict['f1']))

        if con_dict['f1'] > best_val_f1:
            best_val_f1 = con_dict['f1']
            print('here')
            with open('model_architecture.json', 'w') as outf:
                outf.write(model.to_json())
            model.save_weights('best_model_weights.h5', overwrite=True)
            print("Best validation F1 score = {}".format(best_val_f1))
        print()


def main():
    sf = SlotFilling()
    sf.train()

if __name__ == '__main__':
    main()
