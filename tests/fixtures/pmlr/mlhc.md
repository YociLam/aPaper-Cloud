---
title: 'NAST: Improving Negation Handling in Medical Vision–Language Models through
  Negation-Aware Selective Training'
abstract: Negation is a fundamental linguistic operation in clinical reporting, yet
  vision–language models (VLMs) frequently fail to distinguish affirmative from negated
  medical statements. To systematically characterize this limitation, we introduce
  MedNega-Bench, a radiology-specific diagnostic benchmark that evaluates polarity
  sensitivity under controlled clinical conditions, revealing that common medical
  VLMs consistently confuse negated and non-negated findings. To enable learning beyond
  simple condition absence, we further construct MedNega-FT, a contextual clinical
  negation dataset that encodes structured claims and supports attributelevel negations
  involving location and severity. Building on these resources, we propose Negation-Aware
  Selective Training (NAST), an interpretability-guided adaptation method that uses
  causal tracing effects (CTEs) to modulate layer-wise gradient updates during fine-tuning.
  NAST scales each layer’s update according to its causal contribution to negation
  processing, transforming mechanistic interpretability signals into a principled
  optimization rule. Experiments demonstrate improved discrimination of affirmative
  and negated clinical statements without degrading general vision–language alignment,
  highlighting the value of causal interpretability for targeted model adaptation
  in safety-critical medical settings. Code and resources are available at https://github.com/healthylaife/NAST.
layout: inproceedings
series: Proceedings of Machine Learning Research
publisher: PMLR
issn: 2640-3498
id: abbasi26a
month: 0
tex_title: 'NAST: Improving Negation Handling in Medical Vision–Language Models through
  Negation-Aware Selective Training'
firstpage: 1
lastpage: 29
page: 1-29
order: 1
cycles: false
bibtex_author: Abbasi, Ali and Taghipour, Mehdi and Beheshti, Rahmatollah
author:
- given: Ali
  family: Abbasi
- given: Mehdi
  family: Taghipour
- given: Rahmatollah
  family: Beheshti
date: 2026-09-08
address:
container-title: Proceedings of the 11th Machine Learning for Healthcare Conference
volume: '340'
genre: inproceedings
issued:
  date-parts:
  - 2026
  - 9
  - 8
pdf: https://raw.githubusercontent.com/mlresearch/v340/main/assets/abbasi26a/abbasi26a.pdf
extras: []
# Format based on Martin Fenner's citeproc: https://blog.front-matter.io/posts/citeproc-yaml-for-bibliographies/
---
