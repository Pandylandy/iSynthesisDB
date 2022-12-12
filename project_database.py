from decimal import Decimal
from pony.orm import *
from datetime import *
from CGRtools.files import SDFRead

db = Database()


class Molecule(db.Entity):
    """Full information about every molecule in laboratory"""
    id = PrimaryKey(int, auto=True)  # Identification number of the molecule
    name = Required(str)
    organic_molecule = Required(bool)  # Is that organic molecule or not
    structure = Set('Molecule_Structure')
    property = Set('Molecule_Property')
    storage = Set('Storage')

    # Определяем функцию, которая добавляет новую молекулу в базу данных, выписывая всю информацию
    def add_molecule(structure, organic_molecule=True, substance_form='No information', remaining=None,
                                            shelf_life='01.01.1900', place='No information', supplier='No information'):
        structure.canonicalize()
        with db_session:
            if Molecule_Structure.exists(signature=bytes(structure)):
                print('That molecule is already in the database >:-(')
                return None

            molecule = Molecule(name=str(structure), organic_molecule=organic_molecule)
            Molecule_Structure(molecule=molecule, signature=bytes(structure))
            Molecule_Property(molecule=molecule, substance_form=substance_form, remaining=remaining, shelf_life=shelf_life)
            Storage(molecule=molecule, place=place, supplier=supplier)

    # Определяем функцию, обновляет информацию по имеющейся в базе данны молекуле
    def add_info(structure, organic_molecule=True, substance_form='No information', remaining=None,
                                            shelf_life='01.01.1900', place='No information', supplier='No information'):
        structure.canonicalize()
        with db_session:
            if Molecule_Structure.exists(signature=bytes(structure)):
                if input(f'Are you sure about that molecule: {structure}? y/n: ') == 'y':
                    molecule = Molecule.select(lambda m: m.name == str(structure))
                    molecule.organic_molecule = organic_molecule
                    Molecule_Property(molecule=[i.id for i in molecule][0], substance_form=substance_form, remaining=remaining, shelf_life=shelf_life)
                    Storage(molecule=[i.id for i in molecule][0], place=place, supplier=supplier)
                else: 
                    print("\nOkay :-(\n")
                    return None
            else:
                print("\nThat molecule doesn't exist in that database. For add new molecule, please, use add_molecule() function\n")
                return None        

class Molecule_Property(db.Entity):
    molecule = Required(Molecule)
    id = PrimaryKey(int, auto=True)  # Identification number of the property
    substance_form = Optional(str)
    remaining = Optional(Decimal)
    shelf_life = Optional(datetime, auto=True)

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

class Molecule_Structure(db.Entity):
    molecule = Required(Molecule)
    id = PrimaryKey(int, auto=True)  # Identification number of the structure
    signature = Required(bytes)
    bit_array = Optional(str)

    # Определяем функцию, которой передаём молекулу в каноничном виде и находим её в базе данных
    def find_molecule_in_database(any_molecule):
        
        with db_session:
            any_molecule.canonicalize()            
            results = select(molecule
                                for molecule in Molecule
                                for molecule_structure in molecule.structure
                                if molecule_structure.signature == bytes(any_molecule))
            return list(results)[0]

class Storage(db.Entity):
    molecule = Required(Molecule)
    id = PrimaryKey(int, auto=True)  # Identification number of the molecule storage rules
    storage_conditions = Optional(Json)
    place = Required(str)
    supplier = Optional(str)


db.bind('sqlite', 'moleculesDB.sqlite', create_db=True)
db.generate_mapping(create_tables=True)

data_molecules = []
with SDFRead('logBB.sdf') as f:
    data_molecules = [r for r in f]

Molecule.add_info(data_molecules[100], organic_molecule=False, substance_form='oil', remaining=None,
                                            shelf_life='01.01.1900', place='No information', supplier='No information')