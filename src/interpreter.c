#include <string.h>
#include <stdio.h>
#include <stdlib.h>

typedef int bool;
#define true 1
#define false 0

#define DEBUG

#define OP_ADD 1
#define OP_AND 2
#define OP_ASSIGN 3
#define OP_CONSTANT 4
#define OP_DIVIDE 5
#define OP_DO 6
#define OP_ENDPROG 8
#define OP_EQUAL 9
#define OP_FIELD 10
#define OP_GOTO 11
#define OP_GREATER 12
#define OP_INDEX 13
#define OP_LESS 14
#define OP_MINUS 15
#define OP_MODULO 16
#define OP_MULTIPLY 17
#define OP_NOT 18
#define OP_NOTEQUAL 19
#define OP_NOTGREATER 20
#define OP_NOTLESS 21
#define OP_OR 22
#define OP_PROGRAM 25
#define OP_SUBTRACT 26
#define OP_VALUE 27
#define OP_VARIABLE 28
#define OP_VARPARAM 29
#define OP_READ 30
#define OP_WRITE 31
#define OP_DEFADDR 32
#define OP_DEFARG 33
#define OP_LOCALVAR 34
#define OP_SHORTVALUE 35
#define OP_BITAND 36
#define OP_BITOR 37
#define OP_BITLSHIFT 38
#define OP_BITRSHIFT 39
#define OP_RETURN 40
#define OP_FUNCTION 41
#define OP_FUNCCALL 42
#define OP_RETURNSPACE 44

#define STACK_SIZE 1000000

typedef struct {
  int* opcodes;
  int length;
} code;

int p = 0, b = 0;
int s = 3;
int* stack;
code program;
bool running = true;

bool get_code(char* const file_name, int *length) {
  int code_size = 1000;
  int* code = (int*) malloc(code_size * sizeof(int));
  int code_length = 0;

  FILE *fp = fopen(file_name, "r");
  if (fp == NULL) {
    printf("Could not open file %s for reading", file_name);
    return false;
  }
  while (true) {
    if (code_length == code_size) {
      int new_size = code_size * 2;
      int* new_code = (int*) malloc(new_size * sizeof(int));
      memcpy(new_code, code, code_length * sizeof(int));
      code = new_code;
      code_size = new_size;
    }

    int ret = fscanf(fp, "%d ", code + code_length);
    if (ret == EOF) {
      break;
    } else if (ret == 0) {
      //no matches
      return false;
    }  
    code_length++;
  }
  fclose(fp);

  int* final_code = (int*) malloc(code_length * sizeof(int));
  memcpy(final_code, code, code_length * sizeof(int));

  program.opcodes = final_code;
  program.length = code_length;
  *length = code_length;
  return true;
}

void error(char* const msg) {
  printf("%s\n", msg);
  running = false;
}

void add() {
  s--;
  stack[s] = stack[s] + stack[s + 1];
  p++;
}

void and() {
  s--;
  if (stack[s] == 1) {
    stack[s] = stack[s + 1] == 1;
  } else {
    stack[s] = 0;
  }
  p++;
}

void divide() {
  s--;
  stack[s] = stack[s] / stack[s + 1];
  p++;
}

void equal() {
  s--;
  stack[s] = stack[s] == stack[s + 1] ? 1 : 0;
  p++;
}

void greater() {
  s--;
  stack[s] = stack[s] > stack[s + 1] ? 1 : 0;
  p++;
}

void less() {
  s--;
  stack[s] = stack[s] < stack[s + 1] ? 1 : 0;
  p++;
}

void minus() {
  stack[s] = -stack[s];
  p++;
}

void modulo() {
  s--;
  stack[s] = stack[s] % stack[s + 1];
  p++;
}

void multiply() {
  s--;
  stack[s] = stack[s] * stack[s + 1];
  p++;
}

void bit_and() {
  s--;
  stack[s] = stack[s] & stack[s + 1];
  p++;
}
void bit_or() {
  s--;
  stack[s] = stack[s] | stack[s + 1];
  p++;
}
void bit_lshift() {
  s--;
  stack[s] = stack[s] << stack[s + 1];
  p++;
}
void bit_rshift() {
  s--;
  stack[s] = stack[s] >> stack[s + 1];
  p++;
}

void not() {
  stack[s] = stack[s] == true ? false : true;
  p++;
}

void notequal() {
  s--;
  stack[s] = stack[s] != stack[s + 1] ? 1 : 0;
  p++;
}

