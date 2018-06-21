import re

'''
'signal time=1529507303.118529 sender=:1.290 -> destination=(null destination) serial=4 path=/EntitlementStatus; interface=com.redhat.SubscriptionManager.EntitlementStatus; member=entitlement_status_changed\n   int32 0\nmethod return time=1529507303.118541 sender=:1.290 -> destination=:1.289 serial=5 reply_serial=6\n',
'''

def is_signal(path, interface, member):
    regexp = {
        'path': re.compile('path=[ ]*{0}'.format(path.strip())),
        'member': re.compile('member=[ ]*{0}'.format(member.strip())),
        'interface': re.compile('interface=[ ]*{0}'.format(interface.strip()))
    }
    def predicate(s):
        firstline = s.splitlines()[0]
        return  s.startswith('signal ') \
            and regexp['path'].search(firstline) \
            and regexp['interface'].search(firstline) \
            and regexp['member'].search(firstline)
    return predicate

