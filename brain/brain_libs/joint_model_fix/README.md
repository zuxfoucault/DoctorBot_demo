# LU_MODEL

## Usage:
### Get LU prediction in a cmd environment:
`python3 get_lu_pred.py` will get a cmd prompt for input sentence iteration.

### Get LU prediction as a object output:
	import get_lu_pred as lu
	model = lu.LuModel()
	intent, slot = model.get_lu_pred(sentence=sentence)
	model.sess.close()  # Close tensorflow session

### Training model:
`python3 run_multi-task_rnn.py`  

### Prerequisites:
Tensorflow, jieba


### References
Code modified from https://github.com/HadoopIt/rnn-nlu
