import datetime#For getting system date and time.
import csv, sqlite3#For performing operation for CSV files and SQlite3 database
import os.path#For file operation

#For sending attachment mail from gmail
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

#Function to get all image files from a directory in a list
def get_picture_list(rel_path):
    abs_path = os.path.join(os.getcwd(),rel_path)
    #print('abs_path =', abs_path)
    dir_files = os.listdir(abs_path)
    #print(dir_files)
    return dir_files

picture_list = get_picture_list('pictures')
# print(picture_list)

###Calculating Today's Date
now=datetime.datetime.now()
curr_date_time=now.strftime("%d-%m-%Y")
current_day, current_month, current_year=curr_date_time.split("-")

con = sqlite3.connect(":memory:")#It creates database on RAM, everytime it flush the database and create.
##Creating a "Shop.db" Database
# db_is_new = not os.path.exists("Shop.db")
# con = sqlite3.connect("Shop.db")
cur = con.cursor()

#### Creating Customer table from Customer.csv file.
cur.execute('''CREATE TABLE if not exists Customer(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    NAME TEXT,
    AGE TEXT,
    ADDRESS TEXT,
    DOB DATE,
    EMAIL TEXT,
    PICTURE BLOB);''')  # use your column names here

#Inserting data into database customer table from csv file.
with open('New_Customer.csv','r') as fin: # `with` statement available in 2.5+
# csv.DictReader uses first line in file for column headings by default
    dr = csv.DictReader(fin) # comma is default delimiter
    to_db = [(i['ID'], i['NAME'],i['AGE'], i['ADDRESS'], i['DOB'], i['EMAIL']) for i in dr]#Column names are exactly same as in csv files.
cur.executemany("INSERT INTO Customer (ID, NAME, AGE, ADDRESS, DOB, EMAIL) VALUES (?, ?, ?, ?, ?, ?);", to_db)
con.commit()

#Fetching all customer's name to insert their photos into database customer table.
sql = "SELECT NAME FROM Customer"
cur.execute(sql)
records = cur.fetchall()

#Matched photo's name with cutomer's name from picture directory, and update into Customer table.
for data_record in records:
    for pict_rec in picture_list:
        pic_name,ext=pict_rec.split('.')
        if data_record[0]==pic_name:
            picture_file = "./pictures/" + pict_rec
            # print("inserting : ",picture_file)
            with open(picture_file, 'rb') as input_file:
                ablob = input_file.read()
                sql = 'UPDATE Customer SET PICTURE = ? WHERE NAME = ?;'
                con.execute(sql,(sqlite3.Binary(ablob), data_record[0]))
                con.commit()

## For accessing row data using column names
with con:
    con.row_factory = sqlite3.Row
cur = con.cursor()

##Writing Image file from database's Customer table.
sql="SELECT * FROM Customer"
cur.execute(sql)
records = cur.fetchall()
for record in records:
    # print("ID:{}, NAME:{}, AGE:{}, ADDRESS:{}, DOB:{}, DESIGNATION:{}, SALARY:{} ,PICTURE:{}".format(record[0],record[1],record[2],record[3],record[4],record[5],record[6],record[7]))
    # cust_name, ablob = record[1], record[-1]
    cust_name, ablob = record["NAME"], record["PICTURE"]
    filename = cust_name+".jpeg"
    with open(filename, 'wb') as output_file:
        output_file.write(ablob)
    output_file.close

    ###Condition for filtering Person's birthday Today.
    dob_d, dob_m, dob_y = record["DOB"].split("-")
    if (dob_d == current_day and dob_m == current_month):
        ##print("Hi {}, wishing you many many happy returns of the day God bless you !!!".format(record["NAME"]))

        ###Sending Birthday wishing mail.
        ###Instruction link to generate 16-digit mail app password:-> https://support.google.com/accounts/answer/185833
        fromaddr = "krishna1gupta@gmail.com"
        toaddr = record["EMAIL"]

        # instance of MIMEMultipart
        msg = MIMEMultipart()

        # storing the senders email address
        msg['From'] = fromaddr

        # storing the receivers email address
        msg['To'] = toaddr

        # storing the subject
        msg['Subject'] = "Birthday Greetings !!!"

        # string to store the body of the mail
        body = "Hi {}, wishing you many many happy returns of the day God bless you !!!".format(record["NAME"])

        # attach the body with the msg instance
        msg.attach(MIMEText(body, 'plain'))

        # open the file to be sent
        filename = record["NAME"]+".jpeg"
        attachment = open(filename, "rb")

        # instance of MIMEBase and named as p
        p = MIMEBase('application', 'octet-stream')

        # To change the payload into encoded form
        p.set_payload((attachment).read())

        # encode into base64
        encoders.encode_base64(p)

        p.add_header('Content-Disposition', "attachment; filename= %s" % filename)

        # attach the instance 'p' to instance 'msg'
        msg.attach(p)

        # creates SMTP session
        s = smtplib.SMTP('smtp.gmail.com', 587)

        # start TLS for security
        s.starttls()

        # Authentication
        s.login(fromaddr, "your 16-digit mail app password")

        # Converts the Multipart msg into a string
        text = msg.as_string()

        # sending the mail
        s.sendmail(fromaddr, toaddr, text)

        # terminating the session
        s.quit()