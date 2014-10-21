# -*- coding: utf-8 -*-
import xmlrpclib
import mimetypes
from query import Query


for m in [".xqm", ".xql", ".xquery", ".xqy", "xqws"]:
    mimetypes.add_type("application/xquery", m, strict=True)

CHUNK_SIZE = 65536
OPTIONS = {
    "ident": "yes",
    "encoding": "UTF-8",
    "omit-xml-declaration": "yes"
}


class ExistExc(Exception):

    def __init__(self, message="Database error"):
        self.error = message

    def __str__(self):
        return self.error


class PyExistXR(object):

    def __init__(self, url, collection=None, verbose=False, options=None):
        self.proxy = self.connect(url, verbose)
        self.collection = collection or ""
        self.options = xmlrpclib.DictType(options or OPTIONS)

    def connect(self, url, verbose):
        return xmlrpclib.ServerProxy(url, verbose=verbose)

    def query(self, qtext):
        q = Query(self.proxy)
        return q.send(qtext)

    def xpath(self, qtext):
        if self.collection:
            qtext = "collection('%s')%s" % (self.collection, qtext)
        q = Query(self.proxy)
        return q.send(qtext)

    def func(self, module, func, *args, **kwargs):
        """
        Call remote xquery function.

        @module - exist module
        @func - function in module
        @args - function arguments - a, b, c
        @ns - namespace 'http://localhost/example/' at
                        'xmldb:exist:///db/example.xq'
        """
        q = Query(self.proxy)
        ns_tmpl = "'http://localhost/%s/' at 'xmldb:exist:///db/%s.xq'"
        ns = kwargs.get("ns", None) or ns_tmpl % (module, module)
        context = {
            "module": module,
            "func": func,
            "args": ", ".join(q.parse_arg(i) for i in args),
            "ns": ns
        }
        qtext = """import module namespace %(module)s = %(ns)s;
                    %(module)s:%(func)s(%(args)s)""" % context
        return q.send(qtext)

    def q(self, qtext, max_length=1000, ind=1):
        res = self.proxy.query(qtext, max_length, ind, {})
        return res.encode("utf8")

    def create_collection(self, name):
        return self.proxy.createCollection(name)

    def remove_collection(self, path):
        return self.proxy.removeCollection(path)

    def store_document(self, path, doc, overwrite=0):
        """
        Inserts a new xml document into the
        database or replace an existing one.
        """
        return self.proxy.parse(doc, path, overwrite)

    def store(self, path, doc_name, chunk_size=CHUNK_SIZE,
              mimetype=None, overwrite=0):
        """
        Store file into the database or replace an existing one.
        @path - path to local file
        @doc_name - full path to file in database
        @chunk_size
        @mimetype
        @overwrite
        """
        f = open(path, "rb")
        chunk = f.read(chunk_size)
        tmp_fname = self.proxy.upload(xmlrpclib.Binary(chunk), len(chunk))
        while chunk:
            chunk = f.read(chunk_size)
            if chunk:
                self.proxy.upload(
                    tmp_fname, xmlrpclib.Binary(chunk), len(chunk))
        mtype = mimetype or mimetypes.guess_type(path)[0]
        return self.proxy.parseLocal(tmp_fname, doc_name, overwrite, mtype)

    def get_document(self, path):
        f = self.proxy.getDocumentAsString
        return f(path, self.options)

    def remove_document(self, path):
        return self.proxy.remove(path)
