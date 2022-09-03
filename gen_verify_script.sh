for i in $(seq 5 2 52)
do
    \rm data
    python3 maj_decomp.py $i -o tcad > data
    python3 mock.py data majority_syn.hpp $i
    # python3 abc_gen.py tcad $i
    # abc -F abc_script.txt

    # abc -F abc_script.txt
done

# mkdir -p op1_tcad
# mkdir -p op2_tcad
# for file in `ls tcad/*.v`
# do
    
#     echo "read_genlib majority2.genlib;read $file; st; &get; &nf -R 1000; &put; ps; pg; write_verilog op1_${file}" > abc_script_1
#     abc -F abc_script_1 >> v1
#     echo "read_genlib majority2.genlib;read $file; st; map -a; ps; pg; write_verilog op2_${file}" > abc_script_2
#     abc -F abc_script_2 >> v2
#     echo Processed $file
#     \rm abc_script_1 \abc_script_2
# done