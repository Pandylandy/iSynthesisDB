from datetime import date
from decimal import Decimal
from pony.orm import *


db = Database()


class Molecule(db.Entity):
    """Full information about every molecule the in laboratory"""
    ID = PrimaryKey(int, auto=True)  # Identification number of the molcule
    Organic_Molecule = Required(bool)  # Is that organic molecule or not
    Inorganic_Molecule = Required(bool)  # Is that inorganic molecule or not
    Structure = Set('Molecule_Structure')
    Property = Set('Molecule_Property')
    Storage = Set('Storage')


class Molecule_Property(db.Entity):
    Molecule = Required(Molecule)
    ID = PrimaryKey(int, auto=True)  # Identification number of the property
    Substance_form = Required(str)
    Remaining = Required(Decimal)
    Shelf_life = Required(date)


class Molecule_Structure(db.Entity):
    Molecule = Required(Molecule)
    ID = PrimaryKey(int, auto=True)  # Identification number of the structure
    Signature = Required(Json)
    Bit_array = Required(str)


class Storage(db.Entity):
    Molecule = Required(Molecule)
    ID = PrimaryKey(int, auto=True)  # Identification number of the molecule storage rules
    Storage_conditions = Required(Json)
    Place = Required(str)
    Supplier = Optional(str)


set_sql_debug(True)
db.bind('sqlite', 'moleculesDB.sqlite', create_db=True)
db.generate_mapping(create_tables=True)