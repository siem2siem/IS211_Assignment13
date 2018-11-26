#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""IS211 Assignment13 - sqlite schema for studentgrade database - Tested in Python 3.6.3 :: Anaconda, Inc."""

import sqlite3


def main():
    conn = sqlite3.connect('studentgrade.db')
    f = open('schema.sql','r')
    sql = f.read()
    conn.executescript(sql)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
