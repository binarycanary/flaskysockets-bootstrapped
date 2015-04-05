"""
    Flaskysockets - Barebones SPA template for websockets communication with flask. This has
        been done countless times already.. I did my own to learn more about websockets and
        to keep it dead simple and stripped down. Gevent intentionally not included.
        Goal was to make it easy to integrate into something like a initializr.com template.

    Built using input from blogs, stackoverflow, etc:
        http://stackoverflow.com/questions/323972/is-there-any-way-to-kill-a-thread-in-python
        http://blog.miguelgrinberg.com/post/easy-websockets-with-flask-and-gevent
        http://www.alexhadik.com/blog/2015/1/29/using-socketio-with-python-and-flask-on-heroku
"""

from flask import Flask, render_template
from flask.ext.socketio import SocketIO
import json
import time
import threading

app = Flask(__name__)
socketio = SocketIO(app)

# Used by top section of the page with the start/stop buttons
class KillableThread(threading.Thread):

    def __init__(self, name='KillableThread'):
        """ constructor, setting initial variables """
        self._stopevent = threading.Event( )
        self._sleepperiod = 1.0
        threading.Thread.__init__(self, name=name)
    def run(self):
        """ main control loop """
        # print "%s starts" % (self.getName( ),)
        count = 0
        while not self._stopevent.isSet( ):
            count += 1
            # print "loop %d" % (count,)
            socketio.emit('newlogentry', {'logentry': 'Loop count from server: '+str(count)})
            self._stopevent.wait(self._sleepperiod)
        # print "%s ends" % (self.getName(),)
    def stop(self, timeout=None):
        """ Stop the thread and wait for it to end. """
        self._stopevent.set( )
        threading.Thread.join(self, timeout)

# Required routing for Flask, rendering out index page
@app.route("/")
def index():
    return render_template('index.html',)
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Handlers for messages used by top section of the page with the start/stop buttons
@socketio.on('send_startlisten')
def handle_source(json_data):
    text = json_data['message'].encode('ascii', 'ignore')  # 'super awesome message'
    # Spin up a thread that shoots out a message every 5 seconds
    global t
    t = KillableThread('PacketScrapeJob')
    t.start()
@socketio.on('send_stoplisten')
def handle_source(json_data):
    text = json_data['message'].encode('ascii', 'ignore')  # 'super awesome message'
    t.stop()
# def runjob(threadnum):
#     threadnum = 1
#     print 'started thread number %d' % threadnum
#     for x in range(0, 5):
#         socketio.emit('newlogentry', {'logentry': 'Server Says: '+str(x+1)})
#         time.sleep(5)

# Handler for the bottom section of the page with textbox and echo button
@socketio.on('send_message')
def handle_source(json_data):
    text = json_data['message'].encode('ascii', 'ignore')
    socketio.emit('echo', {'echo': 'Echoed back: '+text})

# main
if __name__ == "__main__":
    # socketio.run(app)
    socketio.run(app, host='0.0.0.0') #listen on external ip
