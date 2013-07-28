program longassign;
type mya = array[1..10] of Integer;
var x, y: mya; i : Integer;
begin
  x[1] := 65;
  x[2] := 66;
  x[3] := 67;
  x[4] := 68;
  x[5] := 69;
  x[6] := 70;
  x[7] := 71;
  x[8] := 72;
  x[9] := 73; 
  x[10] := 74;

  y := x;

  i := 1;
  while i <= 10 do
    begin 
      Write(y[i]);
      i := i + 1;
    end;
end.
