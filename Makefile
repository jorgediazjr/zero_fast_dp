# This is a modified version of eiger2cbf Makefile.dials to use
# after initialization by . fast_dp.ini
# Makefile.dials  was contributed to eiger2cbf by Graeme Winter (Diamond Light Source)
# to work in a DIALS build environment

SHELL = /bin/bash
PREFIX  ?=	$(PWD)
CBFLIB	?=	${CCP4}/lib
CCP4LIB	?=	${CCP4}/lib
CBFINC	?=	${CCP4}/include/cbflib
CCP4INC	?=	${CCP4}/include
CC	?=	gcc
CFLAGS	?=	-std=c99 -g -O3
#FGETLN  ?= 	-lbsd
FGETLN  ?= 	eiger2cbf/fgetln.c



clean: 
	rm -f *.o

all:	build/bin/eiger2cbf \
	build/bin/eiger2cbf_par \
	build/bin/eiger2cbf_4t \
	build/lib/eiger2cbf.so \
	build/bin/eiger2cbf-so-worker \
	build/bin/eiger2params \
	build/bin/xsplambda2cbf

build/bin/eiger2cbf_4t: eiger2cbf/eiger2cbf_4t
	mkdir -p build/bin
	cp eiger2cbf/eiger2cbf_4t build/bin/eiger2cbf_4t
	chmod 755 build/bin/eiger2cbf_4t

build/bin/eiger2cbf_par: eiger2cbf/eiger2cbf_par
	mkdir -p build/bin
	cp eiger2cbf/eiger2cbf_par build/bin/eiger2cbf_par
	chmod 755 build/bin/eiger2cbf_par
	
build/bin/eiger2cbf:  eiger2cbf/eiger2cbf.c eiger2cbf/lz4/lz4.c eiger2cbf/lz4/h5zlz4.c \
	eiger2cbf/bitshuffle/bshuf_h5filter.c \
	eiger2cbf/bitshuffle/bshuf_h5plugin.c \
	eiger2cbf/bitshuffle/bitshuffle.c
	mkdir -p build/bin 
	${CC} ${CFLAGS} -o build/bin/eiger2cbf \
	-I${CBFINC} -I${CCP4INC} \
        -L${CBFLIB} -L${CCP4LIB} -Ieiger2cbf/lz4 \
	eiger2cbf/eiger2cbf.c \
        -Ieiger2cbf/lz4 \
	eiger2cbf/lz4/lz4.c eiger2cbf/lz4/h5zlz4.c \
	eiger2cbf/bitshuffle/bshuf_h5filter.c \
	eiger2cbf/bitshuffle/bshuf_h5plugin.c \
	eiger2cbf/bitshuffle/bitshuffle.c \
	${CBFLIB}/libcbf.a \
	${CCP4LIB}/libhdf5_hl.a \
	${CCP4LIB}/libhdf5.a \
	-lm -lpthread -lz -ldl

build/bin/eiger2params:  eiger2cbf/eiger2params.c \
	eiger2cbf/lz4/lz4.c eiger2cbf/lz4/h5zlz4.c \
	eiger2cbf/bitshuffle/bshuf_h5filter.c \
	eiger2cbf/bitshuffle/bshuf_h5plugin.c \
	eiger2cbf/bitshuffle/bitshuffle.c eiger2cbf/fgetln.c 
	mkdir -p build/bin
	${CC} ${CFLAGS} -o build/bin/eiger2params \
	-I${CBFINC} \
	eiger2cbf/eiger2params.c \
        -Ieiger2cbf/lz4 \
	eiger2cbf/lz4/lz4.c eiger2cbf/lz4/h5zlz4.c \
	eiger2cbf/bitshuffle/bshuf_h5filter.c \
	eiger2cbf/bitshuffle/bshuf_h5plugin.c \
	eiger2cbf/bitshuffle/bitshuffle.c \
	${CCP4LIB}/libhdf5_hl.a \
	${CCP4LIB}/libhdf5.a \
	-lm $(FGETLN) -lpthread -lz -ldl

build/bin/eiger2cbf-so-worker:	eiger2cbf/plugin-worker.c \
	eiger2cbf/lz4 eiger2cbf/lz4/lz4.c eiger2cbf/lz4/h5zlz4.c \
	eiger2cbf/bitshuffle/bshuf_h5filter.c \
	eiger2cbf/bitshuffle/bshuf_h5plugin.c \
	eiger2cbf/bitshuffle/bitshuffle.c
	mkdir -p build/bin
	${CC} ${CFLAGS} -o build/bin/eiger2cbf-so-worker \
	-I${CBFINC} \
	eiger2cbf/plugin-worker.c \
	-Ieiger2cbf/lz4 eiger2cbf/lz4/lz4.c eiger2cbf/lz4/h5zlz4.c \
	eiger2cbf/bitshuffle/bshuf_h5filter.c \
	eiger2cbf/bitshuffle/bshuf_h5plugin.c \
	eiger2cbf/bitshuffle/bitshuffle.c \
	-L${CCP4LIB} -lpthread -lhdf5_hl -lhdf5 -lrt

