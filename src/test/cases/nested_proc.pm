program nestedproc;
procedure w;
  var x : Integer;
  procedure inside;
    begin
      Write(x)
    end;
  begin
    x := 65;
    inside
  end;
begin
  w
end.
