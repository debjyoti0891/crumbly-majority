import cocotb
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from cocotb.clock import Clock
from cocotb.binary import BinaryValue
from cocotb.result import TestFailure
import itertools

import cocotb
from cocotb import start_soon
from cocotb.triggers import Edge, Timer, ReadOnly
import random

N = 3

def maj(inputs):
  c1 = 0
  for i in inputs:
    if i == 1:
      c1+= 1
  if c1 >= int(len(inputs)/2)+1:
    return 1
  else:
    return 0


# Predicts or calculates what the output should be
def predictor(dut):
  global N
  inputs = []
  for i in range(N):
    i_wire = getattr(dut, f'i{i}')
    inputs.append(i_wire.value)
  dut._log.info(f'checking inputs: {inputs}')
  return maj(inputs)

# Compares simulated output with predicted output
async def compare(dut):
  global N
  while 1:
    # Test on new input, then let output settle.
    attr = getattr(dut, f'i{N-1}')
    await Edge(attr)
    await ReadOnly()
    predicted = predictor(dut)
    isCorrect = (dut.o2.value == predicted)
    if not isCorrect:
      dut._log.info(f"output ({dut.o2.value}) is not as predicted: {predicted}")

    assert isCorrect



# Sets stimuli-data in DUT
async def set_stimuli(dut, vector):
  global N
  for i in range(N):
    i_wire = getattr(dut, f'i{i}')
    i_wire.value = vector[i]
  await Timer(1, units= 'ns')


# Generate all data
async def stimuli_generator(dut):
  global N
  input_combinations = list(itertools.product([0, 1], repeat=N))
  dut._log.info(f'total combinations to check: {len(input_combinations)}')
  for dut_input in input_combinations:
    await start_soon(set_stimuli(dut, dut_input))


@cocotb.test()
async def main_test(dut):
  """Try accessing the design."""
  dut._log.info("Running test...")
  start_soon(compare(dut))
  await start_soon(stimuli_generator(dut))
  dut._log.info("Running test...done")


# @cocotb.test()
# async def test_majority_function(dut):
#     # clock = Clock(dut.i0._get_drive(), 10, units="ns")  # Clock with 10ns period
#     # cocotb.fork(clock.start())

#     # Define the input signals
#     inputs = [dut.i0, dut.i1, dut.i2, dut.i3, dut.i4]

#     # Generate all possible input combinations
#     input_combinations = list(itertools.product([0, 1], repeat=len(inputs)))

#     # Iterate over all input combinations
#     for input_values in input_combinations:
#         # Set input values
#         for input_signal, value in zip(inputs, input_values):
#             input_signal = value

#         # Wait for a few clock cycles
#         await RisingEdge(dut.i0)
#         await Timer(1, units="ns")

#         # Calculate expected output
#         expected_output = (input_values[2] & input_values[3]) | \
#                           (input_values[3] & input_values[4]) | \
#                           (input_values[0] & input_values[2]) | \
#                           (input_values[0] & input_values[3]) | \
#                           (input_values[0] & input_values[4]) | \
#                           (input_values[0] & input_values[1]) | \
#                           (input_values[1] & input_values[2])

#         # Check if the output matches the expected majority function
#         if dut.o2.value.integer != expected_output:
#             raise TestFailure(f"Output does not match expected value for inputs: {input_values}")

#     # If we reached this point, all tests passed
#     dut.log.info("All tests passed!")
