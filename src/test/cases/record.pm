program recordtest;
type myrec = 
  record
    foo, bar : Integer
  end;
var x : myrec;
begin
  x.foo := 65;
  x.bar := 66;
  Write(x.foo); Write(x.bar)
end.
