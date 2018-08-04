import sys
sys.path.append("/var/www/FlaskApp/FlaskApp")
import os

from flask import Flask, render_template, flash, request, url_for, redirect, session
from content_management import Content

from wtforms import Form, BooleanField, TextField, PasswordField, validators
from passlib.hash import sha256_crypt
from MySQLdb import escape_string as thwart

from functools import wraps

from dbconnect import connection
import gc

TOPIC_DICT = Content()

app = Flask(__name__)
app.secret_key = os.urandom(12) 

@app.route('/')
def homepage():
    return render_template("header.html")

#@app.route('/slashboard/')
@app.route('/dashboard/')
def dashboard():
    #return ("hi")
    #flash("flash test!!!")
    print(session)
    return render_template("dashboard.html", TOPIC_DICT = TOPIC_DICT)
    #return render_template("dashboard.html")

@app.route('/jewelry/')
def jewelry():
    return render_template("jewelry.html")

@app.route('/watches/')
def watches():
    return render_template("watches.html")

@app.route('/fragrance/')
def fragrance():
    return render_template("fragrance.html")

@app.errorhandler(404)
def page_not_found(e):
    #return ("404")
    return render_template("404.html")

@app.errorhandler(405)
def page_not_found(e):
    #return ("405")
    return render_template("405.html")

@app.route('/slashboard/')
def slashboard():
    try:
        return render_template("dashboard.html", TOPIC_DICT = TOPIC_DICT)
    except Exception as e:
#        return(str(e))
        return render_template("500.html", error=e)

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('login_page'))

    return wrap

@app.route("/logout/")
@login_required
def logout():
   session.clear()
   flash("You have been logged out!")
   #c.close()
   #conn.close()
   gc.collect()
   return redirect(url_for('homepage'))


@app.route('/login/', methods=["GET","POST"])
def login_page():
    print (request)
    error = ''
    try:
        c, conn = connection()
        if request.method == "POST":

            c.execute("SELECT * FROM users WHERE username = (%s)", (thwart(request.form['username']),))

            data = c.fetchone()[2] 

            if sha256_crypt.verify(request.form['password'], data):
                session['logged_in'] = True
                session['username'] = request.form['username']
                print(session)
                print(session['username'])

                flash("You are now logged in")
                return redirect(url_for("dashboard"))

            else:
                #error = "Invalid credentials(1), try again."
                error = "Password is not correct, try again."

        c.close()
        conn.close()
        #gc.collect()

        return render_template("login.html", error = error)

    except Exception as e:
        #flash(e)
        #error = "Invalid credentials(2), try again."
        error = "User does not exist, please signup first."
        return render_template("login.html", error = error)  
		

class RegistrationForm(Form):
   username = TextField('Username', [validators.Length(min=4, max=20)])
   email = TextField('Email Address', [validators.Length(min=6, max=50)])
   password = PasswordField('Password', [validators.Required(),
		validators.EqualTo('confirm', message="Passwords must match.")])
   confirm = PasswordField('Repeat Password')

   accept_tos = BooleanField('I accept the <a href="/tos/">Terms of Service</a> and the <a href="/privacy/">Privacy Notice</a>',[validators.Required()])


@app.route('/register/',methods=['GET','POST'])
def register_page():
    try:
       print (request)
       form = RegistrationForm(request.form) 

       if request.method == "POST" and form.validate():
          username = form.username.data
          email = form.email.data
          password = sha256_crypt.encrypt((str(form.password.data)))

          c, conn = connection()

          x = c.execute("SELECT * FROM users WHERE username = (%s)", (thwart(username),))

          if int(x) > 0:
             flash("That username already exists, please choose another")
             return render_template('register.html', form=form)

          else:
             c.execute("INSERT INTO users (username, password, email, tracking) VALUES (%s, %s, %s, %s)", (thwart(username), thwart(password), thwart(email), thwart("/abc")))

             conn.commit()
             flash("Thanks for registration!")
             c.close()
             conn.close()
             #gc.collect()

             return redirect(url_for('dashboard'))

       return render_template("register.html", form=form)


    except Exception as e:
       return(str(e))

class OrderForm(Form):
   productid = TextField('Product Id', [validators.Length(min=3, max=3)])
   orderqty = TextField('Order Quantity', [validators.Length(min=1, max=3)])
   confirm = BooleanField('Confirm ?',[validators.Required()])


@app.route('/order/', methods=['GET','POST'])
def order_page():
    try:
       #form = OrderForm(request.POST)
       form = OrderForm(request.form)

       if request.method == "POST" and form.validate():
          productid = form.productid.data
          orderqty = form.orderqty.data

          c, conn = connection()
          x = c.execute("SELECT * FROM products WHERE productid = (%s)", (thwart(productid),))

          if int(x) > 0 and form.confirm:
             price = c.fetchone()[2]
             print(session['username'])
             username = session['username']
             totalprice = int(orderqty) * int(price)
             c.execute("INSERT INTO orders (username, productid, orderqty, totalprice) VALUES (%s, %s, %s, %s)", (thwart(username), thwart(productid), thwart(orderqty), thwart(str(totalprice))))
             conn.commit()
             flash("Thanks for your order!")
          else:
             flash("That product does not exist, please choose another")
             return render_template('order.html', form=form)

          #c.close()
          #conn.close()
          #gc.collect()

          return redirect(url_for('dashboard'))

       return render_template("order.html", form=form)


    except Exception as e:
       return(str(e))



if __name__ == "__main__":
    app.run(debug=True)
