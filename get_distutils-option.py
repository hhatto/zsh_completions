"""This is got to Initial Version of Zsh Completion Function for setup.py.
"""
#from distutils import dist
from setuptools import dist, command
from jinja2 import Template


def _escape(strings):
    """escape to square-bracket and double-quorte."""
    ret = []
    for string in strings:
        if string == '[' or string == ']' or string == "\"":
            string = '\\' + string
        ret.append(string)
    return "".join(ret)

options = []
d = dist.Distribution()
for i in d._get_toplevel_options():
    options.append({'optstring': '--' + i[0],
                    'helpstring': _escape(i[2])})
    if i[1] != None:
        options.append({'optstring': '-' + i[1],
                        'helpstring': _escape(i[2])})
for i in d.display_options:
    options.append({'optstring': '--' + i[0],
                    'helpstring': _escape(i[2])})
    if i[1] != None:
        options.append({'optstring': '-' + i[1],
                        'helpstring': _escape(i[2])})

subcommands = []
subcommand_opts = {}

for subcommand in d.get_command_list():
    opt = subcommand[0]
    subcommands.append({'optstring': opt,
                        'helpstring': _escape(subcommand[1])})
    subcmdopts = d.get_command_obj(opt).user_options
    subcommand_opts[opt] = []
    for cmdopt in subcmdopts:
        subcommand_opts[opt].append({'optstring': '--' + cmdopt[0],
                                     'helpstring': _escape(cmdopt[2])})
        if cmdopt[1] != None:
            subcommand_opts[opt].append({'optstring': '-' + cmdopt[1],
                                         'helpstring': _escape(cmdopt[2])})

for opt in [i for i in command.__all__ if '__' not in i]:
    if opt in [j[0] for j in d.get_command_list()]:
        continue
    helpstring = d.get_command_obj(opt).description
    subcommands.append({'optstring': opt,
                        'helpstring': _escape(helpstring)})
    subcmdopts = d.get_command_obj(opt).user_options
    subcommand_opts[opt] = []
    for cmdopt in subcmdopts:
        subcommand_opts[opt].append({'optstring': '--' + cmdopt[0],
                                     'helpstring': _escape(cmdopt[2])})
        if cmdopt[1] != None:
            subcommand_opts[opt].append({'optstring': '-' + cmdopt[1],
                                         'helpstring': _escape(cmdopt[2])})

template = \
"""#compdef setup.py

typeset -A opt_args
local context state line

_setuppy() {
  _arguments -s -S \\
    {% for item in options -%}
    "{{item['optstring']}}[{{item['helpstring']}}]" \\
    {% endfor -%}
    "*::setup.py commands:_setuppy_command"
}

(( $+functions[_setuppy_command] )) ||
_setuppy_command() {
  local cmd ret=1

  (( $+setuppy_cmds )) || _setuppy_cmds=(
    {% for item in subcommands -%}
    "{{item['optstring']}}:{{item['helpstring']}}" \\
    {% endfor -%}
  )

  if (( CURRENT == 1 )); then
    _describe -t commands 'setup.py subcommand' _setuppy_cmds || compadd "$@" - ${(s.:.)${(j.:.)_setuppy_syns}}
  else
    local curcontext="$curcontext"

    cmd="${${_setuppy_cmds[(r)$words[1]:*]%%:*}:-${(k)_setuppy_syns[(r)(*:|)$words[1](:*|)]}}"
    if (( $#cmd )); then
      curcontext="${curcontext%:*:*}:setuppy-${cmd}:"
      _call_function ret _setuppy_$cmd || _message 'no more arguments'
    else
      _message "unknown setup.py command: $words[1]"
      fi
    return ret
  fi
}

{% for subcommand in subcommands -%}
(( $+functions[_setuppy_{{subcommand['optstring']}}] )) ||
_setuppy_{{subcommand['optstring']}}() {
  _arguments -s \\
    {% for subcommand_opt in subcommand_opts[subcommand['optstring']] -%}
    "{{subcommand_opt['optstring']}}[{{subcommand_opt['helpstring']}}]" \\
    {% endfor -%}
    "*::setup.py commands:_setuppy"
}

{% endfor -%}

_setuppy "$@"
"""
t = Template(template)
print t.render(options=options,
               subcommands=subcommands,
               subcommand_opts=subcommand_opts)
