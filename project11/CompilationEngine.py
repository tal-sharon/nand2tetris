"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import JackTokenizer
from SymbolTable import SymbolTable
from VMWriter import VMWriter


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

        self.VMwriter = VMWriter(output_stream)
        self.symbol_table = SymbolTable()
        self.argument_num = 0
        self.if_counter = 0
        self.while_counter = 0

        self.SUBROUTINE = ["METHOD", "FUNCTION", "CONSTRUCTOR"]
        self.TYPE = ["INT", "CHAR", "BOOLEAN"]
        self.TOKEN_TYPE = ["INT", "CHAR", "BOOLEAN"]
        self.class_names = []
        self.ERROR = "ERROR"
        self.IF_WHILE_LET_RET_DO = ["IF", "WHILE", "LET", "RETURN", "DO"]
        self.Tokenize = input_stream
        self.output_stream = output_stream
        self.opDict = {'<': '&lt;', '>': '&gt;', '"': '&quot;', '&': '&amp;'}

    def compile_class(self) -> None:  # OK VM
        """Compiles a complete class."""
        if (self.Tokenize.token_type() != "KEYWORD" or self.Tokenize.keyword()
                != 'CLASS'):
            raise self.ERROR
        # self.output_stream.write("// class \n")
        if self.Tokenize.has_more_tokens():
            self.Tokenize.advance()
        if self.Tokenize.token_type() != "IDENTIFIER":
            raise self.ERROR

        self.class_names.append(self.Tokenize.identifier())
        if self.Tokenize.has_more_tokens():
            self.Tokenize.advance()
        if (self.Tokenize.token_type() != "SYMBOL" or self.Tokenize.symbol()
                != "{"):
            raise self.ERROR
        if self.Tokenize.has_more_tokens():
            self.Tokenize.advance()

        while (self.Tokenize.token_type() == "KEYWORD" and
               (self.Tokenize.keyword() == "FIELD" or self.Tokenize.keyword()
                == "STATIC")):
            self.compile_class_var_dec()
        while (self.Tokenize.token_type() == "KEYWORD" and
               self.Tokenize.keyword() in self.SUBROUTINE):
            self.compile_subroutine()

        if (self.Tokenize.token_type() != "SYMBOL" or
                self.Tokenize.symbol() != "}"):
            raise self.ERROR

    def compile_class_var_dec(self) -> None:  # OK VM
        """Compiles a static declaration or a field declaration."""
        # self.output_stream.write("// classVarDec\n")
        kind_of_var = self.Tokenize.keyword().upper()
        if self.Tokenize.has_more_tokens():
            self.Tokenize.advance()
        if (self.Tokenize.token_type() != "KEYWORD" and
                self.Tokenize.token_type() != "IDENTIFIER"):
            raise self.ERROR
        if self.Tokenize.token_type() == "KEYWORD":
            type_of_var = self.Tokenize.keyword().upper()
        else:
            type_of_var = self.Tokenize.identifier()
        if self.Tokenize.has_more_tokens():
            self.Tokenize.advance()
        if self.Tokenize.token_type() != "IDENTIFIER":
            raise self.ERROR
        name_of_var = self.Tokenize.identifier()
        self.symbol_table.define(name_of_var, type_of_var, kind_of_var)

        if self.Tokenize.has_more_tokens():
            self.Tokenize.advance()
        while (self.Tokenize.token_type() == "SYMBOL" and
               self.Tokenize.symbol() == ","):
            if self.Tokenize.has_more_tokens():
                self.Tokenize.advance()
            if self.Tokenize.token_type() != "IDENTIFIER":
                raise self.ERROR
            name_of_var = self.Tokenize.identifier()
            self.symbol_table.define(name_of_var, type_of_var, kind_of_var)
            if self.Tokenize.has_more_tokens():
                self.Tokenize.advance()
        if (self.Tokenize.token_type() != "SYMBOL" or self.Tokenize.symbol()
                != ";"):
            raise self.ERROR
        if self.Tokenize.has_more_tokens():
            self.Tokenize.advance()

    def compile_subroutine(self) -> None:  # OK VM

        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        self.if_counter = 0
        self.while_counter = 0

        subroutine_type = self.Tokenize.keyword()

        # self.output_stream.write("// subroutineDec \n")
        self.symbol_table.start_subroutine()
        # ADD THIS IN THE START to symbol table !
        if self.Tokenize.keyword() == "METHOD":
            self.symbol_table.define("this", self.class_names[0], "ARG")

        if self.Tokenize.has_more_tokens():
            self.Tokenize.advance()
        if (self.Tokenize.token_type() != "KEYWORD" and
                self.Tokenize.token_type() != "IDENTIFIER"):
            raise self.ERROR
        # solve void identifier problem.

        if self.Tokenize.has_more_tokens():
            self.Tokenize.advance()
        if self.Tokenize.token_type() != "IDENTIFIER":
            raise self.ERROR
        function_name = self.class_names[0] + "." + self.Tokenize.identifier()
        if self.Tokenize.has_more_tokens():
            self.Tokenize.advance()
        if (self.Tokenize.token_type() != "SYMBOL" or self.Tokenize.symbol()
                != "("):
            raise self.ERROR
        if self.Tokenize.has_more_tokens():
            self.Tokenize.advance()
        self.compile_parameter_list()

        if self.Tokenize.has_more_tokens():
            self.Tokenize.advance()

        # self.output_stream.write("// subroutineBody\n")
        if (self.Tokenize.token_type() != "SYMBOL" or
                self.Tokenize.symbol() != "{"):
            raise self.ERROR
        if self.Tokenize.has_more_tokens():
            self.Tokenize.advance()

        self.argument_num = 0
        while (self.Tokenize.token_type() == "KEYWORD" and
               self.Tokenize.keyword() == "VAR"):
            self.compile_var_dec()

        self.VMwriter.write_function(function_name, self.argument_num)

        if subroutine_type == "METHOD":
            self.VMwriter.write_push("ARG", 0)
            self.VMwriter.write_pop("POINTER", 0)

        # alloc memory ! page 235 in book
        # Watch for "FIELD" >= 0 ?
        if subroutine_type == "CONSTRUCTOR":
            self.VMwriter.write_push("CONST",
                                     self.symbol_table.var_count("FIELD") + 1)
            self.VMwriter.write_call("Memory.alloc", 1)
            self.VMwriter.write_pop("POINTER", 0)

        self.compile_statements()
        if (self.Tokenize.token_type() != "SYMBOL" or
                self.Tokenize.symbol() != "}"):
            raise self.ERROR
        if self.Tokenize.has_more_tokens():
            self.Tokenize.advance()

    def compile_parameter_list(self) -> None:  # OK VM
        """Compiles a (possibly empty) parameter list, not including the
        enclosing "()".
        """
        # self.output_stream.write("// parameterList\n")
        kind_of_var = "ARG"

        if (self.Tokenize.token_type() != "SYMBOL" or
                self.Tokenize.symbol() != ")"):
            if (self.Tokenize.token_type() != "KEYWORD" and
                    self.Tokenize.token_type() != "IDENTIFIER"):
                raise self.ERROR

            while (self.Tokenize.token_type() != "KEYWORD" or
                   self.Tokenize.token_type() != "IDENTIFIER"):

                if self.Tokenize.token_type() == "KEYWORD":
                    type_of_var = self.Tokenize.keyword().lower()
                else:
                    type_of_var = self.Tokenize.identifier()
                if self.Tokenize.has_more_tokens():
                    self.Tokenize.advance()
                if self.Tokenize.token_type() != "IDENTIFIER":
                    raise self.ERROR
                name_of_var = self.Tokenize.identifier()
                self.symbol_table.define(name_of_var, type_of_var,
                                         kind_of_var)
                if self.Tokenize.has_more_tokens():
                    self.Tokenize.advance()
                if (self.Tokenize.token_type() != "SYMBOL" or
                        (self.Tokenize.symbol() != "," and
                         self.Tokenize.symbol() != ")")):
                    raise self.ERROR
                if self.Tokenize.symbol() != ",":
                    break
                if self.Tokenize.has_more_tokens():
                    self.Tokenize.advance()

    def compile_var_dec(self) -> None:  # OK VM
        """Compiles a var declaration."""
        # self.output_stream.write("// varDec \n")
        kind_of_var = "VAR"
        self.argument_num += 1
        if self.Tokenize.has_more_tokens():
            self.Tokenize.advance()
        if (self.Tokenize.token_type() != "KEYWORD" and
                self.Tokenize.token_type() != "IDENTIFIER"):
            raise self.ERROR
        if self.Tokenize.token_type() == "KEYWORD":
            type_of_var = self.Tokenize.keyword().lower()
        else:
            type_of_var = self.Tokenize.identifier()
        if self.Tokenize.has_more_tokens():
            self.Tokenize.advance()
        if self.Tokenize.token_type() != "IDENTIFIER":
            raise self.ERROR
        name_of_var = self.Tokenize.identifier()
        self.symbol_table.define(name_of_var, type_of_var,
                                 kind_of_var)
        if self.Tokenize.has_more_tokens():
            self.Tokenize.advance()
        while (self.Tokenize.token_type() == "SYMBOL" and
               self.Tokenize.symbol() == ","):
            self.argument_num += 1
            if self.Tokenize.has_more_tokens():
                self.Tokenize.advance()
            if self.Tokenize.token_type() != "IDENTIFIER":
                raise self.ERROR
            name_of_var = self.Tokenize.identifier()
            self.symbol_table.define(name_of_var, type_of_var,
                                     kind_of_var)
            if self.Tokenize.has_more_tokens():
                self.Tokenize.advance()

        if (self.Tokenize.token_type() != "SYMBOL" or
                self.Tokenize.symbol() != ';'):
            raise self.ERROR
        if self.Tokenize.has_more_tokens():
            self.Tokenize.advance()

    def compile_statements(self) -> None:  # OK VM
        """Compiles a sequence of statements, not including the enclosing
        "{}".
        """
        # self.output_stream.write("// statements\n")
        if (self.Tokenize.token_type() == "SYMBOL" and
                self.Tokenize.symbol() == "}"):
            return
        if self.Tokenize.token_type() != "KEYWORD":
            raise self.ERROR
        tmp_key = self.Tokenize.keyword()
        if tmp_key == "IF":
            self.compile_if()

        elif tmp_key == "WHILE":
            self.compile_while()

        elif tmp_key == "LET":
            self.compile_let()

        elif tmp_key == "RETURN":
            self.compile_return()

        elif tmp_key == "DO":
            self.compile_do()

        else:
            raise self.ERROR
        while (self.Tokenize.token_type() == "KEYWORD" and
               self.Tokenize.keyword() in self.IF_WHILE_LET_RET_DO):
            tmp_key = self.Tokenize.keyword()
            if tmp_key == "IF":
                self.compile_if()
            elif tmp_key == "WHILE":
                self.compile_while()
            elif tmp_key == "LET":
                self.compile_let()
            elif tmp_key == "RETURN":
                self.compile_return()
            elif tmp_key == "DO":
                self.compile_do()

    def compile_do(self) -> None:  # OK VM
        """Compiles a do statement."""
        # self.output_stream.write("// doStatement\n")
        push_this = 0
        if self.Tokenize.has_more_tokens():
            self.Tokenize.advance()
        if self.Tokenize.token_type() != "IDENTIFIER":
            raise self.ERROR

        name = self.Tokenize.identifier()
        function_name = self.Tokenize.identifier()
        class_name = self.symbol_table.type_of(name)
        segment = self.symbol_table.kind_of(name)
        if segment == "FIELD":
            segment = "THIS"
        elif segment == "VAR":
            segment = "LOCAL"
        # else segment is "STATIC" or "ARG"
        elif segment is None:
            segment = "POINTER"
        if segment == "POINTER":
            index = 0
        else:
            index = self.symbol_table.index_of(name)
            self.VMwriter.write_push(segment, index)

        if self.Tokenize.has_more_tokens():
            self.Tokenize.advance()

        if (self.Tokenize.token_type() == "SYMBOL" and self.Tokenize.symbol()
                == "."):
            if self.Tokenize.has_more_tokens():
                self.Tokenize.advance()
            if self.Tokenize.token_type() != "IDENTIFIER":
                raise self.ERROR
            if class_name is None:
                class_name = function_name
            else:
                push_this = 1

            function_name = self.Tokenize.identifier()
            if self.Tokenize.has_more_tokens():
                self.Tokenize.advance()
        else:
            class_name = self.class_names[
                0]  # this list always filled with class's name
            self.VMwriter.write_push("POINTER", 0)
            push_this = 1

        if (self.Tokenize.token_type() != "SYMBOL" or self.Tokenize.symbol()
                != "("):
            raise self.ERROR
        if self.Tokenize.has_more_tokens():
            self.Tokenize.advance()

        self.compile_expression_list()  # pushes all args to stack and counts them
        if (self.Tokenize.token_type() != "SYMBOL" or
                self.Tokenize.symbol() != ")"):
            raise self.ERROR

        self.VMwriter.write_call(f"{class_name}.{function_name}",
                                 self.argument_num + push_this)  # WHY + 1?
        self.VMwriter.write_pop("TEMP",
                                0)  # "do" does not assign function's return value to any variable.

        if self.Tokenize.has_more_tokens():
            self.Tokenize.advance()
        if (self.Tokenize.token_type() != "SYMBOL" or
                self.Tokenize.symbol() != ";"):
            raise self.ERROR

        if self.Tokenize.has_more_tokens():
            self.Tokenize.advance()

    def compile_let(self) -> None:  # OK VM
        """Compiles a let statement."""
        # self.output_stream.write("// letStatement\n")
        if self.Tokenize.has_more_tokens():
            self.Tokenize.advance()
        if self.Tokenize.token_type() != "IDENTIFIER":
            raise self.ERROR

        identifier_name = self.Tokenize.identifier()
        if self.Tokenize.has_more_tokens():
            self.Tokenize.advance()

        segment = self.symbol_table.kind_of(identifier_name)
        if segment == "FIELD":
            segment = "THIS"
        elif segment == "VAR":
            segment = "LOCAL"
        # else segment is "STATIC" or "ARG"
        index = self.symbol_table.index_of(identifier_name)

        is_array = False
        if (self.Tokenize.token_type() == "SYMBOL" and
                self.Tokenize.symbol() == "["):
            is_array = True
            if self.Tokenize.has_more_tokens():
                self.Tokenize.advance()

            self.compile_expression()  # expression value is pushed onto top of the stack
            self.VMwriter.write_push(segment,
                                     index)  # push array's memory location to stack
            self.VMwriter.write_arithmetic(
                "ADD")  # top of stack is the designated variable

            if (self.Tokenize.token_type() != "SYMBOL" or
                    self.Tokenize.symbol() != "]"):
                raise self.ERROR
            if self.Tokenize.has_more_tokens():
                self.Tokenize.advance()
        if (self.Tokenize.token_type() != "SYMBOL" or
                self.Tokenize.symbol() != "="):
            raise self.ERROR
        if self.Tokenize.has_more_tokens():
            self.Tokenize.advance()

        self.compile_expression()
        if is_array:  # instructions are on page 240 of the book (figure 11.12)
            self.VMwriter.write_pop("TEMP", 0)
            self.VMwriter.write_pop("POINTER", 1)
            self.VMwriter.write_push("TEMP", 0)
            self.VMwriter.write_pop("THAT", 0)
        else:
            self.VMwriter.write_pop(segment, index)

        if (self.Tokenize.token_type() != "SYMBOL" or
                self.Tokenize.symbol() != ";"):
            raise self.ERROR
        if self.Tokenize.has_more_tokens():
            self.Tokenize.advance()

    def compile_while(self) -> None:  # OK VM
        """Compiles a while statement."""
        # Your code goes here!
        # self.output_stream.write("// whileStatement\n")
        label1 = f"WHILE_EXP{self.while_counter}"
        label2 = f"WHILE_END{self.while_counter}"
        self.while_counter += 1

        self.VMwriter.write_label(label1)  # start of while loop

        if self.Tokenize.has_more_tokens():
            self.Tokenize.advance()
        if (self.Tokenize.token_type() != "SYMBOL" or self.Tokenize.symbol()
                != "("):
            raise self.ERROR
        if self.Tokenize.has_more_tokens():
            self.Tokenize.advance()

        # if cond is false exit while loop go to label2
        # else continue with the loop
        self.compile_expression()
        self.VMwriter.write_arithmetic("NOT")
        self.VMwriter.write_if(label2)

        if (self.Tokenize.token_type() != "SYMBOL" or self.Tokenize.symbol()
                != ")"):
            raise self.ERROR
        if self.Tokenize.has_more_tokens():
            self.Tokenize.advance()
        if (self.Tokenize.token_type() != "SYMBOL" or self.Tokenize.symbol()
                != "{"):
            raise self.ERROR
        if self.Tokenize.has_more_tokens():
            self.Tokenize.advance()
        self.compile_statements()
        if (self.Tokenize.token_type() != "SYMBOL" or self.Tokenize.symbol()
                != "}"):
            raise self.ERROR

        self.VMwriter.write_goto(label1)  # go to beginning of loop
        self.VMwriter.write_label(label2)  # end of loop after exit

        if self.Tokenize.has_more_tokens():
            self.Tokenize.advance()

    def compile_return(self) -> None:  # OK VM
        """Compiles a return statement."""
        # self.output_stream.write("// return Statement \n")
        if self.Tokenize.has_more_tokens():
            self.Tokenize.advance()
        if self.Tokenize.symbol() != ";":
            self.compile_expression()  # Should push the value.
        else:
            self.VMwriter.write_push("CONST", 0)
        if self.Tokenize.symbol() != ";":
            raise self.ERROR
        self.VMwriter.write_return()
        if self.Tokenize.has_more_tokens():
            self.Tokenize.advance()

    def compile_if(self) -> None:  # OK VM
        """Compiles a if statement, possibly with a trailing else clause."""
        # self.output_stream.write("// ifStatement\n")
        if_true_label = f"IF_TRUE{self.if_counter}"
        if_false_label = f"IF_FALSE{self.if_counter}"
        if_end_label = f"IF_END{self.if_counter}"
        self.if_counter += 1

        if self.Tokenize.has_more_tokens():
            self.Tokenize.advance()
        if (self.Tokenize.token_type() != "SYMBOL" or self.Tokenize.symbol()
                != "("):
            raise self.ERROR
        if self.Tokenize.has_more_tokens():
            self.Tokenize.advance()

        # if condition is not true go to "else" (label1),
        # otherwise go into the "if" and then go after the "else" (label2)

        self.compile_expression()
        # self.VMwriter.write_arithmetic("NOT")
        self.VMwriter.write_if(if_true_label)
        self.VMwriter.write_goto(if_false_label)
        self.VMwriter.write_label(if_true_label)

        if (self.Tokenize.token_type() != "SYMBOL" or self.Tokenize.symbol()
                != ")"):
            raise self.ERROR
        if self.Tokenize.has_more_tokens():
            self.Tokenize.advance()
        if self.Tokenize.has_more_tokens():
            self.Tokenize.advance()
        self.compile_statements()
        if (self.Tokenize.token_type() != "SYMBOL" or self.Tokenize.symbol()
                != "}"):
            raise self.ERROR
        if self.Tokenize.has_more_tokens():
            self.Tokenize.advance()

        # check else
        if self.Tokenize.keyword() == "ELSE":
            self.VMwriter.write_goto(if_end_label)
        self.VMwriter.write_label(if_false_label)
        if (self.Tokenize.token_type() == "KEYWORD" and
                self.Tokenize.keyword() == "ELSE"):
            if self.Tokenize.has_more_tokens():
                self.Tokenize.advance()
            if (self.Tokenize.token_type() != "SYMBOL" or
                    self.Tokenize.symbol() != "{"):
                raise self.ERROR
            if self.Tokenize.has_more_tokens():
                self.Tokenize.advance()
            self.compile_statements()
            if (self.Tokenize.token_type() != "SYMBOL" or
                    self.Tokenize.symbol() != "}"):
                raise self.ERROR
            if self.Tokenize.has_more_tokens():
                self.Tokenize.advance()
            # if self.Tokenize.keyword() == "ELSE":
            self.VMwriter.write_label(if_end_label)

    def compile_expression(self) -> None:  # OK VM
        # we call when it should be an
        # expression and this function also checks it.
        """Compiles an expression."""
        all_op = ['+', '-', '*', '/', '&', '|', '<', '>', '=', '^', '#']
        translate_dict = {"+": "ADD", "-": "SUB", "=": "EQ", ">": "GT",
                          "<": "LT",
                          "&": "AND", "|": "OR", "^": "SHIFTLEFT",
                          "#": "SHIFTRIGHT"}
        # self.output_stream.write("// expression\n")
        self.compile_term()
        while (self.Tokenize.token_type() == "SYMBOL" and
               self.Tokenize.symbol() in all_op):
            tmp_symbol = self.Tokenize.symbol()
            # if self.Tokenize.symbol() in self.opDict:
            #     tmp_symbol = self.opDict[tmp_symbol]
            if self.Tokenize.has_more_tokens():
                self.Tokenize.advance()
            self.compile_term()
            if tmp_symbol in translate_dict:
                self.VMwriter.write_arithmetic(translate_dict[tmp_symbol])
            elif tmp_symbol == "*":
                self.VMwriter.write_call("Math.multiply", 2)
            elif tmp_symbol == "/":
                self.VMwriter.write_call("Math.divide", 2)

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

        # self.output_stream.write("// term \n")
        keyword_constant = ["TRUE", "FALSE", "NULL", "THIS"]
        op = ['+', '-', '*', '/', '&', '|', '>', '<', '=']
        unary_op = ['-', '~', '^', '#']

        if (self.Tokenize.token_type() == "SYMBOL" and
                (self.Tokenize.symbol() in op or self.Tokenize.symbol() in unary_op)):
            op = self.Tokenize.symbol()
            if self.Tokenize.has_more_tokens():
                self.Tokenize.advance()
            self.compile_term()
            # self.VMwriter.write_arithmetic(str(op))
            if op == '-':
                self.VMwriter.write_arithmetic("NEG")
            if op == '~':
                self.VMwriter.write_arithmetic("NOT")
            if op == '^':
                self.VMwriter.write_arithmetic("SHIFTLEFT")
            if op == '#':
                self.VMwriter.write_arithmetic("SHIFTRIGHT")
            return
        tmp_type = self.Tokenize.token_type()

        # " ( expression ) "
        if tmp_type == "SYMBOL" and self.Tokenize.symbol() == '(':
            if self.Tokenize.has_more_tokens():
                self.Tokenize.advance()
            self.compile_expression()
            if tmp_type != "SYMBOL" or self.Tokenize.symbol() != ')':
                raise self.ERROR

        # " Key Word Constant "
        if tmp_type == "KEYWORD" and self.Tokenize.keyword() in keyword_constant:
            key = self.Tokenize.keyword()
            if key in ["NULL", "FALSE"]:
                self.VMwriter.write_push("CONST", 0)
            elif key == "TRUE":
                self.VMwriter.write_push("CONST", 0)
                self.VMwriter.write_arithmetic("NOT")
            else:
                self.VMwriter.write_push("POINTER", 0)

        # HERE
        if tmp_type == "INT_CONST":
            self.VMwriter.write_push("CONST", self.Tokenize.int_val())

        if tmp_type == "STRING_CONST":
            self.solve_string()

        if self.Tokenize.token_type() == "IDENTIFIER":
            name = self.Tokenize.identifier()
            class_name = self.symbol_table.type_of(name)
            if class_name is None:
                class_name = name
            kind_of = self.symbol_table.kind_of(name)
            index_of = self.symbol_table.index_of(name)
            if kind_of == "FIELD":
                kind_of = "THIS"
            elif kind_of == "VAR":
                kind_of = "LOCAL"
            if self.Tokenize.has_more_tokens():
                self.Tokenize.advance()
            if self.Tokenize.token_type() != "SYMBOL":
                raise self.ERROR
            next_tok = self.Tokenize.symbol()

            if next_tok == "[":
                if self.Tokenize.has_more_tokens():  # handle array
                    self.Tokenize.advance()
                    self.compile_expression()
                    self.VMwriter.write_push(kind_of,
                                             self.symbol_table.index_of(name))
                    self.VMwriter.write_arithmetic("ADD")
                    self.VMwriter.write_pop("POINTER", 1)
                    self.VMwriter.write_push("THAT", 0)

                if self.Tokenize.token_type() != "SYMBOL" or self.Tokenize.symbol() != "]":
                    raise self.ERROR
            elif next_tok == "(":
                if self.Tokenize.has_more_tokens():
                    self.Tokenize.advance()

                self.compile_expression_list()
                if self.Tokenize.token_type() != "SYMBOL" or self.Tokenize.symbol() != ")":
                    raise self.ERROR

            elif next_tok == ".":
                push_this = 0
                if self.Tokenize.has_more_tokens():
                    self.Tokenize.advance()
                if self.Tokenize.token_type() != "IDENTIFIER":
                    raise self.ERROR
                function_to_operate = self.Tokenize.identifier()
                if self.Tokenize.has_more_tokens():
                    self.Tokenize.advance()
                if (self.Tokenize.token_type() != "SYMBOL" or
                        self.Tokenize.symbol() != "("):
                    raise self.ERROR
                if self.Tokenize.has_more_tokens():
                    self.Tokenize.advance()
                if kind_of != None:
                    self.VMwriter.write_push(kind_of,index_of)
                    push_this = 1
                self.compile_expression_list()
                if (self.Tokenize.token_type() != "SYMBOL" or
                        self.Tokenize.symbol() != ")"):
                    raise self.ERROR

                self.VMwriter.write_call(f"{class_name}.{function_to_operate}",
                                         self.argument_num+push_this)

            else:
                self.VMwriter.write_push(kind_of,
                                         self.symbol_table.index_of(name))
                return
        if self.Tokenize.has_more_tokens():
            self.Tokenize.advance()

    def compile_expression_list(self) -> None:  # OK VM
        """Compiles a (possibly empty) comma-separated list of expressions."""
        self.argument_num = 0
        # self.output_stream.write("// expressionList\n")
        while (self.Tokenize.token_type() != "SYMBOL" or
               self.Tokenize.symbol() != ")"):
            self.compile_expression()
            self.argument_num += 1
            while (self.Tokenize.token_type() == "SYMBOL" and
                   self.Tokenize.symbol() == ','):
                self.argument_num += 1
                if self.Tokenize.has_more_tokens():
                    self.Tokenize.advance()
                tmp = self.argument_num
                self.compile_expression()
                self.argument_num = tmp

    def solve_string(self):
        # minus 2 for the ""
        self.VMwriter.write_push("CONST", len(self.Tokenize.string_val()) - 2)
        self.VMwriter.write_call("String.new", 1)
        for char in self.Tokenize.string_val()[1:-1]:
            self.VMwriter.write_push("CONST", ord(char))
            self.VMwriter.write_call("String.appendChar", 2)
