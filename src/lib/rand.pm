import lib.writeint;

program rand;
var lastNum : Integer;
    x, i : Integer;
procedure SeedRandom(seed : Integer);
  begin
    lastNum := seed
  end;
procedure NextInt(var n : Integer);
  const a = 1103515245;
        c = 12345;
        m = 2147483648;
  begin
    lastNum := (a * lastNum + c) mod m;
    n := lastNum
  end;
begin 
{
  SeedRandom(13);
  i := 0;
  while i < 100 do
    begin
      NextInt(x);
      WriteInt(x);
      Write(10);
      i := i + 1
    end;
}
end.
