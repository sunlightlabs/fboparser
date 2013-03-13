import requests
import ftplib
import os

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
            os.mkdir(os.path.join(os.getcwd()+'/raw_files', fname))
        except OSError:
            print 'Dir already exists'
             
        ftp.cwd(fname)
        subfiles = []
        ftp.retrlines('LIST', subfiles.append)
        for sf in subfiles:
            subattr = sf.split(None, 8)
            subfname = subattr[-1].lstrip()
            if not os.path.exists(os.getcwd()+'/raw_files/' + fname + '/' + subfname):
                subout = open('raw_files/'+fname+'/'+subfname, 'wb')
                print "Writing %s to disk" % (fname+'/'+subfname)
                ftp.retrbinary("RETR " + subfname, subout.write, 8*1024)
                subout.close()
        ftp.cwd('/')
        

    else:
        if not os.path.exists(os.getcwd()+'/raw_files/'+fname):
            outfile = open('raw_files/'+fname, 'wb')
            print "Writing %s to disk" % fname
            ftp.retrbinary("RETR " + fname, outfile.write, 8*1024)
            outfile.close()


