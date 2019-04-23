grammar Pi;

program 	: (globalnames newlines)?
              definitions newlines?
              helpers newlines?
              limit newlines? EOF; // (mefinitions+=definition);

helpers     : (helper newlines)*;
helper      : procid EQ limit SEM;

globalnames	: GLOBAL (globalname)+ SEM; // (glnames+=names)
globalname  : NAME;

definitions : (definition newlines)*;
definition	: proccalldef DEF actions SEM;

limit		: nullprocess
//            | PAROP term PARCL add support for ( ) to guide view later
            | newnames PAROP parallels PARCL
            | parallels;

nullprocess : ZERO;
newnames    : NEWOP names DOT;
parallels   : comp (PARA comp)*;

comp        : msgout | processcall | iterproccall | PAROP limit PARCL | sublimit;

sublimit    : PAROP limit PARCL OMEGA; // introduce sanity check whether newnames is not empty for sublimit

iterproccall: processcall OMEGA;

proccalldef : procid (BRAOP listofvars BRACL)?;
processcall : procid (BRAOP listofargs BRACL)?;
procid      : PROCID | SECRET | LEAK;

actions     : action (CHOICEOP action)*; // add possibility for ( and )
action		: inputpattern DOT PAROP limit PARCL;

inputpattern: INOP (listofvars COL)? (pattern)? PARCL;

names		: newname (COMMA newname)*;
newname     : NAME;

listofargs	: arguments;
arguments   : argument (COMMA argument)*;
argument    : msg; // got rid of variable here due to basicmsg can see it.

listofvars	: variables;
variables   : (variable | sizedvar) (COMMA variables)*;
variable    : NAME;
sizedvar    : PAROP variable COL SIZE size PARCL;
size        : NUMBER;

msgout      : FROP msg FRCL;

msg         : pairmsg
            | encrymsg
            | aencrymsg
            | signmsg
            | pubkeymsg
            | basicmsg;
basicmsg    : NAME;
encrymsg    : ENCOP msg COMMA msg PARCL | CURLOP msg CURLCL UNDER msg;
aencrymsg   : AENCOP msg COMMA msg PARCL;
signmsg     : SIGNOP msg COMMA msg PARCL;
pubkeymsg   : PUBOP msg PARCL;
pairmsg     : PAROP msg COMMA msg PARCL;

pattern     : pairmsg
            | encrymsg
            | adecpattern
            | veripattern
            | pubkeymsg
            | basicmsg
            | variable;

adecpattern : ADECOP pattern COMMA pattern PARCL;
veripattern : VERIOP pattern COMMA pattern PARCL;

newlines    : NEWLINE (NEWLINE)*;

NAME		: {(self._input.LA(1) != 'global') & (self._input.LA(1) != 'size') &\
               (self._input.LA(1) != 'new') &\
               (self._input.LA(1) != 'aenc') & (self._input.LA(1) != 'sign') &\
               (self._input.LA(1) != 'pub') & (self._input.LA(1) != 'enc') &\
               (self._input.LA(1) != 'adec') & (self._input.LA(1) != 'veri')}?
              [a-z]+;
PROCID		: [A-Z] [0-9]?;
NUMBER      : [1-9] [0-9]*;

GLOBAL      : '#global';
DOUBLESLASH : '//';
SIZE        : 'size ';
NEWOP		: 'new ';
OMEGA       : '^w';
AENCOP      : 'aenc(';
SIGNOP      : 'sign(';
PUBOP       : 'pub(';
ENCOP       : 'enc(';
ADECOP      : 'adec(';
VERIOP      : 'veri(';
CURLOP      : '{';
CURLCL      : '}';
UNDER       : '_';
PAROP       : '(';
PARCL       : ')';
FROP        : '<';
FRCL        : '>';
PARA		: '||';
BRAOP       : '[';
BRACL       : ']';
COMMA       : ',';
ZERO        : 'STOP';
SECRET      : 'Secret';
LEAK        : 'Leak';
DOT         : '.';
SEM         : ';';
NEWLINE     : '\n';
COL         : ':';
CHOICEOP    : '+';
INOP        : 'in(';
DEF         : ':=';
EQ          : '=';
WS          : [ \t\r]+ -> skip;
COMMENTS    : '//' ~('\r' | '\n')+ -> skip;
