package main

import (
	. "util"
	"strings"
	"os"
	"fmt"
)

type commmand struct {
	line int
	cmd string
	value int
	jump int
}

func Main(argv []string) int {
	var argc int = len(argv)
	var flname = "program.sic"
	if (argc == 2){
		flname = argv[1]
	}

	var VARS = map[string]int{
		"stdout":0,	// trigger write
		"input":0,	// trigger read input
		"stdin":0,	// store input
		"status":0,	// exit status
		"debug":0,	// trigger debug
		"clear":0,	// trigger clear screen
		"endl":10,	// \n
	}
	for i:= 0 ; i < 26 ; i++ {
		VARS[string(i+65)] = i+65
		VARS[string(i+97)] = i+97
	}
	var file []string = strings.Split(ReadFile(flname), "\n")
	var dofile []string
	var line string
	var char string
	for linei := 0 ; linei < len(file) ; linei++{
		line = ""
		if len(file[linei]) > 0{
			if !(string(file[linei][0]) == "-" || string(file[linei][0]) == "!") {
				Print(fmt.Sprintf("unknown char '%s'", string(file[linei][0])))
			}
		}
		for chari := 0 ; chari < len(file[linei]) ; chari++{
			char = string(file[linei][chari])
			if char == "#"{break}
			line+=char
		}
		dofile = append(dofile, line)
	}
	Print(dofile)
	return 0
}

func main(){
	var ecode int = Main(os.Args)
	os.Exit(ecode)
}
