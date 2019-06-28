import unittest
from cmpl_new import (Name, Alias, TableAlias, Column, ColumnAlias, 
                      ExpressionAlias, Cond, CondAlias, QStruct, 
                      QOperator, QProjection)

class TestName(unittest.TestCase):
    def setUp(self):
        self.hello = Name("Hello")
        self.goodbye = Name("Goodbye")
        self.hello2 = Name(self.hello)
        self.empty = Name("")

    def test_repr(self):
        self.assertEqual(repr(self.hello), "Hello")
        self.assertEqual(repr(self.hello2), "Hello")
        self.assertEqual(repr(self.goodbye), "Goodbye")
        self.assertEqual(repr(self.empty), "")

    def test_bool(self):
        self.assertTrue(bool(self.hello))
        self.assertFalse(bool(self.empty))

    def test_equal(self):
        self.assertTrue(self.hello == self.hello2)
        self.assertFalse(self.hello == self.goodbye)

class TestAlias(unittest.TestCase):
    def setUp(self):
        self.alias = Alias("alias")
        self.empty = Alias("")

    def test_repr(self):
        self.assertEqual(repr(self.alias), " AS alias")
        self.assertEqual(repr(self.empty), "")

class TestTableAlias(unittest.TestCase):
    def setUp(self):
        self.tablealias = TableAlias("table", "old_table")
        self.table = TableAlias("table")
        self.table2 = TableAlias("table", "table")
        self.table_empty = TableAlias("table", "")
        self.empty = TableAlias("")

    def test_get_alias(self):
        self.assertEqual(self.tablealias.get_alias(), "old_table")
        self.assertEqual(self.table.get_alias(), "table")
        self.assertEqual(self.table_empty.get_alias(), "table")

    def test_repr(self):
        self.assertEqual(repr(self.tablealias), "table AS old_table")
        self.assertEqual(repr(self.table), "table")
        self.assertEqual(repr(self.table2), "table")
        self.assertEqual(repr(self.empty), "")

    def test_substitute(self):
        self.table2.substitute_table(Name("table"), Name("new"))
        self.assertEqual(repr(self.table2), "new AS table")

    def test_replace_alias(self):
        self.tablealias.replace_alias(Name("old"), Name("new"))
        self.assertEqual(repr(self.tablealias), "table AS new_table")

class TestColumn(unittest.TestCase):
    def setUp(self):
        self.columnX = Column("old_tbl", "X")
        self.columnX2 = Column("old_tbl", "X")
        self.columnY = Column("", "Y")

    def test_repr(self):
        self.assertEqual(repr(self.columnX), "old_tbl.X")
        self.assertEqual(repr(self.columnY), "Y")

    def test_equal(self):
        self.assertTrue(self.columnX == self.columnX2)
        self.assertFalse(self.columnX == self.columnY)

    def test_replace_table(self):
        self.columnX.replace_table(Name("old"), Name("new"))
        self.assertEqual(repr(self.columnX), "new_tbl.X")

    def test_substitute_table(self):
        self.columnX2.substitute_table(Name("old_tbl"), Name("tmp1"))
        self.assertEqual(repr(self.columnX2), "tmp1.X")

class TestColumnAlias(unittest.TestCase):
    def setUp(self):
        self.column_alias = ColumnAlias("tbl", "leeftijd", "col1")
        self.column_alias_empty1 = ColumnAlias("", "X", "col2")
        self.column_alias_empty2 = ColumnAlias("tbl", "X", "")

    def test_repr(self):
        self.assertEqual(repr(self.column_alias), "tbl.leeftijd AS col1")
        self.assertEqual(repr(self.column_alias_empty1), "X AS col2")
        self.assertEqual(repr(self.column_alias_empty2), "tbl.X")

    def test_get_column(self):
        column = self.column_alias.get_column()
        column2 = Column("tbl", "leeftijd")
        self.assertIsInstance(column, Column)
        self.assertEqual(column, column2)

class TestExpressionAlias(unittest.TestCase):
    def setUp(self):
        col1 = Column("old_tbl", "inkomen")
        col2 = Column("old_tbl", "aantal")
        self.expr1 = ExpressionAlias([col1, col2], alias = "gemiddeld_inkomen", infix = " / ")
        self.expr2 = ExpressionAlias([], alias = "empty", prefix = "dummy")
        self.expr3 = ExpressionAlias([col1], alias = "totaal_inkomen", prefix = "")
        self.expr4 = ExpressionAlias([col1], alias = "totaal_inkomen", prefix = "SUM")
        
    def test_repr(self):
        self.assertEqual(repr(self.expr1), "(old_tbl.inkomen / old_tbl.aantal) AS gemiddeld_inkomen")
        self.assertEqual(repr(self.expr2), "")
        self.assertEqual(repr(self.expr3), "old_tbl.inkomen AS totaal_inkomen")
        self.assertEqual(repr(self.expr4), "SUM(old_tbl.inkomen) AS totaal_inkomen")

    def test_substitute_table(self):
        self.expr1.substitute_table(Name("whatever"), Name("new_tbl"))
        self.assertEqual(repr(self.expr1), "(old_tbl.inkomen / old_tbl.aantal) AS gemiddeld_inkomen")
        self.expr1.substitute_table(Name("old_tbl"), Name("new_tbl"))
        self.assertEqual(repr(self.expr1), "(new_tbl.inkomen / new_tbl.aantal) AS gemiddeld_inkomen")

