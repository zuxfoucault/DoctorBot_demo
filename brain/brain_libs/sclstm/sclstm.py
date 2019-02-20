import tensorflow as tf

class RNN_cell(object):
  def __init__(self, source_vocab_size, tag_vocab_size, label_vocab_size, buckets,
               word_embedding_size, size, num_layers, max_gradient_norm, batch_size,
               dropout_keep_prob=1.0, use_lstm=False, bidirectional_rnn=True,
               num_samples=1024, use_attention=False,
               task=None, forward_only=False):
    self.source_vocab_size = source_vocab_size
    self.tag_vocab_size = tag_vocab_size
    self.label_vocab_size = label_vocab_size
    self.buckets = buckets
    self.batch_size = batch_size
    self.global_step = tf.Variable(0, trainable=False)

    # If we use sampled softmax, we need an output projection.
    softmax_loss_function = None

    # Create the internal multi-layer cell for our RNN.
    single_cell = tf.contrib.rnn.GRUCell(size)
    if use_lstm:
      single_cell = tf.contrib.rnn.BasicLSTMCell(size)
    cell = single_cell
    if num_layers > 1:
      cell = tf.contrib.rnn.MultiRNNCell([single_cell for _ in range(num_layers)])
      #cell = tf.contrib.rnn.MultiRNNCell([single_cell] * num_layers)

    if not forward_only and dropout_keep_prob < 1.0:
      cell = tf.contrib.rnn.DropoutWrapper(cell,
                                           input_keep_prob=dropout_keep_prob,
                                           output_keep_prob=dropout_keep_prob)


    # Feeds for inputs.
    self.encoder_inputs = []
    self.tags = []
    self.tag_weights = []
    self.labels = []
    self.sequence_length = tf.placeholder(tf.int32, [None], name="sequence_length")

    for i in xrange(buckets[-1][0]):
      self.encoder_inputs.append(tf.placeholder(tf.int32, shape=[None],
                                                name="encoder{0}".format(i)))
    for i in xrange(buckets[-1][1]):
      self.tags.append(tf.placeholder(tf.float32, shape=[None], name="tag{0}".format(i)))
      self.tag_weights.append(tf.placeholder(tf.float32, shape=[None],
                                                name="weight{0}".format(i)))
    self.labels.append(tf.placeholder(tf.float32, shape=[None], name="label"))

    # Initiate embedding
    self.embedding = variable_scope.get_variable("embedding", [self.source_vocab_size, word_embedding_size])
    #self.embedding = tf.Variable(tf.constant(0.0, shape= [self.source_vocab_size, word_embedding_size]), name="embedding")

    base_rnn_output = generate_encoder_output.generate_embedding_RNN_output(self.encoder_inputs,
                                                                            cell,
                                                                            self.source_vocab_size,
                                                                            word_embedding_size,
                                                                            embedding=self.embedding,
                                                                            dtype=dtypes.float32,
                                                                            scope=None,
                                                                            sequence_length=self.sequence_length,
                                                                            bidirectional_rnn=bidirectional_rnn)
    encoder_outputs, encoder_state, attention_states = base_rnn_output

