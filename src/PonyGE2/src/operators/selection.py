from random import sample, shuffle, random
from algorithm.parameters import params
from utilities.algorithm.NSGA2 import compute_pareto_metrics, \
    crowded_comparison_operator
from stats.stats import stats

from fitness.novelty import novelty
from representation.individual import Individual
from typing import List
from utilities.stats.trackers import novelty_fitness_archive, bandit_tracker


def selection(population):
    """
    Perform selection on a population in order to select a population of
    individuals for variation.

    :param population: input population
    :return: selected population
    """

    # Use novelty selection on a per generation basis
    if params["NOVELTY_BY_GEN"]:
        # Exponential Decay based on generation
        if params["NOVELTY_SELECTION_ALG"].lower() == "exp":
            gen = stats['gen']
            novelty_parameter = 1 / (2 ** (gen / round(params["GENERATIONS"] / 10)))

        # Adaptive based on diversity in population
        elif params["NOVELTY_SELECTION_ALG"].lower() == "adapt":
            pheno_set = set()
            count = 0
            for ind in population:
                pheno_set.add(ind.phenotype)
                count += 1
            novelty_parameter = 1 - (len(pheno_set) / count)

        # Knobelty
        else:
            novelty_parameter = params["NOVELTY_FACTOR"]

        if novelty_parameter > random():
            return novelty_tournament(population)

        return params['SELECTION'](population)

    else:
        return params['SELECTION'](population)



def novelty_tournament(population) -> List[Individual]:
    """
    Given an entire population, draw <tournament_size> competitors randomly and
    return the best based on how novel their phenotype is. Unless INVALID_SELECTION
    is true, only valid individuals can be selected for tournaments.

    :param population: A population from which to select individuals.
    :return: A population of the winners from tournaments.
    """

    # Initialise list of tournament winners.
    winners = []

    # Initialize novelty fitness evaluator
    novelty_eval = novelty()

    # The flag "INVALID_SELECTION" allows for selection of invalid individuals.
    if params['INVALID_SELECTION']:
        available = population
    else:
        available = [i for i in population if not i.invalid]

    while len(winners) < params['GENERATION_SIZE']:
        # Randomly choose TOURNAMENT_SIZE competitors from the given
        # population. Allows for re-sampling of individuals.
        competitors = sample(available, params['TOURNAMENT_SIZE'])

        best_competitor = None
        best_novelty = None
        for competitor in competitors:
            # Calculate the novelty of each competitor
            comp_novelty = novelty_eval(competitor)

            # If first time
            if best_novelty is None:
                best_competitor = competitor
                best_novelty = comp_novelty

            # Want to maximize novelty
            if comp_novelty > best_novelty:
                best_competitor = competitor
                best_novelty = comp_novelty

        # Return the single best competitor.
        winners.append(best_competitor)

    # Return the population of novelty tournament winners.
    return winners


def tournament(population) -> List[Individual]:
    """
    Given an entire population, draw <tournament_size> competitors randomly and
    return the best. Unless INVALID_SELECTION is true, only valid individuals
    can be selected for tournaments.

    :param population: A population from which to select individuals.
    :return: A population of the winners from tournaments.
    """

    # Initialise list of tournament winners.
    winners = []

    # The flag "INVALID_SELECTION" allows for selection of invalid individuals.
    if params['INVALID_SELECTION']:
        available = population
    else:
        available = [i for i in population if not i.invalid]

    while len(winners) < params['GENERATION_SIZE']:
        # Randomly choose TOURNAMENT_SIZE competitors from the given
        # population. Allows for re-sampling of individuals.
        competitors = sample(available, params['TOURNAMENT_SIZE'])

        # Return the single best competitor.
        winners.append(max(competitors))

    # Return the population of tournament winners.
    return winners


