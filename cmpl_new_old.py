#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  8 07:55:59 2019

@author: tgelsema
"""
import re

from term import *
from kind import Variable, ObjectTypeRelation, Constant, Operator
#from dm import data
from dm import *

class Name:
    def __init__(self, name):
        self.name = name
            
    def __repr__(self):
        return self.name
            
class Alias:
    def __init__(self, name, alias):
        self.name = name
        self.alias = alias
        
    def get_alias(self):
        return self.alias if self.alias else self.name

    def append_prefix(self, prefix):
        self.alias = prefix + "_" + self.get_alias()
        return self.get_alias()

    def __repr__(self):
        result = ""
        if self.name:
            result += self.name
            if self.alias and self.alias != self.name:
                result += f" AS {self.alias}"
        return result

class ColumnAlias:
    def __init__(self, tablename, column, alias):
        self.tablename = tablename
        self.column = column
        self.alias = alias

    def append_prefix(self, prefix):
        self.tablename = prefix + "_" + self.tablename
        return self.tablename

    def __repr__(self):
        result = ""
        if self.tablename:
            result += f"{self.tablename}."
        result += self.column
        if self.alias and self.alias != self.column:
            result += f" AS {self.alias}"
        return result

class Cond:
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
        
    def append_prefix(self, prefix):
        self.lhs.append_prefix(prefix)
        self.rhs.append_prefix(prefix)

    def __repr__(self):
        return f'({self.lhs} = {self.rhs})'
            
class CondAlias(Cond, Alias):
    def __init__(self, alias, lhs, rhs):
        self.alias = alias
        self.cond = Cond(lhs, rhs)
    
    def get_alias(self):
        return self.alias.get_alias()

    def append_prefix(self, prefix):
        new_alias = self.alias.append_prefix(prefix)
        self.cond.append_prefix(prefix)
        return new_alias

    def __repr__(self):
        return f'({self.alias}) ON {self.cond}'

class QStruct:    
    def __init__(self, selectsdom, selectscod, frm, joins, wheres): #### , create, groupbys, orderbys):
        #### self.create = create
        self.selectsdom = selectsdom
        self.selectscod = selectscod
        self.frm = frm
        self.joins = joins if joins else []
        self.wheres = wheres if wheres else []
        #### self.groupbys = groupbys
        #### self.orderbys = orderbys
        
    def __repr__(self):
        colspec = ""
        for alias in self.selectsdom + self.selectscod:
            if colspec:
                colspec += ", "
            colspec += repr(alias)
        joinstr = ""
        for join in self.joins:
            joinstr += f" JOIN {join}"
        fromstr = f" FROM {self.frm}" if repr(self.frm) else ""
        wherestr = ""
        for where in self.wheres:
            wherestr += f" AND {where}" if wherestr else f" WHERE {where}"
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
    
def cmplcomposition(args):
    qsts = []
    for arg in args:
        qsts.append(cmpl(arg))
    selectsdom = qsts[-1].selectsdom
    selectscod = qsts[0].selectscod
    frm = qsts[-1].frm
    joins = qsts[-1].joins
    alias_chain = joins[-1].get_alias() if joins else frm.get_alias()
    for i in range(len(qsts) - 1, 0, -1):
        if not qsts[i-1].frm.name:  # qstruct does not originate from any database table,
            continue                # so there is nothing to join.
        joindom = qsts[i-1].selectsdom[0]
        joincod = qsts[i].selectscod[0]
        joincod.tablename = alias_chain
        joinfrm = qsts[i-1].frm
        new_alias_chain = alias_chain + "_" + joinfrm.get_alias()
        joinfrm.alias = new_alias_chain
        joindom.tablename = new_alias_chain
        joins.append(CondAlias(joinfrm, joindom, joincod))
        for j in qsts[i-1].joins:
            new_alias_chain = j.append_prefix(alias_chain)
            joins.append(j)
        alias_chain = new_alias_chain
    for s in selectscod:
        if s.tablename:
            s.tablename = alias_chain
    qst = QStruct(selectsdom, selectscod, frm, joins, [])
    return qst

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
    return cmplobjecttyperelation(term)

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
    frm = Alias(repr(table)[1:-1], "") # cheap hack to get rid of parentheses
    selectsdom = [ ColumnAlias(frm.get_alias(), f"{table}_id", "") ]
    selectscod = [ ColumnAlias("", f"{imm}", "") ]
    qst = QStruct(selectsdom, selectscod, frm, [], [])
    return qst

def cmplobjecttyperelation(term):
    table = findtable(term)
    name = re.sub(' ', '_', term.name)
    frm = Alias(repr(table), repr(table))
    selectsdom = [ ColumnAlias(frm.get_alias(), f"{table}_id", "") ]
    selectscod = [ ColumnAlias(frm.get_alias(), f"{name}", "") ]
    qst = QStruct(selectsdom, selectscod, frm, [], [])
    return qst

def cmplconstant(term):

    selectsdom = [ ColumnAlias("", f"'*'", "") ]
    selectscod = [ ColumnAlias("", f"'{term.name}'", "") ]
    qst = QStruct(selectsdom, selectscod, Alias("",""), [], [])
    return qst

def cmploperator(term):
    qst = QStruct(None, None, None, None, None)
    return qst
    
def test_terms(terms):
    if not isinstance(terms, list):
        terms = [terms]
    for term in terms:
        cterm = cmpl(term)
        print(term)
        print(cterm)
        print("\n")

if __name__ == '__main__':
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
        Application(composition, [ ligtin, woontop ]),
        Application(composition, [ ligtin, gevestigdop, werkgever ]),
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
        Application(inclusion, [
            Application(composition, [ gemeentenaam, ligtin, woontop ]),
            Application(composition, [ leiden, allepersonen ])
        ]),
        Application(composition, [ gemeentenaam, ligtin, woontop ]),
        Application(composition, [ 
            Application(composition, [ gemeentenaam, ligtin ]),
            woontop
        ]),
        Application(composition, [
            gemeentenaam,
            Application(composition, [ ligtin, woontop ])
        ])
    ]
    test_terms(terms)