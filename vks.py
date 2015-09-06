#! /usr/bin/python
# -*- coding: utf-8 -*-


import sys
import os
import json
import random
from urllib import urlopen, urlencode
from time import sleep, time
from getpass import getpass as pwd_input


def touch(path):
    with open(path, 'a'):
        os.utime(path, None)


def create_file(file_path):
    if not os.path.exists(file_path):
        touch(file_path)


def rm_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)


def emoji_wipe(plain):
    array = bytearray(plain)
    while b'\xf0' in array:
        pos = array.find(b'\xf0')
        array = array.replace(array[pos:], array[pos+4:])
    while b'\xe2' in array:
        pos = array.find(b'\xe2')
        array = array.replace(array[pos:], array[pos+3:])
    return bytearray.decode(array, 'utf-8', errors='ignore')


def encoded_dict(in_dict):
    out_dict = {}
    for k, v in in_dict.iteritems():
        if isinstance(v, unicode):
            v = v.encode('utf-8')
        elif isinstance(v, str):
            v.decode('utf-8')
        out_dict[k] = v
    return out_dict


def request(method, params):
    try:
        sleep(basic_request_interval)
        request_str = '%s%s?%s' % (api_url, method, urlencode(encoded_dict(params)))
        try:
            r = urlopen(request_str).read()
            if '\"error\":\"need_captcha\"' in r:
                print '! CAPTHA THROWN !'
            json_data = json.loads(emoji_wipe(r))
        except Exception:
            print 'error: problems with connection'
            json_data = {}
        if 'error' in json_data:
            return {'error': json_data['error']}
        if not 'error' in json_data and not 'response' in json_data:
            return {'error': 'unknown error'}
        return json_data
    except Exception:
        print 'exception were thrown during api request'


def check_token(token):
    params = {'access_token': token}
    try:
        check = request('users.get', params)
    except Exception:
        return False
    check = check['response']
    check = check[0]
    if ('uid' in check) and ('first_name' in check) and ('last_name' in check):
        return True
    else:
        return False


def check_user():
    if os.path.exists(file_with_token):
        try:
            f = open(file_with_token, 'r')
            token = f.readline()
            f.close()
        except Exception:
            sys.exit('error while reading access token')
        name = '...'
        try:
            check = request('users.get', {'access_token': token})
            check = check['response']
            check = check[0]
            name = '%s %s' % (check['first_name'], check['last_name'])
        except Exception:
            pass
        print('Authorized as %s' % name)
        return name
    else:
        print('no user authorized')
        return False


def auth(login, pwd):
    fail = 'Failed to login'
    success = 'Login succesful'
    params = {}
    params['grant_type'] = 'password'
    params['client_id'] = '2274003'
    params['client_secret'] = 'hHbZxrka2uZ6jB1inYsH'
    params['username'] = login
    params['password'] = pwd
    request_str = 'https://oauth.vk.com/token?%s' % urlencode(params)
    try:
        r = urlopen(request_str).read()
        response = bytes.decode(r)
        if '\"error\":\"need_captcha\"' in response:
            print '! CAPTHA THROWN !'
            return
        json_data = json.loads(response)
    except Exception:
        print 'error: problems with connection'
        json_data = {}
    if 'error' in json_data:
        print(fail)
        return False
    if 'access_token' in json_data:
        try:
            f = open(file_with_token, 'w')
            f.write(json_data['access_token'])
            f.close()
            print success
            check_user()
            return True
        except Exception:
            print(fail)
            return False
    if not 'error' in json_data and not 'access_token' in json_data:
        print(fail)
        return False


def deauth():
    try:
        if os.path.exists(file_with_token):
            os.remove(file_with_token)
            print 'current user deauthorized'
        else:
            print('error: no user authorized')
    except Exception:
        print('error: unknown')


def load_str_value(fws):
    try:
        f = open(fws, 'rb')
        txt = f.read()
        f.close()
        if txt == '':
            raise Exception
    except Exception:
        print('error while reading data')
        return False
    return txt.decode('utf-8', errors='ignore')


def load_int_value(fwiv):
    try:
        f = open(fwiv, 'r')
        iv = int(f.read())
        f.close()
        if iv < 0:
            raise Exception
    except Exception:
        print('error while reading options')
        return False
    return iv


