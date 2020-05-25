if(!require("reticulate")) install.packages("reticulate", dependencies = TRUE, INSTALL_opts = '--no-lock')
# if(!require("optparse")) install.packages("optparse", dependencies = TRUE, INSTALL_opts = '--no-lock')

library("reticulate")
# install.packages("optparse")
library("optparse")

# Installs densMAP via pip
if(reticulate::py_module_available('densmap')) { 
    sys <- reticulate::import('sys')
    sbp <- reticulate::import('subprocess')
    sbp$check_call(c(sys$executable, "-m", "pip", "install", 'densmap-learn'))
} 

densMAP <- function(data, n_neighbors, n_epochs, ndim, dens_frac, dens_lambda, final_dens, var_shift, metric, min_dist,verbose) { 
    if(missing(n_neighbors)) { 
        n_neighbors <- 30
    }
    if(missing(n_epochs)) { 
        n_epochs <- 750
    }
    if(missing(ndim)) { 
        ndim <- 2
    }
    if(missing(dens_frac)) { 
        dens_frac <- .3
    }
    if(missing(dens_lambda)) { 
        dens_lambda <- 2.
    }
    if(missing(final_dens)) { 
        final_dens <- TRUE
    }
    if(missing(var_shift)) { 
        var_shift <- .1
    }
    if(missing(metric)) { 
        metric <- "euclidean"
    }
    if(missing(min_dist)) { 
        min_dist <- .1
    }
    if(missing(verbose)) { 
        verbose <- TRUE
    }
            
    dm <- reticulate::import('densmap')
    
    densMAP <- dm$densMAP("n_neighbors"=as.integer(n_neighbors),"n_epochs"=as.integer(n_epochs), 
                          "n_components"=as.integer(ndim), "dens_frac"=dens_frac, "dens_lambda"=dens_lambda, 
                          "final_dens"=final_dens, "var_shift"=var_shift, "metric"=metric,
                          "min_dist"=min_dist, "verbose"=verbose)
    
    mdm.full <- densMAP$fit_transform(data)
        
    return(mdm.full)
}

#dm <- reticulate::import('densmap')

#data <- dm$load_trial$load_trial()
#densMAP <- dm$densMAP("final_dens"=FALSE)

#mdm.full <- densMAP$fit_transform(data)

#mdm.full