def lexicase(population) -> List[Individual]:
    """
    Given an entire population, choose the individuals that do the best on
    randomly chosen test cases. Allows for selection of 'specialist' individuals
    that do very well on some test cases even if they do poorly on others.

    :param population: A population from which to select individuals.
    :return: A population of the selected individuals from lexicase selection -- allows
             repeated individuals
    """
    # Initialise list of lexicase selections
    winners = []

    # Max or min
    maximise_fitness = params['FITNESS_FUNCTION'].maximise

    # The flag "INVALID_SELECTION" allows for selection of invalid individuals.
    if params['INVALID_SELECTION']:
        available = population
    else:
        available = [i for i in population if not i.invalid]

    # Basic ensure individuals have been tested on same number of test cases, and that there is at least one test case
    assert (len(available[0].test_case_results) == len(available[1].test_case_results))
    assert (len(available[0].test_case_results) > 0)

    while len(winners) < params['GENERATION_SIZE']:
        # Random ordering of test cases
        random_test_case_list = list(range(len(available[0].test_case_results)))
        shuffle(random_test_case_list)

        # Only choose from a sample not from the entire available population

        if params['LEXICASE_TOURNAMENT']:
            candidates = sample(available, params['TOURNAMENT_SIZE'])
        else:
            candidates = available
        candidate_size = len(candidates)
        while candidate_size > 0:
            # Calculate best score for chosen test case from candidates
            scores = []
            for ind in candidates:
                scores.append(ind.test_case_results[random_test_case_list[0]])
            if maximise_fitness:
                best_score = max(scores)
            else:
                best_score = min(scores)

            # Only retain individuals who have the best score for the test case
            remaining = []
            candidate_size = 0
            for ind in candidates:
                if ind.test_case_results[random_test_case_list[0]] == best_score:
                    remaining.append(ind)
                    candidate_size += 1
            candidates = remaining

            # If only one individual remains, choose that individual
            if len(candidates) == 1:
                winners.append(candidates[0])
                break
                
            # If this was the last test case, randomly choose an individual from remaining candidates
            elif len(random_test_case_list) == 1:
                # Penalize longer solutions
                min_nodes = params["MAX_TREE_NODES"] + 1
                best_ind = None
                for ind in candidates:
                    if ind.nodes < min_nodes:
                        best_ind = ind
                        min_nodes = ind.nodes
                winners.append(best_ind)

                # Choose randomly among solutions
                # winners.append(sample(candidates, 1)[0])
                break

            # Go to next test case and loop
            else:
                random_test_case_list.pop(0)

    # Return the population of lexicase selections.
    return winners

def fitness_novelty(population):
    import numpy as np
    import heapq

    number_of_nearest_neighbors = 15

    # The flag "INVALID_SELECTION" allows for selection of invalid individuals.
    if params['INVALID_SELECTION']:
        available = population
    else:
        available = [i for i in population if not i.invalid]
    # Use current population as well as novelty archive
    available.extend(novelty_fitness_archive)
    heap = []
    heapq.heapify(heap)
    novelty_list = []

    for eval_ind in available:
        for compare_ind in available:
            if compare_ind == eval_ind:
                continue
            distance = np.linalg.norm(np.asarray(eval_ind.test_case_results) - np.asarray(compare_ind.test_case_results))
            # If less then nearest neighbors in heap, add negative distance (because we want max heap)
            if len(list(heap)) <= number_of_nearest_neighbors:
                heapq.heappush(heap, -distance)
            # Otherwise, only add it in if the max in the heap is bigger than the new distance
            elif heap[0] < -distance:
                heapq.heapreplace(heap, -distance)

        # Calc novelty for each individual
        eval_ind.novelty = abs(sum(list(heap))) / len(list(heap))

        # Keep track of all novelties for archive
        novelty_list.append(eval_ind.novelty)
        heap = []
        heapq.heapify(heap)

    # Set archive threshold
    threshold_index = round(len(available) * .8)
    threshold = sorted(novelty_list)[threshold_index]


    # Add to archive
    for ind in available:
        if ind.novelty > threshold:
            novelty_fitness_archive.add(ind)

    # Do selection based on novelty, novelty will not be recalculated since its stored in the individual
    return novelty_tournament(population)