def load_int_list_data(fwl):
    res = []
    try:
        f = open(fwl, 'r')
        for line in f.readlines():
            try:
                res.append(int(line))
            except Exception:
                pass
        f.close()
    except Exception:
        print 'cannot read int list'
        return
    return res


def load_str_list_data(fwl):
    res = []
    try:
        f = open(fwl, 'r')
        data = f.read()
        res = data.split('\n')
        f.close()
        if len(res) > 0:
            res = res[:-1]
    except Exception:
        print 'cannot read string list'
        return
    return res


def dump_value(value, file_name):
    try:
        f = open(file_name, 'w')
        f.write(str(value))
        f.close()
    except Exception:
        print 'error: cannot write down data'


def log(line):
    try:
        f = open(file_with_log, 'a')
        f.write('%s\n' % str(line))
        f.close()
    except Exception:
        pass


def drop():
    print('invalid commandline arguments')


def man():
    print(' *** VKS - vk spam sender ***\n'
          '        by LuigiVampa92\n          enjoy =)\n\n'
          ' Commands:\n'
          'help - show this tutorial\n'
          'exit - close program\n'
          'auth - login to vk\n'
          'deauth - close current user session\n'
          'user - check current session\n'
          'task - assign task\n'
          'start - start spaming\n\n'
          ' Usage:\n'
          '- log in vk by command \"auth\"\n'
          '- assign new task by \"task\"\n'
          '- type \"start\"\n'
          ' Note some importatnt tips when you assigning a task:\n'
          '- text must be encoded in utf-8. You\'ll get msg preview. Make sure it\'s fine\n'
          '- interval between messages contains \"interval value\" +/- \"interval gap\"\n'
          '- choose interval value carefully. You don\'t need a captcha\n'
          '- group id must be its numeric value, not domain!'
    )


def progress_bar(value, total, dots):
    per = float(total/100.0)
    cur = float(value)/per
    per_dot = float(100.0/dots)
    dot_q = int(cur/per_dot)
    diff = dots - dot_q
    if diff < 0:
        diff = 0
    sys.stdout.write('*' * dot_q + '.' * diff + '   [ %.1f %s ]          \r' % (cur, '%'))


def get_group_name(gid):
    params = {}
    params['group_id'] = gid
    try:
        res = request('groups.getById', params)
        res = res['response']
        res = res[0]
        res = res['name']
    except Exception:
        return '???'
    return res


def get_group_members(gid, fwl):
    token = load_str_value(file_with_token)
    if not token:
        print 'error: no user authorized'
        return False
    rm_file(fwl)
    params = {}
    params['group_id'] = gid
    params['access_token'] = token
    params['count'] = 0

    try:
        res = request('groups.getMembers', params)
        res = res['response']
    except Exception:
        print 'error: problems with connection'
        return False

    gname = get_group_name(gid)
    count = res['count']
    print 'group: %s\nid: %s\nmembers: %s\n\ncollecting information about group members...\n' % (gname, gid, count)

    offset = 0
    it = count/1000
    if count % 1000 != 0:
        it += 1

    for i in range(it):
        params = {}
        params['group_id'] = gid
        params['access_token'] = token
        params['count'] = 1000
        params['offset'] = offset
        try:
            res = request('groups.getMembers', params)
            res = res['response']
            res = res['users']
        except Exception:
            print '\nerror: problems with connection'
            rm_file(fwl)
            return False
        progress_bar(offset, count, dots_in_pb)
        f = open(fwl, 'a')
        for id in res:
            f.write('%s\n' % str(id))
        f.close()
        offset += 1000
    progress_bar(count, count, dots_in_pb)
    print '\n'
    return True


def get_switch_map(text, fwsm):
    if not text:
        print 'error: cannot locate text'
        return
    l = len(text)
    lst = []
    for sym in range(l):
        if text[sym] in switch_syms.keys():
            lst.append(sym)
    try:
        f = open(fwsm, 'w')
        f.write(str(lst))
        f.close()
    except Exception:
        print 'error: cannot assign text'


def transformed_msg(msg, list_of_switches):
    res = u''
    for sym in range(len(msg)):
        if sym in list_of_switches:
            try:
                res += switch_syms[msg[sym]]
            except Exception:
                res += msg[sym]
        else:
            res += msg[sym]
    return res


def int_to_bin_str(num, signs):
    res = str(bin(num))[2:]
    if len(res) < signs:
        res = '0' * (signs - len(res)) + res
    return res