class TestCond(unittest.TestCase):
    def setUp(self):
        col1 = Column("old_tbl", "inkomen")
        col2 = Column("old_tbl", "aantal")
        self.cond = Cond(col1, col2)

    def test_repr(self):
        self.assertEqual(repr(self.cond), "(old_tbl.inkomen = old_tbl.aantal)")

    def test_substitute_table(self):
        self.cond.substitute_table(Name("old_tbl"), Name("tmp1"))
        self.assertEqual(repr(self.cond), "(tmp1.inkomen = tmp1.aantal)")

class TestCondAlias(unittest.TestCase):
    def setUp(self):
        col1 = Column("X1", "persoon_id")
        col2 = Column("baan", "werknemer_id")
        self.condalias1 = CondAlias("persoon", "X1", col1, col2)
        self.condalias2 = CondAlias("persoon", "X1", col1, col2)

    def test_repr(self):
        self.assertEqual(repr(self.condalias1), "(persoon AS X1) ON (X1.persoon_id = baan.werknemer_id)")

    def test_substitute_table(self):
        self.condalias1.substitute_table(Name("baan"), Name("job"))
        self.condalias1.substitute_table(Name("persoon"), Name("person"))
        self.assertEqual(repr(self.condalias1), "(person AS X1) ON (X1.persoon_id = job.werknemer_id)")

    def test_replace_alias(self):
        self.condalias2.replace_alias(Name("X"), Name("tmp"))
        self.assertEqual(repr(self.condalias2), "(persoon AS tmp1) ON (tmp1.persoon_id = baan.werknemer_id)")

class TestQOperator(unittest.TestCase):
    def test_qoperator(self):
        qoperator = QOperator("SUM", ",")
        self.assertEqual(qoperator.prefix, "SUM")
        self.assertEqual(qoperator.infix, ",")

class TestQProjection(unittest.TestCase):
    def test_qprojection(self):
        qprojection = QProjection(5)
        self.assertEqual(qprojection.dimension, 4)

class TestQStruct(unittest.TestCase):
    def test_repr(self):
        q = QStruct([ColumnAlias("persoon", "persoon_id", "X")], 
                    [ColumnAlias("persoon", "inkomen", "Y")], 
                    TableAlias("tbl_person", "persoon"))
        self.assertEqual(repr(q), """\
SELECT persoon.persoon_id AS X, persoon.inkomen AS Y
FROM tbl_person AS persoon
""")
        q = QStruct([ColumnAlias("", "'*'", "")], [ColumnAlias("", "1", "")], Name(""))
        self.assertEqual(repr(q), """\
SELECT '*', 1
""")
        q = QStruct([ColumnAlias("baan", "baan_id", "X")], 
                    [ColumnAlias("persoon", "inkomen", "Y")], 
                    TableAlias("baan", ""),
                    joins = [CondAlias("tbl_person", "persoon", Column("baan", "werknemer"), Column("persoon", "persoon_id"))])
        self.assertEqual(repr(q), """\
SELECT baan.baan_id AS X, persoon.inkomen AS Y
FROM baan
JOIN (tbl_person AS persoon) ON (baan.werknemer = persoon.persoon_id)
""")
        q = QStruct([ColumnAlias("persoon", "persoon_id", "X")], 
                    [ColumnAlias("persoon", "inkomen", "Y")], 
                    TableAlias("tbl_person", "persoon"),
                    wheres = [Cond(Column("persoon", "inkomen"), Column("", "100000")), 
                              Cond(Column("persoon", "geslacht"), Column("", "'V'"))]
                    )
        self.assertEqual(repr(q), """\
SELECT persoon.persoon_id AS X, persoon.inkomen AS Y
FROM tbl_person AS persoon
WHERE (persoon.inkomen = 100000) AND (persoon.geslacht = 'V')
""")
        q = QStruct([ColumnAlias("persoon", "geslacht", ""), ColumnAlias("persoon", "leeftijd", "")], 
                    [ExpressionAlias([Column("persoon", "inkomen")], "X", prefix = "SUM")], 
                    TableAlias("tbl_person", "persoon"), 
                    groupbys = [Column("persoon", "geslacht"), Column("persoon", "leeftijd")])
        self.assertEqual(repr(q), """\
SELECT persoon.geslacht, persoon.leeftijd, SUM(persoon.inkomen) AS X
FROM tbl_person AS persoon
GROUP BY persoon.geslacht, persoon.leeftijd
""")
        q = QStruct([ColumnAlias("persoon", "persoon_id", "X")], 
                    [ColumnAlias("persoon", "inkomen", "Y")], 
                    TableAlias("tbl_person", "persoon"),
                    orderby = Column("persoon", "inkomen"),
                    orderdir = "asc")
        self.assertEqual(repr(q), """\
SELECT persoon.persoon_id AS X, persoon.inkomen AS Y
FROM tbl_person AS persoon
ORDER BY persoon.inkomen ASC LIMIT 5
""")
        q = QStruct([ColumnAlias("persoon", "persoon_id", "X")], 
                    [ColumnAlias("persoon", "inkomen", "Y")], 
                    TableAlias("tbl_person", "persoon"),
                    orderby = Column("persoon", "inkomen"),
                    orderdir = "desc")
        self.assertEqual(repr(q), """\
SELECT persoon.persoon_id AS X, persoon.inkomen AS Y
FROM tbl_person AS persoon
ORDER BY persoon.inkomen DESC LIMIT 5
""")
        q = QStruct([ColumnAlias("persoon", "persoon_id", "X")], 
                    [ColumnAlias("persoon", "inkomen", "Y")], 
                    TableAlias("tbl_person", "persoon"),
                    distinct = True)
        self.assertEqual(repr(q), """\
SELECT DISTINCT persoon.persoon_id AS X, persoon.inkomen AS Y
FROM tbl_person AS persoon
""")



if __name__ == "__main__":
    unittest.main()