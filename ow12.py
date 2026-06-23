"""
Badger-8: A self-contained 8-bit CPU simulator.

"""

from debugger_b8 import debugger, print_registers
from helpers_b8 import *

# just come commands that i commonly run so i can copy and paste for convience
# python3 ow12.py /Users/oscarwinter/Documents/comp4106-a2/b8_programs/control_flow/sum_1_to_5.o --clocked
# python3 test_b8.py ow12.py


# ===========================================================================

#   eight_bit_add(a7..a0, b7..b0, c0)        → (carry_out, s7..s0)
def half_add(a, b):
  """1-bit half adder"""
  s = a ^ b
  c = a & b
  return c, s
def full_add(a, b, c_in):
  """1-bit full adder"""
  c1, intermediate = half_add(a, b)
  c2, s = half_add(intermediate, c_in) 
  c_out = c1 | c2
  return c_out, s
def eight_bit_add(a7, a6, a5, a4, a3, a2, a1, a0, b7, b6, b5, b4, b3, b2, b1, b0, c0):
  """8-bit adder with carry in and carry out"""
  c1, s0 = full_add(a0, b0, c0)
  c2, s1 = full_add(a1, b1, c1)
  c3, s2 = full_add(a2, b2, c2)
  c4, s3 = full_add(a3, b3, c3)
  c5, s4 = full_add(a4, b4, c4)
  c6, s5 = full_add(a5, b5, c5)
  c7, s6 = full_add(a6, b6, c6)
  carry_out, s7 = full_add(a7, b7, c7)
  return carry_out, s7, s6, s5, s4, s3, s2, s1, s0




#   eight_bit_sub(x7..x0, y7..y0, b0)        → (borrow_out, d7..d0)
def half_sub(x, y):
  """Half subtractor"""
  d = ((not x) & y) | (x & (not y))
  b = (not x) & y
  return b, d
def full_sub(x, y, b_in):
  """Full subtractor"""
  b1, intermediate = half_sub(x, b_in)
  b2, d = half_sub(intermediate, y)
  b_out = b1 | b2
  return b_out, d
def eight_bit_sub(x7, x6, x5, x4, x3, x2, x1, x0, y7, y6, y5, y4, y3, y2, y1, y0, b0):
  """8-bit subtractor with borrow in and borrow out"""
  b1, d0 = full_sub(x0, y0, b0)
  b2, d1 = full_sub(x1, y1, b1)
  b3, d2 = full_sub(x2, y2, b2)
  b4, d3 = full_sub(x3, y3, b3)
  b5, d4 = full_sub(x4, y4, b4)
  b6, d5 = full_sub(x5, y5, b5)
  b7, d6 = full_sub(x6, y6, b6)
  borrow_out, d7 = full_sub(x7, y7, b7)
  return borrow_out, d7, d6, d5, d4, d3, d2, d1, d0

#   eight_bit_and(a7..a0, b7..b0)            → (r7..r0)
def eight_bit_and(a7, a6, a5, a4, a3, a2, a1, a0, b7, b6, b5, b4, b3, b2, b1, b0):
  """8-bit bitwise AND"""
  r7 = a7 & b7
  r6 = a6 & b6
  r5 = a5 & b5
  r4 = a4 & b4
  r3 = a3 & b3
  r2 = a2 & b2
  r1 = a1 & b1
  r0 = a0 & b0
  return r7, r6, r5, r4, r3, r2, r1, r0



#   eight_bit_not(a7..a0)                    → (r7..r0)
def eight_bit_not(a7, a6, a5, a4, a3, a2, a1, a0):
  """8-bit bitwise NOT"""
  r7 = not a7
  r6 = not a6
  r5 = not a5
  r4 = not a4
  r3 = not a3
  r2 = not a2
  r1 = not a1
  r0 = not a0
  return r7, r6, r5, r4, r3, r2, r1, r0




