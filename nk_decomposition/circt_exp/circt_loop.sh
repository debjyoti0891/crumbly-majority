#!/bin/bash
MLIR_BIN=/Users/Shared/bhatta53/projects/upstream_llvm/circt/build/bin/circt-opt
# Iterate over n from 5 to 101 in odd steps
output_json=tcad.json
rm out.log
ARTEFACTS_DIR=artefacts
mkdir -p ${ARTEFACTS_DIR}
mv tcad.json "tcad.json.b$(date +%d%m%y%H%M)"
RES="res_$(date +%d%m%y%H%M)"
for (( n=1001; n<=1002; n+=2 ))
do
  # Generate the MLIR file with the appropriate structure using the Python script
      python3 gen_mlir_circt.py $n

  # # Iterate over k from n-5 to n in odd steps
  for k in 5 7 9 13 17 21 51 101
  do
  #   # If k is less than 5, do nothing
    if [ $k -gt $n ]; then
        echo "Skipping value: $k because $n < $k"
        continue
    fi
      # k=9

      echo $n "->" $k "synthesis in progress" | tee -a out.log
      # Run the toyc-ch7 command on the generated MLIR file
      # $MLIR_BIN -emit=mlir-synth maj$n.mlir 2> maj${n}_${k}.out | tee -a out.log
      c=$(((k + 1) / 2))
      $MLIR_BIN --maj-to-counter="counter-input-count=$c" --counter-to-maj maj_$n.mlir > maj${n}_${k}.mlir
      $MLIR_BIN --hw-dce maj${n}_${k}.mlir > maj${n}_${k}_dce.mlir
      # python3 trim_trailing_ops.py maj${n}_${k}.mlir
      $MLIR_BIN --view-op-graph maj${n}_${k}_dce.mlir > o 2> maj${n}_${k}.dot
      grep '^\s*[a-zA-Z0-9_]\+\s*\[' maj${n}_${k}.dot | grep sls > nodes
      python3 py_node_count.py nodes $n $k $output_json
  #   fi


      python3 ../mlir2c.py maj${n}_${k}_dce.mlir
      g++ hack${n}_${k}_dce.cpp -o hack${n}_${k}
      ./hack${n}_${k} > verifhack${n}_${k}
      echo -n verifhack${n}_${k} " " >> $RES
      grep PASS verifhack${n}_${k} >> $RES
      grep error verifhack${n}_${k} >> $RES

      mv maj${n}_${k}.mlir ${ARTEFACTS_DIR}
      mv maj${n}_${k}_dce.mlir ${ARTEFACTS_DIR}
      mv maj${n}_${k}.dot ${ARTEFACTS_DIR}
      mv hack${n}_${k}_dce.cpp ${ARTEFACTS_DIR}
      mv hack${n}_${k} ${ARTEFACTS_DIR}
      mv verifhack${n}_${k} ${ARTEFACTS_DIR}
      # mv maj${n}_${k}_trimmed.mlir ${ARTEFACTS_DIR}

    # fi
  done # k
  mv maj_$n.mlir ${ARTEFACTS_DIR}
done
\rm o nodes
echo "verification output: " $RES
# python3 parse_all_stats.py out.log $k
