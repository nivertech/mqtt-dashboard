#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim tabstop=4 expandtab shiftwidth=4 softtabstop=4

#
# mqtt-dashboard
#	....
#
#


__author__ = "Dennis Sell"
__copyright__ = "Copyright (C) Dennis Sell"


APPNAME = "mqtt-dashboard"
VERSION = "0.10"
WATCHTOPIC = "/raw/" + APPNAME + "/command"



import subprocess
from mqttcore import MQTTClientCore
from mqttcore import main
from daemon import Daemon
import threading
import Queue
from Tkinter import *
from ScrolledText import ScrolledText
import datetime


class MyMQTTClientCore(MQTTClientCore):
    def __init__(self, appname, clienttype):
        self.q = Queue.Queue(200)
        MQTTClientCore.__init__(self, appname, clienttype)
        self.clientversion = VERSION
        self.watchtopic = WATCHTOPIC
        self.workingdir = self.cfg.WORKINGDIR
    	self.interval = self.cfg.INTERVAL
        self.root = Tk()
        #build UI

        self.root.title("MQTT Dashboard")
        frame = Frame(self.root)
        frame.pack()
        host_ofx=0
        Label(frame, text="Hostname:").grid(row=host_ofx, column=0, sticky=W)
        self.host_text = Text(frame, height=1, width=30)
        self.host_text.grid(row=host_ofx, column=1, columnspan=3, sticky=W)
        self.host_text.delete(1.0, END)
        self.host_text.insert(END, self.mqtthost)
        self.button_connect = Button(frame, text="Connect", command=connect)
        self.button_connect.grid(row=host_ofx, column=4, columnspan=2, sticky=W)
        self.button_disconnect = Button(frame, text="Disconnect", command=disconnect)
        self.button_disconnect.grid(row=host_ofx, column=5, columnspan=2)

        fill0_ofx=host_ofx+1
        Label(frame, text="").grid(row=fill0_ofx, column=0)

        version_ofx=fill0_ofx+1
        Label(frame, text="Version:").grid(row=version_ofx, column=0, sticky=W)
        self.version_text = Text(frame, height=1, width=30, state=DISABLED)
        self.version_text.grid(row=version_ofx, column=1, columnspan=3)
        self.revision_text = Text(frame, height=1, width=30, state=DISABLED)
        self.revision_text.grid(row=version_ofx, column=4, columnspan=3)
        self.timestamp_text = Text(frame, height=1, width=30, state=DISABLED)
        self.timestamp_text.grid(row=version_ofx, column=7, columnspan=3)

        fill1_ofx=version_ofx+1
        Label(frame, text="").grid(row=fill1_ofx, column=0)

        load_ofx=fill1_ofx+1
        Label(frame, text="Load:").grid(row=load_ofx, column=0, sticky=W)
        Label(frame, text="Per Sec").grid(row=load_ofx, column=1, columnspan=2)
        Label(frame, text="Per 1 Min").grid(row=load_ofx, column=3, columnspan=2)
        Label(frame, text="Per 5 Min").grid(row=load_ofx, column=5, columnspan=2)
        Label(frame, text="Per 15 Min").grid(row=load_ofx, column=7, columnspan=2)
        Label(frame, text="Total").grid(row=load_ofx, column=9, columnspan=2)

        Label(frame, text="Received").grid(row=load_ofx+1, column=2)
        Label(frame, text="Sent").grid(row=load_ofx+1, column=1)
        Label(frame, text="Received").grid(row=load_ofx+1, column=4)
        Label(frame, text="Sent").grid(row=load_ofx+1, column=3)
        Label(frame, text="Received").grid(row=load_ofx+1, column=6)
        Label(frame, text="Sent").grid(row=load_ofx+1, column=5)
        Label(frame, text="Received").grid(row=load_ofx+1, column=8)
        Label(frame, text="Sent").grid(row=load_ofx+1, column=7)
        Label(frame, text="Received").grid(row=load_ofx+1, column=10)
        Label(frame, text="Sent").grid(row=load_ofx+1, column=9)

        Label(frame, text="Bytes").grid(row=load_ofx+2, column=0, sticky=W)
        self.bytes_ss_text = Text(frame, height=1, width=10, state=DISABLED)
        self.bytes_ss_text.grid(row=load_ofx+2, column=1)
        self.bytes_sr_text = Text(frame, height=1, width=10, state=DISABLED)
        self.bytes_sr_text.grid(row=load_ofx+2, column=2)
        self.bytes_1ms_text = Text(frame, height=1, width=10, state=DISABLED)
        self.bytes_1ms_text.grid(row=load_ofx+2, column=3)
        self.bytes_1mr_text = Text(frame, height=1, width=10, state=DISABLED)
        self.bytes_1mr_text.grid(row=load_ofx+2, column=4)
        self.bytes_5ms_text = Text(frame, height=1, width=10, state=DISABLED)
        self.bytes_5ms_text.grid(row=load_ofx+2, column=5)
        self.bytes_5mr_text = Text(frame, height=1, width=10, state=DISABLED)
        self.bytes_5mr_text.grid(row=load_ofx+2, column=6)
        self.bytes_15ms_text = Text(frame, height=1, width=10, state=DISABLED)
        self.bytes_15ms_text.grid(row=load_ofx+2, column=7)
        self.bytes_15mr_text = Text(frame, height=1, width=10, state=DISABLED)
        self.bytes_15mr_text.grid(row=load_ofx+2, column=8)
        self.bytes_ts_text = Text(frame, height=1, width=16, state=DISABLED)
        self.bytes_ts_text.grid(row=load_ofx+2, column=9)
        self.bytes_tr_text = Text(frame, height=1, width=16, state=DISABLED)
        self.bytes_tr_text.grid(row=load_ofx+2, column=10)

        Label(frame, text="Messages").grid(row=load_ofx+3, column=0, sticky=W)
        self.messages_ss_text = Text(frame, height=1, width=10, state=DISABLED)
        self.messages_ss_text.grid(row=load_ofx+3, column=1)
        self.messages_sr_text = Text(frame, height=1, width=10, state=DISABLED)
        self.messages_sr_text.grid(row=load_ofx+3, column=2)
        self.messages_1ms_text = Text(frame, height=1, width=10, state=DISABLED)
        self.messages_1ms_text.grid(row=load_ofx+3, column=3)
        self.messages_1mr_text = Text(frame, height=1, width=10, state=DISABLED)
        self.messages_1mr_text.grid(row=load_ofx+3, column=4)
        self.messages_5ms_text = Text(frame, height=1, width=10, state=DISABLED)
        self.messages_5ms_text.grid(row=load_ofx+3, column=5)
        self.messages_5mr_text = Text(frame, height=1, width=10, state=DISABLED)
        self.messages_5mr_text.grid(row=load_ofx+3, column=6)
        self.messages_15ms_text = Text(frame, height=1, width=10, state=DISABLED)
        self.messages_15ms_text.grid(row=load_ofx+3, column=7)
        self.messages_15mr_text = Text(frame, height=1, width=10, state=DISABLED)
        self.messages_15mr_text.grid(row=load_ofx+3, column=8)
        self.messages_ts_text = Text(frame, height=1, width=16, state=DISABLED)
        self.messages_ts_text.grid(row=load_ofx+3, column=9)
        self.messages_tr_text = Text(frame, height=1, width=16, state=DISABLED)
        self.messages_tr_text.grid(row=load_ofx+3, column=10)

        Label(frame, text="Published").grid(row=load_ofx+4, column=0, sticky=W)
