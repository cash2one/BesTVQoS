#! /usr/bin/env python2.7
#coding=utf-8  
 
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
 
# python 2.3.*: email.Utils email.Encoders
from email.utils import COMMASPACE,formatdate
from email import encoders
 
import os
import sys

text = ""

def send_mail(text, texts=[], files=[], images=[], date=""): 
    global password
    server={}
    server['name'] = 'mail.funshion.com'
    server['user'] = 'sm'
    server['passwd'] = 'FUNshion890*()'
    #to = ['flashp2p@funshion.com']
    to = ['xujy@funshion.com']
    fro = "sm@funshion.com" 
    
    msg3 = MIMEMultipart() 
    msg3['From'] = fro 
    msg3['Subject'] = "vod stuck & dbuffer %s"%(date)
    msg3['To'] = COMMASPACE.join(to) #COMMASPACE==', ' 
    msg3['Date'] = formatdate(localtime=True) 
    #msg3.attach(MIMEText(text, 'html', 'utf-8'))  

    for a_text in texts:
        text += str(a_text)
			 
    for file in files: 
       part = MIMEBase('application', 'octet-stream') #'octet-stream': binary data 
       part.set_payload(open(file, 'rb').read()) 
       encoders.encode_base64(part) 
       part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file)) 
       msg3.attach(part)
        
 
    i = 0;
    for image in images:
        text += '<br><img src="cid:image%d">'%i
        
        part = MIMEImage(open(image, 'rb').read())
        part.add_header('Content-ID', '<image%d>'%i)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(image))

        msg3.attach(part)
        i += 1
 
    msg3.attach(MIMEText(text, 'html', 'utf-8'))  
    
    import smtplib 
    smtp = smtplib.SMTP(server['name'])
    smtp.login(server['user'], server['passwd']) 
    msg_content = msg3.as_string()
    smtp.sendmail(fro, to, msg_content) #msg.as_string()
    smtp.close()

def main(date, ver1, ver2):
    print ("Send mail start")
	
    img_list=[]
    img_list.append("png/daily_pn_plot_by_vod_stuck_of_%s_%s.png"%(ver1, date))
    img_list.append("png/daily_pn_plot_by_vod_stuck_of_%s_%s.png"%(ver2, date))
    img_list.append("png/daily_pn_plot_by_vod_dbuffer_of_%s_%s.png"%(ver1, date))
    img_list.append("png/daily_pn_plot_by_vod_dbuffer_of_%s_%s.png"%(ver2, date))
    send_mail(text, [], [], img_list, date)
    print ("Send Over")

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])
