# Try saving to actual dir rather than workdir

init_densne <- function(data, workdir, no_dims, initial_dims, perplexity, theta,
                        randseed, verbose, max_iter, dens_frac, dens_lambda,
                        final_dens) {

    # print(final_dens)
    write_binary_file(data, paste(workdir,"data.dat",sep="/"), theta, perplexity,
                      no_dims, max_iter, dens_frac, dens_lambda, final_dens, randseed)
}

densne <- function(workdir, verbose) {
    basedir = getwd()
    exec_path = paste(basedir, 'den_sne', sep='/')
    
    setwd(workdir)
    system(exec_path, intern=verbose, ignore.stdout=TRUE)
    setwd(basedir)
    
    outfile <- paste(workdir, "result.dat", sep='/')
    
    # Read out the results
    connection = file(outfile,"rb")
    # Dimensions
    dims <- readBin(connection, integer(), n=2)
    
    # Final Dens Flag
    fdf <- readBin(connection, character(), n=1)
    
    # Read out the results
    total_coords <- dims[[1]]*dims[[2]]
    emb_vec <- readBin(connection, double(), n=total_coords)
    
    embedding <- matrix(data=emb_vec, nrow=dims[[1]], ncol=2, byrow=TRUE)
    
    if(!final_dens) { 
        return(embedding)
    }
    
    dens_vec <- readBin(connection, double(), n=2)
    
    dens <- matrix(data=emb_vec, nrow=dims[[1]], ncol=2, byrow=TRUE)
    
    ro <- dens(,1)
    re <- dens(,2)
    
    output <- list(embedding, ro, re)
    
    return(output)
}

run_densne <- function(data, no_dims, initial_dims, perplexity, theta, randseed, 
                       verbose, max_iter, dens_frac, dens_lambda, final_dens) {     
    if(missing(no_dims)) { 
        no_dims <- 2
    }
    if(missing(perplexity)) { 
        perplexity <- 50
    }
    if(missing(theta)) { 
        theta <- .5
    }
    if(missing(randseed)) { 
        randseed <- -1
    }
    if(missing(verbose)) { 
        verbose <- TRUE
    }
    if(missing(initial_dims)) { 
        initial_dims <- dim(data)[[2]]
    }
    if(missing(max_iter)) { 
        max_iter <- 1000
    }
    if(missing(dens_frac)) { 
        dens_frac <- .3
    }
    if(missing(dens_lambda)) { 
        dens_lambda <- .1
    }
    if(missing(final_dens)) { 
        final_dens <- TRUE
    }

    workdir <- paste(getwd(), 'tmp', sep='/')
    # workdir <- tempdir()
    
    init_densne(data, workdir, no_dims, initial_dims, perplexity, theta, randseed, verbose, max_iter, 
                dens_frac, dens_lambda, final_dens)
    
    output <- densne(workdir, verbose)
    return(output)
}

# Add arguments here
write_binary_file <- function(matrix, path.to.bin.file, theta, perplexity,
                              no_dims, max_iter, dens_frac, dens_lambda, 
                              final_dens, randseed) {
    connection = file(path.to.bin.file,"wb")
    rownames(matrix)=NULL;colnames(matrix)=NULL
    writeBin(as.integer(dim(matrix)),connection)
    writeBin(as.double(c(theta, perplexity)), connection, size=8)
    writeBin(as.integer(c(no_dims, max_iter)), connection)
    writeBin(as.double(c(dens_frac, dens_lambda)), connection, size=8)
    writeBin(as.character(c(final_dens, FALSE)), connection)
    
    
    for(i in 1:nrow(matrix)){
        writeBin(as.double(matrix[i,]),connection)
    }
    if(randseed != -1) { 
        writeBin(as.integer(randseed), connection)
    }
    
    close(connection)
}