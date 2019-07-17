
def checksum(string):
    char_sum = 0
    for char in string:
        char_sum += ord(char)
    char_mod = char_sum % 64
    char_mod_with_space = char_mod + ord(" ")
    res0 = chr(char_mod_with_space % 128)
    return res0


def compare_string_lenghths(n1, n2, n3):
    if len(n1) < len(n2) and len(n2) < len(n3):
        return True
    return False


def count_odds(vec):
    count = 0
    for item in vec:
        if item % 2 == 0:
            count += 1
    return count


def digits(i1):
    def int_to_int_array(integer):
        b = list(str(integer))
        if b[0] == "-":
            b[1] = b[0] + b[1]
            b = b[1:]
        return list(map(int, b))
    out = int_to_int_array(i1)
    out.reverse()
    return out


def double_letters(string):
    out = ""
    for char in string:
        out += char
        if char in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
            out += char
        if char == "!":
            out += char * 2
    return out


def even_squares(num):
    i0 = int()
    res0 = []
    for i in range(num):
        i0 = i * i
        if i0 < num:
            if i0 % 2 == 0:
                res0.append(i0)
    return res0


def for_loop_index(start, end, step):
    out = []
    count = start
    for i in range(start, end):
        if count < end:
            out.append(count)
        count += step
    return out


def grade(a_thresh, b_thresh, c_thresh, d_thresh, grade):
    out = ""
    if grade > a_thresh:
        out = "A"
    if a_thresh > grade > b_thresh:
        out = "B"
    if b_thresh > grade > c_thresh:
        out = "C"
    if c_thresh > grade > d_thresh:
        out = "D"
    if d_thresh > grade:
        out = "F"
    return out


def last_index_of_zero(vec):
    out_index = 0
    for index in range(len(vec)):
        if vec[index] == 0:
            out_index = index
    return out_index


def median(in0, in1, in2):
    out = max(min(in1, in0), min(max(in0, in1), in2))
    return out


def mirror_image(vec1, vec2):
    vec1.reverse()
    out = vec1 == vec2
    return out


def negative_to_zero(vec):
    out = []
    for item in vec:
        if item < 0:
            out.append(0)
        else:
            out.append(item)
    return out


def number_IO(int, float):
    return int + float


def pig_latin(sentence):
    pig_latin_words = []
    for word in sentence.split(" "):
        if word[0] in "aeiou":
            pig_latin_words.append(word + "ay")
        else:
            pig_latin_words.append(word[1:] + word[0] + "ay")
    return " ".join(pig_latin_words)


def replace_space_with_newline(string):
    new_string = ""
    count = 0
    for char in string:
        if char == " ":
            new_string += "\n"
        else:
            new_string += char
            count += 1
    return new_string, count


def small_or_large(n):
    out = ""
    if n < 1000:
        out = "small"
    if n >= 2000:
        out = "large"
    return out


def smallest(in0, in1, in2, in3):
    out = min(min(min(in0, in1), in2), in3)
    return out


def string_lengths_backwards(vec):
    vec.reverse()
    out = []
    for item in vec:
        out.append(len(item))
    return out


def sum_of_squares(n):
    out = 0
    for val in range(n + 1):
        out += val * val
    return out


def super_anagrams(stringx, stringy):
    out = True
    for char in stringx:
        if char not in stringy:
            out = False
    return out


def syllables(string):
    out = 0
    for char in string:
        if char in "aeiou":
            out += 1
    return out


def vector_average(vector):
    total = 0
    for item in vector:
        total += item
    out = total / len(vector)
    return out


def vectors_summed(vector1, vector2):
    out = []
    for x in range(len(vector1)):
        out.append(vector1[x] + vector2[x])
    return out


def x_word_lines(string, wordsPerLine):
    out = ""
    count = 0
    prev_word = ""
    for char in string:
        if char == " " or char == "\n":
            if count <= wordsPerLine:
                out += prev_word + " "
                count += 1
            else:
                out += prev_word + "\n"
                count = 0
            prev_word = ""
        else:
            prev_word += char
    out += prev_word
    return out
