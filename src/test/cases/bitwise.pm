import lib.writeint;
program bitwise;
var x : Integer;
begin
  x := 1 << 1; {2}
  WriteInt(x);
  Write(10); {\n}
  x := 2 >> 1; {1}
  WriteInt(x);
  Write(10);
  x := 4 | 3; {7}
  WriteInt(x);
  Write(10);
  x := 4 & 6; {6}
  WriteInt(x);
  Write(10)
end.
