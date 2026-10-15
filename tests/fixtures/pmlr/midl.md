---
title: Does Grounding Improve Radiology Report Generation? An Empirical Study on PadChest-GR
abstract: Radiology Report Generation (RRG) aims to automatically produce clinically
  accurate descriptions of medical images, yet current models often struggle with
  incomplete findings, generic phrasing, and hallucinations due to the absence of
  explicit grounding signals. To address these limitations, we propose a grounding-based
  RRG framework that integrates spatially localized visual evidence into the generation
  process. Our approach combines a vision encoder ViT with a language decoder LLM
  GPT-2 through a lightweight transformer-based bridging module inspired by Bridge-Enhanced
  Vision Encoder–Decoder (VED) architectures. Grounding is introduced using bounding
  boxes of anatomical regions and pathologies, enabling the model to attend to both
  global and localized features. We further define a adopt the region-to-text task,
  where the model generates findings directly from specific regions of interest. Experiments
  on the PadChest-GR dataset demonstrate that grounding substantially improves linguistic
  quality and clinical accuracy, with the full image plus grounding mask configuration
  achieving the strongest gains across BLEU, ROUGE-L, CIDEr, BERTScore, CheXbert F1,
  and RadGraph F1. Analyses also show that even partial or noisy grounding yields
  consistent benefits.
layout: inproceedings
series: Proceedings of Machine Learning Research
publisher: PMLR
issn: 2640-3498
id: aas-alas26a
month: 0
tex_title: Does Grounding Improve Radiology Report Generation? An Empirical Study
  on PadChest-GR
firstpage: 1375
lastpage: 1391
page: 1375-1391
order: 1375
cycles: false
bibtex_author: Aas-Alas, Mohamed and Albiol, Alberto and Paredes, Roberto
author:
- given: Mohamed
  family: Aas-Alas
- given: Alberto
  family: Albiol
- given: Roberto
  family: Paredes
date: 2026-05-05
address:
container-title: Proceedings of The 9th International Conference on Medical Imaging
  with Deep Learning
volume: '315'
genre: inproceedings
issued:
  date-parts:
  - 2026
  - 5
  - 5
pdf: https://raw.githubusercontent.com/mlresearch/v315/main/assets/aas-alas26a/aas-alas26a.pdf
extras: []
# Format based on Martin Fenner's citeproc: https://blog.front-matter.io/posts/citeproc-yaml-for-bibliographies/
---