#        self.publish_ss_text = Text(frame, height=1, width=10, state=DISABLED)
#        self.publish_ss_text.grid(row=5+1, column=1)
#        self.publish_sr_text = Text(frame, height=1, width=10, state=DISABLED)
#        self.publish_sr_text.grid(row=load_ofx+4, column=2)
        self.publish_1ms_text = Text(frame, height=1, width=10, state=DISABLED)
        self.publish_1ms_text.grid(row=load_ofx+4, column=3)
        self.publish_1mr_text = Text(frame, height=1, width=10, state=DISABLED)
        self.publish_1mr_text.grid(row=load_ofx+4, column=4)
        self.publish_5ms_text = Text(frame, height=1, width=10, state=DISABLED)
        self.publish_5ms_text.grid(row=load_ofx+4, column=5)
        self.publish_5mr_text = Text(frame, height=1, width=10, state=DISABLED)
        self.publish_5mr_text.grid(row=load_ofx+4, column=6)
        self.publish_15ms_text = Text(frame, height=1, width=10, state=DISABLED)
        self.publish_15ms_text.grid(row=load_ofx+4, column=7)
        self.publish_15mr_text = Text(frame, height=1, width=10, state=DISABLED)
        self.publish_15mr_text.grid(row=load_ofx+4, column=8)