#   eight_bit_multiplex_four_to_one(         → (z7..z0)
#       a7..a0, b7..b0, c7..c0, d7..d0,
#       s1, s0)
def multiplex(a, b, s):
  """1-bit 2-1 multiplexer"""
  z = ((a & (not s)) 
     | (b & s))
  return z

def eight_bit_multiplex_four_to_one(a7, a6, a5, a4, a3, a2, a1, a0, b7, b6, b5, b4, b3, b2, b1, b0, c7, c6, c5, c4, c3, c2, c1, c0, d7, d6, d5, d4, d3, d2, d1, d0, s1, s0):
  """8-bit 4-1 multiplexer"""
  z7 = multiplex(multiplex(a7, b7, s0), multiplex(c7, d7, s0), s1)
  z6 = multiplex(multiplex(a6, b6, s0), multiplex(c6, d6, s0), s1)
  z5 = multiplex(multiplex(a5, b5, s0), multiplex(c5, d5, s0), s1)
  z4 = multiplex(multiplex(a4, b4, s0), multiplex(c4, d4, s0), s1)
  z3 = multiplex(multiplex(a3, b3, s0), multiplex(c3, d3, s0), s1)
  z2 = multiplex(multiplex(a2, b2, s0), multiplex(c2, d2, s0), s1)
  z1 = multiplex(multiplex(a1, b1, s0), multiplex(c1, d1, s0), s1)
  z0 = multiplex(multiplex(a0, b0, s0), multiplex(c0, d0, s0), s1)
  return z7, z6, z5, z4, z3, z2, z1, z0

# ============================================================================


def alu(a7, a6, a5, a4, a3, a2, a1, a0, b7, b6, b5, b4, b3, b2, b1, b0, f1, f0, opcode1, opcode0):
  """
  4-opcode 8-bit ALU.

  Opcodes (opcode1, opcode0):
    0 0 = ADD   (use f1 as carry-in)
    0 1 = SUB   (use f1 as borrow-in)
    1 0 = AND
    1 1 = NOT   (operates on first operand only)

  f1 = carry/borrow flag in,  f0 = zero flag in (unused by ALU logic itself).

  Returns: (carry_flag_out, zero_flag_out, r7, r6, r5, r4, r3, r2, r1, r0)
    carry_flag_out  — carry out for ADD, borrow out for SUB, unchanged otherwise
    zero_flag_out   — 1 when the result is all zeros
  """

  # Compute all 4 operations in parallel, then multiplex result

  # ===setting carry and borrow to 0 for AND and NOT since they are not used ============================================================================
  carry,  x7, x6, x5, x4, x3, x2, x1, x0  = eight_bit_add(a7, a6, a5, a4, a3, a2, a1, a0, b7, b6, b5, b4, b3, b2, b1, b0, f1)
  borrow, y7, y6, y5, y4, y3, y2, y1, y0 = eight_bit_sub(a7, a6, a5, a4, a3, a2, a1, a0, b7, b6, b5, b4, b3, b2, b1, b0, f1)
  z7, z6, z5, z4, z3, z2, z1, z0 = eight_bit_and(a7, a6, a5, a4, a3, a2, a1, a0, b7, b6, b5, b4, b3, b2, b1, b0)
  w7, w6, w5, w4, w3, w2, w1, w0 = eight_bit_not(a7, a6, a5, a4, a3, a2, a1, a0)

  r7, r6, r5, r4, r3, r2, r1, r0 = eight_bit_multiplex_four_to_one(x7, x6, x5, x4, x3, x2, x1, x0, y7, y6, y5, y4, y3, y2, y1, y0, z7, z6, z5, z4, z3, z2, z1, z0, w7, w6, w5, w4, w3, w2, w1, w0, opcode1, opcode0)

  carry_flag_out = carry if (opcode1, opcode0) == (0, 0) else borrow if (opcode1, opcode0) == (0, 1) else f1
  zero_flag_out =  1 if (r7, r6, r5, r4, r3, r2, r1, r0) == (0, 0, 0, 0, 0, 0, 0, 0) else 0
  return carry_flag_out, zero_flag_out, r7, r6, r5, r4, r3, r2, r1, r0
  # ======================================================================================================================================================



