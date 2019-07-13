#!/usr/bin/python
import sys
import ast
import pickle
import io
d = {}
d= ast.literal_eval(sys.stdin.readline())
print(d)
out = sys.stdin.readline()
f = io.open(out, 'wb')
pickle.dump(d, f)
f.close()