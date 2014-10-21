# -*- coding: utf-8 -*-
import xmlrpclib
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
        self.info = self._info(q_id)
        self.length = self._length(q_id)
        self.data = self._data(q_id)
        return self

    def fetch(self):
        try:
            item = self.data.next()
            return self.parse_answ(item)
        except StopIteration:
            return None

    def fetchall(self):
        return map(self.parse_answ, self.data)

    def parse_arg(self, val):
        if isinstance(val, str) or isinstance(val, unicode):
            arg = "'%s'" % val
        elif isinstance(val, etree._Element):
            arg = etree.tostring(val)
        else:
            arg = str(val)
        return arg

    def parse_answ(self, item):
        if isinstance(item, xmlrpclib.Binary):
            item = item.data
        else:
            item = str(item)
        return etree.fromstring(item)

    def __len__(self):
        return self.length

    def __iter__(self):
        while True:
            item = self.data.next()
            yield self.parse_answ(item)

    def __getitem__(self, key):
        return self.fetch_all()[key]

    def __getslice__(self, start=0, end=2147483647):
        return self.fetch_all()[start: end]

    def _data(self, q_id):
        for i in xrange(self.length):
            yield self.proxy.retrieve(q_id, i, self.params)

    def _info(self, q_id):
        return self.proxy.querySummary(q_id)

    def _length(self, q_id):
        return self.proxy.getHits(q_id)
