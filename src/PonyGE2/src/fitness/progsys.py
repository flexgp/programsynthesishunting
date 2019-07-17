from algorithm.parameters import params
from fitness.base_ff_classes.base_ff import base_ff

from os import path
import subprocess
import json
import sys
import ast
import timeout_decorator

TIMEOUT = 1


class progsys(base_ff):
    """Fitness function for program synthesis problems. Grammars and datasets
    for 29 benchmark problems from doi.org/10.1145/2739480.2754769 are
    provided. Evaluation is done in a separate python process."""

    # constants required for formatting the code correctly
    INSERTCODE = "<insertCodeHere>"

    INDENTSPACE = "  "
    LOOPBREAK = "loopBreak"
    LOOPBREAKUNNUMBERED = "loopBreak%"
    LOOPBREAK_INITIALISE = "loopBreak% = 0"
    LOOPBREAK_IF = "if loopBreak% >"
    LOOPBREAK_INCREMENT = "loopBreak% += 1"
    FORCOUNTER = "forCounter"
    FORCOUNTERUNNUMBERED = "forCounter%"

    def __init__(self):
        # Initialise base fitness function class.
        super().__init__()
        self.training_test = True
        
        self.training, self.test, self.embed_header, self.embed_footer = \
            self.get_data(params['DATASET_TRAIN'], params['DATASET_TEST'],
                          params['GRAMMAR_FILE'])
        self.len_training = len(eval(self.training.split("\n")[0].split("inval = ")[1]))
        # self.eval = self.create_eval_process()
        if params['MULTICORE']:
            print("Warming: Multicore is not supported with progsys "
                  "as fitness function.\n"
                  "Fitness function only allows sequential evaluation.")

    def evaluate(self, ind, **kwargs):

        dist = kwargs.get('dist', 'training')
        if not dist == "training":
            global TIMEOUT
            TIMEOUT = 100

        program = self.format_program(ind.phenotype,
                                      self.embed_header, self.embed_footer)
        data = self.training if dist == "training" else self.test
        program = "{}\n{}\n".format(data, program)
        # timeout = 1 if dist == "training" else 5
        # eval_json = json.dumps({'script': program, 'timeout': timeout,
        #                         'variables': ['cases', 'caseQuality',
        #                                       'quality']})
        # self.eval.stdin.write((eval_json+'\n').encode())
        # self.eval.stdin.flush()
        # result_json = self.eval.stdout.readline()
        #
        # result = json.loads(result_json.decode())
        try:
            result = self.run_program(program)
        except TimeoutError:
            result = {"Timeout": "Error"}

        # if 'exception' in result and 'JSONDecodeError' in result['exception']:
        #     self.eval.stdin.close()
        #     self.eval = self.create_eval_process()

        fitness_multiplier = 1
        if params['FITNESS_CODE_EVAL']:
            fitness_multiplier = self.evaluate_code(ind.phenotype)

        # params['SELECTION'] is the actual function
        if ("lexicase" in str(params['SELECTION']) or "fitness_novelty" in str(params['SELECTION'])) and dist != "test":
            if 'caseQuality' not in result:
                # inval = eval(data.split("\n")[0].split("inval = ")[1])
                result['caseQuality'] = [sys.maxsize] * self.len_training
                result["cases"] = [True] * self.len_training
            elif len(result["caseQuality"]) != self.len_training:
                if len(result['caseQuality']) > self.len_training:
                    result['caseQuality'] = result['caseQuality'][:self.len_training]
                else:
                    result['caseQuality'] = result['caseQuality'].extend([sys.maxsize] * (self.len_training - len(result['caseQuality'])))

            ind.test_case_results = [x * fitness_multiplier for x in result['caseQuality']]
            ind.test_cases = result["cases"]

        # Set AST tree of individual
        ind.AST = self.create_flat_AST(self.format_individual(ind.phenotype))

        if 'quality' not in result:
            # with open("ErrorLog.txt", "a+") as elog:
            #     elog.write(str(result))
            #     elog.write(str(program))
            result['quality'] = sys.maxsize

        result['quality'] = min(sys.maxsize, result['quality'])

        return result['quality'] * fitness_multiplier

    @timeout_decorator.timeout(TIMEOUT, timeout_exception=TimeoutError)
    def run_program(self, program):
        result = {'stop': False}
        exec(program, result)
        return result

    @staticmethod
    def create_flat_AST(program: str) -> dict:
        tree_dic = {}
        tree = ast.parse(program)
        for x in ast.walk(tree):
            if str(type(x)) not in tree_dic.keys():
                tree_dic[str(type(x))] = 1
            else:
                tree_dic[str(type(x))] += 1

        return tree_dic

    @staticmethod
    def create_eval_process():
        """create separate python process for evaluation"""
        return subprocess.Popen(['python',
                                 'scripts/python_script_evaluation.py'],
                                stdout=subprocess.PIPE,
                                stdin=subprocess.PIPE)

    def format_program(self, individual, header, footer):
        """formats the program by formatting the individual and adding
        a header and footer"""
        last_new_line = header.rindex('\n')
        indent = header[last_new_line + len('\n'):len(header)]
        return header + self.format_individual(individual, indent) + footer

    def format_individual(self, code, additional_indent=""):
        """format individual by adding appropriate indentation and loop break
        statements"""
        parts = code.split('\n')
        indent = 0
        string_builder = ""
        for_counter_number = 0
        first = True
        for part in parts:
            line = part.strip()
            # remove indentation if bracket is at the beginning of the line
            while line.startswith(":}"):
                indent -= 1
                line = line[2:].strip()

            # add indent
            if not first:
                string_builder += additional_indent
            else:
                first = False

            for i in range(0, indent):
                string_builder += self.INDENTSPACE

            # add indentation
            while line.endswith("{:"):
                indent += 1
                line = line[:len(line) - 2].strip()
            # remove indentation if bracket is at the end of the line
            while line.endswith(":}"):
                indent -= 1
                line = line[:len(line) - 2].strip()

            if self.LOOPBREAKUNNUMBERED in line:
                if self.LOOPBREAK_INITIALISE in line:
                    line = ""  # remove line

                elif self.LOOPBREAK_IF in line:
                    line = line.replace(self.LOOPBREAKUNNUMBERED,
                                        self.LOOPBREAK)
                elif self.LOOPBREAK_INCREMENT in line:
                    line = line.replace(self.LOOPBREAKUNNUMBERED,
                                        self.LOOPBREAK)
                else:
                    raise Exception("Python 'while break' is malformed.")
            elif self.FORCOUNTERUNNUMBERED in line:
                line = line.replace(self.FORCOUNTERUNNUMBERED,
                                    self.FORCOUNTER + str(for_counter_number))
                for_counter_number += 1

            # add line to code
            string_builder += line
            string_builder += '\n'

        return string_builder

    def get_data(self, train, test, grammar):
        """ Return the training and test data for the current experiment.
        A new get_data method is required to load from a sub folder and to
        read the embed file"""
        train_set = path.join("..", "datasets", "progsys", train)
        test_set = path.join("..", "datasets", "progsys", test)
        embed_file = path.join("..", "grammars", grammar.split("/")[0],
                               grammar.split("/")[1][:-4] + "-Embed.txt")
        with open(embed_file, 'r') as embed:
            embed_code = embed.read()
        insert = embed_code.index(self.INSERTCODE)
        embed_header, embed_footer = "", ""
        if insert > 0:
            embed_header = embed_code[:insert]
            embed_footer = embed_code[insert + len(self.INSERTCODE):]
        with open(train_set, 'r') as train_file,\
                open(test_set, 'r') as test_file:
            return train_file.read(), test_file.read(), \
                   embed_header, embed_footer

    def evaluate_code(self, code):
        problem = params['GRAMMAR_FILE'].split("/")[1][:-4]
        with open("fitness/progsys_code_components.json", "r") as component_file:
            component_dic = json.loads(component_file.read())
        if problem not in component_dic:
            return 1
        positive_components = component_dic[problem]["Positive"]
        negative_components = component_dic[problem]["Negative"]
        fitness_weight = (1 - params['FITNESS_CODE_WEIGHT']) * 2
        num_positive = len(positive_components)
        positive_count = 0
        positive_multiplier = 1
        if num_positive > 0:
            for pos_item in positive_components:
                if pos_item in code:
                    positive_count += 1
            positive_multiplier -= fitness_weight * (positive_count / num_positive)

        num_negative = len(negative_components)
        negative_count = 0
        negative_multiplier = 1
        if num_negative > 0:
            for neg_item in negative_components:
                if neg_item in code:
                    negative_count += 1
            negative_multiplier += fitness_weight * (negative_count / num_negative)

        return (positive_multiplier + negative_multiplier) / 2  # min .5 if all pos no neg, max 1.5 if no pos all neg
