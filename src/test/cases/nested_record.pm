program nested_record;
type myintr = 
  record
     intone, inttwo : Integer
  end;
     myrecr =
  record
    rec1, rec2 : myintr
  end;
var x : myrecr;
begin
  x.rec1.intone := 65;
  x.rec1.inttwo := 66;
  x.rec2.intone := 67;
  x.rec2.inttwo := 68;
  Write(x.rec1.intone);
  Write(x.rec1.inttwo);
  Write(x.rec2.intone);
  Write(x.rec2.inttwo)
end.
   
