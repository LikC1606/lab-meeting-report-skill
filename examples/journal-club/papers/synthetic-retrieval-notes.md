# Synthetic example: contrastive retrieval paper notes

> This paper, its results, and its metadata are fictional and must not be cited as real research.

## Metadata

- Title: Contrastive Retrieval for Low-Resource Intent Classification
- Authors, venue, year, and DOI: not supplied

## Method

- Six synthetic domains with 500 labeled examples per domain
- Bi-encoder retrieval model
- Hard-negative mining from the two nearest incorrect intents
- Five random seeds
- Baselines: standard bi-encoder and a lexical retrieval system

## Results

- Average in-domain macro-F1: standard bi-encoder 0.68; proposed method 0.74
- Cross-domain macro-F1: standard bi-encoder 0.61; proposed method 0.65
- Ablation without hard-negative mining: 0.70 in-domain macro-F1
- Lexical baseline value: not supplied

## Limitations in the supplied notes

- Dataset and code access are not provided.
- Hyperparameters are incomplete.
- Compute cost and domain class balance are not reported.
