# -*- coding: utf-8 -*-
import os, sys, xmlrpclib
from query import Query

class ExistExc(Exception):
	def __init__(self, message = "Unknown error"):
		self.error = message

	def __str__(self):
		return self.error

class PyExistXR(object):
    options = {
        "ident": "yes",
        "encoding": "UTF-8",
        "omit-xml-declaration": "yes"
    }
    
    def __init__(self, url, collection = None, verbose = False):
        self.proxy = self.connect(url, verbose)
        self.collection = collection or ""
        self.options = xmlrpclib.DictType(self.options)

    def connect(self, url, verbose):
        return xmlrpclib.ServerProxy(url, verbose = verbose)

    def query(self, qtext):
        """
        Make xquery
        @qtext - query text as string
        """
        q = Query(self.proxy)
        data = q.send(qtext)
        if q.length == 0:
            return None
        elif q.length == 1: 
            return q.parse_answer(data.next())
        else:
            return map(q.parse_answer, data)

    def xpath(self, qtext):
        """
        Return list of items
        """
        if self.collection:
            qtext = "collection('%s')%s" % (self.collection, qtext)
        q = Query(self.proxy)
        data = q.send(qtext)
        return map(q.parse_answer, data)

    def func(self, module, func, *args, **kwargs):
        """
        Call remote xquery function.
        
        @module - exist module
        @func - function in module
        @args - function arguments - a, b, c
        @ns - namespace 'http://localhost/example/' at 'xmldb:exist:///db/example.xq'
        """
        q = Query(self.proxy)
        ns = kwargs.get("ns", None) or "'http://localhost/%s/' at 'xmldb:exist:///db/%s.xq'" % (module, module)
        context = {
            "module": module,
            "func": func,
            "args": ", ".join(q.parse_arg(i) for i in args),
            "ns": ns
        }
        qtext = """import module namespace %(module)s = %(ns)s;
                    %(module)s:%(func)s(%(args)s)""" % context

        data = q.send(qtext)
        if q.length == 0:
            return None
        elif q.length == 1: 
            return q.parse_answer(data.next())
        else:
            return map(q.parse_answer, data)

    def q(self, qtext, max_length = 1000, ind = 1):
        res = self.proxy.query(qtext, max_length, ind, {})
        return res.encode("utf8")

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

    def store_document(self, doc, path, overwrite = 0):
        """
        Inserts a new document into the database or replace an existing one.
        @doc as string
        @path as string
        @overwrite as bool - default false
        """
        return self.proxy.parse(doc, path, overwrite)

    def get_document(self, path):
        """
        @path as string
        Retrieves a document from the database.
        """
        #f = self.proxy.getDocument # return byte
        f = self.proxy.getDocumentAsString # return str
        return f(path, self.options)

    def remove_document(self, path):
        """
        Removes a document from the database.
        @path as string
        """
        return self.proxy.remove(path)
