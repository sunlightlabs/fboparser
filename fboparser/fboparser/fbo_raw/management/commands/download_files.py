from django.core.management.base import CommandError, BaseCommand
from django.conf import settings
import requests
import ftplib
import os

class Command(BaseCommand):

    def handle(self, *args, **kwargs):


        files = []
        ftp = ftplib.FTP('ftp.fbo.gov')
        ftp.login()
        ftp.retrlines('LIST', files.append)

        for f in files:
            attributes = f.split(None, 8)
            fname = attributes[-1].lstrip()
            if attributes[0].strip()[0] == 'd':
                #it's a dir
                try:
                    os.mkdir(settings.RAW_PATH, fname))
                except OSError:
                    print('Dir already exists')
                     
                ftp.cwd(fname)
                subfiles = []
                ftp.retrlines('LIST', subfiles.append)
                for sf in subfiles:
                    subattr = sf.split(None, 8)
                    subfname = subattr[-1].lstrip()
                    if not os.path.exists(settings.RAW_PATH + fname + '/' + subfname):
                        subout = open(settings.RAW_PATH+fname+'/'+subfname, 'wb')
                        print("Writing %s to disk" % (fname+'/'+subfname))
                        ftp.retrbinary("RETR " + subfname, subout.write, 8*1024)
                        subout.close()
                ftp.cwd('/')
                

            else:
                if not os.path.exists(settings.RAW_PATH + fname):
                    outfile = open(settings.RAW_PATH +fname, 'wb')
                    print("Writing %s to disk" % fname)
                    ftp.retrbinary("RETR " + fname, outfile.write, 8*1024)
                    outfile.close()


