---
title: Cached Summary Embeddings for Memory-Efficient EHR Inference
abstract: 'Transformer-based clinical prediction models face a deployment challenge:
  processing long patient histories can require memory that exceeds available resources
  in resource-constrained settings. We propose a deployment architecture that separates
  expensive historical encoding from lightweight inference. In an offline preprocessing
  phase, a clinical language model compresses each patient’s historical events into
  a fixed-size vector (768 dimensions, 5 KB per patient). At inference time, the prediction
  model processes only a short window of recent events, conditioned on the cached
  summary. Through 252 experiments on a 24-hour in-ICU mortality cohort from MIMIC-IV,
  we characterize when this architecture provides value. The benefit of cached summaries
  decays as the recent context window grows: a 6.5% relative AUROC improvement at
  $N$=8 recent events ($p < 0.001$) shrinks to a negligible 0.1% at $N$=256 (not statistically
  significant). We find that Feature-wise Linear Modulation (FiLM) outperforms token
  injection for integrating summaries ($p < 0.001$). Our results provide deployment
  guidance: when hardware constraints limit the recent context to 32 events or fewer,
  cached summaries recover meaningful predictive signal; when longer sequences are
  feasible, the caching overhead is not justified.'
layout: inproceedings
series: Proceedings of Machine Learning Research
publisher: PMLR
issn: 2640-3498
id: al-attrach26a
month: 0
tex_title: Cached Summary Embeddings for Memory-Efficient EHR Inference
firstpage: 778
lastpage: 793
page: 778-793
order: 778
cycles: false
bibtex_author: Al Attrach, Rafi and Fani, Rajna and Restrepo, David and Jia, Yugang
  and Celi, Leo Anthony and Schuffler, Peter
author:
- given: Rafi
  family: Al Attrach
- given: Rajna
  family: Fani
- given: David
  family: Restrepo
- given: Yugang
  family: Jia
- given: Leo Anthony
  family: Celi
- given: Peter
  family: Schuffler
date: 2026-06-29
address:
container-title: Proceedings of the 7th Conference on Health, Inference, and Learning
volume: '333'
genre: inproceedings
issued:
  date-parts:
  - 2026
  - 6
  - 29
pdf: https://raw.githubusercontent.com/mlresearch/v333/main/assets/al-attrach26a/al-attrach26a.pdf
extras: []
# Format based on Martin Fenner's citeproc: https://blog.front-matter.io/posts/citeproc-yaml-for-bibliographies/
---
