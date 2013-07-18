program foo;
const cn = 100;
type
myarray = array[0..12] of Integer;
myotherarray = array[0..cn] of Integer;
myrecordtype = record 
foo, bar : Integer
end;
var x : Integer;
myrecord : myrecordtype;
mya      : myarray;

procedure p(p1, p3 : Integer;
            p2 : myarray);
const newc = 21;
var y : Integer;
begin
y := 1;
if y = 1 then
p(1, 2, mya)
else
y := (2*(1+3-2)) + mya[1] * myrecord.foo
end;

begin
  p(x, x, mya);
  while 2 <> 3 do
    begin
      p(x, 3, mya); 
      p(4, x, mya)
    end;
  mya[1] := 5;
  myrecord.foo := 1;
end

.
