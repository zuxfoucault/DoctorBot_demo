# train_model.SlotFilling

## Usage:
### Training mode:
`python3 train_model.py`

### Decoding mode:
Reverse the comment mark in line 22[3-4].
`python3 train_model.py`

**Or**
```
import train_model
sf = train_model.SlotFilling()
slot = sf.decode(“sentence”)
```

### Prerequisites:
Tensorflow, Keras

Manually generate data and model directories for storing data and model, respectively.

### Toy data:
Uncomment line 11[1-5] in train_model.py to apply toy data
