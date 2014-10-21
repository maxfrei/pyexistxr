# -*- coding: utf-8 -*-
import os
import unittest
from pyexistxr import PyExistXR
from lxml import etree


class TestPyExistXR(unittest.TestCase):

    url = "http://admin:@localhost:8080/exist/xmlrpc"
    overwrite_doc = 1
    test_coll_path = "/db/pytest"
    test_doc_name = "pytest.xml"
    test_doc = """
    <root>
      <ul id='test'>
        <li id='1'>first</li>
        <li id='2'>second</li>
        <li id='3'>third</li>
      </ul>
    </root>
    """

    def test_api(self):
        self.connect()
        self.create_coll()
        self.store_doc()
        self.get_doc()
        self.xpath()
        self.call_func()
        self.query()
        self.remove_doc()
        self.remove_coll()

    def connect(self):
        self.db = PyExistXR(self.url, collection=self.test_coll_path)
        is_inst = isinstance(self.db, PyExistXR)
        self.assertEqual(is_inst, True)

    def create_coll(self):
        res = self.db.create_collection(self.test_coll_path)
        self.assertEqual(res, True)

    def store_doc(self):
        path = os.path.join(self.test_coll_path, self.test_doc_name)
        res = self.db.store_document(
            path, self.test_doc, overwrite=self.overwrite_doc)
        self.assertEqual(res, True)

    def get_doc(self):
        path = os.path.join(self.test_coll_path, self.test_doc_name)
        self.db.get_document(path)

    def xpath(self):
        q = self.db.xpath("//ul[@id eq 'test']//li")
        res = q.fetch_all()
        self.assertEqual(len(res), 3)

    def call_func(self):
        arg = "ololo"
        ns = "'http://localhost/func/' at 'xmldb:exist:///db/test/func.xq'"
        q = self.db.func("func", "test", arg, ns=ns)
        res = q.fetch()
        self.assertEqual(res, arg)

    def query(self):
        q = self.db.query(
            "collection('/db/pytest')//ul[@id = 'test']/li[2]/text()")
        res = q.fetch()
        self.assertEqual(res, 'second')

    def remove_doc(self):
        path = os.path.join(self.test_coll_path, self.test_doc_name)
        res = self.db.remove_document(path)
        self.assertEqual(res, True)

    def remove_coll(self):
        res = self.db.remove_collection(self.test_coll_path)
        self.assertEqual(res, True)

    def _to_str(self, node):
        return etree.tostring(
            node, pretty_print=True, xml_declaration=True, encoding="UTF-8")


if __name__ == "__main__":
    unittest.main()