# ============================================================================
# badger-8 CPU Implementation
# ============================================================================

def sel_register(register_file, sel3, sel2, sel1, sel0):
  """Select a register from the register file using a 4-bit selector."""
  return register_file[bits_to_integer([sel3, sel2, sel1, sel0])]

def eight_bit_add_no_carry(a7, a6, a5, a4, a3, a2, a1, a0, b7, b6, b5, b4, b3, b2, b1, b0):
  """8-bit adder ignoring carry in/out — used for IP arithmetic."""
  _, s7, s6, s5, s4, s3, s2, s1, s0 = eight_bit_add(a7, a6, a5, a4, a3, a2, a1, a0, b7, b6, b5, b4, b3, b2, b1, b0, 0)
  return s7, s6, s5, s4, s3, s2, s1, s0

def sixteen_bit_add_no_carry(a15, a14, a13, a12, a11, a10, a9, a8, a7, a6, a5, a4, a3, a2, a1, a0, b15, b14, b13, b12, b11, b10, b9, b8, b7, b6, b5, b4, b3, b2,b1, b0):
  """16-bit adder (two chained 8-bit adds) ignoring carry out — used for CS:IP fetch."""
  c, s7, s6, s5, s4, s3, s2, s1, s0 = eight_bit_add(a7, a6, a5, a4, a3, a2, a1, a0, b7, b6, b5, b4, b3, b2, b1, b0, 0)
  _, s15, s14, s13, s12, s11, s10, s9, s8 = eight_bit_add(a15, a14, a13, a12, a11, a10, a9, a8, b15, b14, b13, b12, b11, b10, b9, b8, c)
  return s15, s14, s13, s12, s11, s10, s9, s8, s7, s6, s5, s4, s3, s2, s1, s0


