import sys

def generate_mlir(n):
    # Create the input arguments
    inputs = [f"%arg{i}: i1" for i in range(n)]
    inputs_str = ", ".join(f"in {arg}" for arg in inputs)

    # Create the operation arguments
    op_args = ", ".join(f"%arg{i}" for i in range(n))
    op_types = ", ".join("i1" for _ in range(n))

    # Generate the MLIR content
    mlir_content = f"""module {{
    hw.module  @test({inputs_str}, out o2: i1) {{
        %o2 = sls.maj({op_args}: {op_types}) to i1
        hw.output %o2: i1
    }}
}}"""

    return mlir_content

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python generate_mlir.py <n>")
        sys.exit(1)

    try:
        n = int(sys.argv[1])
    except ValueError:
        print("Error: <n> must be an integer")
        sys.exit(1)

    if n <= 0 or n %2 == 0:
        print("Error: <n> must be a positive odd integer")
        sys.exit(1)

    mlir_content = generate_mlir(n)
    print(mlir_content)
    with open(f'maj_{n}.mlir', 'w') as f:
        f.write(mlir_content)