def get_switches_list_from_str(bit_sequence, list_with_msm):
    res = []
    for i in range(len(bit_sequence)):
        if bit_sequence[i] == '1':
            res.append(list_with_msm[i])
    return res


def get_dts(fwdts, fwul, fwmsm):
    try:
        recievers_list = load_int_list_data(fwul)
        list_of_switch_sym = json.loads(load_str_value(fwmsm))
        recievers_cnt = len(recievers_list)
        switches_cnt = len(list_of_switch_sym)
        random.seed(time())
        create_file(fwdts)
        f = open(fwdts, 'wb')
        for i in range(recievers_cnt):
            f.write('%s\n' % int_to_bin_str(random.getrandbits(switches_cnt), switches_cnt))
            progress_bar(i, recievers_cnt, dots_in_pb)
        f.close()
        progress_bar(recievers_cnt, recievers_cnt, dots_in_pb)
        print '\n'
        return True
    except Exception:
        print '\nerror: cannot create message scrumbles'
        return False


def send_msg(mts, uid, exc):
    token = load_str_value(file_with_token)
    if not token:
        print 'error: no user authorized'
        return
    params = {}
    params['user_id'] = uid
    params['access_token'] = token
    params['message'] = mts
    mid = -1
    try:
        res = request('messages.send', params)
        try:
            mid = res['response']
        except Exception:
            mid = -1
        try:
            f = open(exc, 'a')
            f.write('%s\n' % str(uid))
            f.close()
        except Exception:
            pass
    except Exception:
        print 'error: problems with connection'
        log('error. message didnt send to user %s\n' % str(uid))
        return
    params = {}
    params['access_token'] = token
    params['message_ids'] = mid
    try:
        request('messages.delete', params)
    except Exception:
        pass


def send_msg_dummy(mts, uid, exc):
    token = load_str_value(file_with_token)
    if not token:
        print 'error: no user authorized'
        return
    log('\nMESSAGE:\n%s\nSENT TO USER id%s\n' % (mts, uid))
    f = open(exc, 'a')
    f.write('%s\n' % str(uid))
    f.close()


def rm_options_values():
    rm_file(file_with_interval_value)
    rm_file(file_with_random_diff)
    rm_file(file_with_userlist)
    rm_file(file_with_exclusions)
    rm_file(file_with_msg_sym_map)
    rm_file(file_with_mts)
    rm_file(file_with_exclusions)
    rm_file(file_with_dts)


def new_task():
    iv = 0
    ivrd = 0
    msg = ''
    file_with_msg = ''
    gid = 0
    rm_options_values()
    try:
        gid = input('group id: ')
        iv = input('request interval: ')
        ivrd = input('interval gap: ')
        if ivrd >= iv or not isinstance(gid, int) or not isinstance(iv, int) or not isinstance(ivrd, int) or gid <= 0 or iv <= 0 or ivrd <= 0:
            raise Exception
    except Exception:
        print 'invalid input data'
        rm_options_values()
        return
    try:
        file_with_msg = raw_input('file with message: ')
        if file_with_msg == '':
            raise Exception
        msg = load_str_value(file_with_msg)
    except Exception:
        print 'error: cannot read message'
        rm_options_values()
        return
    dump_value(iv, file_with_interval_value)
    dump_value(ivrd, file_with_random_diff)

    f = open(file_with_mts, 'w')
    f.write(msg.replace('\r\n','\n').encode('utf-8',errors='ignore'))
    f.close()

    msg = load_str_value(file_with_mts)

    print '\noption values set'
    print '\nMESSAGE TEXT:\n%s\n' % msg

    get_switch_map(msg, file_with_msg_sym_map)

    print '\nprepaing recievers list...\n'
    step = get_group_members(gid, file_with_userlist)
    if not step:
        print 'task is not assigned'
        rm_options_values()
        return
    print '\nprepaing message text for sending...\n'
    step = get_dts(file_with_dts, file_with_userlist, file_with_msg_sym_map)
    if not step:
        print 'task is not assigned'
        rm_options_values()
        return
    create_file(file_with_exclusions)
    print '\n task assigned succesfully'


