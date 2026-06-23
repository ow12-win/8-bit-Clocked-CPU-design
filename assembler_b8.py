#!/usr/bin/env python3
"""
Simple assembler for 8-bit CPU instruction set.
Converts textual assembly to binary representation.
"""

REGISTERS = {
    'al': [0, 0, 0, 0],
    'ah': [0, 0, 0, 1],
    'bl': [0, 0, 1, 0],
    'bh': [0, 0, 1, 1],
    'cl': [0, 1, 0, 0],
    'ch': [0, 1, 0, 1],
    'dl': [0, 1, 1, 0],
    'dh': [0, 1, 1, 1],
    
    'cs': [1, 0, 0, 0],
    'ds': [1, 0, 0, 1],
    'inp': [1, 0, 1, 0],
    'out': [1, 0, 1, 1],
    'flags': [1, 1, 1, 0],
    'ip'   : [1, 1, 1, 1] # read only
}

# Instruction mnemonics map
# to their base opcode (S2, S1, S0)
#   + their arity
#   + whether they override the operand type:
#           (None if not, otherwise provide the bit)
OPCODES = {
    'add':   ([0, 0, 0], 2, None),
    'sub':   ([0, 0, 1], 2, None),
    'and':   ([0, 1, 0], 2, None),
    'not':   ([0, 1, 1], 1, None),
    'nop':   ([0, 1, 1], 0, 1),
    'mov':   ([1, 0, 0], 2, None),
    'load':  ([1, 0, 1], 2, None),
    'store': ([1, 1, 0], 2, None),
    'je':    ([1, 1, 1], 1, 0),
    'ja':    ([1, 1, 1], 1, 1)
}

zero = [0 for _ in range(0, 8)]
zero_short = [0 for _ in range(0, 4)]

def parse_register(reg_str):
    """Parse register name and return 2-bit encoding."""
    reg = reg_str.strip().lower()
    if reg not in REGISTERS:
        raise ValueError(f"Unknown register: {reg}")
    return REGISTERS[reg]

def integer_to_bits(n, width):
    """Convert an integer n to a list of bits of length width."""
    # If n is negative, convert to two's complement representation
    if n < 0:
        n = 2**width + n
    if 2**width <= n:
        raise ValueError(f"Cannot represent {n} in {width} bits")
    return [(n >> i) & 1 for i in range(width-1, -1, -1)]

def parse_immediate(imm_str):
    """Parse immediate value (binary 0b or hex 0x) and return 8-bit value."""
    imm_str = imm_str.strip()
    if imm_str.startswith('0x') or imm_str.startswith('0X'):
        value = int(imm_str, 16)
    elif imm_str.startswith('0b') or imm_str.startswith('0B'):
        value = int(imm_str, 2)
    else:
        raise ValueError(f"Immediate values must use 0b (binary) or 0x (hex) notation, got: {imm_str}")
    
    if value < 0 or value > 256:
        raise ValueError(f"Immediate value {value} out of range (0-255)")
    return integer_to_bits(value, 8)

def resolve_value(token, labels=None):
    """Resolve a token as an 8-bit immediate: 0x/0b literal, or a label name."""
    token = token.strip()
    if token.startswith(('0x', '0X', '0b', '0B')):
        return parse_immediate(token)
    if labels is not None and token in labels:
        return integer_to_bits(labels[token], 8)
    raise ValueError(
        f"Expected immediate (0x.../0b...) or known label, got: {token!r}"
        + (f"  (known labels: {list(labels)})" if labels else "")
    )

def assemble_instruction(line, labels=None):
    """
    Assemble a single instruction line into two bytes (opcode, operand).
    labels: optional dict of {name: byte_address} for resolving label references.
    Returns tuple of (opcode_bits, operand_bits), or None for blank/comment lines.
    """
    # Remove comments and strip whitespace
    if ';' in line:
        line = line[:line.index(';')]
    line = line.strip()
    
    if not line:
        return None
    
    # Split instruction and operands
    parts = line.replace(',', ' ').split()
    if not parts:
        return None
    
    mnemonic = parts[0].lower()
    
    if mnemonic not in OPCODES:
        raise ValueError(f"Unknown instruction: {mnemonic}")
    
    (opcode_base, arity, override_bit) = OPCODES[mnemonic]
    operand_type = None
    operand_fst = None
    operand_snd = None

    if (len(parts) - 1) > arity:
        raise ValueError(f"{mnemonic.upper()} takes {arity} operands, got {len(parts) - 1} operands")

    # 0 arity instructions
    if arity == 0:
      operand_snd   = zero
      operand_fst   = zero_short
      operand_type  = override_bit
    
    # >= 1 arity functions
    else:
      dest = parts[1].lower()
      # 1 arity functions
      if arity == 1:
          operand_snd = zero
          if dest in REGISTERS.keys():
              operand_fst = REGISTERS[dest]
              if override_bit is None:
                  operand_type = 0
              else:
                  operand_type = override_bit
          else:
                raise ValueError(f"{mnemonic} requires a single register operand")
      else:
          if arity == 2:
              src = parts[2].lower()
              if dest == "ip":
                  raise ValueError("Cannot use IP as a destination register; the IP register is read-only")

              match mnemonic:
                case 'store':
                  if not (dest[0] == "[" and dest[-1] == "]"):
                    raise ValueError(f"Expecting an address designator")  
                  dest = dest.strip('[]')
                  # order is flipped in the encoding for store
                  operand_fst = parse_register(src)
                  if dest in REGISTERS.keys():
                      operand_type = 0
                      operand_snd = parse_register(dest) + zero_short
                  else:
                      operand_type = 1
                      operand_snd = resolve_value(dest, labels)

                case 'load':
                  if not (src[0] == "[" and src[-1] == "]"):
                    raise ValueError(f"Expecting an address designator")  
                  src = src.strip('[]')
                  operand_fst = parse_register(dest)
                  if src in REGISTERS.keys():
                      operand_type = 0
                      operand_snd = parse_register(src) + zero_short
                  else:
                      operand_type = 1
                      operand_snd = resolve_value(src, labels)

                case _:
                  operand_fst = parse_register(dest)

                  # For ADD, SUB, AND, MOV: check if source is register, then
                  # immediate or label
                  try:
                    # Try parsing source as register
                    operand_type = 0
                    operand_snd = parse_register(src) + zero_short
                  except Exception:
                    # Try parsing source as immediate or label
                    operand_type = 1
                    operand_snd = resolve_value(src, labels)

    opcode = [operand_type] + opcode_base + operand_fst
    operand = operand_snd
    return (opcode, operand)

