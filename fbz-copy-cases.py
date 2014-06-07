from fogbugz import FogBugz
import sys


URL_FROM = None
EMAIL_FROM = None
PASSWORD_FROM = None

URL_TO = None
EMAIL_TO = None
PASSWORD_TO = None


if __name__ == '__main__':
    try:
        print '** LOGIN DATA FOR ACCOUNT FROM WHICH CASES WILL BE COPIED ***'
        if URL_FROM:
            print 'url from: ' + URL_FROM
        else:
            URL_FROM = raw_input('set url from (eg. https://from.fogbugz.com): ')

        if EMAIL_FROM:
            print 'email from: ' + EMAIL_FROM
        else:
            EMAIL_FROM = raw_input('set email from (eg. from@mail.com): ')

        if PASSWORD_FROM:
            print 'password from: ok'
        else:
            PASSWORD_FROM = raw_input('set password from: ')

        print '-----------------------------------------------------------'
        print 'Trying to login ........'
        fbz_from = FogBugz(URL_FROM)
        fbz_from.logon(EMAIL_FROM, PASSWORD_FROM)
        print 'ok'
    except:
        print '*** Cannot login to [{0}] ***'.format(URL_FROM)
        print 'copy aborted'
        sys.exit()

    print '-----------------------------------------------------------'

    try:
        print '** LOGIN DATA FOR ACCOUNT TO WHICH CASES WILL BE PASTED ***'
        if URL_TO:
            print 'url to: ' + URL_TO
        else:
            URL_TO = raw_input('set url to (eg. https://to.fogbugz.com): ')

        if EMAIL_TO:
            print 'email to: ' + EMAIL_TO
        else:
            EMAIL_TO = raw_input('set email to (eg. to@mail.com): ')

        if PASSWORD_TO:
            print 'password to: ok'
        else:
            PASSWORD_TO = raw_input('set password to: ')
        print '-----------------------------------------------------------'

        print 'Trying to login ........'
        fbz_to = FogBugz(URL_TO)
        fbz_to.logon(EMAIL_TO, PASSWORD_TO)
        print 'ok'
    except:
        print '*** Cannot login to [{0}] ***'.format(URL_TO)
        print 'copy terminated'
        sys.exit()


    try:
        fbz_to = FogBugz(URL_TO)
        fbz_to.logon(EMAIL_TO, PASSWORD_TO)
    except:
        print '*** Cannot login to [{0}] ***'.format(URL_TO)
        sys.exit()

    # when q='' it takes the user's (from) current selected filter in fogbugz.com (and copies only those cases)
    resp_from = fbz_from.search(q='', cols='ixBug,ixBugParent,ixStatus,sTitle,sProject,sFixFor,'
                                           'sCategory,sPersonAssignedTo,sPriority,dtDue,events')

    for case in resp_from.cases.childGenerator():
        title = case.stitle.string.encode('UTF-8')  # to eliminate the garbage from <![CDATA[title here]]>
        resp_to = fbz_to.search(q='title:"{0}"'.format(title), cols='ixBug')

        if resp_to.cases.case:
            print case.ixbug.string, 'ALREADY EXISTS as', resp_to.cases.case.ixbug.string
        else:
            resp_new_case = fbz_to.new(ixBug=case.ixbug.string, ixBugParent=case.ixbugparent.string,
                                       sTitle=case.stitle.string, sProject=case.sproject.string,
                                       sFixFor=case.sfixfor.string, sCategory=case.scategory.string,
                                       sPersonAssignedTo=case.spersonassignedto.string,
                                       spriority=case.spriority.string, dtdue=case.dtdue.string,
                                       cols='ixBug')
            new_id = int(resp_new_case.ixbug.string)

            # changes the status of the newly created case
            fbz_to.edit(ixBug=new_id, ixStatus=int(case.ixstatus.string))

            # add all the events
            for event in case.events.childGenerator():
                fbz_to.edit(ixBug=new_id, sEvent=event.s.string)
            print case.ixbug.string, 'ADDED as', new_id