#        self.publish_ts_text = Text(frame, height=1, width=10, state=DISABLED)
#        self.publish_ts_text.grid(row=load_ofx+4, column=9)
#        self.publish_tr_text = Text(frame, height=1, width=10, state=DISABLED)
#        self.publish_tr_text.grid(row=load_ofx+4, column=10)

        Label(frame, text="Connections").grid(row=load_ofx+5, column=0, sticky=W)
#        self.connections_s_text = Text(frame, height=1, width=20, state=DISABLED)
#        self.connections_s_text.grid(row=load_ofx+5, column=1, columnspan=2)
        self.connections_1m_text = Text(frame, height=1, width=21, state=DISABLED)
        self.connections_1m_text.grid(row=load_ofx+5, column=3, columnspan=2)
        self.connections_5m_text = Text(frame, height=1, width=21, state=DISABLED)
        self.connections_5m_text.grid(row=load_ofx+5, column=5, columnspan=2)
        self.connections_15m_text = Text(frame, height=1, width=21, state=DISABLED)
        self.connections_15m_text.grid(row=load_ofx+5, column=7, columnspan=2)
#        self.connections_t_text = Text(frame, height=1, width=20, state=DISABLED)
#        self.connections_t_text.grid(row=load_ofx+5, column=9, columnspan=2)

        Label(frame, text="Sockets").grid(row=load_ofx+6, column=0, sticky=W)
#        self.sockets_s_text = Text(frame, height=1, width=20, state=DISABLED)
#        self.sockets_s_text.grid(row=load_ofx+6, column=1, columnspan=2)
        self.sockets_1m_text = Text(frame, height=1, width=21, state=DISABLED)
        self.sockets_1m_text.grid(row=load_ofx+6, column=3, columnspan=2)
        self.sockets_5m_text = Text(frame, height=1, width=21, state=DISABLED)
        self.sockets_5m_text.grid(row=load_ofx+6, column=5, columnspan=2)
        self.sockets_15m_text = Text(frame, height=1, width=21, state=DISABLED)
        self.sockets_15m_text.grid(row=load_ofx+6, column=7, columnspan=2)
#        self.sockets_t_text = Text(frame, height=1, width=20, state=DISABLED)
#        self.sockets_t_text.grid(row=load_ofx+6, column=9, columnspan=2)

        fill2_ofx=load_ofx+7
        Label(frame, text="").grid(row=fill2_ofx, column=0)

        clients_ofx=fill2_ofx+1
        clients_ofy=0
        Label(frame, text="Clients:").grid(row=clients_ofx, column=clients_ofy, sticky=W)
        Label(frame, text="Active").grid(row=clients_ofx+1, column=clients_ofy+1, sticky=W)
        self.active_text = Text(frame, height=1, width=7, state=DISABLED)
        self.active_text.grid(row=clients_ofx+1, column=clients_ofy+2)
        Label(frame, text="Inactive").grid(row=clients_ofx+2, column=clients_ofy+1, sticky=W)
        self.inactive_text = Text(frame, height=1, width=7, state=DISABLED)
        self.inactive_text.grid(row=clients_ofx+2, column=clients_ofy+2)
        Label(frame, text="Total").grid(row=clients_ofx+3, column=clients_ofy+1, sticky=W)
        self.clients_total_text = Text(frame, height=1, width=7, state=DISABLED)
        self.clients_total_text.grid(row=clients_ofx+3, column=clients_ofy+2)
        Label(frame, text="Expired").grid(row=clients_ofx+4, column=clients_ofy+1, sticky=W)
        self.expired_text = Text(frame, height=1, width=7, state=DISABLED)
        self.expired_text.grid(row=clients_ofx+4, column=clients_ofy+2)
        Label(frame, text="Maximum").grid(row=clients_ofx+5, column=clients_ofy+1, sticky=W)
        self.max_text = Text(frame, height=1, width=7, state=DISABLED)
        self.max_text.grid(row=clients_ofx+5, column=clients_ofy+2)

        other_ofx=fill2_ofx+1
        other_ofy=8
        Label(frame, text="Other:").grid(row=other_ofx, column=other_ofy, sticky=W)
        Label(frame, text="Uptime").grid(row=other_ofx+1, column=other_ofy+1, sticky=W)
        self.uptime_text = Text(frame, height=1, width=16, state=DISABLED)
        self.uptime_text.grid(row=other_ofx+1, column=other_ofy+2)
        Label(frame, text="Heap Current").grid(row=other_ofx+2, column=other_ofy+1, sticky=W)
        self.heap_text = Text(frame, height=1, width=16, state=DISABLED)
        self.heap_text.grid(row=other_ofx+2, column=other_ofy+2)
        Label(frame, text="Heap Max.").grid(row=other_ofx+3, column=other_ofy+1, sticky=W)
        self.heap_max_text = Text(frame, height=1, width=16, state=DISABLED)
        self.heap_max_text.grid(row=other_ofx+3, column=other_ofy+2)
