class Molecule:


    def __init__(self, id, name, structure):
        self.id = id
        self.name = name
        self.structure = structure

    def PrintAttributes(self):
        print('ID:', self.id)
        print('Name of molecule:', self.name)
        print('SMILES:', self.structure)

    def __str__(self):
        return f"{self.name}, {self.structure}"

benzene = Molecule(1, 'benzene', 'cccccc')

benzene.PrintAttributes()

print(str(benzene))

