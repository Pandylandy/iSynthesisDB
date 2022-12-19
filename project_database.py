from decimal import Decimal
from pony.orm import *
from datetime import *
from CGRtools.files import SDFRead
from pickle import dumps, loads
import time

db = Database()


class Molecule(db.Entity):
    """Full information about every molecule in laboratory"""
    id = PrimaryKey(int, auto=True)  # Identification number of the molecule
    name = Required(str)
    organic_molecule = Required(bool)  # Is that organic molecule or not
    structure = Set('Molecule_Structure')
    properties = Set('Molecule_Property')
    storage = Set('Storage')
    reactions = Set('MoleculeReaction')

    def __init__(self, structure, organic_molecule=True, substance_form='No information', remaining=None,
                        shelf_life='01.01.1900', place='No information', supplier='No information'):
        if Molecule_Structure.exists(signature=bytes(structure)):
            raise ValueError('That molecule is already in the database >:-(')
        db.Entity.__init__(self, name = str(structure), organic_molecule = organic_molecule)
        Molecule_Structure(molecule=self, signature=bytes(structure), data=structure)
        Molecule_Property(molecule=self, substance_form=substance_form, remaining=remaining, shelf_life=shelf_life)
        Storage(molecule=self, place=place, supplier=supplier)
        print('Molecule added')
        
    @property
    def _structure(self):
        return next(iter(self.structure)).structure

    @property
    def description(self):
        return [x.molecule_description for x in self.properties]

    # Определяем метод, в который передаём молекулу в каноничном виде и находим её в базе данных
    def find_molecule_in_db(any_molecule):
        with db_session:
            result =  Molecule_Structure.get(signature=bytes(any_molecule))
            if result:
                return result.molecule

    # Определяем метод, который обновляет информацию по имеющейся в базе данных молекуле
    def add_info(self, substance_form='No information', remaining=None,
                        shelf_life='01.01.1900', place='No information', supplier='No information'):
        Molecule_Property(molecule=self, substance_form=substance_form, remaining=remaining, shelf_life=shelf_life)
        Storage(molecule=self, place=place, supplier=supplier)

class Molecule_Property(db.Entity):
    molecule = Required(Molecule)
    id = PrimaryKey(int, auto=True)  # Identification number of the property
    substance_form = Optional(str)
    remaining = Optional(Decimal)
    shelf_life = Optional(datetime, auto=True)

    def __init__(self, molecule, substance_form, remaining, shelf_life):
        if Molecule_Property.exists(molecule=molecule, substance_form=substance_form, 
                                    remaining=remaining, shelf_life=shelf_life):
            raise ValueError('That property information is already in the database >:-(')
        db.Entity.__init__(self, molecule=molecule, substance_form=substance_form, remaining=remaining, shelf_life=shelf_life)

    # Определяем метод, который показывает заканчивающиеся в ближайшие 180 дней сроки годности молекул
    @classmethod
    def upcoming_180_days(cls):
        with db_session:
            return [x.molecule for x in cls.select(lambda p: p.shelf_life < datetime.today() + timedelta(days=180))]

    # Определяем метод, который принимает дату и выводит молекулы до этой даты
    @classmethod
    def molecules_before_date(cls, year, month, day):
        with db_session:
            return [x.molecule for x in cls.select(lambda p: p.shelf_life < datetime(year, month, day))]      

    # Определяем метод, который вернёт все молекулы определённой формы
    @classmethod
    def find_form(cls, subst_form):
        with db_session:
            return [x.molecule for x in cls.select(lambda p: p.substance_form == subst_form)]
    
    # Определяем метод, который вернёт все молекулы меньше определённого порога по весу
    @classmethod
    def less_than(cls, remain):
        with db_session:
            return [x.molecule for x in cls.select(lambda p: p.remaining < remain)]
     
     # Определяем метод, который вернёт полное описание молекулы
    @property
    def molecule_description(self):
        with db_session:
            res_1 = {'Форма субстанции': self.substance_form}
            res_2 = {'Остаток': str(int(self.remaining))}
            res_3 = {'Срок годности': self.shelf_life.strftime('%d.%m.%Y')}
        return {**res_1, **res_2, **res_3}

class Molecule_Structure(db.Entity):
    molecule = Required(Molecule)
    id = PrimaryKey(int, auto=True)  # Identification number of the structure
    signature = Required(bytes)
    bit_array = Optional(str)
    data = Required(bytes)

    def __init__(self, molecule, data, signature):
        data = dumps(data)
        db.Entity.__init__(self, molecule=molecule, signature=signature, data=data)

    @property
    def structure(self):
        return loads(self.data)

class Storage(db.Entity):
    molecule = Required(Molecule)
    id = PrimaryKey(int, auto=True)  # Identification number of the molecule storage rules
    storage_conditions = Optional(Json)
    place = Required(str)
    supplier = Optional(str)

    def __init__(self, molecule, place='No information', supplier='No information'):
        db.Entity.__init__(self, molecule=molecule, place=place, supplier=supplier)

class Reaction(db.Entity):
    id = PrimaryKey(int, auto=True)
    molecules = Set('MoleculeReaction')
    metadata = Optional(Json)
    reaction_indexs = Set('ReactionIndex')

    def __init__(self, structure):
        if ReactionIndex.exists(signature=bytes(~structure)):
            raise ValueError('That molecule is already in the database >:-(')
        Reactants=structure.reactants
        Products=structure.products

class MoleculeReaction(db.Entity):
    id = PrimaryKey(int, auto=True)
    reaction = Required(Reaction)
    molecule = Required(Molecule)
    product = Optional(bool)

class ReactionIndex(db.Entity):
    id = PrimaryKey(int, auto=True)
    reaction = Required(Reaction)
    signature = Optional(Json)
    bit_array = Optional(str)

db.bind('sqlite', 'moleculesDB.sqlite', create_db=True)
db.generate_mapping(create_tables=True)

data_molecules = []
with SDFRead('logBB.sdf') as f:
    data_molecules = [r for r in f]

with db_session:
    # Тест работы метода find_molecule_in_db()
    # data_molecules[3].canonicalize
    # print(Molecule.find_molecule_in_db(data_molecules[2]))

    # Добавить молекулу из logBB.sdf
    # db.Molecule(data_molecules[3], organic_molecule=True, substance_form='Powder', remaining='480',
    #                     shelf_life='01.05.2023', place='18', supplier='EcoPharm')

    # db.Molecule[1].add_info(substance_form='Solution', remaining=500.0, shelf_life='01.01.2023')
    # print(db.Molecule[1].structure.get_structure())
    # print(db.Molecule[1]._structure)

    # Тест работы метода description()
    # print(db.Molecule[1].description)

    # Тест работы метода upcoming_180_days()
    # print(Molecule_Property.upcoming_180_days())

    # Тест работы метода molecules_before_date()
    # print(Molecule_Property.molecules_before_date(2023, 4, 30))

    # Тест работы метода find_form()
    # print(Molecule_Property.find_form('Solution'))

    # Тест работы метода less_than()
    print(Molecule_Property.less_than(499))