# encoding=utf-8

import os
import pytest
from ShulchanArukh import *

def setup_module():
    Root.create_skeleton('test_document.xml')

def teardown_module():
    os.remove('test_document.xml')

def test_add_titles():
    root = Root('test_document.xml')
    base_text = root.get_base_text()
    base_text.add_titles('Shulchan Arukh', u'שולחן ערוך')

    assert unicode(root) == u'<root><base_text><en_title>Shulchan Arukh</en_title><he_title>שולחן ערוך</he_title>' \
                                u'</base_text><commentaries/></root>'

def test_add_commentary():
    root = Root('test_document.xml')
    commentaries = root.get_commentaries()
    shach = commentaries.add_commentary('Shach', u'ש"ך')

    assert isinstance(shach, Commentary)
    assert unicode(shach) == u'<commentary id="1"><en_title>Shach</en_title><he_title>ש"ך</he_title></commentary>'
    assert unicode(commentaries) == u'<commentaries>{}</commentaries>'.format(shach.Tag)
    assert unicode(root) == u'<root><base_text/>{}</root>'.format(unicode(commentaries.Tag))


class TestAddVolume(object):

    def test_add_volume(self):
        vol = 'some really interesting text'
        root = Root('test_document.xml')
        base_text = root.get_base_text()
        volume = base_text.add_volume(vol, 1)

        assert isinstance(volume, Volume)
        assert unicode(volume) == u'<volume num="1">some really interesting text</volume>'
        assert unicode(base_text) == u'<base_text>{}</base_text>'.format(unicode(volume))
        assert unicode(root) == u'<root>{}<commentaries/></root>'.format(unicode(base_text))

    def test_add_multiple_volumes(self):
        vol_a, vol_b, vol_c = 'first', 'second', 'third'
        root = Root('test_document.xml')
        base_text = root.get_base_text()
        v3 = base_text.add_volume(vol_c, 3)
        v1 = base_text.add_volume(vol_a, 1)
        v2 = base_text.add_volume(vol_b, 2)

        assert unicode(base_text) == u'<base_text>{}{}{}</base_text>'.format(unicode(v1), unicode(v2), unicode(v3))
        assert unicode(root) == u'<root>{}<commentaries/></root>'.format(unicode(base_text))

