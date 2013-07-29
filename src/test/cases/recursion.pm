program recursion;
procedure loop(x : Integer);
  begin
    Write(x);
    if x < 75 then
      loop(x + 1);
  end;
begin
  loop(65)
end.