#        Label(frame, text="Bridges:").grid(row=other_ofx+4, column=other_ofy, sticky=W)
#        self.connections_text = Text(frame, height=3, width=8, state=DISABLED)
#        self.connections_text.grid(row=other_ofx+5, column=other_ofy+2, rowspan=3)

        msg_ofx=fill2_ofx+1
        msg_ofy=4
        Label(frame, text="Messages:").grid(row=msg_ofx, column=msg_ofy, sticky=W)
        Label(frame, text="Retained").grid(row=msg_ofx+1, column=msg_ofy+1, sticky=W)
        self.retained_text = Text(frame, height=1, width=7, state=DISABLED)
        self.retained_text.grid(row=msg_ofx+1, column=msg_ofy+2)
        Label(frame, text="Stored").grid(row=msg_ofx+2, column=msg_ofy+1, sticky=W)
        self.stored_text = Text(frame, height=1, width=7, state=DISABLED)
        self.stored_text.grid(row=msg_ofx+2, column=msg_ofy+2)
        Label(frame, text="Dropped").grid(row=msg_ofx+3, column=msg_ofy+1, sticky=W)
        self.dropped_text = Text(frame, height=1, width=7, state=DISABLED)
        self.dropped_text.grid(row=msg_ofx+3, column=msg_ofy+2)
        Label(frame, text="Inflight").grid(row=msg_ofx+4, column=msg_ofy+1, sticky=W)
        self.inflight_text = Text(frame, height=1, width=7, state=DISABLED)
        self.inflight_text.grid(row=msg_ofx+4, column=msg_ofy+2)
        Label(frame, text="Subscriptns").grid(row=msg_ofx+5, column=msg_ofy+1, sticky=W)
        self.subscriptions_text = Text(frame, height=1, width=7, state=DISABLED)
        self.subscriptions_text.grid(row=msg_ofx+5, column=msg_ofy+2)

        fill3_ofx=msg_ofx+8
        Label(frame, text="").grid(row=fill3_ofx, column=0)

        log_ofx=fill3_ofx+1
        Label(frame, text="Log:").grid(row=log_ofx, column=0, sticky=W)
        self.log_text = ScrolledText(frame, height=6, state=DISABLED)
        self.log_text.grid(row=log_ofx+1, column=0, columnspan=11, sticky=N+W+E+S)
        self.root.update()
        self.root.protocol("WM_DELETE_WINDOW", self.closehandler)
        self.root.update()
        self.t = threading.Thread(target=self.do_thread_loop)

    def do_thread_loop(self):
        self.main_loop()        

    def on_connect(self, mself, obj, rc):
        MQTTClientCore.on_connect(self, mself, obj, rc)
        self.mqttc.subscribe("$SYS/#", qos=2)

    def on_message(self, mself, obj, msg):
        MQTTClientCore.on_message(self, mself, obj, msg)
        obj.put(msg)

    def closehandler(self):
        print "closing window"
        self.root.destroy()
        self.root.quit()


def connect():
    MQTTClientCore.mqtt_connect(daemon.mqttcore)

def disconnect():
    MQTTClientCore.mqtt_disconnect(daemon.mqttcore)


