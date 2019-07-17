import pandas as pd

from algorithm.parameters import params
from stats.stats import stats
from utilities.stats.trackers import cache, runtime_error_cache, unique_ind_tracker
from utilities.stats import trackers


def evaluate_fitness(individuals):
    """
    Evaluate an entire population of individuals. Invalid individuals are given
    a default bad fitness. If params['CACHE'] is specified then individuals
    have their fitness stored in a dictionary called utilities.trackers.cache.
    Dictionary keys are the string of the phenotype.
    There are currently three options for use with the cache:
        1. If params['LOOKUP_FITNESS'] is specified (default case if
           params['CACHE'] is specified), individuals which have already been
           evaluated have their previous fitness read directly from the cache,
           thus saving fitness evaluations.
        2. If params['LOOKUP_BAD_FITNESS'] is specified, individuals which
           have already been evaluated are given a default bad fitness.
        3. If params['MUTATE_DUPLICATES'] is specified, individuals which
           have already been evaluated are mutated to produce new unique
           individuals which have not been encountered yet by the search
           process.

    :param individuals: A population of individuals to be evaluated.
    :return: A population of fully evaluated individuals.
    """

    results, pool = [], None
    
    if params['MULTICORE']:
        pool = params['POOL']

    for name, ind in enumerate(individuals):
        ind.name = name

        # Iterate over all individuals in the population.
        if ind.invalid:
            # Invalid individuals cannot be evaluated and are given a bad
            # default fitness.
            ind.fitness = params['FITNESS_FUNCTION'].default_fitness
            stats['invalids'] += 1

        else:
            eval_ind = True

            # Valid individuals can be evaluated.
            if params['CACHE'] and hash(ind.phenotype) in unique_ind_tracker:
                # The individual has been encountered before in
                # the utilities.trackers.cache.

                if params['LOOKUP_FITNESS'] and ind.phenotype in cache:
                    # Set the fitness as the previous fitness from the
                    # cache.
                    ind.fitness = cache[ind.phenotype]["fitness"]
                    eval_ind = False

                elif params['LOOKUP_BAD_FITNESS']:
                    # Give the individual a bad default fitness.
                    ind.fitness = params['FITNESS_FUNCTION'].default_fitness
                    eval_ind = False

                elif params['MUTATE_DUPLICATES']:
                    # Mutate the individual to produce a new phenotype
                    # which has not been encountered yet.
                    counter = 0
                    orginal = ind
                    while (not ind.phenotype) or hash(ind.phenotype) in unique_ind_tracker:
                        ind = params['MUTATION'](ind)
                        stats['regens'] += 1
                        counter += 1
                        if counter > 1000:
                            ind = orginal
                            break
                    
                    # Need to overwrite the current individual in the pop.
                    individuals[name] = ind
                    ind.name = name

            if eval_ind:
                results = eval_or_append(ind, results, pool)

    if params['MULTICORE']:
        for result in results:
            # Execute all jobs in the pool.
            ind = result.get()

            # Set the fitness of the evaluated individual by placing the
            # evaluated individual back into the population.
            individuals[ind.name] = ind

            ind_dic = {}
            ind_dic["fitness"] = ind.fitness
            ind_dic["phenotype"] = ind.phenotype
            ind_dic["genome"] = ind.genome
            ind_dic["AST"] = ind.AST
            ind_dic["derivation"] = ind.derivation

            # Add the evaluated individual to the cache.
            if trackers.max_cache_size is None or trackers.max_cache_size > len(cache):
                cache[ind.phenotype] = ind_dic
            else:
                cache.popitem(False)
                cache[ind.phenotype] = ind_dic
            trackers.unique_ind_tracker.add(hash(ind.phenotype))

            # Check if individual had a runtime error.
            if ind.runtime_error:
                runtime_error_cache.append(ind.phenotype)
                    
    return individuals


def eval_or_append(ind, results, pool):
    """
    Evaluates an individual if sequential evaluation is being used. If
    multi-core parallel evaluation is being used, adds the individual to the
    pool to be evaluated.

    :param ind: An individual to be evaluated.
    :param results: A list of individuals to be evaluated by the multicore
    pool of workers.
    :param pool: A pool of workers for multicore evaluation.
    :return: The evaluated individual or the list of individuals to be
    evaluated.
    """

    if params['MULTICORE']:
        # Add the individual to the pool of jobs.
        results.append(pool.apply_async(ind.evaluate, ()))
        return results
    
    else:
        # Evaluate the individual.
        ind.evaluate()

        # Check if individual had a runtime error.
        if ind.runtime_error:
            runtime_error_cache.append(ind.phenotype)

        if params['CACHE']:
            # The phenotype string of the individual does not appear
            # in the cache, it must be evaluated and added to the
            # cache.
            ind_dic = {}
            ind_dic["fitness"] = ind.fitness
            ind_dic["phenotype"] = ind.phenotype
            ind_dic["genome"] = ind.genome
            ind_dic["AST"] = ind.AST
            ind_dic["derivation"] = ind.derivation
            ind_dic["output_cases"] = ind.test_cases


            if (isinstance(ind.fitness, list) and not
                    any([pd.isnull(i) for i in ind.fitness])) or \
                    (not isinstance(ind.fitness, list) and not
                     pd.isnull(ind.fitness)):
                
                # All fitnesses are valid.
                if trackers.max_cache_size is None or trackers.max_cache_size > len(cache):
                    cache[ind.phenotype] = ind_dic
                else:
                    cache.popitem(False)
                    cache[ind.phenotype] = ind_dic
                trackers.unique_ind_tracker.add(hash(ind.phenotype))
