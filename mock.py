import sys 
import os
node_info =dict()
def val_n(node):
    global node_info
    if node not in node_info:
        return node
    if node_info[node] == '1' or node_info[node] == '0': 
        return 'const'+ node_info[node]
    else:
        return node 

def mock(file_name, out_name, n):
    global node_info
    exists = os.path.isfile(out_name)
    outf = open(out_name, 'a') 
    if not exists:
        outf.write('#pragma once \n#include <mockturtle/networks/mig.hpp>\nusing namespace mockturtle; \n\n')
    outf.write(f'\n auto create_maj_{n}(mig_network &mig) ->void '+'{\n auto const1 = mig.get_constant(true); auto const0 = mig.get_constant(false);\n\n')
    var_count = 0
    with open(file_name) as f:
        node_info = dict()

        for l in f:
            # do stuff
            if 'node' in l:
                # this is a node 
                l = l.split(' ')
                name = l[1].strip()
                val = l[-1].strip()[:-1]
                # print(name, val, val=='0', val=='1')
                node_info[name] = val

                if val != '0' and val != '1':
                    outf.write(f'auto {name} = mig.create_pi("{name}");\n')
            elif '//' in l:
                continue
            elif '->' in l: 
                i = l.find('->') 
                vars = l[:i].strip().split()
                out = l[i+2:].strip().split()
                # print(vars, out)
                var_count = var_count + 1 
                outf.write(f'auto v{var_count} = mig.create_maj(!{val_n(vars[0])}, {val_n(vars[1])}, {val_n(vars[2])});\n')
                outf.write(f'auto {out[1]} = mig.create_maj({val_n(vars[0])}, {val_n(vars[1])}, {val_n(vars[2])});\n')
                outf.write(f'auto {out[0]} = mig.create_maj({val_n(vars[0])}, v{var_count}, !{out[1]});\n')
            elif '=' in l:
                val = l.strip().split()[0]
                v2 = l.strip().split()[-1][:-1]
                outf.write(f'mig.create_po( {val}, "{v2}" );\n')
    outf.write('}')
    outf.close()
                


if __name__ == '__main__':
    if(len(sys.argv) < 4):
        print('python3 mock.py data majority.hpp maj_n')
    mock(sys.argv[1],  sys.argv[2], sys.argv[3])
