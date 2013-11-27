#encoding=utf8
import sys
import argparse
import os
import re

def main():
    parser = argparse.ArgumentParser(
            description='SVN Diff Utils',
            prog = "svndiff",
            epilog='''=========== Author: powerfj@gmail.com=============''')

    #positional argument, 不带--或者-
    #optional argument 带--sum或者-
    parser.add_argument('file', help='the file to operate')
    parser.add_argument('-log', dest='log', action='store_true',
            help='print the log revisions of the file')
    parser.add_argument('-r', dest='revision', action='store',
            help='''diff the current file with revision, 
                    r1 => diff the r1 with current, 
                    r1: => diff the r1 with the previous vison of r1, \n
                    r1:r2=> diff the ''')
    args = parser.parse_args()

    if args.log:
        revisions=get_svn_logs(args.file)
        print "\n".join(map(lambda x:x[0],revisions))
    elif args.revision:
        rs = args.revision.split(":")
        if len(rs)==1:
            rev=rs[0]
            diff_file_with_revision(args.file,rev)
        elif len(rs)==2:
            #对比某一个版本以及它之前的版本
            if rs[1]=="":
                diff_file_revision_with_pre(args.file,rs[0])
            else:
                diff_file_revision_with_two_revision(args.file,rs[0],rs[1])
    else:
        compare_file_with_latest_revision(args.file)
        
    #print args.accumulate(args)

def diff_file_revision_with_pre(file,rev):
    """
       对比文件与之前的文件版本
    """
    revisions = get_file_revisions(file)

    if rev not in revisions:
        print "can't find revision %s in the log history"%rev
        return False
        
    idx = revisions.index(rev)

    if len(revisions)-1==idx:
        print "revision %s is the earliest revisions"%rev
        return False
    
    prerev=revisions[idx+1]
    diff_file_revision_with_two_revision(file,prerev,rev,revisions)


def get_file_revisions(file):
    """
        通过svn logs 获取文件的版本号
    """
    revisions = get_svn_logs(file)

    #去除首位的r字符
    revisions = map(lambda x:x[1][1:],revisions)
    return revisions
    

def diff_file_revision_with_two_revision(file,rev1,rev2,revisions=None):
    """
    """
    if not revisions:
        revisions = get_file_revisions(file)
    
    if rev1 not in revisions:
        print "can't find revision %s in the log history"%rev1
        return False

    if rev2 not in revisions:
        print "can't find revision %s in the log history"%rev2

    svnfile1 = get_file_to_tmp_dir(file,rev1)
    svnfile2 = get_file_to_tmp_dir(file,rev2)
    compare_file(svnfile1,svnfile2)

def diff_file_with_revision(file,rev):
    """
        对比文件工作版本与某个特定版本号的版本
    """
    path= os.path.abspath(file)
    if not os.path.exists(path):
        print "error: file %s not exist"%os.path.abspath(path)
        return 1
    svnfile= get_file_to_tmp_dir(file,rev)
    compare_file(svnfile,file)

def get_file_to_tmp_dir(file,rev):
    svntempdir=get_svntemp_dir()
    svnfile= os.path.join(svntempdir,"%s.r%s"%(file,rev))
    os.system("svn cat -r %s %s> %s"%(rev,file,svnfile))
    return svnfile

def get_svntemp_dir():
    path  = os.path.expanduser("~/svntemp")
    if not os.path.exists(path):
        os.mkdir(path)
    return path

def compare_file_with_latest_revision(file):
    file=os.path.abspath(file)
    d = os.path.dirname(file)
    f = os.path.basename(file)
    compare_file("%s/.svn/text-base/%s.svn-base"%(d,f),file)

def compare_file(file1,file2):
    """
        d=`dirname $1`
        f=`basename $1`
        ksdiff "$d/.svn/text-base/$f.svn-base" "$1"
    """
    os.system('ksdiff "%s" "%s"'%(file1,file2))
    

def test_main():
    (options, args) = parser.parse_args()

    if len(sys.argv)<2:
        print """Usage:
                 svndiff <file>             diff the current file with the svn base version
                 svndiff l <file>           show the versions of the file use svn log
                 svndiff <file>@revison     diff file @revision with the last revision of this file
              """
    else:
        print sys.argv

def get_svn_logs(file):
    lines = os.popen("svn log %s"%file).readlines()
    revisons=[]
    for line in lines:
        if re.search("^r\d+ \|",line):
            revisons.append((line,line.split("|")[0].strip()))
    return revisons

if __name__=="__main__":
    main()