class MyDaemon(Daemon):
    def run(self):
        self.mqttcore = MyMQTTClientCore(APPNAME, clienttype="type3")
        if(len(sys.argv) > 1):
            self.mqttcore.mqtthost = sys.argv[1]
            self.mqttcore.host_text.delete(1.0, END)
            self.mqttcore.host_text.insert(END, self.mqttcore.mqtthost)
            self.mqttcore.root.update()
        self.mqttcore.t.start()
        while(self.mqttcore.running):
            self.mqttcore.root.update()
            if (not self.mqttcore.q.empty()):
                msg = self.mqttcore.q.get()
                if(msg.topic == "$SYS/broker/version"):
                    self.mqttcore.version_text.config(state=NORMAL)
                    self.mqttcore.version_text.delete(1.0, END)
                    self.mqttcore.version_text.insert(END, msg.payload) 
                    self.mqttcore.version_text.config(state=DISABLED) 
                elif(msg.topic == "$SYS/broker/changeset"):
                    self.mqttcore.revision_text.config(state=NORMAL)
                    self.mqttcore.revision_text.delete(1.0, END)
                    self.mqttcore.revision_text.insert(END, msg.payload) 
                    self.mqttcore.revision_text.config(state=DISABLED)                  
                elif(msg.topic == "$SYS/broker/timestamp"):
                    self.mqttcore.timestamp_text.config(state=NORMAL)
                    self.mqttcore.timestamp_text.delete(1.0, END)
                    self.mqttcore.timestamp_text.insert(END, msg.payload)
                    self.mqttcore.timestamp_text.config(state=DISABLED)

                elif(msg.topic == "$SYS/broker/bytes/per second/sent"):
                    self.mqttcore.bytes_ss_text.config(state=NORMAL)
                    self.mqttcore.bytes_ss_text.delete(1.0, END)
                    self.mqttcore.bytes_ss_text.insert(END, msg.payload)
                    self.mqttcore.bytes_ss_text.config(state=DISABLED)
                elif(msg.topic == "$SYS/broker/bytes/per second/received"):
                    self.mqttcore.bytes_sr_text.config(state=NORMAL)
                    self.mqttcore.bytes_sr_text.delete(1.0, END)
                    self.mqttcore.bytes_sr_text.insert(END, msg.payload)
                    self.mqttcore.bytes_sr_text.config(state=DISABLED)
                elif(msg.topic == "$SYS/broker/load/bytes/sent/1min"):
                    self.mqttcore.bytes_1ms_text.config(state=NORMAL)
                    self.mqttcore.bytes_1ms_text.delete(1.0, END)
                    self.mqttcore.bytes_1ms_text.insert(END, msg.payload)
                    self.mqttcore.bytes_1ms_text.config(state=DISABLED)
                elif(msg.topic == "$SYS/broker/load/bytes/received/1min"):
                    self.mqttcore.bytes_1mr_text.config(state=NORMAL)
                    self.mqttcore.bytes_1mr_text.delete(1.0, END)
                    self.mqttcore.bytes_1mr_text.insert(END, msg.payload)
                    self.mqttcore.bytes_1mr_text.config(state=DISABLED)
                elif(msg.topic == "$SYS/broker/load/bytes/sent/5min"):
                    self.mqttcore.bytes_5ms_text.config(state=NORMAL)
                    self.mqttcore.bytes_5ms_text.delete(1.0, END)
                    self.mqttcore.bytes_5ms_text.insert(END, msg.payload)
                    self.mqttcore.bytes_5ms_text.config(state=DISABLED)
                elif(msg.topic == "$SYS/broker/load/bytes/received/5min"):
                    self.mqttcore.bytes_5mr_text.config(state=NORMAL)
                    self.mqttcore.bytes_5mr_text.delete(1.0, END)
                    self.mqttcore.bytes_5mr_text.insert(END, msg.payload)
                    self.mqttcore.bytes_5mr_text.config(state=DISABLED)
                elif(msg.topic == "$SYS/broker/load/bytes/sent/15min"):
                    self.mqttcore.bytes_15ms_text.config(state=NORMAL)
                    self.mqttcore.bytes_15ms_text.delete(1.0, END)
                    self.mqttcore.bytes_15ms_text.insert(END, msg.payload)
                    self.mqttcore.bytes_15ms_text.config(state=DISABLED)
                elif(msg.topic == "$SYS/broker/load/bytes/received/15min"):
                    self.mqttcore.bytes_15mr_text.config(state=NORMAL)
                    self.mqttcore.bytes_15mr_text.delete(1.0, END)
                    self.mqttcore.bytes_15mr_text.insert(END, msg.payload)
                    self.mqttcore.bytes_15mr_text.config(state=DISABLED)
                elif(msg.topic == "$SYS/broker/bytes/sent"):
                    self.mqttcore.bytes_ts_text.config(state=NORMAL)
                    self.mqttcore.bytes_ts_text.delete(1.0, END)
                    self.mqttcore.bytes_ts_text.insert(END, msg.payload)
                    self.mqttcore.bytes_ts_text.config(state=DISABLED)
                elif(msg.topic == "$SYS/broker/bytes/received"):
                    self.mqttcore.bytes_tr_text.config(state=NORMAL)
                    self.mqttcore.bytes_tr_text.delete(1.0, END)
                    self.mqttcore.bytes_tr_text.insert(END, msg.payload)
                    self.mqttcore.bytes_tr_text.config(state=DISABLED)

                elif(msg.topic == "$SYS/broker/messages/per second/sent"):
                    self.mqttcore.messages_ss_text.config(state=NORMAL)
                    self.mqttcore.messages_ss_text.delete(1.0, END)
                    self.mqttcore.messages_ss_text.insert(END, msg.payload)
                elif(msg.topic == "$SYS/broker/messages/per second/received"):
                    self.mqttcore.messages_sr_text.config(state=NORMAL)
                    self.mqttcore.messages_sr_text.delete(1.0, END)
                    self.mqttcore.messages_sr_text.insert(END, msg.payload)
                elif(msg.topic == "$SYS/broker/load/messages/sent/1min"):
                    self.mqttcore.messages_1ms_text.config(state=NORMAL)
                    self.mqttcore.messages_1ms_text.delete(1.0, END)
                    self.mqttcore.messages_1ms_text.insert(END, msg.payload)
                elif(msg.topic == "$SYS/broker/load/messages/received/1min"):
                    self.mqttcore.messages_1mr_text.config(state=NORMAL)
                    self.mqttcore.messages_1mr_text.delete(1.0, END)
                    self.mqttcore.messages_1mr_text.insert(END, msg.payload)
                elif(msg.topic == "$SYS/broker/load/messages/sent/5min"):
                    self.mqttcore.messages_5ms_text.config(state=NORMAL)
                    self.mqttcore.messages_5ms_text.delete(1.0, END)
                    self.mqttcore.messages_5ms_text.insert(END, msg.payload)
                elif(msg.topic == "$SYS/broker/load/messages/received/5min"):
                    self.mqttcore.messages_5mr_text.config(state=NORMAL)
                    self.mqttcore.messages_5mr_text.delete(1.0, END)
                    self.mqttcore.messages_5mr_text.insert(END, msg.payload)
                elif(msg.topic == "$SYS/broker/load/messages/sent/15min"):
                    self.mqttcore.messages_15ms_text.config(state=NORMAL)
                    self.mqttcore.messages_15ms_text.delete(1.0, END)
                    self.mqttcore.messages_15ms_text.insert(END, msg.payload)
                elif(msg.topic == "$SYS/broker/load/messages/received/15min"):
                    self.mqttcore.messages_15mr_text.config(state=NORMAL)
                    self.mqttcore.messages_15mr_text.delete(1.0, END)
                    self.mqttcore.messages_15mr_text.insert(END, msg.payload)
                elif(msg.topic == "$SYS/broker/messages/sent"):
                    self.mqttcore.messages_ts_text.config(state=NORMAL)
                    self.mqttcore.messages_ts_text.delete(1.0, END)
                    self.mqttcore.messages_ts_text.insert(END, msg.payload)
                elif(msg.topic == "$SYS/broker/messages/received"):
                    self.mqttcore.messages_tr_text.config(state=NORMAL)
                    self.mqttcore.messages_tr_text.delete(1.0, END)
                    self.mqttcore.messages_tr_text.insert(END, msg.payload)

