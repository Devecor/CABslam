distance = xlsread('test9_data.xlsx', 'sheet1', 'A2:A159');
angel = xlsread('test9_data.xlsx', 'sheet1', 'B2:B157');
angel_f = xlsread('test9_data.xlsx', 'sheet1', 'C2:C158');
angel_h = xlsread('test9_data.xlsx', 'sheet1', 'D2:D159');
%cdfplot(distance); hold;
%cdfplot(angel); hold on;
%cdfplot(angel_f); hold on;
cdfplot(angel_h); hold on;
%pdfplot(distance, 200);
