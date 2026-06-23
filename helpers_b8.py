import threading

def integer_to_bits(n, width):
    """Convert an integer n to a list of bits of length width."""
    # If n is negative, convert to two's complement representation
    if n < 0:
        n = 2**width + n
    if 2**width <= n:
        raise ValueError(f"Cannot represent {n} in {width} bits")
    return [(n >> i) & 1 for i in range(width-1, -1, -1)]

def bits_to_integer(bits, signed=False):
    """Convert a list of bits to an integer.
    If signed is True, then the first bit is the sign bit
    and the rest are the magnitude bits."""
    n = 0

    sign = 0
    if signed and len(bits) > 0:
        # Record the sign and flip the rest of the bits
        sign = bits[0]
        if (sign == 1):
          bits = map(lambda x: not x, bits[1:])
        else:
          bits = bits[1:]
    
    # Convert the bits to an integer
    for bit in bits:
        n = (n << 1) | bit
    
    # If signed and negative then flip at the end 
    if signed & (sign == 1):
        n = -(n + 1)
    return n

# ============================================================================
# Helper functions for CPU
# ============================================================================

def bit(byte, pos):
  """Extract a single bit from a byte at the given position,
     indexing from the left."""
  return byte[7-pos]

def bits(byte, start, end):
  """Extract a range of bits from a byte, indexing from the left."""
  return byte[7-start:8-end]

def set_flag(flag_reg, flag_bit, value):
  """Set or clear a specific flag bit in the flags register."""
  flags = flag_reg.read()
  flags[7-flag_bit] = value
  flag_reg.write(flags)  # Update the flags register with the new value

# ============================================================================
# Memory and register model
# ============================================================================

class Memory:
  def __init__(self, bits, size):
    """Initialize memory with specified bit width and size."""
    zero = [0 for _ in range(0, bits)]
    self.ram = [zero.copy() for x in range(0, size)]
  
  def read(self, address):
    """Read value from memory at given address."""
    return self.ram[bits_to_integer(address)].copy()
  
  def write(self, address, val):
    """Write value to memory at given address."""
    self.ram[bits_to_integer(address)] = val

  def load_binary(self, filename):
    """Load memory contents from a binary file."""
    size = 0
    with open(filename, 'rb') as f:
      for i in range(0, len(self.ram)):
        byte = f.read(1)
        size = size + 1
        if not byte:
          break
        self.ram[i] = integer_to_bits(ord(byte), 8)
    return size

class Register:
  def __init__(self, size, name = ""):
    """Initialize a register with specified bit size."""
    self.value = [0 for x in range(0, size)]
    self.name = name

  def read(self):
    """Read the current value of the register."""
    return self.value
  
  def write(self, val):
    """Write a new value to the register."""
    self.value = val

# ============================================================================
# IO keyboard model (asynchronous)
# ============================================================================

def keyboard_thread(flags, inp):
    def inner():
        try:
            while True:
                line = input()
                if not line:
                    continue
                set_flag(flags, 2, 1)  # Set IS (Input Strobe) to 1
                inp.write(integer_to_bits(ord(line[0]), 8))
        except BaseException:
            pass  # Swallow EOFError/IndexError/etc. during shutdown
    return inner

def start_keyboard_hardware(flags, inp):
    threading.Thread(target=keyboard_thread(flags, inp), daemon=True).start()

