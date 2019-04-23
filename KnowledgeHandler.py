from Message import *


def reduce_knowledge(knowledge):
    changed = True
    while changed:
        changed = False
        for m in knowledge:
            if m.get_kind() == KindMsg.PAIR:
                changed = True
                knowledge.remove(m)
                knowledge.extend(m.get_comps())
            elif (m.get_kind() == KindMsg.ENC) | (m.get_kind() == KindMsg.AENC):
                if constructable_from(m.second, knowledge):
                    changed = True
                    knowledge.remove(m)
                    knowledge.append(m.first)
            elif m.get_kind() == KindMsg.PUB:
                if constructable_from(m.private, knowledge):
                    knowledge.remove(m)


def constructable_from(key, knowledge):
    if key in knowledge:
        return True
    if key.get_kind() == KindMsg.BASIC:
        return False
    elif key.get_kind() == KindMsg.PUB:
        return constructable_from(key.private, knowledge)
    elif key.get_kind() == KindMsg.VAR:
        return False
    elif key.get_kind() == KindMsg.PAIR:
        comps = key.get_comps()
        return constructable_from(comps[0], knowledge) & constructable_from(comps[1], knowledge)
    else:
        raise Exception("Option causing trouble: " + key.get_kind())


def filter_messages_by_size(messages, size):
    return set(filter(lambda x : x.get_size() == size, messages))


def all_messages_of_size(messages, size):
    messages_up_to_s = filter_messages_by_size(messages, size)
    for s in xrange(2, size + 1):
        messages_s_enc = [EncMsg(x, y) for x in messages_up_to_s for y in messages_up_to_s]
        messages_s_pair = [PairMsg(x, y) for x in messages_up_to_s for y in messages_up_to_s]
        messages_up_to_s.union(messages_s_enc)
        messages_up_to_s.union(messages_s_pair)
        messages_up_to_s.union(filter_messages_by_size(messages, s))
    return messages_up_to_s


def get_pairs_from_list_of_msgs(list_msgs):
    if len(list_msgs) > 1:
        return PairMsg(list_msgs[0], get_pairs_from_list_of_msgs(list_msgs[1:]))
    else:
        return list_msgs[0]

