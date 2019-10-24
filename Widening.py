# Widening.py

from copy import deepcopy
from Program import *
from Limit import *
from Message import Message
from ProcessCall import ProcessCall
from collections import defaultdict
from PostError import *


def widen_iteratively(program, counter):
    program.rename_name_repr() # ensures different numerical names for all binders (important for backtracking)
    limit = program.limit
    c = 0
    no_errors = False
    while c < counter:
        result = widen_by_contis_of_one_proc(limit, program.name_repr_man)
        if result is not None:
            no_errors, limit = result
            if no_errors:
                break
        else:
            break
        c += 1
    program.limit = limit
    return no_errors, program


def widen_by_contis_of_one_proc(limit, name_repr_man):
    original_limit = deepcopy(limit)
    operating_limit = deepcopy(limit)
    name_repr_man_e_dict, lists_of_errors_e = operating_limit.get_error_list_of_posts(name_repr_man)
    error_found = False
    error_processcall_continuation = defaultdict(lambda: [], {})
    for e in lists_of_errors_e.keys():
        # if len(lists_of_errors_e[e]) > 0:
        #     error_found = True
        for error in lists_of_errors_e[e]:
            proccall = name_repr_man_e_dict[e].translate_back_to_num(error.init_proccall)
            continuation = name_repr_man_e_dict[e].translate_back_to_num(error.continuation)
            error_processcall_continuation[proccall].append(continuation)
    continuation_list_one_proccall = None
    for k in error_processcall_continuation.iterkeys():
        initiating_proccall = k
        continuation_list_one_proccall =  error_processcall_continuation[k]
        # break;
    # Merge errors from the same (processcall) continuation
    continuation_msgs = []
    continuation_pcs = []
    if continuation_list_one_proccall is None:
        return True, limit
    if len(continuation_list_one_proccall) > 0:
        error_found = True
        continuation_newnames_chosen = continuation_list_one_proccall[0].newnames
        i = 0
        while (len(continuation_newnames_chosen) > 1) and (len(continuation_list_one_proccall) > i + 1):
            i += 1
            continuation_newnames_chosen = continuation_list_one_proccall[i].newnames
    for conti in continuation_list_one_proccall:
        conti.reduce_knowledge()
        if conti.newnames == continuation_newnames_chosen:
            for m in conti.messages:
                if m not in continuation_msgs:
                    continuation_msgs.append(m)
            for pc in conti.processcalls:
                num_in_single = len(filter(lambda x: x == pc, conti.processcalls))
                num_in_combin = len(filter(lambda x: x == pc, continuation_pcs))
                if num_in_single > num_in_combin:
                    continuation_pcs.extend([pc for _ in range(num_in_single - num_in_combin)])
    if error_found:
        combined_continuation = Process(continuation_list_one_proccall[i].newnames, continuation_msgs, continuation_pcs, [])
        result = tighten_normalised_process(combined_continuation)
        if result is not None:
            new_process, bubbled_up = result
        else:
            return None
        # 1st check whether PC is omega_needed -> need to apply omega to all: new_process and bubbled_up
        # omega_needed = is_reproducing(bubbled_up, initiating_proccall) | choice_has_tau(initiating_proccall)
        omega_needed = True
        # 2nd find upper-most position for new_process in limit and place it there
        #     for bubbled_up, we can also check whether old parts already exist and omit them or just add omegas
        original_limit = incorporate_bubbled_up(original_limit, bubbled_up, omega_needed)
        if new_process is not None:
           original_limit = incorporate_new_process(original_limit, new_process, omega_needed)
    return (not error_found), original_limit


