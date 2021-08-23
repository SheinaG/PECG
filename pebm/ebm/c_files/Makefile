# file: Makefile	G. Moody	10 April 2003
#
# make description file for compiling epltd_all & bxbep using gcc
#
# Install the WFDB package (http://www.physionet.org/physiotools/wfdb.shtml)
# before attempting to compile these programs.
#
# To compile these programs, just type 'make' at a command prompt while in
# this directory.  This has been tested under GNU/Linux and MS-Windows/Cygwin,
# and it should also work under MacOS/X (Darwin) and all versions of Unix.
#
# See '00README' in this directory for further information.

# CC is the name of your ANSI/ISO C compiler (might be 'cc' on some platforms).
CC = gcc -fPIC

# set this to the appropriate path for WFDB
CFLAGS = -I/usr/local/include/
# set this to the appropriate path for WFDB
LDFLAGS = -L/usr/local/lib/

ETOBJS = epltd_all.o bdac.o classify.o rythmchk.o noisechk.o match.o \
 postclas.o analbeat.o qrsfilt.o

all:		epltd_all easytest2 bxbep

epltd_all:	$(ETOBJS) qrsdet.o
	$(CC) $(LDFLAGS) -o epltd_all $(ETOBJS) qrsdet.o -lwfdb -lm

easytest2:	$(ETOBJS) qrsdet2.o
	$(CC) $(LDFLAGS) -o easytest2 $(ETOBJS) qrsdet2.o -lwfdb -lm

epltd_all.o:	epltd_all.c qrsdet.h inputs.h
	$(CC) $(CFLAGS) -c epltd_all.c

bdac.o:		bdac.c bdac.h qrsdet.h
	$(CC) -c bdac.c

classify.o:	classify.c qrsdet.h bdac.h match.h rythmchk.h analbeat.h \
 postclas.h
	$(CC) $(CFLAGS) -c classify.c

rythmchk.o:	rythmchk.c qrsdet.h
	$(CC) $(CFLAGS) -c rythmchk.c

noisechk.o:	noisechk.c qrsdet.h
	$(CC) -c noisechk.c

match.o:	match.c bdac.h
	$(CC) $(CFLAGS) -c match.c

postclas.o:	postclas.c bdac.h
	$(CC) $(CFLAGS) -c postclas.c

analbeat.o:	analbeat.c bdac.h
	$(CC) -c analbeat.c

qrsfilt.o:	qrsfilt.c qrsdet.h
	$(CC) -c qrsfilt.c

qrsdet.o:	qrsdet.c qrsdet.h
	$(CC) -c qrsdet.c

qrsdet2.o:	qrsdet2.c qrsdet.h
	$(CC) -c qrsdet2.c


bxbep:		bxbep.c inputs.h
	$(CC) $(CFLAGS) $(LDFLAGS) -o bxbep bxbep.c -lwfdb -lm


clean:
	rm -f *.o *~ bxbep epltd_all easytest2

check:
