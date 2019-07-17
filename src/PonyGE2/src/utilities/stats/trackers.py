"""Utilities for tracking progress of runs, including time taken per
generation, fitness plots, fitness caches, etc."""
import collections

cache = collections.OrderedDict()
# This dict stores the cache for an evolutionary run. The key for each entry
# is the phenotype of the individual, the value is the individual.

max_cache_size = None
# A cap on the size of the cache based on available memory and size of Individual
# Calculated in algorithm.search_loop

unique_ind_tracker = set()
# Stores the hash of all seen phenotypes, used to determine the number of unique
# individuals that have been seen

novelty_fitness_archive = set()
# Novelty-fitness archive

bandit_tracker = {"avg_fit_from_nov": 0, "num_nov": 0, "avg_fit_from_fit": 0, "num_fit": 0}
# Tracker used in multi arm bandit adaptive novelty

runtime_error_cache = []
# This list stores a list of phenotypes which produce runtime errors over an
# evolutionary run.

best_fitness_list = []
# fitness_plot is simply a list of the best fitnesses at each generation.
# Useful for plotting evolutionary progress.

first_pareto_list = []
# first_pareto_list stores the list of all individuals stored on the first
# pareto front during multi objective optimisation.

time_list = []
# time_list stores the system time after each generation has been completed.
# Useful for keeping track of how long each generation takes.

stats_list = []
# List for storing stats at each generation
# Used when verbose mode is off to speed up program

best_ever = None
# Store the best ever individual here.