def start():
    try:
        token = load_str_value(file_with_token)
        iv = load_int_value(file_with_interval_value)
        ivrd = load_int_value(file_with_random_diff)
        if ivrd >= iv or not isinstance(iv, int) or not isinstance(ivrd, int) or iv <= 0 or ivrd <= 0:
            raise Exception
        print '\n'
        msg = load_str_value(file_with_mts)
        list_of_switch_sym = json.loads(load_str_value(file_with_msg_sym_map))
        list_of_recievers =load_int_list_data(file_with_userlist)
        if list_of_recievers == []:
            raise Exception
        list_of_exclusions = load_int_list_data(file_with_exclusions)
        list_of_dts = load_str_list_data(file_with_dts)
        if len(list_of_recievers) != len(list_of_dts):
            raise Exception
    except Exception:
        print 'task is not ready or data corrupted. cannot start'
        return
    if not check_token(token):
        print 'access token is not valid. cannot start'
        return
    iterations = len(list_of_recievers)
    for i in range(iterations):
        progress_bar(i, iterations, dots_in_pb)
        round_switches = get_switches_list_from_str(list_of_dts[i],list_of_switch_sym)
        if list_of_recievers[i] not in list_of_exclusions:
            send_msg(transformed_msg(msg,round_switches), list_of_recievers[i], file_with_exclusions)
            list_of_exclusions.append(list_of_recievers[i])
            sleep(iv - ivrd)
            sleep(random.randint(0, ivrd * 2))
    progress_bar(iterations, iterations, dots_in_pb)
    print '\n\n  task completed'


def execute_command(command):
    second_param = ''
    third_param = ''
    argvs = command.split(' ')
    if argvs[0] == '' or argvs[0] not in allowed_commands:
        if argvs[0] != '':
            drop()
        return
    if argvs[0] == 'exit':
        sys.exit()
    if argvs[0] == 'help':
        man()
    if argvs[0] == 'user':
        check_user()
    if argvs[0] == 'deauth':
        deauth()
    if argvs[0] == 'auth':
        try:
            second_param = raw_input('Login: ')
            third_param = pwd_input('Password: ')
        except Exception:
            drop()
            return
        auth(second_param, third_param)
    if argvs[0] == 'task':
        if not os.path.exists(file_with_token):
            print 'cannot assign new task. no user authorized'
            return
        try:
            new_task()
        except Exception:
            print 'cannot assign new task. error occured'
            return
    if argvs[0] == 'start':
        if not os.path.exists(file_with_token) or not os.path.exists(file_with_userlist) or not os.path.exists(file_with_interval_value) \
        or not os.path.exists(file_with_random_diff) or not os.path.exists(file_with_mts) or not os.path.exists(file_with_exclusions) \
        or not os.path.exists(file_with_msg_sym_map):
            print 'cannot start. task is not ready'
            return
        try:
            start()
        except Exception:
            print 'error occured. sending paused'
            return


def listen():
    while True:
        print '\nenter command:'
        try:
            command = raw_input('> ')
            execute_command(command)
        except Exception:
            print 'error'


file_with_token = 'at.dfs'
file_with_exclusions = 'exc.dfs'
file_with_log = 'log.txt'
file_with_userlist = 'lst.dfs'
file_with_interval_value = 'iv.dfs'
file_with_random_diff = 'ivrd.dfs'
file_with_msg_sym_map = 'msm.dfs'
file_with_mts = 'mts.dfs'
file_with_dts = 'dts.dfs'

basic_request_interval = 0
dots_in_pb = 50
api_url = 'https://api.vk.com/method/'
switch_syms = {
    u'А': u'A', u'В': u'B', u'Е': u'E', u'З': u'3', u'К': u'K', u'М': u'M', u'Н': u'H', u'О': u'O', u'Р': u'P', u'С': u'C', u'Т': u'T', u'Х': u'X', #R-E
    u'а': u'a', u'е': u'e', u'и': u'u', u'о': u'o', u'р': u'p', u'с': u'c', u'у': u'y', u'х': u'x', #R-E

    u'A': u'А', u'B': u'В', u'E': u'Е', u'3': u'З', u'K': u'К', u'M': u'М', u'H': u'Н', u'O': u'О', u'P': u'Р', u'C': u'С', u'T': u'Т', u'X': u'Х', #E-R
    u'a': u'а', u'e': u'е', u'u': u'и', u'o': u'о', u'p': u'р', u'c': u'с', u'y': u'у', u'x': u'х' #E-R
}
allowed_commands = ['auth', 'deauth', 'user', 'exit', 'help', 'task', 'start']


def main():
    man()
    listen()


if __name__ == '__main__':
    main()