#                elif(msg.topic == "$SYS/broker/publish/per second/sent"):
#                    self.mqttcore.publish_ss_text.config(state=NORMAL)
#                    self.mqttcore.publish_ss_text.delete(1.0, END)
#                    self.mqttcore.publish_ss_text.insert(END, msg.payload)
#                elif(msg.topic == "$SYS/broker/publish/per second/received"):
#                    self.mqttcore.publish_sr_text.config(state=NORMAL)
#                    self.mqttcore.publish_sr_text.delete(1.0, END)
#                    self.mqttcore.publish_sr_text.insert(END, msg.payload)
                elif(msg.topic == "$SYS/broker/load/publish/sent/1min"):
                    self.mqttcore.publish_1ms_text.config(state=NORMAL)
                    self.mqttcore.publish_1ms_text.delete(1.0, END)
                    self.mqttcore.publish_1ms_text.insert(END, msg.payload)
                elif(msg.topic == "$SYS/broker/load/publish/received/1min"):
                    self.mqttcore.publish_1mr_text.config(state=NORMAL)
                    self.mqttcore.publish_1mr_text.delete(1.0, END)
                    self.mqttcore.publish_1mr_text.insert(END, msg.payload)
                elif(msg.topic == "$SYS/broker/load/publish/sent/5min"):
                    self.mqttcore.publish_5ms_text.config(state=NORMAL)
                    self.mqttcore.publish_5ms_text.delete(1.0, END)
                    self.mqttcore.publish_5ms_text.insert(END, msg.payload)
                elif(msg.topic == "$SYS/broker/load/publish/received/5min"):
                    self.mqttcore.publish_5mr_text.config(state=NORMAL)
                    self.mqttcore.publish_5mr_text.delete(1.0, END)
                    self.mqttcore.publish_5mr_text.insert(END, msg.payload)
                elif(msg.topic == "$SYS/broker/load/publish/sent/15min"):
                    self.mqttcore.publish_15ms_text.config(state=NORMAL)
                    self.mqttcore.publish_15ms_text.delete(1.0, END)
                    self.mqttcore.publish_15ms_text.insert(END, msg.payload)
                elif(msg.topic == "$SYS/broker/load/publish/received/15min"):
                    self.mqttcore.publish_15mr_text.config(state=NORMAL)
                    self.mqttcore.publish_15mr_text.delete(1.0, END)
                    self.mqttcore.publish_15mr_text.insert(END, msg.payload)
