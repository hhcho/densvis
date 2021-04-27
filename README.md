# densVis #
This repository contains density-preserving data visualization tools **den-SNE** and **densMAP**,
augmenting the tools t-SNE and UMAP respectively.

A detailed README for each algorithm (including installation notes, usage guidelines, and example scripts) is provided in its respective subdirectory.
Direct links: [den-SNE](https://github.com/hhcho/densvis/tree/master/densne) and [densMAP](https://github.com/hhcho/densvis/tree/master/densmap).

<p align="center">
<img src="http://cb.csail.mit.edu/cb/densvis/fig_workflow_final_web.jpg">
</p>

## Reference
Our algorithms are described in the following manuscript: 

Ashwin Narayan, Bonnie Berger\*, and Hyunghoon Cho\*, ["Assessing single-cell transcriptomic variability through density-preserving data visualization"](https://www.nature.com/articles/s41587-020-00801-7), *Nature Biotechnology*, 2021

 and an earlier preprint:

Ashwin Narayan, Bonnie Berger\*, and Hyunghoon Cho\*. ["Density-Preserving Data Visualization Unveils Dynamic Patterns of Single-Cell Transcriptomic Variability"](https://www.biorxiv.org/content/10.1101/2020.05.12.077776v1), *bioRxiv*, 2020.

## Notes
<b>densMAP is now available as part of the Python [UMAP](https://github.com/lmcinnes/umap) package. </b>

Our den-SNE software is based on the Barnes-Hut implementation of t-SNE (https://github.com/lvdmaaten/bhtsne) described in the following paper:

Laurens Van Der Maaten. "Accelerating t-SNE using Tree-based Algorithms", *Journal of Machine Learning Research*, 15(1), 2014.

Our densMAP software is based on the implementation of UMAP (https://github.com/lmcinnes/umap) described in the following paper:

Leland McInnes, John Healy, and James Melville. "UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction", *arXiv*, 1802.03426, 2018.

## License
Both den-SNE and densMAP are licensed under the MIT license. See each subdirectory for detail.

## Contact for questions about software
Ashwin Narayan, [ashwinn@mit.edu](mailto:ashwinn@mit.edu) \
Hyunghoon Cho, [hhcho@broadinstitute.org](mailto:hhcho@broadinstitute.org)
