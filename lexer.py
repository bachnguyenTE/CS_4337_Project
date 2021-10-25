###########################################################################
# DESCRIPTION lexer.py 
#
# What this code does: lexer coded for Project Part 1 of UTD Course
#   CS 4337.501 Programming Language Paradigms
# Lexes the modified syntax language as described by the project.
#
# Authors: Bach Nguyen (NVB180000), Thanh Pham (TVP200000)
###########################################################################

import sys
import re
import codecs

###############
#  CONSTANTS  #
###############

ID_TOKEN = 0
INT_TOKEN = 1
STRING_TOKEN = 2
LEXEME = 3
ERROR = 4
END_OF_INPUT = 5
ALLOWED_OPS = ['+', '-', '*', '/', '%', '>', '<', '=', '!', ';']
LEXEME_LIST = ["get", "print", "if", "then", "else", "while", "do", "end", "for", "and", "or", "not"]

line = 1; 
[ID_TOKEN, "x"]


######################
#  HELPER FUNCTIONS  #
######################

# Helper lexer for integers
def lexInt(input, sign):
    i = 0
    while i < len(input) and not input[i].isspace():
        if input[i].isdigit():
            i = i+1
        elif input[i] in ALLOWED_OPS:
            break
        else:
            return[[ERROR, "Invalid integer formatting on line " + str(line)], input]
    return [[INT_TOKEN, sign*int("".join(input[0:i]))], input[i:]]

# Checker for ID token first character
def isIdChar(c):
    return c == "_" or c.isalpha() or c.isdigit()

# Lexer and checker for ID token
def lexIdChecker(lexeme):
    patternID = re.compile(r"[_a-zA-Z][_a-zA-Z0-9]*")
    # Check if ID token matches the formatting requirement
    if patternID.fullmatch(lexeme):
        return [ID_TOKEN, lexeme]
    else: 
        print(lexeme)
        return [ERROR, "Invalid ID formatting on line " + str(line)]

# Lexeme lookup function and redirection to ID lexer
def lookup(lexeme):
    # print, get, if, then, else, while, do, end, for, and, or, not, 
    if lexeme in LEXEME_LIST:
        return [LEXEME, lexeme]
    else:
        return lexIdChecker(lexeme)

# Mother function to both ID and lexeme parse, generating string to pass to helper functions
def lexIdOrKeyword(input, onlyId=False):
    i = 0
    while i < len(input) and isIdChar(input[i]):
        i = i + 1
    if onlyId:
        return [lexIdChecker("".join(input[0:i])), input[i:]]
    return [lookup("".join(input[0:i])), input[i:]] # Use join to convert array to a string

# Helper function for backslash removing (string preprocessing)
def removeOtherBackslash(match_obj):
    string_elem = match_obj.group(0)
    return string_elem.replace("\\", "")

# Function lexing strings
def lexString(input):
    i = 0
    while i < len(input):
        i = i + 1
        if input[i] == "\"":
            if input[i-1] == "\\":
                continue
            else: 
                break
        elif input[i] == ";":
            return [[ERROR, "Invalid STRING formatting on line " + str(line)], input]
    # Preprocess the string, removing various backslashes according to specification
    prepString = r"".join(input[1:i])
    prepString = prepString.replace(r"\\", "\\")
    prepString = prepString.replace(r"\t", "\t")
    prepString = prepString.replace(r"\n", "\n")
    prepString = prepString.replace(r"\"", "\"")
    prepString = re.sub(r"\\[^\s]", removeOtherBackslash, prepString)
    
    return [[STRING_TOKEN, prepString], input[i+1:]]


################
#  MAIN LEXER  #
################

def lex(input):
    global line
    # Eat up whitespace
    i = 0
    while i < len(input) and input[i].isspace():
        if input[i] == "\n":
            line = line + 1
        i = i + 1
        
    # Check EOF
    if i >= len(input):
        return [[END_OF_INPUT, ""], input]
    
    input = input[i:] # remove the whitespace
     
    # Parse equal sign
    if input[0] == "=":
        if len(input) > 1 and input[1] == "=":
            return [[LEXEME, "=="], input[2:]]
        else:
            return [[LEXEME, "="], input[1:]]

    # Parse program sentence line separator
    elif input[0] == ";":
        return [[LEXEME, ";"], input[1:]]
    
    # Parse comma (added for function)
    elif input[0] == ",":
        return [[LEXEME, ","], input[1:]]
    
    # Parse less sign, two cases: less than, less than and equal
    elif input[0] == "<":
        if len(input) > 1 and input[1] == "=":
            return [[LEXEME, "<="], input[2:]]
        else:
            return [[LEXEME, "<"], input[1:]]

    # Parse greater sign, two cases: greater than, greater than and equal
    elif input[0] == ">":
        if len(input) > 1 and input[1] == "=":
            return [[LEXEME, ">="], input[2:]]
        else:
            return [[LEXEME, ">"], input[1:]]

    #Parse not equal sign with error constraint
    elif input[0] == "!":
        if len(input) > 1 and input[1] == "=":
            return [[LEXEME, "!="], input[2:]]
        else:
            return [[ERROR, "Expected '=' after '!' on line " + str(line)], input]

    # Parse integer if found digit
    elif input[0].isdigit():
        return lexInt(input, 1)

    # Parse add (plus) sign
    elif input[0] == "+":
        return [[LEXEME, "+"], input[1:]]

    # Parse minus sign, two cases: negative integer, operator
    elif input[0] == "-":
        if input[1].isdigit():
            return lexInt(input[1:], -1)
        else:
            return [[LEXEME, "-"], input[1:]]

    # Parse multiply 
    elif input[0] == "*":
        return [[LEXEME, "*"], input[1:]]
            
    # Parse divide
    elif input[0] == "/":
        return [[LEXEME, "/"], input[1:]]
    
    # Parse modulo
    elif input[0] == "%":
        return [[LEXEME, "%"], input[1:]]

    # Parse parentheses 
    elif input[0] == "(" or input[0] == ")":
        return [[LEXEME, input[0]], input[1:]]

    # Parse string starting from quote
    elif input[0] == "\"":
        return lexString(input)
            
    # Parse ID or lexeme starting with underscore or alphabet char
    elif input[0] == "_" or input[0].isalpha():
        return lexIdOrKeyword(input)
    
    # Pass all whitespaces
    elif input[0].isspace():
        pass

    # Exception case, char not recognizable by lexer
    else: # not a valid lexeme or token
        return[[ERROR, "Unexpected character on line " + str(line)], input]


##########################
#  PROGRAM LEXER CALLER  #
##########################

# Read entire std input into an array
# This is done for convenience. Usually, the lexer would read directly from a file
print("Enter name of test file (helloworld.txt, test2.txt, test3.txt, test4.txt): ")
filename = input()
file_input = open(filename, "r")
input_prog = list(file_input.read())
# sentence_file = open("/content/test4.txt", "r")
#input = list(sentence_file.read())
print(input)

# Loop through the lexemes and tokens until an error or end of input happens
[next, input_prog] = lex(input_prog)

while next[0] != END_OF_INPUT and next[0] != ERROR:
    print(next)
    [next, input_prog] = lex(input_prog)

if next[0] == ERROR:
    print("ERROR: " + next[1])

file_input.close()