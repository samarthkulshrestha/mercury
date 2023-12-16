#!/usr/bin/env python3

import sys
import subprocess


iota_count = 0


def iota(reset=False):
    global iota_count
    if reset:
        iota_count = 0
    res = iota_count
    iota_count += 1
    return res

OP_PUSH = iota(True)
OP_PLUS = iota()
OP_MINUS = iota()
OP_DUMP = iota()
COUNT_OPS = iota()


def push(x):
    return(OP_PUSH, x)


def plus():
    return(OP_PLUS, )


def minus():
    return(OP_MINUS, )


def dump():
    return(OP_DUMP, )


def simulate_program(program):
    stack = []
    for op in program:
        assert COUNT_OPS == 4, "exhaustive handling of operations in simulation."
        if op[0] == OP_PUSH:
            stack.append(op[1])
        elif op[0] == OP_PLUS:
            a = stack.pop()
            b = stack.pop()
            stack.append(a + b)
        elif op[0] == OP_MINUS:
            a = stack.pop()
            b = stack.pop()
            stack.append(b - a)
        elif op[0] == OP_DUMP:
            a = stack.pop()
            print(a)
        else:
            assert False, "unreachable."


def compile_program(program, out_fp):
    with open(out_fp, "w") as out:
        out.write("segment .text\n")

        out.write("dump:\n")
        out.write("    mov     r8, -3689348814741910323\n")
        out.write("    sub     rsp, 40\n")
        out.write("    mov     BYTE [rsp+31], 10\n")
        out.write("    lea     rcx, [rsp+30]\n")
        out.write(".L2:\n")
        out.write("    mov     rax, rdi\n")
        out.write("    mul     r8\n")
        out.write("    mov     rax, rdi\n")
        out.write("    shr     rdx, 3\n")
        out.write("    lea     rsi, [rdx+rdx*4]\n")
        out.write("    add     rsi, rsi\n")
        out.write("    sub     rax, rsi\n")
        out.write("    mov     rsi, rcx\n")
        out.write("    sub     rcx, 1\n")
        out.write("    add     eax, 48\n")
        out.write("    mov     BYTE [rcx+1], al\n")
        out.write("    mov     rax, rdi\n")
        out.write("    mov     rdi, rdx\n")
        out.write("    cmp     rax, 9\n")
        out.write("    ja      .L2\n")
        out.write("    lea     rdx, [rsp+32]\n")
        out.write("    mov     edi, 1\n")
        out.write("    sub     rdx, rsi\n")
        out.write("    mov     rax, 1\n")
        out.write("    syscall\n")
        out.write("    add     rsp, 40\n")
        out.write("    ret\n")

        out.write("\n")
        out.write("global _start\n")
        out.write("_start:\n")

        for op in program:
            assert COUNT_OPS == 4, "exhaustive handling of operations in simulation."
            if op[0] == OP_PUSH:
                out.write(f"    ;; push {op[1]} ;;\n")
                out.write(f"    push    {op[1]}\n")
            elif op[0] == OP_PLUS:
                out.write(f"    ;; plus ;;\n")
                out.write(f"    pop     rax\n")
                out.write(f"    pop     rbx\n")
                out.write(f"    add     rax, rbx\n")
                out.write(f"    push    rax\n")
            elif op[0] == OP_MINUS:
                out.write(f"    ;; minus ;;\n")
                out.write(f"    pop     rax\n")
                out.write(f"    pop     rbx\n")
                out.write(f"    sub     rbx, rax\n")
                out.write(f"    push    rbx\n")
            elif op[0] == OP_DUMP:
                out.write(f"    ;; dump ;;\n")
                out.write(f"    pop     rdi\n")
                out.write(f"    call    dump\n")
            else:
                assert False, "unreachable."

        out.write("\n")
        out.write("    mov     rax, 60\n")
        out.write("    mov     rdi, 0\n")
        out.write("    syscall\n")


def parse_word_as_op(wd):
    assert COUNT_OPS == 4, "exhaustive handling of operations in simulation."

    if wd == '+':
        return plus()
    elif wd == '-':
        return minus()
    elif wd == '.':
        return dump()
    else:
        return push(int(wd))

def load_prgm_from_file(fp):
    with open(fp, "r") as f:
        return [parse_word_as_op(word) for word in f.read().split()]

def usage(program_name):
        print(f"usage: {program_name} <subcommand> [args]")
        print("subcommands:")
        print("    sim <file>    run the program in simulation mode.")
        print("    com <file>    run the compiler.")

def call_cmd(cmd):
    print(' '.join(cmd))
    subprocess.call(cmd)

def uncons(xs):
    return (xs[0], xs[1:])


if __name__ == "__main__":
    argv = sys.argv
    assert len(argv) >= 1
    (program_name, argv) = uncons(argv)

    if len(argv) < 1:
        usage(program_name)
        print("\nerror: no subcommand provided")
        exit(1)

    (subcommand, argv) = uncons(argv)

    if subcommand == "sim":
        if len(argv) < 1:
            usage(program_name)
            print("\nerror: argument required")
            exit(1)

        (input_fp, argv) = uncons(argv)
        program = load_prgm_from_file(input_fp);
        simulate_program(program)

    elif subcommand == "com":
        if len(argv) < 1:
            usage(program_name)
            print("\nerror: argument required")
            exit(1)

        (input_fp, argv) = uncons(argv)
        program = load_prgm_from_file(input_fp);
        compile_program(program, "output.asm")

        call_cmd(["nasm", "-felf64", "output.asm"])
        call_cmd(["ld", "output.o", "-o", "output"])
    else:
        usage()
        print(f"\nerror: unknown subcommand - {subcommand}")
        exit(1)
