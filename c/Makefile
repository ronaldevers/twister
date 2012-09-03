all:
	gcc -c midirwp.c -I/usr/include/python2.7 -fPIC
	ld -shared midirwp.o -lasound -o midirwp.so
