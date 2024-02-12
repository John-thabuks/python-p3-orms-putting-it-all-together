import sqlite3

CONN = sqlite3.connect('lib/dogs.db')
CURSOR = CONN.cursor()

class Dog:

    #this is to hold all the list of tuples of rows
    all = []
    
    def __init__(self, name, breed):
        self.id = None
        self.name = name
        self.breed = breed

    #Classes are converted to tables hence this should be a classmethod
    @classmethod
    def create_table(cls):
        CURSOR.execute(
            """
                CREATE TABLE IF NOT EXISTS dogs(
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    breed TEXT
                )
            """            
        )

    #This will drop the table. Table is a class object in python
    @classmethod
    def drop_table(cls):
        CURSOR.execute(
            """
                DROP TABLE IF EXISTS dogs
            """
        )

    #Here we are inserting data to table 
    #Hence we are dealing with rows. so this is instance
    def save(self):
        sql = """
                INSERT INTO dogs (name, breed)
                VALUES (?,?)
            """
        
        CURSOR.execute(
            sql,
            (self.name, self.breed)
        )

        self.id = CURSOR.execute( "SELECT last_insert_rowid() FROM dogs").fetchone()[0]

    #rows in SQL are instances in python. 
    #So we can instantiate the Dog.create()
    @classmethod
    def create(cls, name, breed):
        dog = Dog(name, breed)
        dog.save()
        return dog
    
    #From raw data (row) in sql to python object (instance)
    #Then has to be classmethod
    @classmethod
    def new_from_db(cls, row):
        # #lets name our instance dog
        # dog = cls(row[1], row[2])
        # dog.id = row[0] #represents the entire sql row
        # return dog
        if row:
        # Create a new Dog instance from the database row
            dog = cls(row[1], row[2])
            dog.id = row[0]
            return dog
        else:
            # If row is None, return None
            return None


    #returns a list of Dog instances which are in a tuple
    #THen should be class
    @classmethod
    def get_all(cls):
        sql = """
                SELECT *
                FROM dogs
            """
        all_rows = CURSOR.execute(sql).fetchall()

        cls.all = [cls.new_from_db(row) for row in all_rows]

        return cls.all  #returns a list of Dog instances for every record in the database

    ##Rather than retur list of all instances, we return one Dog instance
    #This instance should correspond with name argument
    #so we use LIMIT and it classmethod
    @classmethod
    def find_by_name(cls, name):
        sql = """
                SELECT *
                FROM dogs
                WHERE name = ?
                LIMIT 1
            """
        
        dog = CURSOR.execute(sql, (name,)).fetchone()

        #Now we convert it into an object
        return cls.new_from_db(dog)
    
    @classmethod
    def find_by_id(cls, id):
        sql = """
                SELECT *
                FROM dogs
                WHERE id = ?
                LIMIT 1
            """
        dog = CURSOR.execute(sql, (id,)).fetchone()
        return cls.new_from_db(dog)
    

    @classmethod
    def find_or_create_by(cls, name, breed):
        sql = """
            SELECT * FROM dogs
            WHERE (name, breed) = (?, ?)
        """

        dog = CURSOR.execute(sql, (name, breed)).fetchone()
        if not dog:
            sql1 = """
                INSERT INTO dogs (name, breed)
                VALUES (?, ?)
            """

            CURSOR.execute(sql1, (name, breed))
            CONN.commit()
            return cls.find_by_name(name)  
        else:
            return cls.new_from_db(dog)  


    # def update(self):
    #     sql = """
    #         UPDATE dogs
    #         SET name = ?,
    #             breed = ?
    #         WHERE id = ?
    #     """

    #     CURSOR.execute(sql, (self.name, self.breed, self.id))
    #     CONN.commit()  
        
    def update(self):
        sql = """
            UPDATE dogs
            SET name = ?,
                breed = ?
            WHERE id = ?
        """

        CURSOR.execute(sql, (self.name, self.breed, self.id))
        CONN.commit()

        # After updating, we fetch the updated record from the database and return an instance
        updated_dog = self.find_by_id(self.id)
        self.name = updated_dog.name
        self.breed = updated_dog.breed