def tighten_normalised_process(process):
    # assert normalised (by the fact where it stems from)
    # new _. ( ... || ... || new _. ...) is not necessary. The inner subprocess can be modelled via tau. and pc-def
    assert len(process.subprocesses) == 0
    # currently just bubble up things that don't use THE new name (in all 3ex. only 1)
    bubbled_up = [] #for them, we need to check whether they are in there
    if len(process.newnames) > 1:
        return None
        # raise Exception()
    bubble_all_up = False
    if len(process.newnames) == 0:
        # split them -> in this Yahalom example only one but may be more
        bubble_all_up = True
    process.reduce_knowledge() # in order to split pairs and all that
    stays_as_msg = []
    for m in process.messages:
        if process.newnames  <= m.get_names() and not bubble_all_up:
            stays_as_msg.append(m)
            # keep there and include,
        else:
            bubbled_up.append(m)
    proccalls = deepcopy(process.processcalls)
    stays_as_pc = []
    for pc in proccalls:
        if process.newnames <= pc.get_names() and not bubble_all_up:
            stays_as_pc.append(pc)
            # keep there and include,
        else:
            bubbled_up.append(pc)
    if bubble_all_up:
        return None, bubbled_up
    return Process(process.newnames, stays_as_msg, stays_as_pc, []), bubbled_up


def is_reproducing(bubbled_up, init_proccall):
    for b in filter(lambda x: isinstance(x, ProcessCall), bubbled_up):
        if (b.label == init_proccall.label) & (b.parameters == init_proccall.parameters):
            return True
    return False


def choice_has_tau(initiating_proccall):
    return len(filter(lambda action: action.inputprefix.tau, initiating_proccall.get_substituted_actions())) > 0


def incorporate_bubbled_up(new_limit, bubbled_up, reproducing):
    global_names = new_limit.get_globalnames()
    for b in bubbled_up:
        names_in_b = b.get_names() - global_names
        # Find upper-most position
        # descend_in_sublimit_or_subprocess to cover another name (should be unique choice),
        # Maybe, we can build an auxiliary structure for the limit which indicates where (unique) names are;
        # possibly as sequence of indices to follow and then choose the longest sequence for names contained in b
        indices_to_scope_extrude, indices = find_position_with_names_linearly(names_in_b, new_limit)
        if len(indices_to_scope_extrude) is not 0:
            pass
        # Apply position:
        current_limit_or_process = new_limit
        for (which, i) in indices:
            if which:
                current_limit_or_process = current_limit_or_process.subprocesses[i]
            else:
                current_limit_or_process = current_limit_or_process.sublimits[i]
        # b can only be a message or process call by assumption that only one new name is produced
        if isinstance(b, Message):
            if b not in current_limit_or_process.messages:
                current_limit_or_process.messages.append(b)
        elif isinstance(b, ProcessCall):
            if reproducing:
                # remove from processcalls and ensure it is in iterproccalls
                if b in current_limit_or_process.processcalls:
                    current_limit_or_process.processcalls.remove(b)
                if b not in current_limit_or_process.iterproccalls:
                    current_limit_or_process.iterproccalls.append(b)
            else:
                # if it is in iterproccalls, should be handled
                # if not, check if in processcalls and put it there
                if b not in current_limit_or_process.iterproccalls and b not in current_limit_or_process.processcalls:
                    current_limit_or_process.processcalls.append(b)
        else:
            raise Exception('only messages and processcalls should be bubbled up')
    return new_limit


# Works only for e=1 currently as it is not too obvious how to handle e > 1 as names are introduced several times
# Need to log more about the renaming behaviour
# Assumes unique names for now (should be reasonable)
def find_position_with_names_linearly(names_in_b, current_limit_or_process):
    working_names = deepcopy(names_in_b)
    working_names.difference_update(current_limit_or_process.newnames)
    if len(working_names) is not 0:
        for i in range(len(current_limit_or_process.subprocesses)):
            if working_names <= current_limit_or_process.subprocesses[i].get_all_boundnames():
                remaining, indices = find_position_with_names_linearly(working_names, current_limit_or_process.subprocesses[i])
                if not (working_names <= remaining): # had some success
                    return remaining, [(True , i)] + indices
        for i in range(len(current_limit_or_process.sublimits)):
            if working_names <= current_limit_or_process.sublimits[i].get_all_boundnames():
                remaining, indices = find_position_with_names_linearly(working_names, current_limit_or_process.sublimits[i])
                if not (working_names <= remaining):
                    return remaining, [(False , i)] + indices
    return working_names, []


