import json

def write_ind_grammar(problem_name):
    with open("problem_data.json", "r") as data_file:
        problem_dic = json.loads(data_file.read())
    grammar = grammarFromDic(problem_dic[problem_name])
    with open("../progsys/" + problem_name + ".bnf", "w") as grammar_file:
        grammar_file.write(grammar)

def grammarFromDic(metadata_dic):
    predefined = makePredefined(metadata_dic["DataTypes"], metadata_dic["OutputType"])
    grammar_string = "<code> ::= <code><assign>'\\n'|<assign>'\\n'\n"
    using_list = False
    for dtype in metadata_dic["DataTypes"]:
        if "list" in dtype or "string" in dtype:
            using_list = True
    if "bool" in metadata_dic["DataTypes"]:
        if using_list:
            grammar_string = """<code> ::= <code><statement>'\\n'|<statement>'\\n'
<statement> ::= <call>|<assign>|<compound_stmt>
<compound_stmt> ::= <for>|<if>|'loopBreak% = 0\\nwhile '<bool>':{:\\n'<code>'\\nif loopBreak% > loopBreakConst or stop:{:\\nbreak\\n:}loopBreak% += 1\\n:}'
"""
        else:
            grammar_string = """<code> ::= <code><statement>'\\n'|<statement>'\\n'
<statement> ::= <assign>|<assign>|<compound_stmt>
<compound_stmt> ::= <if>|'loopBreak% = 0\\nwhile '<bool>':{:\\n'<code>'\\nif loopBreak% > loopBreakConst or stop:{:\\nbreak\\n:}loopBreak% += 1\\n:}'
"""
    elif using_list:
        grammar_string = """<code> ::= <code><statement>'\\n'|<statement>'\\n'
<statement> ::= <call>|<assign>|<for>
"""
    grammar_type_components = ""
    assign = "<assign> ::= "
    list_for = "<for> ::= "
    call = "<call> ::= "
    for dtype in metadata_dic["DataTypes"]:
        if dtype == "list_int":
            list_for += "<for_int>|"
            call += "<call_int>|"
        elif dtype == "list_float":
            list_for += "<for_float>|"
            call += "<call_float>|"
        elif dtype == "list_string":
            list_for += "<for_string>|"
            call += "<call_string>|"
        elif dtype == "string":
            list_for += "<for_iter_string>|"
            call += "<assign>|"
        with open(dtype + ".bnf", "r") as grammar_type_file:
            for line in grammar_type_file:
                if "<assign> ::= " in line:
                    assign += line.split("<assign> ::= ")[1].strip() + "|"
                    continue
                elif "<bool> ::= " in line:
                    line = line.strip()
                    bool_dic = {"bool_int": "<bool_int> ::= <int>' '<comp_op>' '<int>",
"bool_float": "<bool_float> ::= <float>' '<comp_op>' '<float>",
"bool_string": "<bool_string> ::= <string>' in '<string>|<string>' not in '<string>|<string>' == '<string>|<string>' != '<string>|<string>'.startswith('<string>')'|<string>'.endswith('<string>')'",
"bool_list_int": "<bool_list_int> ::= <int>' '<in_list_comp_op>' '<list_int>|<list_int>' '<list_comp_op>' '<list_int>",
"bool_list_float": "<bool_list_float> ::= <float>' '<in_list_comp_op>' '<list_float>|<list_float>' '<list_comp_op>' '<list_float>",
"bool_list_string": "<bool_list_string> ::= <string>' '<in_list_comp_op>' '<list_string>|<list_string>' '<list_comp_op>' '<list_string>"}
                    after_lines = ""
                    for dtype2 in metadata_dic["DataTypes"]:
                        if dtype2 == "bool":
                            continue
                        line += "|<bool_" + dtype2 + ">"
                        after_lines += bool_dic["bool_" + dtype2] + "\n"
                    line += "\n" + after_lines
                elif "<int_specialop> ::= " in line:
                    if "string" in metadata_dic["DataTypes"]:
                        line = line.strip() + "|'len('<string>')'|'saveOrd('<string>')'" + '\n'
                    if "list_int" in metadata_dic["DataTypes"]:
                        line = line.strip() + "|'getIndexIntList('<list_int>', '<int>')'|'len('<list_int>')'" + '\n'
                    if "list_float" in metadata_dic["DataTypes"]:
                        line = line.strip() + "|'len('<list_float>')'" + '\n'
                    if "list_string" in metadata_dic["DataTypes"]:
                        line = line.strip() + "|'len('<list_string>')'" + '\n'
                elif "<float_specialop> ::= " in line:
                    if "list_float" in metadata_dic["DataTypes"]:
                        line = line.strip() + "|'getIndexFloatList('<list_float>','<int>')'" + '\n'
                elif "<string_specialop> ::= " in line:
                    if "list_string" in metadata_dic["DataTypes"]:
                        line = line.strip() + "|'getIndexStringList('<list_string>','<int>')'" + '\n'
                grammar_type_components += line

    grammar_string += assign[:-1] + "\n"  # remove trailing |
    if len(list_for) > 10:  # somethings been added, using list
        grammar_string += list_for[:-1] + "\n"
        grammar_string += call[:-1] + "\n"
        grammar_string += """<in_list_comp_op> ::= 'in'|'not in'
<list_comp_op> ::= '=='|'!='\n"""
    grammar_string += grammar_type_components

    # Add inputs into type variables
    split_grammar = grammar_string.split("\n")
    assembled_grammar = ""
    for line in split_grammar:
        assembled_grammar += line
        for ind in range(len(metadata_dic["InputTypes"])):
            if "<" + metadata_dic["InputTypes"][ind] + "_var> ::=" in line:
                assembled_grammar += "|'in" + str(ind) + "'"
        for ind in range(len(metadata_dic["OutputType"])):
            if "<" + metadata_dic["OutputType"][ind] + "_var> ::=" in line:
                assembled_grammar += "|'res" + str(ind) + "'"

        assembled_grammar += "\n"
    return predefined + assembled_grammar


