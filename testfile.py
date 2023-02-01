from CGRdb.database import Molecule, Substance, db
from CGRdb.database.config import Config
from chython import RDFRead, ReactionContainer, SDFRead, smiles
from pony.orm import db_session
import sys
import zipfile
from CGRdb.tests import mol_queries

sys.modules[
    '__main__'].__file__ = None  # ad-hoc for disabling the Pony interactive mode.

db.bind(provider='postgres', user='postgres', host='localhost',
        password="example", database='test', port=5432)
db.generate_mapping(check_tables=False, create_tables=True)
# db.drop_all_tables(with_all_data=True)
# db.commit()
# db.disconnect()
# db.unbind()

with db_session():
    db.execute("Create extension if not exists intarray;")
    # Config(key="fingerprint",value={"min_radius":1, "max_radius":4, "length":2048,
    #              "number_active_bits":2, "number_bit_pairs":4})
    # Config(key="lsh_num_permute",value=64)
    # Config(key="lsh_threshold",value=0.7)

    # read one smiles from zip file and constract CGRtools.MoleculeContainer
    file = zipfile.ZipFile(
        "dataset/Chembl28.smi.zip")  # test dataset with molecules within the library
    line = next(file.open("Chembl28.smi")).decode().split()
    if len(line) >= 3 and line[1].startswith("|"):
        mol = smiles("".join([line[0], line[1]]))
    else:
        mol = smiles(line[0])

    print(f"\033[32mMolecule from Chembl28.smi.zip:\033[0m {mol}")
    print(f"\033[32mType of 'mol' variable:\033[0m {type(mol)}")

    file = zipfile.ZipFile(
        "dataset/USPTO.smi.zip")  # test dataset with reactions within the library
    line = next(file.open("USPTO.smi")).decode().split()
    if len(line) >= 3 and line[1].startswith("|"):
        reaction = smiles("".join([line[0], line[1]]))
    else:
        reaction = smiles(line[0])

    print(f"\033[32mReaction from USPTO.smi.zip:\033[0m {reaction}")

    m = Molecule.get(mol)
    idx = m.id
    print(f"\033[32midx = m.id:\033[0m {idx}")

    # Relation to the canonic structure
    m = Molecule.get(mol)  # get DB object by structure
    print(mol)
    can_structure = m.canonic_structure
    print()
    print(f"\033[32mMoleculeStructure of {m}:\033[0m {can_structure}")

    # lookup for the whole list of structures that corresponds to this molecule
    m = Molecule.get(mol)  # get DB object by structure
    structures = list(m.structures)
    print()
    print(f"\033[32mMoleculeStructures list of {m}:\033[0m {structures}")

    # take chython.MoleculeContainer object from DB
    m = Molecule.get(mol)
    structure = m.canonic_structure.structure
    print()
    print(f"\033[32mStructure of {m}:\033[0m {structure}")

    # alternative way of accessing the structures
    m = Molecule.get(mol)
    structure = list(m.structures)[0].structure
    print()
    print(f"\033[32mlist(m.structures)[0].structure:\033[0m {structure}")
    # structure is a chython.MoleculeContainer and provide all method of the Class

    # fingerprint of the Molecular Structure can be accessed as well as SMILES
    # (if user do not access the graph based representaion of molecule)
    m = Molecule.get(mol)
    fp = m.canonic_structure.fingerprint
    print()
    print(f"\033[32mfingerprint of the Molecular Structure can be accessed as well as SMILES:\033[0m {fp}")

    m = Molecule.get(mol)
    sm = m.canonic_structure.smiles
    print()
    print(f"\033[32mSMILES:\033[0m {sm}")

    # Also reverse relation can be seen
    m = Molecule.get(mol)
    moldb = m.canonic_structure.molecule
    print()
    print(f"\033[32mAlso reverse relation can be seen:\033[0m {moldb}")



    hexane = smiles("C1CCCCC1")
    print()
    print(f"\033[32mHexane molecule:\033[0m {hexane}")
    print(f"\033[32mType of 'hexane' variable:\033[0m {type(hexane)}")

    y = mol.union(hexane, remap=True)
    print(f"\033[32mLet's add solvent to our molecule and change map to have no collisions:\033[0m {y}")

    mol, hexane = y.split()
    print()
    print(f"\033[32mSeparate back molecules with proper mappings:\033[0m")
    print(f"\033[32m'mol' variable:\033[0m {mol}")
    print(f"\033[32mHexane molecule:\033[0m {hexane}")

    # Substance take list of tuples of molecules with their percentage in the compound.
    # If there is no information about ratio, None can be used.
    # for example we will add some n-hexane solvent and store the solution of previous molecule
    subs = [(mol, 0.2), (hexane, 0.8)]
    s = Substance(subs, name="AA000001")
    s = Substance[1]
    idx = s.id
    print()
    print(f"\033[32mId of substance with name AA000001:\033[0m {idx}")

    print()
    print(f"\033[32mShow name of the substance:\033[0m {s.name}")

    # accessing the stucture of substance
    s = Substance[idx]
    s_struct = s.structure
    print()
    print(f"\033[32mAccessing the stucture of substance:\033[0m {s_struct}")

    s = Substance[idx]
    component2, component1 = s.components  # components are either Molecules or NonOrganics
    print()
    print(f"\033[32mComponents are either Molecules or NonOrganics:\033[0m {component2, component1}")

    # accesing molar_fraction property
    print(f"""
\033[32mmolar_fraction of 1st mol,\033[0m {component1.molar_fraction}
\033[32mmolar_fraction of 2nd mol,\033[0m {component2.molar_fraction}
          """)

    # get individual structures of components
    s = Substance[idx]
    component2, component1 = s.components
    structure1 = component1.structure
    structure2 = component2.structure
    print(f"\033[32mGet individual structures of components:\033[0m")
    print(f"\033[32mStructure1:\033[0m {structure1}")
    print(f"\033[32mStructure2:\033[0m {structure2}")

    print()
    print()
    print(f"\033[32mSubstructure search of molecules:\033[0m")
    query = smiles(list(mol_queries.values())[2])
    print(f"\033[32mquery=smiles(list(mol_queries.values())[0]):\033[0m {query}")
    res = Molecule.substructures(query, ordered=True, request_only=False,
                                tanimoto_limit=None)
    print(f"\033[32mres=Molecule.substructures(query…):\033[0m {res}")
    a = next(res)  # result is Molecule obj, MoleculeStructure obj that contain query and Tanimoto score
    print(f"\033[32ma=next(res):\033[0m {a}")
    print(f"\033[32ma[1].structure:\033[0m {a[1].structure}")
    print(f"\033[32ma[0].canonic_structure.structure:\033[0m {a[0].canonic_structure.structure}")
    print(f"\033[32ma[2]:\033[0m {a[2]}")
    a = next(res)  # result is Molecule obj, MoleculeStructure obj that contain query and Tanimoto score
    print(f"\033[32ma=next(res):\033[0m {a}")
    print(f"\033[32ma[1].structure:\033[0m {a[1].structure}")
    print(f"\033[32ma[0].canonic_structure.structure:\033[0m {a[0].canonic_structure.structure}")
    print(f"\033[32ma[2]:\033[0m {a[2]}")
    a = next(res)  # result is Molecule obj, MoleculeStructure obj that contain query and Tanimoto score
    print(f"\033[32ma=next(res):\033[0m {a}")
    print(f"\033[32ma[1].structure:\033[0m {a[1].structure}")
    print(f"\033[32ma[0].canonic_structure.structure:\033[0m {a[0].canonic_structure.structure}")
    print(f"\033[32ma[2]:\033[0m {a[2]}")

    print()
    print()
    print(f"\033[32mSimilarity search of molecules:\033[0m")
    print(f"\033[32mquery=smiles(list(mol_queries.values())[0]):\033[0m {query}")
    res = Molecule.similars(query) # options and return is the same as substrcuture method
    print(f"\033[32mres=Molecule.similars(query):\033[0m {res}")
    a = next(res)
    print(f"\033[32ma=next(res):\033[0m {a}")
    print(f"\033[32mnext(res)[1].structure:\033[0m {a[1].structure}")
    print(f"\033[32mnext(res)[0].canonic_structure.structure:\033[0m {a[0].canonic_structure.structure}")
    print(f"\033[32mTanimoto:\033[0m {a[2]}")
    a = next(res)
    print(f"\033[32ma=next(res):\033[0m {a}")
    print(f"\033[32mnext(res)[1].structure:\033[0m {a[1].structure}")
    print(f"\033[32mnext(res)[0].canonic_structure.structure:\033[0m {a[0].canonic_structure.structure}")
    print(f"\033[32mTanimoto:\033[0m {a[2]}")
    a = next(res)
    print(f"\033[32ma=next(res):\033[0m {a}")
    print(f"\033[32mnext(res)[1].structure:\033[0m {a[1].structure}")
    print(f"\033[32mnext(res)[0].canonic_structure.structure:\033[0m {a[0].canonic_structure.structure}")
    print(f"\033[32mTanimoto:\033[0m {a[2]}")
    a = next(res)
    print(f"\033[32ma=next(res):\033[0m {a}")
    print(f"\033[32mnext(res)[1].structure:\033[0m {a[1].structure}")
    print(f"\033[32mnext(res)[0].canonic_structure.structure:\033[0m {a[0].canonic_structure.structure}")
    print(f"\033[32mTanimoto:\033[0m {a[2]}")

    # db.MoleculeProperties(db.Molecule[1], place='14', supplier='EkoPharm', substance_form='Powder', remaining='500.0', shelf_life='01.12.2023')
    # db.MoleculeProperties(db.Molecule[2], place='15', supplier='EkoPharm', substance_form='Gas', remaining='600.0', shelf_life='01.06.2023')
    # db.MoleculeProperties(db.Molecule[3], place='16', supplier='EkoPharm', substance_form='Powder', remaining='1000.0', shelf_life='01.10.2023')
    # db.MoleculeProperties(db.Molecule[4], place='17', supplier='EkoPharm', substance_form='Solution', remaining='500.0', shelf_life='01.12.2023')

    print()
    print(f"\033[32mТест работы метода upcoming_180_days():\033[0m {db.MoleculeProperties.upcoming_180_days()}")

    print()
    print(f"\033[32mТест работы метода molecules_before_date(yyyy, m, d):\033[0m {db.MoleculeProperties.molecules_before_date(2023, 11, 1)}")

    print()
    print(f"\033[32mТест работы метода find_form():\033[0m {db.MoleculeProperties.find_form('Solution')}")

    print()
    print(f"\033[32mТест работы метода less_than():\033[0m {db.MoleculeProperties.less_than(550)}")

    print()
    print(f"\033[32mТест работы метода molecule_description():\033[0m {db.MoleculeProperties[1].molecule_description}")

    # Тест изменения значения remaining в таблице
    # db.MoleculeProperties[1].remaining = '2000.0'

    # Тест работы метода add_info():
    # db.Molecule[1].add_info(substance_form='Solution', remaining=500.0, shelf_life='01.01.2023', place='17', supplier='EkoPharm')

    print()
    print(f"\033[32mТест работы метода description:\033[0m {db.Molecule[1].description}")
