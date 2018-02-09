# -*- coding: utf-8 -*-

from .types import Type


class Expression(object):
    """
    AST for simple Java expressions. Note that this package deal only with compile-time types;
    this class does not actually _evaluate_ expressions.
    """

    def static_type(self):
        """
        Returns the compile-time type of this expression, i.e. the most specific type that describes
        all the possible values it could take on at runtime. Subclasses must implement this method.
        """
        raise NotImplementedError(type(self).__name__ + " must implement static_type()")

    def check_types(self):
        """
        Validates the structure of this expression, checking for any logical inconsistencies in the
        child nodes and the operation this expression applies to them.
        """
        raise NotImplementedError(type(self).__name__ + " must implement check_types()")


class Variable(Expression):
    """ An expression that reads the value of a variable, e.g. `x` in the expression `x + 5`.
    """
    def __init__(self, name, declared_type):
        self.name = name                    #: The name of the variable
        self.declared_type = declared_type  #: The declared type of the variable (Type)

    def static_type(self):
        return self.declared_type

    def check_types(self):
        pass


class Literal(Expression):
    """ A literal value entered in the code, e.g. `5` in the expression `x + 5`.
    """
    def __init__(self, value, type):
        self.value = value  #: The literal value, as a string
        self.type = type    #: The type of the literal (Type)

    def static_type(self):
        return self.type

    def check_types(self):
        pass


class NullLiteral(Literal):
    def __init__(self):
        super().__init__("null", Type.null)
        self.declared_type = Type.null

    def static_type(self):
        return Type.null

    # def check_types(self):
    #     raise NoSuchMethod()



class MethodCall(Expression):
    """
    A Java method invocation, i.e. `foo.bar(0, 1, 2)`.
    """
    def __init__(self, receiver, method_name, *args):
        self.receiver = receiver
        self.receiver = receiver        #: The object whose method we are calling (Expression)
        self.method_name = method_name  #: The name of the method to call (String)
        self.args = args                #: The method arguments (list of Expressions)

    def static_type(self):
        return self.receiver.declared_type.method_named(self.method_name).return_type

    def check_types(self):
        if self.receiver.declared_type == Type.null:
            self.receiver.declared_type.check_for_null_method(self.method_name)

        if not self.receiver.declared_type.is_subtype_of(Type.object):
            raise JavaTypeError("Type {0} does not have methods".format(self.receiver.declared_type.name))

        method = self.receiver.declared_type.method_named(self.method_name)
        if len(method.argument_types) != len(self.args):
            raise JavaTypeError("Wrong number of arguments for {3}.{0}(): expected {1}, got {2}".format(self.method_name,
                                                                                                        len(method.argument_types),
                                                                                                        len(self.args),
                                                                                                        self.receiver.declared_type.name))
        for i in range(len(method.argument_types)):
            if not self.args[i].static_type().is_subtype_of(method.argument_types[i]):
                raise JavaTypeError("{3}.{0}() expects arguments of type {1}, but got {2}".format(self.method_name,
                                                                                                names(method.argument_types),
                                                                                                typeNames(self.args),
                                                                                                self.receiver.declared_type.name))
            # if self.args[i].type == Type.null and method
            self.args[i].check_types()  # THIS IS AMAZING <-----------


class ConstructorCall(Expression):
    """
    A Java object instantiation, i.e. `new Foo(0, 1, 2)`.
    """
    def __init__(self, instantiated_type, *args):
        self.instantiated_type = instantiated_type  #: The type to instantiate (Type)
        self.args = args                            #: Constructor arguments (list of Expressions)

    def static_type(self):
        return self.instantiated_type

    def check_types(self):
        if self.instantiated_type == Type.null:
            raise JavaTypeError("Type null is not instantiable")

        if not self.static_type().is_subtype_of(Type.object):
            raise JavaTypeError("Type "+self.instantiated_type.name+" is not instantiable")

        if len(self.args) != len(self.instantiated_type.constructor.argument_types):
            raise JavaTypeError("Wrong number of arguments for {0} constructor: expected {1}, got {2}".format(self.instantiated_type.name, len(self.instantiated_type.constructor.argument_types), len(self.args)))

        constructorString = self.instantiated_type.name
        reqArgs = names(self.instantiated_type.constructor.argument_types)
        givenArgs = typeNames(self.args)

        for i in range(len(self.args)):
            self.args[i].check_types()

        for i in range(len(self.args)):
            if not self.args[i].static_type().is_subtype_of(self.instantiated_type.constructor.argument_types[i]):
                raise JavaTypeError("{0} constructor expects arguments of type {1}, but got {2}".format(constructorString,
                                                                                                        reqArgs,
                                                                                                        givenArgs))



class JavaTypeError(Exception):
    """ Indicates a compile-time type error in an expression.
    """
    pass


def names(named_things):
    """ Helper for formatting pretty error messages
    """
    # str = "("

    return "(" + ", ".join([e.name for e in named_things]) + ")"


def typeNames(items):
    """ Helper for formatting pretty error messages for type names
    """
    return "(" + ", ".join([e.static_type().name for e in items]) + ")"

