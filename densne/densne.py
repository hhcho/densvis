#!/usr/bin/env python

'''
A simple Python wrapper for the den_sne binary that makes it easier to use it
for TSV files in a pipeline without any shell script trickery.

Note: The script does some minimal sanity checking of the input, but don't
    expect it to cover all cases. After all, it is a just a wrapper.

Example:

    > echo -e '1.0\t0.0\n0.0\t1.0' | ./densne.py -d 2 -p 0.1
    -2458.83181442  -6525.87718385
    2458.83181442   6525.87718385

The output will not be normalised, maybe the below one-liner is of interest?:

    python -c 'import numpy;  from sys import stdin, stdout;
        d = numpy.loadtxt(stdin); d -= d.min(axis=0); d /= d.max(axis=0);
        numpy.savetxt(stdout, d, fmt="%.8f", delimiter="\t")'

Authors:     Ashwin Narayan      <github ashwinn226>
             Hyunghoon Cho       <github: hhcho>
Version:    2020
'''

# Copyright (c) 2020 Ashwin Narayan and Hyunghoon Cho

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# This is modified from the source code provided by the origin BH t-SNE implementation
# (https://github.com/lvdmaaten/bhtsne), with the following copyright

# Copyright (c) 2013, Pontus Stenetorp <pontus stenetorp se>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

from argparse import ArgumentParser, FileType
from os.path import abspath, dirname, isfile, join as path_join
from shutil import rmtree
from struct import calcsize, pack, unpack
from subprocess import Popen
from sys import stderr, stdin, stdout
from tempfile import mkdtemp
from platform import system
from os import devnull
import numpy as np
import os, sys
import io

### Constants
IS_WINDOWS = True if system() == 'Windows' else False
DEN_SNE_BIN_PATH = path_join(dirname(__file__), 'windows', 'den_sne.exe') if IS_WINDOWS else path_join(dirname(__file__), 'den_sne')
assert isfile(DEN_SNE_BIN_PATH), ('Unable to find the den_sne binary in the '
    'same directory as this script, have you forgotten to compile it?: {}'
    ).format(DEN_SNE_BIN_PATH)
# Default hyper-parameter values
# den_sne parameters
DEFAULT_DENS_LAMBDA = 0.1
DEFAULT_DENS_FRAC = 0.3
DEFAULT_FINAL_DENS = True

# bh_tsne parameters (from van der Maaten (2014))
# https://lvdmaaten.github.io/publications/papers/JMLR_2014.pdf (Experimental Setup, page 13)
DEFAULT_NO_DIMS = 2
INITIAL_DIMENSIONS = 50
DEFAULT_PERPLEXITY = 50
DEFAULT_THETA = 0.5
EMPTY_SEED = -1
DEFAULT_USE_PCA = True
DEFAULT_MAX_ITERATIONS = 1000

###

def _argparse():
    argparse = ArgumentParser('den_sne Python wrapper')
    argparse.add_argument('-d', '--no_dims', type=int,
                          default=DEFAULT_NO_DIMS)
    argparse.add_argument('-p', '--perplexity', type=float,
            default=DEFAULT_PERPLEXITY)
    # 0.0 for theta is equivalent to vanilla t-SNE
    argparse.add_argument('-t', '--theta', type=float, default=DEFAULT_THETA)
    argparse.add_argument('-r', '--randseed', type=int, default=EMPTY_SEED)
    argparse.add_argument('-n', '--initial_dims', type=int, default=INITIAL_DIMENSIONS)
    argparse.add_argument('-v', '--verbose', action='store_true')
    argparse.add_argument('-i', '--input', type=FileType('r'), default=stdin)
    # argparse.add_argument('-o', '--output', type=FileType('w'),
    #         default=stdout)
    argparse.add_argument('-o', '--outname', help='Output prefix for saving _emb.txt, _dens.txt',
                          default='out')
    argparse.add_argument('--use_pca', action='store_true')
    argparse.add_argument('--no_pca', dest='use_pca', action='store_false')
    argparse.set_defaults(use_pca=DEFAULT_USE_PCA)
    argparse.add_argument('-m', '--max_iter', type=int, default=DEFAULT_MAX_ITERATIONS)

    # den_sne specific
    argparse.add_argument('-f', '--dens_frac', type=float, default=DEFAULT_DENS_FRAC)
    argparse.add_argument('-l', '--dens_lambda', type=float, default=DEFAULT_DENS_LAMBDA)
    argparse.add_argument('--final_dens', action='store_true')
    argparse.add_argument('--no_final_dens', dest='final_dens', action='store_false')
    argparse.add_argument('-y', '--initial_emb', type=FileType('r'), default=None)
    return argparse


