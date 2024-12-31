#!/usr/bin/env python3

from utils import *

class UserReportBuilder:
    TEMPLATE_FILENAME = 'gastro-report-template.xlsx'
    TEMPLATE_PATH = join(dirname(__file__), TEMPLATE_FILENAME)
    TEMPLATE_SHEET_TITLE = 'Šablóna'
    SHEET_TITLE_FORMAT = 'Hárok{}'
    FOREIGN_ABSENCE_DESCRIPTION = 'Zahraničná pracovná cesta'
    DOMESTIC_ABSENCE_DESCRIPTION = 'Tuzemská pracovná cesta'
    
    def __init__(self, data):
        self.year = data['year']
        self.month = data['month']
        self.month_sk = data['month_sk']
        self.employees = data['employees']
        self.public_holidays = index_by('day', data['public_holidays'])
        self.absences = dict(
            (eid, index_by('day', eabs))
            for (eid, eabs) in index_by('user_id', data['absences']).items()
        )
        self.holidays_budget = dict(
            (eid, index_by('year', yr))
            for (eid, yr) in index_by('user_id', data['holidays_budget']).items()
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
            ws.cell(row=currentRow, column=5).value = self.getBudget(employee.get('id'), self.year)
            ws.cell(row=currentRow, column=6).value = self.getSubtrahend(employee.get('id'))
            ws.cell(row=currentRow, column=7).value = self.getDiff(ws, currentRow)
            ws.cell(row=currentRow, column=8).value = self.getNote(employee.get('id'))
        
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

    def getBudget(self, employeeID, year):
        try:
            return float(self.holidays_budget.get(employeeID, {}).get(year, {})[0].get('num'))
        except (IndexError, KeyError, TypeError, ValueError):
            return 0.00
    
    def getSubtrahend(self, employeeID):
        absences = self.absences.get(employeeID, {})
        if not absences:
            return 0.00
        
        absenceDays = set(absences.keys())
        holidayDays = set(self.public_holidays.keys())
        if not holidayDays:
            return float(len(absenceDays))

        return float(len(absenceDays) - len(holidayDays))
    
    def getDiff(self, ws, row):
        return ws.cell(row=row, column=5).value - ws.cell(row=row, column=6).value

    def getNote(self, employeeID):
        absences = self.absences.get(employeeID, {})
        if not absences:
            return ''

        # at most one absence per day
        descriptions = {absence[0]['description'] for absence in absences.values()}

        note = list()
        if self.FOREIGN_ABSENCE_DESCRIPTION in descriptions:
            note.append('zpc')
        if self.DOMESTIC_ABSENCE_DESCRIPTION in descriptions:
            note.append('tpc')

        return ', '.join(note)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.stderr.write(
            "Usage: {} output-workbook.xlsx\n"
            .format(sys.argv[0])
        )
        exit(1)
    data = json.load(sys.stdin)
    UserReportBuilder(data).build(sys.argv[1])