def lexicase_and_novelty(population):
    # Initialise list of lexicase selections
    winners = []

    # Max or min
    maximise_fitness = params['FITNESS_FUNCTION'].maximise

    # The flag "INVALID_SELECTION" allows for selection of invalid individuals.
    if params['INVALID_SELECTION']:
        available = population
    else:
        available = [i for i in population if not i.invalid]

    novelty_eval = novelty()
    novelty_selection_alg = params["NOVELTY_SELECTION_ALG"].lower()

    # Ensure individuals have been tested on same number of test cases, and that there is at least one test case
    assert (len(available[0].test_case_results) == len(available[1].test_case_results))
    assert (len(available[0].test_case_results) > 0)

    # Exponential Decay based on generation
    if novelty_selection_alg == "exp":
        gen = stats['gen']
        novelty_parameter = 1 / (2 ** (gen / round(params["GENERATIONS"] / 10)))

    # Adaptive based on diversity in population
    elif novelty_selection_alg == "adapt":
        pheno_set = set()
        count = 0
        for ind in population:
            pheno_set.add(ind.phenotype)
            count += 1
        novelty_parameter = 1 - (len(pheno_set) / count)

    elif novelty_selection_alg == "bandit":
        # Will set per individual in for loop
        novelty_parameter = 0

    elif novelty_selection_alg == "reverse_exp":
        current_gen = stats['gen']
        total_gens = params["GENERATIONS"]
        novelty_parameter = 1 / (2 ** ((total_gens - current_gen) / round(total_gens / 10)))

    elif novelty_selection_alg == "gauss":
        current_gen = stats['gen']
        total_gens = params["GENERATIONS"]
        exp_constant = 10
        split = total_gens / 2
        if current_gen <= split:
            novelty_parameter = 1 / (2 ** ((split - current_gen) / round(total_gens / exp_constant)))
        else:
            novelty_parameter = 1 / (2 ** ((current_gen - round(split)) / round(total_gens / exp_constant)))

    # Knobelty
    else:
        novelty_parameter = params["NOVELTY_FACTOR"]

    while len(winners) < params['GENERATION_SIZE']:

        if novelty_selection_alg == "bandit":
            epsilon = 0.2
            rand = random()
            if rand < epsilon or bandit_tracker["avg_fit_from_nov"] == bandit_tracker["avg_fit_from_fit"]:
                if rand < (epsilon / 2):
                    novelty_parameter = 1
                else:
                    novelty_parameter = 0
            else:
                if bandit_tracker["avg_fit_from_nov"] < bandit_tracker["avg_fit_from_fit"]:
                    novelty_parameter = 1 if not maximise_fitness else 0
                else:
                    novelty_parameter = 0 if not maximise_fitness else 1

        # Do novelty selection
        if novelty_parameter > random():
            # Randomly choose TOURNAMENT_SIZE competitors from the given
            # population. Allows for re-sampling of individuals.
            competitors = sample(available, params['TOURNAMENT_SIZE'])

            best_competitor = None
            best_novelty = None
            for competitor in competitors:
                # Calculate the novelty of each competitor
                comp_novelty = novelty_eval(competitor)

                # If first time
                if best_novelty is None:
                    best_competitor = competitor
                    best_novelty = comp_novelty

                # Want to maximize novelty
                if comp_novelty > best_novelty:
                    best_competitor = competitor
                    best_novelty = comp_novelty

            # Return the single best competitor.
            winners.append(best_competitor)
            if novelty_selection_alg == "bandit":
                update_bandit_tracker(best_competitor.fitness)

        # Do lexicase selection
        else:
            # Random ordering of test cases
            random_test_case_list = list(range(len(available[0].test_case_results)))
            shuffle(random_test_case_list)
            # Only choose from a sample not from the entire available population
            if params['LEXICASE_TOURNAMENT']:
                candidates = sample(available, params['TOURNAMENT_SIZE'])
            else:
                candidates = available
            candidate_size = len(candidates)
            while candidate_size > 0:
                # Calculate best score for chosen test case from candidates
                scores = []
                for ind in candidates:
                    scores.append(ind.test_case_results[random_test_case_list[0]])
                if maximise_fitness:
                    best_score = max(scores)
                else:
                    best_score = min(scores)

                # Only retain individuals who have the best score for the test case
                remaining = []
                candidate_size = 0
                for ind in candidates:
                    indScore = ind.test_case_results[random_test_case_list[0]]
                    if indScore == best_score:
                        remaining.append(ind)
                        candidate_size += 1
                candidates = remaining

                # If only one individual remains, choose that individual
                if len(candidates) == 1:
                    winner = candidates[0]
                    winners.append(winner)
                    if novelty_selection_alg == "bandit":
                        update_bandit_tracker(winner.fitness)
                    break

                # If this was the last test case, randomly choose an individual from remaining candidates
                elif len(random_test_case_list) == 1:
                    # Penalize longer solutions
                    min_nodes = params["MAX_TREE_NODES"] * 10
                    best_ind = None
                    for ind in candidates:
                        if ind.nodes < min_nodes:
                            best_ind = ind
                            min_nodes = ind.nodes
                    winners.append(best_ind)

                    # Choose randomly among solutions
                    # winner = sample(candidates, 1)[0]
                    # winners.append(winner)
                    # if novelty_selection_alg == "bandit":
                    #     update_bandit_tracker(winner.fitness)
                    break

                # Go to next test case and loop
                else:
                    random_test_case_list.pop(0)
    # Return the selections.
    return winners