def _read_unpack(fmt, fh):
    return unpack(fmt, fh.read(calcsize(fmt)))


def _is_filelike_object(f):
    try:
        return isinstance(f, (file, io.IOBase))
    except NameError:
        # 'file' is not a class in python3
        return isinstance(f, io.IOBase)


def init_den_sne(samples, workdir, no_dims=DEFAULT_NO_DIMS, initial_dims=INITIAL_DIMENSIONS, perplexity=DEFAULT_PERPLEXITY,
        theta=DEFAULT_THETA, randseed=EMPTY_SEED, verbose=False, use_pca=DEFAULT_USE_PCA, max_iter=DEFAULT_MAX_ITERATIONS,
        dens_frac=DEFAULT_DENS_FRAC, dens_lambda=DEFAULT_DENS_LAMBDA, final_dens=DEFAULT_FINAL_DENS, initial_emb=None):

    if initial_dims is None:
        initial_dims = samples.shape[1]
    if use_pca:
        samples = samples - np.mean(samples, axis=0)
        cov_x = np.dot(np.transpose(samples), samples)
        [eig_val, eig_vec] = np.linalg.eig(cov_x)

        # sorting the eigen-values in the descending order
        eig_vec = eig_vec[:, eig_val.argsort()[::-1]]

        if initial_dims > len(eig_vec):
            initial_dims = len(eig_vec)

        # truncating the eigen-vectors matrix to keep the most important vectors
        eig_vec = np.real(eig_vec[:, :initial_dims])
        samples = np.dot(samples, eig_vec)

    # Assume that the dimensionality of the first sample is representative for
    #   the whole batch
    sample_dim = len(samples[0])
    sample_count = len(samples)

    # Note: The binary format used by den_sne is roughly the same as for
    #   vanilla tsne
    with open(path_join(workdir, 'data.dat'), 'wb') as data_file:
        # Write the header
        data_file.write(pack('iiddiidd??', sample_count, sample_dim, theta, perplexity, no_dims, max_iter,
                                          dens_frac, dens_lambda, final_dens, initial_emb is not None))
        # Then write the data
        for sample in samples:
            data_file.write(pack('{}d'.format(len(sample)), *sample))

        if initial_emb is not None:
            for sample in initial_emb:
                data_file.write(pack('{}d'.format(len(sample)), *sample))

        # Write random seed if specified
        if randseed != EMPTY_SEED:
            data_file.write(pack('i', randseed))

def load_data(input_file):
    # Read the data, using numpy's good judgement
    return np.loadtxt(input_file)

def den_sne(workdir, verbose=False):

    # Call den_sne and let it do its thing
    with open(devnull, 'w') as dev_null:
        den_sne_p = Popen((abspath(DEN_SNE_BIN_PATH), ), cwd=workdir,
                # bh_tsne is very noisy on stdout, tell it to use stderr
                #   if it is to print any output
                stdout=stderr if verbose else dev_null)
        den_sne_p.wait()
        assert not den_sne_p.returncode, ('ERROR: Call to den_sne exited '
                'with a non-zero return code exit status, please ' +
                ('enable verbose mode and ' if not verbose else '') +
                'refer to the den_sne output for further details')

    # Read and pass on the results
    with open(path_join(workdir, 'result.dat'), 'rb') as output_file:
        # The first two integers are just the number of samples and the
        #   dimensionality
        result_samples, result_dims, final_dens = _read_unpack('ii?', output_file)
        # Collect the results, but they may be out of order
        results = [_read_unpack('{}d'.format(result_dims), output_file)
            for _ in range(result_samples)]

        # Read original and embedding densities
        if final_dens:
            results = [(_read_unpack('{}d'.format(2), output_file), e)
                       for e in results]
        # Now collect the landmark data so that we can return the data in
        #   the order it arrived
        results = [(_read_unpack('i', output_file), e) for e in results]
        # Put the results in order and yield it
        results.sort()
        for _, result in results:
            yield result
        # The last piece of data is the cost for each sample, we ignore it
        #read_unpack('{}d'.format(sample_count), output_file)

