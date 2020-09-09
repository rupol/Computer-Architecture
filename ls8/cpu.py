"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256  # 256 bytes of memory
        self.reg = [0] * 8  # 8 general-purpose registers
        self.sp = 244  # stack pointer, set to F4 on initialization
        self.reg[7] = self.sp
        self.pc = 0  # program counter, address of the currently executing instruction
        self.running = True
        self.opcode = {
            # set instruction codes
            'HLT': 0b00000001,
            'LDI': 0b10000010,
            'PRN': 0b01000111,
            'MUL': 0b10100010,
            'ADD': 0b10100000,
            'PUSH': 0b01000101,
            'POP': 0b01000110
        }

    def load(self):
        """Load a program into memory."""
        address = 0

        # check for proper number of command line arguments
        if len(sys.argv) != 2:
            print('Usage: cpy.py filename')
            sys.exit(1)

        filename = sys.argv[1]

        # open a file and load into memory
        try:
            with open(filename)as f:
                for line in f:
                    # split on # symbol and remove comments
                    line = line.split("#")
                    opcode = line[0].strip()

                    # remove empty lines
                    if opcode == "":
                        continue

                    num = int(opcode, 2)
                    self.ram_write(num, address)
                    address += 1
        # if file doesn't exist
        except FileNotFoundError:
            print(f'{filename} file not found')
            sys.exit(2)

    def ram_read(self, MAR):
        # return MAR (address) MDR (value)
        return self.ram[MAR]

    def ram_write(self, MDR, MAR):
        # write MDR (value) to MAR (address)
        self.ram[MAR] = MDR

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == self.opcode['ADD']:
            self.reg[reg_a] += self.reg[reg_b]
        elif op == self.opcode['MUL']:
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        while self.running:
            # read the memory address stored in register PC
            # store in IR (instruction register - local variable)
            IR = self.ram_read(self.pc)

            # read bytes at pc + 1 and pc + 2 and store into operand_a and operand_b
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            # determine if IR is an ALU operation
            isALU = (IR >> 5) & 0b00000001

            # perform actions needed based on given opcode (if-elif statements)
            # exit the loop if a HLT instruction is encountered (no matter what comes next)
            if IR == self.opcode['HLT']:
                self.running = False

            # dispatch ALU operations to alu function
            elif isALU == 1:
                self.alu(IR, operand_a, operand_b)

            elif IR == self.opcode['LDI']:
                # load "immediate", store a value in a register, or "set this register to this value"
                # register location is byte at pc + 1 (operand_a)
                # value is byte at pc + 2 (operand_b)
                self.reg[operand_a] = operand_b

            elif IR == self.opcode['PRN']:
                # prints the numeric value stored in a register
                # register location is byte at pc + 1 (operand_a)
                print(self.reg[operand_a])

            elif IR == self.opcode['PUSH']:
                # decrement the SP
                self.sp -= 1
                # copy the value in the given register to the address pointed to by SP
                self.ram_write(self.reg[operand_a], self.sp)

            elif IR == self.opcode['POP']:
                # copy the value from the address pointed to by SP to the given register
                value = self.ram_read(self.sp)
                self.reg[operand_a] = value
                # increment the SP
                self.sp += 1

            # determine number of operands
            num_operands = IR >> 6
            # update pc to point to next instruction
            self.pc += num_operands + 1


cpu = CPU()

cpu.load()
cpu.run()
