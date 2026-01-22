# Architectures Proposed in "Efficient Estimation of Word Representations in Vector Space"

## Paper Overview
**Authors:** Tomas Mikolov, Kai Chen, Greg Corrado, Jeffrey Dean (Google Inc.)

This paper proposes **two novel model architectures** for computing continuous vector representations of words (word embeddings) from very large datasets.

---

## 1. Continuous Bag-of-Words Model (CBOW)

### Description:
- Similar to feedforward NNLM but with the **non-linear hidden layer removed**
- The projection layer is **shared for all words** (vectors are averaged)
- All words get projected into the same position
- Uses **bag-of-words approach** - the order of words in the history does not influence the projection
- Uses words from both **past and future context** (4 history words + 4 future words)
- Predicts the **current (middle) word** based on the surrounding context

### Training Complexity:
**Q = N × D + D × log₂(V)**

Where:
- N = number of context words
- D = dimensionality of word vectors
- V = vocabulary size

### Key Features:
- Much faster training than traditional neural network language models
- Performs well on **syntactic tasks**
- Can be trained efficiently on large datasets

---

## 2. Continuous Skip-gram Model

### Description:
- **Opposite approach to CBOW**
- Instead of predicting the current word from context, it predicts **surrounding context words** from the current word
- Uses the current word as input to a log-linear classifier
- Predicts words within a certain range before and after the current word
- Gives **less weight to distant words** by sampling less from them

### Training Complexity:
**Q = C × (D + D × log₂(V))**

Where:
- C = maximum distance of words (context window)
- D = dimensionality of word vectors
- V = vocabulary size

### Key Features:
- Performs significantly better on **semantic tasks**
- Slightly worse than CBOW on syntactic tasks
- Training is about 3x slower than CBOW
- Achieved state-of-the-art performance on word similarity tasks

---

## Comparison with Previous Architectures

The paper also discusses (but does not propose) these existing architectures for comparison:

1. **Feedforward Neural Net Language Model (NNLM)**
   - Has input, projection, hidden, and output layers
   - Complexity: Q = N × D + N × D × H + H × V
   
2. **Recurrent Neural Net Language Model (RNNLM)**
   - Has input, hidden, and output layers (no projection layer)
   - Uses recurrent matrix connecting hidden layer to itself
   - Complexity: Q = H × H + H × V

---

## Performance Highlights

### CBOW Results:
- Best performance: **63.7% accuracy** (1000-dimensional vectors, 6B words)
- Semantic accuracy: 57.3%
- Syntactic accuracy: 68.9%

### Skip-gram Results:
- Best performance: **65.6% accuracy** (1000-dimensional vectors, 6B words)
- Semantic accuracy: 66.1%
- Syntactic accuracy: 65.1%
- Particularly strong on **semantic relationships** like country-capital pairs

---

## Key Innovations

1. **Simplified Architecture:** Removed non-linear hidden layers to enable training on much larger datasets
2. **Computational Efficiency:** Both models train much faster than traditional neural network language models
3. **Scalability:** Can be trained on billions of words in reasonable time (less than a day for CBOW)
4. **Quality:** Achieved state-of-the-art performance on word similarity and analogy tasks

---

## Summary

The paper's main contribution is introducing **CBOW and Skip-gram** as efficient alternatives to complex neural network language models. These architectures enabled training high-quality word vectors on much larger datasets, leading to the development of **Word2Vec**, one of the most influential word embedding methods in NLP.