def run_densne(data, no_dims=2, perplexity=50, theta=0.5, randseed=-1, verbose=False, initial_dims=None, use_pca=True, max_iter=1000, dens_frac=0.3, dens_lambda=0.1, final_dens=True, initial_emb=None):
    '''
    Run denSNE based on the Barnes-Hut t-SNE algorithm

    Parameters:
    ----------
    data: file or numpy.array
        The data used to run denSNE, one sample per row
    no_dims: int
    perplexity: int
    randseed: int
    theta: float
    initial_dims: int
    verbose: boolean
    use_pca: boolean
    max_iter: int
    dens_frac: float
    dens_lambda: float
    final_dens: boolean
    '''

    # den_sne works with fixed input and output paths, give it a temporary
    #   directory to work in so we don't clutter the filesystem
    tmp_dir_path = mkdtemp()

    # Load data in forked process to free memory for actual den_sne calculation
    child_pid = os.fork()
    if child_pid == 0:
        if _is_filelike_object(data):
            data = load_data(data)

        if initial_emb is not None and _is_filelike_object(initial_emb):
            initial_emb = load_data(initial_emb)
        
        init_den_sne(data, tmp_dir_path, no_dims=no_dims, perplexity=perplexity, theta=theta, randseed=randseed,verbose=verbose, initial_dims=initial_dims, use_pca=use_pca, max_iter=max_iter, dens_frac=dens_frac, dens_lambda=dens_lambda, final_dens=final_dens, initial_emb=initial_emb)
        os._exit(0)
    else:
        try:
            os.waitpid(child_pid, 0)
        except KeyboardInterrupt:
            print("Please run this program directly from python and not from ipython or jupyter.")
            print("This is an issue due to asynchronous error handling.")

        res = []
        # dens_res = []
        ro = []
        re = []
        for result in den_sne(tmp_dir_path, verbose):
            if final_dens:
                sample_dens_res = []
                # sample_ro = []
                # sample_re = []
                for r in result[0]:
                    sample_dens_res.append(r)
                    # sample_ro.append(r[0])
                    # sample_re.append(r[1])
                # dens_res.append(sample_dens_res)
                ro.append(sample_dens_res[0])
                re.append(sample_dens_res[1])
                result = result[1]

            sample_res = []
            for r in result:
                sample_res.append(r)
            res.append(sample_res)

        rmtree(tmp_dir_path)
        if final_dens:
            # return (np.asarray(res, dtype='float64'), np.asarray(dens_res, dtype='float64'))
            return (np.asarray(res, dtype='float64'), np.asarray(ro, dtype='float64'), 
                    np.asarray(re, dtype='float64'))
        else:
            return np.asarray(res, dtype='float64')


def main(args):
    parser = _argparse()

    if len(args) <= 1:
        print(parser.print_help())
        return 

    argp = parser.parse_args(args[1:])
    
    header = "\t".join(["dim{}".format(ind+1) for ind in range(argp.no_dims)])
    # if argp.final_dens:
    # header += "\torig_dens\temb_dens"
    # argp.output.write(header + "\n")

    result = run_densne(argp.input, no_dims=argp.no_dims, perplexity=argp.perplexity, theta=argp.theta, randseed=argp.randseed,
            verbose=argp.verbose, initial_dims=argp.initial_dims, use_pca=argp.use_pca, max_iter=argp.max_iter,
            dens_frac=argp.dens_frac, dens_lambda=argp.dens_lambda, final_dens=argp.final_dens, initial_emb=argp.initial_emb)

    emb_file = argp.outname + '_emb.txt'

    if argp.final_dens:
        ro = result[1]
        re = result[2]

        dens = np.stack((ro, re)).transpose()
        dens_file = argp.outname + '_dens.txt'
        np.savetxt(dens_file, dens, fmt='%e')

        result = result[0]

    np.savetxt(emb_file, result, fmt='%e')
    
    # if argp.final_dens:
    #     # result = np.concatenate(result, axis=1)
    #     result = result[0]
        
    # for res in result:
    #     fmt = ''
    #     for i in range(1, len(res)):
    #         fmt = fmt + '{}\t'
    #     fmt = fmt + '{}\n'
    #     argp.output.write(fmt.format(*res))

if __name__ == '__main__':
    from sys import argv
    exit(main(argv))
