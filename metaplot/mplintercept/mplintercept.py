#!/usr/bin/python

_current = None
_intercept = False
_intercept_user = False

import sys
import decorations
import functools

try:
    from astropy.table import Table, Column
except ImportError:
    _has_astropy = False
else:
    _has_astropy = True


def intercept_func(fctn):
    """
    this is a decorator, which when attached to a function will pass
    that function through mpltr.add()

    """
    @functools.wraps(fctn)
    def call(*args, **kwargs):
        global _intercept
        if _intercept:
            #~ print "intercept_func enabled", fctn
            _intercept = False
            return_ = add(fctn, *args, **kwargs)
            _intercept = True
            return return_
        else:
            #~ print "intercept_func disabled", fctn
            return fctn(*args, **kwargs)

    return call

def intercept_method(obj, fctn):
    """
    this is a decorator, which when attached to a method of an object will pass
    that function through mpltr.add()

    """
    # extra argument needed because of this bug: http://bugs.python.org/issue3445
    @functools.wraps(fctn, set(['__doc__']))
    def call(*args, **kwargs):
        global _intercept
        if _intercept:
            #~ print "intercept_method enabled", obj, fctn
            _intercept = False
            return_ = add(fctn, *args, **kwargs)
            _intercept = True
            return return_
        else:
            #~ print "intercept_method disabled", obj, fctn
            return fctn(*args, **kwargs)

    return call

def attach_decorators_to_object(obj):
    recursive_names = []
    #~ recursive_names = ['canvas']
    # canvas causes problem with exit not being able to disconnect

    for name, fn in inspect.getmembers(obj):
        if isinstance(fn, types.UnboundMethodType):
            # fn is original method of obj
            new_method = intercept_method(obj, fn)
            # now override so that the decorator will always be called
            setattr(obj, name, new_method)
        elif isinstance(fn, types.ObjectType) and name in recursive_names:
            # recursively call this functiona gain
            attach_decorators_to_object(fn)



def disable_intercept(fctn):
    """
    this is a decorator which should wrap any internal function that calls plt
    it will temporarily disable intercepting so we don't get caught in an infinite loop
    """
    @functools.wraps(fctn)
    def call(self, *args, **kwargs):
        global _intercept
        _intercept = False
        return_ = fctn(self, *args, **kwargs)
        _intercept = _intercept_user
        return return_
    return call


# attach decorator to matplotlib function calls
# later we'll attach the decorator to any returned object
decorations.register(intercept_func, "matplotlib.pyplot")

import numpy as np
import matplotlib.pyplot as plt
import inspect, types
import json
import os, sys
import urllib2

class NumpyAwareJSONEncoder(json.JSONEncoder):
    """
    handle translating np arrays into lists so json can dump correctly
    """
    def default(self, obj):
        if isinstance(obj, np.ndarray) and obj.ndim == 1:
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

class MPLPlotCommand(object):
    """
    class that holds all the information necessary to execute a single mpl command
    """
    def __init__(self, obj, func, *args, **kwargs):
        if hasattr(func, 'func_name'):
            func = func.func_name

        self.id_obj = obj if (isinstance(obj, int) or obj is None) else id(obj) if obj != plt else None
        self.func = func
        self.args = args
        self.ids_return = kwargs.pop('ids_return', [])
        self.kwargs = kwargs

    def run(self, obj=None):
        #~ print "MPLPlotCommand.run", self.func, self.args, self.kwargs
        if obj is None:
            obj = plt

        ret = getattr(obj, self.func)(*self.args, **self.kwargs)

        return ret

