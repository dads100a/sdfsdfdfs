from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import db, User, Transaction, Check
from database import db, User, Transaction


app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bank.db'
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        id = request.form['id']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone = request.form['phone']
        password = request.form['password']

        new_user = User(id=id, first_name=first_name, last_name=last_name,
                        phone=phone, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful!')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        id = request.form['id']
        password = request.form['password']
        user = User.query.filter_by(id=id, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('account', user_id=user.id))
        flash('Invalid credentials')
    return render_template('login.html')


@app.route('/account/<user_id>', methods=['GET', 'POST'])
def account(user_id):
    user = User.query.get(user_id)
    if request.method == 'POST':
        if 'deposit' in request.form:
            amount = float(request.form['amount'])
            user.balance += amount
            db.session.add(Transaction(amount=amount, user=user, type='deposit'))
            db.session.commit()
            flash('Deposit successful!')
        elif 'transfer' in request.form:
            recipient_id = request.form['recipient_id']
            amount = float(request.form['amount'])
            recipient = User.query.get(recipient_id)
            if recipient and user.balance >= amount:
                user.balance -= amount
                recipient.balance += amount
                db.session.add(Transaction(amount=-amount, user=user, recipient_id=recipient.id, type='transfer'))
                db.session.add(Transaction(amount=amount, user=recipient, type='transfer'))
                db.session.commit()
                flash('Transfer successful!')
            else:
                flash('Transfer failed. Check recipient ID or insufficient balance.')
    transactions = Transaction.query.filter((Transaction.user_id == user.id) | (Transaction.recipient_id == user.id)).all()
    return render_template('account.html', user=user, transactions=transactions)
    


@app.route('/transactions')
def transactions():
    user = User.query.get(session['user_id'])
    transactions = Transaction.query.filter((Transaction.user_id == user.id) | (Transaction.recipient_id == user.id)).all()
    return render_template('transactions.html', transactions=transactions)

# Консоль разработчика - показывает всех пользователей и их балансы
@app.route('/admin')
def admin():
    # Получаем список всех пользователей из базы данных
    users = User.query.all()
    # Рендерим шаблон admin.html, передавая туда список пользователей
    return render_template('admin.html', users=users)

@app.route('/checks', methods=['GET', 'POST'])
def checks():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        if 'create_check' in request.form:
            name = request.form['check_name']
            code = request.form['check_code']
            amount = float(request.form['check_amount'])

            if len(code) == 4:  # Проверка на длину кода
                new_check = Check(name=name, code=code, amount=amount, user=user)
                db.session.add(new_check)
                db.session.commit()
                flash('Чек создан успешно!')
            else:
                flash('Код чека должен состоять из 4 чисел.')

        elif 'input_check' in request.form:
            code = request.form['check_code_input']
            check = Check.query.filter_by(code=code).first()
            if check:
                return redirect(url_for('pay_check', check_id=check.id))
            else:
                flash('Чек с таким кодом не найден.')

    checks = Check.query.filter_by(user_id=user.id).all()
    return render_template('checks.html', user=user, checks=checks)

@app.route('/pay_check/<check_id>', methods=['GET', 'POST'])
def pay_check(check_id):
    check = Check.query.get(check_id)
    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        if user.balance >= check.amount:
            user.balance -= check.amount
            check.user.balance += check.amount
            db.session.commit()
            flash('Оплата успешна!')
            return redirect(url_for('account', user_id=user.id))
        else:
            flash('Недостаточно средств.')

    return render_template('pay_check.html', check=check)


@app.route('/pay_services', methods=['GET', 'POST'])
def pay_services():
    if request.method == 'POST':
        # Получаем выбранный объем трафика
        amount_mb = request.form['amount_mb']
        return redirect(url_for('pay_internet', amount_mb=amount_mb))  # перенаправляем на маршрут оплаты конкретного объема
    return render_template('pay_services.html')

@app.route('/pay_internet', methods=['GET', 'POST'])
def pay_internet():
    amount_mb = request.args.get('amount_mb', type=int)
    if request.method == 'POST':
        # Рассчитываем стоимость
        cost = amount_mb * 10  # 10 руб за 1 МБ
        user = User.query.get(session['user_id'])
        
        # Проверяем, достаточно ли средств у пользователя
        if user.balance >= cost:
            # Списываем средства с баланса пользователя
            user.balance -= cost
            
            # Найдите пользователя с ID 56565656 и зачислите средства
            recipient = User.query.get('56565656')  # Получаем пользователя с айди '56565656'
            recipient.balance += cost
            
            # Делаем коммит для сохранения изменений в базе данных
            db.session.commit()
            
            # Сообщение об успешной оплате
            flash(f'Оплата на {amount_mb} МБ успешна! Списано {cost} руб.')
            return redirect(url_for('account', user_id=user.id))
        else:
            flash('Недостаточно средств для оплаты!')
    
    return render_template('pay_internet.html', amount=amount_mb, cost=amount_mb * 10)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)