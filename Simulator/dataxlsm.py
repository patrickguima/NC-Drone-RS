
import xlsxwriter
import statistics
def write_xlsm(metrics,target_results):


    workbook = xlsxwriter.Workbook('results.xlsx')
    worksheet = workbook.add_worksheet()

# Some data we want to write to the worksheet.
    expenses = (
        ['Drone', 'num_target_founds', 'interval_found', 'num_recharges','interval_recharges','manouvers','target_was_found','interval_found'],

    )
    row = 0
    col = 0
# Iterate over the data and write it out row by row.
    for num, qmi,sdf,ncc,ntm,mano,targ,ti in (expenses):
        worksheet.write(row, col,     num)
        worksheet.write(row, col + 1, qmi)
        worksheet.write(row, col + 2, sdf)
        worksheet.write(row, col + 3, ncc)
        worksheet.write(row, col + 4, ntm)
        worksheet.write(row, col + 5, mano)
        worksheet.write(row, col + 6, targ)
        worksheet.write(row, col + 7, ti)
        row += 1
    for met in metrics:
        for num, qmi,sdf,ncc,ntm,mano in met:  
            worksheet.write(row, col,     num)
            worksheet.write(row, col + 1, qmi)
            worksheet.write(row, col + 2, sdf)
            worksheet.write(row, col + 3, ncc)
            worksheet.write(row, col + 4, ntm)
            worksheet.write(row, col + 5, mano)
            row += 1

    row = 1
    for target in target_results:
        for tag,inter in target:
            worksheet.write(row, col+6,tag)
            worksheet.write(row, col+7,inter)
            row += 4

    workbook.close()

