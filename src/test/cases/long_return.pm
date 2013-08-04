{import lib.writeint;}
program long_return;
const LIST_LENGTH = 10;
type list = array[1..LIST_LENGTH] of Integer;
var myList : list; idx : Integer;
function return_long : list;
  var i : Integer; 
      x : list;
  begin
    i := 1;
    while i <= LIST_LENGTH do
      begin
        x[i] := i + 64;
        i := i + 1;
      end;
    return x;
  end;
begin
  myList := return_long;
  idx := 1;
  while idx <= LIST_LENGTH do
    begin
      Write(myList[idx]);
      idx := idx + 1
    end;
end.
