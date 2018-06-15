from src.types import Verification
import re

def verify_dbus_object_exists(object_path):
   def verify(events):
       busctl_events = tuple(filter(lambda event: event.get('type')=='shell command' \
                                    and event.get('command') == 'busctl',
                                    events))
       if not busctl_events:
           return Verification(False,"No event of type: 'shell command' with command:'busctl' found")

       lines = [s.strip() for s in busctl_events[0]['stdout'].split('\n')]
       pattern = re.compile("(└─|├─){0}".format(object_path))
       object_line = filter(pattern.match,lines)

       if not object_line:
           return Verification(False,"No line '{0}' appears in 'busctl tree' result".format(object_path))
       return Verification(True,"a text '{0}' exists in 'busctl tree' result".format(object_path))

   return verify
