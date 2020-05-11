# den-SNE

This software package contains an implementation of density-preserving data visualization tool **den-SNE**, which augments the [Barnes-Hut t-SNE](https://github.com/lvdmaaten/bhtsne) algorithm (based on the latest version as of May 2020; tag `d76dccd`).
Some of the following instructions are adapted from the t-SNE repository.

## Installation

On Linux or OS X, compile the source using the following command:

```
g++ sptree.cpp densne.cpp densne_main.cpp -o den_sne -O2
```

The executable will be called `den_sne`.

## Usage

The code comes with wrappers for Matlab and Python. These wrappers write your data to a file called `data.dat`, run the `den_sne` binary, and read the result file `result.dat` that the binary produces. 

### Example usage in Python:

```python
import numpy as np
import densne

from sklearn.datasets import fetch_openml
from sklearn.utils import resample

digits = fetch_openml(name='mnist_784')

subsample, subsample_labels = resample(digits.data, digits.target, n_samples=7000,
                                       stratify=digits.target, random_state=1)

embedding, ro, re = densne.run_densne(subsample)
```

The function `run_densne` takes in a number of parameters that can be set by the user:
```python
densne.run_densne(data, no_dims=2, perplexity=50, theta=0.5, rand_seed=-1,
                  verbose=False, initial_dims=None, use_pca=False,
                  max_iter=1000, dens_frac=0.3, final_dens=True)
```
These parameters are described below.

### Example usage in Matlab:

```matlab
datafile = websave('mnist_train.txt', ...
                   'http://densvis.csail.mit.edu/datasets/mnist_subsample.txt'); 
labelfile = websave('mnist_labels.txt', ...
                    'http://densvis.csail.mit.edu/datasets/mnist_subsample_labels.txt'); 

data = textread(datafile);
labels = textread(labelfile);

no_dims = 2; initial_dims = 50; perplexity = 50; theta = .5; alg = 'svd'; max_iter = 1000;
dens_frac = 0.3; dens_lambda = 0.1; final_dens = true;

[embedding, ro, re] = run_densne(data, no_dims, initial_dims, perplexity, theta, alg, max_iter, ...
            	                 dens_frac, dens_lambda, final_dens);

gscatter(embedding(:,1), embedding(:,2), labels); 
```

The parameteres in Matlab are the same as in Python; the additional parameter `alg` determines
which preprocessing transform is done when `initial_dims` is smaller than the dimensionality
of the input data. It can take values "svd" (for a singular
value decomposition, default), "eig" (eigenvalue decomposition"), or "als" (alternating least 
squares); see [Matlab documentation](https://www.mathworks.com/help/stats/pca.html "PCA"). 

### Input arguments

#### Inherited from t-SNE

* `no_dims`: Number of dimensions for the output embedding (int), default 2

* `perplexity`: Perplexity parameter used to select length scale (float), default 50

* `theta`: Used in Barnes-Hut approximation to speed up computation, smaller is more accurate but
slower (float, between 0 and 1), default 0.5

* `randseed`: Optionally set a random seed for reproducibility (int), default -1 (random seed)

* `verbose`: If `True`, displays progress text (bool), default `False`

* `initial_dims`: If `use_pca=True`, this many dimensions of the data will be taken. If `None`, then
this will be the number of dimensions in the input (int or `None`), default `None`

* `max_iter`: Number of iterations to run the gradient descent (int), default 1000 

#### New in den-SNE

* `dens_frac`: Fraction of iterations to incorporate the density-preserving gradient term
(float, between 0 and 1), default 0.3

* `dens_lambda`: Weight to give the density-preserving gradient term. When set to 0, ordinary
BH t-SNE will be run (float), default 0.1

* `final_dens`: If `True`, will return the log local radii of the original data and the embedding in
addition to the embedding (bool), default `True`

### Output arguments

If `final_dens` is True, returns `(embedding, ro, re)`, where:

* `embedding`: a (number of data points)-by-`no_dims` array containing the embedding
coordinates, and

* `ro`: a (number of data points)-lenth array containing the log local
radii of the original dataset

* `re`: a (number of data points)-lenth array containing the log local radii of the embeddding.

If `final_dens` is `False`, returns just `embedding`.

## From the command line

We also provide the file `densne.py` which can be run from the command line: 

```bash
python densne.py -h [--help HELP] -i [--input INPUT] -o [--outname OUTNAME]
                 -d [--no_dims NO_DIMS] -p[--perplexity PERPLEXITY]
                 -t [--theta THETA] -r [--randseed RANDSEED]
                 -n [--initial_dims INITIAL_DIMS] -v [--verbose VERBOSE]
                 [--use_pca/--no_pca USE_PCA] -m [--max_iter MAX_ITER]
                 -f [--dens_frac DENS_FRAC]  -l [--dens_lambda DENS_LAMBDA]
                 [--final_dens/--no_final_dens FINAL_DENS]
```

where within the square braces are the long-form flag and the capitalized text corresponds to
the parameters above, with these clarifications: 

* `--final_dens`                    Output local radii for the final embedding
* `--no_final_dens`                 Do not output local radii for the final embedding
* `--use_pca`			    Perform PCA on the input data
* `--no_pca`			    Do not perform PCA on the input data

As an example,
```
python densne.py -i data.txt -o out -f .3 -p 30
```
and
```
python densne.py --input data.txt --outname out --dens_frac .3 --perplexity 30
```
both run den-SNE on input file `data.txt` to produce output files `out_emb.txt` (containing the 
output embedding) and `out_dens.txt` (containing the local radii),
using `dens_frac=0.3` and `perplexity=30`.
The input file is parsed using numpy's `loadtxt` function; we assume that the first dimension
(row index) iterates over the data instances, and the second dimension (column index) iterates over the features.

The output `out.txt` is a TSV file containing the embeddedings and, if `final_dens` is set, the local radii
of the original space and embedding are also included.

## Example data and script
We have included the file `trial_densne.py` which allows you to run an example straight out of
the box. Having 

Having downloaded the repo, run: 
```bash
python trial_densne.py
```
The code will load the file `trial_data.txt`, which
contains a mixture of six Gaussian point clouds with increasing variance,
and will run both den-SNE and t-SNE on the dataset with default parameters and plot the embeddings
(if you have `matplotlib` installed),
and alignment of the local radius in each case. It will also save the embeddings 
in `{tsne,densne}_trial_emb.txt`, the local radii in `{tsne,densne}_trial_dens.txt`, and the plot in `densne_trial_fig.png`.

The plot will look like: 
<p align="center">
<img src="http://cb.csail.mit.edu/cb/densvis/figs/densne_trial_fig_labels.jpg" width="700">
</p>

## References
Our den-SNE algorithm is described in:

Ashwin Narayan, Bonnie Berger\*, and Hyunghoon Cho\*. "Density-Preserving Data Visualization Unveils Dynamic Patterns of Single-Cell Transcriptomic Variability", *bioRxiv*, 2020.

Original Barnes-Hut t-SNE algorithm is described in:

Laurens Van Der Maaten. "Accelerating t-SNE using Tree-based Algorithms", *Journal of Machine Learning Research*, 15(1), 2014.

## License
This package is licensed under the MIT license.

## Contact for questions
Ashwin Narayan, [ashwinn@mit.edu](mailto:ashwinn@mit.edu)\
Hoon Cho, [hhcho@broadinstitute.org](mailto:hhcho@broadinstitute.org)
