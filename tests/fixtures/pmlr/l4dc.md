---
title: Balance Equation-based Distributionally Robust Offline Imitation Learning
section: Poster
openreview: GV8D1hvvp8
abstract: Imitation Learning (IL) has proven highly effective for robotic and control
  tasks where manually designing reward functions or explicit controllers is infeasible.
  However, standard IL methods implicitly assume that the environment dynamics remain
  fixed between training and deployment. In practice, this assumption rarely holds
  where modeling inaccuracies, real-world parameter variations, and adversarial perturbations
  can all induce shifts in transition dynamics, leading to severe performance degradation.
  We address this challenge through Balance Equation-based Distributionally Robust
  Offline Imitation Learning, a framework that learns robust policies solely from
  expert demonstrations collected under nominal dynamics, without requiring further
  environment interaction. We formulate the problem as a distributionally robust optimization
  over an uncertainty set of transition models, seeking a policy that minimizes the
  imitation loss under the worst-case transition distribution. Importantly, we show
  that this robust objective can be reformulated entirely in terms of the nominal
  data distribution, enabling tractable offline learning. Empirical evaluations on
  continuous-control benchmarks demonstrate that our approach achieves superior robustness
  and generalization compared to state-of-the-art offline IL baselines, particularly
  under perturbed or shifted environments.
layout: inproceedings
series: Proceedings of Machine Learning Research
publisher: PMLR
issn: 2640-3498
id: agrawal26a
month: 0
tex_title: Balance Equation-based Distributionally Robust Offline Imitation Learning
firstpage: 1916
lastpage: 1938
page: 1916-1938
order: 1916
cycles: false
bibtex_author: Agrawal, Rishabh and Alvi, Yusuf and Jain, Rahul and Nayyar, Ashutosh
author:
- given: Rishabh
  family: Agrawal
- given: Yusuf
  family: Alvi
- given: Rahul
  family: Jain
- given: Ashutosh
  family: Nayyar
date: 2026-06-07
address:
container-title: Proceedings of The 8th Annual Learning for Dynamics and Control Conference
volume: '331'
genre: inproceedings
issued:
  date-parts:
  - 2026
  - 6
  - 7
pdf: https://raw.githubusercontent.com/mlresearch/v331/main/assets/agrawal26a/agrawal26a.pdf
extras: []
# Format based on Martin Fenner's citeproc: https://blog.front-matter.io/posts/citeproc-yaml-for-bibliographies/
---
