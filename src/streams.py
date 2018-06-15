from rx.subjects import Subject
streams = {
    "/ws/testware/monitor": Subject(),
    "/ws/dbus/system/monitor": Subject(),
}
