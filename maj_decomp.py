
# Online Python - IDE, Editor, Compiler, Interpreter
import datetime 

class Wire:
    def __init__(self, name, val=0):
        self.name = name 
        self.val = val 
        print(f'wire {self.name};')
        
    def set_wire_val(self, another_wire):
        self.val = another_wire.val 
        print(f'assign {self.name} = {another_wire.name};')
    
    def set_computed_val(self, value):
        self.val = value 

class Sum:
    def __init__(self, mod_name):
        self.__name = mod_name 
        self.sum = Wire(self.__name+'sum')
        self.c_out = Wire(self.__name+'cout')
        
    def comp(self, a, b, c):
        self.sum.set_computed_val(a.val ^ b.val ^ c.val)
        print(f"assign {self.sum.name} = {a.name} ^ {b.name} ^ {c.name};")
        
        self.c_out.set_computed_val((a.val & b.val) | ( c.val & (a.val ^ b.val)))
        print(f"assign {self.c_out.name} = (({a.name} & {b.name}) | ( {c.name} & ({a.name} ^ {b.name})));")

        # print(f's:{self.sum.val}, c:{self.c_out.val}')
        return self.sum, self.c_out
        
def sum(a, b):
    return (a + b)

# a, b, c = Wire('a', 1), Wire('b', 1), Wire('c', 0)
# m_s1= Sum('s1')
# s,cout = m_s1.comp(a, b, c)

# d = Wire('d', 1)
# m_s2= Sum('s2')
# s1,cout1 = m_s2.comp(s, cout, d)
def print_header(inputs, comp_val, out):
    h = f'// Module to compute majority with {len(inputs)-1} bits \n'
    h = h + f'// Created on {datetime.datetime.now()} \n'
    h = h + 'module Maj(\n'
    for i in inputs[:-1]:
        h += f'\tinput {i.name}, \n'
    
    for i in comp_val:
        h += f'\tinput {i.name}, \n'
    
    h = h + f'\toutput {out.name});\n'

    h = h + f'wire {inputs[-1].name};\n'
    h = h + f'assign {inputs[-1].name} = 1;\n'
    print(h)

def print_footer():
    print('endmodule')

adder_index = 0
def this_level_add(o0, o1, bit, level):
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
    # print(f'level: {level} | len: {len(inputs)}')
    # [print(f'{i.name} ', end='') for i in inputs]
    # print('\n')
    if len(inputs) <= 3: 
        print(f'\n\n// Level {level} adders')
        return this_level_add([inputs[0]], [inputs[1]], inputs[-1], level)
    else:
        split = int(len(inputs)/2)
        output_0 = level_add(inputs[0:split], level - 1)
        output_1 = level_add(inputs[split:-1], level - 1)
        print(f'\n\n// Level {level} adders')
        return this_level_add(output_0, output_1, inputs[-1], level)

def compare(outputs, comp_val, last_bit, level):
    print('\n// comparison adders')
    return this_level_add(outputs, comp_val, last_bit, level)


def parallel_stuff(n_bits, m_bits):
    # n_bits = 15, m_bits = 4 + 1
    depth = m_bits 
    print('\n')
    inputs = [Wire(f'x{i}') for i in range(n_bits)] + [Wire('l1', 0)]
    print('\n')
    comp_val = [Wire(f't{i}') for i in range(m_bits)]
    output = Wire(f'out_maj_{n_bits}')
    print('\n')

    print_header(inputs, comp_val, output)

    # create all the adders! 
    adder_tree = []
    level = m_bits - 1
    outputs = level_add(inputs[:-1], 3)
    fin_output = compare(outputs, comp_val, inputs[-1], level+1)
    output.set_wire_val(fin_output[-1])
    print_footer()
    
parallel_stuff(15, 4)

    