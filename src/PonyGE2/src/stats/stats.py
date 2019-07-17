from copy import copy
from sys import stdout
from time import time
import numpy as np

from algorithm.parameters import params
from utilities.algorithm.NSGA2 import compute_pareto_metrics
from utilities.algorithm.state import create_state
from utilities.stats import trackers
from utilities.stats.save_plots import save_plot_from_data, \
    save_pareto_fitness_plot
from utilities.stats.file_io import save_stats_to_file, save_stats_headers, \
    save_best_ind_to_file, save_first_front_to_file
from fitness.novelty import novelty

import datetime

"""Algorithm statistics"""
stats = {
        "gen": 0,
        "total_inds": 0,
        "regens": 0,
        "invalids": 0,
        "runtime_error": 0,
        "unique_inds": len(trackers.unique_ind_tracker),
        "unused_search": 0,
        "ave_genome_length": 0,
        "max_genome_length": 0,
        "min_genome_length": 0,
        "ave_used_codons": 0,
        "max_used_codons": 0,
        "min_used_codons": 0,
        "ave_tree_depth": 0,
        "max_tree_depth": 0,
        "min_tree_depth": 0,
        "ave_tree_nodes": 0,
        "max_tree_nodes": 0,
        "min_tree_nodes": 0,
        "ave_fitness": 0,
        "best_fitness": 0,
        "best_test_fitness": 0,
        "time_taken": 0,
        "total_time": 0,
        "time_adjust": 0,
        "novelty_output": 0,
        "novelty_genotype": 0,
        "novelty_phenotype": 0,
        "novelty_ast": 0,
        "novelty_derivation": 0,
        "nov_output_total": 0,
        "nov_genotype_total": 0,
        "nov_phenotype_total": 0,
        "nov_ast_total": 0,
        "nov_derivation_total": 0

}


def get_stats(individuals, end=False):
    """
    Generate the statistics for an evolutionary run. Save statistics to
    utilities.trackers.stats_list. Print statistics. Save fitness plot
    information.

    :param individuals: A population of individuals for which to generate
    statistics.
    :param end: Boolean flag for indicating the end of an evolutionary run.
    :return: Nothing.
    """

    if hasattr(params['FITNESS_FUNCTION'], 'multi_objective'):
        # Multiple objective optimisation is being used.

        # Remove fitness stats from the stats dictionary.
        stats.pop('best_fitness', None)
        stats.pop('ave_fitness', None)

        # Update stats.
        get_moo_stats(individuals, end)

    else:
        # Single objective optimisation is being used.
        get_soo_stats(individuals, end)

    if params['SAVE_STATE'] and not params['DEBUG'] and \
                            stats['gen'] % params['SAVE_STATE_STEP'] == 0:
        # Save the state of the current evolutionary run.
        create_state(individuals)


def get_soo_stats(individuals, end):
    """
    Generate the statistics for an evolutionary run with a single objective.
    Save statistics to utilities.trackers.stats_list. Print statistics. Save
    fitness plot information.

    :param individuals: A population of individuals for which to generate
    statistics.
    :param end: Boolean flag for indicating the end of an evolutionary run.
    :return: Nothing.
    """

    # Get best individual.
    best_ind = individuals[0]
    for ind in individuals:
        if ind.fitness < best_ind.fitness:
            best_ind = ind
        if ind.fitness == best_ind.fitness:
            if ind.nodes < best_ind.nodes:
                best_ind = ind

    if not trackers.best_ever or best_ind > trackers.best_ever:
        # Save best individual in trackers.best_ever.
        trackers.best_ever = best_ind
    if best_ind.fitness == trackers.best_ever.fitness and best_ind.nodes < trackers.best_ever.nodes:
        trackers.best_ever = best_ind

    if end or params['VERBOSE'] or not params['DEBUG']:
        # Update all stats.
        update_stats(individuals, end)

    # Save fitness plot information
    if params['SAVE_PLOTS'] and not params['DEBUG']:
        if not end:
            trackers.best_fitness_list.append(trackers.best_ever.fitness)

        if params['VERBOSE'] or end:
            save_plot_from_data(trackers.best_fitness_list, "best_fitness")

    # Print statistics
    if params['VERBOSE'] and not end:
        print_generation_stats()

    elif not params['SILENT']:
        # Print simple display output.
        perc = stats['gen'] / (params['GENERATIONS']+1) * 100
        stdout.write("Evolution: %d%% complete\r" % perc)
        stdout.flush()


    # Generate test fitness on regression problems
    if hasattr(params['FITNESS_FUNCTION'], "training_test") and end:

        # Save training fitness.
        trackers.best_ever.training_fitness = copy(trackers.best_ever.fitness)

        # Evaluate test fitness.
        trackers.best_ever.test_fitness = params['FITNESS_FUNCTION'](
            trackers.best_ever, dist='test')
        stats["best_test_fitness"] = trackers.best_ever.test_fitness

        # Save to final stats so stored in stats.tsv
        final_stats = trackers.stats_list[-1]
        final_stats["best_test_fitness"] = trackers.best_ever.test_fitness

        # Set main fitness as training fitness.
        trackers.best_ever.fitness = trackers.best_ever.training_fitness

    # Save stats to list.
    if params['VERBOSE'] or (not params['DEBUG'] and not end):
        trackers.stats_list.append(copy(stats))

    # Save stats to file.
    if not params['DEBUG']:

        if stats['gen'] == 0:
            save_stats_headers(stats)

        save_stats_to_file(stats, end)

        if params['SAVE_ALL']:
            save_best_ind_to_file(stats, trackers.best_ever, end, stats['gen'])

        elif params['VERBOSE'] or end:
            save_best_ind_to_file(stats, trackers.best_ever, end)

    if end and not params['SILENT']:
        print_final_stats()


