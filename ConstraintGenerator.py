from Message import *
from z3 import *

from collections import defaultdict


def get_matching_and_constraints(proc1, proc2):
    proc1.normalise()
    proc2.normalise()
    constraints = []
    matching, matching_c = get_distinct_matching(proc1.newnames, proc1.get_globalnames(),
                                                 proc2.newnames, proc2.get_globalnames())
    constraints.append(matching_c)
    proc1.reduce_knowledge()
    proc2.reduce_knowledge()
    constraints.append(get_basicmsg_constraints(matching, proc1, proc2))
    constraints.append(get_knowledge_constraints(matching, proc1.messages, proc2.messages))
    constraints.append(get_process_calls_constraints(matching, proc1.processcalls, proc2.processcalls))
    return matching, constraints


def get_distinct_matching(newnames1, globalnames1, newnames2, globalnames2):
    matching = dict(zip(newnames1, [Int('x_%i' %i) for i in newnames1]))
    for g in globalnames1:
        matching[g] = Int('x_%g' % g)
    bounds_cond = And([(Or([matching[i] == j for j in newnames2])) for i in newnames1])
    global_cond = And([matching[i] == i for i in globalnames1])
    if newnames1:
        matching_cond = And(bounds_cond, Distinct(matching.values()), global_cond)
    else:
        matching_cond = And(bounds_cond, global_cond)
    return matching, matching_cond


def get_basicmsg_constraints(matching, proc1, proc2):
    k_l = defaultdict(lambda: False, {})
    k_r = defaultdict(lambda: False, {})
    for m in proc1.messages:
        if m.get_kind() == KindMsg.BASIC:
            k_l[m.name] = True
    for m in proc2.messages:
        if m.get_kind() == KindMsg.BASIC:
            k_r[m.name] = True
    constraints = [If(j == matching[i], (Implies(k_l[i], k_r[j])), True) for i in (proc1.newnames | proc1.get_globalnames())
                                                                         for j in (proc2.newnames | proc2.get_globalnames())]
    return And(constraints)


def get_knowledge_constraints(matching, knowledge1, knowledge2):
    constraints = []
    for m1 in knowledge1:
        if m1.get_kind() != KindMsg.BASIC:
            res = m1.get_conds(matching, knowledge2)
            constraints.append(res[0])  # variables representing
            constraints.extend(res[1])  # constraints
    return And(constraints)


def get_process_calls_constraints(matching, proccalls1, proccalls2):
    proccalls1multiset = defaultdict(lambda: 0, {})
    proccalls2multiset = defaultdict(lambda: 0, {})
    for pc1 in proccalls1:
        proccalls1multiset[pc1] += 1
    for pc2 in proccalls2:
        proccalls2multiset[pc2] += 1
    constraints = []
    pc_w_label = defaultdict(lambda: [], {})
    for pc in proccalls2multiset:
        pc_w_label[pc.label].append(pc)
    pcvariables = defaultdict(lambda: [], {})
    for pc1 in proccalls1multiset:
        pc_right = filter(lambda pc2: proccalls2multiset[pc2] >= proccalls1multiset[pc1], pc_w_label[pc1.label])
        Q = [FreshBool(str(pc1)+'_%i' % i) for i in range(len(pc_right))]
        constraints.append(Or(Q))
        index = 0
        p1 = pc1.parameters
        for pc2 in pc_right:
            p2 = pc2.parameters
            eq_constraints = []
            for i in range(len(p1)):
                equalities = p1[i].equalities_for_split_msgs(p2[i])
                if not equalities:
                    eq_constraints = False
                    break
                eq_constraints.extend([matching[k] == v for (k, v) in equalities])
            if eq_constraints:
                impl = Implies(Q[index], And(eq_constraints))
                constraints.append(impl)
                pcvariables[pc2].append(Q[index])
            else:
                constraints.append(Implies(Q[index], False))
            index += 1
    for key, values in pcvariables.iteritems():
        constraints.append(Sum([If(v, 1, 0) for v in values]) <= 1)
    return And(constraints)
