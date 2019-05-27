from term import *
from kind import Variable, ObjectTypeRelation, Constant, Operator
from dm import *
from cmpl_new import cmpl
from cmpl_new_test import  test_terms

if False:
    term = Application(composition, [ ligtin, woontop ])

    compiled_term = cmpl(term)
    print(repr(compiled_term))
    compiled_term.freeze()
    print(repr(compiled_term))

terms = [
[
Application(product, [ inkomen, leeftijd ]),
"""\
"""], [
Application(composition, [ ligtin, woontop ]),
"""\
"""
], [
Application(inclusion, [ inkomen, leeftijd ]),
"""\
"""
], [
Application(alpha, [ inkomen, geslacht ]),
"""\
"""
], [
    Application(product, [
        Application(composition, [
            inkomen,
            Application(inclusion, [
                Application(composition, [ gemeentenaam, ligtin, woontop ]),
                Application(composition, [ leiden, allepersonen ])        
            ])
        ]),
        Application(composition, [
            woontop,
            Application(inclusion, [
                Application(composition, [ gemeentenaam, ligtin, woontop ]),
                Application(composition, [ leiden, allepersonen ])        
            ])
        ])
    ]),
"""\
"""
]
]

test_terms(terms)
