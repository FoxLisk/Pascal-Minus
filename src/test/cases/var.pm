program vars;
var x, y : Integer;
procedure p(var p1 : Integer);
begin
  p1 := 999
end;
begin
x := 11;
y := 22;
p(x);
y := x
end.

