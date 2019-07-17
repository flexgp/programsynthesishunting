from algorithm.parameters import params
from fitness.base_ff_classes.base_ff import base_ff
from utilities.stats.trackers import cache
from representation.individual import Individual

import numpy as np
from random import sample
from Levenshtein import distance as ldistance
from Levenshtein import hamming as hdistance


class novelty(base_ff):
    def __init__(self) -> None:
        # Initialise base fitness function class.
        super().__init__()

    def evaluate(self, ind: Individual, **kwargs) -> float:
        # Larger return is larger novelty

        novelty_algorithm = params["NOVELTY_ALGORITHM"]
        if novelty_algorithm.lower() == "basic":
            return self.basic(ind)
        else:
            return self.evaluate_distance(ind, novelty_algorithm.lower())

    def basic(self, ind: Individual) -> int:
        """Just checks if this phenotype has been seen before"""
        if ind.phenotype in cache:
            return 0
        return 10

    def evaluate_distance(
        self, ind: Individual, novelty_alg: str = "levi", max_comparisons: int = 100
    ) -> float:
        """Compare current phenotype with phenotypes from other seen phenotypes:
        scales very poorly without a max number of comparisons, as the cache is constantly
        growing"

        :param ind: An individual to be evaluated
        :param novelty_alg: algorithm to be used
        :param max_comparisons: The upper bound on the number of comparisons to run
        :return: The novelty of the individual, larger number represents larger novelty
        """
        if not np.isnan(ind.novelty):
            return ind.novelty

        size_cache = len(cache)
        # Bound the number of comparisons
        number_comparisons = (
            size_cache if size_cache < max_comparisons else max_comparisons
        )
        total_novelty = 0
        if size_cache > 0:
            choices = sample(cache.keys(), number_comparisons)
            for other_phenotype in choices:
                # If comparing to itself, don't count it
                if other_phenotype == ind.phenotype:
                    number_comparisons -= 1
                    continue

                # Want hamming distance of genotype
                if novelty_alg in ("geno", "genotype"):
                    other_geno = cache[other_phenotype]["genome"]
                    smaller_size = min(len(ind.genome), len(other_geno))
                    this_novelty = 0
                    for index in range(smaller_size):
                        if ind.genome[index] != other_geno[index]:
                            this_novelty += 1
                    total_novelty += this_novelty / smaller_size

                # Compute hamming distance of phenotype
                elif novelty_alg == 'hamming':
                    smaller_size = min(len(ind.phenotype), len(other_phenotype))
                    total_novelty += hdistance(ind.phenotype[:smaller_size], other_phenotype[:smaller_size])

                # Compute the normalized levenshtein distance
                elif novelty_alg in ("levi", "levenshtein", "pheno", "phenotype"):
                    total_novelty += ldistance(ind.phenotype, other_phenotype) / max(len(ind.phenotype), len(other_phenotype))

                # Compute distance of flat AST trees
                elif novelty_alg == "ast":
                    other_ind = cache[other_phenotype]
                    total_novelty += self.compare_tree_dicts(ind.AST, other_ind["AST"])

                # Compute distance of flat derivation trees
                elif novelty_alg == "derivation":
                    other_ind = cache[other_phenotype]
                    total_novelty += self.compare_tree_dicts(ind.derivation, other_ind["derivation"])

                elif novelty_alg == "fitness":
                    other_ind = cache[other_phenotype]
                    total_novelty += abs(ind.fitness - other_ind["fitness"])

                elif novelty_alg == "output":
                    other_ind = cache[other_phenotype]
                    count = 0
                    for tcase_ind in range(len(ind.test_cases)):
                        count += ((ind.test_cases[tcase_ind] + other_ind["output_cases"][tcase_ind]) % 2)
                    total_novelty += count

                else:
                    raise NotImplementedError(novelty_alg + " has not been implemented")
            ind.novelty = total_novelty / number_comparisons
            return ind.novelty
        # If cache is empty, doesn't matter what is returned since every individual will reach this point
        # and thus will all have the same novelty. Also, cache should never be empty.
        return 0

    @staticmethod
    def compare_tree_dicts(tree_dic1: dict, tree_dic2: dict) -> float:
        compareVec1 = []
        compareVec2 = []
        differenceVec1 = []
        differenceVec2 = []
        # O(n)
        for astType in tree_dic1:
            if astType in tree_dic2:
                compareVec1.append(tree_dic1[astType])
                compareVec2.append(tree_dic2[astType])
            else:
                differenceVec1.append(tree_dic1[astType])
        # O(n)
        for astType in tree_dic2:
            if astType not in tree_dic1:
                differenceVec2.append(tree_dic2[astType])

        # Compare similarity of nodes in common
        similarityDifference = np.linalg.norm(np.array(compareVec1) - np.array(compareVec2))

        # Compute a value for the nodes not in common for each
        extraDiffAst1 = np.linalg.norm(differenceVec1)
        extraDiffAst2 = np.linalg.norm(differenceVec2)

        return similarityDifference + max(extraDiffAst1, extraDiffAst2)


