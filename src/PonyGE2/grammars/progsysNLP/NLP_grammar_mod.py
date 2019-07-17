import json


def get_problem_words(problem_name):
    with open("ProblemDescriptions.json", "r") as problem_file:
        problem_dic = json.loads(problem_file.read())
        problem = problem_dic[problem_name]
        return problem.split(" ")

def match_words(word_list):
    with open("NLP_keywords.json", "r") as keywords_file:
        keywords_dic = json.loads(keywords_file.read())
    out_dic = {}
    for word in word_list:
        if word in keywords_dic:
            out_dic[word] = keywords_dic[word]
    return out_dic

def modify_grammar(problem_name, matched_words):
    new_grammar = ""
    with open("../progsys/" + problem_name + ".bnf", "r") as grammar:
        for line in grammar:
            line = line.strip()
            line_parts = line.split("::=")
            if len(line_parts) <= 1:
                new_grammar += line + "\n"
                continue
            line_choices = line_parts[1].split("|")
            to_add = []
            for matched_key in matched_words.keys():
                for nt_key in matched_words[matched_key].keys():
                    if nt_key in line_parts[0]:
                        for choice in line_choices:
                            if matched_words[matched_key][nt_key] in choice:
                                to_add.append(choice)
            for item in to_add:
                line += "|" + item
            new_grammar += line + "\n"

    with open("../progsysRule/" + problem_name + ".bnf", "w") as grammarMod:
        grammarMod.write(new_grammar)


def apply_rules(problem_name):
    words = get_problem_words(problem_name)
    change_dic = match_words(words)
    modify_grammar(problem_name, change_dic)


def modify_grammar_with_problem_keywords(problem_name):
    with open("problem_keywords.json", "r") as keywords:
        problem_keywords = json.loads(keywords.read())
    arguments = problem_keywords[problem_name]
    with open("../progsysRule/" + problem_name + ".bnf", "r") as grammar:
        new_grammar = ""
        for line in grammar:
            for key in arguments:
                if key + " ::=" in line:
                    if arguments[key]:
                        line = key + " ::= "
                        for value in arguments[key]:
                            line += "'" + str(value) + "'|"
                        line = line[:-1] + "\n"  # remove trailing |
            new_grammar += line

    with open("../progsysRuleAndKey/" + problem_name + ".bnf", "w") as new_g:
        new_g.write(new_grammar)


first_ten = ["Checksum", "Compare String Lengths", "Double Letters", "Grade", "Last Index of Zero", "Median", "Mirror Image", "Negative To Zero", "Small Or Large", "Vectors Summed"]
second_ten = ["Count Odds", "Even Squares", "For Loop Index", "Digits", "Number IO", "Super Anagrams", "Smallest", "String Lengths Backwards","Sum of Squares", "Syllables", "Vector Average"]
for problem in second_ten:
    apply_rules(problem)
    modify_grammar_with_problem_keywords(problem)
