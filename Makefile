all: cookbook

cookbook: cookbook.s
	as --64 -o cookbook.o cookbook.s
	ld -o cookbook cookbook.o
	chmod +x cookbook

run: cookbook
	./cookbook

clean:
	rm -f cookbook cookbook.o

.PHONY: all run clean
