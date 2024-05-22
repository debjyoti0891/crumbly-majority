module simpleCFG (
  input  logic i0,
  input  logic i1,
  input  logic i2,
  output logic o2
);

  // Three-input majority logic (can be reused)
  function logic three_input_majority (logic a, logic b, logic c);
    three_input_majority = (a & b) | (a & c) | (b & c);
  endfunction


  // Second-level majority (final output)
  assign o2 = three_input_majority(i0, i1, i2);

endmodule
