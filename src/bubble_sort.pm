import lib.writeint;
import lib.rand;

program bubblesort;
const MAX = 500;
type List = array [1..MAX] of Integer;
var x : List;
    i, tmp : Integer;
    changed : Boolean;
begin
  SeedRandom(1234);
  i := 1;
  {populate}
  while i < MAX do
    begin
      NextInt(x[i]);
      i := i + 1
    end;
  
  {sort}
  changed := True;
  while changed do
    begin
      changed := False;
      i := 1;
      while i < MAX do
        begin
          if x[i] > x[i + 1] then
            begin
              tmp := x[i];
              x[i] := x[i + 1];
              x[i + 1] := tmp;
              changed := True
            end;
          i := i + 1
        end;
    end;

  i := 1;
  while i < MAX do
    begin
      WriteInt(x[i]);
      Write(10); {\n}
      i := i + 1;
    end;
end.