def incorporate_new_process(new_limit, new_process, reproducing):
    global_names = new_limit.get_globalnames()
    names_in_new_proc = new_process.get_globalnames() - global_names
    # may need to descend there, but might not be necessary (or even complete) but reduces number of burden of new names introduced there
    # Find upper-most position
    # descend_in_sublimit_or_subprocess to cover another name (should be unique choice)
    current_limit_or_process = new_limit
    indices_to_scope_extrude, indices = find_position_with_names_linearly(names_in_new_proc, current_limit_or_process)
    # Either find the right subcomponent by descending linearly or scope extrude and try again
    # Apply position:
    for (which, i) in indices:
        if which:
            new_process.newnames.difference_update(current_limit_or_process.subprocesses[i].newnames)
            current_limit_or_process = current_limit_or_process.subprocesses[i]
        else:
            new_process.newnames.difference_update(current_limit_or_process.sublimits[i].newnames)
            current_limit_or_process = current_limit_or_process.sublimits[i]
    while len(indices_to_scope_extrude) is not 0:
            splitting_point_indices, first_indices, second_indices = get_indices_to_move_one_to_another_comp(indices_to_scope_extrude, current_limit_or_process)
            # apply splitting point indices
            splitting_limit = current_limit_or_process
            for (which, i) in splitting_point_indices:
                if which:
                    splitting_limit = splitting_limit.subprocesses[i]
                else:
                    splitting_limit = splitting_limit.sublimits[i]
            # find the component to put into
            where_to_put_limit = splitting_limit
            for (which, i) in first_indices:
                if which:
                    where_to_put_limit = where_to_put_limit.subprocesses[i]
                else:
                    where_to_put_limit = where_to_put_limit.sublimits[i]
            # find the component to move
            working_limit = splitting_limit
            second_indices_ = second_indices[:-1]
            for (which, i) in second_indices_:
                if which:
                    working_limit = working_limit.subprocesses[i]
                else:
                    working_limit = working_limit.sublimits[i]
            kind_of_comp, index_of_comp = second_indices[-1]
            if kind_of_comp:
                component = working_limit.subprocesses.pop(index_of_comp)
            else:
                component = working_limit.sublimits.pop(index_of_comp)
            # input the component:
            if kind_of_comp:
                where_to_put_limit.subprocesses.append(component)
            else:
                where_to_put_limit.sublimits.append(component)
            # Find new and apply position:
            indices_to_scope_extrude, indices = find_position_with_names_linearly(names_in_new_proc, current_limit_or_process)
            for (which, i) in indices:
                if which:
                    names_in_new_proc.difference_update(current_limit_or_process.subprocesses[i].newnames)
                    current_limit_or_process = current_limit_or_process.subprocesses[i]
                else:
                    names_in_new_proc.difference_update(current_limit_or_process.sublimits[i].newnames)
                    current_limit_or_process = current_limit_or_process.sublimits[i]
    descend_further = (new_process.newnames <= current_limit_or_process.get_all_boundnames()) & (not (len(new_process.newnames) == 0))
    if descend_further:
        indices_to_scope_extrude, indices = find_position_with_names_linearly(new_process.newnames, current_limit_or_process)
        if len(indices_to_scope_extrude) is not 0:
            raise Exception()
        for (which, i) in indices:
            if which:
                current_limit_or_process = current_limit_or_process.subprocesses[i]
            else:
                current_limit_or_process = current_limit_or_process.sublimits[i]
        similar_to_bubbled_up = []
        similar_to_bubbled_up.extend(new_process.messages)
        similar_to_bubbled_up.extend(new_process.processcalls)
        # This does not work due to 'new' global names
        # b can only be a message or process call by assumption that only one new name is produced
        for b in similar_to_bubbled_up:
            if isinstance(b, Message):
                if b not in current_limit_or_process.messages:
                    current_limit_or_process.messages.append(b)
            elif isinstance(b, ProcessCall):
                if reproducing:
                    # remove from processcalls and ensure it is in iterproccalls
                    if b in current_limit_or_process.processcalls:
                        current_limit_or_process.processcalls.remove(b)
                    if b not in current_limit_or_process.iterproccalls:
                        current_limit_or_process.iterproccalls.append(b)
                else:
                    # if it is in iterproccalls, should be handled
                    # if not, check if in processcalls and put it there
                    if b not in current_limit_or_process.iterproccalls and b not in current_limit_or_process.processcalls:
                        current_limit_or_process.processcalls.append(b)
            else:
                raise Exception('only messages and processcalls should be bubbled up')
    else:
        # Incorporate new_process there as sublimit iff reproducing
        if len(new_process.newnames) == 0:
            sim_bubbled_up = [x for x in new_process.messages] + \
                             [x for x in new_process.processcalls] + \
                             [x for x in new_process.subprocesses]
            # maybe current_limit_... here but it may work like this
            new_limit = incorporate_bubbled_up(new_limit, sim_bubbled_up, reproducing)
        else:
            if reproducing:
                new_proc_omega = new_process.make_limit_from_proc()
                current_limit_or_process.sublimits.append(new_proc_omega)
            else:
                current_limit_or_process.subprocesses.append(new_process)
    return new_limit # Check whether the inner part is really updated and returned