def get_moo_stats(individuals, end):
    """
    Generate the statistics for an evolutionary run with multiple objectives.
    Save statistics to utilities.trackers.stats_list. Print statistics. Save
    fitness plot information.

    :param individuals: A population of individuals for which to generate
    statistics.
    :param end: Boolean flag for indicating the end of an evolutionary run.
    :return: Nothing.
    """

    # Compute the pareto front metrics for the population.
    pareto = compute_pareto_metrics(individuals)

    # Save first front in trackers. Sort arbitrarily along first objective.
    trackers.best_ever = sorted(pareto.fronts[0], key=lambda x: x.fitness[0])

    # Store stats about pareto fronts.
    stats['pareto_fronts'] = len(pareto.fronts)
    stats['first_front'] = len(pareto.fronts[0])

    if end or params['VERBOSE'] or not params['DEBUG']:
        # Update all stats.
        update_stats(individuals, end)

    # Save fitness plot information
    if params['SAVE_PLOTS'] and not params['DEBUG']:

        # Initialise empty array for fitnesses for all inds on first pareto
        # front.
        all_arr = [[] for _ in range(params['FITNESS_FUNCTION'].num_obj)]

        # Generate array of fitness values.
        fitness_array = [ind.fitness for ind in trackers.best_ever]

        # Add paired fitnesses to array for graphing.
        for fit in fitness_array:
            for o in range(params['FITNESS_FUNCTION'].num_obj):
                all_arr[o].append(fit[o])

        if not end:
            trackers.first_pareto_list.append(all_arr)

            # Append empty array to best fitness list.
            trackers.best_fitness_list.append([])

            # Get best fitness for each objective.
            for o, ff in \
                    enumerate(params['FITNESS_FUNCTION'].fitness_functions):

                # Get sorted list of all fitness values for objective "o"
                fits = sorted(all_arr[o], reverse=ff.maximise)

                # Append best fitness to trackers list.
                trackers.best_fitness_list[-1].append(fits[0])

        if params['VERBOSE'] or end:

            # Plot best fitness for each objective.
            for o, ff in \
                    enumerate(params['FITNESS_FUNCTION'].fitness_functions):
                to_plot = [i[o] for i in trackers.best_fitness_list]

                # Plot fitness data for objective o.
                plotname = ff.__class__.__name__ + str(o)

                save_plot_from_data(to_plot, plotname)

            # TODO: PonyGE2 can currently only plot moo problems with 2 objectives.
            # Check that the number of fitness objectives is not greater than 2
            if params['FITNESS_FUNCTION'].num_obj > 2:
                s = "stats.stats.get_moo_stats\n" \
                    "Warning: Plotting of more than 2 simultaneous " \
                    "objectives is not yet enabled in PonyGE2."
                print(s)

            else:
                save_pareto_fitness_plot()

    # Print statistics
    if params['VERBOSE'] and not end:
        print_generation_stats()
        print_first_front_stats()

    elif not params['SILENT']:
        # Print simple display output.
        perc = stats['gen'] / (params['GENERATIONS'] + 1) * 100
        stdout.write("Evolution: %d%% complete\r" % perc)
        stdout.flush()

    # Generate test fitness on regression problems
    if hasattr(params['FITNESS_FUNCTION'], "training_test") and end:

        for ind in trackers.best_ever:
            # Iterate over all individuals in the first front.

            # Save training fitness.
            ind.training_fitness = copy(ind.fitness)

            # Evaluate test fitness.
            ind.test_fitness = params['FITNESS_FUNCTION'](ind, dist='test')

            # Set main fitness as training fitness.
            ind.fitness = ind.training_fitness

    # Save stats to list.
    if params['VERBOSE'] or (not params['DEBUG'] and not end):
        trackers.stats_list.append(copy(stats))

    # Save stats to file.
    if not params['DEBUG']:

        if stats['gen'] == 0:
            save_stats_headers(stats)

        save_stats_to_file(stats, end)

        if params['SAVE_ALL']:
            save_first_front_to_file(stats, end, stats['gen'])

        elif params['VERBOSE'] or end:
            save_first_front_to_file(stats, end)

    if end and not params['SILENT']:
        print_final_moo_stats()


