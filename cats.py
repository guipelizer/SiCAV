from flask import Flask, render_template, request, redirect, url_for, json, Response
from flaskext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash
import numpy as np
import cv2
from motion import Movement
from threading import Thread
from webcamvideostream import WebcamVideoStream
from random import randint

app = Flask(__name__) 
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'sel0630#'
app.config['MYSQL_DATABASE_DB'] = 'stefano_pelizer'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')  



@app.route('/gerenciamento')
def gerenciamento():
    return render_template('gerenciamento.html')



@app.route('/logs')
def logs():
    conn = mysql.connect()
    cursor = conn.cursor()
    query = 'SELECT log.data_hora, log.nome_funcionario, log.carro FROM log ORDER BY log.data_hora DESC'
    cursor.execute(query)
    logs = cursor.fetchall() 
    return render_template('logs.html', logs=logs)



@app.route('/showCadastroFuncionario')
def showCadastroFuncionario():
    return render_template('cadastroFuncionario.html')

@app.route('/cadastroFuncionario', methods=['POST'])
def cadastroFuncionario():
    name = request.form['inputName']
    cargo = request.form['inputJob']

    print("oi2", name, cargo)

    if name and cargo:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_cadastraFuncionario',(name, cargo))
        data = cursor.fetchall()
        if len(data) is 0:
            conn.commit()
            print("deu certo")
            return redirect(url_for('showCadastroFuncionario'))
        else:
            print("deu errado")
            return json.dumps({'error':str(data[0])})
    else:
        return json.dumps({'html':'<span>Enter the required fields !!</span>'})



@app.route('/showCadastroCarro')
def showCadastroCarro():
    conn = mysql.connect()
    cursor = conn.cursor()
    query = 'SELECT nome FROM funcionario'
    cursor.execute(query)
    funcionarios_tuple = cursor.fetchall() 
    funcionarios = [func[0] for func in funcionarios_tuple]
    print(funcionarios)
    print(type(funcionarios))
    return render_template('cadastroCarro.html', funcionarios=funcionarios)

@app.route('/cadastroCarro', methods=['POST'])
def cadastroCarro():
    name = request.form['inputName']
    plate = request.form['inputPlate']
    model = request.form['inputModel']
    
    print("oi2", name, plate, model)

    if plate and model and name:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_cadastraCarro',(plate, model, name))
        data = cursor.fetchall()
        if len(data) is 0:
            conn.commit()
            print("deu certo 2")
            return redirect(url_for('showCadastroCarro'))
        else:
            print("deu errado 2")
            return json.dumps({'error':str(data[0])})
    else:
        return json.dumps({'html':'<span>Enter the required fields !!</span>'})




@app.route('/showRemoverFuncionario')
def showRemoverFuncionario():
    conn = mysql.connect()
    cursor = conn.cursor()
    query = 'SELECT nome FROM funcionario'
    cursor.execute(query)
    funcionarios_tuple = cursor.fetchall() 
    funcionarios = [func[0] for func in funcionarios_tuple]
    print(funcionarios)
    print(type(funcionarios))
    return render_template('removerFuncionario.html', funcionarios=funcionarios)

@app.route('/removerFuncionario', methods=['POST'])
def removerFuncionario(): 
    name = request.form['inputName']
    
    print("oi2", name)

    if name:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_removeFuncionario', (name, ))
        data = cursor.fetchall()
        if len(data) is 0:
            conn.commit()
            print("deu certo 2")
            return redirect(url_for('showRemoverFuncionario'))
        else:
            print("deu errado 2")
            return json.dumps({'error':str(data[0])})
    else:
        return json.dumps({'html':'<span>Enter the required fields !!</span>'})


@app.route('/showRemoverCarro')
def showRemoverCarro():
    conn = mysql.connect()
    cursor = conn.cursor()
    query = 'SELECT placa FROM carro'
    cursor.execute(query)
    carros_tuple = cursor.fetchall() 
    carros = [car[0] for car in carros_tuple]
    print(carros)
    print(type(carros))
    return render_template('removerCarro.html', carros=carros)

@app.route('/removerCarro', methods=['POST'])
def removerCarro(): 
    plate = request.form['inputPlate']
    
    print("oi2", plate)

    if plate:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_removeCarro', (plate, ))
        data = cursor.fetchall()
        if len(data) is 0:
            conn.commit()
            print("deu certo 2")
            return redirect(url_for('showRemoverCarro'))
        else:
            print("deu errado 2")
            return json.dumps({'error':str(data[0])})
    else:
        return json.dumps({'html':'<span>Enter the required fields !!</span>'})



def gen(camera):
    firstFrame = None
    while True:
        nextFrame = camera.read()
        frame = cv2.imencode('.jpg', nextFrame)[1].tobytes()
        yield(b'--frame\r\n'
             b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(camera),
            mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/fota')
def fota():
    return render_template('fota.html')



@app.route('/showSignUp')
def showSignUp():
    return render_template('signup_template.html')

@app.route('/signUp',methods=['POST'])
def signUp():
    #read the posted values from the UI
    _name = request.form['inputName']
    _email = request.form['inputEmail']
    _password = request.form['inputPassword']

    #validate the received values
    if _name and _email and _password:
        conn = mysql.connect()
        cursor = conn.cursor()
        _hashed_password = generate_password_hash(_password)
        cursor.callproc('sp_createUser',(_name,_email,_hashed_password))
        data = cursor.fetchall()
        if len(data) is 0:
            conn.commit()
            return json.dumps({'message':'User created sucessfully!'})
        else:
            return json.dumps({'error':str(data[0])})
    else:
        return json.dumps({'html':'<span>Enter the required fields !!</span>'})

@app.route('/refresh',methods=['POST'])
def refresh():
    return json.dumps({'plate': motion.plate, 'nome': motion.nome, 'carro': motion.modelo, 'cargo': motion.cargo})

        
if __name__ == '__main__':
    camera = WebcamVideoStream(src='/home/pi/camera1.mp4', measuring=True).start() 
    motion = Movement(camera, mysql).start() 
    app.run(host="0.0.0.0", threaded = True)
