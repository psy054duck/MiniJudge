import os
import subprocess
from ..models import *
from flask import render_template, flash, redirect, url_for
from . import main
from .forms import *

state = {'Compile error':0, 'Time Limit':1, 'AC':2}

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/problem-list')
def problem_list():
    problem_list = Problem.query.all()
    return render_template('problem-list.html', problem_list=problem_list)

@main.route('/problem/<id>', methods=['GET', 'POST'])
def problem(id):
    problem = Problem.query.get_or_404(id)
    submit_form = SubmitForm()
    res = None

    if submit_form.validate_on_submit():
        data = submit_form.body.data
        res = judge(int(id), data)
    return render_template('problem.html', problem=problem,
                            res=res, form=submit_form)

@main.route('/create', methods=['GET', 'POST'])
def create():
    form = CreateProblemForm()

    if form.validate_on_submit():
        title = form.title.data
        detail = form.detail.data
        main = form.main.data
        rand = form.rand.data
        p = Problem(title=title, detail=detail)
        db.session.add(p)
        db.session.commit()
        createFile('problem/%d/standard/main.c' % p.id, main)
        createFile('problem/%d/random/main.c' % p.id, rand)
        flash('Success')
        return redirect(url_for('main.problem_list'))

    return render_template('create.html', form=form)

@main.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    p = Problem.query.get_or_404(id)
    form = CreateProblemForm()

    if form.validate_on_submit():
        p.title = form.title.data
        p.detail = form.detail.data
        p.main = form.main.data
        p.rand = form.rand.data
        db.session.add(p)
        db.session.commit()
        createFile('problem/%d/standard/main.c' % p.id, p.main)
        createFile('problem/%d/random/main.c' % p.id, p.rand)
        flash('Success')
        return redirect(url_for('main.problem', id=id))

    form.title.data = p.title
    form.detail.data = p.detail
    with open('problem/%s/standard/main.c' % id) as fp:
        form.main.data = fp.read()

    with open('problem/%s/random/main.c' % id) as fp:
        form.rand.data = fp.read()
    return render_template('edit.html', form=form)


def createFile(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as fp:
        fp.write(data)

def judge(id, data):
    num = 30
    if not os.path.exists('problem/%d' % id):
        os.mkdir('problem/%d' % id)
    if not os.path.exists('problem/%d/student' % id):
        os.mkdir('problem/%d/student' % id)

    student_path = 'problem/%d/student/' % id
    standard_path = 'problem/%d/standard/' % id
    random_path = 'problem/%d/random/' % id

    with open(os.path.join(student_path, 'main.c'), 'w') as fp:
        fp.write(data)

    student_compile_output = compile(student_path)
    standard_compile_output = compile(standard_path)
    random_compile_output = compile(random_path)

    if len(student_compile_output) != 0:
        return (0, student_compile_output)

    random_input_path = os.path.join(random_path, 'output')
    for i in range(num):
        try:
            run(random_path)
            run(student_path, random_input_path)
            run(standard_path, random_input_path)
        except Exception:
            rand_input = read_output(random_path)
            return (3, rand_input)

        student_output = read_output(student_path)
        standard_output = read_output(standard_path)

        if student_output != standard_output:
            break

    rand_input = read_output(random_path)
    if student_output == standard_output:
        return (1, student_output, standard_output, rand_input)
    else:
        return (2, student_output, standard_output, rand_input)

def compile(path):
    error = open(os.path.join(path, 'output'), 'w')
    subprocess.run(['gcc', os.path.join(path, 'main.c'),
                    '-o', os.path.join(path, 'a.out')],
                    stderr=error, stdout=error)
    # fp = os.popen('gcc ' + os.path.join(path, 'main.c') + \
    #               ' -o ' + os.path.join(path, 'a.out'))
    error.close()
    output = read_output(path)
    return output

def run(path, input_path=None):
    file_out = open(os.path.join(path, 'output'), 'w')
    if input_path:
        file_in = open(input_path)
        subprocess.run([os.path.join(path, 'a.out')],
                       stdout=file_out, stdin=file_in, timeout=1)
        file_in.close()
        # fp = os.popen(os.path.join(path, 'a.out 1>' + \
        #               os.path.join(path, 'output')) + \
        #               ' 0<%s' % input_path)
    else:
        subprocess.run([os.path.join(path, 'a.out')], stdout=file_out, timeout=1)
        # fp = os.popen(os.path.join(path, 'a.out 1>' + os.path.join(path, 'output')))
    file_out.close()
    # fp.close()

def read_output(path):
    output = ''
    with open(os.path.join(path, 'output')) as fp:
        output = fp.read()
    return output