#                elif(msg.topic == "$SYS/broker/publish/messages/sent"):
#                    self.mqttcore.publish_ts_text.config(state=NORMAL)
#                    self.mqttcore.publish_ts_text.delete(1.0, END)
#                    self.mqttcore.publish_ts_text.insert(END, msg.payload)
#                elif(msg.topic == "$SYS/broker/publish/messages/received"):
#                    self.mqttcore.publish_tr_text.config(state=NORMAL)
#                    self.mqttcore.publish_tr_text.delete(1.0, END)
#                    self.mqttcore.publish_tr_text.insert(END, msg.payload)

#                elif(msg.topic == "$SYS/broker/connections/per second/sent"):
#                    self.mqttcore.connections_s_text.config(state=NORMAL)
#                    self.mqttcore.connections_s_text.delete(1.0, END)
#                    self.mqttcore.connections_s_text.insert(END, msg.payload)
                elif(msg.topic == "$SYS/broker/load/connections/1min"):
                    self.mqttcore.connections_1m_text.config(state=NORMAL)
                    self.mqttcore.connections_1m_text.delete(1.0, END)
                    self.mqttcore.connections_1m_text.insert(END, msg.payload)
                elif(msg.topic == "$SYS/broker/load/connections/5min"):
                    self.mqttcore.connections_5m_text.config(state=NORMAL)
                    self.mqttcore.connections_5m_text.delete(1.0, END)
                    self.mqttcore.connections_5m_text.insert(END, msg.payload)
                elif(msg.topic == "$SYS/broker/load/connections/15min"):
                    self.mqttcore.connections_15m_text.config(state=NORMAL)
                    self.mqttcore.connections_15m_text.delete(1.0, END)
                    self.mqttcore.connections_15m_text.insert(END, msg.payload)
#                elif(msg.topic == "$SYS/broker/connections/messages/sent"):
#                    self.mqttcore.connections_t_text.config(state=NORMAL)
#                    self.mqttcore.connections_t_text.delete(1.0, END)
#                    self.mqttcore.connections_t_text.insert(END, msg.payload)

#                elif(msg.topic == "$SYS/broker/connections/per second/sent"):
#                    self.mqttcore.sockets_s_text.config(state=NORMAL)
#                    self.mqttcore.sockets_s_text.delete(1.0, END)
#                    self.mqttcore.sockets_s_text.insert(END, msg.payload)
                elif(msg.topic == "$SYS/broker/load/sockets/1min"):
                    self.mqttcore.sockets_1m_text.config(state=NORMAL)
                    self.mqttcore.sockets_1m_text.delete(1.0, END)
                    self.mqttcore.sockets_1m_text.insert(END, msg.payload)
                elif(msg.topic == "$SYS/broker/load/sockets/5min"):
                    self.mqttcore.sockets_5m_text.config(state=NORMAL)
                    self.mqttcore.sockets_5m_text.delete(1.0, END)
                    self.mqttcore.sockets_5m_text.insert(END, msg.payload)
                elif(msg.topic == "$SYS/broker/load/sockets/15min"):
                    self.mqttcore.sockets_15m_text.config(state=NORMAL)
                    self.mqttcore.sockets_15m_text.delete(1.0, END)
                    self.mqttcore.sockets_15m_text.insert(END, msg.payload)