def pack_bits(bits):
    """Convert list of bits to to a character"""
    value = bits_to_integer(bits)
    return bytes([value])

def bits_to_integer(bits):
    """Convert a list of bits to an integer."""
    value = 0
    for bit in bits:
        value = (value << 1) | bit
    return value

def bits_to_string(bits):
    """Convert list of bits to string."""
    return ''.join(str(b) for b in bits)

def _is_valid_label(name):
    """Return True if name is a valid label identifier."""
    return (bool(name)
            and name[0].isalpha()
            and all(c.isalnum() or c == '_' for c in name))

def assemble_program(program_text):
    """
    Assemble a complete program (two-pass to resolve labels).
    Labels are defined as  `label:` or  `label: instruction`
    and can be referenced anywhere an immediate is expected, or inside [...].
    Each instruction is 2 bytes; label address = instruction_index * 2.
    Returns list of (opcode_bits, operand_bits) tuples.
    """
    raw_lines = program_text.strip().split('\n')

    # ── Pass 1: strip labels and build address map ────────────────────────────
    labels = {}        # label_name -> byte_address
    clean_lines = []   # raw_lines with label prefixes removed
    instruction_count = 0

    for line in raw_lines:
        # Strip inline comments, then whitespace
        code = line.split(';')[0].strip()

        # Detect  label:  prefix (but not inside bracket notation like [0x00])
        if ':' in code and not code.lstrip().startswith('['):
            label_part, _, rest = code.partition(':')
            label_part = label_part.strip()
            if _is_valid_label(label_part):
                labels[label_part] = instruction_count * 2
                code = rest.strip()

        clean_lines.append(code)

        # Count this line as an instruction if non-empty after stripping label
        if code.strip():
            instruction_count += 1

    # ── Pass 2: assemble with label resolution ───────────────────────────────
    instructions = []
    for line_num, line in enumerate(clean_lines, 1):
        try:
            result = assemble_instruction(line, labels)
            if result:
                instructions.append(result)
        except Exception as e:
            print(f"Error on line {line_num}: {e}")
            print(f"  Line: {line}")
            raise
    return instructions

def save_to_binary(instructions, output_path):
    """
    Save assembled instructions to binary .o file.
    Each instruction (opcode + operand) is packed into 2 byte:
    """
    bytes_data = bytearray()
    
    for opcode, operand in instructions:
        bytes_data.append(bits_to_integer(opcode))
        bytes_data.append(bits_to_integer(operand))
    
    # Write to file
    with open(output_path, 'wb') as f:
        f.write(bytes_data)
    
    return len(bytes_data)

if __name__ == '__main__':
    import sys
    import os
    
    if len(sys.argv) < 2:
        print("Usage: python3 assembler_b8.py <input.asm> [output.o]")
        print("Output will be saved as <input.o> if output isn't given")
        sys.exit(1)
    
    input_path = sys.argv[1]

    # Handle optional output .o file specification
    if len(sys.argv) >= 3:
        output_path = sys.argv[2]
    else:    
      # Generate output filename: replace .asm with .o
      if input_path.endswith('.asm'):
          output_path = input_path[:-4] + '.o'
      else:
          output_path = input_path + '.o'
    
    # Read input file
    try:
        with open(input_path, 'r') as f:
            program = f.read()
    except FileNotFoundError:
        print(f"Error: File '{input_path}' not found")
        sys.exit(1)
    
    # Assemble program
    try:
        instructions = assemble_program(program)
    except Exception:
        sys.exit(1)
    
    # Save to binary file
    num_bytes = save_to_binary(instructions, output_path)
    
    print(f"Successfully assembled {len(instructions)} instructions ({num_bytes} bytes)")
    print(f"Output written to: {output_path}")