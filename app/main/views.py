import os
import subprocess
from ..models import *
from flask import render_template
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
    status = ''

    if submit_form.validate_on_submit():
        data = submit_form.body.data
        res = judge(int(id), data)
        status = 'Pass' if res[0] == res[1] else 'Wrong'
    return render_template('problem.html', problem=problem,
                            res=res, form=submit_form, status=status)

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
        run(random_path)
        run(student_path, random_input_path)
        run(standard_path, random_input_path)

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
    if input_path:
        fp = os.popen(os.path.join(path, 'a.out 1>' + \
                      os.path.join(path, 'output')) + \
                      ' 0<%s' % input_path)
    else:
        fp = os.popen(os.path.join(path, 'a.out 1>' + os.path.join(path, 'output')))
    fp.close()

def read_output(path):
    output = ''
    with open(os.path.join(path, 'output')) as fp:
        output = fp.read()
    return output
