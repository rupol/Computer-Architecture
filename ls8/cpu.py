"""CPU functionality."""

import sys

# OP codes
ADD = 0b10100000
AND = 0b10101000
CALL = 0b01010000
CMP = 0b10100111
DEC = 0b01100110
DIV = 0b10100011
HLT = 0b00000001
INC = 0b01100101
IRET = 0b00010011
JEQ = 0b01010101
JLE = 0b01011001
JLT = 0b01011000
JMP = 0b01010100
JNE = 0b01010110
LD = 0b10000011
LDI = 0b10000010
MOD = 0b10100100
MUL = 0b10100010
NOT = 0b01101001
OR = 0b10101010
POP = 0b01000110
PRA = 0b01001000
PRN = 0b01000111
PUSH = 0b01000101
RET = 0b00010001
SHL = 0b10101100
SHR = 0b10101101
ST = 0b10000100
SUB = 0b10100001
XOR = 0b10101011


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256  # 256 bytes of memory
        self.reg = [0] * 8  # 8 general-purpose registers
        self.sp = 244  # stack pointer, set to F4 on initialization
        self.reg[7] = self.sp
        self.pc = 0  # program counter, address of the currently executing instruction
        self.fl = 0b00000000  # 00000LGE
        self.running = True
        self.bt = {  # branch table
            CALL: self.op_call,
            HLT: self.op_hlt,
            # IRET: self.op_iret,
            JEQ: self.op_jeq,
            # JLE: self.op_jle,
            # JLT: self.op_jlt,
            JMP: self.op_jmp,
            JNE: self.op_jne,
            # LD: self.op_ld,
            LDI: self.op_ldi,
            POP: self.op_pop,
            # PRA: self.op_pra,
            PRN: self.op_prn,
            PUSH: self.op_push,
            RET: self.op_ret,
            # ST: self.op_st,
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

    # alu operations (arithmetic and logic operators)
    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == ADD:
            self.reg[reg_a] += self.reg[reg_b]
        elif op == AND:
            self.reg[reg_a] &= self.reg[reg_b]
        elif op == CMP:
            # Compare the values in two registers. (FL = 00000LGE)
            # If they are equal, set the Equal E flag to 1, otherwise set it to 0.
            if self.reg[reg_a] == self.reg[reg_b]:
                self.fl = 0b00000001
            # If registerA is less than registerB, set the Less-than L flag to 1, otherwise set it to 0.
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.fl = 0b00000100
            # If registerA is greater than registerB, set the Greater-than G flag to 1, otherwise set it to 0.
            else:
                self.fl = 0b00000010
        elif op == DEC:
            self.reg[reg_a] -= 1
        elif op == DIV:
            if reg_b == 0:
                print('ERROR: cannot divide by 0')
                self.running = 0
                sys.exit(1)
            else:
                self.reg[reg_a] /= self.reg[reg_b]
        elif op == INC:
            self.reg[reg_a] += 1
        elif op == MOD:
            if reg_b == 0:
                print('ERROR: cannot divide by 0')
                self.running = 0
                sys.exit(1)
            else:
                self.reg[reg_a] %= self.reg[reg_b]
        elif op == MUL:
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == NOT:
            self.reg[reg_a] != self.reg[reg_b]
        elif op == OR:
            self.reg[reg_a] |= self.reg[reg_b]
        elif op == SHL:
            self.reg[reg_a] <<= self.reg[reg_b]
        elif op == SHR:
            self.reg[reg_a] >>= self.reg[reg_b]
        elif op == SUB:
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == XOR:
            self.reg[reg_a] ^= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    # OP functions
    def op_call(self, operand_a, operand_b):
        # push the address of the instruction directly after CALL (pc + 2)
        # decrement the SP
        self.sp -= 1
        # write the return address to memory at the SP location
        self.ram_write(self.pc + 2, self.sp)
        # set PC to the address stored in the given register
        self.pc = self.reg[operand_a]

    def op_hlt(self, operand_a, operand_b):
        # exit the loop (no matter what comes next)
        self.running = False

    def op_jeq(self, operand_a, operand_b):
        # If equal flag is set (true), jump to the address stored in the given register.
        equalFL = self.fl & 0b00000001
        if equalFL == 1:
            # set the PC to the address stored in the given register
            self.op_jmp(operand_a, operand_b)
        else:
            self.pc += 2

    def op_jmp(self, operand_a, operand_b):
        # set the PC to the address stored in the given register
        self.pc = self.reg[operand_a]

    def op_jne(self, operand_a, operand_b):
        # If E flag is clear (false, 0), jump to the address stored in the given register.
        equalFL = self.fl & 0b00000001
        if equalFL == 0:
            # set the PC to the address stored in the given register
            self.op_jmp(operand_a, operand_b)
        else:
            self.pc += 2

    def op_ldi(self, operand_a, operand_b):
        # load "immediate", store a value in a register, or "set this register to this value"
        # register location is byte at pc + 1 (operand_a)
        # value is byte at pc + 2 (operand_b)
        self.reg[operand_a] = operand_b

    def op_pop(self, operand_a, operand_b):
        # copy the value from the address pointed to by SP to the given register
        value = self.ram_read(self.sp)
        self.reg[operand_a] = value
        # increment the SP
        self.sp += 1

    def op_prn(self, operand_a, operand_b):
        # prints the numeric value stored in a register
        # register location is byte at pc + 1 (operand_a)
        print(self.reg[operand_a])

    def op_push(self, operand_a, operand_b):
        # decrement the SP
        self.sp -= 1
        # copy the value in the given register to the address pointed to by SP
        self.ram_write(self.reg[operand_a], self.sp)

    def op_ret(self, operand_a, operand_b):
        # pop the value from the top of the stack and store it in the PC
        self.pc = self.ram_read(self.sp)
        # increment the SP
        self.sp += 1

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

            # dispatch ALU operations to alu function
            if isALU == 1:
                self.alu(IR, operand_a, operand_b)

            # perform actions needed based on given opcode (branch table)
            else:
                if IR in self.bt:
                    self.bt[IR](operand_a, operand_b)

            # update pc to point to next instruction (if the instruction doesn't set the PC)
            setsPC = (IR >> 4) & 0b00000001
            if setsPC == 0:
                # determine number of operands
                num_operands = IR >> 6
                # update pc to point to next instruction
                self.pc += num_operands + 1


cpu = CPU()

cpu.load()
cpu.run()
