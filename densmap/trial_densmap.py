import numpy as np
import densmap
from densmap.load_trial import load_trial

try:
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    mpl = True
except:
    mpl = False

data = load_trial()

print(data.shape)
# densMAP run
print('Running densMAP')
emb, ro, re = densmap.densMAP(verbose=True, n_components=2,
                              n_neighbors=30, n_epochs=750,
                              dens_frac=0.3, dens_lambda=2.,
                              logdist_shift=0, var_shift=.1).fit_transform(data)

dens = np.stack((ro,re)).transpose()

# UMAP run
print('Running UMAP')
u_emb, u_ro, u_re = densmap.densMAP(verbose=True, n_components=2,
                                    n_neighbors=30, n_epochs=750,
                                    dens_frac=0., var_shift=.1, dens_lambda=0.).fit_transform(data)


u_dens = np.stack((u_ro,u_re)).transpose()

# Saving
print('-- Saving densMAP --')
print('Embedding: densmap_trial_emb.txt')
print('Densities: densmap_trial_dens.txt')
np.savetxt('densmap_trial_emb.txt', emb)
np.savetxt('densmap_trial_dens.txt', dens)


print('-- Saving UMAP --')
print('Embedding: umap_trial_emb.txt')
print('Densities: umap_trial_dens.txt')
np.savetxt('umap_trial_emb.txt', u_emb)
np.savetxt('umap_trial_dens.txt', u_dens)


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
    ax[0,1].scatter(ro, re, c=colors, s=2, alpha=.4)
    
    ax[1,0].scatter(u_emb[:,0], u_emb[:,1], c=colors, s=2, alpha=.4)
    ax[1,1].scatter(u_ro, u_re, c=colors, s=2, alpha=.4)

    ax[0,0].set_ylabel('densMAP_y')
    ax[1,0].set_ylabel('UMAP_y')

    ax[0,0].set_xlabel('densMAP_x')
    ax[1,0].set_xlabel('UMAP_x')


    ax[0,0].set_title('Embedding (densMAP)')
    ax[1,0].set_title('Embedding (UMAP)')
    ax[0,1].set_title('Density Preservation (densMAP)')
    ax[1,1].set_title('Density Preservation (UMAP)')

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
    
    fig.savefig('densmap_trial_fig.png', bbox_inches='tight')
    plt.show()