def cpu(memory, debug=False):
  """Execute a program from memory using a simple 8-bit CPU model."""
  # ── Registers ──────────────────────────────────────────────────────────────
  al = Register(8, "al")
  ah = Register(8, "ah")
  bl = Register(8, "bl")
  bh = Register(8, "bh")
  cl = Register(8, "cl")
  ch = Register(8, "ch")
  dl = Register(8, "dl")
  dh = Register(8, "dh")
  cs = Register(8, "cs")
  ds = Register(8, "ds")
  inp = Register(8, "inp")
  out = Register(8, "out")
  r12 = Register(8, "r12")
  r13 = Register(8, "r13")
  flags = Register(8, "flags")
  ip = Register(8, "ip")




  opcode = Register(8, "opcode")
  operand = Register(8, "operand")

  # register_file = [...]
  register_file = [al, ah, bl, bh, cl, ch, dl, dh, cs, ds, inp, out, r12, r13, flags, ip]

  

  if not debug:
    # passing it the flags and inp registers

    try:
      start_keyboard_hardware(flags, inp)
    except TypeError:
      start_keyboard_hardware(inp, flags)
    # note: had errors using just start_keyboard_hardware(flags, inp) so added TypeError ecection handling and it worked i think this is because of the order of the arguments in the function definition of start_keyboard_hardware in keyboard.py but not sure was just a idea

  # ── Main loop ──────────────────────────────────────────────────────────────
  while True:

    #   If it is 1, break out of the loop, then call print_registers(...).
    def bit7_is_set(flags):
      return bit(flags.read(), 7) == 1
    

    if bit7_is_set(flags):
      print_registers(al, ah, bl, bh, cl, ch, dl, dh, cs, ds, inp, out, flags, ip)
      break
    #already explained by template

    # ── FETCH ─────────────────────────────────────────────────────────────────
    #   Use sixteen_bit_add_no_carry to compute the operand address.

    # i do CS:IP+1 because the operand is located at the next adress after the opcode so by adding one we reach the operand and make them into fuctions for clearity and reuse
    # i used • hear to unpack the lists so i can pass it into the sixteen_bit_add_no-carry
    def read_memory(address):
      return memory.read(address)
    

    def fetch_opcode(cs, ip):
      address = sixteen_bit_add_no_carry(*cs.read(), *ip.read(), *[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]) 
      return read_memory(address)
    

    def fetch_operand(cs, ip):
      address = sixteen_bit_add_no_carry(*cs.read(), *ip.read(), *[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1])
      return read_memory(address)
    


    opcode.write(fetch_opcode(cs, ip)) # CS is at index 8
    operand.write(fetch_operand(cs, ip)) 

    if debug:
     if not debugger(al, ah, bl, bh, cl, ch, dl, dh, cs, ds, inp, out, flags, ip, opcode, operand, memory):
       break

    # ── DECODE operand type ───────────────────────────────────────────────────
    op_bits = opcode.read()
    operand_type = op_bits[0]
    s2, s1, s0 = op_bits[1], op_bits[2], op_bits[3] # sets the bits of the opcode to be used to work out what operation the ALU needs to do
    trg = sel_register(register_file, op_bits[4], op_bits[5], op_bits[6], op_bits[7])



    if operand_type == 0: #
      src = sel_register(register_file, operand.read()[0], operand.read()[1], operand.read()[2], operand.read()[3])
      # src is the register we want basied off the operand bits 
      op = src.read()
    else:
      op = operand.read()
    # then we read the register to find the value to be manipulated by the ALU or memory access

    # ── DECODE opcode and EXECUTE ─────────────────────────────────────────────
    jumped = False
    if s2 == 0: # S2 = 0 means ALU operation so we call the AlU function with the inputs
      flag_bits = flags.read()
      status1, status0, *res = alu(*trg.read(), *op, flag_bits[6], flag_bits[7], s1, s0)
      trg.write(res)
      f = flags.read()
      flags.write([f[0], f[1], f[2], f[3], f[4], f[5], status1, status0])


    elif [s2, s1, s0] == [1, 0, 0]: # S2 = 1, S1 = 0, S0 = 0 means MOV operation so we write the value of op into the trg register
      trg.write(op)
      if out is trg:
        print(chr(bits_to_integer(list(op))), end="", flush=True)


    elif [s2, s1, s0] == [1, 0, 1]: # S2 = 1, S1 = 0, S0 = 1 means MOV from memory to register so we read the value from memory at the address given by op and write it into trg
      address = op if operand_type == 1 else src.read()
      trg.write(memory.read(address))
      list_value = memory.read(address)
      if  out is trg:
        print(chr(bits_to_integer(list(list_value))), end="", flush=True)


    elif [s2, s1, s0] == [1, 1, 0]: # S2 = 1, S1 = 1, S0 = 0 means MOV from register to memory so we write the value of trg into memory at the address given by op
      address = op if operand_type == 1 else src.read()
      memory.write(address, trg.read())


    elif [s2, s1, s0] == [1, 1, 1]: # S2 = 1, S1 = 1, S0 = 1 means jump so we check the flags and if the condition is met we write the value of trg into ip to jump to that address
      flag_bits = flags.read()
      if operand_type == 0:
        # JE: jump if equal (zero flag set)
        if flag_bits[7] == 1:
          ip.write(trg.read())
          jumped = True
      else:
        # JA: jump above (carry flag clear)
        if flag_bits[6] == 0:
          ip.write(trg.read())
          jumped = True

    # ── ADVANCE IP ────────────────────────────────────────────────────────────
    if not jumped:
      ip.write(eight_bit_add_no_carry(*ip.read(), *[0, 0, 0, 0, 0, 0, 1, 0]))


  # If we exited print final registers
  # comment this out once you have implemented more
  # print_registers(al, ah, bl, bh, cl, ch, dl, dh, cs, ds, inp, out, flags, ip)\


