import websockets, os
from colorama import Fore
from urllib.parse import urljoin
import logging, asyncio, logging.config, json

#
# 600Kc mamce
#

from rx import Observable
from rx.subjects import Subject
logging.config.fileConfig("logging.conf")

entitlementStatusStream = Subject()
subscriptionManagerStream = Subject()

entitlementStatusStream.subscribe(
    lambda x:   print(x),
    lambda err: print(err),
    lambda :   print('end of the show')
)
subscriptionManagerStream.subscribe(
    lambda x:   print(x),
    lambda err: print(err),
    lambda :   print('end of the show')
)

Observable.zip(entitlementStatusStream,subscriptionManagerStream, lambda x,y: [x,y])\
    .subscribe(
        lambda x:   print("entitlement + subscription zip: ", str(x)),
        lambda err: print("zip error: " + str(err)),
        lambda x:   print('end of the show')
    )

aa = Observable.from_(['ent01','ent02','ent03'])
bb = Observable.from_(['subMan01','subMan02','subMan03'])

aa.zip(bb, lambda x,y: [x,y])\
    .subscribe(
        lambda x: print("zip(aa,bb) : " + str(x)),
        lambda err: print("zip error: " + str(err)),
        lambda : print('end of the show')
    )

Observable.from_(['ent01','ent02','ent03'])\
    .subscribe(
        lambda x: entitlementStatusStream.on_next(x)
    )

Observable.from_(['subMan01','subMan02','subMan03'])\
    .subscribe(
        lambda x: subscriptionManagerStream.on_next(x)
    )
