# Badger-8 CPU Simulator

## Overview

This project is a software implementation of the **Badger-8 CPU**, an 8-bit processor simulator written entirely in Python. The simulator models fundamental computer architecture concepts from the logic gate level up to complete instruction execution.

The project demonstrates how modern processors operate by implementing arithmetic circuits, memory systems, registers, instruction fetching, decoding, execution, and clock-driven state updates.

Two CPU implementations are included:

* **Combinational CPU** – executes instructions immediately.
* **Clocked CPU** – simulates real hardware behaviour using flip-flops and clock cycles.

---

## Features

### Arithmetic Logic Unit (ALU)

The ALU supports:

* Addition
* Subtraction
* Bitwise AND
* Bitwise NOT

The ALU is built from lower-level digital logic components including:

* Half Adders
* Full Adders
* Half Subtractors
* Full Subtractors
* Multiplexers

Status flags are updated after operations:

* Carry Flag
* Zero Flag

---

### CPU Architecture

The simulator implements:

* 16 CPU registers
* Instruction Pointer (IP)
* Flags Register
* Input and Output Registers
* Code Segment (CS)
* Data Segment (DS)

The processor follows the standard:

1. Fetch
2. Decode
3. Execute

instruction cycle.

---

### Memory System

Supports:

* 64KB address space
* Binary program loading
* Memory read/write operations
* Separate current and next-state memory for clocked execution

---

### Clocked Hardware Simulation

The clocked implementation introduces hardware timing concepts through:

* Flip-Flops
* Clock Cycles
* State Propagation
* Synchronous Memory Updates

This allows the simulator to more accurately represent how real hardware behaves.

---

## Instruction Set

Supported instruction categories include:

| Category       | Description           |
| -------------- | --------------------- |
| ALU Operations | ADD, SUB, AND, NOT    |
| MOV            | Register to Register  |
| LOAD           | Memory to Register    |
| STORE          | Register to Memory    |
| Jumps          | Conditional Branching |

Conditional jumps include:

* Jump Equal (JE)
* Jump Above (JA)

---

## Key Components

### ALU

Responsible for arithmetic and logical operations.

Functions include:

* `eight_bit_add()`
* `eight_bit_sub()`
* `eight_bit_and()`
* `eight_bit_not()`
* `alu()`

### CPU

Responsible for:

* Instruction fetching
* Decoding
* Register selection
* Execution control
* Flag updates

Functions:

* `cpu()`
* `cpu_clocked()`

### Memory

Provides:

* Program storage
* Data storage
* Address decoding

Classes:

* `Memory`
* `ClockedMemory`

### Clock System

Simulates hardware timing through:

* `Clock`
* `FlipFlop`

---

## What I Learned

Developing this project required learning several core concepts from computer architecture and digital systems.

### Digital Logic Design

* Boolean algebra
* Logic gates
* Combinational circuits
* Multiplexers
* Binary arithmetic

### Arithmetic Circuits

* Half Adders
* Full Adders
* Carry propagation
* Binary subtraction
* Overflow and carry handling

### Computer Architecture

* CPU design principles
* Register files
* Memory addressing
* Fetch-Decode-Execute cycle
* Instruction encoding

### Assembly and Machine Code

* Opcode decoding
* Instruction formats
* Register addressing
* Immediate values
* Branching instructions

### Hardware Simulation

* Flip-flops
* Clock cycles
* State transitions
* Synchronous systems

### Software Engineering

* Modular programming
* Debugging complex systems
* Testing low-level functionality
* Code organisation
* Documentation

---

## Running the Simulator

Run the standard CPU:

```bash
python3 ow12.py program.bin
```

Run the clocked CPU implementation:

```bash
python3 ow12.py program.bin --clocked
```

Example:

```bash
python3 ow12.py sum_1_to_5.o --clocked
```

---

## Future Improvements

Possible extensions include:

* Additional ALU instructions
* Stack implementation
* Function call support
* Interrupt handling
* Pipelined execution
* Cache simulation
* Expanded instruction set
* Performance visualisation tools

---

## Conclusion

This project demonstrates the construction of a complete 8-bit CPU simulator from basic digital logic components through to full instruction execution. It provides practical insight into how processors operate internally and how hardware concepts such as registers, memory, ALUs, and clock cycles work together to execute machine code.
