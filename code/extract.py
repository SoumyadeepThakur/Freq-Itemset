import xlrd, json
from sets import Set
#----------------------------------------------------------------------
def extract_data(path):
    """
    Open and read an Excel file
    """ 
    book = xlrd.open_workbook(path)
    # get the first worksheet
    first_sheet = book.sheet_by_index(0)
    # read col
    lines = first_sheet.col_values(1)
    data = dict()
    itemlist=list()
    data['students'] = []
    row = first_sheet.row_slice(rowx=1, start_colx=0, end_colx=8)
    invoice=row[0].value
    epoch=date=row[4].value
    itemset={str(row[1].value)}
    for i in range(len(lines)-1):
        print(i)
        row = first_sheet.row_slice(rowx=(i+1), start_colx=0, end_colx=8)
        itemset = itemset | {str(row[1].value)}
        if invoice == row[0].value:
            itemlist.append(row[1].value)
        else:
            data['students'].append({'Invoice': invoice, 'Items': itemlist, 'Date':date})
            invoice=row[0].value
            itemlist=list()
            itemlist.append(row[1].value)
            date=row[4].value

    print ("hello")
    print (len(itemset))
    with open ("items.txt",'w') as outfile:
        outfile.writelines(["%s\n" %item for item in itemset])
    outfile.close() 
    data['students'].append({'Invoice': invoice, 'Items': itemlist, 'Date':date})
    return data['students']
#----------------------------------------------------------------------
if __name__ == "__main__":
    path = "Online-Retail.xlsx"
    print(path)
    student_dict = extract_data(path)
    with open ('trans_data.json', 'w') as outfile:
        json.dump(student_dict,outfile)
    outfile.close()