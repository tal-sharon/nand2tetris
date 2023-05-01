"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import re


class Parser:
    """
    # Parser
    
    Handles the parsing of a single .vm file, and encapsulates access to the
    input code. It reads VM commands, parses them, and provides convenient 
    access to their components. 
    In addition, it removes all white space and comments.

    ## VM Language Specification

    A .vm file is a stream of characters. If the file represents a
    valid program, it can be translated into a stream of valid assembly 
    commands. VM commands may be separated by an arbitrary number of whitespace
    characters and comments, which are ignored. Comments begin with "//" and
    last until the line’s end.
    The different parts of each VM command may also be separated by an arbitrary
    number of non-newline whitespace characters.

    - Arithmetic commands:
      - add, sub, and, or, eq, gt, lt
      - neg, not, shiftleft, shiftright
    - Memory segment manipulation:
      - push <segment> <number>
      - pop <segment that is not constant> <number>
      - <segment> can be any of: argument, local, static, constant, this, that, 
                                 pointer, temp
    - Branching (only relevant for project 8):
      - label <label-name>
      - if-goto <label-name>
      - goto <label-name>
      - <label-name> can be any combination of non-whitespace characters.
    - Functions (only relevant for project 8):
      - call <function-name> <n-args>
      - function <function-name> <n-vars>
      - return
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Gets ready to parse the input file.

        Args:
            input_file (typing.TextIO): input file.
        """
        # Your code goes here!
        # A good place to start is to read all the lines of the input:
        # input_lines = input_file.read().splitlines()
        self._input_lines = []
        input_file.seek(0)
        for line in input_file.read().splitlines():
            line = re.sub(r"[\n\t]*", "", line)
            line = line.split("/")[0]
            if line and not line[0] == "/":
                self._input_lines.append(line)

        self._line_num = -1
        self._cur_inst = ""
        self.cur_cmd = None
        self.argument1 = None
        self.argument2 = None

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?
        Returns:
            bool: True if there are more commands, False otherwise.
        """
        return self._line_num < len(self._input_lines)

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current
        command. Should be called only if has_more_commands() is true. Initially
        there is no current command.
        """
        group_c = ["C_PUSH", "C_POP", "C_FUNCTION", "C_CALL"]
        self._line_num += 1
        if not self.has_more_commands():
            return
        self._cur_inst = self._input_lines[self._line_num]
        cmd = self.command_type()
        self.cur_cmd = self._cur_inst
        if cmd == "C_ARITHMETIC":
            self.cur_cmd = self._cur_inst.split(" ")[0]
            return
        self.argument1 = self._cur_inst.split(" ")[1]
        if cmd not in group_c:
            return
        self.argument2 = self._cur_inst.split(" ")[2]
        return

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current VM command.
            "C_ARITHMETIC" is returned for all arithmetic commands.
            For other commands, can return:
            "C_PUSH", "C_POP", "C_LABEL", "C_GOTO", "C_IF", "C_FUNCTION",
            "C_RETURN", "C_CALL".
        """
        cur_first_part = self._cur_inst.split(" ")[0]
        arithmetic_logical = ["add", "sub", "neg", "eq", "gt", "lt", "and",
                              "or", "not", "shiftleft", "shiftright"]
        if cur_first_part in arithmetic_logical:

            return "C_ARITHMETIC"
        if cur_first_part == "push":

            return "C_PUSH"
        if cur_first_part == "pop":

            return "C_POP"
        # if cur_first_part == "label":
        #     return "C_LABEL"
        # if cur_first_part == "goto":
        #     return "C_GOTO"
        # if cur_first_part == "if-goto":
        #     return "C_IF"
        # if cur_first_part == "function":
        #     return "C_FUNCTION"
        # if cur_first_part == "return":
        #     return "C_RETURN"
        # if cur_first_part == "call":
        #     return "C_CALL"

    def arg1(self) -> str:
        """
        Returns:
            str: the first argument of the current command. In case of
            "C_ARITHMETIC", the command itself (add, sub, etc.) is returned.
            Should not be called if the current command is "C_RETURN".
        """
        return self.argument1

    def arg2(self) -> int:
        """
        Returns:
            int: the second argument of the current command. Should be
            called only if the current command is "C_PUSH", "C_POP",
            "C_FUNCTION" or "C_CALL".
        """
        return int(self.argument2)

    def curcmd(self) -> str:
        """
        curcmd: the current commend of the line.
        :return: curcmd
        """
        return self.cur_cmd
