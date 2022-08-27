
# Online Python - IDE, Editor, Compiler, Interpreter
import datetime 
import sys 

module_file = None 
enable_file_write = False
class Wire:
    def __init__(self, name, val=0):
        global module_file, enable_file_write
        self.name = name 
        self.val = val 
        if enable_file_write: module_file.write(f'wire {self.name}; \n')
        
    def set_wire_val(self, another_wire):
        global module_file, enable_file_write
        self.val = another_wire.val 
        if enable_file_write: module_file.write(f'assign {self.name} = {another_wire.name};\n')
    
    def set_computed_val(self, value):
        self.val = value 

class Sum:
    def __init__(self, mod_name):
        self.__name = mod_name 
        self.sum = Wire(self.__name+'sum')
        self.c_out = Wire(self.__name+'cout')
        
    def comp(self, a, b, c):
        global module_file, enable_file_write
        self.sum.set_computed_val(a.val ^ b.val ^ c.val)
        self.c_out.set_computed_val((a.val & b.val) | ( c.val & (a.val ^ b.val)))
        if enable_file_write: 
            module_file.write(f"assign {self.sum.name} = {a.name} ^ {b.name} ^ {c.name}; ")
            module_file.write(f"assign {self.c_out.name} = (({a.name} & {b.name}) | ( {c.name} & ({a.name} ^ {b.name})));\n")

        return self.sum, self.c_out
        
def print_header(input_var, n_bits, thresh_var, m_bits, const_var, output_var):
    global module_file, enable_file_write
    if enable_file_write:
        h = f'// Module to compute majority with {n_bits} bits \n'
        h = h + f'// Created on {datetime.datetime.now()} \n'
        h = h + f'module Maj{n_bits}(\n'
        h = h + f'input [{n_bits}:0] {input_var},\n'
        h = h + f'input [{m_bits}:0] {thresh_var},\n'
        h = h + f'output {output_var});\n'
        

        h = h + f'wire {const_var};\n'
        h = h + f'assign {const_var} = 1;\n'
    
        module_file.write(h)

def print_footer():
    global module_file, enable_file_write
    if enable_file_write:
        module_file.write('endmodule')

adder_index = 0
def this_level_add(o0, o1, bit, level):
    global module_file, enable_file_write
    global adder_index
    out = []
    carry = None 
    for i in range(len(o0)):
            
        a = o0[i]
        b = o1[i]
        if i == 0:
            c =  bit 
        else:
            c = carry
        adder_index = adder_index + 1
        s = Sum(f'L{level}_FA_{adder_index}')
        sum,carry = s.comp(a, b, c)
        out.append(sum)
    out.append(carry)
    return out

def level_add(inputs, level):
    global module_file, enable_file_write
    # print(f'level: {level} | len: {len(inputs)}')
    # [print(f'{i.name} ', end='') for i in inputs]
    # print('\n')
    if len(inputs) <= 3: 
        if enable_file_write: module_file.write(f'\n\n// Level {level} adders|\n')
        return this_level_add([inputs[0]], [inputs[1]], inputs[-1], level-1)
    else:
        split = int(len(inputs)/2)
        output_0 = level_add(inputs[0:split], level - 1)
        output_1 = level_add(inputs[split:-1], level - 1)
        if enable_file_write: module_file.write(f'\n\n// Level {level} adders\n')
        return this_level_add(output_0, output_1, inputs[-1], level)

def compare(outputs, comp_val, last_bit, level):
    global module_file, enable_file_write
    if enable_file_write: module_file.write('\n// comparison adders\n')
    # import pdb; pdb.set_trace()
    return this_level_add(outputs, comp_val, last_bit, level)

