from chython import SDFRead, RDFRead, SMILESRead
from chython.containers import ReactionContainer
from datetime import datetime, timedelta
from decimal import Decimal
from pickle import dumps, loads
from pony.orm import Database, PrimaryKey, Required, Set, Optional, Json, db_session


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
                        shelf_life='01.01.1900', place='No information', supplier='No information', canonical_structure='No information'):
        if Molecule_Structure.exists(signature=bytes(structure)):
            raise ValueError('That molecule is already in the database >:-(')
        db.Entity.__init__(self, name = str(structure), organic_molecule = organic_molecule)
        Molecule_Structure(molecule=self, signature=bytes(structure), data=structure, canonical_structure=canonical_structure)
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
    @staticmethod
    def find_molecule_in_db(any_molecule):
        result = Molecule_Structure.get(signature=bytes(any_molecule))
        if result:
            return result.molecule

    # Определяем метод, который обновляет информацию по имеющейся в базе данных молекуле
    def add_info(self, substance_form='No information', remaining=None,
                        shelf_life='01.01.1900', place='No information', supplier='No information'):
        Molecule_Property(molecule=self, substance_form=substance_form, remaining=remaining, shelf_life=shelf_life)
        Storage(molecule=self, place=place, supplier=supplier)

    # Метод, который возвращает все структуры одной молекулы
    @property
    def structures(self):
        return [structure for structure in self.structure]

    # Внутренняя функция, недоступная извне для двух последующих методов ниже
    def __find_reactions_by_molecule(cls, molecule, product):
        finding_mol = cls.find_molecule_in_db(molecule)
        if finding_mol:
            reactions = [i.reaction for i in finding_mol.reactions if i.molecule == finding_mol and i.product == product]
        return reactions

    # Метод, который возвращает все реакции, в которых передаваемая молекула является продуктом
    @classmethod
    def find_reactions_with_molecule_as_product(cls, molecule):
        return cls.__find_reactions_by_molecule(molecule, product=True)

    # Метод, который возвращает все реакции, в которых передаваемая молекула является реактантом
    @classmethod
    def find_reactions_with_molecule_as_reactant(cls, molecule):
        return cls.__find_reactions_by_molecule(molecule, product=False)

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
        return [x.molecule for x in cls.select(lambda p: p.shelf_life < datetime.today() + timedelta(days=180))]

    # Определяем метод, который принимает дату и выводит молекулы до этой даты
    @classmethod
    def molecules_before_date(cls, year, month, day):
        return [x.molecule for x in cls.select(lambda p: p.shelf_life < datetime(year, month, day))]      

    # Определяем метод, который вернёт все молекулы определённой формы
    @classmethod
    def find_form(cls, subst_form):
        return [x.molecule for x in cls.select(lambda p: p.substance_form == subst_form)]
    
    # Определяем метод, который вернёт все молекулы меньше определённого порога по весу
    @classmethod
    def less_than(cls, remain):
        return [x.molecule for x in cls.select(lambda p: p.remaining < remain)]
     
     # Определяем метод, который вернёт полное описание молекулы
    @property
    def molecule_description(self):
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
    canonical_structure = Optional(str)

    def __init__(self, molecule, data, signature, canonical_structure):
        data = dumps(data)
        db.Entity.__init__(self, molecule=molecule, signature=signature, data=data, canonical_structure=canonical_structure)

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
        if not isinstance(structure, ReactionContainer):
            raise ValueError('It is not a reaction >:-(')
        if ReactionIndex.exists(signature=bytes(~structure)):
            raise ValueError('That reaction is already in the database >:-(')
        if not structure.reactants:
            raise ValueError('That reaction have no any reactants >:-(')
        if not structure.products:
            raise ValueError('That reaction have no any products >:-(')
        reactants=structure.reactants
        products=structure.products
        db.Entity.__init__(self)
        for structures,p in ((products, True), (reactants, False)):
            for m in structures:
                mol = Molecule.find_molecule_in_db(m)
                if mol:
                    MoleculeReaction(reaction=self, molecule=mol, product=p)
                else:
                    mol = Molecule(m)
                    MoleculeReaction(reaction=self, molecule=mol, product=p)
        ReactionIndex(reaction=self, signature=bytes(~structure))

     # Определяем метод, в который передаём реакцию и находим её объект в базе данных
    @staticmethod
    def find_reaction_in_db(any_reaction):
        result = ReactionIndex.get(signature=bytes(~any_reaction))
        if result:
            return result.reaction

    # Метод получает объект класса Reaction и возвращает ReactionContainer этого класса
    @property
    def structure(self):
        res_1 = [(i.molecule._structure, i.product) for i in self.molecules]
        print(res_1)
        print(self.molecules)
        list_of_products = [i[0] for i in res_1 if i[1] == True]
        list_of_reactants = [i[0] for i in res_1 if i[1] == False]
        return ReactionContainer(reactants=list_of_reactants, products=list_of_products)

class MoleculeReaction(db.Entity):
    id = PrimaryKey(int, auto=True)
    reaction = Required(Reaction)
    molecule = Required(Molecule)
    product = Optional(bool)

class ReactionIndex(db.Entity):
    id = PrimaryKey(int, auto=True)
    reaction = Required(Reaction)
    signature = Optional(bytes)
    bit_array = Optional(str)

db.bind('sqlite', 'moleculesDB.sqlite', create_db=True)
db.generate_mapping(create_tables=True)