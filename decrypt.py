import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import pyodbc as cnn
import pandas as pd
import credentials as cd

#Establish connection to SQL database. Replace credentials with your own
cnxn = cnn.connect('DRIVER={SQL Server};SERVER='+cd.server+';DATABASE='+cd.database+';UID='+cd.userid+';PWD='+cd.password)

#Query for bank account numbers
sql = pd.read_sql_query('SELECT acctrefno, account_number from loanacct_ach', cnxn)

#Query for TINs
sql1 = pd.read_sql_query('SELECT cifno, tin from cif where tin is not null and tin <> \'\'', cnxn)

#function to decode a single account number. Enter your encryption key
def decode(acctrefno):
    key = '#'.encode('utf-8')
    cursor = cnxn.cursor()
    enc_account_number = cursor.execute('select account_number from loanacct_ach where acctrefno = \''+acctrefno+'\'').fetchone()[0]
    iv = enc_account_number[9:25].encode('utf-8')
    enc = enc_account_number[34:].encode('utf-8')
    DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e))
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decoded = DecodeAES(cipher, enc)
    paddingbytes = decoded[-2]
    return decoded[:-paddingbytes].decode('utf-8')

#Enter your encryption key. 
key = '#'.encode('utf-8')
decode= []

#Run the specified query and replace the column with decoded bank account numbers
for i in range(len(sql)):
    iv = (sql.iloc[i]['account_number'][9:25]).encode('utf-8')
    enc = (sql.iloc[i]['account_number'][34:]).encode('utf-8')
    DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e))
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decoded = DecodeAES(cipher, enc)
    paddingbytes = decoded[-2]
    decode.append(decoded[:-paddingbytes])
    
sql['decoded'] = decode

key = '#'.encode('utf-8')
decode= []

#Run the specified query and replace the column with decoded TINs
for i in range(len(sql1)):
    iv = (sql1.iloc[i]['tin'][9:25]).encode('utf-8')
    enc = (sql1.iloc[i]['tin'][34:]).encode('utf-8')
    DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e))
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decoded = DecodeAES(cipher, enc)
    paddingbytes = decoded[-2]
    decode.append(decoded[:-paddingbytes].decode('utf-8'))
    
sql1['tin'] = decode
