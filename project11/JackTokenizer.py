"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import re
import string
import typing

IDENTIFIER_TYPE = "IDENTIFIER"
STRING_TYPE = "STRING_CONST"
INT_TYPE = "INT_CONST"
SYMBOL_TYPE = "SYMBOL"
KEYWORD_TYPE = "KEYWORD"

LT = "&lt;"
GT = "&gt;"
QUOTE = "&quot;"
AMP = "&amp;"


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.
    
    # Jack Language Grammar

    A Jack file is a stream of characters. If the file represents a
    valid program, it can be tokenized into a stream of valid tokens. The
    tokens may be separated by an arbitrary number of whitespace characters, 
    and comments, which are ignored. There are three possible comment formats: 
    /* comment until closing */ , /** API comment until closing */ , and 
    // comment until the line’s end.

    - ‘xxx’: quotes are used for tokens that appear verbatim (‘terminals’).
    - xxx: regular typeface is used for names of language constructs 
           (‘non-terminals’).
    - (): parentheses are used for grouping of language constructs.
    - x | y: indicates that either x or y can appear.
    - x?: indicates that x appears 0 or 1 times.
    - x*: indicates that x appears 0 or more times.

    ## Lexical Elements

    The Jack language includes five types of terminal elements (tokens).

    - keyword: 'class' | 'constructor' | 'function' | 'method' | 'field' | 
               'static' | 'var' | 'int' | 'char' | 'boolean' | 'void' | 'true' |
               'false' | 'null' | 'this' | 'let' | 'do' | 'if' | 'else' | 
               'while' | 'return'
    - symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
    - integerConstant: A decimal number in the range 0-32767.
    - StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
    - identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.

    ## Program Structure

    A Jack program is a collection of classes, each appearing in a separate 
    file. A compilation unit is a single class. A class is a sequence of tokens 
    structured according to the following context free syntax:
    
    - class: 'class' className '{' classVarDec* subroutineDec* '}'
    - classVarDec: ('static' | 'field') type varName (',' varName)* ';'
    - type: 'int' | 'char' | 'boolean' | className
    - subroutineDec: ('constructor' | 'function' | 'method') ('void' | type) 
    - subroutineName '(' parameterList ')' subroutineBody
    - parameterList: ((type varName) (',' type varName)*)?
    - subroutineBody: '{' varDec* statements '}'
    - varDec: 'var' type varName (',' varName)* ';'
    - className: identifier
    - subroutineName: identifier
    - varName: identifier

    ## Statements

    - statements: statement*
    - statement: letStatement | ifStatement | whileStatement | doStatement | 
                 returnStatement
    - letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
    - ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{' 
                   statements '}')?
    - whileStatement: 'while' '(' 'expression' ')' '{' statements '}'
    - doStatement: 'do' subroutineCall ';'
    - returnStatement: 'return' expression? ';'

    ## Expressions
    
    - expression: term (op term)*
    - term: integerConstant | stringConstant | keywordConstant | varName | 
            varName '['expression']' | subroutineCall | '(' expression ')' | 
            unaryOp term
    - subroutineCall: subroutineName '(' expressionList ')' | (className | 
                      varName) '.' subroutineName '(' expressionList ')'
    - expressionList: (expression (',' expression)* )?
    - op: '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '='
    - unaryOp: '-' | '~' | '^' | '#'
    - keywordConstant: 'true' | 'false' | 'null' | 'this'
    
    Note that ^, # correspond to shiftleft and shiftright, respectively.
    """

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        # Your code goes here!
        # A good place to start is to read all the lines of the input:
        # input_lines = input_stream.read().splitlines()
        input_stream.seek(0)
        self._word_num = -1
        self._cur_word = ""
        self._cur_token = ""
        self._cur_type = ""
        self._keywords = {"class", "method", "function", "constructor", "int",
                          "boolean", "char", "void", "var", "static", "field", "let", "do",
                          "if", "else", "while", "return", "true", "false", "null", "this"}
        self._symbols = {'{', '}', '(', ')', '[', ']', '.', ',', ';', '+',
                         '-', '*', '/', '&', '|', '<', '>', '=', '~', '^', '#'}
        self._preprocess_input(input_stream)

    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        # Your code goes here!
        return self._word_num < len(self._input_words)

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token. 
        This method should be called if has_more_tokens() is true. 
        Initially there is no current token.
        """
        # Your code goes here!
        if not self._cur_word:
            self._word_num += 1
            if not self.has_more_tokens():
                return
            self._cur_word = self._input_words[self._word_num]

        while self.has_more_tokens() and not self._cur_word:
            self._word_num += 1
            self._cur_word = self._input_words[self._word_num]

        if not self.has_more_tokens():
            return

        self._process_token()
        # print(self._cur_type + ": " + self._cur_token)

    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        # Your code goes here!
        return self._cur_type

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT", 
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", 
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        # Your code goes here!
        return self._cur_token.upper()

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
            Recall that symbol was defined in the grammar like so:
            symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
        """
        # Your code goes here!
        return self._cur_token

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
            Recall that identifiers were defined in the grammar like so:
            identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.
        """
        # Your code goes here!
        return self._cur_token

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
            Recall that integerConstant was defined in the grammar like so:
            integerConstant: A decimal number in the range 0-32767.
        """
        # Your code goes here!
        return int(self._cur_token)

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double 
            quotes. Should be called only when token_type() is "STRING_CONST".
            Recall that StringConstant was defined in the grammar like so:
            StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
        """
        # Your code goes here!
        return self._cur_token

    # private methods
    """
    Pre-processes the input.
    Splits the input by lines, handles and deletes '//' comments.
    Splits the input by "words", handles and deletes '/** ... */' and '/* ... */' comments.
    After all is done - The instance's _input_words is a list of all the inputs tokens. 
    """
    def _preprocess_input(self, input_stream) -> None:
        self._input_lines = input_stream.read().splitlines()
        self._words_with_comments = []
        self._input_words = []
        self._delete_line_comments()
        in_string = False
        cur_string = ""
        for line in self._input_lines:
            if not line:
                continue
            if '"' not in line and not in_string:
                for word in line.split():
                    self._words_with_comments.append(word)
                continue
            indices = [idx for idx in range(len(line)) if line[idx] == '"']
            if len(indices) == 0 and in_string:
                cur_string += line
                continue
            j = 0
            while j < len(indices):
                # prev_ind, cur_ind, next_ind = indices[j-1], indices[j], indices[j+1]
                if in_string:
                    cur_string += line[:min(indices[j]+1, len(line)-1)]
                    self._words_with_comments.append(cur_string)
                    cur_string = ""
                    in_string = False
                    if len(indices) == 1:
                        for word in line[min(indices[0]+1, len(line)-1):].split():
                            self._words_with_comments.append(word)
                        break
                    j += 1

                if in_string is False:
                    if j == 0:
                        for word in line[:indices[j]].split():
                            self._words_with_comments.append(word)
                    else:
                        for word in line[indices[j-1]+1:indices[j]].split():
                            self._words_with_comments.append(word)

                    if j == len(indices)-1:
                        cur_string += line[indices[j]:]
                        in_string = True
                    else:
                        cur_string = ""
                        self._words_with_comments.append(line[indices[j]:min(indices[j+1]+1, len(line)-1)])
                    if (j+1) == len(indices) - 1:
                        self._words_with_comments.append(line[indices[j+1]+1:])
                j += 2
        self._delete_long_comments()
        # for word in self._input_words:
        #     print(word)
        self.advance()

    """
    Deletes comments of types:
        /* comment until closing */
        /** API comment until closing */
    """

    def _delete_long_comments(self) -> None:
        to_add = True
        for word in self._words_with_comments:
            temp_word = word
            if to_add is False:
                if '*/' not in word:
                    continue
                else:
                    start = word.find('*/') + 2
                    word = word[start:]
                    to_add = True

            while temp_word:
                if to_add:
                    add_word = ""
                    if '/**' in temp_word and temp_word[0] != '"' and temp_word[-1] != '"':
                        to_add = False
                        add_word, temp_word = temp_word[:temp_word.find('/**')], temp_word[temp_word.find('/**')+3:]
                    elif '/*' in temp_word and temp_word[0] != '"' and temp_word[-1] != '"':
                        to_add = False
                        add_word, temp_word = temp_word[:temp_word.find('/*')], temp_word[temp_word.find('/*')+2:]
                    if add_word:
                        if ('\t' in add_word or ' ' in add_word) and add_word[0] != '"' and add_word[-1] != '"':
                            words = add_word.split()
                            for w in words:
                                self._input_words.append(w)
                        else:
                            self._input_words.append(add_word)
                    break
                else:
                    if '*/' in temp_word:
                        to_add = True
                        temp_word = temp_word[temp_word.find('*/')+1:]


            if (len(word) >= 2 and word[0:2] == '/*') or (len(word) >= 3 and word[0:3] == '/**'):
                to_add = False
                continue
            # if '/**' in word:
            #     to_add = False
            #     continue
            # elif '/*' in word:
            #     to_add = False
            #     continue
            if temp_word:
                if ('\t' in word or ' ' in word) and word[0] != '"' and word[-1] != '"':
                    words = word.split()
                    for w in words:
                        self._input_words.append(w)
                else:
                    self._input_words.append(word)

    """
    Deletes comments of type:
        // comment until the line’s end.
    """
    def _delete_line_comments(self) -> None:
        for i, line in enumerate(self._input_lines):
            if '//' in line:
                line = self._handle_line_comment(i, line)
            self._input_lines[i] = line

    """
    Handles a line which includes a '//' string.
    Checks if it's a comment or a part of a string constant.
    If it's a comment -> splits the line accordingly.
    """
    def _handle_line_comment(self, i, line):
        indices = [idx for idx in range(len(line)) if line[idx] == '"']
        if line[0:2] == '//':
            line = ""
        elif '"' not in line:
            line = line.split('//')[0]
            self._input_lines[i] = line.split()
        elif line.count('"') == 1:
            line = line.split('//')[0]
            self._input_lines[i] = line.split()
        elif line.count('//') == 1 and (indices[1] < line.find('//') or line.find('//') < indices[0]):
            line = line.split('//')[0]
        elif indices[0] < line.find('//') < indices[1] and line.count('//') >= 2:
            second_slash = line.find('//', indices[1], len(line) - 1)
            line = line[:second_slash]
        return line

    def _process_token(self):
        if self._is_cur_word_keyword():
            self._cur_type = KEYWORD_TYPE
        elif self._is_cur_word_symbol():
            self._cur_type = SYMBOL_TYPE
        elif self._is_cur_word_int():
            self._cur_type = INT_TYPE
        elif self._is_cur_word_string():
            self._cur_type = STRING_TYPE
        else:
            self._get_identifier()
            self._cur_type = IDENTIFIER_TYPE

    def _get_identifier(self) -> None:
        self._cur_token = ""
        while self._cur_word and self._cur_word[0] not in self._symbols:
            self._cur_token += self._cur_word[0]
            self._cur_word = self._cur_word[1:]

    def _is_cur_word_symbol(self) -> bool:
        char = self._cur_word[0]
        for symbol in self._symbols:
            if char == symbol:
                # self._cur_token = self._token_is_symbol(symbol)
                self._cur_token = symbol
                self._cur_word = self._cur_word[1:]
                return True
        return False

    # def _token_is_symbol(self, symbol) -> string:
    #     if symbol == '<':
    #         return LT
    #     elif symbol == '>':
    #         return GT
    #     elif symbol == '&':
    #         return AMP
    #     return symbol

    def _is_str_keyword(self, word, keyword) -> bool:
        if word == keyword:
            return True
        if len(word) >= len(keyword) and word[0:len(keyword)] == keyword:
            if word[len(keyword)] in self._symbols:
                return True
        # if keyword in {"while", "if", "return"}:
        #     if len(word) >= len(keyword) and word[0:len(keyword)] == keyword:
        #         if word[len(keyword)] == "(":
        #             return True
        #
        # if keyword in {"else"}:
        #     if len(word) >= len(keyword) and word[0:len(keyword)] == keyword:
        #         if word[len(keyword)] == "{":
        #             return True
        #
        # if keyword in {"return", "true", "false", "null", "this"}:
        #     if len(word) >= len(keyword) and word[0:len(keyword)] == keyword:
        #         if word[len(keyword)] == ";":
        #             return True

    def _is_cur_word_keyword(self) -> bool:
        word = self._cur_word
        for keyword in self._keywords:
            if self._is_str_keyword(word, keyword):
                self._cur_token = keyword
                self._cur_word = self._cur_word[len(self._cur_token):]
                return True
        return False

    def _is_cur_word_int(self) -> bool:
        if self._cur_word:
            if self._cur_word[0].isnumeric():
                self._cur_token = ""
                i = 0
                while i < len(self._cur_word) and self._cur_word[i].isnumeric():
                    self._cur_token += self._cur_word[i]
                    i += 1
                if i < len(self._cur_word):
                    self._cur_word = self._cur_word[i:]
                else:
                    self._cur_word = ""
                return True
        return False

    def _is_cur_word_string(self) -> bool:
        if self._cur_word and self._cur_word[0] == '"':
            self._cur_token = ""
            if self._cur_word.count('"') == 1:
                self._cur_token += self._cur_word
                self._word_num += 1
                self._cur_word = self._input_words[self._word_num]
                while self._cur_word.count('"') == 0:
                    self._cur_token += " " + self._cur_word
                    self._word_num += 1
                    self._cur_word = self._input_words[self._word_num]
                split_index = self._cur_word.find('"')
                self._cur_token += " " + self._cur_word[0:split_index + 1]
                self._cur_word = self._cur_word[split_index + 1:]
            elif self._cur_word.count('"') == 2 and self._cur_word[len(self._cur_word) - 1] == '"':
                self._cur_token, self._cur_word = self._cur_word, ""
            else:
                second_quote_index = self._cur_word[1:].find('"')
                self._cur_token = self._cur_word[:second_quote_index+2]
                self._cur_word = self._cur_word[second_quote_index+2:]
            return True
        return False
