Pascal-Minus
============

This is an implementation of the Pascal- language as specified in Per Brinch Hansen's [On Pascal Compilers](http://www.amazon.com/Brinch-Hansen-Pascal-Compilers/dp/0130830984/ref=sr_1_4?ie=UTF8&qid=1375247876&sr=8-4&keywords=pascal+compilers). It is, in fact, already a slight extension of this work.

Usage

-----

The compiler is the file `pascalm.py`. To compile is simple:

    python pascalm.py my_input_file.pm

This stores the results in my_input_file.pmc

You can then run the code with

    python interpreter.py my_input_file.pmc

This is the simplest way to do things. The python implementation of the interpreter is very slow, so if you want to see greater performance you'll need to compile the C implementation. The compilation is simple:

    gcc -std=C99 interpreter.c -o pascalvm

and running is the same:

    ./pascalvm my_input_file.pmc

but executes tremendously faster - from some limited profiling of a bubble sort, the difference is at least two orders of magnitude.

I have not made any attempt to compile the C interpreter in any system other than gcc on OS X.

Fancy Usage
-----------

All of these (the compiler and both interpreters) accept `-d` or `--debug` as a parameter. This provides a lot of extra debug information in various ways. The two interpreters provide runtime debug information to a dramatic extreme, but not the same information. The compiler provides some extra information it thinks is interesting at compile time, and also outputs the bytecode in a human-readable format to input_file.pmc_debug. This is useful if you're not sure the code is being emitted correctly.

The compiler takes some additional options:

* -o <output file> to specify a different destination
* -i or --interpret to immediately interpret the code using the python interpreter
* -t or --tokens to output the tokenized source
* -b or --bytecodes to output the bytecode before assembly is done

In testing new additions I find generally `python pascalm.py source -d -i` to be the fastest way to get feedback.

Compiler Internals
------------------

This is what would be called perhaps a 3-pass compiler.

1. The scanner runs through the source and tokenizes the output. This is a simple process and mostly just makes sure there are no illegal symbols. One thing that is a bit unusual is that for name tokens, instead of storing some sort of object type with attached information, it simply stores two tokens, like `['name', 'foo']`.

2. The parser is a recursive descent parser, that emits code while reading through source. It creates a list of bytecodes that requires some assembly before consumption. The grammar and first/follow lists are given, and to understand the parsing is a simple matter of matching up function names with generator names. To understand the code emission requires an understanding of the interpreter.

3. The assembler finalizes a few things. Code displacements for various jump statements are emitted by the parser as stand-in labels to be resolved by the assembler. The assembler goes through and replaces instructions like "jump to label 13" with "jump forward 171 instructions"

The interpreter is a bytecode interpreter, using a vaguely-documented bytecode. It is stack-based, and maps cleanly onto the instructions in the Pascal- language. It should be possible to understand the working from reading the better-commented python interpreter and perhaps watching it run in debug mode a few times.

Perhaps the most difficult part of the interpreter to understand is the handling of stack frames. When a procedure is called, two things happen:

1. Any actual parameters are pushed onto the stack. This is why parameter access instructions have negative displacements.
2. A new stack frame is set up on top of the stack, pushing the top 3 values of the stack to be the "static link," "dynamic link," and "return address." The static link is the link to the previous lexical (static) scope. The dynamic link is the link to the previous runtime (dynamic) scope. The return address is the next instruction after the procedure call instruction in the program code. 

Other than this, which execution model I was unable to make very clear in the code itself, the stack behaviour is very straightforward.

Want to work on a compiler?
---------------------------

Send me a pull request! Lots of stuff needs work. I will endeavour to keep the neighbouring todo.pm up to date. If you want to add a feature, pick one off the list and send it in.

Before you do, though, make sure all the tests run, and add some of your own for whatever it is you're implementing. Simply run python test.py in the /src/test directory. If it is silent, you're good to go (after you add your own, of course).
