for i in $(seq 5 2 26)
do
    python3 maj_decomp.py $i -c
    abc -F abc_script.txt
done