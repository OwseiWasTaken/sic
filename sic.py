#! /usr/bin/python3.10
#imports
from util import *

if OS == "windows": # no color support
	COLOR = {
		"nc":"",
		"red":"",
		"BrOrange":"",
		"DarkBlue":"",
		"green":""
	}
else:
	import util
	COLOR = util.COLOR

errors = {
	2 : "value name error",
	2 : "variable nameing error",
	3 : "debug quit",
	4 : "missing filename error",
	5 : "missing file error",
}

options = """
options in order
--TKN overwrites --ST as false
(if running a .sict file, only --debug will work)

--OLJ (only set this if all jumps are to labels!) if set, all lines that don't execute commands will be removed
--TKN if set, print tokens and exit
--ST if set, export tokens to {program name}.sict (sict is Single Instruction CPU Tokens)
--debug if set,the program will tell how much time was needed to tokenize and run the program
"""

# token class, all lines will become a token and the be run by program.run
class token:
	def __init__(this,type,value,addr,jump):
		this.type = type
		this.value = value
		this.addr = addr
		this.jump = jump
	def __repr__(this): # only to write the token to the screen
		if this.type == "COMMENT":
			return this.value
		elif this.type == "LABEL":
			return f"label !{this.addr}"
		return f"{this.addr} {'+' if this.type == 'PLUS' else '-'}= {this.value} {'goto '+this.jump if this.jump != None else ''}"


