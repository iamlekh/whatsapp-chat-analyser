from .data import details
import codecs
from fpdf import FPDF, HTMLMixin
from datetime import datetime
import os
today_date = datetime.today().strftime("%d %B %Y")
basedir = os.path.abspath(os.path.dirname(__file__))

def report(filepath):
    # print("rep bse-", basedir)
    # print("report ------",os.getcwd() )
    filepath = filepath.split('/',2)[2]
    # print(filepath)
    try:
        a = details(filepath)
    except Exception as e:
        pass
    
    report_name = filepath.rsplit("/")[-1].split('.')[0]
    report_path = basedir + "/static/pdf/"
    print("report base --", basedir)
    print(report_path+report_name+'.pdf')

    WIDTH = 210
    HEIGHT = 297


    def create_title(day, pdf):
        pdf.set_font('Arial', 'IB', 24)  
        pdf.ln(40)
        pdf.write(15, f"WHATSAPP CHAT REPORT")
        pdf.ln(15)
        pdf.set_font('Arial', 'I', 16)
        #   pdf.write(4, f'{day}')
        pdf.ln(10)

    def create_analytics_report(day=today_date, filename=report_path+report_name+'.pdf'):
        pdf = FPDF() # A4 (210 by 297 mm)

        ''' First Page '''
        pdf.add_page()
        pdf.image(basedir+"/static/img/format.png", 0, 0, WIDTH)
        create_title(day, pdf)


        pdf.set_font('Arial', 'I', 16)
        pdf.write(1, "Some Basic insights of your group", 0)
        pdf.ln(15)
        pdf.set_font('Arial', '', 12)
        pdf.write(1, a[10], 0)
        pdf.ln(7)
        pdf.write(1, a[11], 0)
        pdf.ln(7)
        pdf.write(1,a[12], 0)
        pdf.image(basedir+"/temp/activity_wrt_time.png", x = 2, y = 120, w = 206, h = 170, type = '', link = '')

        pdf.ln(10)
        
        #2
        pdf.add_page()
        pdf.ln(20)
        pdf.write(1, "Total unique user - {}".format(a[0]), 0)
        pdf.ln(10)
        pdf.write(1, "Average messages per day - {}".format(a[2]), 0)
        pdf.image(basedir+"/temp/top_active_member.png", x = 2, y = 80, w = 206, h = 170, type = '', link = '')
        
        #3
        pdf.add_page()
        pdf.image(basedir+"/temp/timeseries_masg_count.png", x = 2, y = 20, w = 206, h = 140, type = '', link = '')
        pdf.image(basedir+"/temp/top_busy_days.png", x = 2, y = 170, w = 206, h = 100, type = '', link = '')
        #4
        pdf.add_page()
        pdf.ln(15)
        pdf.write(1, "Total messages deleted - {}".format(a[13]), 0)
        
        pdf.ln(10)
        pdf.write(1, "Average letter per message  - {}".format(a[5]), 0)
        pdf.ln(10)
        pdf.write(1, "Average words per message  - {}".format(a[6]), 0)
        pdf.ln(10)
        pdf.write(1, "Total letters - {}".format(a[7]), 0)
        pdf.ln(10)
        pdf.write(1, "Total words - {}".format(a[8]), 0)
        pdf.ln(10)
        pdf.write(1, "Total media shared - {}".format(a[3]), 0)
        pdf.image(basedir+"/temp/top_media_member.png", x = 2, y = 80, w = 206, h = 170, type = '', link = '')
        #5
        pdf.add_page()
        pdf.ln(5)
        pdf.write(1, "Total emojies shared - {}".format(a[4]), 0)
        # pdf.add_font("NotoEmoji",fname = '/home/darpan/Documents/whatsapp_report/emoji.ttf', uni = True)
        pdf.image(basedir+"/temp/top_used_words.png", x = 2, y = 150, w = WIDTH-4, h = HEIGHT-160, type = '', link = '')
        
        pdf.ln(15)
        pdf.write(12, "                                           Top 10 Emoji count", 0)
        pdf.ln(20)
        pdf.cell(40)
        # pdf.cell(75, 10, "A Tabular and Graphical Report of Professor Criss's Ratings by Users Charles and Mike", 0, 2, 'C')
        # pdf.cell(90, 10, " ", 0, 2, 'C')
        # pdf.cell(-80)
        # pdf.cell(50, 10, 'Question', 1, 0, 'C')

        
        pdf.cell(40, 10, 'Emoji Count', 1, 0, 'C')
        pdf.cell(100, 10, 'Emoji desc', 1, 2, 'C')
        pdf.cell(-40)
        pdf.set_font('arial', '', 12)
        for i in range(0, len(a[9])):
            # pdf.cell(50, 10, '%s' % (a[9]['emoji'].iloc[i]), 1, 0, 'C')
            pdf.cell(40, 7, '%s' % (str(a[9]['emoji_count'].iloc[i])), 1, 0, 'C')
            pdf.cell(100, 7, '%s' % (str(a[9]['emoji_description'].iloc[i])), 1, 2, 'C')
            pdf.cell(-40)
        pdf.cell(90, 10, " ", 0, 2, 'C')

        # pdf.write(1, a[9], 0)
        #6
        pdf.add_page()
        # pdf.multi_cell(1, 5, a[14], border = 0, str = 'J',bool = False)
        pdf.write(10,a[14],0)
        pdf.image(basedir+"/temp/sentiment.png", x = 2, y = 80, w = 206, h = 170, type = '', link = '')
        #7
        pdf.add_page()
        pdf.image(basedir+"/temp/word_cloud.png", x = 2, y = 2, w = WIDTH-4, h = HEIGHT-4, type = '', link = '')



        pdf.output(filename, 'F')

    
    create_analytics_report(today_date)
    # if __name__ == '__main__':
    #     create_analytics_report(today_date)
    #     print("done")

# data.details("/chat/upload/aa.txt")