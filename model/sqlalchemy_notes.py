#!/usr/bin/env python3

# So, I've often found myself bumping up against a lack of
# understanding of SQLAlchemy's basic principles. These are my notes
# taken during a study sesh, during which I go on some tangents into
# Python's metaclasses.
#
# Skimming through the SQLAlchemy docs the basic separation seems to
# be between the "core" which provides a set of tools for representing
# schemas and queries, and the "ORM" which helps with the rather
# complicated task of relating Python objects to each other in a way
# that corresponds to the relationships in the database.

# ====================================================================

# Question: How does inheriting from a specific class create an entry
# in the metadata? For example:

from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column('id', Integer, primary_key=True)
    name = Column('name', String)

# That's weird. Like C#'s main ORM "Entity Framework" you write
# classes that correspond to tables, but you have to use an external
# tool at compile time to actually create the database from the model
# definitions in code. I guess the alternative approach (that would be
# close to how things work in SQLAlchemy) would be to use reflection
# to generate the database at runtime.
#
# Basically the way SQLAlchemy creates the relationship between the
# Python definition of an object and their counterparts in the
# database (i.e. the object relational model) is by keeping a list of
# entries in a thing called the "metadata":

# ====================================================================
#      +----------+
#      | metadata |
#      +----------+
#           |
#    +------+------+------+------+--- …
#    |             |             |
# +------+      +------+         …
# | User |      | Post |
# +------+      +------+
# ====================================================================

# The class version is syntactic sugar from the `orm` module for this:

from sqlalchemy import MetaData, Table

metadata = MetaData()

user = Table('users',
             metadata,
             Column('id', Integer, primary_key=True),
             Column('name', String))

print(metadata.sorted_tables)

# That version is easier to understand because you're explicitly
# passing the `metadata` into the table, so you could just update the
# metadata by adding the new table of it. Then when you go to create
# the database in SQLite or whatever you can easily traverse the
# `metadata`. The mechanism that allows the class version to work is
# Python's metaclass feature:

# ====================================================================
#              +--------+    +-------+    +-----------+
#              | object | -> | class | -> | metaclass |
#              +--------+    +-------+    +-----------+
#
#        An object is to a class as a class is to a metaclass.
# ====================================================================

# In Python /everything/ is an object, including classes. A class
# definition isn't really much like a class definition in a statically
# typed language, they're really more like regular variable
# definitions; declaring a class is defining a concrete instance of an
# object. What is it an instance of, you may ask? Well:

class Foo:
    pass

print('Type of Foo: {0}'.format(type(Foo)))

# => Type of Foo: <class 'type'>

# All classes are instances of the God Metaclass `type`. You can even
# construct a class imperatively:

Foo = type(
    'Foo',                      # __name__
    (object,),                  # __bases__
    {                           # __dict__
        'hi': 2,
    }
)

print('Foo.__dict__ = {0}'.format(Foo.__dict__))
print('Foo.__bases__ = {0}'.format(Foo.__bases__))
print(Foo())

# So basically `type` is my mental canonical example of what a
# metaclass is; if you inspect the output of the `__dict__`:
#
# ====================================================================
# {'hi': 2, '__module__': '__main__', '__dict__': <attribute
# '__dict__' of 'Foo' objects>, '__weakref__': <attribute
# '__weakref__' of 'Foo' objects>, '__doc__': None}
# ====================================================================
#
# … You'll see that there's a bunch of stuff we didn't declare
# explicitly. The `type` metaclass is a constructor for classes which
# adds all the crap you'd expect any Python class to have, like
# __doc__. Languages like C# don't have the concept of metaclasses and
# it's very rare in Python to use any metaclass other than `type`, but
# SQLAlchemy uses metaclasses to implement its DSL for describing
# schemas; when you use the class syntax to declare a schema, each
# class is having a bunch of extra junk added to it and being thrown
# into the metadata object by the metaclass.
#
# Because classes are objects and created at runtime
# (i.e. fundamentally imperative rather than declarative), everything
# you need to implement Python's OOP is in the Python code itself,
# rather than in the interpreter:

print('Foo MRO: {0}'.format(Foo.mro()))

# You could do something like this to get a list of classes in a
# simple inheritance hierarchy:

class A:
    pass

class B(A):
    pass

