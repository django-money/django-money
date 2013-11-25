# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
from django.test import TestCase
from django import template
from django.utils import translation

from ..models.fields import MoneyPatched
from moneyed import Money


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

        # with a tag template "money_localize"
        self.assertTemplate(
            '{% load djmoney %}{% money_localize money %}',
            '2,30 zł',
            context={'money': Money(2.3, 'PLN')})

        # without a tag template "money_localize"
        self.assertTemplate(
            '{{ money }}',
            '2,30 zł',
            context={'money': MoneyPatched(2.3, 'PLN')})

        with self.settings(USE_L10N=False):
            # money_localize has a default setting USE_L10N = True
            self.assertTemplate(
                '{% load djmoney %}{% money_localize money %}',
                '2,30 zł',
                context={'money': Money(2.3, 'PLN')})

            # without a tag template "money_localize"
            self.assertTemplate(
                '{{ money }}',
                '2.30 zł',
                context={'money': MoneyPatched(2.3, 'PLN')})
            mp = MoneyPatched(2.3, 'PLN')
            mp.use_l10n = True
            self.assertTemplate(
                '{{ money }}',
                '2,30 zł',
                context={'money': mp})

        self.assertTemplate(
            '{% load djmoney %}{% money_localize money on %}',
            '2,30 zł',
            context={'money': Money(2.3, 'PLN')})

        with self.settings(USE_L10N=False):
            self.assertTemplate(
                '{% load djmoney %}{% money_localize money on %}',
                '2,30 zł',
                context={'money': Money(2.3, 'PLN')})

        self.assertTemplate(
            '{% load djmoney %}{% money_localize money off %}',
            '2.30 zł',
            context={'money': Money(2.3, 'PLN')})

    def testAsVar(self):

        self.assertTemplate(
            '{% load djmoney %}{% money_localize money as NEW_M %}{{NEW_M}}',
            '2,30 zł',
            context={'money': Money(2.3, 'PLN')})

        self.assertTemplate(
            '{% load djmoney %}{% money_localize money off as NEW_M %}{{NEW_M}}',
            '2.30 zł',
            context={'money': Money(2.3, 'PLN')})

        # test zero amount of money
        self.assertTemplate(
            '{% load djmoney %}{% money_localize money off as NEW_M %}{{NEW_M}}',
            '0.00 zł',
            context={'money': Money(0, 'PLN')})

    def testConvert(self):

        self.assertTemplate(
            '{% load djmoney %}{% money_localize "2.5" "PLN" as NEW_M %}{{NEW_M}}',
            '2,50 zł',
            context={})

        self.assertTemplate(
            '{% load djmoney %}{% money_localize "2.5" "PLN" %}',
            '2,50 zł',
            context={})

        self.assertTemplate(
            '{% load djmoney %}{% money_localize amount currency %}',
            '2,60 zł',
            context={'amount': 2.6, 'currency': 'PLN'})
