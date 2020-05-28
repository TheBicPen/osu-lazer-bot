#!/usr/bin/python
from sys import stdin  # can read from pipes
import ast
import pickle

d= ast.literal_eval(stdin.readline())
print(d)
out = stdin.readline()
with open(out, 'wb') as f:
    pickle.dump(d, f)