build/lib/eiger2cbf.so:	eiger2cbf/plugin.c \
	eiger2cbf/lz4 eiger2cbf/lz4/lz4.c eiger2cbf/lz4/h5zlz4.c \
	eiger2cbf/bitshuffle/bshuf_h5filter.c \
	eiger2cbf/bitshuffle/bshuf_h5plugin.c \
	eiger2cbf/bitshuffle/bitshuffle.c
	mkdir -p build/lib
	${CC} ${CFLAGS} -o build/lib/eiger2cbf.so -shared -fPIC \
	-I${CBFINC} \
	eiger2cbf//plugin.c \
	-Ieiger2cbf/lz4 eiger2cbf/lz4/lz4.c eiger2cbf/lz4/h5zlz4.c \
	eiger2cbf/bitshuffle/bshuf_h5filter.c \
	eiger2cbf/bitshuffle/bshuf_h5plugin.c \
	eiger2cbf/bitshuffle/bitshuffle.c \
	-L${CCP4LIB} -lpthread -lhdf5_hl -lhdf5 -lrt

build/bin/xsplambda2cbf:  eiger2cbf/xsplambda2cbf.c \
	eiger2cbf/lz4/lz4.c eiger2cbf/lz4/h5zlz4.c \
	eiger2cbf/bitshuffle/bshuf_h5filter.c \
	eiger2cbf/bitshuffle/bshuf_h5plugin.c \
	eiger2cbf/bitshuffle/bitshuffle.c
	mkdir -p build/bin
	${CC} ${CFLAGS} -o build/bin/xsplambda2cbf \
	-I${CBFINC} \
	eiger2cbf/xsplambda2cbf.c \
        -Ieiger2cbf/lz4 \
	eiger2cbf/lz4/lz4.c eiger2cbf/lz4/h5zlz4.c \
	eiger2cbf/bitshuffle/bshuf_h5filter.c \
	eiger2cbf/bitshuffle/bshuf_h5plugin.c \
	eiger2cbf/bitshuffle/bitshuffle.c \
	${CBFLIB}/libcbf.a \
	${CCP4LIB}/libhdf5_hl.a \
	${CCP4LIB}/libhdf5.a \
	-lm -lpthread -lz -ldl
	

$(PREFIX)/bin:
	mkdir -p $(PREFIX)/bin
	
$(PREFIX)/lib:
	mkdir -p $(PREFIX)/lib

install: all $(PREFIX)/bin $(PREFIX)/lib \
	build/bin/eiger2cbf_par \
	build/bin/eiger2cbf_4t \
	build/bin/eiger2cbf \
	build/bin/eiger2params \
	build/lib/eiger2cbf.so \
	build/bin/eiger2cbf-so-worker \
	build/bin/xsplambda2cbf
	cp build/bin/eiger2cbf $(PREFIX)/bin/eiger2cbf
	chmod 755 $(PREFIX)/bin/eiger2cbf
	cp build/bin/eiger2params $(PREFIX)/bin/eiger2params
	chmod 755 $(PREFIX)/bin/eiger2params
	cp build/bin/eiger2cbf_par $(PREFIX)/bin/eiger2cbf_par
	chmod 755 $(PREFIX)/bin/eiger2cbf_par
	cp build/bin/eiger2cbf_4t $(PREFIX)/bin/eiger2cbf_4t
	chmod 755 $(PREFIX)/bin/eiger2cbf_4t
	cp build/bin/eiger2cbf-so-worker $(PREFIX)/bin/eiger2cbf-so-worker
	chmod 755 $(PREFIX)/bin/eiger2cbf-so-worker
	cp build/lib/eiger2cbf.so $(PREFIX)/lib/eiger2cbf.so
	cp build/lib/eiger2cbf.so $(PREFIX)/bin/eiger2cbf.so
	chmod 755 $(PREFIX)/bin/eiger2cbf.so
	cp build/bin/xsplambda2cbf $(PREFIX)/bin/xsplambda2cbf
	chmod 755 $(PREFIX)/bin/xsplambda2cbf

clean: 
	rm -f *.o build

