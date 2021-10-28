" vim syntax file for the s programming lang

if exists("b:current_syntax")
	finish
endif


syn match KWD '^\(+\|--\|-\)'
syn match KWD '\<\(out\|stdout\|input\|in\|flush\|clear\)\>'

syn match comment '#.*'
syn match Todo '#.*TODO.*'

syn match Number '\d\+'

syn match Function '!\w\+'

hi def link KWD				Keyword
hi def link Todo			Todo
hi def link Comment			Comment
hi def link Number			Constant
hi def link Function		Function
