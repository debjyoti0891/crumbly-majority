import datetime 
import math
import argparse
import os

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
        if enable_file_write:
            module_file.write(f'assign {self.name} = {another_wire.name};\n')
    
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

        for v in [a.name, b.name, c.name]:
            print(f'{v} ', end='')
        print(f'-> {self.sum.name} {self.c_out.name}')
        
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
    

def print_specialized_header(input_var, n_bits, real_bits, thresh_var, m_bits, thresh_val, const_var, output_var):
    '''
    Print the header for a specialized majority implementation. This can be used only
    for the specific Maj m_bits computation.
    Args:
        input_var (string|list): Input variable (either a list for bits or a single value if it is a bit-vector)
        n_bits (int): Number of bits for the threshold circuit
        real_bits (int): Actual number of bits implementing majority! (real_bits <= n_bits)
        thresh_var (string|list): Threshold variable (either a list for bits or a single value if it is a bit-vector)
        m_bits (int): Number of bits for the majority circuit
        thresh_val (int|list): Counter value (either an int or a list of bits)
        const_var  (string): Name of the constant variable
        output_var (string): Name of the output variable
    '''
    global module_file, enable_file_write
    if enable_file_write:
        h = f'// Module to compute majority with {real_bits} bits \n'
        h = h + f'// Created on {datetime.datetime.now()} \n'
        h = h + f'module Maj{real_bits}(\n'
        if type(input_var) == list:
            for i in input_var[:real_bits]:
                h = h + f'{i},\n'
        else:
            h = h + f' [{n_bits}:0] {input_var},\n'
        h = h + f'{output_var});\n'

        # print the inputs here!
        h = h + 'input '
        if type(input_var) == list:
            for i in input_var[:real_bits]:
                h = h + f' {i},'
                print(f'node {i} [label = {i}]')
        else:
            h = h + f' input [{n_bits}:0] {input_var},'
        
        

        h = h[:-1] + ';\n'
        h = h + f'output {output_var};\n'

        
        if type(input_var) == list and n_bits > real_bits:
            h = h + f'// unused inputs from the threshold circuit (with {n_bits})\n'
            for i in input_var[real_bits:]:
                h = h + f'wire {i}; assign {i} = 0;\n'
                print(f'node {i} [label = 0]')

        
        if type(thresh_var) == list:
            for i, v in enumerate(thresh_var):
                h = h + f'wire {v};\n'
                h = h + f'assign {v} = {thresh_val[i]};\n'
                print(f'node {v} [label = {thresh_val[i]}]')
        else:
            h = h + f'wire [{m_bits}:0] {thresh_var};\n'
            assert type(thresh_val) == int, "Threshold value {thresh_val}should be int"
            h = h + f'assign {thresh_var} = {thresh_val};\n'

        h = h + f'wire {const_var}; '
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
def parallel_stuff(n_bits, real_bits, m_bits, specialize = False, val_n = None, val_thresh = None):
    '''
    Print the header for a specialized majority implementation. This can be used only
    for the specific Maj m_bits computation.
    Args:
        n_bits (int): Number of bits for the threshold circuit
        thresh_var (string|list): Threshold variable (either a list for bits or a single value if it is a bit-vector)
        real_bits (int): Number of bits for the majority circuit
        m_bits (int): Number of bits for the counter 
        specialize (bool): Specialized majority circuit (cannot be used as threshold circuit)
        val_n (list): List of binary values of the input 
        val_thresh (int): Counter value
    '''
    global module_file, enable_file_write, adder_index
    global passing
    # n_bits = 15, m_bits = 4 + 1
    depth = m_bits 
    if val_n is None:
        val_n = [0 for i in range(n_bits)]
    if val_thresh is None:
        val_thresh = [0 for j in range(m_bits)]
    
    output_var = "F0"
    output = Wire(output_var)
    const_var = 'const1'

    if not specialize:
        input_var = "xin"
        inputs = [Wire(f'{input_var}[{i}]', val_n[i]) for i in range(n_bits)] + [Wire(const_var, 1)]
    else:
        inputs = []
        prefix = 'x'
        for i in range(n_bits):
            if i < 26:
                inputs.append(Wire(f'{chr(97+i)}', val_n[i]))
            else:
                inputs.append(Wire(f'x{i}', val_n[i]))
        inputs = inputs + [Wire(const_var, 1)]
        input_wires = [t.name for t in inputs[:-1]]
    
    thresh_var = "th"
    if not specialize:
        comp_val = [Wire(f'{thresh_var}[{i}]', val_thresh[i]) for i in range(m_bits)]
    else:
        comp_val = [Wire(f'{thresh_var}{i}', val_thresh[i]) for i in range(m_bits)]
        thresh_wires = [t.name for t in comp_val]    

    if module_file is not None:
        enable_file_write = True

        if specialize:
            print_specialized_header(input_wires, n_bits, real_bits, thresh_wires, m_bits, val_thresh, const_var, output_var)
        else:
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
        
        assert maj_circ == maj, 'Invalid output'
        
    print(f"{fin_output[-1].name} = {output.name};") 
    output.set_wire_val(fin_output[-1])
    print_footer()
    return adder_index


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
    

