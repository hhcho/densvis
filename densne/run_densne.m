function [mappedX, origDens, embDens] = run_densne(X, no_dims, initial_dims, perplexity, theta, alg, max_iter, dens_frac, dens_lambda, final_dens, Y_init)
%RUN_DENSNE Runs the C++ implementation of den-SNE
%
%   mappedX = run_densne(X, no_dims, initial_dims, perplexity, theta, alg, max_iter, dens_frac, dens_lambda, final_dens)
%
%
% Builds upon the C++ implementation of Barnes-Hut-SNE. The high-dimensional 
% datapoints are specified in the NxD matrix X. The dimensionality of the 
% datapoints is reduced to initial_dims dimensions using PCA (default = 50)
% before t-SNE is performed. Next, t-SNE reduces the points to no_dims
% dimensions. The perplexity of the input similarities may be specified
% through the perplexity variable (default = 30). The variable theta sets
% the trade-off parameter between speed and accuracy: theta = 0 corresponds
% to standard, slow t-SNE, while theta = 1 makes very crude approximations.
% Appropriate values for theta are between 0.1 and 0.7 (default = 0.5).
% The variable alg determines the algorithm used for PCA. The default is set 
% to 'svd'. Other options are 'eig' or 'als' (see 'doc pca' for more details).
% The function returns the two-dimensional data points in mappedX.
%
% NOTE: The function is designed to run on large (N > 5000) data sets. It
% may give poor performance on very small data sets (it is better to use a
% standard t-SNE implementation on such data).

% Copyright (c) 2020 Ashwin Narayan and Hyunghoon Cho

% Permission is hereby granted, free of charge, to any person obtaining a copy
% of this software and associated documentation files (the "Software"), to deal
% in the Software without restriction, including without limitation the rights
% to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
% copies of the Software, and to permit persons to whom the Software is
% furnished to do so, subject to the following conditions:

% The above copyright notice and this permission notice shall be included in all
% copies or substantial portions of the Software.

% THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
% IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
% FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
% AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
% LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
% OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
% SOFTWARE.

% This software is modified from the original source code t-SNE implementation
% (https://github.com/lvdmaaten/bhtsne), with the following copyright

% Copyright (c) 2014, Laurens van der Maaten (Delft University of Technology)
% All rights reserved.
% 
% Redistribution and use in source and binary forms, with or without
% modification, are permitted provided that the following conditions are met:
% 1. Redistributions of source code must retain the above copyright
%    notice, this list of conditions and the following disclaimer.
% 2. Redistributions in binary form must reproduce the above copyright
%    notice, this list of conditions and the following disclaimer in the
%    documentation and/or other materials provided with the distribution.
% 3. All advertising materials mentioning features or use of this software
%    must display the following acknowledgement:
%    This product includes software developed by the Delft University of Technology.
% 4. Neither the name of the Delft University of Technology nor the names of 
%    its contributors may be used to endorse or promote products derived from 
%    this software without specific prior written permission.
%
% THIS SOFTWARE IS PROVIDED BY LAURENS VAN DER MAATEN ''AS IS'' AND ANY EXPRESS
% OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES 
% OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO 
% EVENT SHALL LAURENS VAN DER MAATEN BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, 
% SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
% PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR 
% BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
% CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING 
% IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY 
% OF SUCH DAMAGE.


    if ~exist('no_dims', 'var') || isempty(no_dims)
        no_dims = 2;
    end
    if ~exist('initial_dims', 'var') || isempty(initial_dims)
        initial_dims = 50;
    end
    if ~exist('perplexity', 'var') || isempty(perplexity)
        perplexity = 30;
    end
    if ~exist('theta', 'var') || isempty(theta)
        theta = 0.5;
    end
    if ~exist('alg', 'var') || isempty(alg)
        alg = 'svd';
    end
    if ~exist('max_iter', 'var') || isempty(max_iter)
       max_iter = 1000; 
    end
    if ~exist('dens_frac', 'var') || isempty(dens_frac)
       dens_frac = 0.2; 
    end
    if ~exist('dens_lambda', 'var') || isempty(dens_lambda)
       dens_lambda = 0.1; 
    end
    if ~exist('final_dens', 'var') || isempty(final_dens)
       final_dens = false; 
    end
    if ~exist('Y_init', 'var') || isempty(Y_init)
      Y_init = [];
    else
      assert(size(Y_init, 1) == size(X, 1));
      assert(size(Y_init, 2) == no_dims);
    end
    % Perform the initial dimensionality reduction using PCA
    X = double(X);
    if initial_dims < size(X, 2)
        X = bsxfun(@minus, X, mean(X, 1));
        M = pca(X,'NumComponents',initial_dims,'Algorithm',alg);
        X = X * M;
    end
    
    densne_path = which('den_sne');
    densne_path = fileparts(densne_path);
    
    % Compile t-SNE C code
    if(~exist(fullfile(densne_path,'./den_sne'),'file') && isunix)
        system(sprintf('g++ %s %s %s -o %s -O2',...
            fullfile(densne_path,'./sptree.cpp'),...
            fullfile(densne_path,'./densne.cpp'),...
            fullfile(densne_path,'./densne_main.cpp'),...
            fullfile(densne_path,'./den_sne')));
    end

    % Run the fast diffusion SNE implementation
    write_data(X, no_dims, theta, perplexity, max_iter, dens_frac, dens_lambda, final_dens, Y_init);
    tic
    [flag, cmdout] = system(['"' fullfile(densne_path,'./den_sne') '"']);
    if(flag~=0)
        error(cmdout);
    end
    toc
        [mappedX, dens, landmarks, costs] = read_data;   
    if (final_dens ~= 0) 
        origDens = dens(:,1);
        embDens = dens(:,2);
    else
        % [mappedX, landmarks, costs] = read_data; 
        origDens = [];
        embDens = [];
    end
    
    landmarks = landmarks + 1;              % correct for Matlab indexing
    %delete('data.dat');
    %delete('result.dat');
end


% Writes the datafile for the fast t-SNE implementation
function write_data(X, no_dims, theta, perplexity, max_iter, dens_frac, dens_lambda, final_dens, Y_init)
    [n, d] = size(X);
    h = fopen('data.dat', 'wb');
	  fwrite(h, n, 'integer*4');
	  fwrite(h, d, 'integer*4');
    fwrite(h, theta, 'double');
    fwrite(h, perplexity, 'double');
	  fwrite(h, no_dims, 'integer*4');
    fwrite(h, max_iter, 'integer*4');

    % densne
    fwrite(h, dens_frac, 'double');
    fwrite(h, dens_lambda, 'double');
    fwrite(h, char(int32(final_dens)), 'char*1');
    fwrite(h, char(int32(~isempty(Y_init))), 'char*1');

    fwrite(h, X', 'double');
    if ~isempty(Y_init)
      fwrite(h, Y_init', 'double');
    end
	  fclose(h);
end


% Reads the result file from the den-SNE implementation
function [X, dens, landmarks, costs] = read_data
    h = fopen('result.dat', 'rb');
	  n = fread(h, 1, 'integer*4');
	  d = fread(h, 1, 'integer*4');
	  dens_flag = fread(h, 1, 'char*1');
	  X = fread(h, n * d, 'double');
    X = reshape(X, [d n])';
    if dens_flag ~= 0
	    dens = fread(h, n * 2, 'double');
      dens = reshape(dens, [2 n])';
    else
        dens=[];
    end
    landmarks = fread(h, n, 'integer*4');
    costs = fread(h, n, 'double');      % this vector contains only zeros
	  fclose(h);
end
