#!/usr/bin/env python3

import sys
import os

if __name__ == "__main__":
    existing_args = []

    for arg in sys.argv[1:]:
        if os.path.exists(arg):
            existing_args.append(arg)
        else:
            print("No such file: {}".format(arg),
                  file=sys.stderr)

    for arg in existing_args:
        with open(arg, 'rU') as infil:
            for (num, ln) in enumerate(infil, start=1):
                print("{ln!s: >5} {txt}".format(ln=num, txt=ln), end='')
