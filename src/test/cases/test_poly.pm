program test_poly;
function f1 : void;
begin
  Write(65)
end;
function f2(x : Integer) : void;
begin
  Write(66)
end;
function f3(x : Boolean) : void;
begin
  Write(67)
end;
begin
  f1;
  f2(1);
  f3(True);
end.