class C(B):
    pass

print(C.mro()[1:-1]) # => [<class '__main__.B'>, <class '__main__.A'>]

# Or you could use `__subclasses__` on the parent:

class D(A):
    pass

print('A and its subclasses:')
subclasses = [A]
all_subclasses = []

while len(subclasses) > 0:
    print(subclasses)
    for item in subclasses: all_subclasses.append(item)
    subclasses = [item for classitem in subclasses
                  for item in classitem.__subclasses__()]

print('All subclasses of A: {0}'.format(all_subclasses))

# There's nothing really magical about this:
# https://github.com/python/cpython/blob/b11a384dc7471ffc16de4b86e8f5fdeef151f348/Include/cpython/object.h#L214

# For the sake of completeness, here's an example of a real-world metaclass:

class Singleton(type):
    instance = {}

    def __call__(cls):
        if cls not in cls.instance:
            # This `super` prevents the `__call__` from calling the
            # metaclass (i.e., this class itself).
            cls.instance[cls] = super(Singleton, cls).__call__()
        return cls.instance[cls]

class A(metaclass=Singleton):
    value = 'honk'

class B(metaclass=Singleton):
    pass

A().value = 'bonk'
B()

print(A().value)
print(Singleton.instance)

# … But obviously that's an insane way to implement a
# singleton. Really, ORMs seem to be the main use case. Basically, if
# you ever want to use a class as a definition of arbitrary data then
# a metaclass is the trick; it so happens in the case of SQLAlchemy
# that classes describe:
#
# + The way we want to access information in the database
# + The way information in the database should be created
#
# And this coincidence makes metaclasses handy for combining both
# descriptions into a single declarative element. Incidentally, the
# fact that classes are objects means you can write decorators for
# them:

def singleton(cls):
    return Singleton(cls.__name__, cls.__bases__, dict(cls.__dict__))

@singleton
class C:
    value = 'hello'

C().value = 'hi'
print('C().value = {0}'.format(C().value)) # C().value = hi

# Hmm…

class Table:
    def __repr__(self):
        return 'Table {0}:\n\n'.format(self.name) + \
            '\n'.join([str(row) for row in self.rows])

    def insert(self, values):
        for i in range(len(values)):
            if not isinstance(values[i], self.schema[i][1]):
                return
        self.rows.append(values)

    def __init__(self, name, schema):
        self.name = name
        self.schema = schema
        print(schema)
        self.rows = []

class Database:
    def create(self, tablename, schema):
        self.tables[tablename] = Table(tablename, schema)

    def insert(self, tablename, values):
        self.tables[tablename].insert(values)

    def __repr__(self):
        return '\n\n'.join([str(v) for k, v in self.tables.items()])

    def __init__(self):
        self.tables = {}

class Engine:
    class MetadataClass(type):
        __metadata__ = {}

        def __init__(cls, name, bases, dct):
            if name not in cls.__metadata__ and name != 'Model':
                cls.__metadata__[name] = [(k, v) for k, v in cls.__dict__.items() if k[0:2] != '__']

        def __call__(cls, *args, **kwargs):
            ret = type(cls.__name__, cls.__bases__, dict(cls.__dict__))
            setattr(ret, '__values__', list(args))
            return ret

    class Model(metaclass=MetadataClass):
        pass

    def create_all(self):
        for k, v in self.MetadataClass.__metadata__.items():
            self.db.create(k, v)

    def commit(self):
        for name, values in self.uncommitted:
            self.db.insert(name, values)
        self.uncommitted = []

    def add(self, obj):
        self.uncommitted.append((obj.__name__, obj.__values__))

    def __repr__(self):
        return '{0}\n\nUncommitted transactions:\n\n{1}\n'.format(str(self.db), '\n'.join(['insert into {0} values ({1})'.format(name, values) for name, values in self.uncommitted]))

    def __init__(self):
        self.db = Database()
        self.uncommitted = []

# User code:

db = Engine()

class Person(db.Model):
    id = int
    name = str

db.create_all()

bob = Person(1, 'bob')
alice = Person(2, 'alice')
john = Person(3, 42)

db.add(bob)
db.add(alice)
db.add(john)

print(db)

db.commit()

print(db)

# Well anyway this is getting to be a diversion, maybe I'll come back
# to this and add queries and such.

