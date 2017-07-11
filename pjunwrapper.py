import sys
import os
import marshal
import dis
import pystack
import argparse

turn_on = False
idx = 0
max_depth = 0

def trace(frame, event, arg):
    global turn_on, idx
    if event == 'line':
        # Get the code object
        co_object = frame.f_code

        # Retrieve the name of the associated code object
        co_name = co_object.co_name
        if turn_on or co_name == '<pjorion_protected>':
            turn_on = True

            # Get the code bytes
            co_bytes = co_object.co_code

            # f_lasti is the offset of the last bytecode instruction executed
            # w.r.t the current code object
            # For the very first instruction this is set to -1
            ins_offs = frame.f_lasti

            if ins_offs >= 0:
                opcode = ord(co_bytes[ins_offs])

                # Check if it is a valid opcode
                if opcode == dis.opmap['EXEC_STMT']:
                    idx += 1
                    f = open('wrapper_'+str(idx)+'.pyc', 'wb')
                    f.write('\x03\xF3\x0D\x0A\0\0\0\0')
                    marshal.dump(pystack.getStackItem(frame, 2), f)
                    f.close()
                    print '[*] Dumped 1 code object'
                    if idx == max_depth:
                        sys.settrace = None
    return trace


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--ifile', help='Input pyc file name', required=True)
    parser.add_argument('-d', '--depth', help='Maximum dumping depth, defaults to unlimited.', required=False, type=int, default=0)
    args = parser.parse_args()
    max_depth = args.depth
    f = open(args.ifile, 'rb')
    f.seek(8)
    co=marshal.load(f)
    sys.settrace(trace)
    eval(co)
