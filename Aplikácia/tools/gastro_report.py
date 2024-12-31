#!/usr/bin/env python3

from monthly_report import *
from copy import copy

class UserReportBuilder:
    TEMPLATE_FILENAME = 'gastro-report-template.xlsx'
    TEMPLATE_PATH = join(dirname(__file__), TEMPLATE_FILENAME)
    TEMPLATE_SHEET_TITLE = 'Šablóna'
    SHEET_TITLE_FORMAT = 'Hárok{}'
    
    def __init__(self, data):
        self.year = data['year']
        self.month = data['month']
        self.month_sk = data['month_sk']
        self.personal_id_prefix = data['personal_id_prefix']
        self.employees = data['employees']
        self.public_holidays = index_by('day', data['public_holidays'])
        self.absences = dict((eid, index_by('day', eabs))
            for (eid, eabs) in index_by('user_id', data['absences']).items()
        )
        self.holidays_budget = dict((eid, index_by('year', eabs))
            for (eid, eabs) in index_by('user_id', data['holidays_budget']).items()
        )
        
    def build(self, outputPath):
        wb = openpyxl.load_workbook(self.TEMPLATE_PATH)
        ws = wb.active
        
        self.fillHeader(ws)
        lastRow = self.fillEmployeeData(ws)
        self.fillTotals(ws, lastRow)
        
        wb.save(outputPath)

    def fillHeader(self, ws):
        ws['B1'] = '107240-KAI'
        ws['B3'] = f"Obdobie: {self.month_sk} {self.year}"
    
    def fillEmployeeData(self, ws):
        templateRow = 4
        self.insertRows(ws, templateRow, len(self.employees) - 1)

        for i, employee in enumerate(self.employees):
            currentRow = templateRow + i
            ws.cell(row=currentRow, column=1).value = i + 1
            ws.cell(row=currentRow, column=2).value = employee.get('personal_id')
            ws.cell(row=currentRow, column=3).value = employee.get('surname')
            ws.cell(row=currentRow, column=4).value = employee.get('name')
            ws.cell(row=currentRow, column=5).value = 0
            ws.cell(row=currentRow, column=6).value = 0.00
            ws.cell(row=currentRow, column=7).value = 0
            ws.cell(row=currentRow, column=8).value = ''
            #ws.cell(row=currentRow, column=5).value = self.getBudget(employee.get('user_id'), self.year)
            #ws.cell(row=currentRow, column=6).value = self.getSub(employee.get('user_id'))
            #ws.cell(row=currentRow, column=7).value = ws.cell(row=currentRow, column=5).value - ws.cell(row=currentRow, column=6).value
            #ws.cell(row=currentRow, column=8).value = self.getNote(employee.get('user_id'))
        
        return templateRow + len(self.employees) - 1


    def fillTotals(self, ws, lastRow):
        totalsRow = lastRow + 3

        narok = f'=SUM(E4:E{lastRow})'
        zaloha = f'=SUM(G4:G{lastRow})'

        ws.cell(totalsRow, 5).value = narok
        ws.cell(totalsRow, 7).value = zaloha


    def insertRows(self, ws, insertRow, numRows):
        mergedRanges = list(ws.merged_cells.ranges)
        
        for mergedRange in mergedRanges:
            ws.unmerge_cells(str(mergedRange))
        
        ws.insert_rows(insertRow + 1, numRows)
        for i in range(1, numRows + 1):
            ws.row_dimensions[insertRow + i].height = ws.row_dimensions[insertRow].height
            for cell in ws[insertRow]:
                newCell = ws.cell(row=insertRow + i, column=cell.column)
                newCell._style = copy(cell._style)
        
        for mergedRange in mergedRanges:
            if mergedRange.min_row >= insertRow:
                ws.merge_cells(
                    start_row=mergedRange.min_row + numRows,
                    start_column=mergedRange.min_col,
                    end_row=mergedRange.max_row + numRows,
                    end_column=mergedRange.max_col
                )
            else:
                ws.merge_cells(str(mergedRange))

    def getBudget(self, employee_id, year):
        return self.holidays_budget[employee_id].get(year, 0)
    
    def getSub(self, employee_id):
        pass

    def getNote(self, employee_id):
        pass

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.stderr.write(
            "Usage: {} output-workbook.xlsx\n"
            .format(sys.argv[0])
        )
        exit(1)
    data = json.load(sys.stdin)
    UserReportBuilder(data).build(sys.argv[1])