# Resources:
#
# + https://towardsdatascience.com/metaclasses-e9d23ae44c2d
#   A succinct overview of metaclasses
# + https://rhettinger.wordpress.com/2011/05/26/super-considered-super/
#   yes
# + https://xnuinside.medium.com/sqlalchemy-metaclasses-and-declarative-base-configure-db-models-classes-a904429d728a
#   Weird use case of metaclasses to modify SQLAlchemy's DSL
# + https://blog.pilosus.org/posts/2019/05/02/python-mro/
#   Discussion of how Python handles multiple inheritance with C3
# + https://fuhm.net/super-harmful/
#   Overview of gotchas with `super`

# ====================================================================

# So that's all the metaclass malarky out of the way and we can get
# back to actual SQLAlchemy.

from sqlalchemy import Column, String, Integer
from sqlalchemy import MetaData, Table

metadata1 = MetaData()
metadata2 = MetaData()

user = Table('users',
             metadata1,
             Column('id', Integer, primary_key=True),
             Column('name', String))

user = Table('users',
             metadata2,
             Column('id', Integer, primary_key=True),
             Column('name', String))

print(metadata1.sorted_tables)
print(metadata2.sorted_tables)

# ====================================================================
#
#                                +-----+
#                                | SQL |
#                                +-----+
#                                   |
#                    +---------+---------+---------+
#                    |         |         |         |
#                 +-----+   +-----+   +-----+   +-----+
#                 | DML |   | DDL |   | DCL |   | TCL |
#                 +-----+   +-----+   +-----+   +-----+
#                 Select    Create    Grant     Save point
#                 Insert    Alter     Revoke    Roll back
#                 Update    Drop                Commit
#                 Delete    Truncate
#
#                   The four primary subsets of SQL:
#
#                    - Data modification language
#                    - Data definition language
#                    - Data control language
#                    - Transaction control language
#
# ====================================================================

from sqlalchemy import create_engine

engine = create_engine('sqlite:///:memory:', echo=True)

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column('id', Integer, primary_key=True)
    username = Column('username', String)

Base.metadata.create_all(engine)

# Or we could deal with the metadata directly:

metadata = MetaData()

user = Table('users',
             metadata,
             Column('id', Integer, primary_key=True),
             Column('username', Integer))

metadata.create_all(engine)

# So at this point there's an engine, but that really just deals with
# translating between the specific database's dialect of SQL and the
# internal representation of DDL/DML with query objects and such. It
# also manages all the connections you might have if you're connected
# to multiple engines. To communicate with a specific database you
# have to create a session:

from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)

# The `Session` is capitalized because it's a class generated by a
# metaclass.

session = Session()

A = User(username='A')
B = User(username='B')
C = User(username='C')

session.add(A)
session.add(B)
session.add(C)

# All changes and additions get batched intelligently by the
# engine. You can check the state of unflushed data at any time:

print(session.new) # => IdentitySet([
                   #      <__main__.User object at 0x...>,
                   #      <__main__.User object at 0x...>,
                   #      <__main__.User object at 0x...>
                   #    ])

# You can expunge all the things you've added to a session that
# haven't yet been flushed to the underlying database or add things
# all at once rather than with individual calls to `add`:

session.expunge_all()
session.add_all([A, B, C])

session.commit()

# Or check for modifications:

A.username = '100'

print(session.dirty)
# => IdentitySet([<__main__.User object at 0x...>])

session.commit()

# When we created the engine with `echo=True` it enabled logging with
# Python's standard `logging` library, which allows us to see the SQL
# generated by the previous `commit()`:
#
# ====================================================================
# BEGIN
# SELECT users.id AS users_id
# FROM users
# WHERE users.id = 1
# UPDATE users SET username='100' WHERE users.id = 1
# COMMIT
# ====================================================================
#
# Flask-SQLAlchemy has `db.Model` instead of the `Base` you would get
# from `declarative_base`. It has some extra stuff for dealing with
# SQLAlchemy in the context of a web server, like `first_or_404` and
# `paginate`:
#
# https://stackoverflow.com/questions/22698478/what-is-the-difference-between-the-declarative-base-and-db-model
#
# Under the hood it's just `declarative_base`. It also does some extra
# wrapping so you don't have to specify `__tablename__` manually.