class Clock: # used to track and preform the tick cycle


  def __init__(self):
    self.cycle = 0
    self.components = []

  def cycles(self):
    return self.cycle

  def tick(self): # moves all components by one clock cycle
    for component in self.components:
      component.tick()
    self.cycle += 1 # incremnts the counter

  def register(self, component): # adds the specified component to the clocks update list
    self.components.append(component)
    return component
  
# ClockedMemory class is used to store both the current and next sate of memory and update them upon a clock tick
class ClockedMemory:


  def __init__(self, size = 2**16):
    self.size = size
    self.current = [[0]*8 for _ in range(size)] #use a list to store current memory by using a loop to create a list of lists where each inner list is a byte of memory and the main list represents the whole memory like ram
    self.next = [[0]*8 for _ in range(size)] #same as current but next memory state
    self.written_addresses = set() # use set to mark addresses that have been written so we can only update those that have been changed

  def tick(self): # updates all of the memory states that have been marked
    for addr in self.written_addresses:
      self.current[addr] = list(self.next[addr]) # moves to the next memory addresses that are marked written_addresses
    self.written_addresses.clear()# resets for next tick

  def write(self, address, bits): # similar to write in flip flop but additionaly need to mark whats been written to
    addr = bits_to_integer(list(address))
    self.next[addr] = list(bits)
    self.written_addresses.add(addr)

  def load_binary(self, filename):  # loads the binary file into memory by reading byte by byte abd writting it into memory 
    with open(filename, "rb") as f:
      data = f.read()
    for i, byte in enumerate(data):
      bits = integer_to_bits(byte, 8)
      self.current[i] = bits
      self.next[i] = bits
    return self

  def read(self, address): # reads current state of memory at adress given
    addr = bits_to_integer(list(address))
    return list(self.current[addr])
  
  
  
#flip flop class to store the current and next state of the registers and memory and update them on each clock tick 
class FlipFlop:

  def __init__(self, n, name = ""): # n is the number of bits of the CPU register and names are for identification
    self.name = name
    self.n = n
    self.next = [0] * n
    self.current = [0] * n

  def tick(self): # updates current state to next state 
    self.current = list(self.next)

  def write(self, bits): # allows you to modify the next state of a register by writing to it this will be implemented in the next clock tick
    bits = list(bits)
    if len(bits) != self.n:
      raise ValueError(f"FlipFlop {self.name} expected {self.n} bits, got {len(bits)}")
    self.next = bits

  def read(self): # returns the current state of the given register
    return list(self.current)
  
