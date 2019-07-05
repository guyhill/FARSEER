from term import *
from kind import Variable, ObjectTypeRelation, Constant, Operator
from dm import *
from cmpl_new import cmpl

def show_tests(terms):
    for i, term in enumerate(terms):
        print(i, repr(term[0]))


def test_terms(terms, showall = False, ordered = False):
    error = False
    for i, term in enumerate(terms):
        if ordered:
            output = repr(cmpl(term[0], leeftijd, "asc"))
        else:
            output = repr(cmpl(term[0]))
        expected = term[1]
        if showall or output != expected:
            failstr = " failed" if output != expected else "======="
            msg = (f"======test {i}{failstr}===========\n" +
                  repr(term[0]) + "\n\n" +
                  "Output:\n" +
                  output + "\n\n" +
                  "Expected output:\n" +
                  expected )
            print(msg)
            error = True
    if not error:
        print("all tests passed")

              
if __name__ == "__main__":
    terms = [ 
    # Terms contains a number of test cases for testing compilation to SQL code. Test cases have
    # been grouped into a groups of related tests
    # The first group tests all cases consisting of a single element. Five different types of 
    # elements exist: object type relations, variables, constants and the immediates "one" and "all"
    # We include one test case from each of these types.
    [       # object type relation
    woontop, 
    """\
SELECT persoon.persoon_id, persoon.woont_op
FROM persoon
""" ], [    # Variable
    leeftijd,
    """\
SELECT persoon.persoon_id, persoon.leeftijd
FROM persoon
""" ], [    # Immediate variable "all"
    allepersonen, 
    """\
SELECT persoon.persoon_id, '*'
FROM persoon
""" ], [    # Immediate variable "one"
    eenpersoon,
    """\
SELECT persoon.persoon_id, 1
FROM persoon
""" ], [    # Constant
    leiden, 
    """\
SELECT '*', 'Leiden'
""" ],
    # The second group of test cases deals with element composition. We first test composition of two elements
    # and composition of three elements. We assume that this is sufficient for testing composition of n elements.
    # Both these tests have only object type relations as their elements. In addition to this, we also test
    # composition of other element types. The following is an exhaustive list of all possibilities:
    # 1. otr ∘ otr (already tested)
    # 2. var ∘ otr
    # 3. one ∘ otr
    # 4. all ∘ otr
    # 5. const ∘ all
    # We include one test case for each of the cases 2-5
    [       # otr ∘ otr
    Application(composition, [ ligtin, woontop ]),
    """\
SELECT persoon.persoon_id, persoon_woont_op.ligt_in
FROM persoon
JOIN (adres AS persoon_woont_op) ON (persoon_woont_op.adres_id = persoon.woont_op)
"""], [     # otr ∘ otr ∘ otr
    Application(composition, [ ligtin, gevestigdop, werkgever ]),
    """\
SELECT baan.baan_id, baan_werkgever_gevestigd_op.ligt_in
FROM baan
JOIN (bedrijf AS baan_werkgever) ON (baan_werkgever.bedrijf_id = baan.werkgever)
JOIN (adres AS baan_werkgever_gevestigd_op) ON (baan_werkgever_gevestigd_op.adres_id = baan_werkgever.gevestigd_op)
""" ], [    # var ∘ otr
    Application(composition, [ leeftijd, werknemer ]),
    """\
SELECT baan.baan_id, baan_werknemer.leeftijd
FROM baan
JOIN (persoon AS baan_werknemer) ON (baan_werknemer.persoon_id = baan.werknemer)
"""], [     # one ∘ otr
    Application(composition, [ eenpersoon, werknemer ]),
    """\
SELECT baan.baan_id, 1
FROM baan
JOIN (persoon AS baan_werknemer) ON (baan_werknemer.persoon_id = baan.werknemer)
"""], [     # all ∘ otr
    Application(composition, [allepersonen, werknemer ]),
    """\
SELECT baan.baan_id, '*'
FROM baan
JOIN (persoon AS baan_werknemer) ON (baan_werknemer.persoon_id = baan.werknemer)
"""], [     # const ∘ all
    Application(composition, [ leiden, allepersonen ]),
    """\
SELECT persoon.persoon_id, 'Leiden'
FROM persoon
"""],
    # The next group of test cases deals with products. We first test products of two
    # and three elements, where all elements are otr's. After that we also test every
    # other combination of two elements. And since order matters we test both orders
    # for every such combination
    [       # Product of two otr
    Application(product, [ werknemer, werkgever ]),
    """\
SELECT baan.baan_id, baan.werknemer, baan.werkgever
FROM baan
""" ], [    # Product of three otr - note: we don't have three different otr with the same domain
            # in our test cases, therefore we use a synthetic test with multiple copies of otr
    Application(product, [ werknemer, werkgever, werknemer ]),
    """\
SELECT baan.baan_id, baan.werknemer, baan.werkgever, baan.werknemer
FROM baan
"""], [     # Product of otr with var
    Application(product, [ woontop, leeftijd ]),
    """\
SELECT persoon.persoon_id, persoon.woont_op, persoon.leeftijd
FROM persoon
"""], [     # Product of otr with one
    Application(product, [ woontop, eenpersoon ]),
    """\
SELECT persoon.persoon_id, persoon.woont_op, 1
FROM persoon
"""], [     # Product of otr with all
    Application(product, [ woontop, allepersonen ]),
    """\
SELECT persoon.persoon_id, persoon.woont_op, '*'
FROM persoon
"""], [     # Product of var with otr
    Application(product, [ leeftijd, woontop ]),
    """\
SELECT persoon.persoon_id, persoon.leeftijd, persoon.woont_op
FROM persoon
"""], [     # Product of var with var
    Application(product, [ inkomen, leeftijd ]),
    """\
SELECT persoon.persoon_id, persoon.inkomen, persoon.leeftijd
FROM persoon
"""], [     # Product of var with one
    Application(product, [ leeftijd, eenpersoon ]),
    """\
SELECT persoon.persoon_id, persoon.leeftijd, 1
FROM persoon
"""], [     # Product of var with all
    Application(product, [ leeftijd, allepersonen ]),
    """\
SELECT persoon.persoon_id, persoon.leeftijd, '*'
FROM persoon
"""], [     # Product of een with otr
    Application(product, [ eenpersoon, woontop ]),
    """\
SELECT persoon.persoon_id, 1, persoon.woont_op
FROM persoon
"""], [     # Product of een with var
    Application(product, [ eenpersoon, leeftijd ]),
    """\
SELECT persoon.persoon_id, 1, persoon.leeftijd
FROM persoon
"""], [     # Product of een with een
    Application(product, [ eenpersoon, eenpersoon ]),
    """\
SELECT persoon.persoon_id, 1, 1
FROM persoon
"""], [     # Product of een with all
    Application(product, [ eenpersoon, allepersonen ]),
    """\
SELECT persoon.persoon_id, 1, '*'
FROM persoon
"""], [     # Product of all with otr
    Application(product, [ allepersonen, woontop ]),
    """\
SELECT persoon.persoon_id, '*', persoon.woont_op
FROM persoon
"""], [     # Product of all with var
    Application(product, [ allepersonen, leeftijd ]),
    """\
SELECT persoon.persoon_id, '*', persoon.leeftijd
FROM persoon
"""], [     # Product of all with one
    Application(product, [ allepersonen, eenpersoon ]),
    """\
SELECT persoon.persoon_id, '*', 1
FROM persoon
"""], [     # Product of all with all
    Application(product, [ allepersonen, allepersonen ]),
    """\
SELECT persoon.persoon_id, '*', '*'
FROM persoon
"""],
    # The next group of tests deal with inclusions. We first test inclusion with one and two comparisons
    # (i.e., 2 and 4 inputs), and we assume that this is enough to also test inclusion with more comparisons.
    # We also include one test case with two operands (one comparison), for operands of each element type.
    # It turns out to be rather hard to devise realistic test cases for inclusion that do not contain any 
    # other operators, so we choose syntactically correct examples that are entirely synthetic.
    [       # Inclusion with 2 variable operands (not a realistic example)
    Application(inclusion, [ leeftijd, inkomen ]),
    """\
SELECT persoon.persoon_id, persoon.persoon_id
FROM persoon
WHERE (persoon.leeftijd = persoon.inkomen)
""" ], [    # Inclusion with 4 operands (not a realistic example either)
    Application(inclusion, [ leeftijd, inkomen, lengte, gewicht ]),
    """\
SELECT persoon.persoon_id, persoon.persoon_id
FROM persoon
WHERE (persoon.leeftijd = persoon.inkomen) AND (persoon.lengte = persoon.gewicht)
"""], [     # Inclusion with 2 otr operands
            # Inclusion does not remove trivial comparisons, so we can test with identical operands
    Application(inclusion, [ leeftijd, leeftijd ]),
    """\
SELECT persoon.persoon_id, persoon.persoon_id
FROM persoon
WHERE (persoon.leeftijd = persoon.leeftijd)
"""], [     # Inclusion with two constants as operands
    Application(inclusion, [leiden, denhaag]),
    """\
SELECT '*', '*'
WHERE ('Leiden' = 'Den_Haag')
"""], [     # Inclusion with "one"
    Application(inclusion, [eenpersoon, eenpersoon]),
    """\
SELECT persoon.persoon_id, persoon.persoon_id
FROM persoon
WHERE (1 = 1)
"""], [     # Inclusion with "all"
    Application(inclusion, [allepersonen, allepersonen]),
    """\
SELECT persoon.persoon_id, persoon.persoon_id
FROM persoon
WHERE ('*' = '*')
"""], [     # Inclusion with variable and one
    Application(inclusion, [leeftijd, eenpersoon]),
    """\
SELECT persoon.persoon_id, persoon.persoon_id
FROM persoon
WHERE (persoon.leeftijd = 1)
"""],
    # This group of tests deals with the inverse operation. Since inverse has only one
    # element as argument, we include one test for each element type
    [       # Inverse with otr
    Application(inverse, [ werknemer ]),
    """\
SELECT DISTINCT baan.werknemer, baan.werknemer
FROM baan
"""], [     # Inverse with variable
    Application(inverse, [ leeftijd ]),
    """\
SELECT DISTINCT persoon.leeftijd, persoon.leeftijd
FROM persoon
"""], [     # Inverse with constant
    Application(inverse, [ leiden ]),
    """\
SELECT DISTINCT 'Leiden', 'Leiden'
"""], [     # Inverse with one
    Application(inverse, [ eenpersoon ]),
    """\
SELECT DISTINCT 1, 1
FROM persoon
"""], [     # Inverse with all
    Application(inverse, [ allepersonen ]),
    """\
SELECT DISTINCT '*', '*'
FROM persoon
"""],
    # This group of tests deals with aggregation. The aggregation operation has 2 arguments:
    # The first must be have number as its codomain, so it is limited to numerical variables and one;
    # the second can be either an otr, a classifying variable, or "all". We therefore distinguish the
    # following cases:
    # 1. Numerical variable, otr
    # 2. Numerical variable, non-numerical variable
    # 3. Numerical variable, all
    # 4. One, otr
    # 5. One, non-numerical variable
    # 6. One, all
    [       # Numerical variable, otr
    Application(alpha, [ inkomen, woontop ]),
    """\
SELECT persoon.woont_op, SUM(persoon.inkomen)
FROM persoon
GROUP BY persoon.woont_op
"""], [     # Numerical variable, other variable
    Application(alpha, [ inkomen, geslacht ]),
    """\
SELECT persoon.geslacht, SUM(persoon.inkomen)
FROM persoon
GROUP BY persoon.geslacht
"""], [     # Numerical variable, all
    Application(alpha, [ inkomen, allepersonen ]),
    """\
SELECT '*', SUM(persoon.inkomen)
FROM persoon
"""], [     # One, otr
    Application(alpha, [ eenpersoon, woontop ]),
    """\
SELECT persoon.woont_op, SUM(1)
FROM persoon
GROUP BY persoon.woont_op
"""], [     # One, non-numerical variable
    Application(alpha, [ eenpersoon, geslacht ]),
    """\
SELECT persoon.geslacht, SUM(1)
FROM persoon
GROUP BY persoon.geslacht
"""], [     # One, all
    Application(alpha, [ eenpersoon, allepersonen ]),
    """\
SELECT '*', SUM(1)
FROM persoon
"""],
    # From here on, tests deal with combinations of operators. We include test cases for
    # every possible combination of two operators with 2 arguments each. We then assume that combinations of 
    # more than two operators will work as well, due to the recursive nature of the compiler.
    # We distinguish the following cases, and include on test for each of them:
    # A. Composition
    # 1. Product inside left hand side of composition
    # 2. Product inside right hand side of composition. Only two possible cases: 
    #    a. the division operator
    #    b. the projection operator
    # 3. Aggregation inside left hand side of composition. Aggregation inside rhs is not possible,
    #    because the co-domain of aggregation is a number, and nothing has number as domain
    # 4. Inclusion inside lhs of composition <-- this one cannot occur as the domain of inclusion 
    #                                            is a subset of an object type, not the object type itself
    # 5. Inclusion inside rhs of composition
    # 6. Inverse in lhs of composition <-- This one cannot occur, for the same reason as inclusion
    # 7. Inverse in rhs of composition
    # 8. Composition in lhs of composition
    # 9. Composition in rhs of composition
    [       # Product inside left hand side of composition
    Application(composition, [
        Application(product, [woontop, leeftijd]),
        werknemer
    ]), 
    """\
SELECT baan.baan_id, baan_werknemer.woont_op, baan_werknemer.leeftijd
FROM baan
JOIN (persoon AS baan_werknemer) ON (baan_werknemer.persoon_id = baan.werknemer)
"""], [     # Product inside right hand side of composition, with division
    Application(composition, [
        gedeelddoor, 
        Application(product, [ inkomen, leeftijd ])
    ]),
    """\
SELECT persoon.persoon_id, (persoon.inkomen / persoon.leeftijd)
FROM persoon
""" ], [     # Product inside right hand side of composition, with projection
    Application(composition, [
        Application(projection, [getal, getal, 2]), 
        Application(product, [ inkomen, leeftijd ])
    ]),
    """\
SELECT persoon.persoon_id, persoon.leeftijd
FROM persoon
""" ], [    # Aggregation inside left hand side of composition
    Application(composition, [
        Application(alpha, [leeftijd, woontop]),
        gevestigdop
    ]),
    """\
CREATE TEMPORARY TABLE tmp0
SELECT persoon.woont_op AS col0, SUM(persoon.leeftijd) AS col1
FROM persoon
GROUP BY persoon.woont_op
SELECT bedrijf.bedrijf_id, tmp0.col1
FROM bedrijf
JOIN (tmp0) ON (tmp0.col0 = bedrijf.gevestigd_op)
"""], [    # Inclusion inside rhs of composition
    Application(composition, [
        woontop,
        Application(inclusion, [leeftijd, gewicht])
    ]),
    """\
SELECT persoon.persoon_id, persoon.woont_op
FROM persoon
WHERE (persoon.leeftijd = persoon.gewicht)
"""], [    # Inverse in rhs of composition
    Application(composition, [
        leeftijd,
        Application(inverse, [werknemer])
    ]),
    """\
CREATE TEMPORARY TABLE tmp0
SELECT DISTINCT baan.werknemer AS col0, baan.werknemer AS col1
FROM baan
SELECT tmp0.col0, tmp0_col1.leeftijd
FROM tmp0
JOIN (persoon AS tmp0_col1) ON (tmp0_col1.persoon_id = tmp0.col1)
"""], [    # Composition in lhs of composition
    Application(composition, [
        Application(composition, [ligtin, woontop]),
        werknemer
    ]),
    """\
SELECT baan.baan_id, baan_werknemer_woont_op.ligt_in
FROM baan
JOIN (persoon AS baan_werknemer) ON (baan_werknemer.persoon_id = baan.werknemer)
JOIN (adres AS baan_werknemer_woont_op) ON (baan_werknemer_woont_op.adres_id = baan_werknemer.woont_op)
"""], [    # Composition in rhs of composition
    Application(composition, [
        ligtin,
        Application(composition, [woontop, werknemer])
    ]),
    """\
SELECT baan.baan_id, baan_werknemer_woont_op.ligt_in
FROM baan
JOIN (persoon AS baan_werknemer) ON (baan_werknemer.persoon_id = baan.werknemer)
JOIN (adres AS baan_werknemer_woont_op) ON (baan_werknemer_woont_op.adres_id = baan_werknemer.woont_op)
"""],
    # B. Product
    # 1. Composition in lhs of product
    # 2. Composition in rhs of product
    # 3. Product in lhs of product
    # 4. Product in rhs of product
    # 5. Inclusion in lhs and rhs of product
    #    Note: it is not possible to have inclusion in lhs without also having inclusion in rhs
    #    Reason for this is that domain of lhs & rhs must be the same, and inclusion has its own domain,
    #    different from the domain of the otr's inside the inclusion. No otr / variable / constant
    #    has the same domain as an inclusion.
    # 6. Inverse in lhs and rhs of product.
    #    Note: like inclusion, it is not possible to have inverse in lhs without having the same inverse in rhs.
    # 7. Aggregation in lhs of product
    # 8. Aggregation in rhs of product
    [       # Composition in lhs of product
    Application(product, [
        Application(composition, [ligtin, woontop]),
        leeftijd
    ]),
    """\
SELECT persoon.persoon_id, persoon_woont_op.ligt_in, persoon.leeftijd
FROM persoon
JOIN (adres AS persoon_woont_op) ON (persoon_woont_op.adres_id = persoon.woont_op)
"""], [     # Composition in rhs of product
    Application(product, [
        leeftijd,
        Application(composition, [ligtin, woontop])
    ]),
    """\
SELECT persoon.persoon_id, persoon.leeftijd, persoon_woont_op.ligt_in
FROM persoon
JOIN (adres AS persoon_woont_op) ON (persoon_woont_op.adres_id = persoon.woont_op)
"""], [     # Product in lhs of product
    Application(product, [
        Application(product, [leeftijd, inkomen]),
        lengte
    ]),
    """\
SELECT persoon.persoon_id, persoon.leeftijd, persoon.inkomen, persoon.lengte
FROM persoon
"""], [     # Product in rhs of product
    Application(product, [
        lengte,
        Application(product, [leeftijd, inkomen])
    ]),
    """\
SELECT persoon.persoon_id, persoon.lengte, persoon.leeftijd, persoon.inkomen
FROM persoon
"""], [     # Inclusion in lhs and rhs of product
    Application(product, [
        Application(inclusion, [leeftijd, gewicht]),
        Application(inclusion, [leeftijd, gewicht])
    ]),
    """\
SELECT persoon.persoon_id, persoon.persoon_id, persoon.persoon_id
FROM persoon
WHERE (persoon.leeftijd = persoon.gewicht)
"""], [     # Inverse in lhs & rhs of product
    Application(product, [
        Application(inverse, [werknemer]),
        Application(inverse, [werknemer])
    ]),
    """\
CREATE TEMPORARY TABLE tmp0
SELECT DISTINCT baan.werknemer AS col0, baan.werknemer AS col1
FROM baan
SELECT tmp0.col0, tmp0.col1, tmp0.col1
FROM tmp0
"""], [     # Aggregation in lhs of product
    Application(product, [
        Application(alpha, [salaris, werknemer]),
        inkomen
    ]),
    """\
CREATE TEMPORARY TABLE tmp0
SELECT baan.werknemer AS col0, SUM(baan.salaris) AS col1
FROM baan
GROUP BY baan.werknemer
SELECT tmp0.col0, tmp0.col1, persoon.inkomen
FROM tmp0
JOIN (persoon) ON (tmp0.col0 = persoon.persoon_id)
"""], [     # Aggregation in rhs of product
    Application(product, [
        inkomen,
        Application(alpha, [salaris, werknemer])
    ]),
    """\
CREATE TEMPORARY TABLE tmp0
SELECT baan.werknemer AS col0, SUM(baan.salaris) AS col1
FROM baan
GROUP BY baan.werknemer
SELECT persoon.persoon_id, persoon.inkomen, tmp0.col1
FROM persoon
JOIN (tmp0) ON (persoon.persoon_id = tmp0.col0)
"""],
    # C. Inclusion
    # 1. Composition in lhs of inclusion
    # 2. Composition in rhs of inclusion
    # 3. Product in lhs & rhs of inclusion
    #    Note: no primitives exist with multi-dimensional co-domain, so 
    #    it is impossible to have an inclusion with a product in lhs and a primitive in rhs
    #    Note: I chose not to implement inclusions with multi-dimensional co-domain
    # 4. Inclusion inside inclusion? Does this even make sense?
    # 5. Inverse in lhs and rhs of inclusion
    #    Note: like with products, it is impossible to have inverse on one side and a primitive on the other side.
    # 6. Aggregation inside inclusion?
    [       # Composition in lhs of inclusion
    Application(inclusion, [
        Application(composition, [ inkomen, werknemer ]),
        salaris
    ]),
    """\
SELECT baan.baan_id, baan.baan_id
FROM baan
JOIN (persoon AS baan_werknemer) ON (baan_werknemer.persoon_id = baan.werknemer)
WHERE (baan_werknemer.inkomen = baan.salaris)
"""], [     # Composition in rhs of inclusion
    Application(inclusion, [
        salaris,
        Application(composition, [ inkomen, werknemer ]),
    ]),
    """\
SELECT baan.baan_id, baan.baan_id
FROM baan
JOIN (persoon AS baan_werknemer) ON (baan_werknemer.persoon_id = baan.werknemer)
WHERE (baan.salaris = baan_werknemer.inkomen)
"""], [    # Inverse in lhs & rhs of inclusion
    Application(inclusion, [
        Application(inverse, [werknemer]),
        Application(inverse, [werknemer])
    ]),
    """\
CREATE TEMPORARY TABLE tmp0
SELECT DISTINCT baan.werknemer AS col0, baan.werknemer AS col1
FROM baan
SELECT tmp0.col0, tmp0.col0
FROM tmp0
WHERE (tmp0.col1 = tmp0.col1)
"""], [     # Aggregation in lhs of inclusion
    Application(inclusion, [
        Application(alpha, [ salaris, werknemer ]),
        inkomen
    ]),
    """\
CREATE TEMPORARY TABLE tmp0
SELECT baan.werknemer AS col0, SUM(baan.salaris) AS col1
FROM baan
GROUP BY baan.werknemer
SELECT tmp0.col0, tmp0.col0
FROM tmp0
JOIN (persoon) ON (tmp0.col0 = persoon.persoon_id)
WHERE (tmp0.col1 = persoon.inkomen)
"""], [     # Aggregation in rhs of inclusion
    Application(inclusion, [
        inkomen,
        Application(alpha, [ salaris, werknemer ])
    ]),
    """\
CREATE TEMPORARY TABLE tmp0
SELECT baan.werknemer AS col0, SUM(baan.salaris) AS col1
FROM baan
GROUP BY baan.werknemer
SELECT persoon.persoon_id, persoon.persoon_id
FROM persoon
JOIN (tmp0) ON (persoon.persoon_id = tmp0.col0)
WHERE (persoon.inkomen = tmp0.col1)
"""],
    # D. Inverse
    # 1. Composition inside inverse
    # 2. Product inside inverse
    # 3. Inclusion inside inverse
    # 4. Inverse inside inverse
    # 5. Aggregation inside inverse
    #
    # Note: only 1 is used in practice, the others are entirely hypothetical
    [       # Composition in inverse
    Application(inverse, [
        Application(composition, [ligtin, woontop])
    ]),
    """\
SELECT DISTINCT persoon_woont_op.ligt_in, persoon_woont_op.ligt_in
FROM persoon
JOIN (adres AS persoon_woont_op) ON (persoon_woont_op.adres_id = persoon.woont_op)
"""], [     # Product in inverse
    Application(inverse, [
        Application(product, [werknemer, salaris])
    ]),
    """\
SELECT DISTINCT baan.werknemer, baan.salaris, baan.werknemer, baan.salaris
FROM baan
"""], [     # Inclusion in inverse
    Application(inverse, [
        Application(inclusion, [salaris, eenbaan])
    ]),
    """\
SELECT DISTINCT baan.baan_id, baan.baan_id
FROM baan
WHERE (baan.salaris = 1)
"""], [     # Inverse in inverse
    Application(inverse, [
        Application(inverse, [ werknemer ])
    ]),
    """\
CREATE TEMPORARY TABLE tmp0
SELECT DISTINCT baan.werknemer AS col0, baan.werknemer AS col1
FROM baan
SELECT DISTINCT tmp0.col1, tmp0.col1
FROM tmp0
"""], [     # Aggregation in inverse
    Application(inverse, [
        Application(alpha, [salaris, werknemer])
    ]),
    """\
CREATE TEMPORARY TABLE tmp0
SELECT baan.werknemer AS col0, SUM(baan.salaris) AS col1
FROM baan
GROUP BY baan.werknemer
SELECT DISTINCT tmp0.col1, tmp0.col1
FROM tmp0
"""],
    # E. Aggregation
]






    oldterms = [
    [    # Inversie
    Application(inverse, [
        werknemer
    ]),
    """\
SELECT DISTINCT baan.werknemer, baan.werknemer
FROM baan
""" ], [    # Aggregatie
    Application(alpha, [inkomen, geslacht]),
    """\
SELECT persoon.geslacht, SUM(persoon.inkomen)
FROM persoon
GROUP BY persoon.geslacht
""" ], [    # Simpelste geval van een numerieke operator
    Application(composition, [
        gedeelddoor, 
        Application(product, [ inkomen, leeftijd ])
    ]),
    """\
SELECT persoon.persoon_id, (persoon.inkomen / persoon.leeftijd)
FROM persoon
""" ], [    # Simpelste geval van een projectie-operator
    Application(composition, [
        Application(projection, [ getal, adres, 2]),
        Application(product, [ inkomen, woontop ])
    ]),
    """\
SELECT persoon.persoon_id, persoon.woont_op
FROM persoon
""" ], [
    Application(composition, [
        ligtin,
        Application(composition, [ gevestigdop, werkgever ])
    ]),
    """\
SELECT baan.baan_id, baan_werkgever_gevestigd_op.ligt_in
FROM baan
JOIN (bedrijf AS baan_werkgever) ON (baan_werkgever.bedrijf_id = baan.werkgever)
JOIN (adres AS baan_werkgever_gevestigd_op) ON (baan_werkgever_gevestigd_op.adres_id = baan_werkgever.gevestigd_op)
""" ], [
    Application(composition, [
        Application(composition, [ ligtin, gevestigdop ]),
        werkgever
    ]),
    """\
SELECT baan.baan_id, baan_werkgever_gevestigd_op.ligt_in
FROM baan
JOIN (bedrijf AS baan_werkgever) ON (baan_werkgever.bedrijf_id = baan.werkgever)
JOIN (adres AS baan_werkgever_gevestigd_op) ON (baan_werkgever_gevestigd_op.adres_id = baan_werkgever.gevestigd_op)
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
JOIN (adres AS baan_werkgever_gevestigd_op) ON (baan_werkgever_gevestigd_op.adres_id = baan_werkgever.gevestigd_op)
""" ], [
    Application(composition, [ leiden, allepersonen ]),
    """\
SELECT persoon.persoon_id, 'Leiden'
FROM persoon
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
WHERE (persoon_woont_op_ligt_in.gemeentenaam = 'Leiden')
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
WHERE (persoon_woont_op_ligt_in.gemeentenaam = 'Leiden')
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
WHERE (persoon_woont_op_ligt_in.gemeentenaam = 'Leiden')
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
WHERE (persoon_woont_op_ligt_in.gemeentenaam = 'Leiden')
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
JOIN (persoon AS baan_werknemer) ON (baan_werknemer.persoon_id = baan.werknemer)
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
WHERE (persoon_woont_op_ligt_in.gemeentenaam = 'Leiden')
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
WHERE (persoon_woont_op_ligt_in.gemeentenaam = 'Leiden')
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
WHERE (persoon_woont_op_ligt_in.gemeentenaam = 'Leiden')
""" ], [
    Application(alpha, [inkomen, geslacht]),
    """\
SELECT persoon.geslacht, SUM(persoon.inkomen)
FROM persoon
GROUP BY persoon.geslacht
""" ], [
    Application(alpha, [eenpersoon, geslacht]),
    """\
SELECT persoon.geslacht, SUM(1)
FROM persoon
GROUP BY persoon.geslacht
""" ], [
    Application(alpha, [inkomen, allepersonen]),
    """\
SELECT '*', SUM(persoon.inkomen)
FROM persoon
""" ], [
    Application(alpha, [eenpersoon, allepersonen]),
    """\
SELECT '*', SUM(1)
FROM persoon
"""], [
    Application(alpha, [
        inkomen, 
        Application(product, [ leeftijd, geslacht ])
    ]),
    """\
SELECT persoon.leeftijd, persoon.geslacht, SUM(persoon.inkomen)
FROM persoon
GROUP BY persoon.leeftijd, persoon.geslacht
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
SELECT persoon.geslacht, SUM(persoon.inkomen)
FROM persoon
JOIN (adres AS persoon_woont_op) ON (persoon_woont_op.adres_id = persoon.woont_op)
JOIN (gemeente AS persoon_woont_op_ligt_in) ON (persoon_woont_op_ligt_in.gemeente_id = persoon_woont_op.ligt_in)
WHERE (persoon_woont_op_ligt_in.gemeentenaam = 'Leiden')
GROUP BY persoon.geslacht
""" ], [
    Application(product, [
        Application(alpha, [ inkomen, geslacht ]),
        Application(alpha, [ eenpersoon, geslacht ])
    ]),
    """\
SELECT persoon.geslacht, SUM(persoon.inkomen), SUM(1)
FROM persoon
GROUP BY persoon.geslacht
""" ], [
    Application(composition, [
        gedeelddoor,
        Application(product, [
            Application(alpha, [ inkomen, geslacht ]),
            Application(alpha, [ eenpersoon, geslacht ])
        ]),
    ]),
    """\
    """ ], [
    Application(composition, [
        gedeelddoor,
        Application(product, [
            Application(alpha, [ inkomen, 
                Application(composition, [ ligtin, woontop ]) 
            ]),
            Application(alpha, [ eenadres, ligtin ]),
        ])
    ]),    
    """\
    """ ], [
    Application(composition, [
        gedeelddoor, 
        Application(product, [
            Application(composition, [
                gedeelddoor, 
                Application(product, [ inkomen, leeftijd ])
            ]),
            leeftijd        
        ])
    ]),
    """\
SELECT persoon.persoon_id, ((persoon.inkomen / persoon.leeftijd) / persoon.leeftijd)
FROM persoon
""" ], [
    Application(alpha, [
        Application(composition, [
            eenpersoon,
            Application(inverse, [
                Application(composition, [
                    werknemer,
                    Application(inclusion, [
                        Application(composition, [ gemeentenaam, ligtin, woontop, werknemer ]),
                        Application(composition, [ denhaag, allebanen ])
                    ])
                ])
            ])
        ]),
        Application(composition, [
            allepersonen,
            Application(inverse, [
                Application(composition, [
                    werknemer,
                    Application(inclusion, [
                        Application(composition, [ gemeentenaam, ligtin, woontop, werknemer ]),
                        Application(composition, [ denhaag, allebanen ])
                    ])
                ])
            ])
        ])
    ]),
    """\
""" ], [
    Application(composition, [
        eenpersoon,
        Application(inverse, [
            Application(composition, [
                werknemer,
                Application(inclusion, [
                    Application(composition, [ gemeentenaam, ligtin, woontop, werknemer ]),
                    Application(composition, [ denhaag, allebanen ])
                ])
            ])
        ])
    ]),
    """\
""" ], [
    Application(composition, [ eenpersoon, werknemer ]),
    """\
""" ], [
    eenbaan,
    """\
""" ], [    # The ones below can potentially be deleted      
    ligtin,
    """\
SELECT adres.adres_id, adres.ligt_in
FROM adres
""" ], [
    Application(composition, [ ligtin, woontop ]),
    """\
SELECT persoon.persoon_id, persoon_woont_op.ligt_in
FROM persoon
JOIN (adres AS persoon_woont_op) ON (persoon_woont_op.adres_id = persoon.woont_op)
""" ]
]

    terms_ordered = [
    [
    Application(composition, [ leeftijd, werknemer ]),
    """\
""" ], [
    Application(product, [ leeftijd, inkomen ]),
    """\
"""], [
    Application(alpha, [ leeftijd, geslacht ]),
    """\
"""], [
    Application(composition, [
        gedeelddoor,
        Application(product, [ inkomen, leeftijd ])
    ]),
    """\
"""]
]
    #show_tests(terms)
    test_terms(terms)
    #test_terms(terms_ordered, ordered = True)


    