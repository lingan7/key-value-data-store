import json
import os
import sys
import time
import threading


class data_store:

    def __init__(self, file_path=os.getcwd()):

        self.filepath = file_path + '/database.json'
        self.filelock = threading.Lock()
        self.datalock = threading.Lock()

        try:
            file = open(self.filepath, 'r')
            filedata = json.load(file)
            self.data = filedata
            file.close()

            if not self.handlesizecheck():
                raise Exception('Size exceeds 1 GB. Try again')

            print('Database opened in directory, ' + self.filepath)
        except:

            file = open(self.filepath, 'w')
            self.data = {}
            self.ttldict = {}
            file.close()
            print('Successfully created datastore in directory, ' + self.filepath)

        # checks if the database exists in the directory. If it does, the database is opened and built on.
        # otherwise, it just creates a new database.

    def handlesizecheck(self):

        # Checks if database size exceeds 1 GB size.

        self.filelock.acquire()

        if os.path.getsize(self.filepath) <= 1e+9:
            self.filelock.release()
            return True
        else:
            self.filelock.release()
            return False

    def handlekeyverification(self, key):

        # Checks if key meets required conditions of being a string and capped at 32 chars.

        if type(key) == type(""):
            if len(key) > 32:
                raise Exception(
                    'Trying to add more than 32 chars, Not Allowed!')
            else:
                return True
        else:
            raise Exception('Type of ' + str(type(key)) +
                            ' is not Accepted as a key. Try with a String')
            return False

    def create(self, key='', value='', ttl=None):

        self.handlekeyverification(key)

        if key == '':
            raise Exception('Unable to find a Key')

        if value == '':
            value = None

        # Checks if the size of the value exceeds 16 KB.
        if sys.getsizeof(value) > 16000:
            raise Exception("Oops!, You have exceeded the 16KB size limit.")

        if not self.handlesizecheck():
            raise Exception('Size exceeds 1 GB. Try again')

        self.datalock.acquire()
        if key in self.data.keys():
            self.datalock.release()
            raise Exception('Duplicate Key is not allowed.')

        # ttl = Time-To-Live. parameter ttl stores the time till which the data is allowed to read and delete.

        if ttl is not None:
            ttl = int(time.time()) + abs(int(ttl))

        tempdict = {'value': value, 'ttl': ttl}
        self.data[key] = tempdict

        self.filelock.acquire()
        json.dump(self.data, fp=open(self.filepath, 'w'), indent=2)

        self.filelock.release()
        self.datalock.release()

        print('Value added')

    def read(self, key=''):

        # Finds the key in the data store and displays the value, if the ttl has not crossed.

        self.handlekeyverification(key)

        if key == '':
            raise Exception('Key is Required')

        self.datalock.acquire()

        if key in self.data.keys():
            pass
        else:
            self.datalock.release()
            raise Exception('Key not found in datastore')

        ttl = self.data[key]['ttl']

        # Checks if ttl was provided.
        if not ttl:
            ttl = 0

        # if the ttl was crossed, an error is raised

        if (time.time() < ttl) or (ttl == 0):
            self.datalock.release()
            return json.dumps(self.data[key]['value'])

        else:
            self.datalock.release()
            print(self.data[key]['value'])
            raise Exception("Key's Time-To-Live has expired. Unable to read.")

    def delete(self, key=''):

        # Finds if the inputted key is present and if so, deletes it from the data store.

        self.handlekeyverification(key)

        if key == '':
            raise Exception('Expecting a key to be read.')

        self.datalock.acquire()

        if key in self.data.keys():
            pass
        else:
            self.datalock.release()
            raise Exception('Key not found in database')

        ttl = self.data[key]['ttl']

        # Checks if ttl was provided.
        if not ttl:
            ttl = 0

        if time.time() < ttl or (ttl == 0):

            self.data.pop(key)

            self.filelock.acquire()
            file = open(self.filepath, 'w')
            json.dump(self.data, file)

            self.filelock.release()
            self.datalock.release()

            print("Successfully deleted the Key-value pair")
            return
        else:
            self.datalock.release()
            raise Exception(
                "Sorry, Key's Time-To-Live has expired. Unable to delete.")

    def clearall(self):

        # Clears the database and the class's 'data' attribute.

        ch = input('Are you sure you want to clear the datastore? (y/n)')

        if ch == 'y':
            self.filelock.acquire()
            file1 = open(self.filepath, 'w')
            file1.close()
            print('Data cleared')
            self.filelock.release()

            self.datalock.acquire()
            self.data.clear()
            self.datalock.release()

        else:
            print('Data not cleared')

    def displayall(self):

        # Displays all the key-value pairs in the data store.
        self.datalock.acquire()

        if len(self.data.keys()) == 0:

            self.datalock.release()
            raise Exception("The Datastore you're trying to access is empty.")

        else:
            # Extracts the key-value pairs from the database

            data = list(self.data.items())
            data = dict([[key, values['value']] for key, values in data])
            self.datalock.release()

            print(data)