def cpu_clocked(memory, debug=False): # follows same structure as the original CPU function but using fip flops rather than the registers so ill only comment whats changed

  clock = Clock() # inalizes the clock
  def FF(n, name=""):
    return clock.register(FlipFlop(n, name)) # creates a flip flop of n bits(8 bits in the case) using the previous classes
  
  #makes the flip flops using the above function
  al = FF(8, "al")
  ah = FF(8, "ah")
  bl = FF(8, "bl")
  bh = FF(8, "bh")
  cl = FF(8, "cl")
  ch = FF(8, "ch")
  dl = FF(8, "dl")
  dh = FF(8, "dh")
  cs = FF(8, "cs")
  ds = FF(8, "ds")
  inp = FF(8, "inp")
  out = FF(8, "out")
  r12 = FF(8, "r12")
  r13 = FF(8, "r13")
  flags = FF(8, "flags")
  ip = FF(8, "ip")


  opcode = FF(8, "opcode")
  operand = FF(8, "operand")

  register_file = [al, ah, bl, bh, cl, ch, dl, dh, cs, ds, inp, out, r12, r13, flags, ip]

  clock.register(memory) # adding memory to the registers even though its not one so i can use the tick function to call it every cycle like the others

  if not debug:
    # Keyboard thread usable later
    try:
      start_keyboard_hardware(flags, inp)
    except TypeError:
      start_keyboard_hardware(inp, flags)

    # ── Main loop ──────────────────────────────────────────────────────────────
  while True:
    #   If it is 1, break out of the loop, then call print_registers(...).
    def bit7_is_set(flags):
      return bit(flags.read(), 7) == 1
    if bit7_is_set(flags):
      print_registers(al, ah, bl, bh, cl, ch, dl, dh, cs, ds, inp, out, flags, ip)
      break

    # ── FETCH ─────────────────────────────────────────────────────────────────
    #   Use sixteen_bit_add_no_carry to compute the operand address.
    def read_memory(address):
      return memory.read(address)
    
    def fetch_opcode(cs, ip):
      address = sixteen_bit_add_no_carry(*cs.read(), *ip.read(), *[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
      return read_memory(address)
    
    def fetch_operand(cs, ip):
      address = sixteen_bit_add_no_carry(*cs.read(), *ip.read(), *[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1])
      return read_memory(address)
    
    opcode.write(fetch_opcode(cs, ip)) # CS is at index 8
    operand.write(fetch_operand(cs, ip))

    operand.tick() # latches the opcode and operand so the vlaues held are on the clock edge

    opcode.tick()

    if debug:
     if not debugger(al, ah, bl, bh, cl, ch, dl, dh, cs, ds, inp, out, flags, ip, opcode, operand, memory):
       break
     
    op_bits = opcode.read()
    operand_type = op_bits[0]
    s2, s1, s0 = op_bits[1], op_bits[2], op_bits[3]


    trg = sel_register(register_file, op_bits[4], op_bits[5], op_bits[6], op_bits[7])

    if operand_type == 0:
      src = sel_register(register_file, operand.read()[0], operand.read()[1], operand.read()[2], operand.read()[3])
      op = src.read()
    else:
      op = operand.read()
    jumped = False


    if s2 == 0:
      flag_bits = flags.read()
      status1, status0, *res = alu(*trg.read(), *op, flag_bits[6], flag_bits[7], s1, s0)
      trg.write(res)
      trg.tick() # latches the trg so the vlaues held are on the clock edge
      f = flags.read()
      flags.write([f[0], f[1], f[2], f[3], f[4], f[5], status1, status0])


    elif [s2, s1, s0] == [1, 0, 0]:
      trg.write(op)
      trg.tick() # latches the trg so the vlaues held are on the clock edge
      if trg.name == "out":
        char_code = bits_to_integer(list(op))
        print(chr(char_code), end="", flush=True)
        f = list(flags.read())
        #f[6] = 1
        flags.write(f)



    elif [s2, s1, s0] == [1, 0, 1]:
      address = op if operand_type == 1 else src.read()
      trg.write(memory.read(address))


    elif [s2, s1, s0] == [1, 1, 0]:
      address = op if operand_type == 1 else src.read()
      memory.write(address, trg.read())



    elif [s2, s1, s0] == [1, 1, 1]:
      flag_bits = flags.read()
      if operand_type == 0:
        # JE: jump if equal (zero flag set)
        if flag_bits[7] == 1:
          ip.write(trg.read())
          jumped = True
      else:
        # JA: jump above (carry flag clear)
        if flag_bits[6] == 0:
          ip.write(trg.read())
          jumped = True


    if not jumped:
      ip.write(eight_bit_add_no_carry(*ip.read(), *[0, 0, 0, 0, 0, 0, 1, 0]))



    clock.tick() # advances the clock by one so values are updated

# ============================================================================
# Main Program
# ============================================================================

if __name__ == '__main__': # allows the user to specify a binary file to execute, and whether to use the clocked implementation
  import sys

  if len(sys.argv) < 2: # if no binary file is provided, raise an error
    raise ValueError("Please provide a binary file to execute, e.g. python3 ow12.py program.bin")
  filename = sys.argv[1]

  if "--clocked" in sys.argv: # if the user loads with the --clocked flag the task 5 clocked implementation is used
    memory = ClockedMemory(2**16)
    memory.load_binary(filename)
    cpu_clocked(memory)
  else: # otherwise the normal implementation is used
    Memory = Memory(8, 2**16)
    Memory.load_binary(filename)
    cpu(Memory)



  