def update_bandit_tracker(ind_fitness):
    bandit_tracker["avg_fit_from_nov"] = ((bandit_tracker["avg_fit_from_nov"] * bandit_tracker["num_nov"]) +
                                          ind_fitness) / (bandit_tracker["num_nov"] + 1)
    bandit_tracker["num_nov"] += 1


def truncation(population) -> List[Individual]:
    """
    Given an entire population, return the best <proportion> of them.

    :param population: A population from which to select individuals.
    :return: The best <proportion> of the given population.
    """

    # Sort the original population.
    population.sort(reverse=True)

    # Find the cutoff point for truncation.
    cutoff = int(len(population) * float(params['SELECTION_PROPORTION']))

    # Return the best <proportion> of the given population.
    return population[:cutoff]


def nsga2_selection(population) -> List[Individual]:
    """Apply NSGA-II selection operator on the *population*. Usually, the
    size of *population* will be larger than *k* because any individual
    present in *population* will appear in the returned list at most once.
    Having the size of *population* equals to *k* will have no effect other
    than sorting the population according to their front rank. The
    list returned contains references to the input *population*. For more
    details on the NSGA-II operator see [Deb2002]_.
    
    :param population: A population from which to select individuals.
    :returns: A list of selected individuals.
    .. [Deb2002] Deb, Pratab, Agarwal, and Meyarivan, "A fast elitist
       non-dominated sorting genetic algorithm for multi-objective
       optimization: NSGA-II", 2002.
    """

    selection_size = params['GENERATION_SIZE']
    tournament_size = params['TOURNAMENT_SIZE']

    # Initialise list of tournament winners.
    winners = []

    # The flag "INVALID_SELECTION" allows for selection of invalid individuals.
    if params['INVALID_SELECTION']:
        available = population
    else:
        available = [i for i in population if not i.invalid]

    # Compute pareto front metrics.
    pareto = compute_pareto_metrics(available)

    while len(winners) < selection_size:
        # Return the single best competitor.
        winners.append(pareto_tournament(available, pareto, tournament_size))

    return winners


def pareto_tournament(population, pareto, tournament_size) -> List[Individual]:
    """
    The Pareto tournament selection uses both the pareto front of the
    individual and the crowding distance.

    :param population: A population from which to select individuals.
    :param pareto: The pareto front information.
    :param tournament_size: The size of the tournament.
    :return: The selected individuals.
    """
    
    # Initialise no best solution.
    best = None
    
    # Randomly sample *tournament_size* participants.
    participants = sample(population, tournament_size)
    
    for participant in participants:
        if best is None or crowded_comparison_operator(participant, best,
                                                       pareto):
            best = participant
    
    return best


# Set attributes for all operators to define multi-objective operators.
nsga2_selection.multi_objective = True