def get_indices_to_move_one_to_another_comp(indices_to_scope_extrude, current_limit_or_process):
    # find splitting point
    splitting_point_indices = find_splitting_point(indices_to_scope_extrude, current_limit_or_process)
    # Idea: find two name restrictions that are not linear to each other and input one into the other
    splitting_limit = current_limit_or_process
    for (which, i) in splitting_point_indices:
        if which:
            splitting_limit = splitting_limit.subprocesses[i]
        else:
            splitting_limit = splitting_limit.sublimits[i]
    first_name, second_name = find_two_non_linear_name_restrictions(indices_to_scope_extrude, splitting_limit)
    remaining_1, first_indices = find_position_with_names_linearly({first_name}, splitting_limit)
    remaining_2, second_indices = find_position_with_names_linearly({second_name}, splitting_limit)
    if (len(remaining_1) > 0) or (len(remaining_2) > 0):
        raise Exception('One name should be ok to find indices for!')
    return splitting_point_indices, first_indices, second_indices


def find_splitting_point(indices_to_scope_extrude, working_limit):
    current_limit_or_process = working_limit
    descended = True
    indices = []
    while descended:
        descended = False
        for i in range(len(current_limit_or_process.subprocesses)):
            if indices_to_scope_extrude <= current_limit_or_process.subprocesses[i].get_all_boundnames():
                current_limit_or_process = current_limit_or_process.subprocesses[i]
                indices = indices + [(True, i)]
                descended = True
                continue
        for i in range(len(current_limit_or_process.sublimits)):
            if indices_to_scope_extrude <= current_limit_or_process.sublimits[i].get_all_boundnames():
                current_limit_or_process = current_limit_or_process.sublimits[i]
                indices = indices + [(False, i)]
                descended = True
                continue
    return indices


def find_two_non_linear_name_restrictions(indices_to_scope_extrude, current_limit_or_process):
    name_combinations = [(x, y) for x in indices_to_scope_extrude for y in indices_to_scope_extrude]
    for (x, y) in filter(lambda (x, y): x is not y, name_combinations):
        indices_x = find_position_with_names_linearly(set([x]), current_limit_or_process)
        indices_y = find_position_with_names_linearly(set([y]), current_limit_or_process)
        if (not is_prefix_of(indices_x[1], indices_y[1])) and (not is_prefix_of(indices_y[1], indices_x[1])):
            return x, y
    raise Exception('Should have been possible to deal with this')


# Helper function that checks whether one list is prefix of another (not the same)
def is_prefix_of(indices_x, indices_y):
    if len(indices_x) >= len(indices_y):
        return False
    for i in range(len(indices_x)):
        if not indices_x[i] == indices_y[i]:
            return False
    return True
