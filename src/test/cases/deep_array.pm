program deep_array;
type myinta = array [1..10] of Integer;
     myarra = array [1..10] of myinta;
var x : myarra;
begin
x[1][1] := 65;
Write(x[1][1])
end.