def update_stats(individuals, end):
    """
    Update all stats in the stats dictionary.

    :param individuals: A population of individuals.
    :param end: Boolean flag for indicating the end of an evolutionary run.
    :return: Nothing.
    """

    if not end:
        # Time Stats
        trackers.time_list.append(time() - stats['time_adjust'])
        stats['time_taken'] = trackers.time_list[-1] - \
                              trackers.time_list[-2]
        stats['total_time'] = trackers.time_list[-1] - \
                              trackers.time_list[0]

    # Population Stats
    stats['total_inds'] = params['POPULATION_SIZE'] * (stats['gen'] + 1)
    stats['runtime_error'] = len(trackers.runtime_error_cache)
    if params['CACHE']:
        stats['unique_inds'] = len(trackers.unique_ind_tracker)
        stats['unused_search'] = 100 - stats['unique_inds'] / \
                                       stats['total_inds'] * 100

    # Genome Stats
    genome_lengths = [len(i.genome) for i in individuals]
    stats['max_genome_length'] = np.nanmax(genome_lengths)
    stats['ave_genome_length'] = np.nanmean(genome_lengths)
    stats['min_genome_length'] = np.nanmin(genome_lengths)

    # Used Codon Stats
    codons = [i.used_codons for i in individuals]
    stats['max_used_codons'] = np.nanmax(codons)
    stats['ave_used_codons'] = np.nanmean(codons)
    stats['min_used_codons'] = np.nanmin(codons)

    # Tree Depth Stats
    depths = [i.depth for i in individuals]
    stats['max_tree_depth'] = np.nanmax(depths)
    stats['ave_tree_depth'] = np.nanmean(depths)
    stats['min_tree_depth'] = np.nanmin(depths)

    # Tree Node Stats
    nodes = [i.nodes for i in individuals]
    stats['max_tree_nodes'] = np.nanmax(nodes)
    stats['ave_tree_nodes'] = np.nanmean(nodes)
    stats['min_tree_nodes'] = np.nanmin(nodes)

    # Not using this for current research, don't need to waste time calculating
    # Novelty Stats
    # n = novelty()
    # total_geno = 0
    # total_levi = 0
    # total_ast = 0
    # total_deriv = 0
    # total_output = 0
    # ind_size = len(individuals)
    # for ind in individuals:
    #     ind.novelty = np.NaN
    #     total_output += n.evaluate_distance(ind, "output")
    #     ind.novelty = np.NaN
    #     total_geno += n.evaluate_distance(ind, "genotype")
    #     ind.novelty = np.NaN
    #     total_levi += n.evaluate_distance(ind, "levi")
    #     ind.novelty = np.NaN
    #     total_ast += n.evaluate_distance(ind, "ast")
    #     ind.novelty = np.NaN
    #     total_deriv += n.evaluate_distance(ind, "derivation")
    #     ind.novelty = np.NaN
    #
    # stats["novelty_output"] = total_output / ind_size
    # stats["novelty_genotype"] = total_geno / ind_size
    # stats["novelty_phenotype"] = total_levi / ind_size
    # stats["novelty_ast"] = total_ast / ind_size
    # stats["novelty_derivation"] = total_deriv / ind_size

    # import datetime
    # start = datetime.datetime.now()
    if params["NOVELTY"]:
        if end:
            import random
            from representation.individual import Individual
            # Total Novelty Stats
            n = novelty()
            total_output = 0
            total_geno = 0
            total_levi = 0
            total_ast = 0
            total_deriv = 0
            cache_size = len(trackers.cache)
            individual_dics = list(trackers.cache.values())
            sample_size = min(max(1000, cache_size // 10), 10000)
            sample_size = min(cache_size, sample_size)
            ind_sample = random.sample(individual_dics, sample_size)
            derivation_novelties = []
            output_novelties = []
            for ind_dic in ind_sample:
                ind = Individual(ind_dic["genome"], None, False)
                ind.fitness = ind_dic["fitness"]
                ind.phenotype = ind_dic["phenotype"]
                ind.AST = ind_dic["AST"]
                ind.derivation = ind_dic["derivation"]
                ind.test_cases = ind_dic["output_cases"]

                ind.novelty = np.NaN
                out_distance = n.evaluate_distance(ind, "output")
                output_novelties.append(out_distance)
                total_output += out_distance
                ind.novelty = np.NaN
                total_geno += n.evaluate_distance(ind, "genotype")
                ind.novelty = np.NaN
                total_levi += n.evaluate_distance(ind, "levi")
                ind.novelty = np.NaN
                total_ast += n.evaluate_distance(ind, "ast")
                ind.novelty = np.NaN
                der_distance = n.evaluate_distance(ind, "derivation")
                derivation_novelties.append(der_distance)
                total_deriv += der_distance
                ind.novelty = np.NaN

            stats["nov_output_total"] = total_output / sample_size
            stats["nov_genotype_total"] = total_geno / sample_size
            stats["nov_phenotype_total"] = total_levi / sample_size
            stats["nov_ast_total"] = total_ast / sample_size
            stats["nov_derivation_total"] = total_deriv / sample_size

            # Change the last generation stats in the stats list too
            final_stats = trackers.stats_list[-1]
            final_stats["nov_output_total"] = total_output / sample_size
            final_stats["nov_genotype_total"] = total_geno / sample_size
            final_stats["nov_phenotype_total"] = total_levi / sample_size
            final_stats["nov_ast_total"] = total_ast / sample_size
            final_stats["nov_derivation_total"] = total_deriv / sample_size
    # print("Novelty calculation time: " + str(datetime.datetime.now() - start))

    if not hasattr(params['FITNESS_FUNCTION'], 'multi_objective'):
        # Fitness Stats
        fitnesses = [i.fitness for i in individuals]
        stats['ave_fitness'] = np.nanmean(fitnesses, axis=0)
        stats['best_fitness'] = trackers.best_ever.fitness


def print_generation_stats():
    """
    Print the statistics for the generation and individuals.

    :return: Nothing.
    """

    print("______\n")
    for stat in sorted(stats.keys()):
        print(" ", stat, ": \t", stats[stat])
    print("\n")


def print_first_front_stats():
    """
    Stats printing for the first pareto front for multi-objective optimisation.

    :return: Nothing.
    """

    print("  first front fitnesses :")
    for ind in trackers.best_ever:
        print("\t  ", ind.fitness)


def print_final_stats():
    """
    Prints a final review of the overall evolutionary process.

    :return: Nothing.
    """

    if hasattr(params['FITNESS_FUNCTION'], "training_test"):
        print("\n\nBest:\n  Training fitness:\t",
              trackers.best_ever.training_fitness)
        print("  Test fitness:\t\t", trackers.best_ever.test_fitness)
    else:
        print("\n\nBest:\n  Fitness:\t", trackers.best_ever.fitness)

    print("  Phenotype:", trackers.best_ever.phenotype)
    print("  Genome:", trackers.best_ever.genome)
    print_generation_stats()


def print_final_moo_stats():
    """
    Prints a final review of the overall evolutionary process for
    multi-objective problems.

    :return: Nothing.
    """

    print("\n\nFirst Front:")
    for ind in trackers.best_ever:
        print(" ", ind)
    print_generation_stats()
