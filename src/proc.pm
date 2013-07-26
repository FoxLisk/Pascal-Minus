program proctest;
var gx, gy : Integer;
procedure p(x : Integer; var y : Integer);
begin
  gy := 100;
end;

begin
gx := 101;
gy := 999;
p(gx, gy)
end.
