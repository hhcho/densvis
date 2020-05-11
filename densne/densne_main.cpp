#include <cfloat>
#include <cmath>
#include <cstdlib>
#include <cstdio>
#include <cstring>
#include <ctime>
#include "densne.h"

// Function that runs the Barnes-Hut implementation of t-SNE
int main() {

  // Define some variables
  int origN, N, D, no_dims, max_iter;
  double perplexity, theta, *data, *Y_init;
  int rand_seed = -1;

  double dens_frac, dens_lambda;
  bool final_dens;

  // Read the parameters and the dataset
  if(DENSNE::load_data(&data, &origN, &D, &no_dims, &theta, &perplexity, &rand_seed,
        &max_iter, &dens_frac, &dens_lambda, &final_dens, &Y_init)) {

    // Make dummy landmarks
    N = origN;
    int* landmarks = (int*) malloc(N * sizeof(int));
    if(landmarks == NULL) { printf("Memory allocation failed!\n"); exit(1); }
    for(int n = 0; n < N; n++) landmarks[n] = n;

    // Now fire up the SNE implementation
    double* Y;
    bool skip_rand_init;
    if (Y_init == NULL) {
      Y = (double*) malloc(N * no_dims * sizeof(double));
      skip_rand_init = false;
    } else {
      Y = Y_init;
      Y_init = NULL;
      skip_rand_init = true;
    }

    double* dens = NULL;
    if (final_dens) {
      dens = (double*) malloc(N * 2 * sizeof(double));
    }

    double* costs = (double*) calloc(N, sizeof(double));
    if(Y == NULL || costs == NULL) { printf("Memory allocation failed!\n"); exit(1); }
    if(final_dens && dens == NULL) { printf("Memory allocation failed!\n"); exit(1); }

    DENSNE::run(data, N, D, Y, dens, no_dims, perplexity, theta, rand_seed, skip_rand_init,
        max_iter, 250, 250, dens_frac, dens_lambda, final_dens);

    // Save the results
    DENSNE::save_data(Y, dens, landmarks, costs, N, no_dims);

    // Clean up the memory
    free(data); data = NULL;
    free(Y); Y = NULL;
    free(costs); costs = NULL;
    free(landmarks); landmarks = NULL;
    if (dens != NULL) {
      free(dens); Y = NULL;
    }
  }
}
