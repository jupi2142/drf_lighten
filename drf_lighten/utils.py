def get_flattened_subclasses(class_):
    for subclass in class_.__subclasses__():
        yield subclass
        inner_subclasses = get_flattened_subclasses(subclass)
        for inner_subclass in inner_subclasses:
            yield inner_subclass


def get_model_serializer_subclasses(class_):
    subclasses = get_flattened_subclasses(class_)
    for subclass in subclasses:
        try:
            subclass.Meta.model
            yield subclass
        except AttributeError:
            pass
