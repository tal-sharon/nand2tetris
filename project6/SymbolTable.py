RESERVED_MEM_LEN = 16
SCREEN_ADDRESS = 16384
KBD_ADDRESS = 24576


"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""


class SymbolTable:
    """
    A symbol table that keeps a correspondence between symbolic labels and 
    numeric addresses.
    """

    def __init__(self) -> None:
        """Creates a new symbol table initialized with all the predefined symbols
        and their pre-allocated RAM addresses, according to section 6.2.3 of the
        book.
        """
        self._table = dict()
        self._init_table()

    def _init_table(self) -> None:
        for address in range(RESERVED_MEM_LEN):
            symbol = "R"+str(address)
            self._table[symbol] = address
        self._table["SCREEN"] = SCREEN_ADDRESS
        self._table["KBD"] = KBD_ADDRESS
        self._table["SP"] = 0
        self._table["LCL"] = 1
        self._table["ARG"] = 2
        self._table["THIS"] = 3
        self._table["THAT"] = 4

    def add_entry(self, symbol: str, address: int) -> None:
        """Adds the pair (symbol, address) to the table.

        Args:
            symbol (str): the symbol to add.
            address (int): the address corresponding to the symbol.
        """
        self._table[symbol] = address

    def contains(self, symbol: str) -> bool:
        """Does the symbol table contain the given symbol?

        Args:
            symbol (str): a symbol.

        Returns:
            bool: True if the symbol is contained, False otherwise.
        """
        return symbol in self._table.keys()

    def get_address(self, symbol: str) -> int:
        """Returns the address associated with the symbol.

        Args:
            symbol (str): a symbol.

        Returns:
            int: the address associated with the symbol.
        """
        return self._table[symbol]
