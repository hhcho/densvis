import numpy as np
from densne import run_densne

try:
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm 
    mpl = True
except:
    mpl = False

data = np.loadtxt('trial_data.txt')
print(data.shape)

# denSNE run
print('Running denSNE')
emb, ro, re = run_densne(data, perplexity=50, verbose=True, initial_dims=data.shape[1],
                         dens_frac=0.3, use_pca=False, max_iter=1000, dens_lambda=0.2,
                         final_dens=True)

dens = np.stack((ro,re)).transpose()

# tSNE run
print('Running tSNE')


t_emb, t_ro, t_re = run_densne(data, perplexity=50, verbose=True, initial_dims=data.shape[1],
                               dens_frac=0, use_pca=False, max_iter=1000, dens_lambda=0,
                               final_dens=True)

t_dens = np.stack((t_ro,t_re)).transpose()

# Saving
print('-- Saving denSNE --')
print('Embedding: densne_trial_emb.txt')
print('Densities: densne_trial_dens.txt')
np.savetxt('densne_trial_emb.txt', emb)
np.savetxt('densne_trial_dens.txt', dens)


print('-- Saving tSNE --')
print('Embedding: tsne_trial_emb.txt')
print('Densities: tsne_trial_dens.txt')
np.savetxt('tsne_trial_emb.txt', t_emb)
np.savetxt('tsne_trial_dens.txt', t_dens)


# Plotting (if Matplotlib installed)
if mpl: 
    print('Plotting')
    K=6
    N=data.shape[0]
    color_int = np.array([i // (N/K) for i in range(data.shape[0])], dtype=int)
    cmap = cm.viridis(np.linspace(0,1, K))
    colors=[cmap[i] for i in color_int[::-1]]


    fig, ax = plt.subplots(2,2,figsize=[10,10])

    ax[0,0].scatter(emb[:,0], emb[:,1], c=colors, s=2, alpha=.4)
    ax[0,1].scatter(dens[:,0], dens[:,1], c=colors, s=2, alpha=.4)
    
    ax[1,0].scatter(t_emb[:,0], t_emb[:,1], c=colors, s=2, alpha=.4)
    ax[1,1].scatter(t_dens[:,0], t_dens[:,1], c=colors, s=2, alpha=.4)


    ax[0,0].set_ylabel('denSNE_y')
    ax[1,0].set_ylabel('tSNE_y')

    ax[0,0].set_xlabel('denSNE_x')
    ax[1,0].set_xlabel('tSNE_x')


    ax[0,0].set_title('Embedding (den-SNE)')
    ax[1,0].set_title('Embedding (t-SNE)')
    ax[0,1].set_title('Density Preservation (den-SNE)')
    ax[1,1].set_title('Density Preservation (t-SNE)')

    ax[1,1].set_xlabel('Original Local Radius (log)')
    ax[0,1].set_xlabel('Original Local Radius (log)')
    
    ax[0,1].set_ylabel('Embedding Local Radius (log)')
    ax[1,1].set_ylabel('Embedding Local Radius (log)')

    ax[0,0].set_xticklabels('')
    ax[0,0].set_xticks([])
    ax[0,0].set_yticklabels('')
    ax[0,0].set_yticks([])
    
    ax[1,0].set_xticklabels('')
    ax[1,0].set_xticks([])
    ax[1,0].set_yticklabels('')
    ax[1,0].set_yticks([])
    
    fig.savefig('densne_trial_fig.png', bbox_inches='tight')

    plt.show()

