#!/usr/bin/env python3
"""Magpie from outside, in both modes: the HTTP door (`magpie.door`)
reached by a plain client and by a second program through the verbs given
the door's URL; a log shared by a leader (`magpie.share`) and followed by
followers; a merge and a put ended at a cut (`CROW_MAGPIE_CRASH`) and the
log read whole after; the RESP door (`use magpie.redis`) by a client of
this script's own; and the Kafka door (`use magpie.kafka`) by the
pure-Python client, where a Python with kafka-python 3.0.11 is at hand
(`CROW_KAFKA_PYTHON`, or this one), skipped otherwise.

Each program runs in a directory of its own with this repository's
package linked as crow_modules/magpie, as `crow install` would link it.
A door runs in a process group of its own, ended with the program
`crow run` built. Standard library only.

Usage: python3 tests/doors.py [path to crow]   (exits 1 on any failure)"""
import os
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PACKAGE = os.path.join(os.path.dirname(HERE), 'packages', 'magpie')
CROW = sys.argv[1] if len(sys.argv) > 1 else 'crow'
failures = []


def fresh(name):
    d = tempfile.mkdtemp(prefix=f'magpie-{name}-')
    os.makedirs(os.path.join(d, 'crow_modules'))
    os.symlink(PACKAGE, os.path.join(d, 'crow_modules', 'magpie'))
    return d


def write(d, name, text):
    with open(os.path.join(d, name), 'w') as f:
        f.write(text)


def free_port():
    s = socket.socket()
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()
    return port


def wait_for(port, secs):
    end = time.time() + secs
    while time.time() < end:
        try:
            socket.create_connection(('127.0.0.1', port), timeout=1).close()
            return True
        except OSError:
            time.sleep(0.1)
    return False


def args_of(interpreted, file):
    return [CROW, 'run'] + (['-i'] if interpreted else []) + [file]


