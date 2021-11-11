" vim syntax file for the s programming lang

if exists("b:current_syntax")
	finish
endif

" op
syn match string '^\(--\|-\)'

" triggers
syn match KWD '\<\(out\|stdout\|input\|in\|flush\|clear\)\>'

" comment
syn match comment '#.*'

" TODO comment
syn region Todo start='TODO' end=''  contained
syn match comment '#.*' nextgroup=Todo contains=Todo

" num
syn match Number '\d\+'

" function
syn match Function '!\w\+'

hi def link KWD				Keyword
hi def link Todo			Todo
hi def link String			Constant
hi def link Comment			Comment
hi def link Number			Constant
hi def link Function		Function