# main class
class program:
	# start class
	def __init__(this):
		if get('-bdb').exists:
			this.SmallDebug = false
		else:
			this.SmallDebug = true
		if get('-i', None).list:
			file = get("-i", None).first
			if not exists(file):
				print(errors[5])
				exit(5)

			# remove .sic from filename
			this.ProgramName = file.split('.')[0]

			# check if needs to tokenize
			if file.endswith('.sic'):
				with open(file,'r') as fl:
					content = fl.readlines()
				this.file = this.MakeUsableFile(content)

			# else, loadtokens (pickled file)
			elif file.endswith('.sict'):
				this.file = UseFile(file)[0]
				this.labels = UseFile(file)[1]
		else:
			# if no input was set
			print(errors[4])
			exit(4)

		# set program.ExitCode to the result of running the .sic
		this.ExitCode=this.run()

	def run(this):
		# check if --store-tokens is set
		if get("--ST").exists:
			# make pickled file
			UseFile(f"{this.ProgramName}.sict", (this.file,this.labels))
			return 0
			#
			with open(f"{this.ProgramName}.sict",'w') as file:
				ret = []
				for tkn in this.file:
					ret.append((tkn.type,tkn.value,tkn.addr,tkn.jump))
				file.write(str(ret)+'\n')
				file.write(str(this.labels))

			return 0

		VARS = {
			"stdin":0,
			"status":0,
			"endl":10,
			"Space":32,
		}
		for i in range(0, 26):
			VARS[chr(i+65)] = i+65
			VARS[chr(i+97)] = i+97

		dbg = get('--debug').exists

		LineNumber = 0
		if type(this.file) == int:
			return this.file
		while LineNumber < len(this.file):
			line = this.file[LineNumber]

			TYPE = line.type
			if TYPE in ["COMMENT","LABEL"]: # make runOLJ / run
				LineNumber+=1
				continue

			VALUE = line.value
			ADDR = line.addr.replace("out","stdout").replace("in","input")# shortcuts for triggers

			JUMP = line.jump

			if VALUE[0] in "0123456789-+":
				# if value is a number
				VALUE = eval(VALUE)
			else:
				# if value is var
				try:
					VALUE = VARS[VALUE]
				except KeyError:
					print(f"\n\
run time error\n\
{COLOR.red}VALUE NAME ERROR{COLOR.nc}\n\
No variable has been named \"{VALUE}\"")
					return 1

			if TYPE == "MINUS":
				VARS[ADDR] = VARS.get(ADDR,0)-VALUE
			else:
				VARS[ADDR] = VARS.get(ADDR,0)+VALUE

			if VARS[ADDR] == 0 and JUMP != None:

				if JUMP[0] == '!':
					JUMP = this.labels[JUMP[1:]] # jump to label

				elif JUMP.isnumeric():
					JUMP = eval(JUMP) # jump to line
				else:
					JUMP = VARS[JUMP] # jump to var
				LineNumber = JUMP-2# -2 cus - the jmp one and minus this loop's ++

			match ADDR:
				case "stdout":
					printl(chr(int(VARS["stdout"])))
					VARS["stdout"] = 0

				case "clear":
					clear()

				case "input":
					ch = GetCh()
					if dbg and ch == "\x03":break
					VARS["stdin"] = ord(ch)

				case "debug":
					alp = 0
					ret = {}
					for key in VARS.keys():
						if not key in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" or not this.SmallDebug:
							if key in [ "in", "stdout", "clear", "debug" ]:continue
							var = str(VARS[key])
							try:
								if chr(VARS[key]).isprintable():
									ch = repr(chr(VARS[key]))
								else:
									ch = "!!!"
							except ValueError:
								ch = "!!!"
							ret[key] = (var, ch)
						if key in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
							alp += 1
					if alp == 26:
						print("[A, B, C ...] -> [65, 66, 67 ...]")
					else:
						for key in VARS.keys():
							if key in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
								if key in [ "in", "stdout", "clear", "debug" ]:continue
								var = str(VARS[key])
								try:
									if chr(VARS[key]).isprintable():
										ch = repr(chr(VARS[key]))
									else:
										ch = "!!!"
								except ValueError:
									ch = "!!!"
								ret[key] = (var, ch)
					keytab = BiggestLen([ k for k in ret.keys()])
					vartab = BiggestLen([ ret[k][0] for k in ret.keys()])
					chtab = BiggestLen([ ret[k][1] for k in ret.keys()])
					toprt = ""
					for key in ret.keys():
						var = ret[key][0]
						ch = ret[key][1]
						toprt += f"\
	{key}{' '*(keytab-len(key)+1)}\
	{var}{' '*(vartab-len(var)+1)}\
	{ch }{' '*(chtab -len(ch )+1)}\n"
					print(toprt)
					print(f"\nl:{LineNumber}")
					print(f"jumps:{this.labels}")
					if GetCh() == 'q':
						return 3
					#end debug
			#finish loop
			LineNumber+=1
		# end func
		return VARS["status"]





	def MakeUsableFile(this,file:list[str]) -> list[str]:
		ret = []
		this.labels = {}
		OLJ = get("--OLJ").exists
		for LineNumber in r(file):
			line = file[LineNumber]
			# line+=' '
			if line and line[0] in "+-":
				line = list( TrimSpaces(line.replace('\t',' ').strip()))
				if line[0:2] == ['-', '-']:
					line[1] = '+'
					line = line[1:]
					#print(line)
				pline = ''.join(line)

				# get type
				if line.pop(0) == '+':
					_type = "PLUS"
				else:
					_type = "MINUS"

				# get value
				ns = ''.join(line).find(' ') # next stop
				_value = ''.join(line[0:ns])
				line = line[ns+1:]

				_jmp = 0
				# get addr
				ns = ''.join(line).find(' ') # next stop
				if ns == -1: #no jump
					_jmp = None
					_addr = ''.join(line)
				else:
					_addr = ''.join(line[:ns])
					line = line[ns+1:]

				if _addr.isnumeric():
					print(f"comp time error\n\
{COLOR.red}VARIABLE NAMEING ERROR{COLOR.nc}\n\
No variables can be named numbers! line:{LineNumber}, addres missnamed \"{_addr}\"")
					return 2

				#get jump
				if _jmp == 0:
					_jmp = ''.join(line)

				ret.append(token(_type,_value,_addr,_jmp))
				# debug lines
				dbline = f"\
{COLOR.DarkBlue}{LineNumber}{COLOR.nc} \
{pline} {COLOR.BrOrange} ->\
{COLOR.nc} tp:{_type}, vl:{_value}, addr:{_addr} , jmp:{_jmp}"
				# print(dbline)

			elif line[0] == '!':
				if not OLJ:
					this.labels[line[1:].strip()] = LineNumber+2
				ret.append(token("LABEL",None,line[1:].strip(),None))
			else:
				ret.append(token("COMMENT",'"'+line.strip()+'"',None,None))

		# file has no line jumps -> remove comment lines
		if OLJ:
			# tkni = 0
			# while tkni < len(ret):

			newret = []
			for tkn in ret:
				if not tkn.type == "COMMENT":
					newret.append(tkn)
			ret=newret

			labels = 0
			for tkni in r(ret):
				if ret[tkni].type == "LABEL":
					this.labels[ret[tkni].addr] = tkni+(1-labels)
					# +(1-labels) is the labels existence in the list beeing removed
					labels+=1
			newret = []
			for tkn in ret:
				if not tkn.type == "LABEL":
					newret.append(tkn)
			ret=newret
		else:
			for labeli in this.labels.keys():
				this.labels[labeli] = this.labels[labeli]-1

		if get("--TKN").exists:
			for tkni in r(ret):
				print(f"{COLOR.DarkBlue}{tkni+1}{COLOR.nc}: {ret[tkni]}")

			print(this.labels)
			exit(0)

		return ret

# (normal code) file.sic
# (token) file.sict
#start
if __name__ == '__main__':
	start = tm()
	ExitCode = program().ExitCode

	if get('--debug').exists:
		if not ExitCode:
			printl("%scode successfully exited in " % COLOR.green)
		else:
			printl("%scode exited with error %d in " % (COLOR.red,ExitCode))
		print("%.3f seconds%s" % (tm()-start,COLOR.nc))
	exit(ExitCode)
