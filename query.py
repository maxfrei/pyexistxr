# -*- coding: utf-8 -*-
import os, sys, xmlrpclib
from lxml import etree

class Query(object):
    def __init__(self, proxy):
        self.proxy = proxy
        self.params = {}
        self.info = {}
        self.length = 0
        self.data = None

    def send(self, qtext):
        q_id = self.proxy.executeQuery(qtext, self.params)
        #self.info = self._info(q_id)
        self.length = self._length(q_id)
        self.data = self._fetch(q_id)
        return self.data

    def parse_arg(self, val):
        if isinstance(val, str):
            arg = "'%s'" % val
        elif isinstance(val, unicode):
            arg = "'%s'" % val.encode("utf8")
        elif isinstance(val, etree._Element):
            arg = etree.tostring(val)
        else:
            arg = str(val)
        return arg

    def parse_answer(self, item):
        if isinstance(item, xmlrpclib.Binary):
            item = item.data
        else:
            item = str(item)
        return item

    def _fetch(self, q_id):
        for i in xrange(self.length):
            yield self.proxy.retrieve(q_id, i, self.params)

    def _info(self, q_id):
        return self.proxy.querySummary(q_id)

    def _length(self, q_id):
        return self.proxy.getHits(q_id)

