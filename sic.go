package main
import (
	. "util"
	"strings"
	"os"
	"fmt"
	"strconv"
)

const (
	OP_FUNC = iota
	//OP_INCLUDE = iota
	OP_MINUS = iota
	OP_DMINUS = iota
)


type command struct {
	line int
	optype int
	value string
	addr string
	jt string
}

func main(	) {
	var argv = os.Args
	var argc int = len(argv)
	var flname = "program.sic"
	if (argc == 2){
		flname = argv[1]
	}

	var dofile []command = ParseFile(flname)
	for i := 0 ; i < len(dofile) ; i++ {
		//PrintCommand(dofile[i])
		//Print("\n")
	}
	RunFile(dofile)
	if (false) {
		strconv.Atoi("2")
	}
}

func PrintCommand( cmd command ) {
	var optp string = "no op"
	switch cmd.optype {
		case OP_MINUS:
			optp = "'-'"
		case OP_DMINUS:
			optp = "'--'"
		case OP_FUNC:
			optp = "func"
		//case OP_INCLUDE:
		//	optp = "include"
	}
	Printf("%s in '%s' w/ '%s' -> %s @ %d\n", optp, cmd.addr, cmd.value, cmd.jt, cmd.line)
}

func ParseFile( flname string ) []command {
	var file []string = strings.Split(ReadFile(flname), "\n")
	var dofile []command
	var line string
	var char string
	var cmd command
	var cmdtype int
	var lns []string
	/*
		- = op
		! = func
		# = comment
	*/
	for linei := 0 ; linei < len(file) ; linei++{
		line = ""
		if (len(file[linei]) > 4) {
			if (!(string(file[linei][0]) == "-" || string(file[linei][0]) == "!" || string(file[linei][0]) == "#")) {
				fmt.Printf("unknown char '%s'\n", string(file[linei][0]))
				fmt.Printf("in line \"%s\" @ %d\n", file[linei], linei+1)
				continue
			} else {
				for chari := 0 ; chari < len(file[linei]) ; chari++{
					char = string(file[linei][chari])
					if (char == "#") {
						break
					}
					line+=char
				}
				if (len(line) > 0) {
					// line, optype, value, addr, jump
					cmd = command{0, 0, "", "", ""} //TODO linei+1?
					switch string(line[0]){
						case "-":
							cmdtype = OP_MINUS
						case "!":
							cmdtype = OP_FUNC
						//case "@":
						//	cmdtype = OP_INCLUDE
					}
					cmd.optype = cmdtype
					if string(line[1]) == "-"{ cmd.optype = OP_DMINUS }
					cmd.line = linei+1
					lns = strings.Fields(line)
					if (cmd.optype == OP_FUNC) {
						JUMPS[lns[0]] = len(dofile)
					//} else if (cmd.optype == OP_INCLUDE) {
					//	cmd.addr = lns[0][1:len(lns[0])]
						//
					} else if (cmd.optype == OP_MINUS) {
						cmd.addr = lns[1]
						cmd.value = lns[0][1:len(lns[0])]
						//
					} else if (cmd.optype == OP_DMINUS) {
						cmd.addr = lns[1]
						cmd.value = lns[0][2:len(lns[0])]
						//
					}
					if (len(lns) == 3) {
						cmd.jt = lns[2]
					}
					dofile = append(dofile, cmd)
				}
			}
		}
	}
	return dofile
}

var VARS = map[string]int {
	"stdin":0,	// store input
	"status":0,	// exit status
	"endl":10,	// \n
	"Space":32, // ' '
}

var JUMPS = map[string]int { }

func get( name string ) int {
	var ret int
	var err error
	var nameerror bool
	ret, err = strconv.Atoi(name)
	if (err != nil) {
		ret, nameerror = VARS[name]
		if (nameerror) {
			//TODO panic
		}
	}
	return ret
}

func RunFile( dofile []command ) int { // ret exit num
	InitGetCh()
	for i:= 0 ; i < 26 ; i++ {
		VARS[string(i+65)] = i+65 // A -> Z
		VARS[string(i+97)] = i+97 // a -> z
	}
	var line command
	var value int
	var jump int
	var addr string
	for linei := 0 ; linei < len(dofile) ; linei++{
		line = dofile[linei]
		value = get(line.value)
		addr = line.addr
		switch addr{
			case "out":
				Sout.Write([]byte(string(value)))
			case "in":
				VARS["input"] = int(GetChByte())
			case "flush":
				Sout.Flush()
			case "debug":
				// TODO
			case "clear":
				// TODO
			default:
				switch line.optype{
					case OP_DMINUS:
						VARS[addr] += value
					case OP_MINUS:
						VARS[addr] -= value
				}
		}
		if (addr == "cond" || line.value == "input") {
			fmt.Println(VARS[addr])
		}
		if (VARS[addr] == 0 && line.jt != "" ) {
			jump = JUMPS[line.jt]
			fmt.Print(JUMPS)
			PrintCommand(line)
			PrintCommand(dofile[jump])
			linei = jump
		}
	}
	Sout.Flush()
	return VARS["status"]
}
/*
	line int
	optype int
	value string
	addr string
	jump int
*/
