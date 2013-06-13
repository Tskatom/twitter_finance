#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import gdata.spreadsheet.service
import gdata.spreadsheet
import codecs
import sys
import argparse


class UnfoundException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Translator:
    def __init__(self, email, passwd):
        self.client = gdata.spreadsheet.service.SpreadsheetsService()
        self.client.email = email
        self.client.password = passwd
        self.client.source = 'Translate Tools'
        self.client.ProgrammaticLogin()
        self.curr_key = ''
        self.curr_wksht_id = ''
        self.row = 1
        self.col = 1
        self.feed = self.client.GetSpreadsheetsFeed()

    def get_workspace(self, sheet_name='translate_sheet', worksheet_id=1):
        sheet_id = -1
        #get spredsheets list
        for i, entry in enumerate(self.feed.entry):
            if isinstance(entry, gdata.spreadsheet.SpreadsheetsSpreadsheet):
                print i, entry.title.text
                if sheet_name == entry.title.text:
                    sheet_id = i

        if sheet_id == -1:
            print "No such Spreassheet"
            raise UnfoundException("No such spreadsheet %s" % sheet_name)

        self.curr_key = self.feed.entry[sheet_id].id.text.split('/')[-1]
        #get the first worksheet
        wks_feed = self.client.GetWorksheetsFeed(self.curr_key)
        for i, entry in enumerate(wks_feed.entry):
            print i, entry.title.text
        self.curr_wksht_id = wks_feed.\
            entry[worksheet_id].id.text.split('/')[-1]

        print "\n We choose %s in %s" % \
            (wks_feed.entry[worksheet_id].title.text,
             self.feed.entry[sheet_id].title.text)

    def clear_sheet(self):
        list_feed = self.client.GetListFeed(self.curr_key, self.curr_wksht_id)
        count = len(list_feed.entry)
        for i in range(count):
            self.client.DeleteRow(list_feed.entry[i])
            print "Delete %d" % i

    def translate(self, text, lang_from, lang_to, key=None):
        inputValue = '=GoogleTranslate("%s", "%s", "%s")' % \
            (text, lang_from, lang_to)
        if key is None:
            key = text
        #entry = self.client.UpdateCell(row="1",
        #                               col="1", inputValue=inputValue,
        #                               key=self.curr_key,
        #                               wksht_id=self.curr_wksht_id)
        params = {"text": text, "from": lang_from,
                  "to": lang_to, "translation": inputValue,
                  "key": key}
        entry = self.client.InsertRow(params,
                                      self.curr_key,
                                      self.curr_wksht_id)
        if isinstance(entry, gdata.spreadsheet.SpreadsheetsList):
            print "Translated %s" % text

    def get_result(self):
        result = []
        list_feed = self.client.GetListFeed(self.curr_key, self.curr_wksht_id)
        for entry in list_feed.entry:
            r = {}
            for k, v in entry.custom.items():
                r[k] = v.text
            result.append(r)
        return result

    def translate_file(self, text_file, lang_from, lang_to):
        with codecs.open(text_file) as tf:
            i = -1
            for text in tf.readlines():
                print text
                text_pair = text.strip().split("|", 1)
                if len(text_pair) > 1:
                    key = text_pair[0].strip()
                    content = text_pair[1].strip()
                elif len(text_pair) == 1:
                    key = str(i)
                    content = text_pair[0].strip()
                else:
                    print "Wrong Content %s " % text
                    continue
                try:
                    self.translate(content, lang_from, lang_to, key=key)
                except:
                    print "Exception %s \n %s" % (text, sys.exc_info()[0])
                    continue
                i += 1
        result = self.get_result()
        return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--file', type=str,
                    help="the file to be translated, line by line format")
    ap.add_argument('--lan_from', type=str, help='The source language')
    ap.add_argument('--lan_to', type=str,
                    default='en', help='The target language')
    ap.add_argument('--out', type=str, help='The out put file')
    args = ap.parse_args()

    assert args.file, "Please indicate a input file path"
    assert args.lan_from, "Please set up source language type"
    assert args.lan_to, "Please set up target languate type"
    assert args.out, "Please setup a output file"

    translator = Translator('tskatom@gmail.com', '01124789')
    translator.get_workspace()
    translator.clear_sheet()
    result = translator.translate_file(args.file, args.lan_from, args.lan_to)

    with codecs.open(args.out, 'w', encoding='utf-8') as w:
        import prettytable as pt
        table = pt.PrettyTable(["Text", "Translation", "From", "To", "key"])
        table.padding_width = 1

        for r in result:
            text = r['text']
            translation = r['translation']
            key = r['key']
            lan_from = r["from"]
            lan_to = r["to"]
            table.add_row([text, translation, lan_from, lan_to, key])
            #w.write("%s |---| %s\n\t\t%s\n" % (key, text, translation))a
        w.write(table.get_string())


if __name__ == "__main__":
    main()