class TestMarkSimanim(object):

    def test_simple_mark(self):
        raw_text = u'<volume num="1">@00א\nסימן ראשון\n@00ב\nסימן שני</volume>'
        v = Volume(BeautifulSoup(raw_text, 'xml').volume)
        v.mark_simanim(u'@00([\u05d0-\u05ea])')

        assert len(v.get_child()) == 2
        assert unicode(v) == u'<volume num="1"><siman num="1">סימן ראשון\n</siman><siman num="2">סימן שני</siman></volume>'

    def test_out_of_order(self):
        raw_text = u'<volume num="1">@00ב\nסימן שני\n@00א\nסימן ראשון</volume>'
        v = Volume(BeautifulSoup(raw_text, 'xml').volume)
        v.mark_simanim(u'@00([\u05d0-\u05ea])')

        assert len(v.get_child()) == 2
        assert unicode(v) == u'<volume num="1"><siman num="1">סימן ראשון</siman><siman num="2">סימן שני\n</siman></volume>'

    def test_duplicate_siman(self):
        raw_text = u'<volume num="1">@00א\nסימן ראשון\n@00א\nסימן שני</volume>'
        v = Volume(BeautifulSoup(raw_text, 'xml').volume)
        with pytest.raises(DuplicateChildError):
            v.mark_simanim(u'@00([\u05d0-\u05ea])')

    def test_start_mark(self):
        raw_text = u'<volume num="1">some random stuff\nstart\n@00א\nסימן ראשון\n@00ב\nסימן שני</volume>'
        v = Volume(BeautifulSoup(raw_text, 'xml').volume)
        v.mark_simanim(u'@00([\u05d0-\u05ea])', start_mark=u'start')

        assert len(v.get_child()) == 2
        assert unicode(v) == u'<volume num="1"><siman num="1">סימן ראשון\n</siman><siman num="2">סימן שני</siman></volume>'

    def test_nonsense_before_first_mark(self):
        raw_text = u'<volume num="1">\n@00א\nסימן ראשון\n@00ב\nסימן שני</volume>'
        v = Volume(BeautifulSoup(raw_text, 'xml').volume)
        with pytest.raises(AssertionError):
            v.mark_simanim(u'@00([\u05d0-\u05ea])')

    def test_title(self):
        raw_text = u'<volume num="1">@11\nThe Title\n@00א\nסימן ראשון\n@00ב\nסימן שני</volume>'
        v = Volume(BeautifulSoup(raw_text, 'xml').volume)
        v.mark_simanim(u'@00([\u05d0-\u05ea])', specials={u'@11': {'name': 'title'}})

        assert len(v.get_child()) == 2
        assert unicode(v) == u'<volume num="1"><title found_after="0">The Title\n</title>' \
                             u'<siman num="1">סימן ראשון\n</siman><siman num="2">סימן שני</siman></volume>'

    def test_multi_line(self):
        raw_text = u'<volume num="1">@11\nSome\nlines\nof\ntext\n@12\n@00א\nסימן ראשון\n@00ב\nסימן שני</volume>'
        v = Volume(BeautifulSoup(raw_text, 'xml').volume)
        v.mark_simanim(u'@00([\u05d0-\u05ea])', specials={u'@11': {'name': 'intro', 'end': '@12'}})

        assert len(v.get_child()) == 2
        assert unicode(v) == u'<volume num="1"><intro found_after="0">Some\nlines\nof\ntext\n</intro>' \
                             u'<siman num="1">סימן ראשון\n</siman><siman num="2">סימן שני</siman></volume>'

    def test_between_segments(self):
        raw_text = u'<volume num="1">@00א\nסימן ראשון\n@11\nThe Title\n@00ב\nסימן שני</volume>'
        v = Volume(BeautifulSoup(raw_text, 'xml').volume)
        v.mark_simanim(u'@00([\u05d0-\u05ea])', specials={u'@11': {'name': 'title'}})

        assert len(v.get_child()) == 2
        assert unicode(v) == u'<volume num="1"><siman num="1">סימן ראשון\n</siman><title found_after="1">The Title\n' \
                             u'</title><siman num="2">סימן שני</siman></volume>'

    def test_multi_between_segments(self):
        raw_text = u'<volume num="1">@00א\nסימן ראשון\n@11\nSome\nlines\nof\ntext\n@12\n@00ב\nסימן שני</volume>'
        v = Volume(BeautifulSoup(raw_text, 'xml').volume)
        v.mark_simanim(u'@00([\u05d0-\u05ea])', specials={u'@11': {'name': 'intro', 'end': '@12'}})

        assert len(v.get_child()) == 2
        assert unicode(v) == u'<volume num="1"><siman num="1">סימן ראשון\n' \
                             u'</siman><intro found_after="1">Some\nlines\nof\ntext\n</intro>' \
                             u'<siman num="2">סימן שני</siman></volume>'

    def test_consecutive_specials(self):
        raw_text = u'<volume num="1">@00א\nסימן ראשון\n@11\nThe Title\n@33\nThe Intro\n@00ב\nסימן שני</volume>'
        v = Volume(BeautifulSoup(raw_text, 'xml').volume)
        v.mark_simanim(u'@00([\u05d0-\u05ea])', specials={u'@11': {'name': 'title'}, u'@33': {'name': 'intro'}})

        assert len(v.get_child()) == 2
        assert unicode(v) == u'<volume num="1"><siman num="1">סימן ראשון\n</siman><title found_after="1">The Title\n' \
                             u'</title><intro found_after="1">The Intro\n</intro><siman num="2">סימן שני</siman></volume>'

    def test_matches_two_specials(self):
        raw_text = u'<volume num="1">@00א\nסימן ראשון\n@11\nThe Title\n@1\nThe Intro\n@00ב\nסימן שני</volume>'
        v = Volume(BeautifulSoup(raw_text, 'xml').volume)
        with pytest.raises(AssertionError):
            v.mark_simanim(u'@00([\u05d0-\u05ea])', specials={u'@11': {'name': 'title'}, u'@1': {'name': 'intro'}})

    def test_special_at_end(self):
        raw_text = u'<volume num="1">@00א\nסימן ראשון\n@00ב\nסימן שני\n@11\nThe Title\n</volume>'
        v = Volume(BeautifulSoup(raw_text, 'xml').volume)
        v.mark_simanim(u'@00([\u05d0-\u05ea])', specials={u'@11': {'name': 'title'}})

        assert len(v.get_child()) == 2
        assert unicode(v) == u'<volume num="1"><siman num="1">סימן ראשון\n</siman><siman num="2">סימן שני\n</siman>' \
                             u'<title found_after="2">The Title\n</title></volume>'

    def test_multi_line_at_end(self):
        raw_text = u'<volume num="1">@00א\nסימן ראשון\n@00ב\nסימן שני\n@11\nThe\nmulti\nline\nTitle\n@12</volume>'
        v = Volume(BeautifulSoup(raw_text, 'xml').volume)
        v.mark_simanim(u'@00([\u05d0-\u05ea])', specials={u'@11': {'name': 'title', 'end': '@12'}})

        assert len(v.get_child()) == 2
        assert unicode(v) == u'<volume num="1"><siman num="1">סימן ראשון\n</siman><siman num="2">סימן שני\n</siman>' \
                             u'<title found_after="2">The\nmulti\nline\nTitle\n</title></volume>'

        # no end mark at end of file
        raw_text = u'<volume num="1">@00א\nסימן ראשון\n@00ב\nסימן שני\n@11\nThe\nmulti\nline\nTitle\n</volume>'
        v = Volume(BeautifulSoup(raw_text, 'xml').volume)
        v.mark_simanim(u'@00([\u05d0-\u05ea])', specials={u'@11': {'name': 'title', 'end': '@12'}})

        assert len(v.get_child()) == 2
        assert unicode(v) == u'<volume num="1"><siman num="1">סימן ראשון\n</siman><siman num="2">סימן שני\n</siman>' \
                             u'<title found_after="2">The\nmulti\nline\nTitle\n</title></volume>'


