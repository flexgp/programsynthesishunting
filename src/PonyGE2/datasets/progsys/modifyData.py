import os

def read_file(filename, train=True):
    trainTest = "Train"
    if not train:
        trainTest = "Test"
    with open(os.path.join(filename, trainTest +".txt"), "r") as datafile:
        first_line = datafile.readline()
        second_line = datafile.readline()
        return (first_line, second_line)


def remove_newlines(inval_string):
    data_list = eval(inval_string.split("inval = ")[1])
    output_list = []
    for item in data_list:
        output_list.append([item[0].replace("\n", "")])
    return output_list


def replace_space_with_newline(inval_string):
    data_list = eval(inval_string.split("inval = ")[1])
    output_list = []
    for item in data_list:
        new_string = ""
        count = 0
        for char in item[0]:
            if char == " ":
                new_string += "\n"
            else:
                new_string += char
                count += 1
        output_list.append([new_string, count])
    return output_list


def even_squares_append_0(outval_string):
    data_list = eval(outval_string.split("outval = ")[1])
    output_list = []
    for item in data_list:
        item[0] = [0] + item[0]
        output_list.append(item)
    return output_list

def pig_latin(sentences):
    data_list = eval(sentences.split("inval = ")[1])
    output = []
    for sentence in data_list:
        pig_latin_words = []
        for word in sentence[0].split(" "):
            if word == "":
                pig_latin_words.append("")
                continue
            if word[0] in "aeiou":
                pig_latin_words.append(word + "ay")
            else:
                pig_latin_words.append(word[1:] + word[0] + "ay")
        output.append([" ".join(pig_latin_words)])
    return output

def write_file(filename, data, train=True):
    trainTest = "Train"
    if not train:
        trainTest = "Test"
    with open(os.path.join(filename, trainTest +".txt"), "w") as datafile:
        print(data)
        datafile.write(data[0])
        datafile.write(data[1])

# problem = "Replace Space with Newline"
# data = read_file(problem, False)
# new_input = remove_newlines(data[0])
# new_output = replace_space_with_newline("inval = " + str(new_input))
# write_file(problem, ["inval = " + str(new_input) + "\n", "outval = " + str(new_output)], False)

# problem = "Even Squares"
# data = read_file(problem, False)
# new_output = even_squares_append_0(data[1])
# write_file(problem, [data[0], "outval = " + str(new_output)], False)

problem = "Pig Latin"
data = read_file(problem, False)
new_output = pig_latin(data[0])
print(new_output)
# write_file(problem, [data[0], "outval = " + str(new_output)], False)