class MPLTracker(object):
    """
    class that holds multiple MPLPlotCommand objects and handles passing
    any objects that are returned from one command and later passed to another
    """
    def __init__(self, load=None):
        global _current
        _current = self

        # commands holds an ordered list of MPLPlotCommand objects
        self.commands = []
        # returns holds a dictionary of id, object pairs returned by plotting calls
        self.returns = {}
        # used returns holds a list of the id's of returned objects that are actually used
        self.used_returns = []

        # TODO: handle args smarter so we don't store duplicates for arrays ?
        #   this would require storing data in the MPLTracker instead of the MPLCommand

        if load is not None:
            if isinstance(load, file):
                data = f.readline()
            if os.path.isfile(load):
                f = open(load, 'r')
                data = f.readline()
            else:
                try:
                    # maybe we were passed a url
                    data = urllib2.urlopen(load).read()
                except ValueError:
                    # as last resort: maybe we were passed the json string itself
                    data = load

            for cdict in json.loads(data):
                self.commands.append(MPLPlotCommand(cdict['id_obj'], cdict['func'], *cdict['args'], ids_return=cdict['ids_return'], **cdict['kwargs']))

    def list_commands(self):
        """
        quick summary of all commands that have been tracked
        """
        string = ''
        for command in self.commands:
            # TODO: make this nicer - problem is after saving we lose the actual returns
            # perhaps we could also store their names?
            #~ if command.id_obj is not None:
                #~ print self.returns, command.id_obj
                #~ string += self.returns[command.id_obj].__name__
            string += "{}\n".format(command.func)
        return string

    def get_data(self):
        """
        get all data (args) from all commands that have been tracked
        """
        lst = []
        for command in self.commands:
            # TODO: this makes the assumption of xy data... we may need to be
            # more clever for other plotting types

            # TODO: we are also assuming that data is always sent as args (not
            # kwargs)
            lst.append([command.args[0], command.args[1]])

        return lst

    def get_data_table(self, format=None):
        """
        get all data (args) from all commands that have been tracked and return
        an astropy table instance
        """
        if not _has_astropy:
            raise ImportError("could not import astropy.table.Table")

        t = Table()

        # For now let's only support plot with a single dataset.  Its difficult
        # otherwise to deal with different lengthed columns.
        if len(self.commands) != 1:
            print self.commands
            raise NotImplementedError("currently only supports 1 dataset (you have {})".format(len(self.commands)))

        for command in self.commands:
            # TODO: this makes the assumption of xy data... we may need to be
            # more clever for other plotting types

            # TODO: we are also assuming that data is always sent as args (not
            # kwargs)

            # TODO: get column names from the datalabels or axes labels
            # TODO: units, etc
            xinfo = {}
            xinfo['data'] = command.args[0]
            xinfo['name'] = 'x'
            t.add_column(Column(**xinfo))


            yinfo = {}
            yinfo['data'] = command.args[1]
            yinfo['name'] = 'y'
            t.add_column(Column(**yinfo))

        if format is None:
            return t
        else:
            return t.write(sys.stdout, format)

    def add(self, func, *args, **kwargs):
        """
        add exactly as it would be called from matplotlib.pyplot (plt)

        examples:
        plt.plot(a,b,'k.') => mpltr.add_plot_command(plt.plot, a, b, 'k.')

        fig = plt.figure() => fig = mpltr.add_plot_command(plt.figure)
        ax = fig.add_subplot(111) => ax = mpltr.add_plot_command(fig.add_subplot, (111))
        """
        if hasattr(func, 'im_self'):
            # then func is an attribute of some obj that we hopefully
            # have stored in self.returns
            if func.im_self in self.returns.values():
                # then the obj was a return from a previous command
                obj = func.im_self

                # we need to remember to track this connection when saving
                self.used_returns.append(id(obj))

            else:
                raise ValueError("cannot find object: {}".format(func.im_self))
                # TODO: test this error statement

        else:
            # default to func being an attribute of plt
            # TODO: handle more options
            #   from matplotlib import collections
            #   from mpl_toolkits.mplot3d import art3d
            #   different ways to import plt?
            obj = plt

        comm = MPLPlotCommand(obj, func, *args, **kwargs)
        self.commands.append(comm)

        # we need to run this command so we can track the output
        ret = comm.run(obj)

        if not (isinstance(ret, list) or isinstance(ret, tuple)):
            ret_ = (ret,)
        else:
            ret_ = ret
        for ri in ret_:
            # now we need to attach the intercept decorator to any function of ret
            attach_decorators_to_object(ri)

            comm.ids_return.append(id(ri))
            self.returns[id(ri)] = ri

        # return as if the user was making the call directly
        return ret

    def save(self, filename=None):
        # purge not-needed returns
        #    clear all command.ids_return if not in self.used_returns
        #    clear self.returns
        #    clear self.used_returns

        for command in self.commands:
            for i,id_return in reversed(list(enumerate(command.ids_return))):
                if id_return not in self.used_returns:
                    command.ids_return.pop(i)
        self.returns = {}
        self.used_returns = []

        dump = json.dumps([c.__dict__ for c in self.commands], cls=NumpyAwareJSONEncoder)

        if filename is not None:
            f = open(filename, 'w')
            f.write(dump)
            f.close()
            return filename
        else:
            # just return the json string
            return dump

    @disable_intercept
    def get_fig(self):
        for command in self.commands:
            if command.id_obj is not None:
                # then we need to get from self.returns
                #~ print "getting obj from self.returns", command.id_obj, self.returns
                obj = self.returns[command.id_obj]
            else:
                obj = plt

            ret = command.run(obj)

            if not (isinstance(ret, list) or isinstance(ret, tuple)):
                ret_ = (ret,)
            else:
                ret_ = ret

            for ri,id_return in zip(ret_,command.ids_return):
                self.returns[id_return] = ri

        return plt.gcf()

    @disable_intercept
    def show(self):
        fig = self.get_fig()
        plt.show()
        return None

def intercept(on=True):
    """
    enable or disable tracking/interecpting of matplotlib calls
    """
    global _intercept, _intercept_user
    _intercept = on
    _intercept_user = on

def start(new=False):
    """
    intercept(True)
    """
    if new:
        mpltr = MPLTracker()

    intercept(True)

def stop():
    """
    intercept(False)
    """
    intercept(True)

def gct():
    """
    get current tracker
    """
    if _current is None:
        mpltr = MPLTracker()
    return _current

def list_commands():
    """
    global call to mpltr.list_commands
    """
    return gct().list_commands()

def show(load=None):
    """
    load a figure from a JSON string, URL, or filename and immediately
    open an interactive matplotlib window
    """
    if load is not None:
        mpltr = MPLTracker(load)

    gct().show()

def get_fig(load=None):
    """
    load a figure from a JSON string, URL, or filename and immediately
    return the figure object
    """
    if load is not None:
        mpltr = MPLTracker(load)

    return gct().get_fig()

def get_data(load=None):
    """
    load a figure from a JSON string, URL, or filename and immediately
    return the data associated with that figure
    """
    if load is not None:
        mpltr = MPLTracker(load)

    return gct().get_data()

def get_data_table(load=None):
    """
    load a figure from a JSON string, URL, or filename and immediately
    return the data associated with that figure
    """
    if load is not None:
        mpltr = MPLTracker(load)

    return gct().get_data_table()

def write_data_table(load=None, filename='table.data', format='ascii.ecsv'):
    """
    """
    return get_data_table(load=load).write(filename, format=format)

def add(func, *args, **kwargs):
    """
    global call to mpltr.add
    """
    if _current is None:
        mpltr = MPLTracker()

    return gct().add(func, *args, **kwargs)

def save(filename=None, stop_intercept=True):
    """
    global call to mpltr.save
    """
    if stop_intercept:
        stop()
    return gct().save(filename=filename)

if __name__ == '__main__':
    show(sys.argv[1])