import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("DELETE FROM balance_sheet")

items = [

("ASSETS","Current Assets","Cash and Cash Equivalents","25",0,0),
("ASSETS","Current Assets","Trade Receivables","24",0,0),
("ASSETS","Current Assets","Inventories","23",0,0),
("ASSETS","Current Assets","Other Current Assets","27",0,0),

("ASSETS","Non Current Assets","Property Plant & Equipment","13",0,0),
("ASSETS","Non Current Assets","Tangible Assets","14",0,0),
("ASSETS","Non Current Assets","Intangible Assets","15",0,0),

("EQUITY AND LIABILITIES","Shareholders Funds","Share Capital","1",0,0),
("EQUITY AND LIABILITIES","Shareholders Funds","Reserves and Surplus","2",0,0),

("EQUITY AND LIABILITIES","Current Liabilities","Trade Payables","10",0,0),
("EQUITY AND LIABILITIES","Current Liabilities","Short Term Borrowings","9",0,0),

("EQUITY AND LIABILITIES","Non Current Liabilities","Long Term Borrowings","5",0,0)

]

cursor.executemany("""

INSERT INTO balance_sheet(

section,
group_name,
item_name,
note_no,
current_amount,
previous_amount

)

VALUES(?,?,?,?,?,?)

""",items)

conn.commit()
conn.close()

print("Done")