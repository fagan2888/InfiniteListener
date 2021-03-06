"""
Simple util to check if an artist name is in an SQLlite database.

T. Bertin-Mahieux (2010) Colummbia Unviersity
tb2332@columbia.edu
"""


import os
import os.path
import sys
import time
import copy
import sqlite3
import sqlite3.dbapi2 as sqlite




def die_with_usage():
    print 'usage:'
    print 'python query_db_by_name.py <dbname> <artist name>'
    print ' '
    print 'Query an SQLlist database for a given artist name.'
    print "Assumes there is a table 'artists' with a field 'name'."
    print '<artist name> must be exact in the sense:'
    print '     if weird composed name, add " before and after'
    print '     all " must be removed'
    print '     otherwise, must appear exactly like in EchoNest data'
    print 'RETURN'
    print '  everything for the row containing the artist, or NOT FOUND'
    sys.exit(0)


if __name__ == '__main__':

    if len(sys.argv) < 3:
        die_with_usage()

    dbname = sys.argv[1]
    artist = sys.argv[2]
    artist = artist.replace('"','')


    # check if file exists
    if not os.path.isfile(dbname):
        print 'ERROR:',dbname,'does not exist.'
        sys.exit(0)

    # open connection
    connection = sqlite.connect(dbname)

    # number of element in artists
    nElems = 0

    try:
        # cursor
        cursor = connection.cursor()

        # count number of elements
        query = 'SELECT COUNT(*) FROM artists'
        cursor.execute(query)
        res = cursor.fetchone()
        if len(res) > 0:
            nElems = res[0]
        

        # query
        query = 'SELECT * FROM artists WHERE name='
        query += '"' + artist + '"'
        cursor.execute(query)
        found = cursor.fetchall()
        
    except sqlite3.OperationalError:
        print 'ERROR, wrong database name? artist name with weird signs?'
        connection.close()
        sys.exit(0)

    # close connection
    connection.close()

    # print number of elements in 'artists'
    print "Table 'artists' contains",nElems,'entries.'

    # NOT FOUND
    if len(found) == 0:
        print 'NOT FOUND'
        sys.exit(0)

    if len(found) == 1:
        print len(found),'entry found:'
    else:
        print len(found),'entries found:'
    for entry in found:
        print '  ',entry
    
        
