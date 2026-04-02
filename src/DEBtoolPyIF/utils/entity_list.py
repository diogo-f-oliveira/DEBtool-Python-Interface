from collections.abc import Iterable


def normalize_entity_list(entity_list, *, allow_all=True, argument_name="entity_list"):
    if isinstance(entity_list, str):
        if allow_all and entity_list == "all":
            return "all"
        return [entity_list]

    if not isinstance(entity_list, Iterable):
        raise TypeError(
            f"{argument_name} must be 'all', a string entity ID, or an iterable of string entity IDs."
        )

    return list(entity_list)
