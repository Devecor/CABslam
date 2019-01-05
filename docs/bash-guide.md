# bash guide

## shell commonds

A simple shell command such as echo a b c consists of the command itself followed by arguments, separated by spaces.

If ‘|&’ is used, command1’s standard error, in addition to its standard output, is connected to command2’s standard input through the pipe; it is shorthand for 2>&1 |. This implicit redirection of the standard error to the standard output is performed after any redirections specified by the command.

A single quote may not occur between single quotes, even when preceded by a backslash.