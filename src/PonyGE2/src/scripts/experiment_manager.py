""" This program cues up and executes multiple runs of PYGE. Results of runs
    are parsed and placed in a spreadsheet for easy visual analysis.

    Copyright (c) 2014 Michael Fenton
    Hereby licensed under the GNU GPL v3."""
from sys import path
path.append("../src")

from utilities.algorithm.general import check_python_version

check_python_version()

from multiprocessing import Pool
from subprocess import call
import sys
from os import path, getcwd


from algorithm.parameters import params, set_params
from scripts.stats_parser import parse_stats_from_runs


def execute_run(seed):
    """
    Initialise all aspects of a run.

    :return: Nothing.
    """

    exec_str = "python3 ponyge.py " \
               "--random_seed " + str(seed) + " " + " ".join(sys.argv[1:])

    call(exec_str, shell=True)


def execute_runs():
    """
    Execute multiple runs in series using multiple cores.

    :return: Nothing.
    """

    # Initialise empty list of results.
    results = []

    # Initialise pool of workers.
    pool = Pool(processes=max(1, params['CORES'] - 1))

    for run in range(params['RUNS']):
        # Execute a single evolutionary run.
        results.append(pool.apply_async(execute_run, (run,)))

    for result in results:
        result.get()

    # Close pool once runs are finished.
    pool.close()


def check_params():
    """
    Checks the params to ensure an experiment name has been specified and
    that the number of runs has been specified.

    :return: Nothing.
    """

    if not params['EXPERIMENT_NAME']:
        s = "scripts.run_experiments.check_params\n" \
            "Error: Experiment Name not specified.\n" \
            "       Please specify a name for this set of runs."
        raise Exception(s)

    if params['RUNS'] == 1:
        print("Warning: Only 1 run has been specified for this set of runs.")
        print("         The number of runs can be specified with the command-"
              "line parameter `--runs`.")


def testing():
    """
    A test function for running the experiment manager. Calls all functions.

    :return: Nothing.
    """

    # Quick scrip to run multiple consecutive experiments
    for x in range(10):
        path_1 = path.join(getcwd(), "..", "parameters/progsys.txt")
        new_string = ""
        with open(path_1, 'r') as readf:
            for line in readf:
                if "NOVELTY_FACTOR" in line:
                    line = "NOVELTY_FACTOR:         " + str(x) + "\n"
                elif "EXPERIMENT_NAME" in line:
                    line = "EXPERIMENT_NAME:        NoveltySearchLevi" + str(x) + "\n"
                new_string += line

        with open(path_1, "w") as writef:
            writef.write(new_string)

        # Setup run parameters.
        set_params(sys.argv[1:], create_files=False)

        # Check the correct parameters are set for this set of runs.
        check_params()

        # Execute multiple runs.
        execute_runs()

        # Save spreadsheets and all plots for all runs in the 'EXPERIMENT_NAME'
        # folder.
        parse_stats_from_runs(params['EXPERIMENT_NAME'])


def main():
    """
    The main function for running the experiment manager. Calls all functions.

    :return: Nothing.
    """

    # Setup run parameters.
    set_params(sys.argv[1:], create_files=False)

    # Check the correct parameters are set for this set of runs.
    check_params()

    # Execute multiple runs.
    execute_runs()

    # Save spreadsheets and all plots for all runs in the 'EXPERIMENT_NAME'
    # folder.
    parse_stats_from_runs(params['EXPERIMENT_NAME'])

if __name__ == "__main__":
    main()
    # testing()
