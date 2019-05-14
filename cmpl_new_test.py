from term import *
from kind import Variable, ObjectTypeRelation, Constant, Operator
from dm import *
from cmpl_new import cmpl

def test_terms(terms, expected_output):
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

if __name__ == '__main__':
    terms = [ 
        woontop, # otr
        ligtin,
        Application(composition, [ ligtin, woontop ]),
        Application(composition, [ ligtin, gevestigdop, werkgever ]),
        Application(composition, [
            ligtin,
            Application(composition, [ gevestigdop, werkgever ])
        ]),
        Application(composition, [
            Application(composition, [ ligtin, gevestigdop ]),
            werkgever
        ]),
        Application(product, [ werknemer, werkgever ]),
        Application(product, [ 
            Application(composition, [ ligtin, woontop, werknemer ]),
            Application(composition, [ ligtin, gevestigdop, werkgever ])
        ]),
        leeftijd, # Variabele
        allepersonen, # Variabele "alle"
        eenpersoon,   # Variable "een"
        leiden, # Constante
        Application(composition, [ leiden, allepersonen ]),
        Application(composition, [ gemeentenaam, ligtin, woontop ]),
        Application(composition, [ 
            Application(composition, [ gemeentenaam, ligtin ]),
            woontop
        ]),
        Application(composition, [
            gemeentenaam,
            Application(composition, [ ligtin, woontop ])
        ]),
        Application(inclusion, [
            Application(composition, [ gemeentenaam, ligtin, woontop ]),
            Application(composition, [ leiden, allepersonen ])
        ]),
        woontop,   # Variable "een"
        Application(composition, [
            woontop,
            Application(inclusion, [
                Application(composition, [ gemeentenaam, ligtin, woontop ]),
                Application(composition, [ leiden, allepersonen ])
            ]),
        ]),
        Application(composition, [
            ligtin,
            woontop,
            Application(inclusion, [
                Application(composition, [ gemeentenaam, ligtin, woontop ]),
                Application(composition, [ leiden, allepersonen ])
            ]),
        ]),
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
        Application(product, [
            Application(composition, [
                Application(product, [inkomen, leeftijd]),
                werknemer
            ]),
            Application(composition, [
                Application(product, [inkomen, leeftijd]),
                werknemer
            ])
        ])
    ]
    expected_output = ["""\
SELECT persoon.persoon_id, persoon.woont_op
FROM persoon\
""", """\
SELECT adres.adres_id, adres.ligt_in
FROM adres\
""", """\
SELECT persoon.persoon_id, persoon_woont_op.ligt_in
FROM persoon
JOIN (adres AS persoon_woont_op) ON (persoon_woont_op.adres_id = persoon.woont_op)\
""", """\
SELECT baan.baan_id, baan_werkgever_gevestigd_op.ligt_in
FROM baan
JOIN (bedrijf AS baan_werkgever) ON (baan_werkgever.bedrijf_id = baan.werkgever)
JOIN (adres AS baan_werkgever_gevestigd_op) ON (baan_werkgever_gevestigd_op.adres_id = baan_werkgever.gevestigd_op)\
""", """\
SELECT baan.baan_id, baan_werkgever_gevestigd_op.ligt_in
FROM baan
JOIN (bedrijf AS baan_werkgever) ON (baan_werkgever.bedrijf_id = baan.werkgever)
JOIN (adres AS baan_werkgever_gevestigd_op) ON (baan_werkgever_gevestigd_op.adres_id = baan_werkgever.gevestigd_op)\
""", """\
SELECT baan.baan_id, baan_werkgever_gevestigd_op.ligt_in
FROM baan
JOIN (bedrijf AS baan_werkgever) ON (baan_werkgever.bedrijf_id = baan.werkgever)
JOIN (adres AS baan_werkgever_gevestigd_op) ON (baan_werkgever_gevestigd_op.adres_id = baan_werkgever.gevestigd_op)\
""", """\
SELECT baan.baan_id, baan.werknemer, baan.werkgever
FROM baan\
""", """\
SELECT baan.baan_id, baan_werknemer_woont_op.ligt_in, baan_werkgever_gevestigd_op.ligt_in
FROM baan
JOIN (persoon AS baan_werknemer) ON (baan_werknemer.persoon_id = baan.werknemer)
JOIN (adres AS baan_werknemer_woont_op) ON (baan_werknemer_woont_op.adres_id = baan_werknemer.woont_op)
JOIN (bedrijf AS baan_werkgever) ON (baan_werkgever.bedrijf_id = baan.werkgever)
JOIN (adres AS baan_werkgever_gevestigd_op) ON (baan_werkgever_gevestigd_op.adres_id = baan_werkgever.gevestigd_op)\
""", """\
SELECT persoon.persoon_id, persoon.leeftijd
FROM persoon\
""", """\
SELECT persoon.persoon_id, '*'
FROM persoon\
""", """\
SELECT persoon.persoon_id, 1
FROM persoon\
""", """\
SELECT '*', 'Leiden'\
""", """\
SELECT persoon.persoon_id, 'Leiden'
FROM persoon\
""", """\
SELECT persoon.persoon_id, persoon_woont_op_ligt_in.gemeentenaam
FROM persoon
JOIN (adres AS persoon_woont_op) ON (persoon_woont_op.adres_id = persoon.woont_op)
JOIN (gemeente AS persoon_woont_op_ligt_in) ON (persoon_woont_op_ligt_in.gemeente_id = persoon_woont_op.ligt_in)\
""", """\
SELECT persoon.persoon_id, persoon_woont_op_ligt_in.gemeentenaam
FROM persoon
JOIN (adres AS persoon_woont_op) ON (persoon_woont_op.adres_id = persoon.woont_op)
JOIN (gemeente AS persoon_woont_op_ligt_in) ON (persoon_woont_op_ligt_in.gemeente_id = persoon_woont_op.ligt_in)\
""", """\
SELECT persoon.persoon_id, persoon_woont_op_ligt_in.gemeentenaam
FROM persoon
JOIN (adres AS persoon_woont_op) ON (persoon_woont_op.adres_id = persoon.woont_op)
JOIN (gemeente AS persoon_woont_op_ligt_in) ON (persoon_woont_op_ligt_in.gemeente_id = persoon_woont_op.ligt_in)\
""", """\
SELECT persoon.persoon_id, persoon.persoon_id
FROM persoon
JOIN (adres AS persoon_woont_op) ON (persoon_woont_op.adres_id = persoon.woont_op)
JOIN (gemeente AS persoon_woont_op_ligt_in) ON (persoon_woont_op_ligt_in.gemeente_id = persoon_woont_op.ligt_in)
WHERE (persoon_woont_op_ligt_in.gemeentenaam = 'Leiden')\
""", """\
SELECT persoon.persoon_id, persoon.woont_op
FROM persoon\
""", """\
SELECT persoon.persoon_id, persoon.woont_op
FROM persoon
JOIN (adres AS persoon_woont_op) ON (persoon_woont_op.adres_id = persoon.woont_op)
JOIN (gemeente AS persoon_woont_op_ligt_in) ON (persoon_woont_op_ligt_in.gemeente_id = persoon_woont_op.ligt_in)
WHERE (persoon_woont_op_ligt_in.gemeentenaam = 'Leiden')\
""", """\
SELECT persoon.persoon_id, persoon_woont_op.ligt_in
FROM persoon
JOIN (adres AS persoon_woont_op) ON (persoon_woont_op.adres_id = persoon.woont_op)
JOIN (gemeente AS persoon_woont_op_ligt_in) ON (persoon_woont_op_ligt_in.gemeente_id = persoon_woont_op.ligt_in)
WHERE (persoon_woont_op_ligt_in.gemeentenaam = 'Leiden')\
""", """\
SELECT persoon.persoon_id, persoon_woont_op.ligt_in
FROM persoon
JOIN (adres AS persoon_woont_op) ON (persoon_woont_op.adres_id = persoon.woont_op)
JOIN (gemeente AS persoon_woont_op_ligt_in) ON (persoon_woont_op_ligt_in.gemeente_id = persoon_woont_op.ligt_in)
WHERE (persoon_woont_op_ligt_in.gemeentenaam = 'Leiden')\
"""
    ]
    test_terms(terms, expected_output)