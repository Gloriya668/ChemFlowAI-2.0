"""Bounded stdio client for the official DWSIM MCP server; no shell commands."""
import json
import os
import queue
import subprocess
import threading
import time
from pathlib import Path

from .store import ROOT, read_json
from .adapters import SimulatorUnavailable

CONFIG = ROOT / 'config/dwsim.json'


def settings():
    try:
        cfg = read_json(CONFIG)
        if not isinstance(cfg.get('command'), list) or not all(isinstance(x, str) for x in cfg['command']):
            raise ValueError()
        cfg['timeout_seconds'] = int(cfg.get('timeout_seconds', 120))
        if not 5 <= cfg['timeout_seconds'] <= 600:
            raise ValueError()
        return cfg
    except (OSError, ValueError, TypeError):
        raise SimulatorUnavailable('DWSIM 配置无效，请检查 config/dwsim.json。') from None


def status():
    cfg = settings()
    command = cfg['command']
    return {'configured': bool(command), 'transport': 'stdio', 'protocol': '2024-11-05',
            'routes': list(cfg.get('models', {})),
            'status': 'CONFIGURED_NOT_TESTED' if command else 'NOT_CONFIGURED'}


class Session:
    def __init__(self, config=None, audit=None):
        self.config = config or settings()
        self.audit = audit if audit is not None else []
        self.process = None
        self.log = None
        self.responses = queue.Queue(maxsize=128)
        self.sequence = 0

    def __enter__(self):
        cfg = self.config
        if not cfg['command']:
            raise SimulatorUnavailable('DWSIM 尚未配置。运行 Setup-DWSIM.ps1，或填写 config/dwsim.json。')
        cwd = Path(cfg.get('cwd') or ROOT)
        if not cwd.is_absolute():cwd = ROOT / cwd
        command = list(cfg['command'])
        command[0] = str((ROOT / command[0]).resolve()) if not Path(command[0]).is_absolute() else command[0]
        self.deadline = time.monotonic() + cfg['timeout_seconds']
        try:
            # Logs are never mixed with the JSON-RPC channel or passed back as model instructions.
            import tempfile
            self.log = tempfile.TemporaryFile()
            self.process = subprocess.Popen(command, cwd=cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=self.log, text=True, encoding='utf-8', creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            def read():
                try:
                    for line in self.process.stdout:
                        if len(line)>8_000_000:break
                        try:self.responses.put_nowait(json.loads(line))
                        except (ValueError, queue.Full):continue
                finally:
                    try:self.responses.put_nowait(None)
                    except queue.Full:pass
            self.reader = threading.Thread(target=read, daemon=True)
            self.reader.start()
            self.info = self.rpc('initialize', {'protocolVersion':'2024-11-05', 'capabilities':{},
                                   'clientInfo':{'name':'ChemFlowAI','version':'2.0'}})
            self.process.stdin.write(json.dumps({'jsonrpc':'2.0','method':'notifications/initialized'})+'\n')
            self.process.stdin.flush()
            return self
        except (OSError, ValueError) as exc:
            self.__exit__(None,None,None)
            if getattr(exc,'winerror',None)==4551:
                raise SimulatorUnavailable('Windows 应用程序控制阻止启动 DWSIM MCP（WinError 4551）；请由管理员核对可信文件策略。') from None
            raise SimulatorUnavailable('无法启动 DWSIM MCP；请检查运行包、command 和 cwd。') from None
        except Exception:
            self.__exit__(None,None,None)
            raise

    def rpc(self, method, params):
        self.sequence += 1
        request = {'jsonrpc':'2.0','id':self.sequence,'method':method,'params':params}
        try:
            self.process.stdin.write(json.dumps(request,ensure_ascii=False,allow_nan=False)+'\n')
            self.process.stdin.flush()
            while True:
                remaining = self.deadline-time.monotonic()
                if remaining<=0:raise queue.Empty()
                reply=self.responses.get(timeout=remaining)
                if reply is None:
                    self.log.seek(0)
                    detail=self.log.read(16000).decode('utf-8',errors='replace')
                    self.audit.append({'tool':'process_exit','ok':False,'diagnostic':detail[-4000:]})
                    if '0x800711C7' in detail:
                        raise SimulatorUnavailable('Windows 应用程序控制阻止加载 DWSIM 引擎 DLL（0x800711C7）。请由管理员核对并允许可信发布包；程序不会关闭系统防护。')
                    raise SimulatorUnavailable('DWSIM 进程提前退出，请检查运行依赖。'+detail[-1000:])
                if reply.get('id')==self.sequence:break
            if 'error' in reply:raise SimulatorUnavailable('DWSIM: '+str(reply['error'].get('message','协议错误'))[:1800])
            return reply['result']
        except queue.Empty:
            raise SimulatorUnavailable('DWSIM 任务超时；已终止独立求解进程。') from None
        except (OSError, KeyError, TypeError):
            raise SimulatorUnavailable('DWSIM 通信失败。') from None

    def call(self, name, /, **arguments):
        started=time.monotonic()
        result=self.rpc('tools/call', {'name':name,'arguments':arguments})
        try:
            data=json.loads(next(c['text'] for c in result['content'] if c.get('type')=='text'))
        except (StopIteration,KeyError,TypeError,ValueError):
            raise SimulatorUnavailable('DWSIM 返回的工具结果格式无效。') from None
        self.audit.append({'tool':name,'arguments':arguments,'elapsed_seconds':round(time.monotonic()-started,3),
                           'ok':not result.get('isError',False) and 'error' not in data})
        if result.get('isError') or 'error' in data:
            raise SimulatorUnavailable('DWSIM: '+str(data.get('error','工具执行失败'))[:1800])
        return data

    def __exit__(self,*args):
        if self.process is not None:
            if self.process.poll() is None:
                self.process.kill()
            self.process.wait(timeout=10)
            for stream in (self.process.stdin,self.process.stdout):
                if stream:stream.close()
        if self.log:self.log.close()


def probe():
    with Session() as session:
        tools=session.rpc('tools/list',{}).get('tools',[])
        required={'dwsim_flowsheet_load','dwsim_solve_run','dwsim_stream_get_results','dwsim_stream_set_conditions'}
        missing=sorted(required-{t['name'] for t in tools})
        if missing:raise SimulatorUnavailable('DWSIM MCP 缺少必要工具：'+', '.join(missing))
        return {'status':'CONNECTED','server':session.info.get('serverInfo'), 'tool_count':len(tools)}
