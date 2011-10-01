# -*- coding: utf-8 -*-
import os, sys, xmlrpclib
from lxml import etree

class PyExistXR(object):
    options = {
        "ident": "yes",
        "encoding": "UTF-8",
        "omit-xml-declaration": "yes"
    }
    
    def __init__(self, collection = None):
        self.url = ""
        self.proxy = None
        self.query = Query(self, collection)
        self.options = xmlrpclib.DictType(self.options)

    def connect(self, host, port, username, passwd = "", verbose = False):
        self.url = "http://%s:%s@%s:%s/exist/xmlrpc" % (username, passwd, host, port)
        self.proxy = xmlrpclib.ServerProxy(self.url, verbose = verbose)
        return True

    def get_document(self, path):
        """
        @path as string
        Retrieves a document from the database.
        """
        #f = self.proxy.getDocument # return byte
        f = self.proxy.getDocumentAsString # return str
        return f(path, self.options)

    def store_document(self, doc, path, overwrite = 0):
        """
        Inserts a new document into the database or replace an existing one.
        @doc as string
        @path as string
        @overwrite as bool - default false
        """
        return self.proxy.parse(doc, path, overwrite)

    def remove_document(self, path):
        """
        Removes a document from the database.
        @path as string
        """
        return self.proxy.remove(path)

    def create_collection(self, name):
        """
        Creates a new collection
        @name as string
        """
        return self.proxy.createCollection(name)

    def remove_collection(self, path):
        """
        Removes a collection from the database (including all of its documents and sub-collections).
        @name as string
        """
        return self.proxy.removeCollection(path)
    

class Query(object):
    def __init__(self, db, collection):
        self.db = db
        self.coll = collection or ""
        self.params = {}

    def send(self, qtext):
        q_id = self.db.proxy.executeQuery(qtext, self.params)
        q_info = self._qinfo(q_id)
        q_len = q_info.get("hits")
        return {"len": q_len, "data": self._fetch(q_id, q_len)}

    def _fetch(self, q_id, q_len = None):
        q_len = q_len or self.db.proxy.getHits(q_id)
        for i in xrange(q_len):
            yield self.db.proxy.retrieve(q_id, i, self.params)

    def _qinfo(self, q_id):
        return self.db.proxy.querySummary(q_id)
    
    def xpath(self, qtext, as_xml = False):
        """
        Return list of items
        """
        res = self.send(qtext)
        return [self._parse_answer(item, as_xml) for item in res["data"]]

    def func(self, module, func, ns = None, as_xml = False, *args):
        """
        Call remote xquery function.
        
        @module - exist module
        @func - function in module
        @args - function arguments
        @kwargs - additional parameters
        """
        ns = ns or "'http://localhost/%s/' at 'xmldb:exist:///db/%s.xq'" % (module, module)
        context = {
            "module": module,
            "func": func,
            "args": ", ".join(self._parse_arg(i) for i in args),
            "ns": ns
        }
        qtext = """import module namespace %(module)s = %(ns)s;
                    %(module)s:%(func)s(%(args)s)""" % context

        res = self.send(qtext)
        data = res["data"]
        if res["len"] == 1:
            return self._parse_answer(data.next(), as_xml)
        else:
            return [self._parse_answer(item, as_xml) for item in data]

    def _parse_arg(self, val):
        if isinstance(val, str):
            arg = "'%s'" % val
        elif isinstance(val, unicode):
            arg = "'%s'" % val.encode("utf8")
        elif isinstance(val, etree._Element):
            arg = etree.tostring(val)
        else:
            arg = str(val)
        return arg

    def _parse_answer(self, item, as_xml):
        if isinstance(item, xmlrpclib.Binary):
            item = item.data
        else:
            item = str(item)
        if as_xml:
            item = etree.fromstring(item)
        return item

    def q(self, qtext):
        set_length = 1000
        first_item_index = 1
        res = self.db.proxy.query(qtext, set_length, first_item_index, self.params)
        return res.encode("utf8")

