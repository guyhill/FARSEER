from term import *
from kind import Variable, ObjectTypeRelation, Constant, Operator
from dm import *
from cmpl_new import cmpl

def test_terms_old(terms, expected_output):
    errors = False
    for i, term in enumerate(terms):
        cterm = cmpl(term)
        output = repr(cterm)
        if i >= len(expected_output) or expected_output[i] != output:
            print(term)
            print(cterm)
            print()
            if i < len(expected_output):
                errors = True
    if not errors:
        print("all tests pass")

def test_terms(terms):
    error = False
    for term in terms:
        output = repr(cmpl(term[0]))
        expected = term[1]
        if output != expected:
            msg = ("======test failed===========\n" +
                  repr(term[0]) + "\n\n" +
                  "Output:\n" +
                  output + "\n\n" +
                  "Expected output:\n" +
                  expected )
            print(msg)
            error = True
    if not error:
        print("all tests passed")
                


terms = [ 
[   # object type relation
woontop, 
"""\
SELECT persoon.persoon_id, persoon.woont_op
FROM persoon\
""" ], [          
ligtin,
"""\
SELECT adres.adres_id, adres.ligt_in
FROM adres\
""" ], [
Application(composition, [ ligtin, woontop ]),
"""\
SELECT persoon.persoon_id, persoon_woont_op.ligt_in
FROM persoon
JOIN (adres AS persoon_woont_op) ON (persoon_woont_op.adres_id = persoon.woont_op)\
""" ], [
Application(composition, [ ligtin, gevestigdop, werkgever ]),
"""\
SELECT baan.baan_id, baan_werkgever_gevestigd_op.ligt_in
FROM baan
JOIN (bedrijf AS baan_werkgever) ON (baan_werkgever.bedrijf_id = baan.werkgever)
JOIN (adres AS baan_werkgever_gevestigd_op) ON (baan_werkgever_gevestigd_op.adres_id = baan_werkgever.gevestigd_op)\
""" ], [
Application(composition, [
    ligtin,
    Application(composition, [ gevestigdop, werkgever ])
]),
"""\
SELECT baan.baan_id, baan_werkgever_gevestigd_op.ligt_in
FROM baan
JOIN (bedrijf AS baan_werkgever) ON (baan_werkgever.bedrijf_id = baan.werkgever)
JOIN (adres AS baan_werkgever_gevestigd_op) ON (baan_werkgever_gevestigd_op.adres_id = baan_werkgever.gevestigd_op)\
""" ], [
Application(composition, [
    Application(composition, [ ligtin, gevestigdop ]),
    werkgever
]),
"""\
SELECT baan.baan_id, baan_werkgever_gevestigd_op.ligt_in
FROM baan
JOIN (bedrijf AS baan_werkgever) ON (baan_werkgever.bedrijf_id = baan.werkgever)
JOIN (adres AS baan_werkgever_gevestigd_op) ON (baan_werkgever_gevestigd_op.adres_id = baan_werkgever.gevestigd_op)\
""" ], [
Application(product, [ werknemer, werkgever ]),
"""\
SELECT baan.baan_id, baan.werknemer, baan.werkgever
FROM baan\
""" ], [
Application(product, [ 
    Application(composition, [ ligtin, woontop, werknemer ]),
    Application(composition, [ ligtin, gevestigdop, werkgever ])
]),
"""\
SELECT baan.baan_id, baan_werknemer_woont_op.ligt_in, baan_werkgever_gevestigd_op.ligt_in
FROM baan
JOIN (persoon AS baan_werknemer) ON (baan_werknemer.persoon_id = baan.werknemer)
JOIN (adres AS baan_werknemer_woont_op) ON (baan_werknemer_woont_op.adres_id = baan_werknemer.woont_op)
JOIN (bedrijf AS baan_werkgever) ON (baan_werkgever.bedrijf_id = baan.werkgever)
JOIN (adres AS baan_werkgever_gevestigd_op) ON (baan_werkgever_gevestigd_op.adres_id = baan_werkgever.gevestigd_op)\
""" ], [
leeftijd, # Variabele
"""\
SELECT persoon.persoon_id, persoon.leeftijd
FROM persoon\
""" ], [
allepersonen, # Variabele "alle"
"""\
SELECT persoon.persoon_id, '*'
FROM persoon\
""" ], [
eenpersoon,   # Variable "een"
"""\
SELECT persoon.persoon_id, 1
FROM persoon\
""" ], [
leiden, # Constante
"""\
SELECT '*', 'Leiden'\
""" ], [
Application(composition, [ leiden, allepersonen ]),
"""\
SELECT persoon.persoon_id, 'Leiden'
FROM persoon\
""" ], [
Application(inclusion, [
    Application(composition, [ gemeentenaam, ligtin, woontop ]),
    Application(composition, [ leiden, allepersonen ])
]),
"""\
SELECT persoon.persoon_id, persoon.persoon_id
FROM persoon
JOIN (adres AS persoon_woont_op) ON (persoon_woont_op.adres_id = persoon.woont_op)
JOIN (gemeente AS persoon_woont_op_ligt_in) ON (persoon_woont_op_ligt_in.gemeente_id = persoon_woont_op.ligt_in)
WHERE (persoon_woont_op_ligt_in.gemeentenaam = 'Leiden')\
""" ], [
Application(composition, [
    woontop,
    Application(inclusion, [
        Application(composition, [ gemeentenaam, ligtin, woontop ]),
        Application(composition, [ leiden, allepersonen ])
    ]),
]),
"""\
SELECT persoon.persoon_id, persoon.woont_op
FROM persoon
JOIN (adres AS persoon_woont_op) ON (persoon_woont_op.adres_id = persoon.woont_op)
JOIN (gemeente AS persoon_woont_op_ligt_in) ON (persoon_woont_op_ligt_in.gemeente_id = persoon_woont_op.ligt_in)
WHERE (persoon_woont_op_ligt_in.gemeentenaam = 'Leiden')\
""" ], [
Application(composition, [
    ligtin,
    woontop,
    Application(inclusion, [
        Application(composition, [ gemeentenaam, ligtin, woontop ]),
        Application(composition, [ leiden, allepersonen ])
    ]),
]),
"""\
SELECT persoon.persoon_id, persoon_woont_op.ligt_in
FROM persoon
JOIN (adres AS persoon_woont_op) ON (persoon_woont_op.adres_id = persoon.woont_op)
JOIN (gemeente AS persoon_woont_op_ligt_in) ON (persoon_woont_op_ligt_in.gemeente_id = persoon_woont_op.ligt_in)
WHERE (persoon_woont_op_ligt_in.gemeentenaam = 'Leiden')\
""" ], [
Application(composition, [
    Application(composition, [
        ligtin,
        woontop
    ]),
    Application(inclusion, [
        Application(composition, [ gemeentenaam, ligtin, woontop ]),
        Application(composition, [ leiden, allepersonen ])
    ]),
]),
"""\
SELECT persoon.persoon_id, persoon_woont_op.ligt_in
FROM persoon
JOIN (adres AS persoon_woont_op) ON (persoon_woont_op.adres_id = persoon.woont_op)
JOIN (gemeente AS persoon_woont_op_ligt_in) ON (persoon_woont_op_ligt_in.gemeente_id = persoon_woont_op.ligt_in)
WHERE (persoon_woont_op_ligt_in.gemeentenaam = 'Leiden')\
""" ], [
Application(product, [
    Application(composition, [
        Application(product, [inkomen, leeftijd]),
        werknemer
    ]),
    Application(composition, [
        Application(product, [inkomen, leeftijd]),
        werknemer
    ])
]),
"""\
SELECT baan.baan_id, baan_werknemer.inkomen, baan_werknemer.leeftijd, baan_werknemer.inkomen, baan_werknemer.leeftijd
FROM baan
JOIN (persoon AS baan_werknemer) ON (baan_werknemer.persoon_id = baan.werknemer)\
""" ], [
Application(composition, [
    eenpersoon,
    Application(inclusion, [
        Application(composition, [ gemeentenaam, ligtin, woontop ]),
        Application(composition, [ leiden, allepersonen ])        
    ])
]), 
"""\
SELECT persoon.persoon_id, 1
FROM persoon
JOIN (adres AS persoon_woont_op) ON (persoon_woont_op.adres_id = persoon.woont_op)
JOIN (gemeente AS persoon_woont_op_ligt_in) ON (persoon_woont_op_ligt_in.gemeente_id = persoon_woont_op.ligt_in)
WHERE (persoon_woont_op_ligt_in.gemeentenaam = 'Leiden')\
""" ], [
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
SELECT persoon.persoon_id, persoon.inkomen, persoon.woont_op
FROM persoon
JOIN (adres AS persoon_woont_op) ON (persoon_woont_op.adres_id = persoon.woont_op)
JOIN (gemeente AS persoon_woont_op_ligt_in) ON (persoon_woont_op_ligt_in.gemeente_id = persoon_woont_op.ligt_in)
WHERE (persoon_woont_op_ligt_in.gemeentenaam = 'Leiden')\
""" ], [
Application(composition, [
    Application(product, [ inkomen, woontop ]),
    Application(inclusion, [
        Application(composition, [ gemeentenaam, ligtin, woontop ]),
        Application(composition, [ leiden, allepersonen ])        
    ])
]),
"""\
SELECT persoon.persoon_id, persoon.inkomen, persoon.woont_op
FROM persoon
JOIN (adres AS persoon_woont_op) ON (persoon_woont_op.adres_id = persoon.woont_op)
JOIN (gemeente AS persoon_woont_op_ligt_in) ON (persoon_woont_op_ligt_in.gemeente_id = persoon_woont_op.ligt_in)
WHERE (persoon_woont_op_ligt_in.gemeentenaam = 'Leiden')\
""" ], [
Application(alpha, [inkomen, geslacht]),
"""\
""" ], [
Application(alpha, [eenpersoon, geslacht]),
"""\
""" ], [
Application(alpha, [
    inkomen, 
    Application(product, [ leeftijd, geslacht ])
]),
"""\
""" ], [
Application(alpha, [
    Application(composition, [
        inkomen,
        Application(inclusion, [
            Application(composition, [ gemeentenaam, ligtin, woontop ]),
            Application(composition, [ leiden, allepersonen ])        
        ])
    ]),
    Application(composition, [
        geslacht,
        Application(inclusion, [
            Application(composition, [ gemeentenaam, ligtin, woontop ]),
            Application(composition, [ leiden, allepersonen ])        
        ])
    ])
]),
"""\
""" ], [
Application(alpha, [inkomen, allepersonen]),
"""\
""" ], [
Application(product, [
    Application(alpha, [ inkomen, geslacht ]),
    Application(alpha, [ eenpersoon, geslacht ])
]),
"""\
""" ], [
Application(alpha, [ inkomen, 
    Application(composition, [ ligtin, woontop ]) 
]),
"""\
""" ], [
Application(alpha, [ eenadres, ligtin ]),
"""\
""" ], [
Application(product, [
    Application(alpha, [ inkomen, 
        Application(composition, [ ligtin, woontop ]) 
    ]),
    Application(alpha, [ eenadres, ligtin ]),
]),    
"""\
""" ]#, [
#Application(gedeelddoor, 
#    Application(product, [ inkomen, leeftijd ])
#),
#"""\
#""" ]
]

test_terms(terms)