void lte() {
  s--;
  stack[s] = stack[s] > stack[s + 1] ? 0 : 1;
  p++;
}

void gte() {
  s--;
  stack[s] = stack[s] < stack[s + 1] ? 0 : 1;
  p++;
}

void or() {
  s--;
  if (stack[s] == 0) {
    stack[s] = stack[s + 1] == 1;
  } else {
    stack[s] = 1;
  }
  p++;
}

void shortvalue() {
  int var_addr = stack[s];
  stack[s] = stack[var_addr];
  p++;
}

void subtract() {
  s--;
  stack[s] = stack[s] - stack[s + 1];
  p++;
}

void read() {
  int var_addr = stack[s];
  int read_val;
  scanf("%d", &read_val);
  stack[var_addr] = read_val;
  s--;
  //stack[s] = stack[s] + stack[s + 1];
  p++;
}

void write() {
  putc(stack[s], stdout);
  s--;
  p++;
}

//two-arg
void assign(int length) {
  int val_addr = s - length + 1;
  int var_addr = stack[s - length];
  s -= length + 1;
  while (length > 0) {
    stack[var_addr] = stack[val_addr];
    var_addr++;
    val_addr++;
    length--;
  }
  p += 2;
} 

void constant(int val) {
  s++;
  stack[s] = val;
  p += 2;
} 

void _do(int displ) {
  if (stack[s] == 1) {
    p += 2;
  } else {
    p += displ;
  }
} 

void field(int displ) {
  stack[s] = stack[s] + displ;
  p += 2;
}

void _goto(int displ) {
  p += displ;
}

void localvar(int displ) {
  s++;
  stack[s] = b + displ; //top of stack to var address (level = 0)
  p += 2;
}

void value(int length) {
  int var_addr = stack[s];
  while (length > 0) {
    stack[s] = stack[var_addr];
    s++;
    var_addr++;
    length--;
  }
  s--;
  p += 2;
}

void _index(int lower, int upper, int length, int line_no) {
  int i = stack[s];
  if (i < lower || i > upper) {
    char errmsg[60];
    sprintf(errmsg, "Trying to determine past the bounds of an array on line %d", line_no);
    error(errmsg);
  }
  s--;
  int addr = stack[s] + ((i - lower) * length); //length is element lenth
  stack[s] = addr;
  p += 5;
}

void _program(int var_length, int displ) {
  s += var_length - 1;
  p += displ;
}

void variable(int level, int displ) {
  s++;
  int x = b;
  while (level > 0) {
    x = stack[x];
    level--;
  }
  stack[s] = x + displ;
  p += 3;
}

void varparam(int level, int displ) {
  s++;
  int x = b;
  while (level > 0) {
    x = stack[x];
    level--;
  }
  int var_loc = stack[x + displ];
  stack[s] = var_loc;
  p += 3;
}

void _return(int param_length, int return_length) {
  int return_address_last = b - (param_length + 1);
  int l = return_length;
  int _s = s;
  while (l > 0) {
    stack[return_address_last] = stack[_s];
    return_address_last--;
    l--;
    _s--;
  }
  
  p = stack[b + 2];
  s = b;
  s -= param_length + 1;
  b = stack[b + 1];
}

void function(int var_length, int displ, int return_length) {
  s += var_length + 1;
  p += displ;
}

void func_call(int level, int displ, int return_length) {
  s++;
  int static_link = b;
  while (level > 0) {
    static_link = stack[static_link];
    level--;
  }
  stack[s] = static_link;
  stack[s + 1] = b;
  stack[s + 2] = p + 4;
  b = s;
  s = b + 2;
  p += displ;
}

void return_space(int displ) {
  s += displ;
  p += 2;
}

