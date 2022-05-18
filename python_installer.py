import logging
import os
import shlex
from subprocess import Popen, PIPE

login_obj = dict()


def cmd(command):
    p = Popen(shlex.split(command), stdin=PIPE, stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()

    if p.returncode != 0:
        logging.error('     Error executing command [%s]' % command)
        logging.error('     [%s]' % stderr)

    return {'exit_code': p.returncode, 'stdout': stdout, 'stderr': stderr}


def cloneRepo(login_obj):
    dirs = "C:\\Users\\{}".format(login_obj['username'])
    sub_dirs = dirs + "\\Bitcoin_Trading"

    if not os.path.exists(dirs):
        os.mkdir(dirs)
        logging.info("Directory {} created".format(dirs))
    else:
        logging.info("Directory {} already exists".format(dirs))

    os.chdir(dirs)
    if not os.path.exists(sub_dirs):
        repo_url = "https://github.com/Cliffcomplier/Bitcoin_Trading"
        cmd_clone = "git clone {}".format(repo_url)
        res = cmd(cmd_clone)

        if res['exit_code'] == 0:
            logging.info('    Clone done!')
        os.chdir(sub_dirs)

        cmd_update = "git submodule update --init"
        res = cmd(cmd_update)
    else:
        logging.info('git repo has already coloned.')
    login_obj['sub_dirs'] = sub_dirs


def install_xlwings(login_obj):
    xlwings_config_dirs = "C:\\Users\\{}\\.xlwings".format(login_obj['username'])
    debug_udf = "\"DEBUG UDFS\",\"False\""
    use_udf_server = "\"USE UDF SERVER\", \"False\""
    python_path = "\"PYTHONPATH\", \"{}\"".format(login_obj['sub_dirs'])
    udf_modules = "\"UDF MODULES\",\"\""
    interpreter = "\"INTERPRETER\",\"C:\Program Files\Python39\python.exe\""

    if not os.path.exists(xlwings_config_dirs):
        os.mkdir(xlwings_config_dirs)
        logging.info("xlwings directory {} created".format(xlwings_config_dirs))
    else:
        logging.info("xlwings directory {} already exists".format(xlwings_config_dirs))

    os.chdir(xlwings_config_dirs)

    if os.path.exists("xlwings.conf"):
        os.remove('xlwings.conf')

    with open("xlwings.conf", "w+") as f:
        f.write(debug_udf + "\r")
        f.write(use_udf_server + "\r")
        f.write(python_path + "\r")
        f.write(udf_modules + "\r")
        f.write(interpreter + "\r")
    logging.info("Generate xlwings.conf at \"{}\"".format(xlwings_config_dirs))
    try:
        cmd_xlw = "xlwings addins install"
        logging.info("    {}".format(cmd_xlw))
        cmd(cmd_xlw)
    except:
        logging.info("{} failed, pls run manually".format(cmd_xlw))
        print("{} failed, pls run manually".format(cmd_xlw))


login_obj = {'username': "Cliff"}
cloneRepo(login_obj)
install_xlwings(login_obj)
