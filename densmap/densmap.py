import sys
import numpy as np
import argparse
import pickle

import densmap
from sklearn.datasets import load_digits

def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-i','--input', help='Input .txt or .pkl', default='data.txt')
    parser.add_argument('-o','--outname', help='Output prefix for saving _emb.txt, _dens.txt',
                        default='out')
    parser.add_argument('-f','--dens_frac', type=float, default=0.3)
    parser.add_argument('-l','--dens_lambda', type=float, default=2.0)
    parser.add_argument('-s','--var_shift', type=float, default=0.1)
    parser.add_argument('-d','--ndim', type=int, default=2, help='Embedding dimension (default: %(default)s)')
    parser.add_argument('-n','--n-epochs', type=int, help='Number of epochs', default=750)
    parser.add_argument('-k','--n-nei', type=int, default=30, help='Number of neighbors (default: %(default)s)')
    parser.add_argument('--final_dens', action='store_true', default=True)
    parser.add_argument('--no_final_dens', dest='final_dens', action='store_false')
    parser.add_argument('--outtype', choices=('pkl','txt'), default='txt', help='Output format type (default: %(default)s)')
    return parser

def main(args):
    if args.input.endswith('.txt'):
        data = np.loadtxt(args.input)
    elif args.input.endswith('.pkl'):
        data = pickle.load(open(args.input,'rb'))
    else:
        raise RuntimeError(f'File format for {args.input} not supported')

    if data.shape[0] < data.shape[1]:
        data = data.T
    
    emb = densmap.densMAP(verbose=True,
                          n_components=args.ndim,
                          n_neighbors=args.n_nei,
                          n_epochs=args.n_epochs,
                          dens_frac=args.dens_frac,
                          dens_lambda=args.dens_lambda,
                          logdist_shift=0,
                          var_shift=args.var_shift,
                          final_dens=args.final_dens).fit_transform(data)

    outname = args.outname
    if args.final_dens:
        (emb, ro, re) = emb
        rero = np.stack((ro,re)).transpose()

        if args.outtype=='txt':
            np.savetxt(outname+'_dens.txt',rero, fmt='%e')
        elif args.outtype=='pkl':
            with open(outname + '_dens.pkl','wb') as f:
                pickle.dump(rero, f)
        else:
            raise RuntimeError
        
    if args.outtype == 'txt':
        np.savetxt(outname+'_emb.txt',emb, fmt='%e')

    elif args.outtype == 'pkl':
        with open(outname + '_emb.pkl','wb') as f:
            pickle.dump(emb, f)
    else: # should not reach here
        raise RuntimeError 

    print("Done")

if __name__ == '__main__':
    main(parse_args().parse_args())
