import time

from flask import Flask, render_template, Response, stream_with_context
from flask_socketio import SocketIO, emit
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app, resources={r"/*": {"origins": "*"}})

# 클라이언트에서 연결되었을 때 처리하는 이벤트
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('message', {'data': 'Connected to server!'})

# 클라이언트에서 보내는 'signal' 이벤트 처리
@socketio.on('signal')
def handle_signal(data):
    print('Received signal:', data)
    # 받은 데이터를 처리하거나, 필요에 따라 클라이언트에게 다시 전송할 수 있습니다.
    emit('response', {'data': 'Signal received'}, broadcast=True)

# 클라이언트가 연결 해제되었을 때 처리하는 이벤트
@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

# @app.route("/stream")
# def stream():
#     def event_stream():
#         while True:
#             # 클라이언트에게 데이터를 전송합니다.
#             time.sleep(1)
#             yield 'data: {}\n\n'.format('Hello, world!')
#
#     return Response(stream_with_context(event_stream()), content_type='text/event-stream')

if __name__ == '__main__':
    # Flask-SocketIO는 일반 Flask와 다르게 socketio.run()을 사용해 서버를 실행합니다.
    socketio.run(app, host='127.0.0.1', port=5002, debug=True)
