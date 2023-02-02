from project_database import *

# Определяем функцию, добавляющую в базу данных первые 10 молекул из любого файла с расширением .sdf
# def add_first_10_mols_from_sdf(file):

#     data_molecules = []
#     with SDFRead(file) as f:
#         data_molecules = [r for r in f]

#     with db_session:
#         number_of_molecule = 1
#         for i in data_molecules[:10]:
#             i.canonicalize()
#             if Molecule_Structure.exists(signature=bytes(i)):
#                 print(f'Molecule number {number_of_molecule} already in the database')
#             else:
#                 molecule = Molecule(name=str(i), organic_molecule = True)
#                 Molecule_Structure(molecule=molecule, signature=bytes(i))
#             number_of_molecule += 1

# Вызываем функцию и добавляем первые 10 молекул из файла
# add_first_10_mols_from_sdf('logBB.sdf')

# @db_session
# Добавляем 5 условных молекул в базу данных
# def add_molecules():

#     Benzene = Molecule(name='Benzene', organic_molecule = True)
#     Phenol = Molecule(name='Phenol', organic_molecule = True)
#     Copper_sulfate = Molecule(name='Copper_sulfate', organic_molecule = False)  
#     Silver_nitrate = Molecule(name='Silver_nitrate', organic_molecule = False)
#     Silver_sulfate = Molecule(name='Silver_sulfate', organic_molecule = False)

#     Molecule_Property(molecule=Benzene, substance_form='liquid', remaining='50.8', shelf_life='01.06.2023')
#     Molecule_Property(molecule=Phenol, substance_form='liquid', remaining='65.3', shelf_life='01.05.2023')
#     Molecule_Property(molecule=Copper_sulfate, substance_form='powder', remaining='40.4', shelf_life='01.04.2023')
#     Molecule_Property(molecule=Silver_nitrate, substance_form='powder', remaining='91.2', shelf_life='01.03.2023')
#     Molecule_Property(molecule=Silver_sulfate, substance_form='powder', remaining='101.2', shelf_life='01.02.2023')

#     Storage(molecule=Benzene, place='1', supplier='Supplier1')
#     Storage(molecule=Phenol, place='2', supplier='Supplier2')
#     Storage(molecule=Copper_sulfate, place='11', supplier='Supplier3')
#     Storage(molecule=Silver_nitrate, place='11', supplier='Supplier4')
#     Storage(molecule=Silver_sulfate, place='12', supplier='Supplier5')

# Вызов функции с отправкой 5 условных молекул в базу данных
# add_molecules()

# Тренируемся в запросах в базу данных
# with db_session:
#     query_molecule = Molecule.select(lambda m: m.id >= 2 and m.id < 4) # Получаем и сохраняем молекулы с id >= 2 и id < 4
#     print(list(query_molecule)) # Распечатываем в виде списка
#     print([m.name for m in query_molecule]) # Распечатываем атрибут name

#     print()

#     query_molecule_propertie = Molecule_Property.select(lambda i: i.id in [1, 2, 3, 4]) # Получаем и сохраняем свойства молекул с id 1, 2, 3, 4
#     print(list(query_molecule_propertie)) # Распечатываем в виде списка

#     print()

#     query_storage = Storage.select(lambda i: i.id in [1, 2, 3, 4]) # Получаем и сохраняем порядок хранения молекул с id 1, 2, 3, 4
#     print(list(query_storage)) # Распечатываем в виде списка

#     print()

#     query_all_molecules = Molecule.select() # Получаем и сохраняем всю информацию по молекулам
#     # Получаем и сохраняем в словарь, где ключ - id молекулы, а значение - tuple с названием молекулы и указанием того, что молекула inorganic. id > 2
#     not_tuple_molecules = {m.id: (m.name, {'inorganic: ': m.organic_molecule}) for m in query_all_molecules if m.id > 2 and not m.organic_molecule}
#     print(not_tuple_molecules) # Распечатываем

#     print()
    
#     # Получаем и сохраняем в словарь все сульфаты, где ключ - id молекулы, а значение - string с названием молекулы
#     all_sulfates = {m.id: m.name for m in query_all_molecules if not m.organic_molecule and 'sulfate' in m.name}
#     print(all_sulfates)

#     print()

#     # Получаем и сохраняем все порошочки
#     result = select((molecule, molecule_propertie.substance_form)
#                             for molecule in Molecule
#                             for molecule_propertie in molecule.property
#                             if molecule.id > 2)[:]
#     print(result)

#     print()

