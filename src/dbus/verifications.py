from src.types import Verification
import re
import json
import funcy
from src.dbus.monitor import is_signal

def verify_dbus_object_exists(object_path):
   def verify(events):
       busctl_events = tuple(filter(lambda event: event.get('type')=='shell command' \
                                    and event.get('command') == 'busctl',
                                    events))
       if not busctl_events:
           return Verification(False,"No event of type: 'shell command' with command:'busctl' found")

       lines = [s.strip() for s in busctl_events[0]['stdout'].splitlines()]
       pattern = re.compile("(└─|├─){0}".format(object_path))
       object_line = filter(pattern.match,lines)

       if not object_line:
           return Verification(False,"No line '{0}' appears in 'busctl tree' result".format(object_path))
       return Verification(True,"a text '{0}' exists in 'busctl tree' result".format(object_path))

   return verify

def verify_dbus_signal_was_emitted(path, interface, member):
   is_the_right_signal = is_signal(path=path, interface=interface, member=member)

   def verify(events):
      the_right_dbus_signals = [e for e in events if e.get('type') == 'system dbus monitor' \
                      and is_the_right_signal(funcy.get_in(e,['event','stdout'],""))]
      if not the_right_dbus_signals:
         return Verification(False,"No signal event has appeared in 'system dbus monitor' for path={0};interface={1};member={2}"\
                             .format(path,interface,member))
      return Verification(True,"a system dbus signal event for path={0};interface={1};member={2} appeared".format(path, interface, member))

   return verify
