from term import *
from kind import Variable, ObjectTypeRelation, Constant, Operator
from dm import *
from cmpl_new import cmpl

term = Application(composition, [ ligtin, woontop ])

compiled_term = cmpl(term)
print(repr(compiled_term))
compiled_term.freeze()
print(repr(compiled_term))
