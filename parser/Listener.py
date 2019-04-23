from PiListener import PiListener
from Message import *
from ProcessCall import *
from Limit import *
from Process import *
from Definition import *
from Action import *
from Variable import *
from InputPrefix import *
from InputPatterns import *
from NameRepr import *
from collections import defaultdict


class Listener(PiListener):
    def __init__(self):
        self.state = []
        self.globals = []
        self.definitions = []
        self.helpers = defaultdict(lambda: None, {})
        self.limit = None
        self.variables_pattern = set()
        self.variables_pcdef = set()

    def exitProgram(self, ctx):
        self.limit = self.state.pop()[1]
        set_globals = set(self.globals)
        limit_globals = self.limit.get_globalnames()
        if set_globals != limit_globals:
            # print (limit_globals - set_globals)
            raise Exception('Given and actual globalnames do not match in instantiation')
        for d in self.definitions:
            def_globals = d.get_globalnames()
            if not def_globals <= set_globals:
                # diff = def_globals - set_globals
                # for d in diff:
                #     print d
                raise Exception('Unlisted global name in definition')

    def exitGlobalname(self, ctx):
        self.globals.append(NameRepr(ctx.getText()))

    def exitHelper(self, ctx):
        limit = self.state.pop()[1]
        id = self.state.pop()
        if self.helpers[id] is None:
            self.helpers[id] = limit
        else:
            raise Exception('Second Helper defined')

    # Definitions

    def enterDefinitions(self, ctx):
        self.state.append(StackMarker.DEFINITIONS)

    def exitDefinition(self, ctx):
        actions = self.state.pop()
        proccall = self.state.pop()[1]
        definition = Definition(proccall, actions)
        self.state.append(definition)
        self.variables_pcdef = set()

    def exitDefinitions(self, ctx):
        definitions = []
        temp = self.state.pop()
        while temp != StackMarker.DEFINITIONS:
            definitions.append(temp)
            temp = self.state.pop()
        self.definitions = definitions

    # Actions (& inputpattern)

    def enterActions(self, ctx):
        self.state.append(StackMarker.ACTIONS)

    def exitActions(self, ctx):
        actions = []
        temp = self.state.pop()
        while temp != StackMarker.ACTIONS:
            actions.append(temp)
            temp = self.state.pop()
        self.state.append(actions)

    def exitAction(self, ctx):
        self.variables_pattern = set()
        limit = self.state.pop()[1]
        if not limit.is_proc():
            raise Exception('Attempt to have a definition with a limit instead of a process')
        inputprefix = self.state.pop()
        self.state.append(Action(inputprefix, limit))

    def exitInputpattern(self, ctx):
        if len(ctx.children) == 4:
            raise Exception('Cannot have an inputprefix without message but with list of variables')
        elif len(ctx.children) == 5:
            msg = self.state.pop()
            names = self.state.pop()
            self.state.append(InputPrefix(set(names), msg))
        elif len(ctx.children) == 3:
            msg = self.state.pop()
            self.state.append(InputPrefix(set(), msg))
        elif len(ctx.children) == 2:
            self.state.append(InputPrefix(None, None))

    # Messages

    def exitPairmsg(self, ctx):
        second = self.state.pop()
        first = self.state.pop()
        self.state.append(PairMsg(first, second))

    def exitEncrymsg(self, ctx):
        key = self.state.pop()
        msg = self.state.pop()
        self.state.append(EncMsg(msg, key))

    def exitAencrymsg(self, ctx):
        key = self.state.pop()
        msg = self.state.pop()
        self.state.append(AEncMsg(msg, key))

    def exitSignmsg(self, ctx):
        key = self.state.pop()
        msg = self.state.pop()
        self.state.append(SignMsg(msg, key))

    def exitPubkeymsg(self, ctx):
        msg = self.state.pop()
        self.state.append(PublicKeyMsg(msg))

    def exitBasicmsg(self, ctx):
        if Variable(ctx.getText()) in self.variables_pattern | self.variables_pcdef:
            self.state.append(Variable(ctx.getText()))
        else:
            self.state.append(BasicMsg(NameRepr(ctx.getText())))

    # Components of processes/limits

    def enterParallels(self, ctx):
        self.state.append(StackMarker.PARALLELS)

    def exitParallels(self, ctx):
        comps = []
        temp = self.state.pop()
        while temp != StackMarker.PARALLELS:
            comps.append(temp)
            temp = self.state.pop()
        self.state.append(comps)

    def exitMsgout(self, ctx):
        msg = self.state.pop()
        self.state.append((KindComps.MSG, msg))

    def exitProcid(self, ctx):
        self.state.append(ctx.getText())

    def exitProcesscall(self, ctx):
        listofargs = []
        if len(ctx.children) == 4:
            listofargs.extend(self.state.pop())
        procid = self.state.pop()
        if self.helpers[procid] is not None:
            # Assumption: no helper name and process call definition name is shared
            limit = self.helpers[procid]
            if limit.newnames:
                self.state.append((KindComps.SUBPROC, limit))
            else:
                # Expand
                for m in limit.messages:
                    self.state.append((KindComps.MSG, m))
                for p in limit.processcalls:
                    self.state.append((KindComps.PRCCLL, p))
                for s in limit.subprocesses:
                    self.state.append((KindComps.SUBPROC, s))
                for i in limit.iterproccalls:
                    self.state.append((KindComps.ITPRCCLL, i))
                for s in limit.sublimits:
                    self.state.append((KindComps.SUBLIM, s))
        else:
            if len(listofargs) == 1:
                self.state.append((KindComps.PRCCLL, ProcessCall(procid, listofargs[0])))
            else:
                listofargs.reverse()
                self.state.append((KindComps.PRCCLL, ProcessCall(procid, tuple(listofargs))))

    def exitProccalldef(self, ctx):
        listofargs = []
        if len(ctx.children) == 4:
            listofargs.extend(self.state.pop())
        procid = self.state.pop()
        if len(listofargs) == 1:
            self.state.append((KindComps.PRCCLL, ProcessCall(procid, listofargs[0])))
            self.variables_pcdef = set([listofargs[0]])
        else:
            listofargs.reverse()
            self.state.append((KindComps.PRCCLL, ProcessCall(procid, tuple(listofargs))))
            self.variables_pcdef = set(listofargs)

    def exitIterproccall(self, ctx):
        kind, iterated = self.state.pop()
        if kind == KindComps.PRCCLL:
            self.state.append((KindComps.ITPRCCLL, iterated))
        elif kind == KindComps.SUBPROC:
            self.state.append((KindComps.SUBLIM, iterated))

    def exitSublimit(self, ctx):
        self.state.append((KindComps.SUBLIM, self.state.pop()[1]))  # term

    def enterNames(self, ctx):
        self.state.append(StackMarker.NAMES)

    def exitNames(self, ctx):
        temp = self.state.pop()
        names = []
        while temp != StackMarker.NAMES:
            names.append(temp)
            temp = self.state.pop()
        self.state.append(names)

    def exitNewname(self, ctx):
        self.state.append(NameRepr(ctx.getText()))

    def enterListofvars(self, ctx):
        self.state.append(StackMarker.VARIABLES)

    def exitListofvars(self, ctx):
        temp = self.state.pop()
        variables = []
        while temp != StackMarker.VARIABLES:
            variables.append(temp)
            temp = self.state.pop()
        self.variables_pattern = set(variables)
        self.state.append(variables)

    def exitVariable(self, ctx):
        self.state.append(Variable(ctx.getText()))

    def exitSizedvar(self, ctx):
        size = self.state.pop()
        var = self.state.pop()
        self.state.append(Variable(var.name, size))

    def exitSize(self, ctx):
        self.state.append(int(ctx.getText()))

    def enterListofargs(self, ctx):
        self.state.append(StackMarker.ARGUMENTS)

    def exitListofargs(self, ctx):
        temp = self.state.pop()
        arguments = []
        while temp != StackMarker.ARGUMENTS:
            arguments.append(temp)
            temp = self.state.pop()
        self.state.append(arguments)

    def exitLimit(self, ctx):
        components = self.state.pop()
        if isinstance(components, list):
            NameReprs = []
            if len(ctx.children) == 4:
                NameReprs.extend(self.state.pop())
            msgs, pcs, procs, ipcs, sls = Listener.splitcomponents(components)
            self.state.append((KindComps.SUBPROC, Limit(set(NameReprs), msgs, pcs, procs, ipcs, sls)))
        else:
            self.state.append(components)

    def exitNullprocess(self, ctx):
        self.state.append((KindComps.SUBPROC, StopProcess()))

    @staticmethod
    def splitcomponents(components):
        msgs, pcs, ipcs, procs, sls = [], [], [], [], []
        for (k, c) in components:
            if k == KindComps.MSG:
                msgs.append(c)
            elif k == KindComps.PRCCLL:
                pcs.append(c)
            elif k == KindComps.ITPRCCLL:
                ipcs.append(c)
            elif k == KindComps.SUBPROC:
                procs.append(c)
            elif k == KindComps.SUBLIM:
                sls.append(c)
        return msgs, pcs, procs, ipcs, sls


class KindComps(Enum):
    MSG = 1
    PRCCLL  = 2
    ITPRCCLL = 3
    SUBPROC = 4
    SUBLIM = 5


# One might wonder why we use characters here: because names are numbers and cause conflicts in the stack
class StackMarker(Enum):
    DEFINITIONS = 'd'
    ACTIONS = 'a'
    NAMES = 'n'
    PARALLELS = 'p'
    VARIABLES = 'v'
    ARGUMENTS = 'ar'
    INPUT = 'i'
    TAU = 't'
