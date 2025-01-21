#!/usr/bin/env python3

from utils import *

class UserReportBuilder:
    TEMPLATE_FILENAME = 'gastro-report-template.xlsx'
    TEMPLATE_PATH = join(dirname(__file__), TEMPLATE_FILENAME)
    TEMPLATE_SHEET_TITLE = 'Šablóna'
    SHEET_TITLE_FORMAT = 'Hárok{}'
    DEPARTMENT = '107240-KAI'
    FOREIGN_ABSENCE_DESCRIPTION = 'Zahraničná pracovná cesta'
    DOMESTIC_ABSENCE_DESCRIPTION = 'Tuzemská pracovná cesta'
    SICK_LEAVE = 1
    BUSINESS_TRIP = 2
    TIME_FORMAT = '%H:%M:%S'
    LEAVE_AFTER = datetime.strptime('13:00:00', TIME_FORMAT)
    ARRIVE_BEFORE = datetime.strptime('11:00:00', TIME_FORMAT)
    
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
        self.workDays = self.getNumberOfWorkDays()
        
    def build(self, outputPath):
        wb = openpyxl.load_workbook(self.TEMPLATE_PATH)
        ws = wb.active
        
        self.fillHeader(ws)
        lastRow = self.fillEmployeeData(ws)
        self.fillTotals(ws, lastRow)
        
        wb.save(outputPath)

    def fillHeader(self, ws):
        ws['B1'] = self.DEPARTMENT
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
            ws.cell(row=currentRow, column=5).value = self.workDays
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


    def getNumberOfWorkDays(self):
        workDays = 0
        for date in getDates(self.year, self.month):
            if date.month != self.month:
                continue
            if isWeekend(date) or date in self.public_holidays:
                continue

            workDays += 1

        return workDays
    
    def getSubtrahend(self, employeeID):
        count = 0.00
        absences = self.absences.get(employeeID, {})
        if not absences:
            return count
        
        absenceDays = set(absences.keys())
        holidayDays = set(self.public_holidays.keys())
        
        for day in absenceDays:   
            if isWeekend(getDate(self.year, self.month, day)):
                continue

            if not holidayDays or day not in holidayDays:
                if absences.get(day)[0]['type'] == self.SICK_LEAVE or absences.get(day)[0]['type'] == self.BUSINESS_TRIP:
                    count += 1.00
                if absences.get(day)[0]['type'] == self.BUSINESS_TRIP:
                    fromTime = datetime.strptime(absences.get(day)[0]['from_time'], self.TIME_FORMAT)
                    toTime = datetime.strptime(absences.get(day)[0]['to_time'], self.TIME_FORMAT)
                    if fromTime >= self.LEAVE_AFTER or toTime <= self.ARRIVE_BEFORE:
                        count = max(0, count - 1.00)

        return count
    
    def getDiff(self, ws, row):
        return ws.cell(row=row, column=5).value - ws.cell(row=row, column=6).value

    def getNote(self, employeeID):
        absences = self.absences.get(employeeID, {})
        if not absences:
            return ''

        # at most one absence per day
        descriptions = {absence[0]['description'] for absence in absences.values()}

        note = list()
        countDomesticBusinessTrips = 0
        for description in descriptions:
            if self.DOMESTIC_ABSENCE_DESCRIPTION in description:
                countDomesticBusinessTrips += 1
        
        if countDomesticBusinessTrips > 0:
            note.append(f'zpc {countDomesticBusinessTrips}')

        countForeignBusinessTrips = 0
        for description in descriptions:
            if self.FOREIGN_ABSENCE_DESCRIPTION in description:
                countDomesticBusinessTrips += 1

        if countForeignBusinessTrips > 0:
            note.append(f'zpc {countForeignBusinessTrips}')

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
