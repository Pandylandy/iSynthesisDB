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
    property = Set('Molecule_Property')
    storage = Set('Storage')

    def __init__(self, structure, organic_molecule=True, substance_form='No information', remaining=None,
                        shelf_life='01.01.1900', place='No information', supplier='No information'):
        structure.canonicalize()
        if Molecule_Structure.exists(signature=bytes(structure)):
            raise ValueError('That molecule is already in the database >:-(')
        db.Entity.__init__(self, name = str(structure), organic_molecule = organic_molecule)
        Molecule_Structure(molecule=self, signature=bytes(structure), data=structure)
        Molecule_Property(molecule=self, substance_form=substance_form, remaining=remaining, shelf_life=shelf_life)
        Storage(molecule=self, place=place, supplier=supplier)
        print('Molecule added')
        
    def _structure(self):
        return list(self.structure)[0].get_structure()

    # Определяем функцию, которой передаём молекулу в каноничном виде и находим её в базе данных
    def find_molecule_in_database(any_molecule):
        
        with db_session:
            any_molecule.canonicalize()            
            result = select(molecule
                                for molecule in Molecule
                                for molecule_structure in molecule.structure
                                if molecule_structure.signature == bytes(any_molecule))
            print(result)
            return result

    # Определяем функцию, которая обновляет информацию по имеющейся в базе данных молекуле
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

    # Определяем функцию, которая показывает заканчивающиеся в ближайшие 180 дней сроки годности молекул
    def upcoming_180_days():
        with db_session:
            results = select((molecule, f'Срок годности до: {molecule_property.shelf_life}')
                                for molecule in Molecule
                                for molecule_property in molecule.property
                                if molecule_property.shelf_life < datetime.today() + timedelta(days=180))
            return (list(results))

    # Определяем функцию, которая принимает дату и выводит молекулы до этой даты
    def molecules_before_date(year, month, day):
        with db_session:
            results = select((molecule, f'Срок годности до: {molecule_property.shelf_life}')
                                for molecule in Molecule
                                for molecule_property in molecule.property
                                if molecule_property.shelf_life < datetime(year, month, day))
            return (list(results))         

    # Определяем функцию, которая вернёт все молекулы определённой формы
    def find_form(subst_form):
        with db_session:
            result = select((molecule, f'Форма: {molecule_property.substance_form}')
                                for molecule in Molecule
                                for molecule_property in molecule.property
                                if molecule_property.substance_form == subst_form)
            for i in result:
                yield i
    
    # Определяем функцию, которая вернёт все молекулы меньше определённого порога по весу
    def less_than(remain):
        with db_session:
            result = select((molecule, f'Остаток по весу: {molecule_property.remaining}')
                                for molecule in Molecule
                                for molecule_property in molecule.property
                                if molecule_property.remaining < remain)
            for i in result:
                yield i
    
class Molecule_Structure(db.Entity):
    molecule = Required(Molecule)
    id = PrimaryKey(int, auto=True)  # Identification number of the structure
    signature = Required(bytes)
    bit_array = Optional(str)
    data = Required(bytes)

    def __init__(self, molecule, data, signature):
        data = dumps(data)
        db.Entity.__init__(self, molecule=molecule, signature=signature, data=data)

    def get_structure(self):
        return loads(self.data)

class Storage(db.Entity):
    molecule = Required(Molecule)
    id = PrimaryKey(int, auto=True)  # Identification number of the molecule storage rules
    storage_conditions = Optional(Json)
    place = Required(str)
    supplier = Optional(str)

    def __init__(self, molecule, place='No information', supplier='No information'):
        db.Entity.__init__(self, molecule=molecule, place=place, supplier=supplier)


db.bind('sqlite', 'moleculesDB.sqlite', create_db=True)
db.generate_mapping(create_tables=True)

data_molecules = []
with SDFRead('logBB.sdf') as f:
    data_molecules = [r for r in f]

with db_session:
    # db.Molecule(data_molecules[9], organic_molecule=False, substance_form='Solution', remaining='360',
    #                     shelf_life='15.06.2023', place='19', supplier='No information')

    # db.Molecule[1].add_info(substance_form='Solution', remaining=500.0, shelf_life='01.01.2023')
    # print(db.Molecule[1].structure.get_structure())
    # print(type(db.Molecule[1]._structure()))

    print(Molecule_Property.find_form('powder'))

    for i in Molecule_Property.find_form('powder'):
        print(i)

    for i in Molecule_Property.less_than(500):
        print(i)
