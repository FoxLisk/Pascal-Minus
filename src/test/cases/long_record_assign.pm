program longrecord;
type myr = record
  foo, bar, baz : Integer
end;
var x, y : myr;
begin
  x.foo := 65;
  x.bar := 66;
  x.baz := 67;
  y := x;
  Write(y.foo);
  Write(y.bar);
  Write(y.baz)
end.
