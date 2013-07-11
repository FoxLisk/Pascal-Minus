program foo;
const cn = 100;
type
myarray = array[0..12] of Integer;
myotherarray = array[0..cn] of Integer;
myrecordtype = record 
foo, bar : Integer
end;
var x : Integer;

procedure p(p1 : Integer;
            p2 : myarray);
const newc = 21;
var y : Integer;
begin
y := 1;
if y = 1 then
p(1, 2)
else
y := (2*(1+3-2))
end;

begin
  p(x, x);
  while 2 <> 3 do
    begin
      p(x, 3); p(4, x)
    end

end

.