def makePredefined(data_types, output_types):
    variable_type_dic = {"int": "'i0 = int(); i1 = int(); i2 = int()'\n",
                         "bool": "'b0 = bool(); b1 = bool(); b2 = bool()'\n",
                         "list_int": "'li0 = []; li1 = []; li2 = []'\n",
                         "list_string": "'ls0 = []; ls1 = []; ls2 = []'\n",
                         "list_float": "'lf0 = []; lf1 = []; lf2 = []'\n",
                         "string": "'s0 = str(); s1 = str(); s2 = str()'\n",
                         "float": "'f0 = float(); f1 = float(); f2 = float()'\n"}
    defined_var = "<predefined> ::= "
    for dtype in data_types:
        defined_var += variable_type_dic[dtype]
    output_instatiation_types = {"bool": "bool()", "int": "int()", "string": "str()", "float": "float()",
                                 "list_string": "[]", "list_int": "[]", "list_float": "[]"}
    for index in range(len(output_types)):
        if index == 0:
            defined_var += "'res" + str(index) + " = " + output_instatiation_types[output_types[index]]
        else:
            defined_var += "; res" + str(index) + " = " + output_instatiation_types[output_types[index]]
    defined_var += "'\n<code>\n"
    return defined_var


first_ten = ["Checksum", "Compare String Lengths", "Double Letters", "Grade", "Last Index of Zero", "Median", "Mirror Image", "Negative To Zero", "Small Or Large", "Vectors Summed"]
second_ten = ["Count Odds", "For Loop Index", "Digits", "Number IO", "Super Anagrams", "Smallest", "String Lengths Backwards","Sum of Squares", "Syllables", "Vector Average"]
last_five = ["Even Squares", "Pig Latin", "Replace Space With Newline", "Scrabble Score",  "X-Word Lines"]
for problem in last_five:
    write_ind_grammar(problem)
