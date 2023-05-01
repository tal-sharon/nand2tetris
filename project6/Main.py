"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing
from SymbolTable import SymbolTable
from Parser import Parser
from Code import Code


def assemble_file(input_f: typing.TextIO, output_f: typing.TextIO) -> None:
    """Assembles a single file.

    Args:
        input_f (typing.TextIO): the file to assemble.
        output_f (typing.TextIO): writes all output to this file.
    """
    # Your code goes here!
    # A good place to start is to initialize a new Parser object:
    # parser = Parser(input_file)
    # Note that you can write to output_file like so:
    # output_file.write("Hello world! \n")

    parser = Parser(input_f)
    symbol_table = SymbolTable()
    code = Code()
    first_pass(parser, symbol_table)

    parser = Parser(input_f)     # reset parser
    second_pass(parser, symbol_table)

    parser = Parser(input_f)     # reset parser
    third_pass(code, output_f, parser, symbol_table)


def third_pass(code: Code, output_f: typing.TextIO, parser: Parser, symbol_table: SymbolTable) -> None:
    while parser.has_more_commands():
        if parser.command_type() == "A_COMMAND":
            if symbol_table.contains(parser.symbol()):
                address = symbol_table.get_address(parser.symbol())
                output_f.write(f'{int(address):016b}' + '\n')
            else:
                output_f.write(f'{int(parser.symbol()):016b}' + '\n')
        elif parser.command_type() == "C_COMMAND":
            c, d, j = parser.comp(), parser.dest(), parser.jump()
            if "<<" in c or ">>" in c:
                shift = True
            else:
                shift = False
            c, d, j = code.comp(c), code.dest(d), code.jump(j)
            if shift:
                output_f.write('101' + c + d + j + '\n')
            else:
                output_f.write('111' + c + d + j + '\n')
        parser.advance()


def second_pass(parser: Parser, symbol_table: SymbolTable) -> None:
    n = 16
    while parser.has_more_commands():
        if parser.command_type() == "A_COMMAND":
            if not (symbol_table.contains(parser.symbol()) or parser.symbol().isnumeric()):
                symbol_table.add_entry(parser.symbol(), n)
                n += 1
        parser.advance()


def first_pass(parser: Parser, symbol_table: SymbolTable) -> None:
    inst_num = 0
    while parser.has_more_commands():
        if parser.command_type() == "L_COMMAND":
            symbol_table.add_entry(parser.symbol(), inst_num)
        else:
            inst_num += 1
        parser.advance()


if "__main__" == __name__:
    # Parses the input path and calls assemble_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: Assembler <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_assemble = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
    else:
        files_to_assemble = [argument_path]
    for input_path in files_to_assemble:
        filename, extension = os.path.splitext(input_path)
        if extension.lower() != ".asm":
            continue
        output_path = filename + ".hack"
        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            assemble_file(input_file, output_file)