#     # Получаем и сохраняем всё на 11 полочке
#     polo4ka = select((molecule, storage.place)
#                             for molecule in Molecule
#                             for storage in molecule.storage
#                             if storage.place == '11')[:]
#     print(polo4ka)

#     print()

#     # Получаем и сохраняем все порошочки на 11 полочке
#     powder_and_polo4ka = select((f'Молекула: {molecule.name}', f'Полочка №: {storage.place}', f'Форма: {property.substance_form}')
#                                     for molecule in Molecule
#                                     for storage in molecule.storage
#                                     for property in molecule.property
#                                     if storage.place == '11' and property.substance_form == 'powder')[:]
#     print(*powder_and_polo4ka, sep='\n')

#     print()
    
#     # Получаем и сохраняем в словарь все порошочки на 11 полочке
#     powder_polo4ka_dict = {molecule.id: [{'Полочка №': storage.place}, {'Форма': property.substance_form}]
#                             for molecule in Molecule.select()
#                             for storage in molecule.storage
#                             for property in molecule.property}
#     print(powder_polo4ka_dict)

#     print()

#     # Получаем и сохраняем в списочки все порошочки на 11 полочке
#     powder_and_polo4ka = {molecule.id: [storage.place, property.substance_form]
#                             for molecule in Molecule.select()
#                             for storage in molecule.storage
#                             for property in molecule.property}
#     print(powder_and_polo4ka)

# print()

# # Все порошочки на 11 полочке (Плохой код. На самом деле возвращает все молекулы на 11 полке)
# # for key in powder_polo4ka_dict:
# #     for item_molecule in powder_polo4ka_dict[key]:
# #         for key_props in item_molecule:
# #             for item_molecule_propertie in item_molecule[key_props].split():
# #                 print(item_molecule_propertie)
# #                 if item_molecule_propertie == '11':
# #                     print('id:', key, '-->', powder_polo4ka_dict[key])


# # Получаем id всех порошков на 11 полочке
# # Сначала собираем во множество всё, что на 11 полочке
# polo4ki = [key for key in powder_polo4ka_dict
#                for item in powder_polo4ka_dict[key]
#                if '11' in item.values()]
# polo4ki = set(polo4ki)
# print(polo4ki)
# # Затем собираем во список все порошки
# powders = [key for key in powder_polo4ka_dict
#                 for item in powder_polo4ka_dict[key]
#                 if 'powder' in item.values()]
# print(powders)
# # Ловим пересечения множества и списка
# res = polo4ki.intersection(powders)
# print(res)

# print()

# # Получаем айдишники всех порошков на 11 полочке
# polo4ki = [key for key in powder_polo4ka_dict
#                 for item in powder_polo4ka_dict[key]
#                 if 'powder' and '11' in item.values()]
# print(polo4ki)





data_molecules = []
with SDFRead('logBB.sdf') as f:
    data_molecules = [r for r in f]

data_reactions = []
with RDFRead('example.rdf') as f:
    data_reactions = [r for r in f]
reaction = next(SMILESRead('untitled.txt'))

reaction_bug = ReactionContainer(reaction.products, [])
product_of_reaction = reaction.products
reactant_of_reaction = reaction.reactants

with db_session:
    # Тест работы метода find_molecule_in_db()
    # print(Molecule.find_molecule_in_db(data_molecules[5]))

    # Добавить молекулу из logBB.sdf
    # db.Molecule(data_molecules[5], organic_molecule=True, substance_form='Powder', remaining='480',
    #                     shelf_life='01.05.2023', place='18', supplier='EcoPharm', canonical_structure='No')

    # db.Molecule[1].add_info(substance_form='Solution', remaining=500.0, shelf_life='01.01.2023')
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
    # print(Molecule_Property.less_than(499))

    # Тест добавления реакции в базу
    # db.Reaction(reaction)

    # Тест проверки наличия реакции в базе
    # print(Reaction.find_reaction_in_db(reaction))

    # Тест проверки работы метода Reaction.structure()
    # print(db.Reaction[1].structure)

    # Скрипт для добавления ещё одной структуры к уже имеющейся молекуле
    # Molecule_Structure(molecule=Molecule.get(id=1), signature=bytes(data_molecules[3].canonicalize()), data=data_molecules[3].canonicalize(), canonical_structure='Yes')

    # Тест работы метода structures
    # print(db.Molecule[1].structures)

    # Тест работы метода find_reactions_with_molecule_as_product():
    # print(Molecule.find_reactions_with_molecule_as_product(product_of_reaction[0]))

    # Тест работы метода find_reactions_with_molecule_as_reactant():
    print(Molecule.find_reactions_with_molecule_as_reactant(reactant_of_reaction[0]))
