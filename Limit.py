from copy import deepcopy
from KnowledgeHandler import reduce_knowledge
from IdentifierManager import *
from collections import defaultdict


class Limit:
    def __init__(self, newnames, messages, processcalls, subprocesses, iterproccalls, sublimits):
        self.newnames = newnames
        self.processcalls = processcalls
        self.messages = messages
        self.iterproccalls = iterproccalls
        for s in sublimits + subprocesses:
            if s.get_nested_boundnames().intersection(newnames):
                raise Exception("Name clash")
        self.subprocesses = subprocesses
        self.sublimits = sublimits

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __str__(self):
        repnames = ", ".join(str(x) for x in self.newnames)
        repsingles = []
        for m in self.messages:
            repsingles.append('<' + str(m) + '>')
        repsingles.extend(self.processcalls)
        for s in self.subprocesses:
            repsingles.append(str(s))
        for i in self.iterproccalls:
            repsingles.append(str(i) + '^w')
        for l in self.sublimits:
            repsingles.append('(' + str(l) + ')^w')
        repall = " || ". join(str(x) for x in repsingles)
        start = "new " + repnames + "." if self.newnames else ""
        return start + "( " + repall + " )"

    def str_tex(self):
        repnames = ", ".join(x.str_tex() for x in self.newnames)
        repsingles = []
        for m in self.messages:
            repsingles.append('\\out{' + m.str_tex() + '}')
        repsingles.extend(map(lambda x: x.str_tex(), self.processcalls))
        for s in self.subprocesses:
            repsingles.append(s.str_tex())
        for i in self.iterproccalls:
            repsingles.append(i.str_tex() + '^w')
        for l in self.sublimits:
            repsingles.append('(' + l.str_tex() + ')^w')
        repall = " \\parallel ". join(x for x in repsingles)
        start = "\\new " + repnames + "." if self.newnames else ""
        return start + "( " + repall + " )"

    def __copy__(self):
        return deepcopy(self)

    # empty in the sense of actually being a stop process
    def is_empty(self):
        for v in self.__dict__.itervalues():
            if len(v) != 0:
                return False
        return True

    def get_nested_boundnames(self):
        nested_boundnames = set()
        for s in self.subprocesses + self.sublimits:
            nested_boundnames.update(s.get_all_boundnames())
        return nested_boundnames

    def get_all_boundnames(self):
        return self.get_nested_boundnames() | self.newnames

    def get_globalnames(self):
        used_names = set()
        for m in self.messages:
            used_names.update(m.get_names())
        for p in self.processcalls + self.iterproccalls:
            used_names.update(p.get_names())
        global_names = used_names.difference(self.newnames)
        for s in self.subprocesses + self.sublimits:
            for n in s.get_globalnames():
                if n not in self.newnames:
                    global_names.add(n)
        return global_names

    def get_variables(self):
        used_variables = set()
        for m in self.messages:
            used_variables.update(m.get_variables())
        for p in self.processcalls + self.iterproccalls:
            used_variables.update(p.get_variables())
        return used_variables

    def reduce_knowledge(self):
        reduce_knowledge(self.messages)

    @staticmethod
    def get_fresh_names(allnames, names_sub, amount):
        maxallnames = max(allnames) if allnames else 0
        maxnamessub = max(names_sub) if names_sub else 0
        maxname = max(maxallnames, maxnamessub)
        result = range(maxname + 1, maxname + 1 + amount, 1)
        return result

    def rename_to_fresh(self, to_be_renamed, freshnames, name_repr_man):
        substitution = dict(zip(to_be_renamed, freshnames))
        if name_repr_man:
            for (k, v) in substitution.iteritems():
                name_repr_man.add_connection(k, v)
        return self.rename(substitution)

    def rename(self, theta):
        messages = map(lambda m: m.rename(theta), self.messages)
        proccalls = map(lambda pc: pc.rename(theta), self.processcalls)
        subprocesses = map(lambda sp: sp.rename(theta), self.subprocesses)
        iterproccalls = map(lambda ipc: ipc.rename(theta), self.iterproccalls)
        sublimits = map(lambda sl: sl.rename(theta), self.sublimits)
        # names = map(lambda n: n if theta[n] is None else theta[n], self.newnames) does not work due to KeyError
        names = Limit.rename_set_with_dict(self.newnames, theta)
        return Limit(names, messages, proccalls, subprocesses, iterproccalls, sublimits)

    def rename_name_repr(self, repr_man):
        theta = repr_man.get_substitution_for_set(self.newnames)
        newnames = Limit.rename_set_with_dict(self.newnames, theta)
        messages = map(lambda m: m.rename(theta), self.messages)
        proccalls = map(lambda pc: pc.rename(theta), self.processcalls)
        iterproccalls = map(lambda ipc: ipc.rename(theta), self.iterproccalls)
        subprocesses = map(lambda sp: sp.rename(theta), self.subprocesses)
        sublimits = map(lambda sl: sl.rename(theta), self.sublimits)
        new_subprocs = []
        for sp in subprocesses:
            new_sp = sp.rename_name_repr(repr_man)
            new_subprocs.append(new_sp)
        new_sublimits = []
        for sl in sublimits:
            new_sl = sl.rename_name_repr(repr_man)
            new_sublimits.append(new_sl)
        return Limit(newnames, messages, proccalls, new_subprocs, iterproccalls, new_sublimits)

    @staticmethod
    def rename_set_with_dict(newnames, theta):
        names = set(newnames)
        for k, v in theta.items():
            if k in names:
                names.remove(k)
                names.add(v)
        return names

    def normalise(self, name_repr_man=None):
        if name_repr_man is not None:
            pass
        if len(self.subprocesses) != 0:
            for i in reversed(range(len(self.subprocesses))):
                self.subprocesses[i].normalise(name_repr_man)
                s = self.subprocesses.pop()
                allboundnames = self.get_all_boundnames()
                globalnames = self.get_globalnames()
                allnames = allboundnames | globalnames
                to_be_renamed = s.newnames.intersection(allnames)
                names_to_stay = s.newnames.difference(allnames)
                names_in_s = names_to_stay | s.get_globalnames()
                if len(to_be_renamed) == 0:
                    renamed_s = s
                elif name_repr_man is None:
                    fresh_names = Limit.get_fresh_names(allnames, names_in_s, len(to_be_renamed))
                    renamed_s = s.rename_to_fresh(to_be_renamed, fresh_names, name_repr_man)
                else:
                    substitution = name_repr_man.get_substitution_for_set(to_be_renamed)
                    renamed_s = s.rename(substitution)
                self.newnames.update(names_to_stay)
                self.newnames.update(renamed_s.newnames)
                self.messages.extend(renamed_s.messages)
                self.processcalls.extend(renamed_s.processcalls)
                self.sublimits.extend(renamed_s.sublimits)
                renamed_s.sublimits = []
                self.iterproccalls.extend(renamed_s.iterproccalls)
                renamed_s.iterproccalls = []

    def extend_for_inclusion_check(self, fixed1):
        n = max(len(fixed1.newnames), len(fixed1.processcalls))  # + 1
        self.extend(n) # when this is used, rather substitute by 2 (and increase iteratively)

    # extend (currently) changes limit
    def extend(self, factor):
        for i in self.iterproccalls:
            # no deep copy currently but ok as pc's never change
            self.processcalls.extend([i] * factor)
        for s in self.subprocesses:
            s.extend(factor)
        for s in self.sublimits:
            ex_s = deepcopy(s)
            ex_s.extend(factor)
            for f in range(factor):
                self.subprocesses.append(deepcopy(ex_s))

    # expand returns expanded limit
    def expand(self, factor):
        self.extend(factor)
        return self.get_fixedpart()

    def get_fixedpart(self):
        fixed_subprocesses = []
        for s in self.subprocesses:
            fixed_subprocesses.append(s.get_fixedpart())
        return Limit(self.newnames, self.messages, self.processcalls, fixed_subprocesses, [], [])

    def is_proc(self):
        if self.iterproccalls != []:
            return False
        if self.sublimits != []:
            return False
        for s in self.subprocesses:
            if not s.is_proc():
                return False
        return True

    def substitute_variables(self, substitutions):
        messages = [m.substitute_variables(substitutions) for m in self.messages]
        processcalls = [p.substitute_variables(substitutions) for p in self.processcalls]
        subprocesses = [s.substitute_variables(substitutions) for s in self.subprocesses]
        iterproccalls = [i.substitute_variables(substitutions) for i in self.iterproccalls]
        sublimits = [s.substitute_variables(substitutions) for s in self.sublimits]
        return Limit(deepcopy(self.newnames), messages, processcalls, subprocesses, iterproccalls, sublimits)

    # Obsolete, only used in partially automatic
    def compute_postprocs(self, definitions):
        assert self.is_proc()
        pc_next = []
        for pc in self.processcalls:
            for a in pc.get_substituted_actions():
                if a.is_prefixtau():
                    # Actually check whether any message is around (but intruder names are also there)
                    pc_next.append((pc, a.continuation))
                else:
                    posts = a.possible_steps_knowledge(self.messages)
                    pc_next.extend([(pc, p) for p in posts])
        return pc_next

    def get_pretty_error_list_of_posts(self, name_repr_man):
        name_repr_man_e_dict, lists_of_errors = self.get_error_list_of_posts(name_repr_man)
        list_of_pretty_errors = []
        for e in lists_of_errors.iterkeys():
            name_repr_man_e = name_repr_man_e_dict[e]
            list_of_pretty_errors_e = [name_repr_man_e.translate_error_back(x) for x in lists_of_errors[e]]
            list_of_pretty_errors.extend(list_of_pretty_errors_e)
        return list_of_pretty_errors

    def get_error_list_of_posts(self, name_repr_man):
        self.normalise(name_repr_man)
        self.reduce_knowledge()
        assert not self.subprocesses
        id_man = IdentifierManager()
        # First, give list of identifiers to every process call in the limit
        # self.mark_all_actions_in_pcs_with_ids(id_man)
        self.mark_all_pcs_with_ids(id_man)
        # Second, extend it by 1
        extend1 = deepcopy(self)
        name_repr_man_1 = deepcopy(name_repr_man)
        extend1.extend(1)
        extend1.normalise(name_repr_man_1)
        extend1.reduce_knowledge()
        # Third,
        # For every processcall:
        #   For every action in this list of the processcall:
        #       Annotate the input pattern with Eligible, Constr and Bottom
        #       Compute the set of variables (with sizes) to be filled
        #       From them, compute the extension factor and add it to a set
        # Outcome: A dict such that every identifier of a an action has
        #          (i, e, a) with unique identifier, extension factor and annotation
        #          one sets of identifiers for every extension factor (in order not to double-check same pc-action)
        #          one set of extension factors E
        dict_id_factor_annotation = extend1.check_inputpatterns_and_get_annotations(id_man.all_ids())
        # Collect the different ids for every extension factor
        ext_ids = defaultdict(lambda: set(), {})
        for (i, l) in dict_id_factor_annotation.iteritems():
            for (e, _) in l:
                ext_ids[e].add(i)
        list_of_errors = dict()
        name_repr_man_e_dict = dict()
        for e in ext_ids.iterkeys():
            list_of_errors_e = []
            extended = deepcopy(self)
            name_repr_man_e = deepcopy(name_repr_man)
            extended.extend(e)
            extended.normalise(name_repr_man_e)
            name_repr_man_e.finish_renaming()
            name_repr_man_e_dict[e] = name_repr_man_e
            extended.reduce_knowledge()
            allnames = extended.get_globalnames() | extended.get_all_boundnames()
            intruder_names = set(Limit.get_fresh_names(allnames, set(), e))
            for pc in extended.processcalls:
                if pc.id in ext_ids[e]:
                    list_of_factors_annotations = dict_id_factor_annotation[pc.id]
                    for index in xrange(len(list_of_factors_annotations)):
                        extfac, anno = list_of_factors_annotations[index]
                        if extfac == e:
                            action = pc.get_substituted_actions(extended.messages)[index]
                            action_errors = action.check_every_post_for_inclusion(pc, anno, extended, intruder_names)
                            # Not for now as it would make too many copies of it
                            # for a_e in action_errors:
                            #     a_e.set_name_repr_man(name_repr_man_e)
                            list_of_errors_e.extend(action_errors)
                            # if not action.check_every_post_for_inclusion(pc, anno, extended):
                            #     return False
            # Need to translate back here because different expansions have different name_repr
            list_of_errors[e] = list_of_errors_e
        return name_repr_man_e_dict, list_of_errors

    def mark_all_actions_in_pcs_with_ids(self, id_man):
        for pc in self.processcalls:
            pc.mark_all_actions_with_ids(id_man)
        for sl in self.sublimits:
            sl.mark_all_actions_in_pcs_with_ids(id_man)

    def mark_all_pcs_with_ids(self, id_man):
        for pc in self.processcalls + self.iterproccalls:
            pc.mark_with_id(id_man)
        for sl in self.sublimits:
            sl.mark_all_pcs_with_ids(id_man)
        for sp in self.subprocesses:
            sp.mark_all_pcs_with_ids(id_man)

    def check_inputpatterns_and_get_annotations(self, ids_to_be_annotated):
        dict_id_factor_anno = dict()
        for pc in self.processcalls:
            if pc.id in ids_to_be_annotated:
                dict_id_factor_anno[pc.id] = pc.get_extension_factor_and_annotations(self.messages)
                ids_to_be_annotated.remove(pc.id)
            elif not ids_to_be_annotated:
                break
        return dict_id_factor_anno

    def print_with_helper_defs(self):
        sublimitdefs = []
        sublimitdefs, limit_repr = self.print_with_helper_defs_aux(IdentifierManager(1), sublimitdefs)
        sublimitdefs_repr = ";\n".join(sld for sld in sublimitdefs)
        return sublimitdefs_repr + ";\n\n" + limit_repr

    def print_with_helper_defs_aux(self, ident_man, sublimitdefs):
        repnames = ", ".join(str(x) for x in self.newnames)
        repsingles = []
        for m in self.messages:
            repsingles.append('<' + str(m) + '>')
        repsingles.extend(self.processcalls)
        for s in self.subprocesses: # stays currently here (most are limits anyway)
            repsingles.append(str(s))
        for i in self.iterproccalls:
            repsingles.append(str(i) + '^w')
        for l in self.sublimits:
            repsingles.append('L' + str(ident_man.next_id) + '^w')
            sublimitdefs.append('L' + str(ident_man.next()) + ' = ' + l.print_with_helper_defs_aux(ident_man, sublimitdefs)[1])
        repall = " || ". join(str(x) for x in repsingles)
        start = "new " + repnames + "." if self.newnames else ""
        limit_repr = start + "( " + repall + " )"
        return sublimitdefs, limit_repr

    def print_with_helper_defs_tex(self):
        sublimitdefs = []
        sublimitdefs, limit_repr = self.print_with_helper_defs_aux_tex(IdentifierManager(1), sublimitdefs)
        sublimitdefs_repr = "; \\\\ \n".join(sld for sld in sublimitdefs)
        return '\\[ \n\\begin{array}{lcl} \n' + \
               sublimitdefs_repr + "; \n\\end{array} \n\\] \n" +\
               "\\[\n" + limit_repr + '\n\\]'

    def print_with_helper_defs_aux_tex(self, ident_man, sublimitdefs):
        repnames = ", ".join(x.str_tex() for x in self.newnames)
        repsingles = []
        for m in self.messages:
            repsingles.append('\\out{' + m.str_tex() + '}')
        repsingles.extend(map(lambda x: x.str_tex(), self.processcalls))
        for s in self.subprocesses:  # stays currently here (most are limits anyway)
            repsingles.append('S_' + str(ident_man.next_id))
            sublimitdefs.append('S_' + str(ident_man.next()) + ' & = & ' + s.print_with_helper_defs_aux_tex(ident_man, sublimitdefs)[1])
        for i in self.iterproccalls:
            repsingles.append(i.str_tex() + '^w')
        for l in self.sublimits:
            repsingles.append('L_' + str(ident_man.next_id) + '^w')
            sublimitdefs.append('L_' + str(ident_man.next()) + ' & = & ' + l.print_with_helper_defs_aux_tex(ident_man, sublimitdefs)[1])
        repall = " \\parallel ". join(x for x in repsingles)
        start = "\\new " + repnames + "." if self.newnames else ""
        limit_repr = start + "( " + repall + " )"
        return sublimitdefs, limit_repr



