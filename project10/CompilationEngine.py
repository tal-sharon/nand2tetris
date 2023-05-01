"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import JackTokenizer


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_stream: JackTokenizer, output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        # Your code goes here!
        # Note that you can write to output_stream like so:
        # output_stream.write("Hello world! \n")
        self.SUBROTINE = ["METHOD", "FUNCTION", "CONSTRUCTOR"]
        self.TYPE = ["INT", "CHAR", "BOOLEAN"]
        self.TOKEN_TYPE = ["INT", "CHAR", "BOOLEAN"]
        self.class_names = []
        self.ERROR = "ERROR"
        self.IF_WHILE_LET_RET_DO = ["IF", "WHILE", "LET", "RETURN", "DO"]
        self.Tokenize = input_stream
        self.output_stream = output_stream
        self.opDict = {'<': '&lt;', '>': '&gt;', '"': '&quot;', '&': '&amp;'}

    def compile_class(self) -> None:
        """Compiles a complete class."""
        if (self.Tokenize.token_type() != "KEYWORD" or self.Tokenize.keyword()
                != 'CLASS'):
            raise self.ERROR
        self.output_stream.write("<class>\n")
        self.output_stream.write(f"<keyword> class </keyword>\n")
        if (self.Tokenize.has_more_tokens()):
            self.Tokenize.advance()
        if (self.Tokenize.token_type() != "IDENTIFIER"):
            raise self.ERROR
        self.output_stream.write(f"<identifier> {self.Tokenize.identifier()} "
                                 f"</identifier>\n")
        self.class_names.append(self.Tokenize.identifier())
        if (self.Tokenize.has_more_tokens()):
            self.Tokenize.advance()
        if (self.Tokenize.token_type() != "SYMBOL" or self.Tokenize.symbol()
                != "{"):
            raise self.ERROR
        self.output_stream.write("<symbol> { </symbol>\n")
        if (self.Tokenize.has_more_tokens()):
            self.Tokenize.advance()
        while (self.Tokenize.token_type() == "KEYWORD" and
               (self.Tokenize.keyword() == "FIELD" or self.Tokenize.keyword()
                == "STATIC")):
            self.compile_class_var_dec()
        while (self.Tokenize.token_type() == "KEYWORD" and
               self.Tokenize.keyword() in self.SUBROTINE):
            self.compile_subroutine()

        if (self.Tokenize.token_type() != "SYMBOL" or
                self.Tokenize.symbol() != "}"):
            raise self.ERROR
        self.output_stream.write("<symbol> } </symbol>\n")
        self.output_stream.write("</class>\n")

    def compile_class_var_dec(self) -> None:  # OK
        """Compiles a static declaration or a field declaration."""
        self.output_stream.write("<classVarDec>\n")
        tmp = self.Tokenize.keyword().lower()
        self.output_stream.write(f"<keyword> {tmp} </keyword>\n")
        if (self.Tokenize.has_more_tokens()):
            self.Tokenize.advance()
        if (self.Tokenize.token_type() != "KEYWORD"  and
                self.Tokenize.token_type() != "IDENTIFIER"):
            raise self.ERROR
        if (self.Tokenize.token_type() == "KEYWORD"):
            tmp = self.Tokenize.keyword().lower()
            self.output_stream.write(f"<keyword> {tmp} </keyword>\n")
        else:
            self.output_stream.write(f"<identifier>"
                                  f" {self.Tokenize.identifier()} "
                                 f"</identifier>\n")

        if (self.Tokenize.has_more_tokens()):
            self.Tokenize.advance()
        if (self.Tokenize.token_type() != "IDENTIFIER"):
            raise self.ERROR
        self.output_stream.write(f"<identifier> {self.Tokenize.identifier()} "
                                 f"</identifier>\n")
        if (self.Tokenize.has_more_tokens()):
            self.Tokenize.advance()
        while (self.Tokenize.token_type() == "SYMBOL" and
               self.Tokenize.symbol() == ","):
            self.output_stream.write("<symbol> , </symbol>\n")
            if (self.Tokenize.has_more_tokens()):
                self.Tokenize.advance()
            if (self.Tokenize.token_type() != "IDENTIFIER"):
                raise self.ERROR
            self.output_stream.write(
                f"<identifier> {self.Tokenize.identifier()} "
                f"</identifier>\n")
            if (self.Tokenize.has_more_tokens()):
                self.Tokenize.advance()
        if (self.Tokenize.token_type() != "SYMBOL" or self.Tokenize.symbol()
                != ";"):
            raise self.ERROR
        self.output_stream.write("<symbol> ; </symbol>\n")
        if (self.Tokenize.has_more_tokens()):
            self.Tokenize.advance()
        self.output_stream.write("</classVarDec>\n")

    def compile_subroutine(self) -> None:  # OK
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        self.output_stream.write("<subroutineDec>\n")
        self.output_stream.write(
            f"<keyword> {self.Tokenize.keyword().lower()} </keyword>\n")
        if (self.Tokenize.has_more_tokens()):
            self.Tokenize.advance()
        if (self.Tokenize.token_type() != "KEYWORD" and
             self.Tokenize.token_type() != "IDENTIFIER"):
            raise self.ERROR
        #solve void identifier probelm.
        if (self.Tokenize.token_type() == "KEYWORD"):
            self.output_stream.write(
                f"<keyword> {self.Tokenize.keyword().lower()} </keyword>\n")
        else:
            self.output_stream.write(f"<identifier>"
                                  f" {self.Tokenize.identifier()} "
                                 f"</identifier>\n")
        if (self.Tokenize.has_more_tokens()):
            self.Tokenize.advance()
        if (self.Tokenize.token_type() != "IDENTIFIER"):
            raise self.ERROR
        self.output_stream.write(f"<identifier> {self.Tokenize.identifier()} "
                                 f"</identifier>\n")
        if (self.Tokenize.has_more_tokens()):
            self.Tokenize.advance()
        if (self.Tokenize.token_type() != "SYMBOL" or self.Tokenize.symbol()
                != "("):
            raise self.ERROR
        self.output_stream.write("<symbol> ( </symbol>\n")
        if (self.Tokenize.has_more_tokens()):
            self.Tokenize.advance()
        self.compile_parameter_list()

        self.output_stream.write("<symbol> ) </symbol>\n")
        if (self.Tokenize.has_more_tokens()):
            self.Tokenize.advance()

        self.output_stream.write("<subroutineBody>\n")
        if (self.Tokenize.token_type() != "SYMBOL" or
                self.Tokenize.symbol() != "{"):
            raise self.ERROR
        self.output_stream.write("<symbol> { </symbol>\n")
        if (self.Tokenize.has_more_tokens()):
            self.Tokenize.advance()
        while (self.Tokenize.token_type() == "KEYWORD" and
               self.Tokenize.keyword() == "VAR"):
            self.compile_var_dec()
        self.compile_statements()
        if (self.Tokenize.token_type() != "SYMBOL" or
                self.Tokenize.symbol() != "}"):
            raise self.ERROR
        self.output_stream.write("<symbol> } </symbol>\n")
        self.output_stream.write("</subroutineBody>\n")
        self.output_stream.write("</subroutineDec>\n")
        if (self.Tokenize.has_more_tokens()):
            self.Tokenize.advance()

    def compile_parameter_list(self) -> None:  # OK
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        self.output_stream.write("<parameterList>\n")
        if (self.Tokenize.token_type() != "SYMBOL" or
                self.Tokenize.symbol() != ")"):
            if (self.Tokenize.token_type() != "KEYWORD" and
                    self.Tokenize.token_type() != "IDENTIFIER"):
                raise self.ERROR

            while (self.Tokenize.token_type() != "KEYWORD" or
                    self.Tokenize.token_type() != "IDENTIFIER"):
                if (self.Tokenize.token_type() == "KEYWORD"):
                    self.output_stream.write(
                        f"<keyword> {self.Tokenize.keyword().lower()} "
                        f"</keyword>\n")
                else:
                    self.output_stream.write(
                        f"<identifier> {self.Tokenize.identifier()} "
                        f"</identifier>\n")
                if (self.Tokenize.has_more_tokens()):
                    self.Tokenize.advance()
                if (self.Tokenize.token_type() != "IDENTIFIER"):
                    raise self.ERROR
                self.output_stream.write(
                    f"<identifier> {self.Tokenize.identifier()} "
                    f"</identifier>\n")
                if (self.Tokenize.has_more_tokens()):
                    self.Tokenize.advance()
                if (self.Tokenize.token_type() != "SYMBOL" or
                        (self.Tokenize.symbol() != "," and
                        self.Tokenize.symbol() != ")")):
                    raise self.ERROR
                if (self.Tokenize.symbol() == ","):
                    self.output_stream.write("<symbol> , </symbol>\n")
                else:
                    break
                if (self.Tokenize.has_more_tokens()):
                    self.Tokenize.advance()
        self.output_stream.write("</parameterList>\n")

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        self.output_stream.write("<varDec>\n")
        self.output_stream.write("<keyword> var </keyword>\n")
        if (self.Tokenize.has_more_tokens()):
            self.Tokenize.advance()
        if (self.Tokenize.token_type() != "KEYWORD" and
                self.Tokenize.token_type() != "IDENTIFIER"):
            raise self.ERROR
        if (self.Tokenize.token_type() == "KEYWORD"):
            self.output_stream.write(
                f"<keyword> {self.Tokenize.keyword().lower()} </keyword>\n")
        else:
            self.output_stream.write(
                f"<identifier> {self.Tokenize.identifier()} "
                f"</identifier>\n")
        if (self.Tokenize.has_more_tokens()):
            self.Tokenize.advance()
        if (self.Tokenize.token_type() != "IDENTIFIER"):
            raise self.ERROR
        self.output_stream.write(
            f"<identifier> {self.Tokenize.identifier()} "
            f"</identifier>\n")
        if (self.Tokenize.has_more_tokens()):
            self.Tokenize.advance()
        while (self.Tokenize.token_type() == "SYMBOL" and
               self.Tokenize.symbol() == ","):
            self.output_stream.write("<symbol> , </symbol>\n")
            if (self.Tokenize.has_more_tokens()):
                self.Tokenize.advance()
            if (self.Tokenize.token_type() != "IDENTIFIER"):
                raise self.ERROR
            self.output_stream.write(
                f"<identifier> {self.Tokenize.identifier()} "
                f"</identifier>\n")
            if (self.Tokenize.has_more_tokens()):
                self.Tokenize.advance()
        if (self.Tokenize.token_type() != "SYMBOL" or
                self.Tokenize.symbol() != ';'):
            raise self.ERROR
        self.output_stream.write("<symbol> ; </symbol>\n")
        if (self.Tokenize.has_more_tokens()):
            self.Tokenize.advance()

        self.output_stream.write("</varDec>\n")

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        self.output_stream.write("<statements>\n")
        if (self.Tokenize.token_type() == "SYMBOL" and
                self.Tokenize.symbol() == "}"):
            self.output_stream.write("</statements>\n")
            return
        if (self.Tokenize.token_type() != "KEYWORD"):
            raise self.ERROR
        tmp_key = self.Tokenize.keyword()
        if (tmp_key == "IF"):
            self.compile_if()

        elif (tmp_key == "WHILE"):
            self.compile_while()

        elif (tmp_key == "LET"):
            self.compile_let()

        elif (tmp_key == "RETURN"):
            self.compile_return()

        elif (tmp_key == "DO"):
            self.compile_do()

        else:
            raise self.ERROR
        while (self.Tokenize.token_type() == "KEYWORD" and
               self.Tokenize.keyword() in self.IF_WHILE_LET_RET_DO):
            tmp_key = self.Tokenize.keyword()
            if (tmp_key == "IF"):
                self.compile_if()
            elif (tmp_key == "WHILE"):
                self.compile_while()
            elif (tmp_key == "LET"):
                self.compile_let()
            elif (tmp_key == "RETURN"):
                self.compile_return()
            elif (tmp_key == "DO"):
                self.compile_do()

        self.output_stream.write("</statements>\n")

    def compile_do(self) -> None:  # OK
        """Compiles a do statement."""
        self.output_stream.write("<doStatement>\n")
        self.output_stream.write("<keyword> do </keyword>\n")
        if (self.Tokenize.has_more_tokens()):
            self.Tokenize.advance()
        if (self.Tokenize.token_type() != "IDENTIFIER"):
            raise self.ERROR
        self.output_stream.write(f"<identifier> {self.Tokenize.identifier()} "
                                 f"</identifier>\n")
        if (self.Tokenize.has_more_tokens()):
            self.Tokenize.advance()
        if (self.Tokenize.token_type() == "SYMBOL" and self.Tokenize.symbol()
                == "."):
            self.output_stream.write("<symbol> . </symbol>\n")
            if (self.Tokenize.has_more_tokens()):
                self.Tokenize.advance()
            if (self.Tokenize.token_type() != "IDENTIFIER"):
                raise self.ERROR
            self.output_stream.write(f"<identifier> {self.Tokenize.identifier()} "
                                     f"</identifier>\n")
            if (self.Tokenize.has_more_tokens()):
                self.Tokenize.advance()
        if (self.Tokenize.token_type() != "SYMBOL" or self.Tokenize.symbol()
                != "("):
            raise self.ERROR
        self.output_stream.write("<symbol> ( </symbol>\n")
        if (self.Tokenize.has_more_tokens()):
            self.Tokenize.advance()
        self.compile_expression_list()
        if (self.Tokenize.token_type() != "SYMBOL" or
                self.Tokenize.symbol() != ")"):
            raise self.ERROR
        self.output_stream.write("<symbol> ) </symbol>\n")
        if (self.Tokenize.has_more_tokens()):
            self.Tokenize.advance()
        if (self.Tokenize.token_type() != "SYMBOL" or
                self.Tokenize.symbol() != ";"):
            raise self.ERROR
        self.output_stream.write("<symbol> ; </symbol>\n")
        self.output_stream.write("</doStatement>\n")
        if (self.Tokenize.has_more_tokens()):
            self.Tokenize.advance()

    def compile_let(self) -> None:  # OK
        """Compiles a let statement."""
        self.output_stream.write("<letStatement>\n")
        self.output_stream.write("<keyword> let </keyword>\n")
        if (self.Tokenize.has_more_tokens()):
            self.Tokenize.advance()
        if (self.Tokenize.token_type() != "IDENTIFIER"):
            raise self.ERROR
        self.output_stream.write(f"<identifier> {self.Tokenize.identifier()} "
                                 f"</identifier>\n")
        if (self.Tokenize.has_more_tokens()):
            self.Tokenize.advance()
        if (self.Tokenize.token_type() == "SYMBOL" and
                self.Tokenize.symbol() == "["):
            self.output_stream.write("<symbol> [ </symbol>\n")
            if (self.Tokenize.has_more_tokens()):
                self.Tokenize.advance()
            self.compile_expression()
            if (self.Tokenize.token_type() != "SYMBOL" or
                    self.Tokenize.symbol() != "]"):
                raise self.ERROR
            self.output_stream.write("<symbol> ] </symbol>\n")
            if (self.Tokenize.has_more_tokens()):
                self.Tokenize.advance()
        if (self.Tokenize.token_type() != "SYMBOL" or
                self.Tokenize.symbol() != "="):
            raise self.ERROR
        self.output_stream.write("<symbol> = </symbol>\n")
        if (self.Tokenize.has_more_tokens()):
            self.Tokenize.advance()
        self.compile_expression()
        if (self.Tokenize.token_type() != "SYMBOL" or
                self.Tokenize.symbol() != ";"):
            raise self.ERROR
        self.output_stream.write("<symbol> ; </symbol>\n")
        if (self.Tokenize.has_more_tokens()):
            self.Tokenize.advance()
        self.output_stream.write("</letStatement>\n")

    def compile_while(self) -> None:  # OK
        """Compiles a while statement."""
        # Your code goes here!
        self.output_stream.write("<whileStatement>\n")
        self.output_stream.write("<keyword> while </keyword>\n")
        if (self.Tokenize.has_more_tokens()):
            self.Tokenize.advance()
        if (self.Tokenize.token_type() != "SYMBOL" or self.Tokenize.symbol()
                != "("):
            raise self.ERROR
        self.output_stream.write("<symbol> ( </symbol>\n")
        if (self.Tokenize.has_more_tokens()):
            self.Tokenize.advance()
        self.compile_expression()
        if (self.Tokenize.token_type() != "SYMBOL" or self.Tokenize.symbol()
                != ")"):
            raise self.ERROR
        self.output_stream.write("<symbol> ) </symbol>\n")
        if (self.Tokenize.has_more_tokens()):
            self.Tokenize.advance()
        if (self.Tokenize.token_type() != "SYMBOL" or self.Tokenize.symbol()
                != "{"):
            raise self.ERROR
        self.output_stream.write("<symbol> { </symbol>\n")
        if (self.Tokenize.has_more_tokens()):
            self.Tokenize.advance()
        self.compile_statements()
        if (self.Tokenize.token_type() != "SYMBOL" or self.Tokenize.symbol()
                != "}"):
            raise "Grammar error !"
        self.output_stream.write("<symbol> } </symbol>\n")
        self.output_stream.write("</whileStatement>\n")
        if (self.Tokenize.has_more_tokens()):
            self.Tokenize.advance()

    def compile_return(self) -> None:  # OK
        """Compiles a return statement."""
        self.output_stream.write("<returnStatement>\n")
        self.output_stream.write("<keyword> return </keyword>\n")
        if (self.Tokenize.has_more_tokens()):
            self.Tokenize.advance()
        if (self.Tokenize.symbol() != ";"):
            self.compile_expression()
        if (self.Tokenize.symbol() != ";"):
            raise self.ERROR
        self.output_stream.write("<symbol> ; </symbol>\n")
        self.output_stream.write("</returnStatement>\n")
        if (self.Tokenize.has_more_tokens()):
            self.Tokenize.advance()

    def compile_if(self) -> None:  # OK
        """Compiles a if statement, possibly with a trailing else clause."""
        self.output_stream.write("<ifStatement>\n")
        self.output_stream.write("<keyword> if </keyword>\n")
        if (self.Tokenize.has_more_tokens()):
            self.Tokenize.advance()
        if (self.Tokenize.token_type() != "SYMBOL" or self.Tokenize.symbol()
                != "("):
            raise self.ERROR
        self.output_stream.write("<symbol> ( </symbol>\n")
        if (self.Tokenize.has_more_tokens()):
            self.Tokenize.advance()
        self.compile_expression()
        if (self.Tokenize.token_type() != "SYMBOL" or self.Tokenize.symbol()
                != ")"):
            raise self.ERROR
        self.output_stream.write("<symbol> ) </symbol>\n")
        if (self.Tokenize.has_more_tokens()):
            self.Tokenize.advance()
        self.output_stream.write("<symbol> { </symbol>\n")
        if (self.Tokenize.has_more_tokens()):
            self.Tokenize.advance()
        self.compile_statements()
        if (self.Tokenize.token_type() != "SYMBOL" or self.Tokenize.symbol()
                != "}"):
            raise self.ERROR
        self.output_stream.write("<symbol> } </symbol>\n")
        if (self.Tokenize.has_more_tokens()):
            self.Tokenize.advance()
        # check else
        if (self.Tokenize.token_type() == "KEYWORD" and
                    self.Tokenize.keyword() == "ELSE"):
            self.output_stream.write("<keyword> else </keyword>\n")
            if (self.Tokenize.has_more_tokens()):
                self.Tokenize.advance()
            if (self.Tokenize.token_type() != "SYMBOL" or
                    self.Tokenize.symbol() != "{"):
                raise self.ERROR
            self.output_stream.write("<symbol> { </symbol>\n")
            if (self.Tokenize.has_more_tokens()):
                self.Tokenize.advance()
            self.compile_statements()
            if (self.Tokenize.token_type() != "SYMBOL" or
                    self.Tokenize.symbol() != "}"):
                raise self.ERROR
            self.output_stream.write("<symbol> } </symbol>\n")
            if (self.Tokenize.has_more_tokens()):
                self.Tokenize.advance()

        self.output_stream.write("</ifStatement>\n")

    def compile_expression(self) -> None:  # OK
        # we call when it should be an
        # expression and this function also checks it.
        """Compiles an expression."""
        all_op = ['+', '-', '*', '/', '&', '|', '<', '>', '=']
        self.output_stream.write("<expression>\n")
        self.compile_term()
        while (self.Tokenize.token_type() == "SYMBOL" and
               self.Tokenize.symbol() in all_op):
            tmp_symbol = self.Tokenize.symbol()
            if (self.Tokenize.symbol() in self.opDict):
                tmp_symbol = self.opDict[tmp_symbol]
            self.output_stream.write(f"<symbol> {tmp_symbol} "
                                     f"</symbol>\n")
            if (self.Tokenize.has_more_tokens()):
                self.Tokenize.advance()
            self.compile_term()
        self.output_stream.write("</expression>\n")

    def compile_term(self) -> None:
        """Compiles a term. 
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        self.output_stream.write("<term>\n")
        keywordConstant = ["TRUE", "FALSE", "NULL", "THIS"]
        op = ['+', '-', '*', '/', '&', '|', '>', '<', '=']
        unary_op = ['-', '~']
        if (self.Tokenize.token_type() == "SYMBOL" and
                (self.Tokenize.symbol() in op or self.Tokenize.symbol() in
                 unary_op )):
            self.output_stream.write(f"<symbol> {self.Tokenize.symbol()} "
                                     f"</symbol>\n")
            if (self.Tokenize.has_more_tokens()):
                self.Tokenize.advance()
            self.compile_term()
            self.output_stream.write("</term>\n")
            return
        tmp_type = self.Tokenize.token_type()
        if (tmp_type == "SYMBOL" and self.Tokenize.symbol() == '('):
            self.output_stream.write(f"<symbol> ( </symbol>\n")
            if (self.Tokenize.has_more_tokens()):
                self.Tokenize.advance()
            self.compile_expression()
            if (tmp_type != "SYMBOL" or self.Tokenize.symbol() != ')'):
                raise self.ERROR
            self.output_stream.write(f"<symbol> ) </symbol>\n")

        if (
                tmp_type == "KEYWORD" and self.Tokenize.keyword() in keywordConstant):
            self.output_stream.write(
                f"<keyword> {self.Tokenize.keyword().lower()} </keyword>\n")

        if (tmp_type == "INT_CONST"):
            self.output_stream.write(
                f"<integerConstant> {str(self.Tokenize.int_val())} "
                "</integerConstant>\n")
        if (tmp_type == "STRING_CONST"):
            self.output_stream.write(
                f"<stringConstant> {self.Tokenize.string_val()[1:-1]} "
                "</stringConstant>\n")

        if (self.Tokenize.token_type() == "IDENTIFIER"):
            tmp = self.Tokenize.identifier()
            if (self.Tokenize.has_more_tokens()):
                self.Tokenize.advance()
            if (self.Tokenize.token_type() != "SYMBOL"):
                raise self.ERROR
            next_tok = self.Tokenize.symbol()
            if (next_tok == "["):
                self.output_stream.write(
                    f"<identifier> {tmp} </identifier>\n")
                self.output_stream.write(f"<symbol> [ </symbol>\n")
                if (self.Tokenize.has_more_tokens()):
                    self.Tokenize.advance()
                self.compile_expression()
                if (
                        self.Tokenize.token_type() != "SYMBOL" or self.Tokenize.symbol()
                        != "]"):
                    raise self.ERROR
                self.output_stream.write("<symbol> ] </symbol>\n")
            elif (next_tok == "("):
                self.output_stream.write(
                    f"<identifier> {tmp} </identifier>\n")
                self.output_stream.write(f"<symbol> ( </symbol>\n")
                if (self.Tokenize.has_more_tokens()):
                    self.Tokenize.advance()
                self.compile_expression_list()
                if (
                        self.Tokenize.token_type() != "SYMBOL" or self.Tokenize.symbol()
                        != ")"):
                    raise self.ERROR
                self.output_stream.write("<symbol> ) </symbol>\n")

            elif (next_tok == "."):
                self.output_stream.write(
                    f"<identifier> {tmp} </identifier>\n")
                self.output_stream.write("<symbol> . </symbol>\n")
                if (self.Tokenize.has_more_tokens()):
                    self.Tokenize.advance()
                if (self.Tokenize.token_type() != "IDENTIFIER"):
                    raise self.ERROR
                self.output_stream.write(
                    f"<identifier> {self.Tokenize.identifier()}"
                    f" </identifier>\n")
                if (self.Tokenize.has_more_tokens()):
                    self.Tokenize.advance()
                if (self.Tokenize.token_type() != "SYMBOL" or
                        self.Tokenize.symbol() != "("):
                    raise self.ERROR
                self.output_stream.write("<symbol> ( </symbol>\n")
                if (self.Tokenize.has_more_tokens()):
                    self.Tokenize.advance()
                self.compile_expression_list()
                if (self.Tokenize.token_type() != "SYMBOL" or
                        self.Tokenize.symbol() != ")"):
                    raise self.ERROR
                self.output_stream.write("<symbol> ) </symbol>\n")
            else:
                self.output_stream.write(
                    f"<identifier> {tmp} </identifier>\n")
                self.output_stream.write("</term>\n")
                return
        if (self.Tokenize.has_more_tokens()):
            self.Tokenize.advance()
        self.output_stream.write("</term>\n")

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        self.output_stream.write("<expressionList>\n")
        while (self.Tokenize.token_type() != "SYMBOL" or
                self.Tokenize.symbol() != ")"):
            self.compile_expression()
            while (self.Tokenize.token_type() == "SYMBOL" and
                   self.Tokenize.symbol() == ','):
                self.output_stream.write("<symbol> , </symbol>\n")
                if (self.Tokenize.has_more_tokens()):
                    self.Tokenize.advance()
                self.compile_expression()
        self.output_stream.write("</expressionList>\n")