def run(d, interpreted, file, env=None):
    e = dict(os.environ, CROW_BUILD_PROFILE='dev')
    e.update(env or {})
    p = subprocess.run(args_of(interpreted, file), cwd=d, env=e, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def start(d, interpreted, file):
    e = dict(os.environ, CROW_BUILD_PROFILE='dev')
    # its own session, so its group is its own: ending the group ends the
    # program `crow run` built with it
    return subprocess.Popen(args_of(interpreted, file), cwd=d, env=e, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, start_new_session=True)


def stop(p):
    try:
        os.killpg(p.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    p.wait()


def check(name, ok, detail=''):
    if ok:
        print(f'  ok    {name}')
    else:
        failures.append(name)
        print(f'  FAIL  {name}\n        {detail}')


def mode(interpreted):
    return 'interpreted' if interpreted else 'compiled'


# ── the HTTP door ───────────────────────────────────────────────────

def http(port, method, target, body=''):
    s = socket.create_connection(('127.0.0.1', port), timeout=60)
    sent = body.encode()
    s.sendall(f'{method} {target} HTTP/1.1\r\nHost: x\r\nContent-Length: {len(sent)}\r\n\r\n'.encode() + sent)
    have = b''
    while True:
        chunk = s.recv(65536)
        if not chunk:
            break
        have += chunk
        gap = have.find(b'\r\n\r\n')
        if gap >= 0:
            length = 0
            for line in have[:gap].decode('latin-1').split('\r\n'):
                if line.lower().startswith('content-length:'):
                    length = int(line.split(':', 1)[1].strip() or 0)
            if len(have) >= gap + 4 + length:
                break
    s.close()
    head, _, rest = have.partition(b'\r\n\r\n')
    parts = head.split(b' ')
    status = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
    return status, rest.decode('utf-8', 'replace')


DOOR = "use magpie\n\nserved = magpie.door['store', {port}]\nlog[served]\n"
CLIENT = "use magpie\nuse frame\n\nd = 'http://127.0.0.1:{port}/orders'\nlog[magpie.head[d]]\nlog[magpie.batch[d, frame.new[id = [3], qty = [30]]]]\nlog[magpie.latest[d].qty]\nlog[magpie.lookup[d, ['id'], ['2'], ['qty']].qty]\nlog[magpie.latest[d, equal = ['3']].qty]\nlog[magpie.summary[d, [], ['qty'], ['sum']].qty_sum]\nlog[magpie.since[d, 1, 2].qty]\nlog[magpie.put[d, frame.new[id = [4], qty = [40]]]]\nlog[magpie.sync[d] gte 1]\nlog[len[magpie.merge[d]] gt 0]\nlog[magpie.batches[d].form]\nlog[magpie.lookup[d, ['nosuch'], ['1']].kind]\n"


def http_door(interpreted):
    name = f'the verbs reach the {mode(interpreted)} door over HTTP'
    d = fresh('door')
    port = free_port()
    write(d, 'door.co', DOOR.replace('{port}', str(port)))
    door = start(d, interpreted, 'door.co')
    try:
        if not wait_for(port, 60 if interpreted else 600):
            return check(name, False, f'the door did not listen on {port}')
        got = [
            http(port, 'POST', '/orders/batch?by=id', '[{"id": 1, "qty": 10}, {"id": 2, "qty": 20}]') == (200, '0'),
            http(port, 'GET', '/orders/head') == (200, '1'),
        ]
        status, body = http(port, 'GET', '/orders/lookup?on=id&equal=2&columns=qty')
        got.append(status == 200 and '20' in body)
        got += [http(port, 'GET', t)[0] == 404 for t in ('/orders/nosuch', '/head', '/../orders/head')]
        if not all(got):
            return check(name, False, f'the plain client: {got}')
        # a second program, through the verbs given the URL, in the other mode
        write(d, 'client.co', CLIENT.replace('{port}', str(port)))
        code, out, err = run(d, not interpreted, 'client.co')
        want = "1\n2\n[10, 20, 30]\n[20]\n[30]\n[60]\n[20, 30]\n3\ntrue\ntrue\n['segment']\nmagpie\n"
        check(name, out == want, f'the client printed {out!r}, wanted {want!r}: {err[-400:]}')
    finally:
        stop(door)
        shutil.rmtree(d, ignore_errors=True)


# ── a log shared and followed ──────────────────────────────────────

SHARE = "use magpie\nuse frame\n\nfirst = magpie.batch['log', frame.new[id = [1, 2], qty = [10, 20]], by = ['id']]\nsecond = magpie.batch['log', frame.new[id = [2, 3], qty = [25, 30]], by = ['id']]\nserved = magpie.share['log', {port}]\nlog[served]\n"
FOLLOW = "use magpie\nuse frame\n\ngot = magpie.follow['copy', '127.0.0.1', {port}]\nlog[got]\nlog[magpie.latest['copy'].qty]\nlog[magpie.head['copy']]\nagain = magpie.follow['copy', '127.0.0.1', {port}]\nlog[again]\n"


def shared(leader_interpreted):
    leader = fresh('leader')
    port = free_port()
    write(leader, 'share.co', SHARE.replace('{port}', str(port)))
    door = start(leader, leader_interpreted, 'share.co')
    try:
        if not wait_for(port, 60 if leader_interpreted else 600):
            return check(f'a log shared by the {mode(leader_interpreted)} leader', False, f'the leader did not listen on {port}')
        for follower_interpreted in (True, False):
            name = f'the {mode(follower_interpreted)} follower takes the log the {mode(leader_interpreted)} leader shares'
            follower = fresh('follower')
            write(follower, 'follow.co', FOLLOW.replace('{port}', str(port)))
            code, out, err = run(follower, follower_interpreted, 'follow.co')
            # two batches and the manifest come first; the manifest alone comes again
            check(name, out == '3\n[10, 25, 30]\n3\n1\n', f'printed {out!r}: {err[-400:]}')
            shutil.rmtree(follower, ignore_errors=True)
    finally:
        stop(door)
        shutil.rmtree(leader, ignore_errors=True)


# ── a merge or a put ended at a cut ─────────────────────────────────

CRASH = "use magpie\nuse frame\n\na = magpie.batch['log', frame.new[id = [1, 2], qty = [10, 20]], by = ['id']]\nb = magpie.batch['log', frame.new[id = [2, 3], qty = [25, 30]]]\nc = magpie.batch['log', frame.new[id = [1], qty = [15]]]\nlog[magpie.head['log']]\nm = magpie.merge['log']\nlog['merged: `m`']\n"
AFTER_CRASH = "use magpie\nuse frame\n\nb = magpie.batches['log']\nlog[b.form]\nlog[magpie.latest['log'].qty]\nlog[magpie.head['log']]\nm = magpie.merge['log']\nlog[len[m] gt 0]\nafter = magpie.batches['log']\nlog[after.form]\nlog[magpie.latest['log'].qty]\nlog[magpie.lookup['log', ['id'], ['2']].qty]\nlog[magpie.batch['log', frame.new[id = [4], qty = [40]]]]\n"
CUT = "use magpie\nuse frame\n\na = magpie.batch['log', frame.new[id = [1, 2], qty = [10, 20]], by = ['id']]\nlog[a]\nb = magpie.put['log', frame.new[id = [3], qty = [30]]]\nlog[magpie.since['log', 0].qty]\nlog['past the cut']\n"
AFTER_CUT = "use magpie\nuse frame\n\nlog[magpie.batches['log'].form]\nlog[magpie.since['log', 0].qty]\nlog[magpie.head['log']]\nlog[magpie.put['log', frame.new[id = [4], qty = [40]]]]\nlog[magpie.sync['log']]\nlog[magpie.latest['log'].qty]\n"


def files_in(d, *ends):
    return [n for n in os.listdir(os.path.join(d, 'log')) if n.endswith(ends)]


def cut_merge(interpreted, step):
    """A merge ended at each of its cuts — after the segments are placed
    and before the manifest is switched (`placed`), and after the switch,
    before the inputs are removed (`listed`) — leaves a log the next read
    and the next merge answer whole."""
    name = f'a merge ended at `{step}` ({mode(interpreted)}) leaves a log read whole'
    d = fresh('crash')
    try:
        write(d, 'crash.co', CRASH)
        code, out, err = run(d, interpreted, 'crash.co', {'CROW_MAGPIE_CRASH': step})
        if code != 3 or out != '4\n':
            return check(name, False, f'the cut ends the process with 3, nothing past it printed: {code} {out!r} {err[-400:]}')
        if len(files_in(d, '.segment')) != 1:
            return check(name, False, f'the segment was placed before either cut: {files_in(d, ".segment")}')
        write(d, 'after.co', AFTER_CRASH)
        code, out, err = run(d, True, 'after.co')
        forms = "['batch', 'batch', 'batch']" if step == 'placed' else "['segment', 'stale', 'stale', 'stale']"
        merged = 'true' if step == 'placed' else 'false'
        want = f"{forms}\n[25, 30, 15]\n4\n{merged}\n['segment']\n[25, 30, 15]\n[25]\n5\n"
        if code != 0 or out != want:
            return check(name, False, f'after the cut: {code} {out!r}, wanted {want!r}: {err[-400:]}')
        check(name, len(files_in(d, '.segment', '.batch')) == 2, f'one segment and the batch written after: {files_in(d, ".segment", ".batch")}')
    finally:
        shutil.rmtree(d, ignore_errors=True)


def cut_put(interpreted):
    """A put is visible to its process at once and durable at the flush: a
    process ended after a put and before the flush loses that put's rows,
    and keeps every row a `batch` or a `sync` had flushed."""
    name = f'a put ended before its flush is lost, the flushed rows stay ({mode(interpreted)})'
    d = fresh('pending')
    try:
        write(d, 'cut.co', CUT)
        code, out, err = run(d, interpreted, 'cut.co', {'CROW_MAGPIE_CRASH': 'pending:2'})
        if code != 3 or out != '0\n':
            return check(name, False, f'the batch answered, the put did not: {code} {out!r} {err[-400:]}')
        write(d, 'after.co', AFTER_CUT)
        code, out, err = run(d, True, 'after.co')
        want = "['batch']\n[10, 20]\n1\n2\n3\n[10, 20, 40]\n"
        check(name, code == 0 and out == want, f'{code} {out!r}, wanted {want!r}: {err[-400:]}')
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ── the RESP door ───────────────────────────────────────────────────

def whole(b):
    """How many bytes one whole reply takes, none where it is not whole yet."""
    end = b.find(b'\r\n')
    if end < 0:
        return None
    kind = b[:1]
    if kind in (b'+', b'-', b':'):
        return end + 2
    if kind == b'$':
        n = int(b[1:end])
        if n < 0:
            return end + 2
        total = end + 2 + n + 2
        return total if len(b) >= total else None
    if kind == b'*':
        at = end + 2
        for _ in range(max(int(b[1:end]), 0)):
            took = whole(b[at:])
            if took is None:
                return None
            at += took
        return at
    return None


def ask(s, words):
    req = f'*{len(words)}\r\n' + ''.join(f'${len(w.encode())}\r\n{w}\r\n' for w in words)
    s.sendall(req.encode())
    have = b''
    while True:
        chunk = s.recv(4096)
        if not chunk:
            break
        have += chunk
        if whole(have) is not None:
            break
    return have.decode('utf-8', 'replace')


REDIS = "use magpie.redis\n\nserved = redis.serve['store', {port}]\nlog[served]\n"


def redis_door(interpreted):
    name = f'a Redis client speaks to the {mode(interpreted)} door'
    d = fresh('redis')
    port = free_port()
    write(d, 'door.co', REDIS.replace('{port}', str(port)))
    door = start(d, interpreted, 'door.co')
    try:
        if not wait_for(port, 60 if interpreted else 600):
            return check(name, False, f'the door did not listen on {port}')
        s = socket.create_connection(('127.0.0.1', port), timeout=30)
        said = [
            (['PING'], '+PONG\r\n'),
            (['SET', 'greeting', 'hello world'], '+OK\r\n'),
            (['GET', 'greeting'], '$11\r\nhello world\r\n'),
            (['GET', 'nothing'], '$-1\r\n'),
            (['INCR', 'hits'], ':1\r\n'),
            (['INCRBY', 'hits', '41'], ':42\r\n'),
            (['MSET', 'a', '1', 'b', '2'], '+OK\r\n'),
            (['MGET', 'a', 'b', 'c'], '*3\r\n$1\r\n1\r\n$1\r\n2\r\n$-1\r\n'),
            (['DEL', 'a'], ':1\r\n'),
            (['EXISTS', 'a', 'b'], ':1\r\n'),
            (['XADD', 'events', '*', 'kind', 'click', 'page', '/'], '$3\r\n0-0\r\n'),
            (['XADD', 'events', '*', 'kind', 'view'], '$3\r\n1-0\r\n'),
            (['XLEN', 'events'], ':2\r\n'),
            (['XREAD', 'STREAMS', 'events', '0'], '*1\r\n*2\r\n$6\r\nevents\r\n*1\r\n*2\r\n$3\r\n1-0\r\n*2\r\n$4\r\nkind\r\n$4\r\nview\r\n'),
        ]
        for words, want in said:
            got = ask(s, words)
            if got != want:
                return check(name, False, f'{words} answered {got!r}, wanted {want!r}')
        # a second connection sees the same store
        t = socket.create_connection(('127.0.0.1', port), timeout=30)
        got = (ask(t, ['GET', 'hits']), ask(t, ['DBSIZE']))
        check(name, got == ('$2\r\n42\r\n', ':3\r\n'), f'the second connection: {got!r}')
    finally:
        stop(door)
        shutil.rmtree(d, ignore_errors=True)


# ── the Kafka door ─────────────────────────────────────────────────

KAFKA = "use magpie.kafka\n\nserved = kafka.serve['magpie', {port}]\nlog[served]\n"


def python_with_kafka():
    for p in [os.environ.get('CROW_KAFKA_PYTHON'), sys.executable, 'python3']:
        if p and subprocess.run([p, '-c', 'import kafka'], capture_output=True).returncode == 0:
            return p
    return None


def kafka_door(python, interpreted, script):
    name = f'the pure-Python client through the {mode(interpreted)} door ({script})'
    d = fresh('kafka')
    port = free_port()
    write(d, 'door.co', KAFKA.replace('{port}', str(port)))
    door = start(d, interpreted, 'door.co')
    try:
        if not wait_for(port, 60 if interpreted else 600):
            return check(name, False, f'the door did not listen on {port}')
        p = subprocess.run([python, os.path.join(HERE, 'doors', script), f'127.0.0.1:{port}'], capture_output=True, text=True)
        check(name, p.returncode == 0 and 'OK' in p.stdout, f'{p.stdout[-600:]}\n{p.stderr[-600:]}')
    finally:
        stop(door)
        shutil.rmtree(d, ignore_errors=True)


def main():
    print(f'doors: Magpie driven from outside, both modes ({CROW})\n')
    start_at = time.time()
    for interpreted in (True, False):
        http_door(interpreted)
        shared(interpreted)
        redis_door(interpreted)
    cut_put(True)
    cut_put(False)
    for interpreted, step in ((True, 'placed'), (True, 'listed'), (False, 'placed'), (False, 'listed')):
        cut_merge(interpreted, step)
    python = python_with_kafka()
    if python is None:
        print('  skip  the Kafka door: no Python with kafka-python (set CROW_KAFKA_PYTHON)')
    else:
        for script in ('kafka_driver.py', 'kafka_driver2.py'):
            for interpreted in (True, False):
                kafka_door(python, interpreted, script)
    took = time.time() - start_at
    if failures:
        print(f'\n✗ {len(failures)} failed ({took:.1f}s)')
        sys.exit(1)
    print(f'\n✓ the doors answer alike in both modes ({took:.1f}s)')


if __name__ == '__main__':
    main()
