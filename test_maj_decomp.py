import os
import maj_decomp as md
import math

def test_wire_assignment():
    a = md.Wire('a', 1)
    a.set_computed_val(10)
    assert a.val == 10
    a.set_wire_val(md.Wire('b', 2))
    assert a.val == 2

def generate_test(circ_bits, bits, exec_sim=None, sp=False):
    # runs exhaustive tests for majority_{bits} using threshold circuits with {circ_bits}
    counter_bits = int(math.log2(circ_bits + 1))
    cval = 2**counter_bits - (int(bits/2) + 1) - 1
    counter_val = [int(i) for i in list(str(bin(cval))[2:])] 
    counter_val.reverse()
    counter_val = counter_val + [0 for i in range(counter_bits - len(counter_val))]
    specialize = sp
    if exec_sim is not None:
        for i in range(2**bits):
            val = bin(i)
            v = str(val)[2:]
            v = '0'*(circ_bits-len(v)) + v
            q = [int(v_n) for v_n in v]
            md.parallel_stuff(circ_bits, bits, counter_bits, specialize, q, counter_val)
    else:
        md.parallel_stuff(circ_bits, bits, counter_bits, specialize, None, counter_val)
        
def test_maj_7():
    generate_test(7, 7)

def test_maj_15():
    generate_test(15, 7)

def test_maj_13():
    generate_test(15, 13)

def test_maj_7_using_15circ():
    generate_test(15, 7)

def test_general_thresh():
    circ_bits = bits = 7
    specialize = True
    generate_test(circ_bits, bits, None, specialize)

def test_general_thresh(tmp_path):
    out_name = str(tmp_path) + 'thresh_t7_c3.v'
    md.module_file = open(out_name, 'w')
    circ_bits = bits = 7
    specialize = False
    generate_test(circ_bits, bits, None, specialize)
    assert os.path.isfile(out_name)

def test_specialized_thresh(tmp_path):
    out_name = str(tmp_path) + 'thresh_t7_m5_c3.v'
    md.module_file = open(out_name, 'w')
    circ_bits = 7
    bits = 7
    specialize = True
    generate_test(circ_bits, bits, None, specialize)
    assert os.path.isfile(out_name)

def test_specialized_thresh_large(tmp_path):
    out_name = str(tmp_path) + 'thresh_t1023_m711_c3.v'
    md.module_file = open(out_name, 'w')
    circ_bits = 1023
    bits = 711
    specialize = True
    generate_test(circ_bits, bits, None, specialize)
    assert os.path.isfile(out_name)

def test_tb_gen(tmp_path):
    circ_bits = bits = 7
    counter_bits = 3
    counter_val = [1,1,0]
    md.generate_tb(bits, circ_bits, counter_bits, counter_val)

def test_abc_script_gen(tmp_path):
    bits = 7
    gen_file_name = str(tmp_path) + 'abc_script.txt'
    md.verify_with_abc(bits, gen_file_name)
    assert os.path.isfile(gen_file_name)
