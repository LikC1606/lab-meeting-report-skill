# Synthetic example: journal club input

> This fictional paper and all reported values are synthetic. They exist only to demonstrate the skill workflow and must not be cited as real research.

## Paper metadata supplied

- Title: Contrastive Retrieval for Low-Resource Intent Classification
- Authors: not supplied
- Venue: not supplied
- Year: not supplied
- DOI: not supplied
- Local source: `papers/synthetic-retrieval-notes.md`

## Research question

Can hard-negative contrastive training improve retrieval for low-resource intent classification across domains?

## Method notes

- Six synthetic domains
- 500 labeled examples per domain
- Bi-encoder retrieval model
- Hard-negative mining from the two nearest incorrect intents
- Five random seeds
- Baselines: standard bi-encoder and a lexical retrieval system

## Results supplied

- Average in-domain macro-F1: standard bi-encoder 0.68; proposed method 0.74
- Cross-domain macro-F1: standard bi-encoder 0.61; proposed method 0.65
- Ablation without hard-negative mining: 0.70 in-domain macro-F1
- Lexical baseline value was not included in the notes

## Authors' claims in the notes

- Hard-negative mining is responsible for most of the gain.
- The method generalizes across domains.

## Limitations visible in the notes

- Dataset access is not provided.
- Code is not linked.
- Hyperparameters are only partially listed.
- Compute cost is not reported.
- Domain class balance is not described.
