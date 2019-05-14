#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crea ted on Mon Apr  8 07:55:59 2019

@author: tgelsema
"""
import re

from term import *
from kind import Variable, ObjectTypeRelation, Constant, Operator
from dm import *

class Name:
    def __init__(self, name):
        self.name = name

    def __bool__(self):
        return bool(repr(self))

    def __repr__(self):
        if isinstance(self.name, str):
            return self.name
        return repr(self.name)

def testName():
    a = Name("Guido")
    print(a)
    print(bool(a))
    b = Name("")
    print(bool(b))

class Alias:
    def __init__(self, alias):
        self.alias = Name(alias)
        
    def get_alias(self):
        return repr(self.alias)

    def append_prefix(self, prefix):
        if repr(prefix):
            self.alias = Name(repr(prefix) + "_" + self.get_alias())
        return self.get_alias()

    def __repr__(self):
        return f" AS {self.alias}" if self.alias else ""

def testAlias():
    x = Alias("Guido")
    print(x)
    y = Alias("")
    print(y)
    x.append_prefix("test")
    print(x)

class TableAlias(Alias):
    def __init__(self, table, alias):
        self.table = Name(table)
        Alias.__init__(self, alias)

    def get_alias(self):
        return repr(self.alias) if self.alias else repr(self.table)

    def replace_alias(self, table, alias):
        self.alias = Name(repr(self.alias).replace(repr(table), repr(alias), 1))

    def __repr__(self):
        if repr(self.table) == repr(self.alias):
            return repr(self.table)
        return f"{self.table}" + Alias.__repr__(self) if self.table else ""
    
def testTableAlias():
    print("testTableAlias")
    x = TableAlias("tblPersoon", "A")
    print(x)
    print(x.get_alias())
    z = TableAlias("tblPersoon", "")
    print(z.get_alias())
    y = TableAlias("", "B")
    print(y)
    w = TableAlias("X", "X")
    print(w)

class Column:
    def __init__(self, table, column):
        self.table = Name(table)
        self.column = Name(column)

    def append_prefix(self, prefix):
        if repr(prefix):
            self.table = Name(repr(prefix) + "_" + repr(self.table))
        return self.table

    # def replace_table(self, table):
    #     if self.table:
    #         self.table = Name(table)

    def replace_table(self, table, alias):
        self.table = Name(repr(self.table).replace(repr(table), repr(alias), 1))

    def __eq__(self, other):
        return repr(self) == repr(other)

    def __repr__(self):
        return f"{self.table}.{self.column}" if self.table else f"{self.column}"

def testColumn():
    x = Column("tblPersoon", "leeftijd")
    print(x)
    y = Column("", "'Leiden'")
    print(y)
    x.append_prefix("test")
    print(x)

class ColumnAlias(Column, Alias):
    def __init__(self, table, column, alias):
        Column.__init__(self, table, column)
        Alias.__init__(self, alias)

    def get_column(self):
        return Column(self.table, self.column)

    def __repr__(self):
        return Column.__repr__(self) + Alias.__repr__(self)

class Cond:
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
        
    def append_prefix(self, prefix):
        self.lhs.append_prefix(prefix)
        self.rhs.append_prefix(prefix)

    def replace_tables(self, table, alias):
        self.lhs.replace_table(table, alias)
        self.rhs.replace_table(table, alias)

    def __repr__(self):
        return f'({self.lhs} = {self.rhs})'
            
class CondAlias(Cond, TableAlias):
    def __init__(self, table, alias, lhs, rhs):
        TableAlias.__init__(self, table, alias)
        Cond.__init__(self, lhs, rhs)

    def append_prefix(self, prefix):
        Cond.append_prefix(self, prefix)
        new_alias = TableAlias.append_prefix(self, prefix)
        return new_alias

    def replace_alias(self, table, alias):
        Cond.replace_tables(self, table, alias)
        TableAlias.replace_alias(self, table, alias)

    def __repr__(self):
        return f'({TableAlias.__repr__(self)}) ON {Cond.__repr__(self)}'

class QStruct:    
    def __init__(self, selectsdom, selectscod, frm, joins = [], wheres = []): #### , create, groupbys, orderbys):
        #### self.create = create
        self.selectsdom = selectsdom
        self.selectscod = selectscod
        self.frm = frm
        self.joins = []
        for j in joins:
            self.add_join(j)
        self.wheres = wheres
        #### self.groupbys = groupbys
        #### self.orderbys = orderbys

    def add_join(self, new_join):
        for join in self.joins:
            if repr(join) == repr(new_join): # Code for new join already in existing joins
                break                        # therefore the new join can be omitted
        else:
            self.joins.append(new_join)

    def __repr__(self):
        colspec = ""
        for alias in self.selectsdom + self.selectscod:
            if colspec:
                colspec += ", "
            colspec += repr(alias)
        joinstr = ""
        for join in self.joins:
            joinstr += f"\nJOIN {join}"
        fromstr = f"\nFROM {self.frm}" if repr(self.frm) else ""
        wherestr = ""
        for where in self.wheres:
            wherestr += f" AND {where}" if wherestr else f"\nWHERE {where}"
        sql = f"SELECT {colspec}{fromstr}{joinstr}{wherestr}"
        #### if self.create != '':
        ####    sql += """CREATE TEMPORARY TABLE %s\n""" % self.create
        return sql

def cmpl(term):
    if isinstance(term, Application):
        if term.op == composition:
            return cmplcomposition(term.args)
        elif term.op == product:
            return cmplproduct(term.args)
        elif term.op == inclusion:
            return cmplinclusion(term.args)
        elif term.op == inverse:
            return cmplinverse(term.args)
        elif term.op == alpha:
            return cmplaggregation(term.args)
    elif isinstance(term, Variable):
        return cmplvariable(term)
    elif isinstance(term, ObjectTypeRelation):
        return cmplobjecttyperelation(term)
    elif isinstance(term, Constant):
        return cmplconstant(term)
    elif isinstance(term, Operator):
        return cmploperator(term)
    
def cmplcomposition_old(args):
    qsts = []
    for arg in args:
        qsts.append(cmpl(arg))
    selectsdom = qsts[-1].selectsdom
    selectscod = qsts[0].selectscod
    frm = qsts[-1].frm
    joins = qsts[-1].joins
    #alias_chain = joins[-1].get_alias() if joins else frm.get_alias()
    #alias_chain = repr(qsts[-1].selectscod[0].table)
    alias_chain = Name("")
    for i in range(len(qsts) - 1, 0, -1):
        if not qsts[i-1].frm.table: # qstruct does not originate from any database table,
            continue                # so there is nothing to join.
        joindom = qsts[i-1].selectsdom[0].get_column()
        joincod = qsts[i].selectscod[0].get_column()
        alias_chain = joincod.append_prefix(alias_chain)
        joinfrm = qsts[i-1].frm
        #new_alias_chain = alias_chain + "_" + joinfrm.get_alias()
        #joinfrm.alias = new_alias_chain
        #joindom.replace_table(new_alias_chain)
        joinfrm.append_prefix(alias_chain)
        joindom.append_prefix(alias_chain)
        joins.append(CondAlias(joinfrm.table, joinfrm.alias, joindom, joincod))
        for j in qsts[i-1].joins:
            new_alias_chain = j.append_prefix(alias_chain)
            joins.append(j)
        #alias_chain = new_alias_chain
    for s in selectscod:
        s.append_prefix(alias_chain)
    wheres = [ w for q in qsts for w in q.wheres ]
    qst = QStruct(selectsdom, selectscod, frm, joins, wheres)
    return qst

def cmplcomposition(args):
    qsts = []
    for arg in args:
        qsts.append(cmpl(arg))
    return do_composition(qsts)

def do_composition(qsts):
    if len(qsts) == 1:
        return qsts[0]

    rhs = qsts.pop()
    lhs = qsts.pop()
    selectsdom = rhs.selectsdom
    selectscod = lhs.selectscod
    frm = rhs.frm
    joins = rhs.joins
    wheres = lhs.wheres + rhs.wheres

    if lhs.frm.table:
        joinfrm = lhs.frm 
        joincod = rhs.selectscod[0].get_column()
        joindom = lhs.selectsdom[0].get_column()
        if joincod == joindom:
            alias = Name(f"{joincod.table}")
        else:
            alias = Name(f"{joincod.table}_{joincod.column}")

            joinfrm.alias = alias
            joindom.table = alias
            joins.append(CondAlias(joinfrm.table, joinfrm.alias, joindom, joincod))

        for j in lhs.joins:
            j.replace_alias(joinfrm.table, alias)
            joins.append(j)

        for c in selectscod:
            #c.table = alias
            c.replace_table(joinfrm.table, alias)

    qsts.append(QStruct(selectsdom, selectscod, frm, joins, wheres))
    return do_composition(qsts)

def cmplproduct(args):
    qsts = []
    for arg in args:
        qsts.append(cmpl(arg))
    selectsdom = qsts[0].selectsdom
    selectscod = [s for q in qsts for s in q.selectscod]
    frm = qsts[0].frm
    joins = [ j for q in qsts for j in q.joins]
    qst = QStruct(selectsdom, selectscod, frm, joins, [])
    return qst

def cmplinclusion(args):
    qsts = []
    for arg in args:
        qsts.append(cmpl(arg))
    selectsdom = qsts[0].selectsdom
    selectscod = selectsdom
    frm = qsts[0].frm
    joins = [ j for q in qsts for j in q.joins]
    wheres = []
    for i, q in enumerate(qsts):
        if i % 2 == 0: # LHS of comparison
            lhs = q.selectscod[0] # assume 1-dimensional cod only
        else:
            rhs = q.selectscod[0]
            wheres.append(Cond(lhs, rhs))
    qst = QStruct(selectsdom, selectscod, frm, joins, wheres)
    return qst

def cmplinverse(args):
    qst = QStruct(None, None, None, None, None)
    return qst

def cmplaggregation(args):
    qst = QStruct(None, None, None, None, None)
    return qst

def cmplvariable(term):
    if term.codomain == one or term.name[:3] == "een":
        return cmplimmediate(term)

    # Code below is identical to cmplobjecttyperelation()
    table = findtable(term)
    name = re.sub(' ', '_', term.name)
    frm = TableAlias(table, table)
    selectsdom = [ ColumnAlias(frm.get_alias(), f"{table}_id", "") ]
    selectscod = [ ColumnAlias(frm.get_alias(), f"{name}", "") ]
    qst = QStruct(selectsdom, selectscod, frm, [], [])
    return qst

def findtable(term):
    for d in data:
        if foundsome(term, d.constr):
            return d
    return None
        
def foundsome(subterm, term):
    if term.__class__.__name__ == 'Application':
        for arg in term.args:
            if foundsome(subterm, arg):
                return True
    if term.__class__.__name__ == 'Variable' or term.__class__.__name__ == "Constant" or term.__class__.__name__ == "ObjectTypeRelation":
        if term.name == re.sub(' ', '_', subterm.name):
            return True
    return False
    
def cmplimmediate(term):
    if term.codomain == one:
        imm = "'*'"
    elif term.name[:3] == "een":
        imm = "1"
    table = term.domain.name
    frm = TableAlias(table, "") 
    selectsdom = [ ColumnAlias(frm.get_alias(), f"{table}_id", "") ]
    selectscod = [ ColumnAlias("", f"{imm}", "") ]
    qst = QStruct(selectsdom, selectscod, frm, [], [])
    return qst

def cmplobjecttyperelation(term):
    table = findtable(term)
    name = re.sub(' ', '_', term.name)
    frm = TableAlias(table, table)
    selectsdom = [ ColumnAlias(frm.get_alias(), f"{table}_id", "") ]
    selectscod = [ ColumnAlias(frm.get_alias(), f"{name}", "") ]
    qst = QStruct(selectsdom, selectscod, frm, [], [])
    return qst

def cmplconstant(term):
    name = re.sub(" ", "_", term.name)
    selectsdom = [ ColumnAlias("", f"'*'", "") ]
    selectscod = [ ColumnAlias("", f"'{name}'", "") ]
    qst = QStruct(selectsdom, selectscod, TableAlias("",""), [], [])
    return qst

def cmploperator(term):
    qst = QStruct(None, None, None, None, None)
    return qst
    
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
    #testTableAlias()
    #testColumn()
    #quit()
    # create = Name('tmp_persoon')
    # selectsdom = [Alias('baan_werknemer.persoon_id', 'baan_werknemer.persoon_id')]
    # selectscod = [Alias('baan_werknemer.naam', 'baan_werknemer.naam')]
    # frm = Alias('baan', 'baan')
    # print(frm)
    # joins = [CondAlias('persoon', 'baan_werknemer', 'baan_werknemer.persoon_id', 'baan.werknemer')]
    # wheres = [Cond('baan_werknemer.woont_in', 'Amsterdam'), Cond('baan.functie', 'tandarts')]
    # groupbys = []
    # orderbys = []
    # #qst = QStruct(create, selectsdom, selectscod, frm, joins, wheres, groupbys, orderbys)
    # qst = QStruct(selectsdom, selectscod, frm, joins, wheres)
    # print(qst)
    # print(wheres)
    # print(joins)
    # q = cmplobjecttyperelation(woontop)
    # r = cmplobjecttyperelation(ligtin)
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
    test_terms(terms, [])