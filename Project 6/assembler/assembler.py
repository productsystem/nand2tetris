import sys

class Parser:
    def __init__(self, filename):
        with open(filename, 'r') as file:
            self.lines = []
            for line in file:
                if line.strip() and not line.startswith('//'):
                    line_content = line.split('//')[0].strip()
                    self.lines.append(line_content)
        self.current_index = -1

    def has_more_commands(self):
        return self.current_index < len(self.lines) - 1

    def advance(self):
        if self.has_more_commands():
            self.current_index += 1
            self.current_command = self.lines[self.current_index]

    def command_type(self):
        if self.current_command.startswith('@'):
            return 'A_COMMAND'
        elif self.current_command.startswith('(') and self.current_command.endswith(')'):
            return 'L_COMMAND'
        else:
            return 'C_COMMAND'

class Code:
    @staticmethod
    def dest(mnemonic):
        dest_dict = {
            '': '000', 'M': '001', 'D': '010', 'MD': '011',
            'A': '100', 'AM': '101', 'AD': '110', 'AMD': '111'
        }
        return dest_dict.get(mnemonic, '000')

    @staticmethod
    def comp(mnemonic):
        comp_dict = {
            '0': '0101010', '1': '0111111', '-1': '0111010',
            'D': '0001100', 'A': '0110000', '!D': '0001101',
            '!A': '0110001', '-D': '0001111', '-A': '0110011',
            'D+1': '0011111', 'A+1': '0110111', 'D-1': '0001110',
            'A-1': '0110010', 'D+A': '0000010', 'D-A': '0010011',
            'A-D': '0000111', 'D&A': '0000000', 'D|A': '0010101',
            'M': '1110000', '!M': '1110001', '-M': '1110011',
            'M+1': '1110111', 'M-1': '1110010', 'D+M': '1000010',
            'D-M': '1010011', 'M-D': '1000111', 'D&M': '1000000',
            'D|M': '1010101'
        }
        return comp_dict.get(mnemonic, '0101010')

    @staticmethod
    def jump(mnemonic):
        jump_dict = {
            '': '000', 'JGT': '001', 'JEQ': '010', 'JGE': '011',
            'JLT': '100', 'JNE': '101', 'JLE': '110', 'JMP': '111'
        }
        return jump_dict.get(mnemonic, '000')

class SymbolTable:
    def __init__(self):
        self.table = {
            'SP': 0, 'LCL': 1, 'ARG': 2, 'THIS': 3, 'THAT': 4,
            'R0': 0, 'R1': 1, 'R2': 2, 'R3': 3, 'R4': 4, 'R5': 5,
            'R6': 6, 'R7': 7, 'R8': 8, 'R9': 9, 'R10': 10, 'R11': 11,
            'R12': 12, 'R13': 13, 'R14': 14, 'R15': 15, 'SCREEN': 16384, 'KBD': 24576
        }

    def add_entry(self, symbol, address):
        self.table[symbol] = address

    def contains(self, symbol):
        return symbol in self.table

    def get_address(self, symbol):
        return self.table[symbol]


def first_pass(parser, symbol_table):
    line_number = 0
    while parser.has_more_commands():
        parser.advance()
        if parser.command_type() == 'L_COMMAND':
            label = parser.current_command[1:-1]
            symbol_table.add_entry(label, line_number)
        else:
            line_number += 1


def second_pass(parser, symbol_table):
    code_module = Code()
    output_lines = []
    variable_address = 16

    while parser.has_more_commands():
        parser.advance()
        command_type = parser.command_type()

        if command_type == 'A_COMMAND':
            symbol = parser.current_command[1:]
            if symbol.isdigit():
                address = int(symbol)
            else:
                if not symbol_table.contains(symbol):
                    symbol_table.add_entry(symbol, variable_address)
                    variable_address += 1
                address = symbol_table.get_address(symbol)
            output_lines.append(f"0{address:015b}")

        elif command_type == 'C_COMMAND':
            dest = parser.current_command.split('=')[0] if '=' in parser.current_command else ''
            comp_jump = parser.current_command.split('=')[-1]
            comp = comp_jump.split(';')[0]
            jump = comp_jump.split(';')[1] if ';' in comp_jump else ''
            binary_code = (
                '111' +
                code_module.comp(comp) +
                code_module.dest(dest) +
                code_module.jump(jump)
            )
            output_lines.append(binary_code)

    return output_lines


if __name__ == '__main__':
    input_filename = sys.argv[1]
    parser = Parser(input_filename)
    symbol_table = SymbolTable()

    first_pass(parser, symbol_table)

    parser.current_index = -1
    output = second_pass(parser, symbol_table)

    output_filename = input_filename.replace('.asm', '.hack')
    with open(output_filename, 'w') as output_file:
        for line in output:
            output_file.write(line + '\n')
