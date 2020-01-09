
import sys
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase 
from email import encoders 


FROM_ADDR = 'noreply.foldermanager@kla-tencor.com'

class Validator:

    def __init__(self):
        #xmlschema_doc = etree.parse(xsd_path)
        #self.xmlschema = etree.XMLSchema(xmlschema_doc)
        #schema validation does not work 
        pass

    def validate(self, xml_path: str) -> bool:
        try:
            fx = open(xml_path,'r', errors='ignore').read()
            
            return "<SessionData>" in fx
        except:
            print(xml_path)
            #print(sys.exc_info())
            return False

def save_as_csv(input_json , output_file_name , report_only_failures=False):
    data =[]
    for items in input_json.keys():
        for values in input_json[items]:
            if(report_only_failures or (values['TestRailId']=="" and values['Enabled'].lower()=='true')):
                data.append({
                    "path": items,
                    "TestSuite": values['TestSuite'],
                    "TestCase":values['TestCase'],
                    "Enabled":values['Enabled'],
                    "TestRailID": values['TestRailId']

                })
    df = pd.DataFrame(data)
    df.to_csv(output_file_name)
    return df



def create_email_msg( owner_email, attachment_file_path, subject ,TestCaseCount,BlankCount):

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['To'] = owner_email
    msg['From'] = FROM_ADDR
    filename = attachment_file_path
    body = "Total number of TestCase = {0} \nTotal number of test case without TestRail id : {1}".format(TestCaseCount,BlankCount)
    body = MIMEText(body)
    msg.attach(body)
    attachment = open(attachment_file_path, "rb") 
    
    # instance of MIMEBase and named as p 
    p = MIMEBase('application', 'octet-stream') 
    
    # To change the payload into encoded form 
    p.set_payload((attachment).read()) 
    
    # encode into base64 
    encoders.encode_base64(p) 
    
    p.add_header('Content-Disposition', "attachment; filename= %s" % filename) 
    
    # attach the instance 'p' to instance 'msg' 
    msg.attach(p) 
    return msg

def sendmail_msg(msg):
    mailserver = smtplib.SMTP('mailhost.kla-tencor.com', 25)
    mailserver.ehlo()
    mailserver.starttls()
    #mailserver.login(EMAIL_USERNAME, EMAIL_PASSWORD)
    mailserver.send_message(msg)
    mailserver.quit()