#                elif(msg.topic == "$SYS/broker/sockets/messages/sent"):
#                    self.mqttcore.sockets_t_text.config(state=NORMAL)
#                    self.mqttcore.sockets_t_text.delete(1.0, END)
#                    self.mqttcore.sockets_t_text.insert(END, msg.payload)

                elif(msg.topic == "$SYS/broker/clients/active"):
                    self.mqttcore.active_text.config(state=NORMAL)
                    self.mqttcore.active_text.delete(1.0, END)
                    self.mqttcore.active_text.insert(END, msg.payload)
                elif(msg.topic == "$SYS/broker/clients/inactive"):
                    self.mqttcore.inactive_text.config(state=NORMAL)
                    self.mqttcore.inactive_text.delete(1.0, END)
                    self.mqttcore.inactive_text.insert(END, msg.payload)
                elif(msg.topic == "$SYS/broker/clients/total"):
                    self.mqttcore.clients_total_text.config(state=NORMAL)
                    self.mqttcore.clients_total_text.delete(1.0, END)
                    self.mqttcore.clients_total_text.insert(END, msg.payload)
                elif(msg.topic == "$SYS/broker/clients/expired"):
                    self.mqttcore.expired_text.config(state=NORMAL)
                    self.mqttcore.expired_text.delete(1.0, END)
                    self.mqttcore.expired_text.insert(END, msg.payload)
                elif(msg.topic == "$SYS/broker/clients/maximum"):
                    self.mqttcore.max_text.config(state=NORMAL)
                    self.mqttcore.max_text.delete(1.0, END)
                    self.mqttcore.max_text.insert(END, msg.payload)

                elif(msg.topic == "$SYS/broker/uptime"):
                    self.mqttcore.uptime_text.config(state=NORMAL)
                    self.mqttcore.uptime_text.delete(1.0, END)
                    t = msg.payload.split(" ")
                    uptime = datetime.timedelta(seconds=int(t[0]))
                    uptime_text = str(uptime)
                    self.mqttcore.uptime_text.insert(END, uptime_text) 
                elif(msg.topic == "$SYS/broker/heap/current size"):
                    self.mqttcore.heap_text.config(state=NORMAL)
                    self.mqttcore.heap_text.delete(1.0, END)
                    self.mqttcore.heap_text.insert(END, msg.payload)
                elif(msg.topic == "$SYS/broker/heap/maximum size"):
                    self.mqttcore.heap_max_text.config(state=NORMAL)
                    self.mqttcore.heap_max_text.delete(1.0, END)
                    self.mqttcore.heap_max_text.insert(END, msg.payload)

                elif(msg.topic == "$SYS/broker/retained messages/count"):
                    self.mqttcore.retained_text.config(state=NORMAL)
                    self.mqttcore.retained_text.delete(1.0, END)
                    self.mqttcore.retained_text.insert(END, msg.payload)
                elif(msg.topic == "$SYS/broker/messages/stored"):
                    self.mqttcore.stored_text.config(state=NORMAL)
                    self.mqttcore.stored_text.delete(1.0, END)
                    self.mqttcore.stored_text.insert(END, msg.payload)
                elif(msg.topic == "$SYS/broker/messages/dropped"):
                    self.mqttcore.dropped_text.config(state=NORMAL)
                    self.mqttcore.dropped_text.delete(1.0, END)
                    self.mqttcore.dropped_text.insert(END, msg.payload)
                elif(msg.topic == "$SYS/broker/messages/inflight"):
                    self.mqttcore.inflight_text.config(state=NORMAL)
                    self.mqttcore.inflight_text.delete(1.0, END)
                    self.mqttcore.inflight_text.insert(END, msg.payload)
                    self.mqttcore.inflight_text.config(state=DISABLED)
                elif(msg.topic == "$SYS/broker/subscriptions/count"):
                    self.mqttcore.subscriptions_text.config(state=NORMAL)
                    self.mqttcore.subscriptions_text.delete(1.0, END)
                    self.mqttcore.subscriptions_text.insert(END, msg.payload)
                    self.mqttcore.subscriptions_text.config(state=DISABLED)

                elif((msg.topic == "$SYS/broker/log/E") or 
                     (msg.topic == "$SYS/broker/log/N") or 
                     (msg.topic == "$SYS/broker/log/I") or 
                     (msg.topic == "$SYS/broker/log/W")):
                    self.mqttcore.log_text.config(state=NORMAL)
                    self.mqttcore.log_text.insert(END, msg.payload)
                    self.mqttcore.log_text.insert(END, "\n")
                    self.mqttcore.log_text.vbar.set(0.9, 0.91)
                    self.mqttcore.log_text.config(state=DISABLED)

if __name__ == "__main__":
    daemon = MyDaemon('/tmp/' + APPNAME + '.pid')
    daemon.run()
