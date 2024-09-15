import inspect
from enum import Enum
from typing import Callable
from trepan.debugger import Trepan

import mathics.eval.tracing as eval_tracing
from mathics.core.symbols import strip_context
from pymathics.debugger.lib.format import format_element, pygments_format

TraceEventNames = ("SymPy", "Numpy", "mpmath", "apply", "debugger")
TraceEvent = Enum("TraceEvent", TraceEventNames)


dbg = None

def apply_builtin_fn_traced(self, expression, vars, options: dict, evaluation):
    """
    Run debugger on a builtin function call.
    """
    vars_noctx = dict(((strip_context(s), vars[s]) for s in vars))
    if self.pass_expression:
        vars_noctx["expression"] = expression

    if options and self.check_options:
        if not self.check_options(options, evaluation):
            return None

    if eval_tracing.hook_entry_fn is not None:
        args = (self, expression, vars, options, evaluation)
        skip_call = eval_tracing.hook_entry_fn(TraceEvent.apply, *args)
    else:
        skip_call = False

    if not skip_call:
        if options:
            return self.function(evaluation=evaluation, options=options, **vars_noctx)
        else:
            return self.function(evaluation=evaluation, **vars_noctx)


def apply_builtin_fn_print(self, expression, vars, options: dict, evaluation):
    """
    Run debugger on a builtin function call.
    """
    vars_noctx = dict(((strip_context(s), vars[s]) for s in vars))
    if self.pass_expression:
        vars_noctx["expression"] = expression

    if options and self.check_options:
        if not self.check_options(options, evaluation):
            return None

    global dbg
    if dbg is None:
        from pymathics.debugger.lib.repl import DebugREPL
        dbg = DebugREPL()


    style = dbg.settings["style"]
    mathics_str = format_element(expression)
    msg = dbg.core.processor.msg
    msg(f"apply: {pygments_format(mathics_str, style)}")

    if options:
        return self.function(evaluation=evaluation, options=options, **vars_noctx)
    else:
        return self.function(evaluation=evaluation, **vars_noctx)


def call_event_debug(event: TraceEvent, fn: Callable, *args) -> bool:
    """
    A somewhat generic function to show an event-traced call.
    """
    global dbg
    if dbg is None:
        from pymathics.debugger.lib.repl import DebugREPL
        dbg = DebugREPL()

    msg = dbg.core.processor.msg

    if event == TraceEvent.apply:
        # args[0] has the expression to be called
        style = dbg.settings["style"]
        mathics_str = format_element(args[0])
        msg(f"{event.name}: {pygments_format(mathics_str, style)}")
    else:
        if type(fn) is type or inspect.ismethod(fn) or inspect.isfunction(fn):
            name = f"{fn.__module__}.{fn.__qualname__}"
        else:
            name = str(fn)
        msg(f"{event.name} call  : {name}{args[:3]}")

    # Note: there may be a temptation to go back a frame, i.e. use
    # `f_back` to `current_frame`. However, keeping the frame `call_event_debug`,
    # it is easy for trace_dispatch to detect this a known caller
    # and remove a few *more* frames to the traced calls that led up
    # to calling us.
    current_frame = inspect.currentframe()

    # Remove any "Tracing." from event string.
    event_str = str(event).split(".")[-1]
    dbg.core.execution_status = "Running"
    dbg.core.trace_dispatch(current_frame, event_str, args)

    return False

# Shoudl this be here?
def call_trepan3k(proc_obj):
    """
    Go into trepan3k - the lower-level Python debugger
    """
    core_obj = proc_obj.core
    if core_obj.python_debugger is None:
        debug_opts = {
            "settings": core_obj.debugger.settings,
            "interface": proc_obj.intf[-1]
        }
        core_obj.python_debugger = Trepan(opts=debug_opts)

    event = "line"
    python_core_obj = core_obj.python_debugger.core
    python_core_obj.execution_status = "Running"
    python_core_obj.processor.event_processor(proc_obj.curframe, event, None)
    print("call done")
    return
