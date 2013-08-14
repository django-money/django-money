# -*- encoding: utf-8
from django.test import TestCase
from django import template
from django.utils import translation

from moneyed import Money
import moneyed


class MoneyLocalizeTestCase(TestCase):

    def setUp(self):
        self.default_language = translation.get_language()
        translation.activate('pl')
        super(TestCase, self).setUp()

    def tearDown(self):
        translation.activate(self.default_language)
        super(TestCase, self).tearDown()

    def assertTemplate(self, template_string, result, context={}):

        c = template.Context(context)
        t = template.Template(template_string)
        self.assertEqual(t.render(c), result)

    def testOnOff(self):

        self.assertTemplate(
            u'{% load djmoney %}{% money_localize money %}',
            u'2,30 zł',
            context={'money':Money(2.3, 'PLN')})

        self.assertTemplate(
            u'{% load djmoney %}{% money_localize money on %}',
            u'2,30 zł',
            context={'money':Money(2.3, 'PLN')})

        self.assertTemplate(
            u'{% load djmoney %}{% money_localize money off %}',
            u'2.30 zł',
            context={'money':Money(2.3, 'PLN')})

    def testAsVar(self):

        self.assertTemplate(
            u'{% load djmoney %}{% money_localize money as NEW_M %}{{NEW_M}}',
            u'2,30 zł',
            context={'money':Money(2.3, 'PLN')})

        self.assertTemplate(
            u'{% load djmoney %}{% money_localize money off as NEW_M %}{{NEW_M}}',
            u'2.30 zł',
            context={'money':Money(2.3, 'PLN')})

    def testConvert(self):

        self.assertTemplate(
            u'{% load djmoney %}{% money_localize "2.5" "PLN" as NEW_M %}{{NEW_M}}',
            u'2,50 zł',
            context={})

        self.assertTemplate(
            u'{% load djmoney %}{% money_localize "2.5" "PLN" %}',
            u'2,50 zł',
            context={})

        self.assertTemplate(
            u'{% load djmoney %}{% money_localize amount currency %}',
            u'2,60 zł',
            context={'amount': 2.6, 'currency': 'PLN'})
