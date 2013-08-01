program writeint;
procedure Abs(var num : Integer);
  begin
    if num < 0 then
      num := -num;
  end;

procedure WriteInt(num : Integer);
  procedure WritePos(posNum : Integer);
    var beginning, lastDigit : Integer;
    begin
      lastDigit := posNum mod 10;
      beginning := posNum div 10;
      if beginning <> 0 then
        WritePos(beginning);
      if lastDigit = 0 then
        Write(48)
      else if lastDigit = 1 then
        Write(49)
      else if lastDigit = 2 then
        Write(50)
      else if lastDigit = 3 then
        Write(51)
      else if lastDigit = 4 then
        Write(52)
      else if lastDigit = 5 then
        Write(53)
      else if lastDigit = 6 then
        Write(54)
      else if lastDigit = 7 then
        Write(55)
      else if lastDigit = 8 then
        Write(56)
      else if lastDigit = 9 then
        Write(57);
    end;
  begin
    if num < 0 then
      Write(45); {'-'}
    Abs(num);
    WritePos(num)
  end;
begin
end.