def verify_with_abc(bits, gen_file_name):

    abc_command = 'symfun '
    sym_out = ''
    for i in range(bits+1):
        if i < int(bits/2)+1:
            sym_out = sym_out + '0'
        else:
            sym_out = sym_out + '1'
    abc_command = abc_command + sym_out + '\n'
    abc_command = abc_command + f'st\n clp\n muxes\n st\n ps\n write_verilog m{bits}.v\n cec -n m{bits}.v {gen_file_name}\nquit\n'
    
    with open(gen_file_name, 'w') as f:
        f.write(abc_command)
    # p = subprocess.Popen('abc -F abc_script.txt', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # print(p.communicate())
    # # print('error', error)

def dump_rewrite(in_file):
    all_str = ''
    head = ''
    body = ''
    
    with open(in_file) as f:
        state = 0
        for l in f:
            if state == 0:
                head = head + l 
                if 'output ' in l:
                    state = 1
                    continue
            
            if state == 1:
                if 'wire ' in l:
                    w_s = l.find('wire')
                    w_sub = l[w_s : ]
                    w_e = w_sub.find(';')
                    rest = l[:w_s] + w_sub[w_e+1:]
                    body = body + rest 
                    all_str = all_str + w_sub[w_s:w_e+1] + '\n'
                else:
                    body = body + l 

    with open(in_file, 'w') as f:
        f.write(head + all_str + body)


            
        

if __name__ == "__main__": # pragma: no cover
    parser = argparse.ArgumentParser()
    parser.add_argument("maj_bits", type=int, help="Number of bits for majority")
    parser.add_argument("-c", "--check_abc", action="store_true", help="Generate ABC commands to verify", default=False)
    parser.add_argument("-o", "--output_dir", help="Location of the output directory")
    args = parser.parse_args()
    
    # circ_bits is always 2*n - 1
    check_bits = args.maj_bits + 1
    if (check_bits & (check_bits-1) == 0) and check_bits != 0:
        circ_bits = args.maj_bits # the number of bits the circuit is created for
    else:
        circ_bits = 2**(int(math.log2(args.maj_bits))+1) - 1
    bits = args.maj_bits # the number of bits majority function 
    
    counter_bits = int(math.log2(circ_bits + 1))
    cval = 2**counter_bits - (int(bits/2) + 1) - 1
    counter_val = [int(i) for i in list(str(bin(cval))[2:])] 
    counter_val.reverse()
    counter_val = counter_val + [0 for i in range(counter_bits - len(counter_val))]
    specialize = True
    if args.output_dir is not None:
        if not os.path.isdir(args.output_dir):
            os.mkdir(args.output_dir)
        out_dir = args.output_dir
        if out_dir[:-1] != '/':
            out_dir = out_dir + '/'
    else:
        out_dir = './'
    gen_file_name = f'{out_dir}maj_{bits}.v'
    
    module_file = open(gen_file_name, 'w')
    adder_count = parallel_stuff(circ_bits, bits, counter_bits, specialize, None, counter_val)
    module_file.close()
    print(f'//circ_bits: {circ_bits},real_bits: {bits},counter_bits: {counter_bits},counter val:{cval},adders:{adder_count}')
    if args.check_abc:
        verify_with_abc(bits, gen_file_name)

    dump_rewrite(gen_file_name)

    ## test wires and sum
    # a, b, c = Wire('a', 1), Wire('b', 1), Wire('c', 0)
    # m_s1= Sum('s1')
    # s,cout = m_s1.comp(a, b, c)

    # d = Wire('d', 1)
    # m_s2= Sum('s2')
    # s1,cout1 = m_s2.comp(s, cout, d)

    
    # ## when  2*counter_bits - maj_count - 1 is the counter val ( eg 15 circ maj 7 -> counter val = 2*4 - 4 - 1 = 11)
    # bits = 7 # the number of bits majority function 
    # circ_bits = 7 # the number of bits the circuit is created for
    # counter_bits = int(math.log2(circ_bits + 1))
    # counter_val = [int(i) for i in list(str(bin(2**counter_bits - int(bits/2 + 1) - 1))[2:])] 
    # counter_val = counter_val + [0 for i in range(counter_bits - len(counter_val))]
    # specialize = True

    # print(counter_bits, counter_val)

    # # bits = 7
    # # circ_bits = 15
    # # counter_bits = 4
    # # counter_val = [1,1,0,1] 
    # # specialize = True

    # ## this is for testing correctness
    # # for i in range(2**bits):
    # #     val = bin(i)
    # #     v = str(val)[2:]
    # #     v = '0'*(circ_bits-len(v)) + v
    # #     q = [int(v_n) for v_n in v]
    # #     print(f'// maj_res {i} , {q}')
    # #     # q = [0, 0, 0, 0, 0, 0, 1]
    # #     parallel_stuff(circ_bits, bits, counter_bits, specialize q, counter_val)

    # ## this is to generate the module
    # gen_file_name = f'maj_{bits}.v'
    # module_file = open(gen_file_name, 'w')
    # parallel_stuff(circ_bits, bits, counter_bits, specialize, None, counter_val)
    # # int_counter_val = sum([val*(2**i) for i,val in enumerate(counter_val)])
    # # generate_tb(bits, circ_bits, counter_bits, int_counter_val, test_count=None)

    # verify_with_abc(bits, gen_file_name)