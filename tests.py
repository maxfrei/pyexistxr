# -*- coding: utf-8 -*-
import os, sys, random, unittest
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

    def setUp(self):
        print "========== Start ==========="

    def tearDown(self):
        print "=========== End ============"

    def test_api(self):
        self.connect()
        self.create_coll()
        self.store_doc()
        self.get_doc()
        self.xpath()
        self.call_func() # !
        self.query()
        self.remove_doc()
        self.remove_coll()

    def connect(self):
        print "Connecting... ",
        self.db = PyExistXR(self.url, collection = self.test_coll_path)
        is_inst = isinstance(self.db, PyExistXR)
        self.assertEqual(is_inst, True)
        print "successful."

    def create_coll(self):
        print "Creating collection... ",
        res = self.db.create_collection(self.test_coll_path)
        self.assertEqual(res, True)
        print "successful."

    def store_doc(self):
        print "Storing document... ",
        path = os.path.join(self.test_coll_path, self.test_doc_name)
        res = self.db.store_document(self.test_doc,
                                     path,
                                     overwrite = self.overwrite_doc)
        self.assertEqual(res, True)
        print "successful."

    def get_doc(self):
        print "Getting document... ",
        path = os.path.join(self.test_coll_path, self.test_doc_name)
        doc = self.db.get_document(path)
        #print doc
        print "successful."

    def xpath(self):
        print "Verify xpath...",
        q = self.db.xpath("//ul[@id eq 'test']//li")
        res = q.fetch_all()
        self.assertEqual(len(res), 3)
        print "successful."

    def call_func(self):
        print "Verify func...",
        arg = "ololo"
        ns = "'http://localhost/func/' at 'xmldb:exist:///db/test/func.xq'"
        q = self.db.func("func", "test", arg, ns = ns)
        res = q.fetch()
        self.assertEqual(res, arg)
        print "successful."

    def query(self):
        print "Verify query...",
        q = self.db.query("collection('/db/pytest')//ul[@id = 'test']/li[2]/text()")
        res = q.fetch()
        self.assertEqual(res, 'second')
        print "successful."

    def remove_doc(self):
        print "Removing document... ",
        path = os.path.join(self.test_coll_path, self.test_doc_name)
        res = self.db.remove_document(path)
        self.assertEqual(res, True)
        print "successful."

    def remove_coll(self):
        print "Removing collection... ",
        res = self.db.remove_collection(self.test_coll_path)
        self.assertEqual(res, True)
        print "successful."

    def _to_str(self, node):
        return etree.tostring(node,
                              pretty_print=True,
                              xml_declaration=True,
                              encoding="UTF-8")

if __name__ == "__main__":
    unittest.main()
