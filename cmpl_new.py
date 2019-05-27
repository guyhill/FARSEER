#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  8 07:55:59 2019

@author: tgelsema
"""
import re
from copy import copy, deepcopy

from term import *
from kind import Variable, ObjectTypeRelation, Constant, Operator
from dm import *

table_num = 0

class Name:
    def __init__(self, name):
        self.name = name

    def __bool__(self):
        return bool(repr(self))

    def __eq__(self, other):
        return self.name == other.name

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

    def repr_column(self):
        return Column.__repr__(self)

    def __repr__(self):
        return Column.__repr__(self) + Alias.__repr__(self)

class ExpressionAlias(Alias):
    def __init__(self, args, alias = "", prefix = "", infix = ", "):
        super().__init__(alias)
        self.args = args
        self.prefix = prefix
        self.infix = infix

    def __repr__(self):
        if len(self.args) == 0:
            result = ""
        elif len(self.args) == 1 and self.prefix == "":
            result = repr(self.args[0])
        else:
            argstr = self.infix.join([ repr(a) for a in self.args ])
            result = self.prefix + "(" + argstr + ")" + super().__repr__()
        return result

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
    def __init__(self, selectsdom, selectscod, frm, joins = None, wheres = None, groupbys = None, frozen_qsts = None):
        joins = [] if joins is None else joins
        wheres = [] if wheres is None else wheres
        groupbys = [] if groupbys is None else groupbys
        frozen_qsts = [] if frozen_qsts is None else frozen_qsts    

        self.frozen_qsts = frozen_qsts
        self.selectsdom = selectsdom
        self.selectscod = selectscod
        self.frm = frm
        self.joins = []
        for j in joins:
            self.add_join(j)
        self.wheres = []
        for w in wheres:
            self.add_where(w)
        self.groupbys = groupbys
        #### self.orderbys = orderbys

    def add_join(self, new_join):
        for join in self.joins:
            if repr(join) == repr(new_join): # Code for new join already in existing joins
                break                        # therefore the new join can be omitted
        else:
            self.joins.append(new_join)

    def add_where(self, new_where):
        for where in self.wheres:
            if repr(where) == repr(new_where):
                break
        else:
            self.wheres.append(new_where)

    def freeze(self):
        global table_num

        tablename = f"tmp{table_num}"
        table_num += 1

        frozen_qst = copy(self)
        frozen_qst.tablename = tablename
        column_num = 0
        for s in frozen_qst.selectsdom + frozen_qst.selectscod:
            s.alias = f"col{column_num}"  
            column_num += 1
        frozen_qst.frozen_qsts = []

        self.frozen_qsts.append(frozen_qst)
        self.frm = TableAlias(tablename, "")
        self.selectsdom = [ ColumnAlias(tablename, s.alias, "") for s in frozen_qst.selectsdom ]
        self.selectscod = [ ColumnAlias(tablename, s.alias, "") for s in frozen_qst.selectscod ]
        self.joins = []
        self.wheres = []
        self.groupbys = []
        
        return self

    def __repr__(self):
        sql = ""
        for frozen_qst in self.frozen_qsts:
            sql += f"CREATE TEMPORARY TABLE {frozen_qst.tablename}\n{frozen_qst}"

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
        groupbystr = ""
        for groupby in self.groupbys:
            groupbystr += f", {groupby}" if groupbystr else f"\nGROUP BY {groupby}"
        sql += f"SELECT {colspec}{fromstr}{joinstr}{wherestr}{groupbystr}\n"

        return sql

class QOperator:
    def __init__(self, prefix = "", infix = ""):
        self.prefix = prefix
        self.infix = infix

def freeze_qsts(qsts):

    for qst in qsts:
        qst.freeze()

def cmpl(term):
    global table_num

    table_num = 0
    return do_cmpl(term)

def do_cmpl(term):
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
        qsts.append(do_cmpl(arg))

    freeze_qsts(qsts)

    return do_composition(qsts)

def do_composition(qsts):
    if len(qsts) == 1:
        return qsts[0]

    rhs = qsts.pop()
    lhs = qsts.pop()

    selectsdom = rhs.selectsdom
    frm = rhs.frm
    joins = rhs.joins
    wheres = rhs.wheres

    if isinstance(lhs, QOperator):
        selectscod = [ ExpressionAlias(rhs.selectscod, prefix = lhs.prefix, infix = lhs.infix) ]
    else:
        selectscod = lhs.selectscod
        wheres = lhs.wheres + wheres

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
                c.replace_table(joinfrm.table, alias)

    frozen_qsts = [ f for q in [ rhs, lhs ] for f in q.frozen_qsts ]
    qsts.append(QStruct(selectsdom, selectscod, frm, joins, wheres, [], frozen_qsts))
    return do_composition(qsts)

def cmplproduct(args):
    qsts = []
    for arg in args:
        qsts.append(do_cmpl(arg))

    freeze_qsts(qsts)

    selectsdom = qsts[0].selectsdom
    joins = []
    for qst in qsts[1:]:
        if qst.selectsdom[0].table != selectsdom[0].table:
            joins.append(CondAlias(qst.selectsdom[0].table, "", selectsdom[0].get_column(), qst.selectsdom[0].get_column()))
    selectscod = [s for q in qsts for s in q.selectscod ]
    frm = qsts[0].frm
    joins += [ j for q in qsts for j in q.joins ]
    wheres = [ w for q in qsts for w in q.wheres ]
    groupbys = qsts[0].groupbys
    frozen_qsts = [ f for q in qsts for f in q.frozen_qsts ]
    qst = QStruct(selectsdom, selectscod, frm, joins, wheres, groupbys, frozen_qsts)
    return qst

def cmplinclusion(args):
    qsts = []
    for arg in args:
        qsts.append(do_cmpl(arg))

    freeze_qsts(qsts)

    selectsdom = qsts[0].selectsdom
    joins = []
    for qst in qsts[1:]:
        if qst.selectsdom[0].table != selectsdom[0].table:
            joins.append(CondAlias(qst.selectsdom[0].table, "", selectsdom[0].get_column(), qst.selectsdom[0].get_column()))
    selectscod = deepcopy(selectsdom)
    frm = qsts[0].frm
    joins += [ j for q in qsts for j in q.joins]
    wheres = []
    for i, q in enumerate(qsts):
        if i % 2 == 0: # LHS of comparison
            lhs = q.selectscod[0] # assume 1-dimensional cod only
        else:
            rhs = q.selectscod[0]
            wheres.append(Cond(lhs, rhs))
    frozen_qsts = [ f for q in qsts for f in q.frozen_qsts ]
    qst = QStruct(selectsdom, selectscod, frm, joins, wheres, [], frozen_qsts)
    return qst

def cmplinverse(args):
    qst = QStruct(None, None, None, None, None)
    return qst

def cmplaggregation(args):
    qsts = []
    for arg in args:
        qsts.append(do_cmpl(arg))

    freeze_qsts(qsts)

    selectsdom = qsts[1].selectscod
    joins = []
    qst = qsts[0]
    if qst.selectsdom[0].table != selectsdom[0].table:
        joins.append(CondAlias(qst.selectsdom[0].table, "", qsts[1].selectsdom[0].get_column(), qst.selectsdom[0].get_column()))
    selectscod = []
    for s in qsts[0].selectscod:
        selectscod.append(ExpressionAlias([s.get_column()], "", "SUM"))
    frm = qsts[1].frm
    joins += [ j for j in qsts[0].joins + qsts[1].joins ]
    wheres = [ w for w in qsts[0].wheres + qsts[1].wheres ]
    groupbys = [ s for s in selectsdom if s.table ]
    frozen_qsts = [ f for q in qsts for f in q.frozen_qsts ]
    qst = QStruct(selectsdom, selectscod, frm, joins, wheres, groupbys, frozen_qsts)
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
    #qst = QStruct(None, None, None, None, None)
    if term.name == "(/)":
        qop = QOperator(infix = " / ")
    return qop
    
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
    pass