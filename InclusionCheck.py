from ConstraintGenerator import *
from Limit import *
from Process import StopProcess
from PostError import PostError


def check_inclusion(limit1, limit2):
    if not limit1.get_globalnames() <= limit2.get_globalnames():
        return False
    solver = Solver()
    limit1.normalise()
    fixed1 = limit1.get_fixedpart()
    limit2.extend_for_inclusion_check(fixed1)
    limit2.normalise()
    fixed2 = limit2.get_fixedpart()
    matching, constraints = get_matching_and_constraints(fixed1, fixed2)
    solver.add(constraints)
    if (limit1.is_proc()) & (solver.check() == sat):
        return True
    while solver.check() == sat:
        # unwrap limit1 (and discard unused parts of limit2)
        newleft = Limit(set(), limit1.messages, limit1.iterproccalls, limit1.sublimits, [], [])
        # use model to alpha-rename accordingly
        theta = get_theta_from_model(matching, solver.model())
        newleft = newleft.rename(theta)
        l2sublimits = map(lambda x: deepcopy(x), limit2.sublimits)
        newright = Limit(set(), limit2.messages, [], [], limit2.iterproccalls, l2sublimits)
        if check_inclusion(newleft, newright):
            return True
        else:
            # reuse theta as model has changed (could work due to pop())
            solver.add(prohibit_old_model(matching, theta))
    return False


def get_theta_from_model(matching, model):
    theta = dict()
    for i in matching.keys():
        theta[i] = IntNumRef.as_long(model[matching[i]])
    return theta


def prohibit_old_model(matching, theta):
    old_model = []
    for k, v in theta.iteritems():
        old_model.append(matching[k] == v)
    return Not(And(old_model))


def check_inclusion_of_continuation(limit, continuation, proccall, intruders_used):
    if isinstance(continuation, StopProcess):
        return None
    else:
        # compose continuation with messages for left side
        left = Limit(set(), deepcopy(limit.messages), [], [continuation], [], [])
        left.normalise()
        left.reduce_knowledge()
        # only keep iterated components and process call from which the cont. stems
        right = Limit(set(), deepcopy(limit.messages), [proccall], [], deepcopy(limit.iterproccalls), deepcopy(limit.sublimits))
        right.normalise()
        right.reduce_knowledge()
        if check_inclusion(left, deepcopy(right)):
            return None
        # This is the backup-test without absorption, uncomment to enable
        # Currently only used if intruders are used.
        if False:
            left = deepcopy(limit)
            left.processcalls.remove(proccall)
            left.subprocesses.append(continuation)
            left.normalise()
            left.reduce_knowledge()
            if check_inclusion(left, deepcopy(limit)):
                return None
        return PostError(proccall, continuation, limit, left, right)

