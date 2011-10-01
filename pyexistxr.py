# -*- coding: utf-8 -*-
import os, sys, xmlrpclib

class PyExistXR(object):
    def __init__(self, options = None):
        self.url = ""
        self.db = None
        options = options or {
            "ident": "yes",
            "encoding": "UTF-8",
            "omit-xml-declaration": "yes"
        }
        self.options = xmlrpclib.DictType(options)

    def connect(self, host, port, username, passwd = "", verbose = False):
        self.url = "http://%s:%s@%s:%s/exist/xmlrpc" % (username, passwd, host, port)
        self.db = xmlrpclib.ServerProxy(self.url, verbose = verbose)
        return True

    def get_document(self, path):
        #xml = self.db.getDocument(path, self.options) 
        xml = self.db.getDocumentAsString(path, self.options)
        return xml

    def store_document(self, xml, path, overwrite = 0):
        res = self.db.parse(xml, path, overwrite)
        return res

    def remove_document(self, path):
        res = self.db.remove(path)
        return res

    def create_collection(self, name):
        res = self.db.createCollection(name)
        return res

    def remove_collection(self, path):
        res = self.db.removeCollection(path)
        return res

    def execute_query(self, xquery):
        result_id = self.db.executeQuery(xquery, self.options)
        res = self.db.querySummary(result_id) # {'hits': 1, 'documents': [['my.xml', 421, 1]], 'doctypes': [], 'queryTime': 9}
        #res = self.db.getHits(result_id) # items len
        res = self.db.retrieve(result_id, 1, self.options)  # index out of range
        return res

    def query(self, xquery):
        set_length = 1000
        first_item_index = 1
        res = self.db.query(xquery, set_length, first_item_index, self.options)
        return res.encode("utf8")