passing = 0
def parallel_stuff(n_bits, real_bits, m_bits, val_n = None, val_thresh = None):
    global module_file, enable_file_write
    global passing
    # n_bits = 15, m_bits = 4 + 1
    depth = m_bits 
    if val_n is None:
        val_n = [0 for i in range(n_bits)]
    if val_thresh is None:
        val_thresh = [0 for j in range(m_bits)]
    input_var = "xin"
    thresh_var = "th"
    output_var = f"out_maj_{n_bits}"
    const_var = 'const1'
    inputs = [Wire(f'{input_var}[{i}]', val_n[i]) for i in range(n_bits)] + [Wire(const_var, 1)]
    
    comp_val = [Wire(f'{thresh_var}[{i}]', val_thresh[i]) for i in range(m_bits)]
    output = Wire(output_var)
    
    if module_file is not None:
        enable_file_write = True
        print_header(input_var, n_bits, thresh_var, m_bits, const_var, output_var)

    # create all the adders! 
    adder_tree = []
    level = m_bits - 1
    outputs = level_add(inputs[:-1], level)
    count_1s = val_n.count(1)
    maj = int(real_bits/2) + 1 <= count_1s # Higher bit count circuit can be used for smaller operation with a different threshold
   
    if val_n is not None:
        print('//', end='')
        count_circ = 0
        for i,o in enumerate(outputs):
            print(f" {o.val}", end = '')
            count_circ = count_circ + (o.val * 2**i)
        print()
        print(f'// maj_res {count_1s} {maj} {count_circ}')
        
    fin_output = compare(outputs, comp_val, inputs[-1], level+1)
    if val_n is not None:
        print(f'//{len(outputs)}', end='')
        for o in fin_output:
            print(f" {o.val}", end = '')
        print()
        maj_circ = (fin_output[-1].val == 1)
        if maj_circ == maj:
            passing = passing + 1
        print(f'// maj_res {fin_output[-1].val}| {maj_circ} | {maj} -> {passing}')
        
        assert maj_circ == maj , 'Invalid output'
        
        
    output.set_wire_val(fin_output[-1])
    print_footer()

def generate_tb(bits, circ_bits, counter_bits, counter_val, test_count=None):
    # generates a test bench for Maj_bits checking on a circuit with Maj_circ_bits implementation
    f = open(f'stim_M{bits}_{circ_bits}.v', 'w')
    h = '`timescale 1ns / 1ps\n\n'
    h = h + f'module stim_M{bits}_{circ_bits}; \n// Inputs/Outputs \nreg [{circ_bits}:0] xin;\n reg [{counter_bits}:0] th;\n wire out;\n '
    h = h + '// instantiate DUT\n'
    h = h + f'Maj{circ_bits} dut( .xin(xin), .th(th), .out_maj_{circ_bits}(out));\n'

    h = h + 'initial begin \n'
    # drive the inputs 
    h = h + f'th = {counter_val};\n'
    h = h + f'xin = 0;\n\n'
    if (test_count == None):
        test_count = 2**bits 
    
    for i in range(2**bits):
        h = h + f'#10 xin = {i};\n'
    
    h = h + 'end\n\n'

    h = h + 'initial begin \n $monitor("t=%3d xin=%2b,th=%2b,maj=%d\\n",$time,xin,th,out);\n end\n'

    h = h + 'endmodule\n'
    f.write(h)
    f.close()


if __name__ == "__main__":
    ## test wires and sum
    # a, b, c = Wire('a', 1), Wire('b', 1), Wire('c', 0)
    # m_s1= Sum('s1')
    # s,cout = m_s1.comp(a, b, c)

    # d = Wire('d', 1)
    # m_s2= Sum('s2')
    # s1,cout1 = m_s2.comp(s, cout, d)

    
    ## when  2*counter_bits - maj_count - 1 is the counter val ( eg 15 circ maj 7 -> counter val = 2*4 - 4 - 1 = 11)
    bits = 7 # the number of bits majority function 
    circ_bits = 7 # the number of bits the circuit is created for
    counter_bits = 3
    counter_val = [1,1,0] 


    # bits = 7
    # circ_bits = 15
    # counter_bits = 4
    # counter_val = [1,1,0,1] 

    ## this is for testing correctness
    # for i in range(2**bits):
    #     val = bin(i)
    #     v = str(val)[2:]
    #     v = '0'*(circ_bits-len(v)) + v
    #     q = [int(v_n) for v_n in v]
    #     print(f'// maj_res {i} , {q}')
    #     # q = [0, 0, 0, 0, 0, 0, 1]
    #     parallel_stuff(circ_bits, bits, counter_bits, q, counter_val)

    ## this is to generate the module
    module_file = open(f'maj_{circ_bits}.v', 'w')
    parallel_stuff(circ_bits, bits, counter_bits)
    int_counter_val = sum([val*(2**i) for i,val in enumerate(counter_val)]
    generate_tb(bits, circ_bits, counter_bits, int_counter_val, test_count=None)


    