bool interpret(char* const file_name, bool debug) {
  int l;
  bool success = get_code(file_name, &l);
  if (!success) {
    return false;
  }

  stack = (int*) malloc(STACK_SIZE * sizeof(int));
  stack[0] = 0; 
  stack[1] = 0;
  stack[2] = l - 1;
  char *names[] = {
    "UNDEFINED", 
    "ADD",
    "AND",
    "ASSIGN",
    "CONSTANT",
    "DIVIDE",
    "DO",
    "ENDPROC",
    "ENDPROG",
    "EQUAL",
    "FIELD",
    "GOTO",
    "GREATER",
    "INDEX",
    "LESS",
    "MINUS",
    "MODULO",
    "MULTIPLY",
    "NOT",
    "NOTEQUAL",
    "NOTGREATER",
    "NOTLESS",
    "OR",
    "PROCCALL",
    "PROCEDURE",
    "PROGRAM",
    "SUBTRACT",
    "VALUE",
    "VARIABLE",
    "VARPARAM",
    "READ",
    "WRITE",
    "DEFADDR",
    "DEFARG",
    "LOCALVAR",
    "SHORTVALUE"
  };

  while (running) {
    int op = program.opcodes[p];
    if (debug) {
      printf("Handling %s [%d]\n", names[op], op);
    }
    switch(op) {
      case OP_ADD:
        add();
        break;
      case OP_AND:
        and();
        break;
      case OP_DIVIDE:
        divide();
        break;
      case OP_EQUAL:
        equal();
        break;
      case OP_GREATER:
        greater();
        break;
      case OP_LESS:
        less();
        break;
      case OP_MINUS:
        minus();
        break;
      case OP_MODULO:
        modulo();
        break;
      case OP_MULTIPLY:
        multiply();
        break;
      case OP_NOT:
        not();
        break;
      case OP_NOTEQUAL:
        notequal();
        break;
      case OP_NOTGREATER:
        lte();
        break;
      case OP_NOTLESS:
        gte();
        break;
      case OP_OR:
        or();
        break;
      case OP_SHORTVALUE:
        shortvalue();
        break;
      case OP_SUBTRACT:
        subtract();
        break;
      case OP_READ:
        read();
        break;
      case OP_WRITE:
        write();
        break;
      //end no-arg ops
      case OP_ASSIGN:
        assign(program.opcodes[p+1]);
        break;
      case OP_CONSTANT:
        constant(program.opcodes[p+1]);
        break;
      case OP_DO:
        _do(program.opcodes[p+1]);
        break;
      case OP_FIELD:
        field(program.opcodes[p+1]);
        break;
      case OP_GOTO:
        _goto(program.opcodes[p+1]);
        break;
      case OP_LOCALVAR:
        localvar(program.opcodes[p+1]);
        break;
      case OP_VALUE:
        value(program.opcodes[p+1]);
        break;
      //end one-arg opts
      case OP_INDEX:
        _index(program.opcodes[p+1], program.opcodes[p+2], program.opcodes[p+3], program.opcodes[p+4]);
        break;
      case OP_PROGRAM:
        _program(program.opcodes[p+1], program.opcodes[p+2]);
        break;
      case OP_VARIABLE:
        variable(program.opcodes[p+1], program.opcodes[p+2]);
        break;
      case OP_VARPARAM:
        varparam(program.opcodes[p+1], program.opcodes[p+2]);
        break;
      case OP_ENDPROG:
        running = false;
        break;
      case OP_BITAND:
        bit_and();
        break;
      case OP_BITOR:
        bit_or();
        break;
      case OP_BITLSHIFT:
        bit_lshift();
        break;
      case OP_BITRSHIFT:
        bit_rshift();
        break;
      case OP_RETURN:
        _return(program.opcodes[p+1], program.opcodes[p+2]);
        break;
      case OP_FUNCTION:
        function(program.opcodes[p+1],program.opcodes[p+2],program.opcodes[p+3]);
        break;
      case OP_FUNCCALL:
        func_call(program.opcodes[p+1],program.opcodes[p+2],program.opcodes[p+3]);
        break;
      case OP_RETURNSPACE:
        return_space(program.opcodes[p+1]);
        break;
      default:
        running = false;
        char errmsg[20]; 
        sprintf(errmsg, "Unknown opcode %d", op);
        error(errmsg);
        break;

    }

    if (debug) {
      printf("Stack after: ");
      for (int i = 0; i <= s; i++) {
        printf("%d ", stack[i]);
      }
      printf("\n");
    }

  }
  return true;
}

int main(int argc, char* argv[]) {
  if (argc < 2) {
    printf("Error: must provide filename as first argument");
    exit(1);
  }

  char* file_name = argv[1];

  bool debug;
  for (int i = 0; i < argc; i++) {
    if (strcmp(argv[i], "-d") == 0 || strcmp(argv[i], "--debug") == 0) {
      debug = true;
    }
  }

  if (!interpret(file_name, debug)) {
    printf("Error interpreting `%s`", file_name);
  }

  return 0;
}
